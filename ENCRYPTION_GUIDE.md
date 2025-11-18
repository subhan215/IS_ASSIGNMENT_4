# 🔐 Data Encryption & Decryption Guide

## Overview
The Hospital Management System supports **reversible encryption** using **Fernet** (AES-128 CBC + HMAC-SHA256) for sensitive patient data.

---

## Data States

### 1. **Original Data** (Raw)
- Plain text names and contact information
- Stored in: `name`, `contact` columns
- Visible only when imported initially

### 2. **Anonymized Data** (Irreversible)
- SHA-256 hashed patient names
- Masked contact information (e.g., "0300-*****")
- Stored in: `anonymized_name`, `anonymized_contact` columns
- Cannot be reversed to original data

### 3. **Encrypted Data** (Reversible)
- Fernet-encrypted original data
- Can be decrypted back to original
- Stored in: `encrypted_name`, `encrypted_contact` columns
- Requires the `fernet.key` file to decrypt

---

## How to Use

### Step 1: Check if Data is Encrypted
Go to **🔐 Anonymize & Encrypt/Decrypt** tab (Admin only)

You'll see the current state:
```
Reversible Encryption (Fernet)
- 🔒 Encrypt Data    [Button]
- 🔓 Decrypt & Display [Button]
```

### Step 2: Encrypt Patient Data
1. Click **🔒 Encrypt Data** button
2. Wait for encryption to complete
3. You'll see: ✓ Encrypted N records
4. Data is now stored in encrypted columns

**What happens:**
```
Original: "John Doe" → Encrypted: "gAAAAABl8x7kJ3k2L9m..."
Original: "0300-555-1234" → Encrypted: "gAAAAABl8x7pM2n3O9p..."
```

### Step 3: View Encrypted Data in Patients Tab

#### For Admins:
1. Go to **👥 Patient Records** tab
2. You'll see the toggle: **🔓 Show Decrypted Data**

**Without checkbox (default - Anonymized view):**
```
patient_id | name          | contact      | diagnosis
1          | PATIENT_001   | 0300-*****   | Flu
2          | PATIENT_002   | 0300-*****   | Fracture
```

**With checkbox (Decrypted view):**
```
patient_id | name          | contact       | diagnosis
1          | John Doe      | 0300-555-1234 | Flu
2          | Jane Smith    | 0300-999-4592 | Fracture
```

#### For Doctors:
- Always see anonymized data (unless anonymization hasn't run)
- Cannot decrypt data

#### For Receptionists:
- See REDACTED data only

---

## The Process in Detail

### Encryption Flow
```
Raw Data (name, contact)
    ↓
Click "Encrypt Data"
    ↓
For each patient:
  - encrypt_value(name) → encrypted_name column
  - encrypt_value(contact) → encrypted_contact column
    ↓
Data encrypted ✓
Admin can now toggle decrypt checkbox
```

### Decryption Flow
```
Encrypted Data (encrypted_name, encrypted_contact)
    ↓
Admin checks "🔓 Show Decrypted Data" toggle
    ↓
For each patient:
  - IF encrypted_name exists:
      → decrypt_value(encrypted_name) → display
    - ELSE:
      → show original name or "(Not encrypted)"
    ↓
Patient Data
    ↓
Displayed in table
```

---

## Troubleshooting

### Problem: "Cannot decrypt - no encryption key"
**Cause:** `fernet.key` file is missing or corrupted

**Solution:**
1. Go to **🔐 Anonymize & Encrypt/Decrypt** tab
2. Click **Generate Fernet Key**
3. Restart the app
4. Re-encrypt your data

### Problem: Decryption fails for specific records
**Cause:** Data was encrypted with a different key

**Solution:**
1. Ensure you're using the same `fernet.key`
2. If you lost the key, you must:
   - Back up current database
   - Generate a new key
   - Re-encrypt all data with new key

### Problem: Data shows as "(Not encrypted)"
**Cause:** This patient record hasn't been encrypted yet

**Solution:** Click **🔒 Encrypt Data** to encrypt all records

---

## Security Notes

✅ **Strengths:**
- Fernet uses AES-128 encryption (industry standard)
- HMAC-SHA256 ensures data integrity
- Reversible: can access original data when needed
- Admin-only decryption control

⚠️ **Important:**
- **Backup `fernet.key` file securely** - losing it means encrypted data is unrecoverable
- Never share `fernet.key` with unauthorized users
- Encrypted data requires the correct key to decrypt
- Anonymized data is irreversible by design (for privacy)

---

## Data Flow Summary

```
┌─────────────────────────────────────────────┐
│ Raw Patient Data Imported                   │
│ (name, contact, diagnosis)                  │
└──────────────┬──────────────────────────────┘
               │
        ┌──────┴──────┐
        ↓             ↓
   ┌────────────┐  ┌─────────────┐
   │ Anonymize  │  │  Encrypt    │
   │ (irrevers) │  │  (revers.)  │
   └────────────┘  └─────────────┘
        ↓             ↓
   Anonymized   Encrypted
   Hash (SHA)   (Fernet AES)
        ↓             ↓
   ┌────────────────────────────────┐
   │ Stored in Database             │
   │ - anonymized_name              │
   │ - anonymized_contact           │
   │ - encrypted_name               │
   │ - encrypted_contact            │
   └────────────────────────────────┘
        ↓             ↓
   Doctor/Recep  Admin (with toggle)
   (Anon view)   (Anon/Decrypt view)
```

---

## Quick Reference

| Action | Who | Where | Result |
|--------|-----|-------|--------|
| Encrypt Data | Admin | 🔐 Tab | Data moved to encrypted columns |
| View Encrypted | Admin | 👥 Tab + Toggle | Shows original data |
| View Anonymized | Admin | 👥 Tab (default) | Shows hashed/masked data |
| View Anonymized | Doctor | 👥 Tab (always) | Cannot change view |
| View REDACTED | Receptionist | 👥 Tab | Data is hidden (security policy) |

---

## Example Session

1. **Admin logs in** → Sees patients with anonymized data (default)
2. **Admin goes to 🔐 tab** → Clicks "Encrypt Data" → Encryption complete
3. **Admin returns to 👥 tab** → Can now toggle to see original data
4. **Doctor logs in** → Sees only anonymized data (no toggle available)
5. **Admin logs out** → Anonymized data persists (encryption is permanent)
6. **Admin logs back in** → Can still decrypt using same key

---

## GDPR Compliance

✅ **This system supports GDPR requirements:**
- **Data Minimization:** Only needed data is stored
- **Encryption:** Data encrypted at rest (optional)
- **Access Control:** Role-based decryption restrictions
- **Audit Trail:** Every encrypt/decrypt action is logged
- **Data Portability:** Can export encrypted or decrypted data
- **Consent:** Users consent before data processing

---

For questions, refer to `README.md` or `Assignment4.py` for full technical documentation.
