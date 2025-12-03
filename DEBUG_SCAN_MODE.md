# 🔍 Debug Guide - NFC Card Scanning Issue

## Problem
The NFC reader LED turns green (card detected) but the dashboard wizard doesn't show the card.

## ✅ What I Just Fixed

### **The Solution:**
I created a **centralized scan buffer** (`scan_buffer.py`) that properly shares card data between the attendance endpoint and the wizard polling endpoint.

### **Changes Made:**
1. ✅ Created `backend/app/utils/scan_buffer.py` - Singleton scan buffer
2. ✅ Updated `attendance.py` to use scan buffer for unassigned cards
3. ✅ Updated `cards_advanced.py` to read from scan buffer
4. ✅ Added debug logging (prints to console)
5. ✅ Added debug endpoints for troubleshooting

---

## 🧪 Step-by-Step Testing

### **Method 1: Test with Physical Card (Recommended)**

#### Step 1: Restart Backend
```bash
# Stop backend (Ctrl+C)
# Then restart with visible logs
cd backend
.\venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload
```

#### Step 2: Check Backend is Running
Open browser: http://localhost:8000/docs
Should see API documentation ✅

#### Step 3: Open Wizard
```
http://localhost:3000
Login: admin / admin123
Employees → Add Employee
Fill form → Click "Next: Scan NFC Card"
```

#### Step 4: Watch Backend Terminal
You should see:
```
[SCAN API] Frontend polling for card...
[SCAN API] No card in buffer
[SCAN API] Frontend polling for card...
[SCAN API] No card in buffer
```
(Repeats every 500ms)

#### Step 5: Tap Your Card
Use a **NEW/BLANK** card (not one already assigned!)

**Watch backend terminal:**
```
[ATTENDANCE] Unassigned card detected: 04NEW123456 - routing to scan buffer
[SCAN BUFFER] Card added: 04NEW123456 at 2025-12-03 14:30:00
```

Then within 500ms:
```
[SCAN API] Frontend polling for card...
[SCAN API] Found card in buffer: 04NEW123456
[SCAN API] Returning card to frontend: 04NEW123456
[SCAN BUFFER] Cleared
```

**Watch dashboard:**
- Within 500ms, should show "✓ Card Detected!"
- Shows card UID

---

### **Method 2: Test with Manual API Call (Debugging)**

Use this to test WITHOUT tapping a physical card:

#### Step 1: Open API Docs
```
http://localhost:8000/docs
```

#### Step 2: Authorize
- Click "Authorize" button
- Login: admin / admin123
- Click "Authorize" again

#### Step 3: Test Manual Card Addition
Find endpoint: `POST /api/v1/cards/scan-mode/test`

Execute with:
```json
{
  "card_uid": "TESTCARD123456"
}
```

Response:
```json
{
  "success": true,
  "message": "Test card TESTCARD123456 added to scan buffer",
  "test_instructions": "Now the wizard should detect this card within 500ms"
}
```

#### Step 4: Check Wizard
Open wizard (if not already open)
Within 500ms, should show:
```
✓ Card Detected!
Card UID: TESTCARD123456
```

---

### **Method 3: Debug with Status Endpoint**

#### Check Buffer Status Anytime
```
GET http://localhost:8000/api/v1/cards/scan-mode/debug
```

Response when empty:
```json
{
  "scan_buffer_status": {
    "has_card": false,
    "card_uid": null,
    "detected_at": null,
    "age_seconds": 0
  }
}
```

Response when card detected:
```json
{
  "scan_buffer_status": {
    "has_card": true,
    "card_uid": "04ABC123",
    "detected_at": "2025-12-03T14:30:00",
    "age_seconds": 2.5
  }
}
```

---

## 🐛 Common Issues & Solutions

### **Issue 1: Backend Terminal Shows No Logs**

**Problem:** No `[SCAN API]` or `[ATTENDANCE]` logs appearing

**Solution:**
```bash
# Make sure you're running backend correctly
cd backend
.\venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload

# You should see:
# INFO: Uvicorn running on http://0.0.0.0:8000
# INFO: Started reloader process...
# INFO: Application startup complete
```

---

### **Issue 2: Card Tap Shows "Card not found" Error**

**Problem:** Backend returns 404 error

**This means the card IS already assigned!**

**Solution:** Use a different, blank NFC card

**To check which cards are assigned:**
```
GET http://localhost:8000/api/v1/employees
```
Look for `has_active_card: true`

---

### **Issue 3: Backend Logs Show Card Detected But Frontend Doesn't**

**Problem:** 
```
[SCAN BUFFER] Card added: 04ABC123
[SCAN API] Frontend polling for card...
[SCAN API] No card in buffer  ← WRONG!
```

**This means timing issue or card expired**

**Solution:**
1. Card expires after 60 seconds
2. Make sure wizard is open BEFORE tapping card
3. Check system clock is correct

---

### **Issue 4: "Age Seconds" is Too High**

**Problem:** Debug endpoint shows `age_seconds: 75`

**This means card expired (>60 seconds old)**

**Solution:**
1. Clear buffer: `DELETE /api/v1/cards/scan-mode/clear`
2. Tap card again
3. Check within 60 seconds

---

### **Issue 5: Reader Agent Not Sending Cards**

**Problem:** No log like `[ATTENDANCE] Unassigned card detected`

**This means reader agent isn't running or not connected**

**Check:**
```bash
# Is reader agent running?
# Terminal 3 should show:
# [TIME] - __main__ - INFO - Starting main loop
```

**Restart reader agent:**
```bash
cd reader_agent
$env:DEVICE_API_KEY='test-reader-api-key-12345'
python src/main.py
```

---

## 📊 Expected Log Flow

### **Perfect Scenario:**

```
Backend Terminal:
═══════════════════════════════════════════════════
[SCAN API] Frontend polling for card...
[SCAN API] No card in buffer
[SCAN API] Frontend polling for card...
[SCAN API] No card in buffer

... (User taps card) ...

INFO: POST /api/v1/attendance-events HTTP/1.1 202
[ATTENDANCE] Unassigned card detected: 04XYZ789 - routing to scan buffer
[SCAN BUFFER] Card added: 04XYZ789 at 2025-12-03 14:30:00.123456

... (500ms later) ...

INFO: GET /api/v1/cards/scan-mode/latest HTTP/1.1 200
[SCAN API] Frontend polling for card...
[SCAN API] Found card in buffer: 04XYZ789
[SCAN API] Returning card to frontend: 04XYZ789
[SCAN BUFFER] Cleared
═══════════════════════════════════════════════════

Frontend:
═══════════════════════════════════════════════════
Step 2: Scanning... (pulsing animation)

... (After card tap) ...

✓ Card Detected!
Card UID: 04XYZ789
[Continue to Assignment] button appears
═══════════════════════════════════════════════════
```

---

## 🔥 Quick Test Commands

### **Test 1: Check Backend Health**
```bash
curl http://localhost:8000/health
```
Expected: `{"status":"healthy",...}`

### **Test 2: Check Scan Buffer Status**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/cards/scan-mode/debug
```

### **Test 3: Manually Add Test Card**
```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"card_uid":"TESTCARD999"}' \
  http://localhost:8000/api/v1/cards/scan-mode/test
```

### **Test 4: Check Latest Scanned Card**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/cards/scan-mode/latest
```

---

## 💡 Testing Checklist

Before reporting issues, verify:

- [ ] Backend running (port 8000)
- [ ] Frontend running (port 3000)
- [ ] Reader agent running
- [ ] Logged in as admin
- [ ] Wizard open on Step 2
- [ ] Using BLANK/NEW card (not assigned)
- [ ] Card UID not in database
- [ ] Backend logs visible
- [ ] Frontend console open (F12)

---

## 🎯 Success Criteria

You know it's working when:

1. ✅ Backend logs show card detection
2. ✅ Scan buffer logs show card added
3. ✅ Scan API logs show card retrieved
4. ✅ Frontend shows "Card Detected" within 500ms
5. ✅ Card UID displays correctly
6. ✅ Can proceed to Step 3

---

## 📞 If Still Not Working

### **Collect Debug Info:**

1. **Backend logs** (copy last 50 lines)
2. **Frontend console** (F12 → Console tab)
3. **Reader agent logs** (`reader_agent/reader_agent.log`)
4. **Debug endpoint response:**
   ```
   GET http://localhost:8000/api/v1/cards/scan-mode/debug
   ```

### **Manual Test:**

1. Go to http://localhost:8000/docs
2. Authorize as admin
3. Execute `POST /cards/scan-mode/test` with `{"card_uid":"TEST999"}`
4. Keep wizard open on Step 2
5. Within 500ms, wizard should detect TEST999

**If manual test works but physical tap doesn't:**
→ Issue is with reader agent communication

**If manual test doesn't work:**
→ Issue is with frontend polling or backend

---

## 🚀 After This Works

Once Step 2 (scanning) works:
- Step 3 (confirm) will work automatically ✅
- Step 4 (write) shows animation ✅
- Step 5 (test) works when you tap assigned card ✅

**Your complete wizard will be functional!** 🎉

---

**Try Method 2 (Manual API Test) first to isolate the issue!**

