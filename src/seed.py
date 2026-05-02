import asyncio
from datetime import date, time

from database import get_db_connection
from auth import hash_password

async def seed_data():
    print("🌱 Seeding database...")
    conn = await get_db_connection()
    
    # Clear existing data
    await conn.execute("TRUNCATE TABLE attendance, sessions, batch_invites, batch_students, batch_trainers, batches, users RESTART IDENTITY CASCADE")
    
    # Create Programme Manager
    await conn.execute(
        "INSERT INTO users (name, email, hashed_password, role) VALUES ($1, $2, $3, $4)",
        "Programme Manager", "pm@test.com", hash_password("password123"), "programme_manager"
    )
    print("   ✅ Created Programme Manager")
    
    # Create Monitoring Officer
    await conn.execute(
        "INSERT INTO users (name, email, hashed_password, role) VALUES ($1, $2, $3, $4)",
        "Monitoring Officer", "mo@test.com", hash_password("password123"), "monitoring_officer"
    )
    print("   ✅ Created Monitoring Officer")
    
    # Create institutions
    inst_a = await conn.fetchrow(
        "INSERT INTO users (name, email, hashed_password, role) VALUES ($1, $2, $3, $4) RETURNING id",
        "Institution A", "inst_a@test.com", hash_password("password123"), "institution"
    )
    inst_a_id = inst_a["id"]
    print("   ✅ Created Institution A")
    
    inst_b = await conn.fetchrow(
        "INSERT INTO users (name, email, hashed_password, role) VALUES ($1, $2, $3, $4) RETURNING id",
        "Institution B", "inst_b@test.com", hash_password("password123"), "institution"
    )
    inst_b_id = inst_b["id"]
    print("   ✅ Created Institution B")
    
    # Create trainers (4)
    trainers = []
    for i in range(1, 5):
        trainer = await conn.fetchrow(
            "INSERT INTO users (name, email, hashed_password, role, institution_id) VALUES ($1, $2, $3, $4, $5) RETURNING id",
            f"Trainer {i}", f"trainer{i}@test.com", hash_password("password123"), "trainer", 
            inst_a_id if i <= 2 else inst_b_id
        )
        trainers.append(trainer["id"])
    print("   ✅ Created 4 Trainers")
    
    # Create students (15)
    students = []
    for i in range(1, 16):
        student = await conn.fetchrow(
            "INSERT INTO users (name, email, hashed_password, role, institution_id) VALUES ($1, $2, $3, $4, $5) RETURNING id",
            f"Student {i}", f"student{i}@test.com", hash_password("password123"), "student", 
            inst_a_id if i <= 8 else inst_b_id
        )
        students.append(student["id"])
    print("   ✅ Created 15 Students")
    
    # Create batches (3)
    batches = []
    for i in range(1, 4):
        batch = await conn.fetchrow(
            "INSERT INTO batches (name, institution_id) VALUES ($1, $2) RETURNING id",
            f"Batch {i}", inst_a_id if i <= 2 else inst_b_id
        )
        batches.append(batch["id"])
    print("   ✅ Created 3 Batches")
    
    # Assign trainers to batches (many-to-many)
    await conn.execute("INSERT INTO batch_trainers (batch_id, trainer_id) VALUES ($1, $2)", batches[0], trainers[0])
    await conn.execute("INSERT INTO batch_trainers (batch_id, trainer_id) VALUES ($1, $2)", batches[0], trainers[1])
    await conn.execute("INSERT INTO batch_trainers (batch_id, trainer_id) VALUES ($1, $2)", batches[1], trainers[2])
    await conn.execute("INSERT INTO batch_trainers (batch_id, trainer_id) VALUES ($1, $2)", batches[2], trainers[3])
    print("   ✅ Assigned Trainers to Batches")
    
    # Assign students to batches (5 students per batch)
    for i, batch in enumerate(batches):
        for j in range(5):
            student_idx = i * 5 + j
            if student_idx < len(students):
                await conn.execute(
                    "INSERT INTO batch_students (batch_id, student_id) VALUES ($1, $2)", 
                    batch, students[student_idx]
                )
    print("   ✅ Assigned Students to Batches")
    
    # Create sessions (8 sessions across batches)
    session_titles = [
        "Introduction to Programming",
        "Variables and Data Types",
        "Control Flow",
        "Functions",
        "Object Oriented Programming",
        "Error Handling",
        "File Handling",
        "Final Project"
    ]
    
    start_time = time(10, 0, 0)  # 10:00:00 AM as time object
    end_time = time(12, 0, 0)    # 12:00:00 PM as time object
    
    for i in range(1, 9):
        batch_idx = (i - 1) % 3
        trainer_idx = (i - 1) % 4
        session_date = date(2026, 5, i)
        await conn.execute(
            "INSERT INTO sessions (batch_id, trainer_id, title, date, start_time, end_time) VALUES ($1, $2, $3, $4, $5, $6)",
            batches[batch_idx], trainers[trainer_idx], session_titles[i-1], 
            session_date, start_time, end_time
        )
    print("   ✅ Created 8 Sessions")
    
    # Create sample attendance records
    for session_id in range(1, 9):
        for student_id in students[:10]:
            await conn.execute(
                "INSERT INTO attendance (session_id, student_id, status) VALUES ($1, $2, $3)",
                session_id, student_id, "present"
            )
    print("   ✅ Created Sample Attendance Records")
    
    await conn.close()
    
    print("\n" + "="*50)
    print("✅ SEEDING COMPLETED SUCCESSFULLY!")
    print("="*50)
    print("\n📋 TEST ACCOUNTS (Email / Password):")
    print("   🔹 Student: student1@test.com / password123")
    print("   🔹 Trainer: trainer1@test.com / password123")
    print("   🔹 Institution: inst_a@test.com / password123")
    print("   🔹 Programme Manager: pm@test.com / password123")
    print("   🔹 Monitoring Officer: mo@test.com / password123")
    print("="*50)

if __name__ == "__main__":
    asyncio.run(seed_data())