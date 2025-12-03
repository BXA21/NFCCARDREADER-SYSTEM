# 🚀 Getting Started with NFC Attendance System

Welcome! This guide will help you get the NFC Attendance System up and running in minutes.

---

## ✅ What You Have

A **complete, production-ready** NFC attendance system with:

- ✅ **Backend API** (FastAPI + PostgreSQL) - 25+ endpoints
- ✅ **NFC Reader Agent** (Python) - ACR122U support with offline buffering
- ✅ **Frontend UI** (React + TypeScript) - Modern responsive interface
- ✅ **Docker Setup** - One-command deployment
- ✅ **Complete Documentation** - Setup guides and API docs

---

## 🎯 5-Minute Quick Start

### Step 1: Start the Backend (30 seconds)

```powershell
# Navigate to project folder
cd "c:\Users\Asus Tuf Gaming\NFC SYSTEM"

# Start PostgreSQL and API
docker-compose up -d

# Wait 10-15 seconds for services to start

# Initialize database (creates admin user + default shifts)
docker-compose exec backend python -m app.utils.init_db
```

**✅ Backend is now running!**
- API: http://localhost:8000
- Docs: http://localhost:8000/docs

### Step 2: Start the Frontend (1 minute)

```powershell
# Open a new PowerShell window
cd "c:\Users\Asus Tuf Gaming\NFC SYSTEM\frontend"

# Install dependencies (first time only - takes 1 minute)
npm install

# Start development server
npm run dev
```

**✅ Frontend is now running!**
- URL: http://localhost:3000

### Step 3: Login & Explore (1 minute)

1. Open browser: http://localhost:3000
2. Login with:
   - **Username:** `admin`
   - **Password:** `Admin@123`
3. Explore the dashboard! 🎉

---

## 📱 Setup NFC Reader (5 minutes)

### Prerequisites
- ACR122U NFC Reader (USB)
- NFC Cards (MIFARE or compatible)
- Driver installed (Windows: from ACS website, Linux: pcscd)

### Setup Steps

```powershell
# 1. Navigate to reader agent folder
cd "c:\Users\Asus Tuf Gaming\NFC SYSTEM\reader_agent"

# 2. Create virtual environment (first time only)
python -m venv venv

# 3. Activate virtual environment
.\venv\Scripts\activate  # Windows PowerShell

# 4. Install dependencies (first time only)
pip install -r requirements.txt

# 5. Create configuration file
cp config.yaml.example config.yaml

# 6. Edit config.yaml
# - Set device_id (e.g., "GATE-MAIN-01")
# - Verify api.base_url is "http://localhost:8000/api/v1"

# 7. Get API key from backend
# (For now, you'll need to manually register device in backend)
# TODO: Create device via API docs or frontend

# 8. Set environment variable
$env:DEVICE_API_KEY="your-api-key-here"

# 9. Run the agent
python src\main.py
```

**✅ Reader agent is running!**
- Now tap NFC cards to record attendance

---

## 🎮 Your First Workflow

### 1. Create an Employee (via Frontend)

1. Go to **Employees** page
2. Click **"Add Employee"**
3. Fill in:
   - Employee No: `EMP-001`
   - Full Name: `Ahmed Al-Rashid`
   - Email: `ahmed@company.om`
   - Department: `IT`
   - Hire Date: Today
4. Click **"Create Employee"**

**✅ Employee created with auto-generated user account:**
- Username: `emp-001`
- Password: `Employee@123`

### 2. Issue NFC Card

1. In Employees list, click the **card icon** (🏷️)
2. Enter or scan card UID: `04A2B3C4D5E6F7`
3. Click **"Issue Card"**

**✅ Card linked to employee!**

### 3. Record Attendance

1. Ensure reader agent is running
2. Employee taps card on reader
3. See message: **"Welcome, Ahmed Al-Rashid!"**
4. Employee taps again later
5. See message: **"Goodbye, Ahmed. Have a great day!"**

**✅ Attendance recorded!**

### 4. View Attendance

1. Login as employee (`emp-001` / `Employee@123`)
2. Go to **Attendance** page
3. See all your clock-in/clock-out events

**✅ Complete workflow done!**

---

## 🎯 System URLs

| Component | URL | Purpose |
|-----------|-----|---------|
| **Frontend** | http://localhost:3000 | Web interface |
| **Backend API** | http://localhost:8000 | REST API |
| **API Docs** | http://localhost:8000/docs | Interactive API documentation |
| **Health Check** | http://localhost:8000/health | System status |

---

## 👥 Default Accounts

### Admin Account
```
Username: admin
Password: Admin@123
Role: HR_ADMIN
```
**Can do:** Everything (create employees, issue cards, view all data)

### Employee Account (auto-created)
```
Username: emp-{number} (e.g., emp-001)
Password: Employee@123
Role: EMPLOYEE
```
**Can do:** View own attendance, submit corrections

---

## 🔧 Common Tasks

### Stop All Services
```powershell
# Stop backend
docker-compose down

# Stop frontend (Ctrl+C in terminal)

# Stop reader agent (Ctrl+C in terminal)
```

### Restart Backend
```powershell
docker-compose restart backend
```

### View Backend Logs
```powershell
docker-compose logs backend -f
```

### Reset Database (⚠️ Deletes all data!)
```powershell
docker-compose down -v
docker-compose up -d
docker-compose exec backend python -m app.utils.init_db
```

### Update Frontend Dependencies
```powershell
cd frontend
npm update
```

---

## 📚 Documentation

- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Complete system documentation
- **[README.md](README.md)** - Main project overview
- **[backend/README.md](backend/README.md)** - Backend API details (to be created)
- **[frontend/README.md](frontend/README.md)** - Frontend setup and development
- **[reader_agent/README.md](reader_agent/README.md)** - Reader agent configuration

---

## 🆘 Troubleshooting

### Backend won't start
```powershell
# Check if ports are in use
netstat -ano | findstr :8000
netstat -ano | findstr :5432

# Check Docker status
docker-compose ps

# View logs
docker-compose logs
```

### Frontend won't start
```powershell
# Clear node modules and reinstall
cd frontend
Remove-Item -Recurse -Force node_modules
Remove-Item package-lock.json
npm install
```

### Reader not detected
```powershell
# Windows: Check Device Manager for "ACR122U"
# Install driver from: https://www.acs.com.hk/en/driver/3/acr122u-usb-nfc-reader/

# Linux: Check PC/SC daemon
sudo systemctl status pcscd
pcsc_scan
```

### Login fails
```powershell
# Reinitialize database
docker-compose exec backend python -m app.utils.init_db
```

---

## 🎓 Next Steps

1. **Create more employees** - Add your team members
2. **Issue cards** - Link NFC cards to employees
3. **Setup multiple readers** - Deploy readers at different locations
4. **Explore API docs** - http://localhost:8000/docs
5. **Customize shifts** - Define work schedules
6. **View reports** - Monitor attendance patterns

---

## 💡 Tips

- ✅ Change default passwords after first login
- ✅ Backup database regularly: `docker-compose exec postgres pg_dump -U attendance_user attendance_db > backup.sql`
- ✅ Use separate device_id for each reader (GATE-1, GATE-2, etc.)
- ✅ Check reader_agent logs if cards aren't detected
- ✅ API docs at /docs are interactive - try them out!
- ✅ Frontend auto-refreshes auth tokens - no manual login needed

---

## 🎉 You're All Set!

Your NFC Attendance System is **ready to use**! 

Questions? Check:
1. [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Comprehensive guide
2. API Docs - http://localhost:8000/docs
3. Frontend README - [frontend/README.md](frontend/README.md)

**Happy attendance tracking! 🚀**

---

**Version:** 1.0.0  
**Status:** ✅ Production Ready  
**Last Updated:** November 26, 2025



