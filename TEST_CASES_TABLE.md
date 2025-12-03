# Comprehensive Test Case Table - NFC Attendance System

## Complete Test Coverage for All System Components

| Test Case ID | Feature / Module | Description | Preconditions | Test Steps | Expected Result | Pass/Fail Conditions |
|-------------|------------------|-------------|---------------|-----------|-----------------|---------------------|
| **TC-AUTH-01** | Authentication - Login | Verify user can login with valid credentials and receive JWT tokens | - User account exists in database<br>- User is active<br>- Backend API running | 1. Navigate to login page<br>2. Enter valid username (e.g., "admin")<br>3. Enter valid password<br>4. Click "Login" button<br>5. Verify response contains access_token and refresh_token | - HTTP 200 status code<br>- Response contains access_token (JWT format)<br>- Response contains refresh_token<br>- Token type is "bearer"<br>- User object returned with id, username, role, email<br>- User redirected to dashboard<br>- Last login timestamp updated in database | **Pass**: All tokens received and valid JWT format<br>**Fail**: Missing tokens, invalid format, HTTP error, or no redirect |
| **TC-AUTH-02** | Authentication - Invalid Credentials | Verify system rejects login with incorrect password | - User account exists in database<br>- Backend API running | 1. Navigate to login page<br>2. Enter valid username<br>3. Enter incorrect password<br>4. Click "Login" button<br>5. Observe error message | - HTTP 401 Unauthorized status<br>- Error message: "Incorrect username or password"<br>- No tokens generated<br>- User remains on login page<br>- No database changes | **Pass**: 401 error returned with proper message<br>**Fail**: Login succeeds, wrong error code, or no error message |
| **TC-AUTH-03** | Authentication - Token Refresh | Verify refresh token can generate new access token | - User logged in successfully<br>- Valid refresh_token obtained<br>- Access token expired or about to expire | 1. Make POST request to `/api/v1/auth/refresh`<br>2. Include valid refresh_token in request body<br>3. Verify response contains new tokens<br>4. Attempt API call with new access_token | - HTTP 200 status code<br>- New access_token received<br>- New refresh_token received<br>- New tokens are different from old ones<br>- New access_token works for authenticated requests | **Pass**: New valid tokens received and functional<br>**Fail**: Token refresh fails, same tokens returned, or new token non-functional |
| **TC-AUTH-04** | Authorization - Role-Based Access Control | Verify EMPLOYEE role cannot access HR_ADMIN endpoints | - Employee user logged in<br>- Employee role verified<br>- HR_ADMIN endpoint exists (e.g., create employee) | 1. Login as EMPLOYEE user<br>2. Obtain access token<br>3. Attempt POST to `/api/v1/employees` (create employee)<br>4. Observe response | - HTTP 403 Forbidden status<br>- Error message indicates insufficient permissions<br>- No employee created in database<br>- Audit log records unauthorized attempt | **Pass**: 403 error, no data modified<br>**Fail**: Employee created, or wrong status code |
| **TC-EMP-01** | Employee Management - Create Employee | Verify HR Admin can create new employee with valid data | - User logged in with HR_ADMIN role<br>- Unique employee_no available (e.g., "EMP-100")<br>- Valid email format | 1. Navigate to Employees page<br>2. Click "Add Employee" button<br>3. Fill form: employee_no="EMP-100", full_name="John Doe", email="john@company.com", department="Engineering", hire_date="2025-11-01"<br>4. Submit form<br>5. Verify employee created | - HTTP 201 Created status<br>- Employee record created in database<br>- Default user account created (username=employee_no)<br>- Default password set to "Employee@123"<br>- Employee status set to ACTIVE<br>- Success notification displayed<br>- Employee appears in list | **Pass**: Employee created with all fields correct<br>**Fail**: Creation fails, missing fields, or duplicate check fails |
| **TC-EMP-02** | Employee Management - Duplicate Employee Number | Verify system prevents duplicate employee numbers | - Existing employee with employee_no "EMP-100"<br>- HR_ADMIN logged in | 1. Attempt to create new employee<br>2. Use employee_no="EMP-100" (already exists)<br>3. Fill other fields with valid data<br>4. Submit form | - HTTP 400 Bad Request status<br>- Error message: "Employee number already exists"<br>- No new employee created<br>- Database maintains integrity<br>- Form shows validation error | **Pass**: 400 error with proper message, no duplicate created<br>**Fail**: Duplicate employee created or wrong error |
| **TC-EMP-03** | Employee Management - Search and Filter | Verify employee list filtering by department and status | - Multiple employees exist in database<br>- Employees in different departments (Engineering, HR, Sales)<br>- Mix of ACTIVE and INACTIVE employees<br>- User authenticated | 1. Navigate to Employees page<br>2. Select department filter: "Engineering"<br>3. Select status filter: "ACTIVE"<br>4. Apply filters<br>5. Verify results | - Only employees matching both filters displayed<br>- Pagination works correctly<br>- Total count reflects filtered results<br>- No employees from other departments shown<br>- No INACTIVE employees shown<br>- Filter persists on page refresh | **Pass**: Correct employees filtered and displayed<br>**Fail**: Wrong employees shown or filter fails |
| **TC-EMP-04** | Employee Management - Update Employee | Verify HR Admin can update employee information | - Employee exists with id<br>- HR_ADMIN logged in<br>- New email available | 1. Navigate to employee detail page<br>2. Click "Edit" button<br>3. Change email to "newemail@company.com"<br>4. Change department to "Sales"<br>5. Save changes<br>6. Verify update | - HTTP 200 OK status<br>- Employee record updated in database<br>- Updated_at timestamp changed<br>- Email validation passed<br>- User sees success message<br>- Changes reflected in employee list<br>- Audit log records update | **Pass**: All changes saved correctly<br>**Fail**: Update fails or data incorrect |
| **TC-CARD-01** | Card Management - Issue Card to Employee | Verify HR Admin can issue NFC card to active employee | - Active employee without card<br>- HR_ADMIN logged in<br>- Valid card UID read from NFC reader (e.g., "04A2B3C4D5E6F7") | 1. Navigate to employee detail page<br>2. Click "Issue Card" button<br>3. Enter card_uid: "04A2B3C4D5E6F7"<br>4. Submit form<br>5. Verify card created | - HTTP 201 Created status<br>- Card record created in database<br>- Card status set to ACTIVE<br>- Card linked to employee (employee_id)<br>- issued_at timestamp recorded<br>- Employee has_active_card flag = true<br>- Success message displayed | **Pass**: Card issued and linked correctly<br>**Fail**: Card creation fails or duplicate UID |
| **TC-CARD-02** | Card Management - Prevent Duplicate Card UID | Verify system prevents issuing card with existing UID | - Card with UID "04A2B3C4D5E6F7" already exists<br>- HR_ADMIN logged in<br>- Different employee without card | 1. Attempt to issue card to second employee<br>2. Enter same card_uid: "04A2B3C4D5E6F7"<br>3. Submit form | - HTTP 400 Bad Request status<br>- Error message: "Card UID already exists"<br>- No new card created<br>- First employee's card remains unchanged<br>- Database integrity maintained | **Pass**: Duplicate prevented with proper error<br>**Fail**: Duplicate card created |
| **TC-CARD-03** | Card Management - Revoke Card | Verify HR Admin can revoke an active card | - Employee with ACTIVE card<br>- HR_ADMIN logged in | 1. Navigate to employee's card management<br>2. Select active card<br>3. Click "Revoke Card" button<br>4. Confirm revocation | - HTTP 200 OK status<br>- Card status changed to REVOKED<br>- Card cannot be used for attendance<br>- revoked_at timestamp recorded<br>- Employee can receive new card<br>- Success message displayed<br>- Audit log records action | **Pass**: Card revoked successfully<br>**Fail**: Card still ACTIVE or revocation fails |
| **TC-SHIFT-01** | Shift Management - Create Shift | Verify HR Admin can create new shift schedule | - HR_ADMIN logged in<br>- Unique shift name available | 1. Navigate to Shifts page<br>2. Click "Create Shift" button<br>3. Enter name="Morning Shift", start_time="08:00:00", end_time="16:00:00", grace_minutes=15<br>4. Set is_active=true<br>5. Submit form | - HTTP 201 Created status<br>- Shift record created in database<br>- Shift appears in shifts list<br>- Grace period properly set<br>- is_active flag set to true<br>- Success notification shown | **Pass**: Shift created with correct times<br>**Fail**: Creation fails or time validation fails |
| **TC-SHIFT-02** | Shift Management - Assign Shift to Employee | Verify HR Admin can assign shift to employee with date range | - Shift exists (id available)<br>- Employee exists (id available)<br>- HR_ADMIN logged in | 1. Navigate to employee shift assignments<br>2. Click "Assign Shift" button<br>3. Select shift_id<br>4. Set effective_from="2025-11-27"<br>5. Leave effective_to=null (ongoing)<br>6. Submit | - HTTP 201 Created status<br>- EmployeeShift record created<br>- Assignment linked to both employee and shift<br>- Previous overlapping assignments ended (effective_to set)<br>- Employee count for shift incremented<br>- Assignment visible in employee profile | **Pass**: Shift assigned and overlaps handled<br>**Fail**: Assignment fails or overlaps not handled |
| **TC-ATT-01** | Attendance Recording - Valid Card Tap (Clock In) | Verify attendance recorded when valid card tapped on reader | - Employee with ACTIVE card<br>- Card UID: "04A2B3C4D5E6F7"<br>- Employee status: ACTIVE<br>- Reader agent connected to API<br>- Device registered with valid API key<br>- No recent taps (>60 seconds ago) | 1. Employee taps NFC card on ACR122U reader<br>2. Reader reads UID: "04A2B3C4D5E6F7"<br>3. Reader agent sends POST to `/api/v1/attendance-events`<br>4. Include X-API-Key header<br>5. Verify response | - HTTP 201 Created status<br>- AttendanceEvent created with event_type=IN<br>- event_timestamp matches tap time<br>- device_id recorded<br>- source=ONLINE<br>- Welcome message: "Welcome, [Employee Name]!"<br>- Device status updated to ONLINE<br>- Event visible in attendance report | **Pass**: Event created with correct details<br>**Fail**: Event not created or wrong event_type |
| **TC-ATT-02** | Attendance Recording - Auto-Detect Clock Out | Verify system auto-detects OUT event after IN event | - Same employee as TC-ATT-01<br>- Previous IN event exists today<br>- More than 60 seconds since last tap | 1. Same employee taps card again<br>2. Reader sends attendance event<br>3. No event_type specified in request<br>4. System auto-determines event type | - HTTP 201 Created status<br>- AttendanceEvent created with event_type=OUT (auto-detected)<br>- Goodbye message: "Goodbye, [Employee Name]. Have a great day!"<br>- Both IN and OUT events exist for today<br>- Event timeline logically correct | **Pass**: OUT event auto-detected correctly<br>**Fail**: Wrong event_type or detection fails |
| **TC-ATT-03** | Attendance Recording - Prevent Duplicate Tap | Verify system prevents duplicate events within 60 seconds | - Employee tapped card 30 seconds ago<br>- Previous event recorded in database | 1. Same employee taps card again within 60 seconds<br>2. Reader agent sends request<br>3. Check response | - HTTP 400 Bad Request status<br>- Error message: "Duplicate event detected. Please wait 60 seconds between taps."<br>- No new attendance event created<br>- Only one event exists in database<br>- Anti-passback logic enforced | **Pass**: Duplicate prevented with proper error<br>**Fail**: Duplicate event created |
| **TC-ATT-04** | Attendance Recording - Invalid Card Rejection | Verify system rejects tap from non-existent or inactive card | - Card UID "INVALID123" not in database OR card status=REVOKED<br>- Reader agent functional | 1. Unknown card tapped on reader<br>2. Reader sends UID "INVALID123"<br>3. API processes request<br>4. Check response | - HTTP 404 Not Found (if card doesn't exist)<br>- OR HTTP 400 Bad Request (if card REVOKED/LOST)<br>- Error message indicates card not found or inactive<br>- No attendance event created<br>- Reader displays error to user<br>- Security audit logged | **Pass**: Invalid card rejected properly<br>**Fail**: Event created for invalid card |
| **TC-ATT-05** | Attendance Reporting - Get My Attendance | Verify employee can view their own attendance history | - Employee logged in<br>- Employee has attendance events in date range<br>- Date range: 2025-11-20 to 2025-11-27 | 1. Login as employee<br>2. Navigate to "My Attendance" page<br>3. Set from_date="2025-11-20"<br>4. Set to_date="2025-11-27"<br>5. Request loads data | - HTTP 200 OK status<br>- Only employee's own events returned<br>- Events within date range<br>- Pagination works (items, total, page, page_size)<br>- Each event shows: timestamp, event_type (IN/OUT), device_id<br>- Events ordered by timestamp ascending<br>- No other employees' data visible | **Pass**: Correct events displayed for date range<br>**Fail**: Wrong data, missing events, or security breach |
| **TC-ATT-06** | Attendance Reporting - Attendance Report with Filters | Verify HR can generate filtered attendance report | - HR_ADMIN or SUPERVISOR logged in<br>- Multiple employees with attendance data<br>- Filter parameters: department="Engineering", date range | 1. Navigate to Attendance Report page<br>2. Set from_date="2025-11-01", to_date="2025-11-30"<br>3. Select department="Engineering"<br>4. Select employee (optional)<br>5. Set page=1, page_size=20<br>6. Submit filters | - HTTP 200 OK status<br>- Only Engineering department employees shown<br>- Events within date range<br>- Pagination metadata correct (total, pages)<br>- Page_size respected (max 20 items)<br>- Can navigate between pages<br>- Export button available<br>- Summary statistics displayed | **Pass**: Correct filtered data with pagination<br>**Fail**: Wrong data, filter not applied, or pagination broken |
| **TC-ATT-07** | Attendance Reporting - Daily Summary Calculation | Verify system calculates accurate daily attendance summary | - Multiple active employees in database<br>- Some employees clocked in today, some absent<br>- Date: 2025-11-27 | 1. Request GET `/api/v1/attendance/summary?target_date=2025-11-27`<br>2. Optionally filter by department<br>3. Check response | - HTTP 200 OK status<br>- Response contains: total_employees (count of ACTIVE employees), present_count (employees with IN event today), absent_count (total - present), late_count, early_leave_count<br>- Calculations mathematically correct<br>- Department filter applied if specified<br>- Summary updates in real-time | **Pass**: All counts accurate<br>**Fail**: Wrong calculations or missing data |
| **TC-NFC-01** | NFC Reader - ACR122U Detection and Connection | Verify reader agent detects and connects to ACR122U reader | - ACR122U reader connected via USB<br>- Driver installed correctly<br>- PC/SC service running<br>- No other application using reader | 1. Run reader agent: `python main.py`<br>2. Agent attempts to detect reader<br>3. Check startup logs<br>4. Verify connection established | - Agent logs: "Connected to reader: [ACR122U name]"<br>- Reader status indicator shows GREEN/ONLINE<br>- No connection errors in logs<br>- Agent ready to read cards<br>- Startup banner displays device_id and API URL | **Pass**: Reader connected successfully<br>**Fail**: Reader not found, connection failed, or errors logged |
| **TC-NFC-02** | NFC Reader - Card UID Reading | Verify reader correctly reads UID from MIFARE card | - ACR122U connected successfully<br>- MIFARE card available<br>- Reader agent running in main loop | 1. Place MIFARE card on reader<br>2. Agent sends GET_UID_COMMAND (0xFF 0xCA 0x00 0x00 0x00)<br>3. Check response<br>4. Verify UID extracted | - Command returns SW1=0x90, SW2=0x00 (success)<br>- UID extracted as hex string (e.g., "04A2B3C4D5E6F7")<br>- UID logged: "Card detected: [UID]"<br>- No spaces in UID string<br>- UID passed to API client<br>- Card removed detection works (returns None) | **Pass**: UID read correctly and formatted properly<br>**Fail**: Read fails, wrong format, or errors |
| **TC-NFC-03** | NFC Reader - Offline Mode and Buffering | Verify reader buffers events when API unavailable | - ACR122U connected<br>- Reader agent running<br>- Backend API stopped or network disconnected<br>- SQLite offline buffer initialized | 1. Stop backend API server<br>2. Tap card on reader<br>3. Reader attempts API call, fails<br>4. Check offline buffer<br>5. Verify event stored | - API connection fails (timeout/refused)<br>- Warning logged: "API unavailable: [error]"<br>- Event saved to SQLite database (offline_buffer.db)<br>- Event record contains: id (UUID), card_uid, device_id, timestamp, status=PENDING, sync_attempts=0<br>- Display shows "OFFLINE MODE" message<br>- Sync manager queued for retry | **Pass**: Event buffered with all fields<br>**Fail**: Event lost or buffer not working |
| **TC-NFC-04** | NFC Reader - Offline Sync Recovery | Verify offline events sync when API becomes available | - 5 events buffered offline (status=PENDING)<br>- Backend API restarted and available<br>- Sync manager running in background thread | 1. Start backend API<br>2. Sync manager attempts sync (every 60 seconds or immediate)<br>3. Check buffer database<br>4. Verify events synced | - Sync manager fetches pending events<br>- Each event POST to `/api/v1/attendance-events` with event_id<br>- HTTP 201 response for each event<br>- Events marked as SYNCED in buffer<br>- last_sync_attempt timestamp updated<br>- Display shows: "Synced 5 events, 0 pending"<br>- Stats updated: SYNCED count incremented | **Pass**: All events synced successfully<br>**Fail**: Events remain pending or sync fails |
| **TC-CORRECT-01** | Correction Request - Submit Correction | Verify employee can submit attendance correction request | - Employee logged in<br>- Correction needed for date: 2025-11-25 (employee forgot to clock in)<br>- No correction already submitted for this date/time | 1. Navigate to Corrections page<br>2. Click "Request Correction"<br>3. Fill form: date="2025-11-25", requested_event_type="IN", requested_time="08:00:00", reason="Forgot to tap card"<br>4. Submit form | - HTTP 201 Created status<br>- CorrectionRequest record created with status=PENDING<br>- requested_by_user_id set to current user<br>- employee_id linked correctly<br>- created_at timestamp recorded<br>- Approval workflow triggered<br>- Notification sent to supervisor/HR<br>- Request visible in employee's corrections list | **Pass**: Correction request created and pending<br>**Fail**: Creation fails or wrong status |
| **TC-SEC-01** | Security - API Key Authentication for Devices | Verify reader device must provide valid API key | - Device registered in database with api_key<br>- Device status: ACTIVE<br>- Valid card UID available | 1. Attempt POST to `/api/v1/attendance-events`<br>2. Include X-API-Key header with invalid/missing key<br>3. Check response | - HTTP 401 Unauthorized status (if missing key)<br>- OR HTTP 403 Forbidden (if invalid key)<br>- Error message indicates authentication failed<br>- No attendance event created<br>- Device status not updated<br>- Security audit logged<br>- Rate limiting applied | **Pass**: Request rejected with proper auth error<br>**Fail**: Request succeeds without valid key |
| **TC-SEC-02** | Security - Audit Log for Sensitive Actions | Verify all CREATE/UPDATE/DELETE actions logged in audit_logs | - HR_ADMIN logged in<br>- Audit middleware enabled<br>- Database has audit_logs table | 1. Perform sensitive action (e.g., create employee)<br>2. POST to `/api/v1/employees`<br>3. Check audit_logs table<br>4. Verify log entry created | - AuditLog record created immediately after action<br>- Fields recorded: actor_user_id (HR_ADMIN), action_type="Employee_CREATED", entity_type="Employee", entity_id (new employee ID), ip_address, user_agent, timestamp<br>- Details JSON contains method, path, query_params<br>- Log immutable (no updates/deletes)<br>- Accessible via Audit Logs page | **Pass**: Audit log created with all fields<br>**Fail**: No log created or missing fields |

---

## Test Coverage Summary

✅ **Authentication & Authorization**: JWT token generation, refresh, role-based access control (TC-AUTH-01 to TC-AUTH-04)

✅ **Employee Management**: CRUD operations, validation, search/filter, duplicate prevention (TC-EMP-01 to TC-EMP-04)

✅ **Card Management**: Issue, revoke, duplicate prevention, validation (TC-CARD-01 to TC-CARD-03)

✅ **Shift Management**: Create shifts, assign to employees, handle overlaps (TC-SHIFT-01 to TC-SHIFT-02)

✅ **Attendance Recording**: Valid taps, auto-detection (IN/OUT), duplicate prevention, invalid card rejection (TC-ATT-01 to TC-ATT-04)

✅ **Attendance Reporting**: Personal history, filtered reports, daily summaries, pagination (TC-ATT-05 to TC-ATT-07)

✅ **NFC Reader (ACR122U)**: Device detection, UID reading, offline buffering, sync recovery (TC-NFC-01 to TC-NFC-04)

✅ **Correction Workflow**: Submit correction requests, approval tracking (TC-CORRECT-01)

✅ **Security & Audit**: API key authentication, audit logging for compliance (TC-SEC-01 to TC-SEC-02)

---

## Test Execution Notes

### Prerequisites for Testing
1. **Backend**: FastAPI server running on http://localhost:8000
2. **Frontend**: React/Vite dev server on http://localhost:5173
3. **Database**: PostgreSQL with all migrations applied
4. **NFC Reader**: ACR122U connected via USB with drivers installed
5. **Test Data**: Seed database with users, employees, cards, shifts

### Test Environment Setup
```bash
# Backend
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn app.main:app --reload

# Frontend
cd frontend
npm run dev

# Reader Agent
cd reader_agent
pip install -r requirements.txt
python src/main.py --config config.yaml
```

### Critical Test Scenarios Priority
1. **High Priority**: TC-ATT-01, TC-ATT-02, TC-NFC-01, TC-AUTH-01, TC-SEC-01
2. **Medium Priority**: TC-EMP-01, TC-CARD-01, TC-ATT-05, TC-NFC-03, TC-NFC-04
3. **Low Priority**: TC-ATT-06, TC-ATT-07, TC-CORRECT-01, TC-SEC-02

### Bug Reporting Format
- **Test Case ID**: [TC-XXX-XX]
- **Severity**: Critical / High / Medium / Low
- **Steps to Reproduce**: [Detailed steps]
- **Expected vs Actual**: [What should happen vs what happened]
- **Screenshots/Logs**: [Evidence]
- **Environment**: [OS, Browser, Backend version]

---

## Edge Cases & Additional Test Scenarios

**Additional scenarios to consider** (not detailed here but recommended for complete coverage):

- **TC-ATT-08**: Concurrent card taps from multiple readers (race conditions)
- **TC-ATT-09**: Attendance at midnight (date boundary testing)
- **TC-ATT-10**: Large date range report generation (performance test with 10,000+ events)
- **TC-NFC-05**: Reader reconnection after USB disconnect
- **TC-NFC-06**: Multiple readers on same machine (multi-device setup)
- **TC-EMP-05**: Bulk employee import via CSV
- **TC-REPORT-01**: Payroll export with accurate hour calculations
- **TC-REPORT-02**: Late/Early leave detection based on shift times
- **TC-CORRECT-02**: Supervisor approval of correction request
- **TC-CORRECT-03**: HR Admin rejection of correction with comment
- **TC-UI-01**: Frontend pagination for large datasets
- **TC-UI-02**: Frontend form validation (all forms)
- **TC-UI-03**: Mobile responsive design (all pages)
- **TC-DB-01**: Database constraint enforcement (foreign keys, unique indexes)
- **TC-DB-02**: Transaction rollback on error
- **TC-PERF-01**: API response time under load (100 concurrent users)
- **TC-PERF-02**: Reader agent memory usage over 24 hours

---

**Document Version**: 1.0  
**Last Updated**: November 27, 2025  
**Prepared By**: System Test Engineer  
**Status**: Ready for Chapter 5 Inclusion


