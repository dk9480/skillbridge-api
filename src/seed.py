from datetime import date, time
import psycopg2
import os
from dotenv import load_dotenv
from auth import hash_password

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def get_db():
    return psycopg2.connect(DATABASE_URL)

def seed_data():
    print("🌱 Seeding database...")
    conn = get_db()
    cur = conn.cursor()
    
    # Clear existing data
    cur.execute("TRUNCATE TABLE attendance, sessions, batch_invites, batch_students, batch_trainers, batches, users RESTART IDENTITY CASCADE")
    
    # Create Programme Manager
    cur.execute("INSERT INTO users (name, email, hashed_password, role) VALUES (%s, %s, %s, %s)",
                ("Programme Manager", "pm@test.com", hash_password("password123"), "programme_manager"))
    print("   ✅ Created Programme Manager")
    
    # Create Monitoring Officer
    cur.execute("INSERT INTO users (name, email, hashed_password, role) VALUES (%s, %s, %s, %s)",
                ("Monitoring Officer", "mo@test.com", hash_password("password123"), "monitoring_officer"))
    print("   ✅ Created Monitoring Officer")
    
    # Create institutions
    cur.execute("INSERT INTO users (name, email, hashed_password, role) VALUES (%s, %s, %s, %s) RETURNING id",
                ("Institution A", "inst_a@test.com", hash_password("password123"), "institution"))
    inst_a_id = cur.fetchone()[0]
    print("   ✅ Created Institution A")
    
    cur.execute("INSERT INTO users (name, email, hashed_password, role) VALUES (%s, %s, %s, %s) RETURNING id",
                ("Institution B", "inst_b@test.com", hash_password("password123"), "institution"))
    inst_b_id = cur.fetchone()[0]
    print("   ✅ Created Institution B")
    
    # Create trainers (4)
    trainers = []
    for i in range(1, 5):
        inst_id = inst_a_id if i <= 2 else inst_b_id
        cur.execute("INSERT INTO users (name, email, hashed_password, role, institution_id) VALUES (%s, %s, %s, %s, %s) RETURNING id",
                    (f"Trainer {i}", f"trainer{i}@test.com", hash_password("password123"), "trainer", inst_id))
        trainers.append(cur.fetchone()[0])
    print("   ✅ Created 4 Trainers")
    
    # Create students (15)
    students = []
    for i in range(1, 16):
        inst_id = inst_a_id if i <= 8 else inst_b_id
        cur.execute("INSERT INTO users (name, email, hashed_password, role, institution_id) VALUES (%s, %s, %s, %s, %s) RETURNING id",
                    (f"Student {i}", f"student{i}@test.com", hash_password("password123"), "student", inst_id))
        students.append(cur.fetchone()[0])
    print("   ✅ Created 15 Students")
    
    # Create batches (3)
    batches = []
    for i in range(1, 4):
        inst_id = inst_a_id if i <= 2 else inst_b_id
        cur.execute("INSERT INTO batches (name, institution_id) VALUES (%s, %s) RETURNING id",
                    (f"Batch {i}", inst_id))
        batches.append(cur.fetchone()[0])
    print("   ✅ Created 3 Batches")
    
    # Assign trainers to batches
    cur.execute("INSERT INTO batch_trainers (batch_id, trainer_id) VALUES (%s, %s)", (batches[0], trainers[0]))
    cur.execute("INSERT INTO batch_trainers (batch_id, trainer_id) VALUES (%s, %s)", (batches[0], trainers[1]))
    cur.execute("INSERT INTO batch_trainers (batch_id, trainer_id) VALUES (%s, %s)", (batches[1], trainers[2]))
    cur.execute("INSERT INTO batch_trainers (batch_id, trainer_id) VALUES (%s, %s)", (batches[2], trainers[3]))
    print("   ✅ Assigned Trainers to Batches")
    
    # Assign students to batches (5 per batch)
    for i, batch in enumerate(batches):
        for j in range(5):
            student_idx = i * 5 + j
            if student_idx < len(students):
                cur.execute("INSERT INTO batch_students (batch_id, student_id) VALUES (%s, %s)", (batch, students[student_idx]))
    print("   ✅ Assigned Students to Batches")
    
    # Create sessions (8)
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
    
    start_time = time(10, 0, 0)
    end_time = time(12, 0, 0)
    
    for i in range(1, 9):
        batch_idx = (i - 1) % 3
        trainer_idx = (i - 1) % 4
        session_date = date(2026, 5, i)
        cur.execute(
            "INSERT INTO sessions (batch_id, trainer_id, title, date, start_time, end_time) VALUES (%s, %s, %s, %s, %s, %s)",
            (batches[batch_idx], trainers[trainer_idx], session_titles[i-1], session_date, start_time, end_time)
        )
    print("   ✅ Created 8 Sessions")
    
    # Create attendance records (first 10 students for all sessions)
    for session_id in range(1, 9):
        for student_id in students[:10]:
            cur.execute("INSERT INTO attendance (session_id, student_id, status) VALUES (%s, %s, %s)",
                        (session_id, student_id, "present"))
    print("   ✅ Created Sample Attendance Records")
    
    conn.commit()
    cur.close()
    conn.close()
    
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
    seed_data()
