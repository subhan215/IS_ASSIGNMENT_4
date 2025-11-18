# GDPR-Compliant Hospital Management Dashboard
## Information Security (CS-3002) - Assignment 4

A Streamlit-based Hospital Management System demonstrating CIA Triad principles and GDPR compliance.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or later
- pip (Python package manager)

### Installation

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Initialize Database:**
   ```bash
   python db_setup.py
   ```

3. **Generate Encryption Key (Recommended):**
   ```bash
   python create_key.py
   ```
   Or generate within the app: Anonymize tab → Generate Fernet Key

4. **Run the Application:**
   ```bash
   streamlit run streamlit_app.py
   ```
   Opens at: `http://localhost:8501`

---

## 👤 Test Accounts

| Username | Password | Role | Access |
|----------|----------|------|--------|
| `admin` | `admin123` | Admin | Full access to raw data, encryption, logs |
| `drbob` | `doc123` | Doctor | Anonymized patient data only |
| `alice_recep` | `rec123` | Receptionist | Add/edit records, limited view |

---

## 📋 Features

### 1. Confidentiality 🔒
- **Fernet Encryption**: Reversible encryption for patient names and contacts
- **SHA-256 Anonymization**: Irreversible hashing for data masking
- **Role-Based Access**: Admin ↔ Doctor ↔ Receptionist permission levels
- **Data Masking**: Display anonymized data based on user role

### 2. Integrity 📋
- **Audit Logs**: Every action logged with timestamp, user, role, and details
- **Immutable Trail**: Append-only logs for compliance
- **Activity Graphs**: Real-time visualization of user actions
- **Export Logs**: Download audit trail for external audits

### 3. Availability 🟢
- **Local Database**: Fast, reliable SQLite backend
- **Error Handling**: Graceful degradation with user-friendly messages
- **Data Backup**: CSV export for disaster recovery
- **System Monitoring**: Uptime tracking and health indicators

### 4. GDPR Compliance ✓
- **Consent Banner**: Explicit consent required before data access
- **Data Portability**: Export data in CSV format
- **Right to be Forgotten**: Auto-anonymization after 365 days
- **Transparency**: Clear documentation of data processing

---

## 📊 Tabs Overview

| Tab | Access | Function |
|-----|--------|----------|
| **Patients** | All | View patient records (role-based masking) |
| **Add Patient** | Admin, Receptionist | Add or edit patient records |
| **Anonymize** | Admin | Encrypt/decrypt patient data |
| **Logs (Admin)** | Admin | View and export audit logs |
| **Backup/Export** | Admin | Download patient data as CSV |
| **Activity Graphs** | Admin | Real-time activity visualization |
| **Data Retention** | Admin | Manage data retention policy |

---

## 🔐 Encryption Details

### Fernet (Reversible)
- **Algorithm**: AES-128 CBC + HMAC-SHA256
- **Key Size**: 256-bit
- **Use Case**: Encrypt patient names and contacts for later decryption

### SHA-256 (Irreversible)
- **Algorithm**: Cryptographic hash
- **Use Case**: Anonymize data (ANON_xxxxx format)
- **One-way**: Cannot reverse to original

### Contact Masking
- **Pattern**: XXX-XXX-XXXX (last 4 digits visible)
- **Example**: 0300-555-1234 → XXX-XXX-1234

---

## 📁 Project Structure

```
Hospital_Management_System/
├── streamlit_app.py          # Main Streamlit application
├── db.py                      # Database operations
├── auth.py                    # Authentication & password hashing
├── utils.py                   # Encryption, anonymization utilities
├── db_setup.py                # Database initialization
├── create_key.py              # Generate Fernet key
├── requirements.txt           # Python dependencies
├── hospital.db                # SQLite database
├── fernet.key                 # Encryption key
├── Assignment4.py             # Full documentation (this is the main file)
└── README.md                  # This file
```

---

## 🔍 Database Schema

### Users Table
```sql
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT,
    role TEXT
);
```

### Patients Table
```sql
CREATE TABLE patients (
    patient_id INTEGER PRIMARY KEY,
    name TEXT,
    contact TEXT,
    diagnosis TEXT,
    anonymized_name TEXT,
    anonymized_contact TEXT,
    encrypted_name TEXT,
    encrypted_contact TEXT,
    date_added TEXT
);
```

### Logs Table
```sql
CREATE TABLE logs (
    log_id INTEGER PRIMARY KEY,
    user_id INTEGER,
    username TEXT,
    role TEXT,
    action TEXT,
    timestamp TEXT,
    details TEXT
);
```

---

## ⚙️ Configuration

### Retention Period
Edit `streamlit_app.py` line 297:
```python
RETENTION_DAYS = 365  # Anonymize records older than 1 year
```

### Password Salt
Edit `auth.py` line 4:
```python
SALT = "static_salt_for_demo"  # Use bcrypt in production
```

---

## 🔒 Security Notes

### Demo Mode
This implementation is suitable for **educational purposes** and **small pilot deployments**.

### Production Considerations
- [ ] Replace SHA-256 with bcrypt/Argon2
- [ ] Use HSM or cloud KMS for encryption keys
- [ ] Migrate to PostgreSQL with SSL/TLS
- [ ] Implement 2FA/MFA
- [ ] Use HTTPS with valid certificate
- [ ] Add rate limiting on login
- [ ] Implement intrusion detection
- [ ] Regular security audits

---

## 📈 Activity Monitoring

### Audit Log Actions
- `login` - User authentication
- `consent_given` - GDPR consent accepted
- `logout` - User session ended
- `view_patients` - Patient data viewed
- `add_patient` - New patient added
- `update_patient` - Patient record updated
- `anonymize` - Data anonymized
- `encrypt` - Data encrypted
- `decrypt` - Data decrypted
- `export_patients` - Patient data exported
- `export_logs` - Logs exported
- `data_retention` - Old records anonymized

---

## 🧪 Testing

Run all features with test accounts:

1. **Test Admin Access**
   - Login: admin/admin123
   - Access all tabs
   - Encrypt/decrypt data
   - View and export logs

2. **Test Doctor Access**
   - Login: drbob/doc123
   - View anonymized patients only
   - Cannot access encryption or logs

3. **Test Receptionist Access**
   - Login: alice_recep/rec123
   - Add new patients
   - Cannot view sensitive data

---

## 📝 Documentation

**Main Documentation File**: `Assignment4.py`

Contains:
- CIA Triad implementation details
- GDPR compliance checklist
- Database schema
- Cryptographic algorithms
- Security analysis
- Test cases
- Performance metrics
- Best practices and recommendations

View documentation:
```bash
python Assignment4.py
```

---

## 🐛 Troubleshooting

### "Fernet key not loaded"
**Solution**: Run `python create_key.py` or generate key in app

### "Login failed"
**Solution**: Ensure database exists - run `python db_setup.py`

### "ModuleNotFoundError: No module named 'streamlit'"
**Solution**: Run `pip install -r requirements.txt`

### Database locked
**Solution**: Restart the application

---

## 📚 Learning Resources

- [GDPR Compliance Guide](https://gdpr-info.eu/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework/)
- [Python Cryptography](https://cryptography.io/)
- [Streamlit Documentation](https://docs.streamlit.io/)

---

## 🏥 Scenario: Real-World Use

1. **Patient Registration**
   - Receptionist adds patient name, contact, diagnosis
   - Data stored securely

2. **Doctor Review**
   - Doctor logs in, views anonymized patient records
   - Cannot see PII
   - All access logged

3. **Admin Audit**
   - Admin checks audit logs
   - Confirms doctor accessed records
   - Exports logs for compliance report

4. **Data Retention**
   - Records older than 1 year anonymized automatically
   - Original data permanently lost (GDPR compliant)
   - Retention actions logged

---

## 📄 License

Educational material for CS-3002 Information Security course.

---

## ✅ GDPR Compliance Checklist

- ✓ Lawful basis (consent obtained)
- ✓ Purpose limitation (healthcare only)
- ✓ Data minimization (only essential fields)
- ✓ Accuracy (validation & audit logs)
- ✓ Storage limitation (365-day retention)
- ✓ Integrity & confidentiality (encryption)
- ✓ Accountability (comprehensive logging)
- ✓ Right to access (CSV export)
- ✓ Right to be forgotten (anonymization)
- ✓ Right to data portability (CSV export)

---

## 🤝 Support

For questions or issues:
1. Check `Assignment4.py` for detailed documentation
2. Review error messages in browser console
3. Check system logs (logs/audit trail in app)
4. Consult GDPR and CIA Triad resources

---

**Last Updated**: November 2025  
**Status**: Production-Ready for Educational Use
