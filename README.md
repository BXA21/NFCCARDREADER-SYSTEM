# NFC Attendance System

A complete, production-ready web-based attendance management system that uses NFC smart cards for employee clock-in/clock-out operations.

## 🎯 Features

- **NFC Card-Based Attendance**: Clock in/out with a simple card tap
- **Offline Support**: Reader agent buffers events when disconnected
- **Role-Based Access Control**: Employee, Supervisor, and HR Admin roles
- **Correction Requests**: Submit and approve attendance corrections
- **Comprehensive Reports**: Daily, weekly, and monthly attendance summaries
- **Payroll Export**: CSV export for seamless payroll integration
- **Audit Logging**: Complete audit trail of all system actions
- **Modern UI**: Beautiful, responsive interface built with React and Tailwind CSS

## 🏗️ Architecture

### Components

1. **Backend API** (FastAPI + PostgreSQL)
   - RESTful API with JWT authentication
   - Role-based authorization
   - Async SQLAlchemy with Alembic migrations

2. **Frontend** (React + TypeScript + Tailwind CSS)
   - Modern, responsive single-page application
   - Real-time updates with React Query
   - Accessible, mobile-first design

3. **Reader Agent** (Python + pyscard)
   - Interfaces with ACR122U NFC reader
   - Offline event buffering with SQLite
   - Automatic synchronization when online

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.11+ (for reader agent)
- Node.js 18+ (for frontend development)
- ACR122U NFC Reader with drivers installed

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd nfc-attendance-system
```

2. **Set up environment variables**
```bash
cp backend/.env.example backend/.env
# Edit backend/.env with your configuration
```

3. **Start the services**
```bash
# Start database and backend
docker-compose up -d

# The API will be available at http://localhost:8000
# API documentation at http://localhost:8000/docs
```

4. **Run database migrations**
```bash
docker-compose exec backend alembic upgrade head
```

5. **Create initial admin user**
```bash
docker-compose exec backend python -c "from app.utils.init_db import create_admin; create_admin()"
```

### Development

**Backend Development**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend Development** (Phase 6+)
```bash
cd frontend
npm install
npm run dev
```

**Reader Agent** (Phase 5+)
```bash
cd reader_agent
pip install -r requirements.txt
cp config.yaml.example config.yaml
# Edit config.yaml with your settings
python src/main.py
```

## 📋 Project Status

### ✅ **PRODUCTION READY** - Complete NFC Attendance System

All 7 core phases have been completed! The system is fully functional and ready for production use.

#### Phase 1-2: Foundation & Authentication ✅
- [x] Complete FastAPI project structure
- [x] PostgreSQL database with Docker
- [x] All SQLAlchemy models (8 entities)
- [x] Alembic migrations
- [x] JWT authentication with refresh tokens
- [x] Role-based access control (RBAC)
- [x] Audit logging middleware

#### Phase 3: Core Entities CRUD ✅
- [x] Employee management (create, edit, delete, search, filter)
- [x] NFC card issuance, revocation, and history
- [x] Shift scheduling and assignment

#### Phase 4: Attendance Processing ✅
- [x] Real-time attendance event recording
- [x] Auto IN/OUT detection
- [x] Duplicate prevention (60-second threshold)
- [x] Device authentication with API keys
- [x] Attendance reports and summaries

#### Phase 5: NFC Reader Agent ✅
- [x] ACR122U reader integration with pyscard
- [x] Real-time card UID reading
- [x] Offline buffering with SQLite
- [x] Automatic background synchronization
- [x] Console feedback and logging

#### Phase 6-7: React Frontend ✅
- [x] Modern responsive UI (React + TypeScript + Tailwind CSS)
- [x] Authentication with auto-refresh
- [x] Dashboard with real-time statistics
- [x] Complete employee management interface
- [x] Card issuance and management UI
- [x] Personal attendance history viewer

### 🎯 System is Ready!
The core NFC attendance system is **fully implemented and tested**. 
See [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) for complete documentation.

## 🔧 Technology Stack

### Backend
- **Framework**: FastAPI 0.109.0
- **Database**: PostgreSQL 15+
- **ORM**: SQLAlchemy 2.0+
- **Migrations**: Alembic
- **Auth**: JWT (python-jose)
- **Password Hashing**: bcrypt (passlib)

### Frontend (Phase 6+)
- **Framework**: React 18+
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: React Query
- **Routing**: React Router v6
- **Charts**: Recharts
- **Forms**: React Hook Form + Zod

### Reader Agent (Phase 5+)
- **Language**: Python 3.11+
- **NFC Library**: pyscard
- **HTTP Client**: httpx
- **Local Storage**: SQLite

## 📖 API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests (Phase 6+)
cd frontend
npm test

# Reader agent tests (Phase 5+)
cd reader_agent
pytest
```

## 📦 Database Schema

The system uses the following main entities:

- **Employee**: Staff member information
- **User**: Authentication and authorization
- **Card**: NFC card assignments
- **AttendanceEvent**: Clock-in/out records
- **CorrectionRequest**: Attendance correction workflow
- **Shift**: Work schedule definitions
- **Device**: NFC reader registration
- **AuditLog**: System action tracking

## 🔐 Security

- JWT-based authentication with refresh tokens
- Password hashing using bcrypt
- Role-based access control (RBAC)
- Input validation with Pydantic
- SQL injection prevention via SQLAlchemy ORM
- Complete audit logging

## 📄 License

This project is proprietary software developed for {{ COMPANY_NAME }}.

## 👥 Support

For support, please contact the development team or refer to the internal documentation.

---

**Built with ❤️ using FastAPI, React, and PostgreSQL**

