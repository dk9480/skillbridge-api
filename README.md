# SkillBridge Attendance API

A production-ready REST API for a state-level skilling programme attendance management system with role-based access control and JWT authentication.

## 🚀 Live API URL

**Base URL:** `https://skillbridge-api-6l4p.onrender.com`

**API Documentation (Swagger UI):** `https://skillbridge-api-6l4p.onrender.com/docs`

> **Note:** The free tier on Render spins down after 15 minutes of inactivity. The first request may take 30-60 seconds to wake up.

---

## 📋 Test Accounts (5 Roles)

| Role | Email | Password |
|------|-------|----------|
| **Student** | `student1@test.com` | `password123` |
| **Trainer** | `trainer1@test.com` | `password123` |
| **Institution** | `inst_a@test.com` | `password123` |
| **Programme Manager** | `pm@test.com` | `password123` |
| **Monitoring Officer** | `mo@test.com` | `password123` |

---

## 🛠️ Local Setup Instructions

```bash
# 1. Clone the repository
git clone https://github.com/dk9480/skillbridge-api.git
cd skillbridge-api

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file with your database URL
cp .env.example .env
# Edit .env and add your Neon PostgreSQL URL

# 5. Seed the database
python src/seed.py

# 6. Run the API
```

## 📡 API Endpoints

### Authentication (No Auth Required)

| Method | Endpoint        | Description                     |
|--------|---------------|---------------------------------|
| POST   | /auth/signup  | Create new user account         |
| POST   | /auth/login   | Login and receive JWT token     |


uvicorn src.main:app --reload

# 7. Open browser at http://localhost:8000/docs
