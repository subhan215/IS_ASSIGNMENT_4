# 🎥 Demo Script & Screenshots Guide
## Hospital Management System - Information Security Assignment 4

---

## Demo Duration: 2-3 minutes

### Part 1: Login & GDPR Consent (30 seconds)

**Action**: Show the login screen
1. Open app at `http://localhost:8501`
2. **Screenshot 1**: Login page with instructions
   ```
   ┌─────────────────────────────────┐
   │ GDPR Mini Hospital Dashboard    │
   ├─────────────────────────────────┤
   │ Username: [          ]          │
   │ Password: [••••••••••]          │
   │ [Login]                         │
   │                                 │
   │ ℹ️ Sample accounts:              │
   │ • admin/admin123                │
   │ • drbob/doc123                  │
   │ • alice_recep/rec123            │
   └─────────────────────────────────┘
   ```

3. **Demo**: Type "admin" / "admin123"
4. Click "Login"
5. **Screenshot 2**: GDPR Consent Banner
   ```
   ⚠️ GDPR Data Processing Consent Required
   This system collects and processes personal data 
   according to GDPR. Your consent is required before proceeding.
   
   [✓ I Consent] [✗ Decline]
   ```
6. Click "I Consent"
7. **Note**: Logged to audit trail (shown later)

---

### Part 2: Role-Based Data Viewing (45 seconds)

**Action A - Admin View (Decrypted)**:
1. Click on "Patients" tab
2. **Screenshot 3**: Admin sees toggle checkbox
   ```
   ☑ Show decrypted data (Admin only)
   ```
3. Check the checkbox
4. **Screenshot 4**: Table with raw data
   ```
   | patient_id | name      | contact      | diagnosis  |
   |------------|-----------|--------------|------------|
   | 1          | John Doe  | 0300-555-1234| Flu        |
   | 2          | Jane Smith| 0300-999-4592| Fracture   |
   ```

**Action B - Admin View (Anonymized)**:
5. Uncheck the checkbox
6. **Screenshot 5**: Table with anonymized data
   ```
   | patient_id | name           | contact    | diagnosis  |
   |------------|----------------|------------|------------|
   | 1          | ANON_4ff0e5ad | XXX-XXX-1234 | Flu      |
   | 2          | ANON_a1b2c3d4 | XXX-XXX-4592 | Fracture |
   ```

**Action C - Doctor View**:
7. Logout (click Logout in sidebar)
8. Login with "drbob" / "doc123"
9. Consent to GDPR
10. Go to "Patients" tab
11. **Screenshot 6**: Doctor sees ONLY anonymized data (no toggle)
    ```
    | patient_id | name           | contact    | diagnosis  |
    |------------|----------------|------------|------------|
    | 1          | ANON_4ff0e5ad | XXX-XXX-1234 | Flu      |
    | 2          | ANON_a1b2c3d4 | XXX-XXX-4592 | Fracture |
    
    ℹ️ Cannot access Anonymize, Logs, or Backup tabs
    ```

**Action D - Receptionist View**:
12. Logout
13. Login with "alice_recep" / "rec123"
14. Consent to GDPR
15. Go to "Patients" tab
16. **Screenshot 7**: Receptionist sees REDACTED
    ```
    | patient_id | name     | contact | diagnosis  |
    |------------|----------|---------|------------|
    | 1          | REDACTED | REDACTED | Flu      |
    | 2          | REDACTED | REDACTED | Fracture |
    
    ℹ️ Can add new records but cannot view data
    ```

---

### Part 3: Encryption/Anonymization (45 seconds)

**Action**: Log back in as Admin

1. Login as "admin" / "admin123"
2. Consent to GDPR
3. Go to **"Anonymize"** tab
4. **Screenshot 8**: Show anonymization options
   ```
   🔐 Anonymize & Encrypt / Decrypt (Admin only)
   
   [🔄 Anonymize All Patients] [🔒 Encrypt Data] [🔓 Decrypt & Display]
   [🔑 Generate Fernet Key]
   ```

5. Click **"🔄 Anonymize All Patients"**
6. **Screenshot 9**: Success message
   ```
   ✓ Anonymized 2 records
   ```

7. Click **"🔒 Encrypt Data"**
8. **Screenshot 10**: After encryption
   ```
   ✓ Encrypted 2 records
   ```

9. Go to **"Patients"** tab
10. Check "Show decrypted data"
11. **Screenshot 11**: Data is now encrypted (shows error or encrypted blob)
    ```
    | patient_id | name                                    | contact          |
    |-----------|----------------------------------------------|----|
    | 1          | gAAAAABl_Xy...kjZ9MNOP= [Encrypted]  | gAAAAABl_Xy... |
    | 2          | gAAAAABl_Yz...ijX7PQR= [Encrypted]  | gAAAAABl_Yz... |
    ```

12. Go back to **"Anonymize"** tab
13. Click **"🔓 Decrypt & Display"**
14. **Screenshot 12**: Decrypted data shown
    ```
    ✓ Decrypted 2 records
    
    | ID | Decrypted Name | Decrypted Contact |
    |----|---------------|------------------|
    | 1  | John Doe      | 0300-555-1234    |
    | 2  | Jane Smith    | 0300-999-4592    |
    ```

---

### Part 4: Audit Logging (30 seconds)

**Action**: Show audit trail of everything we just did

1. Go to **"Logs (Admin)"** tab
2. **Screenshot 13**: Full audit log
   ```
   🔍 Filter by action: [All ▼]
   
   Total Log Entries: 25
   
   | timestamp           | username    | role | action       | details          |
   |-------------------|-------------|------|-------------|------------------|
   | 2025-11-18 10:45:00| admin       | admin| login        | successful       |
   | 2025-11-18 10:45:05| admin       | admin| consent_given| User accepted... |
   | 2025-11-18 10:45:10| admin       | admin| view_patients| viewed 2 rows    |
   | 2025-11-18 10:45:15| admin       | admin| anonymize    | patient_id=1     |
   | 2025-11-18 10:45:16| admin       | admin| anonymize    | patient_id=2     |
   | 2025-11-18 10:45:20| admin       | admin| encrypt      | patient_id=1     |
   | 2025-11-18 10:45:21| admin       | admin| encrypt      | patient_id=2     |
   | 2025-11-18 10:45:30| drbob       | doctor| login       | successful       |
   | 2025-11-18 10:45:35| drbob       | doctor| view_patients| viewed 2 rows    |
   | 2025-11-18 10:45:40| alice_recep | recep| login       | successful       |
   | 2025-11-18 10:45:45| alice_recep | recep| view_patients| viewed 2 rows    |
   | ... (more entries)
   ```

3. **Show filtering**: Click dropdown, select "encrypt"
4. **Screenshot 14**: Filtered logs
   ```
   🔍 Filter by action: [encrypt ▼]
   
   Total Log Entries: 2
   
   | timestamp            | username | role  | action  | details      |
   |--------------------|----------|-------|---------|--------------|
   | 2025-11-18 10:45:20 | admin    | admin | encrypt | patient_id=1 |
   | 2025-11-18 10:45:21 | admin    | admin | encrypt | patient_id=2 |
   ```

5. Show export button
6. **Screenshot 15**: Export modal
   ```
   [📥 Download logs.csv]
   ```

---

### Part 5: Activity Graphs (20 seconds)

**Action**: Show real-time analytics

1. Go to **"Activity Graphs (Admin)"** tab
2. **Screenshot 16**: Multiple charts
   ```
   📊 User Activity Graph (Admin only)
   
   📈 Actions per Day
   [Line chart showing actions over time]
   
   👥 Actions by User
   [Bar chart: admin: 15, drbob: 3, alice_recep: 2]
   
   🔍 Recent Activity Log
   | timestamp            | username    | role | action         | details |
   |-------------------|-------------|------|----------------|---------|
   | 2025-11-18 10:45:45| alice_recep | recep| view_patients | viewed 2|
   | 2025-11-18 10:45:40| admin       | admin| decrypt        | patient |
   ```

---

### Part 6: Data Backup & Export (20 seconds)

**Action**: Show disaster recovery capability

1. Go to **"Backup/Export"** tab
2. **Screenshot 17**: Export options
   ```
   📦 Backup / Export Data
   
   ☐ Export decrypted data (Admin only)
   
   Patients: 2
   | patient_id | name           | contact    | diagnosis |
   |-----------|----------------|-----------|-----------|
   | 1         | ANON_4ff0e5ad  | XXX-... | Flu      |
   | 2         | ANON_a1b2c3d4  | XXX-... | Fracture |
   
   [📥 Download Patients CSV]
   ```

3. Check "Export decrypted data" checkbox
4. **Screenshot 18**: Decrypted export
   ```
   ⚠️ Exporting raw/decrypted data. Handle with care!
   
   Patients: 2
   | patient_id | name        | contact      | diagnosis |
   |-----------|-----------|---------------|-----------|
   | 1         | John Doe   | 0300-555-1234| Flu      |
   | 2         | Jane Smith | 0300-999-4592| Fracture |
   
   [📥 Download Patients CSV]
   ```

5. Click Download (shows CSV download)
6. **Screenshot 19**: CSV file preview
   ```
   patient_id,name,contact,diagnosis,date_added
   1,John Doe,0300-555-1234,Flu,2025-11-18T...
   2,Jane Smith,0300-999-4592,Fracture,2025-11-18T...
   ```

---

### Part 7: Data Retention (10 seconds)

**Action**: Show GDPR compliance feature

1. Go to **"Data Retention (Admin)"** tab
2. **Screenshot 20**: Retention status
   ```
   🗑️ Data Retention & GDPR Compliance (Admin only)
   
   GDPR Requirement: Data should be retained only as long as necessary.
   This tool automatically anonymizes patient records older than 1 year.
   
   Total Patients: 2
   Due for Anonymization: 0
   Retention Days: 365
   
   ✓ All records are within retention period
   
   📅 Retention Schedule:
   | patient_id | days_until_retention |
   |-----------|---------------------|
   | 1         | 365                 |
   | 2         | 365                 |
   ```

---

## 📸 Screenshots Summary

**Must Include in PDF Report**:
1. Login screen
2. GDPR consent banner
3. Admin decrypted view
4. Admin anonymized view
5. Doctor anonymized view (read-only)
6. Receptionist REDACTED view
7. Anonymization tab options
8. Encryption success
9. Decrypted data display
10. Audit logs full view
11. Audit logs filtered
12. Activity graphs
13. Export options
14. Decrypted export warning
15. CSV preview
16. Data retention status
17. Sidebar with uptime
18. Footer with CIA summary
19. Error handling example
20. Role comparison table

---

## 🎬 Demo Narrative (Read to Audience)

```
"This hospital management system demonstrates the CIA Triad:

1. CONFIDENTIALITY: Patient names encrypted with Fernet and 
   anonymized with SHA-256. Access restricted by role.

2. INTEGRITY: Every action logged—login, view, encrypt, export—
   all with timestamp and user. Logs are immutable.

3. AVAILABILITY: Data backed up as CSV, system remains responsive 
   with error handling, and uptime is monitored.

GDPR compliance is built-in: consent required, data can be exported 
in portable format, and records auto-anonymize after 365 days.

Let me show you how it works..."
```

---

## 🔑 Key Points to Emphasize

1. **Three Roles**: Show clear distinction (Admin full access, Doctor anonymized, Receptionist limited)
2. **Encryption Works**: Encrypt/decrypt demonstrates Fernet working
3. **Logs Everything**: Show that every action is tracked
4. **GDPR Compliance**: Consent, retention, portability all present
5. **Real Data Protection**: Show before/after encryption & anonymization
6. **Professional Implementation**: Error handling, validation, recovery

---

## ⏱️ Timing Breakdown

- Intro: 30 seconds
- Login & Consent: 30 seconds
- Data Viewing by Role: 45 seconds
- Encryption/Decryption: 45 seconds
- Audit Logs: 30 seconds
- Activity Graphs: 20 seconds
- Backup/Export: 20 seconds
- Data Retention: 10 seconds
- Closing: 30 seconds
- **Total: 3 minutes 40 seconds** (trim to 3 minutes)

---

## 📝 Demo Checklist

Before demo, verify:
- [✓] Database initialized: `python db_setup.py`
- [✓] Fernet key created: `python create_key.py` or in-app
- [✓] App starts: `streamlit run streamlit_app.py`
- [✓] All three test accounts working
- [✓] Encryption/decryption buttons appear
- [✓] Logs are populated
- [✓] Export buttons work
- [✓] Charts display (if logs exist)
- [✓] Browser ready for screen recording

---

## 🎥 Recording Tips

1. **Use OBS Studio** or **Windows 10/11 Game Bar** (Win+G)
   - Hide taskbar: Press Alt+Tab then Alt+D
   - Maximize browser window
   - Set resolution to 1920x1080 (Full HD)

2. **Narration**:
   - Speak clearly
   - Explain what you're doing BEFORE clicking
   - Pause briefly on each screenshot for viewers to read

3. **Pacing**:
   - Click slowly (allow time for loads)
   - Don't skip tabs or rush
   - Show success messages

4. **Final Output**:
   - Save as MP4 (h.264 codec)
   - Upload to Google Drive
   - Get shareable link
   - Paste link in PDF report

---

## Example Video Script

```
[0:00] "This is the Hospital Management System for our Information Security 
project. It demonstrates the CIA Triad and GDPR compliance. Let me login 
as an admin..."

[0:30] "First, I'll enter the admin credentials: admin/admin123. Now I need 
to consent to GDPR terms before accessing data... I consent and now I'm 
logged in."

[1:00] "Let me show the Patients tab. I can toggle between decrypted data 
showing real names, or anonymized data showing ANON_xxxxx. This is 
CONFIDENTIALITY."

[1:30] "Now let me encrypt the data. I'll click Encrypt Data. All patient 
names and contacts are now encrypted with Fernet. Only the admin with 
the key can decrypt them."

[2:00] "Let me show the audit logs. Every action is recorded: when admin 
logged in, when data was viewed, when it was encrypted. This is INTEGRITY 
- we can track who did what and when."

[2:30] "I can export patient data as CSV for backup—this is AVAILABILITY. 
The system remains functional and we can recover data."

[3:00] "The system also has a data retention policy. Records older than 
365 days are automatically anonymized, ensuring GDPR compliance. Thank you."
```

---

**Ready for Presentation!** 🎉

All screenshots can be captured by running the app and taking browser 
screenshots. Each screenshot should be ~2-3 seconds in the video.
