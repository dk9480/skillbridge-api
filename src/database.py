# import os
# from dotenv import load_dotenv
# import asyncpg

# load_dotenv()

# DATABASE_URL = os.getenv("DATABASE_URL")

# async def get_db_connection():
#     """Create and return a database connection"""
#     conn = await asyncpg.connect(DATABASE_URL)
#     return conn

# async def init_db():
#     """Create all tables if they don't exist"""
#     conn = await get_db_connection()
    
#     # Create users table
#     await conn.execute('''
#         CREATE TABLE IF NOT EXISTS users (
#             id SERIAL PRIMARY KEY,
#             name VARCHAR(100) NOT NULL,
#             email VARCHAR(100) UNIQUE NOT NULL,
#             hashed_password VARCHAR(255) NOT NULL,
#             role VARCHAR(50) NOT NULL,
#             institution_id INTEGER,
#             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#         )
#     ''')
    
#     # Create batches table
#     await conn.execute('''
#         CREATE TABLE IF NOT EXISTS batches (
#             id SERIAL PRIMARY KEY,
#             name VARCHAR(100) NOT NULL,
#             institution_id INTEGER NOT NULL,
#             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#         )
#     ''')
    
#     # Create batch_trainers table (many-to-many)
#     await conn.execute('''
#         CREATE TABLE IF NOT EXISTS batch_trainers (
#             batch_id INTEGER NOT NULL,
#             trainer_id INTEGER NOT NULL,
#             PRIMARY KEY (batch_id, trainer_id)
#         )
#     ''')
    
#     # Create batch_students table (many-to-many)
#     await conn.execute('''
#         CREATE TABLE IF NOT EXISTS batch_students (
#             batch_id INTEGER NOT NULL,
#             student_id INTEGER NOT NULL,
#             PRIMARY KEY (batch_id, student_id)
#         )
#     ''')
    
#     # Create batch_invites table
#     await conn.execute('''
#         CREATE TABLE IF NOT EXISTS batch_invites (
#             id SERIAL PRIMARY KEY,
#             batch_id INTEGER NOT NULL,
#             token VARCHAR(255) UNIQUE NOT NULL,
#             created_by INTEGER NOT NULL,
#             expires_at TIMESTAMP NOT NULL,
#             used BOOLEAN DEFAULT FALSE
#         )
#     ''')
    
#     # Create sessions table
#     await conn.execute('''
#         CREATE TABLE IF NOT EXISTS sessions (
#             id SERIAL PRIMARY KEY,
#             batch_id INTEGER NOT NULL,
#             trainer_id INTEGER NOT NULL,
#             title VARCHAR(200) NOT NULL,
#             date DATE NOT NULL,
#             start_time TIME NOT NULL,
#             end_time TIME NOT NULL,
#             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#         )
#     ''')
    
#     # Create attendance table
#     await conn.execute('''
#         CREATE TABLE IF NOT EXISTS attendance (
#             id SERIAL PRIMARY KEY,
#             session_id INTEGER NOT NULL,
#             student_id INTEGER NOT NULL,
#             status VARCHAR(20) NOT NULL,
#             marked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#         )
#     ''')
    
#     await conn.close()
#     print("✅ Database tables created successfully!")

# async def close_db_connection(conn):
#     """Close database connection"""
#     await conn.close()



import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    """Create and return a database connection"""
    conn = psycopg2.connect(DATABASE_URL)
    return conn

def init_db():
    """Create all tables if they don't exist"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Create users table
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
    
    # Create batches table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS batches (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            institution_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create batch_trainers table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS batch_trainers (
            batch_id INTEGER NOT NULL,
            trainer_id INTEGER NOT NULL,
            PRIMARY KEY (batch_id, trainer_id)
        )
    ''')
    
    # Create batch_students table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS batch_students (
            batch_id INTEGER NOT NULL,
            student_id INTEGER NOT NULL,
            PRIMARY KEY (batch_id, student_id)
        )
    ''')
    
    # Create batch_invites table
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
    
    # Create sessions table
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
    
    # Create attendance table
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
