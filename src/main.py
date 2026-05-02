# from fastapi import FastAPI, HTTPException, Depends, Header, Security
# from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
# from pydantic import BaseModel
# from typing import Optional
# # from datetime import datetime,time
# from datetime import datetime, date, time

# import os
# from dotenv import load_dotenv

# from .database import get_db_connection, init_db
# from .auth import hash_password, verify_password, create_access_token, create_monitoring_token, verify_token

# load_dotenv()

# app = FastAPI(title="SkillBridge API", description="Attendance Management System", version="1.0.0")

# # Security for Swagger UI
# security = HTTPBearer()

# # ---------- PYDANTIC MODELS ----------
# class UserSignup(BaseModel):
#     name: str
#     email: str
#     password: str
#     role: str
#     institution_id: Optional[int] = None

# class UserLogin(BaseModel):
#     email: str
#     password: str

# class MonitoringTokenRequest(BaseModel):
#     key: str

# class BatchCreate(BaseModel):
#     name: str
#     institution_id: int

# class BatchJoin(BaseModel):
#     token: str

# class SessionCreate(BaseModel):
#     batch_id: int
#     title: str
#     date: str
#     start_time: str
#     end_time: str

# class AttendanceMark(BaseModel):
#     session_id: int
#     status: str

# # ---------- HELPER FUNCTIONS ----------
# async def get_current_user(authorization: str = Header(None)):
#     if not authorization:
#         raise HTTPException(status_code=401, detail="No token provided")
#     parts = authorization.split()
#     if parts[0].lower() != "bearer":
#         raise HTTPException(status_code=401, detail="Invalid authorization header")
#     token = parts[1]
#     payload = verify_token(token)
#     if not payload:
#         raise HTTPException(status_code=401, detail="Invalid or expired token")
#     return payload

# async def get_current_user_swagger(credentials: HTTPAuthorizationCredentials = Security(security)):
#     token = credentials.credentials
#     payload = verify_token(token)
#     if not payload:
#         raise HTTPException(status_code=401, detail="Invalid or expired token")
#     return payload

# def check_role(user_payload: dict, allowed_roles: list):
#     if user_payload.get("role") not in allowed_roles:
#         raise HTTPException(status_code=403, detail=f"Role {user_payload.get('role')} not allowed")

# @app.on_event("startup")
# async def startup():
#     await init_db()

# # ---------- AUTH ENDPOINTS ----------
# @app.post("/auth/signup")
# async def signup(user: UserSignup):
#     conn = await get_db_connection()
#     existing = await conn.fetchrow("SELECT id FROM users WHERE email = $1", user.email)
#     if existing:
#         await conn.close()
#         raise HTTPException(status_code=400, detail="Email already registered")
#     hashed = hash_password(user.password)
#     result = await conn.fetchrow(
#         "INSERT INTO users (name, email, hashed_password, role, institution_id) VALUES ($1, $2, $3, $4, $5) RETURNING id",
#         user.name, user.email, hashed, user.role, user.institution_id
#     )
#     await conn.close()
#     token = create_access_token(result["id"], user.role)
#     return {"message": "User created successfully", "access_token": token, "token_type": "bearer"}

# @app.post("/auth/login")
# async def login(user: UserLogin):
#     conn = await get_db_connection()
#     db_user = await conn.fetchrow("SELECT id, email, hashed_password, role, institution_id FROM users WHERE email = $1", user.email)
#     if not db_user:
#         await conn.close()
#         raise HTTPException(status_code=401, detail="Invalid credentials")
#     if not verify_password(user.password, db_user["hashed_password"]):
#         await conn.close()
#         raise HTTPException(status_code=401, detail="Invalid credentials")
#     await conn.close()
#     token = create_access_token(db_user["id"], db_user["role"], db_user["institution_id"])
#     return {"access_token": token, "token_type": "bearer"}

# @app.post("/auth/monitoring-token")
# async def get_monitoring_token(request: MonitoringTokenRequest, user_payload: dict = Depends(get_current_user)):
#     if user_payload.get("role") != "monitoring_officer":
#         raise HTTPException(status_code=403, detail="Only monitoring officers can get monitoring token")
#     valid_key = os.getenv("MONITORING_API_KEY", "capi_key")
#     if request.key != valid_key:
#         raise HTTPException(status_code=401, detail="Invalid API key")
#     monitoring_token = create_monitoring_token(user_payload.get("user_id"), user_payload.get("role"))
#     return {"access_token": monitoring_token, "token_type": "bearer", "expires_in": "1 hour"}

# # ---------- BATCH ENDPOINTS ----------
# @app.post("/batches")
# async def create_batch(batch: BatchCreate, user_payload: dict = Depends(get_current_user)):
#     check_role(user_payload, ["trainer", "institution"])
#     conn = await get_db_connection()
#     result = await conn.fetchrow("INSERT INTO batches (name, institution_id) VALUES ($1, $2) RETURNING id", batch.name, batch.institution_id)
#     await conn.close()
#     return {"message": "Batch created", "batch_id": result["id"]}

# @app.post("/batches/{batch_id}/invite")
# async def generate_invite(batch_id: int, user_payload: dict = Depends(get_current_user)):
#     check_role(user_payload, ["trainer"])
#     import secrets
#     token = secrets.token_urlsafe(32)
#     conn = await get_db_connection()
#     await conn.execute("INSERT INTO batch_invites (batch_id, token, created_by, expires_at) VALUES ($1, $2, $3, NOW() + INTERVAL '7 days')", batch_id, token, user_payload.get("user_id"))
#     await conn.close()
#     return {"invite_token": token}

# @app.post("/batches/join")
# async def join_batch(join_data: BatchJoin, user_payload: dict = Depends(get_current_user)):
#     check_role(user_payload, ["student"])
#     conn = await get_db_connection()
#     invite = await conn.fetchrow("SELECT batch_id FROM batch_invites WHERE token = $1 AND used = false AND expires_at > NOW()", join_data.token)
#     if not invite:
#         await conn.close()
#         raise HTTPException(status_code=404, detail="Invalid or expired invite")
#     existing = await conn.fetchrow("SELECT * FROM batch_students WHERE batch_id = $1 AND student_id = $2", invite["batch_id"], user_payload.get("user_id"))
#     if existing:
#         await conn.close()
#         raise HTTPException(status_code=400, detail="Already enrolled")
#     await conn.execute("INSERT INTO batch_students (batch_id, student_id) VALUES ($1, $2)", invite["batch_id"], user_payload.get("user_id"))
#     await conn.execute("UPDATE batch_invites SET used = true WHERE token = $1", join_data.token)
#     await conn.close()
#     return {"message": "Successfully joined batch"}
# # ---------- SESSION ENDPOINTS ----------
# @app.post("/sessions")
# async def create_session(session: SessionCreate, user_payload: dict = Depends(get_current_user)):
#     check_role(user_payload, ["trainer"])
#     conn = await get_db_connection()
    
#     # Convert string to date and time objects
#     from datetime import date, time
#     session_date = date.fromisoformat(session.date)
#     start_time = time.fromisoformat(session.start_time)
#     end_time = time.fromisoformat(session.end_time)
    
#     result = await conn.fetchrow(
#         "INSERT INTO sessions (batch_id, trainer_id, title, date, start_time, end_time, created_at) VALUES ($1, $2, $3, $4, $5, $6, NOW()) RETURNING id",
#         session.batch_id, 
#         user_payload.get("user_id"), 
#         session.title, 
#         session_date,      # date object
#         start_time,        # time object
#         end_time           # time object
#     )
#     await conn.close()
#     return {"message": "Session created", "session_id": result["id"]}

# @app.get("/sessions/{session_id}/attendance")
# async def get_session_attendance(session_id: int, user_payload: dict = Depends(get_current_user)):
#     check_role(user_payload, ["trainer"])
#     conn = await get_db_connection()
#     session = await conn.fetchrow("SELECT batch_id FROM sessions WHERE id = $1", session_id)
#     if not session:
#         await conn.close()
#         raise HTTPException(status_code=404, detail="Session not found")
#     attendance = await conn.fetch(
#         "SELECT a.*, u.name FROM attendance a JOIN users u ON a.student_id = u.id WHERE a.session_id = $1",
#         session_id
#     )
#     await conn.close()
#     return {"session_id": session_id, "attendance": [dict(record) for record in attendance]}

# # ---------- ATTENDANCE ENDPOINTS ----------
# @app.post("/attendance/mark")
# async def mark_attendance(attendance: AttendanceMark, user_payload: dict = Depends(get_current_user)):
#     check_role(user_payload, ["student"])
#     conn = await get_db_connection()
#     session = await conn.fetchrow("SELECT batch_id FROM sessions WHERE id = $1", attendance.session_id)
#     if not session:
#         await conn.close()
#         raise HTTPException(status_code=404, detail="Session not found")
#     enrolled = await conn.fetchrow("SELECT * FROM batch_students WHERE batch_id = $1 AND student_id = $2", session["batch_id"], user_payload.get("user_id"))
#     if not enrolled:
#         await conn.close()
#         raise HTTPException(status_code=403, detail="You are not enrolled in this session's batch")
#     already_marked = await conn.fetchrow("SELECT * FROM attendance WHERE session_id = $1 AND student_id = $2", attendance.session_id, user_payload.get("user_id"))
#     if already_marked:
#         await conn.close()
#         raise HTTPException(status_code=400, detail="Attendance already marked for this session")
#     await conn.execute("INSERT INTO attendance (session_id, student_id, status) VALUES ($1, $2, $3)", attendance.session_id, user_payload.get("user_id"), attendance.status)
#     await conn.close()
#     return {"message": "Attendance marked successfully"}


# # ---------- MONITORING ENDPOINTS ----------
# @app.get("/monitoring/attendance")
# async def monitoring_attendance(authorization: str = Header(None)):
#     if not authorization:
#         raise HTTPException(status_code=401, detail="No token provided")
#     parts = authorization.split()
#     if parts[0].lower() != "bearer":
#         raise HTTPException(status_code=401, detail="Invalid authorization header")
#     token = parts[1]
#     payload = verify_token(token)
#     if not payload:
#         raise HTTPException(status_code=401, detail="Invalid or expired token")
#     if payload.get("type") != "monitoring":
#         raise HTTPException(status_code=403, detail="Invalid token type. Use monitoring token")
#     if payload.get("role") != "monitoring_officer":
#         raise HTTPException(status_code=403, detail="Only monitoring officers can access")
#     conn = await get_db_connection()
#     attendance = await conn.fetch("SELECT * FROM attendance")
#     await conn.close()
#     return {"attendance": [dict(record) for record in attendance]}

# @app.api_route("/monitoring/attendance", methods=["POST", "PUT", "DELETE", "PATCH"])
# async def monitoring_attendance_method_not_allowed():
#     raise HTTPException(status_code=405, detail="Method Not Allowed")

# # ---------- SUMMARY ENDPOINTS ----------
# @app.get("/batches/{batch_id}/summary")
# async def batch_summary(batch_id: int, user_payload: dict = Depends(get_current_user)):
#     print(f"DEBUG user_payload: {user_payload}")  # ← ADD THIS LINE
#     check_role(user_payload, ["institution"])
#     conn = await get_db_connection()
#     batch = await conn.fetchrow("SELECT * FROM batches WHERE id = $1", batch_id)
#     if not batch:
#         await conn.close()
#         raise HTTPException(status_code=404, detail="Batch not found")
#     if batch["institution_id"] != user_payload.get("institution_id"):
#         await conn.close()
#         raise HTTPException(status_code=403, detail="You don't have access to this batch")
#     total_students = await conn.fetchval("SELECT COUNT(*) FROM batch_students WHERE batch_id = $1", batch_id)
#     await conn.close()
#     return {"batch_id": batch_id, "batch_name": batch["name"], "total_students": total_students}

# @app.get("/institutions/{institution_id}/summary")
# async def institution_summary(institution_id: int, user_payload: dict = Depends(get_current_user)):
#     check_role(user_payload, ["programme_manager"])
#     conn = await get_db_connection()
#     institution = await conn.fetchrow("SELECT * FROM users WHERE id = $1 AND role = 'institution'", institution_id)
#     if not institution:
#         await conn.close()
#         raise HTTPException(status_code=404, detail="Institution not found")
#     batches = await conn.fetch("SELECT id, name FROM batches WHERE institution_id = $1", institution_id)
#     total_students = await conn.fetchval("SELECT COUNT(DISTINCT student_id) FROM batch_students bs JOIN batches b ON bs.batch_id = b.id WHERE b.institution_id = $1", institution_id)
#     await conn.close()
#     return {"institution_id": institution_id, "institution_name": institution["name"], "total_batches": len(batches), "total_students": total_students, "batches": [{"id": b["id"], "name": b["name"]} for b in batches]}

# @app.get("/programme/summary")
# async def programme_summary(user_payload: dict = Depends(get_current_user)):
#     check_role(user_payload, ["programme_manager"])
#     conn = await get_db_connection()
#     total_institutions = await conn.fetchval("SELECT COUNT(*) FROM users WHERE role = 'institution'")
#     total_students = await conn.fetchval("SELECT COUNT(*) FROM users WHERE role = 'student'")
#     total_trainers = await conn.fetchval("SELECT COUNT(*) FROM users WHERE role = 'trainer'")
#     total_batches = await conn.fetchval("SELECT COUNT(*) FROM batches")
#     total_sessions = await conn.fetchval("SELECT COUNT(*) FROM sessions")
#     total_attendance = await conn.fetchval("SELECT COUNT(*) FROM attendance")
#     await conn.close()
#     return {"total_institutions": total_institutions, "total_students": total_students, "total_trainers": total_trainers, "total_batches": total_batches, "total_sessions": total_sessions, "total_attendance_records": total_attendance}

# @app.get("/")
# async def root():
#     return {"message": "SkillBridge API is running", "docs": "/docs", "version": "1.0.0"}



from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date, time
import os
import secrets
import psycopg2
from dotenv import load_dotenv

from .auth import hash_password, verify_password, create_access_token, create_monitoring_token, verify_token

load_dotenv()

app = FastAPI(title="SkillBridge API", description="Attendance Management System", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# ---------- DATABASE CONNECTION ----------
def get_db():
    return psycopg2.connect(os.getenv("DATABASE_URL"))

# ---------- HELPER FUNCTIONS ----------
def get_current_user(authorization: str = Header(None)):
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

def check_role(user_payload: dict, allowed_roles: list):
    if user_payload.get("role") not in allowed_roles:
        raise HTTPException(status_code=403, detail=f"Role {user_payload.get('role')} not allowed")

# ---------- INIT DATABASE ----------
@app.on_event("startup")
def startup():
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            hashed_password VARCHAR(255) NOT NULL,
            role VARCHAR(50) NOT NULL,
            institution_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS batches (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            institution_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS batch_trainers (
            batch_id INTEGER NOT NULL,
            trainer_id INTEGER NOT NULL,
            PRIMARY KEY (batch_id, trainer_id)
        )
    ''')
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS batch_students (
            batch_id INTEGER NOT NULL,
            student_id INTEGER NOT NULL,
            PRIMARY KEY (batch_id, student_id)
        )
    ''')
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS batch_invites (
            id SERIAL PRIMARY KEY,
            batch_id INTEGER NOT NULL,
            token VARCHAR(255) UNIQUE NOT NULL,
            created_by INTEGER NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            used BOOLEAN DEFAULT FALSE
        )
    ''')
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id SERIAL PRIMARY KEY,
            batch_id INTEGER NOT NULL,
            trainer_id INTEGER NOT NULL,
            title VARCHAR(200) NOT NULL,
            date DATE NOT NULL,
            start_time TIME NOT NULL,
            end_time TIME NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id SERIAL PRIMARY KEY,
            session_id INTEGER NOT NULL,
            student_id INTEGER NOT NULL,
            status VARCHAR(20) NOT NULL,
            marked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    cur.close()
    conn.close()
    print("✅ Database tables created successfully!")

# ---------- AUTH ENDPOINTS ----------
@app.post("/auth/signup")
def signup(user: UserSignup):
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("SELECT id FROM users WHERE email = %s", (user.email,))
    if cur.fetchone():
        cur.close()
        conn.close()
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed = hash_password(user.password)
    cur.execute(
        "INSERT INTO users (name, email, hashed_password, role, institution_id) VALUES (%s, %s, %s, %s, %s) RETURNING id",
        (user.name, user.email, hashed, user.role, user.institution_id)
    )
    user_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    
    token = create_access_token(user_id, user.role)
    return {"message": "User created successfully", "access_token": token, "token_type": "bearer"}

@app.post("/auth/login")
def login(user: UserLogin):
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("SELECT id, email, hashed_password, role, institution_id FROM users WHERE email = %s", (user.email,))
    db_user = cur.fetchone()
    
    if not db_user:
        cur.close()
        conn.close()
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not verify_password(user.password, db_user[2]):
        cur.close()
        conn.close()
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    cur.close()
    conn.close()
    
    token = create_access_token(db_user[0], db_user[3], db_user[4])
    return {"access_token": token, "token_type": "bearer"}

@app.post("/auth/monitoring-token")
def get_monitoring_token(request: MonitoringTokenRequest, user_payload: dict = Depends(get_current_user)):
    if user_payload.get("role") != "monitoring_officer":
        raise HTTPException(status_code=403, detail="Only monitoring officers can get monitoring token")
    valid_key = os.getenv("MONITORING_API_KEY", "capi_key")
    if request.key != valid_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    monitoring_token = create_monitoring_token(user_payload.get("user_id"), user_payload.get("role"))
    return {"access_token": monitoring_token, "token_type": "bearer", "expires_in": "1 hour"}

# ---------- BATCH ENDPOINTS ----------
@app.post("/batches")
def create_batch(batch: BatchCreate, user_payload: dict = Depends(get_current_user)):
    check_role(user_payload, ["trainer", "institution"])
    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO batches (name, institution_id) VALUES (%s, %s) RETURNING id", (batch.name, batch.institution_id))
    batch_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return {"message": "Batch created", "batch_id": batch_id}

@app.post("/batches/{batch_id}/invite")
def generate_invite(batch_id: int, user_payload: dict = Depends(get_current_user)):
    check_role(user_payload, ["trainer"])
    token = secrets.token_urlsafe(32)
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO batch_invites (batch_id, token, created_by, expires_at) VALUES (%s, %s, %s, NOW() + INTERVAL '7 days')",
        (batch_id, token, user_payload.get("user_id"))
    )
    conn.commit()
    cur.close()
    conn.close()
    return {"invite_token": token}

@app.post("/batches/join")
def join_batch(join_data: BatchJoin, user_payload: dict = Depends(get_current_user)):
    check_role(user_payload, ["student"])
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("SELECT batch_id FROM batch_invites WHERE token = %s AND used = false AND expires_at > NOW()", (join_data.token,))
    invite = cur.fetchone()
    if not invite:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Invalid or expired invite")
    
    cur.execute("SELECT * FROM batch_students WHERE batch_id = %s AND student_id = %s", (invite[0], user_payload.get("user_id")))
    if cur.fetchone():
        cur.close()
        conn.close()
        raise HTTPException(status_code=400, detail="Already enrolled")
    
    cur.execute("INSERT INTO batch_students (batch_id, student_id) VALUES (%s, %s)", (invite[0], user_payload.get("user_id")))
    cur.execute("UPDATE batch_invites SET used = true WHERE token = %s", (join_data.token,))
    conn.commit()
    cur.close()
    conn.close()
    return {"message": "Successfully joined batch"}

# ---------- SESSION ENDPOINTS ----------
@app.post("/sessions")
def create_session(session: SessionCreate, user_payload: dict = Depends(get_current_user)):
    check_role(user_payload, ["trainer"])
    conn = get_db()
    cur = conn.cursor()
    
    session_date = date.fromisoformat(session.date)
    start_time = time.fromisoformat(session.start_time)
    end_time = time.fromisoformat(session.end_time)
    
    cur.execute(
        "INSERT INTO sessions (batch_id, trainer_id, title, date, start_time, end_time, created_at) VALUES (%s, %s, %s, %s, %s, %s, NOW()) RETURNING id",
        (session.batch_id, user_payload.get("user_id"), session.title, session_date, start_time, end_time)
    )
    session_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return {"message": "Session created", "session_id": session_id}

@app.get("/sessions/{session_id}/attendance")
def get_session_attendance(session_id: int, user_payload: dict = Depends(get_current_user)):
    check_role(user_payload, ["trainer"])
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("SELECT batch_id FROM sessions WHERE id = %s", (session_id,))
    session = cur.fetchone()
    if not session:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Session not found")
    
    cur.execute("SELECT a.*, u.name FROM attendance a JOIN users u ON a.student_id = u.id WHERE a.session_id = %s", (session_id,))
    attendance = cur.fetchall()
    cur.close()
    conn.close()
    
    result = []
    for row in attendance:
        result.append(dict(row))
    return {"session_id": session_id, "attendance": result}

# ---------- ATTENDANCE ENDPOINTS ----------
@app.post("/attendance/mark")
def mark_attendance(attendance_data: AttendanceMark, user_payload: dict = Depends(get_current_user)):
    check_role(user_payload, ["student"])
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("SELECT batch_id FROM sessions WHERE id = %s", (attendance_data.session_id,))
    session = cur.fetchone()
    if not session:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Session not found")
    
    cur.execute("SELECT * FROM batch_students WHERE batch_id = %s AND student_id = %s", (session[0], user_payload.get("user_id")))
    if not cur.fetchone():
        cur.close()
        conn.close()
        raise HTTPException(status_code=403, detail="You are not enrolled in this session's batch")
    
    cur.execute("SELECT * FROM attendance WHERE session_id = %s AND student_id = %s", (attendance_data.session_id, user_payload.get("user_id")))
    if cur.fetchone():
        cur.close()
        conn.close()
        raise HTTPException(status_code=400, detail="Attendance already marked for this session")
    
    cur.execute("INSERT INTO attendance (session_id, student_id, status) VALUES (%s, %s, %s)", (attendance_data.session_id, user_payload.get("user_id"), attendance_data.status))
    conn.commit()
    cur.close()
    conn.close()
    return {"message": "Attendance marked successfully"}

# ---------- MONITORING ENDPOINTS ----------
@app.get("/monitoring/attendance")
def monitoring_attendance(authorization: str = Header(None)):
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
    
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM attendance")
    attendance = cur.fetchall()
    cur.close()
    conn.close()
    
    result = []
    for row in attendance:
        result.append(dict(row))
    return {"attendance": result}

@app.api_route("/monitoring/attendance", methods=["POST", "PUT", "DELETE", "PATCH"])
def monitoring_attendance_method_not_allowed():
    raise HTTPException(status_code=405, detail="Method Not Allowed")

# ---------- SUMMARY ENDPOINTS ----------
@app.get("/batches/{batch_id}/summary")
def batch_summary(batch_id: int, user_payload: dict = Depends(get_current_user)):
    check_role(user_payload, ["institution"])
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM batches WHERE id = %s", (batch_id,))
    batch = cur.fetchone()
    if not batch:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Batch not found")
    
    if batch[2] != user_payload.get("institution_id"):
        cur.close()
        conn.close()
        raise HTTPException(status_code=403, detail="You don't have access to this batch")
    
    cur.execute("SELECT COUNT(*) FROM batch_students WHERE batch_id = %s", (batch_id,))
    total_students = cur.fetchone()[0]
    
    cur.close()
    conn.close()
    return {"batch_id": batch_id, "batch_name": batch[1], "total_students": total_students}

@app.get("/institutions/{institution_id}/summary")
def institution_summary(institution_id: int, user_payload: dict = Depends(get_current_user)):
    check_role(user_payload, ["programme_manager"])
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM users WHERE id = %s AND role = 'institution'", (institution_id,))
    institution = cur.fetchone()
    if not institution:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Institution not found")
    
    cur.execute("SELECT id, name FROM batches WHERE institution_id = %s", (institution_id,))
    batches = cur.fetchall()
    
    cur.execute("SELECT COUNT(DISTINCT student_id) FROM batch_students bs JOIN batches b ON bs.batch_id = b.id WHERE b.institution_id = %s", (institution_id,))
    total_students = cur.fetchone()[0]
    
    cur.close()
    conn.close()
    
    return {
        "institution_id": institution_id,
        "institution_name": institution[1],
        "total_batches": len(batches),
        "total_students": total_students,
        "batches": [{"id": b[0], "name": b[1]} for b in batches]
    }

@app.get("/programme/summary")
def programme_summary(user_payload: dict = Depends(get_current_user)):
    check_role(user_payload, ["programme_manager"])
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) FROM users WHERE role = 'institution'")
    total_institutions = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM users WHERE role = 'student'")
    total_students = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM users WHERE role = 'trainer'")
    total_trainers = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM batches")
    total_batches = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM sessions")
    total_sessions = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM attendance")
    total_attendance = cur.fetchone()[0]
    
    cur.close()
    conn.close()
    
    return {
        "total_institutions": total_institutions,
        "total_students": total_students,
        "total_trainers": total_trainers,
        "total_batches": total_batches,
        "total_sessions": total_sessions,
        "total_attendance_records": total_attendance
    }

@app.get("/")
def root():
    return {"message": "SkillBridge API is running", "docs": "/docs", "version": "1.0.0"}
