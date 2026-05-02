from fastapi import FastAPI, HTTPException, Depends, Header, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional
# from datetime import datetime,time
from datetime import datetime, date, time

import os
from dotenv import load_dotenv

from .database import get_db_connection, init_db
from .auth import hash_password, verify_password, create_access_token, create_monitoring_token, verify_token

load_dotenv()

app = FastAPI(title="SkillBridge API", description="Attendance Management System", version="1.0.0")

# Security for Swagger UI
security = HTTPBearer()

# ---------- PYDANTIC MODELS ----------
class UserSignup(BaseModel):
    name: str
    email: str
    password: str
    role: str
    institution_id: Optional[int] = None

class UserLogin(BaseModel):
    email: str
    password: str

class MonitoringTokenRequest(BaseModel):
    key: str

class BatchCreate(BaseModel):
    name: str
    institution_id: int

class BatchJoin(BaseModel):
    token: str

class SessionCreate(BaseModel):
    batch_id: int
    title: str
    date: str
    start_time: str
    end_time: str

class AttendanceMark(BaseModel):
    session_id: int
    status: str

# ---------- HELPER FUNCTIONS ----------
async def get_current_user(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="No token provided")
    parts = authorization.split()
    if parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    token = parts[1]
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return payload

async def get_current_user_swagger(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return payload

def check_role(user_payload: dict, allowed_roles: list):
    if user_payload.get("role") not in allowed_roles:
        raise HTTPException(status_code=403, detail=f"Role {user_payload.get('role')} not allowed")

@app.on_event("startup")
async def startup():
    await init_db()

# ---------- AUTH ENDPOINTS ----------
@app.post("/auth/signup")
async def signup(user: UserSignup):
    conn = await get_db_connection()
    existing = await conn.fetchrow("SELECT id FROM users WHERE email = $1", user.email)
    if existing:
        await conn.close()
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = hash_password(user.password)
    result = await conn.fetchrow(
        "INSERT INTO users (name, email, hashed_password, role, institution_id) VALUES ($1, $2, $3, $4, $5) RETURNING id",
        user.name, user.email, hashed, user.role, user.institution_id
    )
    await conn.close()
    token = create_access_token(result["id"], user.role)
    return {"message": "User created successfully", "access_token": token, "token_type": "bearer"}

@app.post("/auth/login")
async def login(user: UserLogin):
    conn = await get_db_connection()
    db_user = await conn.fetchrow("SELECT id, email, hashed_password, role, institution_id FROM users WHERE email = $1", user.email)
    if not db_user:
        await conn.close()
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not verify_password(user.password, db_user["hashed_password"]):
        await conn.close()
        raise HTTPException(status_code=401, detail="Invalid credentials")
    await conn.close()
    token = create_access_token(db_user["id"], db_user["role"], db_user["institution_id"])
    return {"access_token": token, "token_type": "bearer"}

@app.post("/auth/monitoring-token")
async def get_monitoring_token(request: MonitoringTokenRequest, user_payload: dict = Depends(get_current_user)):
    if user_payload.get("role") != "monitoring_officer":
        raise HTTPException(status_code=403, detail="Only monitoring officers can get monitoring token")
    valid_key = os.getenv("MONITORING_API_KEY", "capi_key")
    if request.key != valid_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    monitoring_token = create_monitoring_token(user_payload.get("user_id"), user_payload.get("role"))
    return {"access_token": monitoring_token, "token_type": "bearer", "expires_in": "1 hour"}

# ---------- BATCH ENDPOINTS ----------
@app.post("/batches")
async def create_batch(batch: BatchCreate, user_payload: dict = Depends(get_current_user)):
    check_role(user_payload, ["trainer", "institution"])
    conn = await get_db_connection()
    result = await conn.fetchrow("INSERT INTO batches (name, institution_id) VALUES ($1, $2) RETURNING id", batch.name, batch.institution_id)
    await conn.close()
    return {"message": "Batch created", "batch_id": result["id"]}

@app.post("/batches/{batch_id}/invite")
async def generate_invite(batch_id: int, user_payload: dict = Depends(get_current_user)):
    check_role(user_payload, ["trainer"])
    import secrets
    token = secrets.token_urlsafe(32)
    conn = await get_db_connection()
    await conn.execute("INSERT INTO batch_invites (batch_id, token, created_by, expires_at) VALUES ($1, $2, $3, NOW() + INTERVAL '7 days')", batch_id, token, user_payload.get("user_id"))
    await conn.close()
    return {"invite_token": token}

@app.post("/batches/join")
async def join_batch(join_data: BatchJoin, user_payload: dict = Depends(get_current_user)):
    check_role(user_payload, ["student"])
    conn = await get_db_connection()
    invite = await conn.fetchrow("SELECT batch_id FROM batch_invites WHERE token = $1 AND used = false AND expires_at > NOW()", join_data.token)
    if not invite:
        await conn.close()
        raise HTTPException(status_code=404, detail="Invalid or expired invite")
    existing = await conn.fetchrow("SELECT * FROM batch_students WHERE batch_id = $1 AND student_id = $2", invite["batch_id"], user_payload.get("user_id"))
    if existing:
        await conn.close()
        raise HTTPException(status_code=400, detail="Already enrolled")
    await conn.execute("INSERT INTO batch_students (batch_id, student_id) VALUES ($1, $2)", invite["batch_id"], user_payload.get("user_id"))
    await conn.execute("UPDATE batch_invites SET used = true WHERE token = $1", join_data.token)
    await conn.close()
    return {"message": "Successfully joined batch"}
# ---------- SESSION ENDPOINTS ----------
@app.post("/sessions")
async def create_session(session: SessionCreate, user_payload: dict = Depends(get_current_user)):
    check_role(user_payload, ["trainer"])
    conn = await get_db_connection()
    
    # Convert string to date and time objects
    from datetime import date, time
    session_date = date.fromisoformat(session.date)
    start_time = time.fromisoformat(session.start_time)
    end_time = time.fromisoformat(session.end_time)
    
    result = await conn.fetchrow(
        "INSERT INTO sessions (batch_id, trainer_id, title, date, start_time, end_time, created_at) VALUES ($1, $2, $3, $4, $5, $6, NOW()) RETURNING id",
        session.batch_id, 
        user_payload.get("user_id"), 
        session.title, 
        session_date,      # date object
        start_time,        # time object
        end_time           # time object
    )
    await conn.close()
    return {"message": "Session created", "session_id": result["id"]}

@app.get("/sessions/{session_id}/attendance")
async def get_session_attendance(session_id: int, user_payload: dict = Depends(get_current_user)):
    check_role(user_payload, ["trainer"])
    conn = await get_db_connection()
    session = await conn.fetchrow("SELECT batch_id FROM sessions WHERE id = $1", session_id)
    if not session:
        await conn.close()
        raise HTTPException(status_code=404, detail="Session not found")
    attendance = await conn.fetch(
        "SELECT a.*, u.name FROM attendance a JOIN users u ON a.student_id = u.id WHERE a.session_id = $1",
        session_id
    )
    await conn.close()
    return {"session_id": session_id, "attendance": [dict(record) for record in attendance]}

# ---------- ATTENDANCE ENDPOINTS ----------
@app.post("/attendance/mark")
async def mark_attendance(attendance: AttendanceMark, user_payload: dict = Depends(get_current_user)):
    check_role(user_payload, ["student"])
    conn = await get_db_connection()
    session = await conn.fetchrow("SELECT batch_id FROM sessions WHERE id = $1", attendance.session_id)
    if not session:
        await conn.close()
        raise HTTPException(status_code=404, detail="Session not found")
    enrolled = await conn.fetchrow("SELECT * FROM batch_students WHERE batch_id = $1 AND student_id = $2", session["batch_id"], user_payload.get("user_id"))
    if not enrolled:
        await conn.close()
        raise HTTPException(status_code=403, detail="You are not enrolled in this session's batch")
    already_marked = await conn.fetchrow("SELECT * FROM attendance WHERE session_id = $1 AND student_id = $2", attendance.session_id, user_payload.get("user_id"))
    if already_marked:
        await conn.close()
        raise HTTPException(status_code=400, detail="Attendance already marked for this session")
    await conn.execute("INSERT INTO attendance (session_id, student_id, status) VALUES ($1, $2, $3)", attendance.session_id, user_payload.get("user_id"), attendance.status)
    await conn.close()
    return {"message": "Attendance marked successfully"}


# ---------- MONITORING ENDPOINTS ----------
@app.get("/monitoring/attendance")
async def monitoring_attendance(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="No token provided")
    parts = authorization.split()
    if parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    token = parts[1]
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    if payload.get("type") != "monitoring":
        raise HTTPException(status_code=403, detail="Invalid token type. Use monitoring token")
    if payload.get("role") != "monitoring_officer":
        raise HTTPException(status_code=403, detail="Only monitoring officers can access")
    conn = await get_db_connection()
    attendance = await conn.fetch("SELECT * FROM attendance")
    await conn.close()
    return {"attendance": [dict(record) for record in attendance]}

@app.api_route("/monitoring/attendance", methods=["POST", "PUT", "DELETE", "PATCH"])
async def monitoring_attendance_method_not_allowed():
    raise HTTPException(status_code=405, detail="Method Not Allowed")

# ---------- SUMMARY ENDPOINTS ----------
@app.get("/batches/{batch_id}/summary")
async def batch_summary(batch_id: int, user_payload: dict = Depends(get_current_user)):
    print(f"DEBUG user_payload: {user_payload}")  # ← ADD THIS LINE
    check_role(user_payload, ["institution"])
    conn = await get_db_connection()
    batch = await conn.fetchrow("SELECT * FROM batches WHERE id = $1", batch_id)
    if not batch:
        await conn.close()
        raise HTTPException(status_code=404, detail="Batch not found")
    if batch["institution_id"] != user_payload.get("institution_id"):
        await conn.close()
        raise HTTPException(status_code=403, detail="You don't have access to this batch")
    total_students = await conn.fetchval("SELECT COUNT(*) FROM batch_students WHERE batch_id = $1", batch_id)
    await conn.close()
    return {"batch_id": batch_id, "batch_name": batch["name"], "total_students": total_students}

@app.get("/institutions/{institution_id}/summary")
async def institution_summary(institution_id: int, user_payload: dict = Depends(get_current_user)):
    check_role(user_payload, ["programme_manager"])
    conn = await get_db_connection()
    institution = await conn.fetchrow("SELECT * FROM users WHERE id = $1 AND role = 'institution'", institution_id)
    if not institution:
        await conn.close()
        raise HTTPException(status_code=404, detail="Institution not found")
    batches = await conn.fetch("SELECT id, name FROM batches WHERE institution_id = $1", institution_id)
    total_students = await conn.fetchval("SELECT COUNT(DISTINCT student_id) FROM batch_students bs JOIN batches b ON bs.batch_id = b.id WHERE b.institution_id = $1", institution_id)
    await conn.close()
    return {"institution_id": institution_id, "institution_name": institution["name"], "total_batches": len(batches), "total_students": total_students, "batches": [{"id": b["id"], "name": b["name"]} for b in batches]}

@app.get("/programme/summary")
async def programme_summary(user_payload: dict = Depends(get_current_user)):
    check_role(user_payload, ["programme_manager"])
    conn = await get_db_connection()
    total_institutions = await conn.fetchval("SELECT COUNT(*) FROM users WHERE role = 'institution'")
    total_students = await conn.fetchval("SELECT COUNT(*) FROM users WHERE role = 'student'")
    total_trainers = await conn.fetchval("SELECT COUNT(*) FROM users WHERE role = 'trainer'")
    total_batches = await conn.fetchval("SELECT COUNT(*) FROM batches")
    total_sessions = await conn.fetchval("SELECT COUNT(*) FROM sessions")
    total_attendance = await conn.fetchval("SELECT COUNT(*) FROM attendance")
    await conn.close()
    return {"total_institutions": total_institutions, "total_students": total_students, "total_trainers": total_trainers, "total_batches": total_batches, "total_sessions": total_sessions, "total_attendance_records": total_attendance}

@app.get("/")
async def root():
    return {"message": "SkillBridge API is running", "docs": "/docs", "version": "1.0.0"}

