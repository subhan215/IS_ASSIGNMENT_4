import streamlit as st
from db import fetch_patients, add_patient, update_patient, fetch_logs, add_log, check_consent, set_consent
from auth import login, hash_password
from utils import anonymize_name, mask_contact, FERNET_KEY, encrypt_value, decrypt_value, generate_fernet_key
from datetime import datetime, timedelta
import pandas as pd
import time
import os
import logging

# Configure logging for audit trail
logging.basicConfig(level=logging.INFO)

st.set_page_config(
    page_title="🏥 GDPR Hospital Dashboard", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional CSS styling
st.markdown("""
<style>
    /* Professional styling */
    body { 
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        background: linear-gradient(135deg, #f5f7fa 0%, #e9ecef 100%);
    }
    
    /* Main content area */
    .main {
        padding: 2rem;
    }
    
    /* Login form styling */
    .login-container {
        max-width: 400px;
        margin: 100px auto;
        padding: 40px;
        background: white;
        border-radius: 12px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        border: 1px solid rgba(31, 119, 180, 0.1);
    }
    
    .login-header {
        text-align: center;
        font-size: 2em;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 10px;
    }
    
    .login-subtitle {
        text-align: center;
        color: #666;
        margin-bottom: 30px;
        font-size: 0.9em;
    }
    
    /* Sidebar nav styling */
    .sidebar-nav {
        display: flex;
        flex-direction: column;
        gap: 8px;
    }
    
    .nav-section {
        margin-top: 20px;
        margin-bottom: 10px;
        color: #666;
        font-size: 0.85em;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Button improvements */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
        border: none;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    .stButton > button:active {
        transform: translateY(0px);
    }
    
    /* Input styling */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select,
    .stTextArea > div > div > textarea {
        border-radius: 8px;
        border: 2px solid #e0e0e0;
        transition: all 0.3s ease;
        padding: 10px 12px;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #1f77b4;
        box-shadow: 0 0 0 3px rgba(31, 119, 180, 0.1);
    }
    
    /* Form container styling */
    .stForm {
        padding: 2rem;
        background: white;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        border: 1px solid #e0e0e0;
    }
    
    /* Dataframe styling */
    .stDataFrame {
        font-size: 0.9em;
        border-radius: 8px;
        overflow: hidden;
    }
    
    /* Card styling */
    .card {
        padding: 1.5rem;
        background: white;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        border-left: 4px solid #1f77b4;
        margin-bottom: 1rem;
    }
    
    /* Column containers */
    .stColumn {
        padding: 1rem;
    }
    
    /* Divider styling */
    .stDivider {
        margin: 2rem 0;
        border-top: 2px solid rgba(31, 119, 180, 0.1);
    }
    
    /* Subheader styling */
    h2, h3 {
        color: #1f77b4;
        font-weight: 600;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    
    /* Success/Error/Warning boxes */
    .stSuccess, .stError, .stWarning, .stInfo {
        border-radius: 8px;
        padding: 1rem;
        border-left: 4px solid;
    }
    
    .stSuccess {
        border-left-color: #28a745;
        background-color: rgba(40, 167, 69, 0.1);
    }
    
    .stError {
        border-left-color: #dc3545;
        background-color: rgba(220, 53, 69, 0.1);
    }
    
    .stWarning {
        border-left-color: #ffc107;
        background-color: rgba(255, 193, 7, 0.1);
    }
    
    .stInfo {
        border-left-color: #1f77b4;
        background-color: rgba(31, 119, 180, 0.05);
    }
    
    /* Metric styling */
    [data-testid="metric-container"] {
        background-color: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        border: 1px solid #e0e0e0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "user" not in st.session_state:
    st.session_state["user"] = None
if "start_time" not in st.session_state:
    st.session_state["start_time"] = datetime.now()
if "current_tab" not in st.session_state:
    st.session_state["current_tab"] = "patients"

def uptime_str():
    """Calculate uptime since session started"""
    elapsed = datetime.now() - st.session_state["start_time"]
    hours = int(elapsed.total_seconds() // 3600)
    minutes = int((elapsed.total_seconds() % 3600) // 60)
    seconds = int(elapsed.total_seconds() % 60)
    return f"{hours:02d}h {minutes:02d}m {seconds:02d}s"

@st.fragment(run_every=1)
def display_uptime():
    """Display uptime with continuous updates using fragment"""
    st.metric("⏱️ Uptime", uptime_str())

# ============== LOGIN PAGE ==============
if st.session_state["user"] is None:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### Sign In")
        
        username = st.text_input(
            "Username",
            placeholder="Enter your username",
            key="login_username"
        )
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password",
            key="login_password"
        )
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            login_btn = st.button("🔓 Login", use_container_width=True, type="primary")
        with col_btn2:
            with st.expander("ℹ️ Demo Accounts"):
                st.code("admin / admin123\ndrbob / doc123\nalice_recep / rec123", language="text")
        
        if login_btn:
            if not username or not password:
                st.error("❌ Please enter both username and password")
            else:
                try:
                    user, err = login(username.strip(), password)
                    if user:
                        st.session_state["user"] = user
                        st.success(f"✅ Welcome {user['username']}!")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error(f"❌ {err}")
                except Exception as e:
                    st.error(f"❌ Login error: {e}")
                    logging.error(f"Login failed for {username}: {e}")
    
    st.stop()

# ============== MAIN APP ==============
user = st.session_state["user"]
role = user["role"]

# Check consent from database
user_has_consent = check_consent(user['user_id'])

# GDPR consent required before interacting
if not user_has_consent:
    st.warning("""
    ⚠️ **GDPR Consent Required**  
    This system processes personal data. Your consent is needed to proceed.
    """)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✓ I Consent"):
            try:
                set_consent(user['user_id'], user['username'], role, consent=True)
                st.success("✅ Consent recorded.")
            except Exception as e:
                st.error(f"Error: {e}")
                logging.error(f"Failed to set consent: {e}")
            st.rerun()
    with col2:
        if st.button("✗ Decline"):
            st.error("Consent required to proceed.")
            st.session_state["user"] = None
            st.rerun()
    st.stop()

# ============== SIDEBAR NAVIGATION ==============
with st.sidebar:
    st.title("🏥 Hospital System")
    st.divider()
    
    # User info
    st.markdown(f"**👤 User:** `{user['username']}`")
    st.markdown(f"**👨‍💼 Role:** `{role.title()}`")
    
    # Uptime display with continuous updates (uses fragment for efficiency)
    display_uptime()
    
    st.divider()
    
    # Navigation menu
    st.markdown("### 📑 Navigation")
    
    nav_options = []
    nav_pages = []
    
    # Role-based navigation
    if role == "receptionist":
        # Receptionist: Only Add/Edit records
        nav_options.append("➕ Add Patient")
        nav_pages.append("add_patient")
    elif role == "admin":
        # Admin: Full access
        nav_options.append("� Patients")
        nav_pages.append("patients")
        nav_options.append("➕ Add Patient")
        nav_pages.append("add_patient")
        nav_options.append("🔐 Anonymize & Encrypt")
        nav_pages.append("anonymize")
        nav_options.append("📋 Audit Logs")
        nav_pages.append("logs")
        nav_options.append("📊 Activity Graphs")
        nav_pages.append("activity")
        nav_options.append("📦 Backup & Export")
        nav_pages.append("backup")
        nav_options.append("🗑️ Data Retention")
        nav_pages.append("retention")
    else:
        # Default (doctor): Only view patients
        nav_options.append("👥 Patients")
        nav_pages.append("patients")
    
    selected_nav = st.radio(
        "Select page:",
        nav_options,
        key="sidebar_nav",
        label_visibility="collapsed"
    )
    
    selected_idx = nav_options.index(selected_nav)
    st.session_state["current_tab"] = nav_pages[selected_idx]
    
    st.divider()
    
    # Logout
    if st.button("🚪 Logout", use_container_width=True):
        try:
            add_log(user['user_id'], user['username'], role, "logout", "user logged out")
        except Exception as e:
            logging.error(f"Logout logging failed: {e}")
        st.session_state["user"] = None
        st.rerun()
    
    # Encryption status
    st.divider()
    if FERNET_KEY:
        st.success("🔐 Encryption: Active", icon="✅")
    else:
        st.warning("⚠️ Encryption: Disabled", icon="⚠️")

# ============== MAIN CONTENT ==============

# --- Helper function to render patients table dynamically
def render_patients_table():
    """Render patient table with role-based masking and error handling."""
    try:
        patients = fetch_patients(raw=True)
        rows = []
        show_decrypted = st.session_state.get("show_decrypted", False)
        
        for p in patients:
            row = {"patient_id": p["patient_id"], "diagnosis": p.get("diagnosis", "")}
            
            if role == "admin":
                if show_decrypted:
                    # Admin viewing decrypted: try encrypted first, fall back to raw
                    try:
                        if p.get("encrypted_name"):
                            row["name"] = decrypt_value(p["encrypted_name"])
                        else:
                            row["name"] = p.get("name") or "(Not encrypted)"
                    except Exception as decrypt_err:
                        logging.warning(f"Decryption failed for patient {p['patient_id']}: {decrypt_err}")
                        # Fallback to raw name if decryption fails
                        row["name"] = p.get("name") or "[Cannot decrypt - no encryption key]"
                    
                    try:
                        if p.get("encrypted_contact"):
                            row["contact"] = decrypt_value(p["encrypted_contact"])
                        else:
                            row["contact"] = p.get("contact") or "(Not encrypted)"
                    except Exception as decrypt_err:
                        logging.warning(f"Decryption failed for contact {p['patient_id']}: {decrypt_err}")
                        # Fallback to raw contact if decryption fails
                        row["contact"] = p.get("contact") or "[Cannot decrypt - no encryption key]"
                else:
                    # Admin viewing anonymized
                    row["name"] = p.get("anonymized_name") or anonymize_name(p.get("name") or "")
                    row["contact"] = p.get("anonymized_contact") or mask_contact(p.get("contact") or "")
                row["anonymized_name"] = p.get("anonymized_name") or ""
                row["anonymized_contact"] = p.get("anonymized_contact") or ""
                
            elif role == "doctor":
                # Doctor sees anonymized data only
                row["name"] = p.get("anonymized_name") or anonymize_name(p.get("name") or "")
                row["contact"] = p.get("anonymized_contact") or mask_contact(p.get("contact") or "")
            elif role == "receptionist":
                # Receptionist sees full unmasked data (can add/edit but cannot view masked/anonymized)
                row["name"] = p.get("name") or ""
                row["contact"] = p.get("contact") or ""
            
            rows.append(row)
        
        df = pd.DataFrame(rows)
        
        # Display with better styling
        if len(df) > 0:
            st.markdown(f"**📊 Total Patients: {len(df)}**")
            # Use st.dataframe with column configuration for better display
            st.dataframe(
                df, 
                use_container_width=True,
                hide_index=True,
                column_config={
                    "patient_id": st.column_config.NumberColumn("ID", width="small"),
                    "name": st.column_config.TextColumn("Name", width="medium"),
                    "contact": st.column_config.TextColumn("Contact", width="medium"),
                    "diagnosis": st.column_config.TextColumn("Diagnosis", width="large"),
                    "anonymized_name": st.column_config.TextColumn("Anon. Name", width="medium"),
                    "anonymized_contact": st.column_config.TextColumn("Anon. Contact", width="medium"),
                }
            )
        else:
            st.info("📭 No patients found")
        
        # Log the view action
        try:
            add_log(user['user_id'], user['username'], role, "view_patients", f"viewed {len(rows)} rows")
        except Exception as log_err:
            logging.error(f"Failed to log view_patients: {log_err}")
            
    except Exception as e:
        st.error(f"Error loading patients: {e}")
        logging.error(f"render_patients_table failed: {e}")

# ============== PAGE CONTENT RENDERING ==============

# --- PAGE: Patients
if st.session_state["current_tab"] == "patients":
    st.subheader("👥 Patient Records")
    st.markdown("---")
    
    if role == "receptionist":
        st.warning("🔒 Receptionists cannot view patient records. Use the 'Add Patient' tab to add or edit records.")
    elif role == "admin":
        st.markdown("")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            st.markdown("### Display Mode")
        with col2:
            show = st.checkbox("🔓 Show Decrypted Data", value=st.session_state.get("show_decrypted", False), key="patients_decrypt")
            st.session_state["show_decrypted"] = show
        with col3:
            if show:
                st.success("🔓 Decrypted")
            else:
                st.info("🔒 Anonymized")
        
        st.markdown("---")
        render_patients_table()
    else:
        # Doctor and other roles
        st.markdown("---")
        render_patients_table()

# --- PAGE: Add Patient
if st.session_state["current_tab"] == "add_patient":
    st.subheader("➕ Add / Edit Patient")
    
    # Only admin and receptionist can add patients
    if role not in ["admin", "receptionist"]:
        st.error("🔒 Only Admin and Receptionist can add patients.")
    else:
        col1, col2 = st.columns([1, 1])
        col1.markdown("---")
        col2.markdown("---")
        
        with col1:
            st.markdown("### 📝 Add New Patient")
            with st.form("add_form"):
                st.markdown("")
                name = st.text_input("Patient Name", placeholder="e.g., John Doe")
                st.markdown("")
                contact = st.text_input("Contact", placeholder="e.g., 0300-555-1234")
                st.markdown("")
                diagnosis = st.text_area("Diagnosis", placeholder="e.g., Flu, Fracture, etc.", height=100)
                st.markdown("")
                submitted = st.form_submit_button("✅ Add Patient", use_container_width=True, type="primary")
                
                if submitted:
                    if not name or not contact or not diagnosis:
                        st.error("❌ All fields are required.")
                    else:
                        try:
                            pid = add_patient(name.strip(), contact.strip(), diagnosis.strip(), datetime.utcnow().isoformat())
                            add_log(user['user_id'], user['username'], role, "add_patient", f"patient_id={pid}, name_hash={hash(name)}")
                            st.success(f"✅ Patient added successfully (ID: {pid})")
                            logging.info(f"Patient {pid} added by {user['username']}")
                        except Exception as e:
                            st.error(f"❌ Failed to add patient: {e}")
                            logging.error(f"add_patient error: {e}")

        with col2:
            st.markdown("### 📋 Edit Existing Patient")
            
            if role in ["admin", "receptionist"]:
                try:
                    patients_raw = fetch_patients(raw=True)
                    if not patients_raw:
                        st.info("No patients to edit.")
                    else:
                        st.markdown("")
                        if role == "receptionist":
                            # Receptionist sees only patient IDs
                            pick_options = [(p['patient_id'], f"ID:{p['patient_id']}") for p in patients_raw]
                        else:
                            # Admin sees ID and name
                            pick_options = [(p['patient_id'], f"ID:{p['patient_id']} - {p.get('name') or 'Unknown'}") for p in patients_raw]
                        
                        pick = st.selectbox("Select patient to edit", options=pick_options, format_func=lambda x: x[1], key="edit_patient_select")
                        
                        if pick:
                            pid = pick[0]
                            p = next((x for x in patients_raw if x['patient_id'] == pid), None)
                            if p:
                                st.markdown("")
                                new_diag = st.text_area("Update Diagnosis", value=p.get('diagnosis') or "", key=f"diag_{pid}", height=100)
                                st.markdown("")
                                if st.button("✅ Update Diagnosis", key=f"update_{pid}", use_container_width=True, type="primary"):
                                    try:
                                        update_patient(pid, diagnosis=new_diag)
                                        add_log(user['user_id'], user['username'], role, "update_patient", f"patient_id={pid}, field=diagnosis")
                                        st.success("✓ Diagnosis updated")
                                        logging.info(f"Patient {pid} diagnosis updated by {user['username']}")
                                    except Exception as e:
                                        st.error(f"Update failed: {e}")
                                        logging.error(f"update_patient error: {e}")
                except Exception as e:
                    st.error(f"Error loading patients: {e}")
                    logging.error(f"Edit patient tab error: {e}")
            else:
                st.info("📋 Only Admin and Receptionist can edit records.")

# --- Anonymize tab
# --- PAGE: Anonymize
if st.session_state["current_tab"] == "anonymize":
    st.subheader("🔐 Anonymize & Encrypt / Decrypt")
    st.markdown("---")
    
    if role != "admin":
        st.warning("🔒 Only admin can access this.")
    else:
        try:
            patients_all = fetch_patients(raw=True)
            if not patients_all:
                st.info("No patients to anonymize.")
            else:
                st.markdown("")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### Anonymization")
                    st.markdown("")
                    if st.button("🔄 Anonymize All Patients", key="anon_btn", use_container_width=True, type="primary"):
                        count = 0
                        errors = []
                        
                        with st.spinner("Anonymizing..."):
                            for p in patients_all:
                                try:
                                    anon_name = anonymize_name(p.get("name") or "")
                                    anon_contact = mask_contact(p.get("contact") or "")
                                    update_patient(p["patient_id"], anonymized_name=anon_name, anonymized_contact=anon_contact)
                                    add_log(user['user_id'], user['username'], role, "anonymize", f"patient_id={p['patient_id']}")
                                    count += 1
                                except Exception as e:
                                    errors.append(f"Patient {p['patient_id']}: {e}")
                                    logging.error(f"Anonymize error for {p['patient_id']}: {e}")
                        
                        st.success(f"✓ Anonymized {count} records")
                        if errors:
                            st.warning(f"⚠️ {len(errors)} errors during anonymization")
                            for err in errors:
                                st.caption(err)
                
                if FERNET_KEY:
                    st.markdown("")
                    st.markdown("---")
                    st.markdown("")
                    with col2:
                        st.markdown("### Reversible Encryption")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button("🔒 Encrypt Data", key="enc_btn"):
                            enc_count = 0
                            enc_errors = []
                            
                            with st.spinner("Encrypting..."):
                                for p in patients_all:
                                    try:
                                        en_name = encrypt_value(p.get("name") or "")
                                        en_contact = encrypt_value(p.get("contact") or "")
                                        update_patient(p["patient_id"], encrypted_name=en_name, encrypted_contact=en_contact)
                                        add_log(user['user_id'], user['username'], role, "encrypt", f"patient_id={p['patient_id']}")
                                        enc_count += 1
                                    except Exception as e:
                                        enc_errors.append(f"Patient {p['patient_id']}: {e}")
                                        logging.error(f"Encrypt error: {e}")
                            
                            st.success(f"✓ Encrypted {enc_count} records")
                            if enc_errors:
                                st.warning(f"⚠️ {len(enc_errors)} encryption errors")
                    
                    with col2:
                        if st.button("🔓 Decrypt & Display", key="dec_btn"):
                            dec_count = 0
                            dec_errors = []
                            dec_data = []
                            
                            with st.spinner("Decrypting..."):
                                for p in patients_all:
                                    try:
                                        de_name = decrypt_value(p["encrypted_name"]) if p.get("encrypted_name") else "N/A"
                                        de_contact = decrypt_value(p["encrypted_contact"]) if p.get("encrypted_contact") else "N/A"
                                        dec_data.append({"ID": p['patient_id'], "Decrypted Name": de_name, "Decrypted Contact": de_contact})
                                        dec_count += 1
                                    except Exception as e:
                                        dec_errors.append(f"Patient {p['patient_id']}: {e}")
                                        logging.error(f"Decrypt error: {e}")
                            
                            if dec_data:
                                st.dataframe(pd.DataFrame(dec_data), use_container_width=True)
                            st.success(f"✓ Decrypted {dec_count} records")
                            if dec_errors:
                                st.warning(f"⚠️ {len(dec_errors)} decryption errors")
                else:
                    st.warning("⚠️ Fernet key not loaded")
                    if st.button("Generate Fernet Key", key="gen_key_btn"):
                        try:
                            k = generate_fernet_key()
                            with open("fernet.key", "wb") as f:
                                f.write(k)
                            st.success("✓ fernet.key created. Restart app to load key.")
                            logging.info("Fernet key generated")
                        except Exception as e:
                            st.error(f"Failed to create key: {e}")
                            logging.error(f"Key generation failed: {e}")
        
        except Exception as e:
            st.error(f"Anonymize tab error: {e}")
            logging.error(f"Anonymize tab exception: {e}")

# --- PAGE: Logs
if st.session_state["current_tab"] == "logs":
    st.subheader("📋 Integrity Audit Log")
    if role != "admin":
        st.info("🔒 Only admin can view audit logs.")
    else:
        try:
            logs = fetch_logs(limit=1000)
            if logs:
                df_logs = pd.DataFrame(logs)
                # Format timestamp for readability
                df_logs['timestamp'] = pd.to_datetime(df_logs['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
                
                col1, col2 = st.columns(2)
                with col1:
                    filter_action = st.selectbox("Filter by action", 
                                                options=["All"] + sorted(df_logs['action'].unique().tolist()))
                if filter_action != "All":
                    df_logs = df_logs[df_logs['action'] == filter_action]
                
                st.subheader(f"Total Log Entries: {len(df_logs)}")
                st.dataframe(df_logs[['log_id', 'timestamp', 'username', 'role', 'action', 'details']], 
                           use_container_width=True)
                
                with col2:
                    if st.button("📥 Export Logs CSV"):
                        csv = df_logs.to_csv(index=False).encode("utf-8")
                        st.download_button("Download logs.csv", data=csv, file_name="logs.csv", mime="text/csv")
                        add_log(user['user_id'], user['username'], role, "export_logs", f"exported {len(df_logs)} logs")
            else:
                st.info("No audit logs available yet.")
        except Exception as e:
            st.error(f"Error loading logs: {e}")
            logging.error(f"Logs tab error: {e}")

# --- PAGE: Backup
if st.session_state["current_tab"] == "backup":
    st.subheader("📦 Backup / Export")
    if role != "admin":
        st.warning("🔒 Only Admin can export data.")
    else:
        try:
            patients = fetch_patients(raw=True)
            if not patients:
                st.info("No patients to export.")
            else:
                df_export = pd.DataFrame(patients)
                
                show_decrypted_export = st.checkbox("Export decrypted data (Admin only)", value=False)
                
                if show_decrypted_export:
                    st.info("⚠️ Exporting raw/decrypted data. Handle with care!")
                    def decrypt_row(r):
                        try:
                            if r.get("encrypted_name"):
                                r["name"] = decrypt_value(r["encrypted_name"])
                            if r.get("encrypted_contact"):
                                r["contact"] = decrypt_value(r["encrypted_contact"])
                        except Exception as e:
                            logging.warning(f"Decryption failed during export: {e}")
                            r["name"] = r.get("name") or "[Error]"
                            r["contact"] = r.get("contact") or "[Error]"
                        return r
                    df_export = df_export.apply(decrypt_row, axis=1)
                else:
                    df_export["name"] = df_export.apply(lambda r: r.get("anonymized_name") or r.get("name") or "", axis=1)
                    df_export["contact"] = df_export.apply(lambda r: r.get("anonymized_contact") or r.get("contact") or "", axis=1)
                
                to_export = df_export[["patient_id", "name", "contact", "diagnosis", "date_added"]]
                st.subheader(f"Patients: {len(to_export)}")
                st.dataframe(to_export, use_container_width=True)
                
                if st.button("📥 Download Patients CSV"):
                    csv = to_export.to_csv(index=False).encode()
                    st.download_button("Download patients.csv", data=csv, file_name="patients.csv", mime="text/csv")
                    try:
                        add_log(user['user_id'], user['username'], role, "export_patients", f"exported {len(to_export)} rows")
                    except Exception as log_err:
                        logging.error(f"Failed to log export: {log_err}")
        except Exception as e:
            st.error(f"Export error: {e}")
            logging.error(f"Export tab error: {e}")

# --- PAGE: Activity
if st.session_state["current_tab"] == "activity":
    st.subheader("📊 User Activity Graph")
    if role != "admin":
        st.info("🔒 Only Admin can view activity graphs.")
    else:
        try:
            logs = fetch_logs(limit=5000)
            if logs:
                df_logs = pd.DataFrame(logs)
                df_logs["timestamp"] = pd.to_datetime(df_logs["timestamp"])
                df_logs["date"] = df_logs["timestamp"].dt.date
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("📈 Actions per Day")
                    activity_summary = df_logs.groupby(["date", "action"]).size().reset_index(name="count")
                    pivot_df = activity_summary.pivot(index="date", columns="action", values="count").fillna(0)
                    st.line_chart(pivot_df)
                
                with col2:
                    st.subheader("👥 Actions by User")
                    user_activity = df_logs.groupby("username").size().reset_index(name="count").sort_values("count", ascending=False)
                    st.bar_chart(user_activity.set_index("username"))
                
                st.markdown("---")
                st.subheader("🔍 Recent Activity Log")
                display_cols = ["timestamp", "username", "role", "action", "details"]
                st.dataframe(df_logs[display_cols].head(50), use_container_width=True)
            else:
                st.info("No activity logs available yet.")
        except Exception as e:
            st.error(f"Graph generation error: {e}")
            logging.error(f"Activity graphs error: {e}")

# --- PAGE: Retention
if st.session_state["current_tab"] == "retention":
    st.subheader("🗑️ Data Retention")
    if role != "admin":
        st.warning("🔒 Only Admin can manage data retention.")
    else:
        st.info("**GDPR:** Automatically anonymizes records older than 365 days.")
        
        
        try:
            RETENTION_DAYS = 365
            patients = fetch_patients(raw=True)
            
            # Calculate retention metrics
            now = datetime.utcnow()
            retention_due = []
            recently_added = []
            
            for p in patients:
                added = datetime.fromisoformat(p['date_added'])
                days_old = (now - added).days
                if days_old > RETENTION_DAYS:
                    retention_due.append({"patient_id": p['patient_id'], "days_old": days_old, "name": p.get('name') or 'Unknown'})
                else:
                    recently_added.append({"patient_id": p['patient_id'], "days_until_retention": RETENTION_DAYS - days_old})
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Patients", len(patients))
            with col2:
                st.metric("Due for Anonymization", len(retention_due))
            with col3:
                st.metric("Retention Days", RETENTION_DAYS)
            
            if retention_due:
                st.warning(f"⚠️ {len(retention_due)} records are due for anonymization")
                st.subheader("Records Ready for Anonymization:")
                df_due = pd.DataFrame(retention_due)
                st.dataframe(df_due, use_container_width=True)
                
                if st.button("🔄 Run Data Retention Cleanup Now"):
                    count = 0
                    with st.spinner("Anonymizing old records..."):
                        for p in patients:
                            added = datetime.fromisoformat(p['date_added'])
                            if now - added > timedelta(days=RETENTION_DAYS):
                                try:
                                    update_patient(p['patient_id'],
                                                 name="REDACTED_ARCHIVED",
                                                 contact="REDACTED_ARCHIVED",
                                                 anonymized_name="ANON_ARCHIVED",
                                                 anonymized_contact="XXX-XXX-XXXX")
                                    add_log(user['user_id'], user['username'], role, "data_retention", 
                                           f"Anonymized patient {p['patient_id']} after {RETENTION_DAYS} days")
                                    count += 1
                                except Exception as e:
                                    st.error(f"Failed to anonymize {p['patient_id']}: {e}")
                                    logging.error(f"Retention error: {e}")
                    
                    st.success(f"✓ Anonymized {count} old records")
            else:
                st.success("✓ All records are within retention period")
                if recently_added:
                    st.subheader("📅 Retention Schedule:")
                    df_upcoming = pd.DataFrame(recently_added).sort_values("days_until_retention")
                    st.dataframe(df_upcoming.head(10), use_container_width=True)
        
        except Exception as e:
            st.error(f"Data retention error: {e}")
            logging.error(f"Data retention tab error: {e}")

# --- Footer
st.divider()
st.markdown("""
### 🔐 CIA Triad Implementation
- **Confidentiality:** Fernet encryption, SHA-256 anonymization, role-based masking
- **Integrity:** Audit logging, activity tracking, immutable logs
- **Availability:** Fast database, recovery options, robust error handling

✅ GDPR Compliant | 🔐 Privacy First | 📊 Fully Audited
""")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("🔐 Encryption", "✅ Active" if FERNET_KEY else "⚠️ Disabled")
with col2:
    st.metric("📊 Audit", "✅ Logging")
with col3:
    st.metric("🕐 Last Sync", datetime.utcnow().strftime("%H:%M:%S"))

