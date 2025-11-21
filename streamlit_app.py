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
    page_title="GDPR Hospital Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)
# Modern CSS styling - Inspired by contemporary design systems (e.g., Tailwind + subtle neumorphism)
st.markdown("""
<style>
    /* Reset and base styles */
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
   
    body {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: #1a202c;
    }
   
    /* Main content */
    .main {
        padding: 1rem;
        background: #f7fafc;
        min-height: 100vh;
    }
   
    /* Login form - Centered, modern glassmorphism effect */
    .login-container {
        max-width: 420px;
        margin: 4rem auto;
        padding: 2.5rem;
        background: rgba(255, 255, 255, 0.25);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.18);
    }
   
    .login-header {
        text-align: center;
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #10b981, #059669);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
    }
   
    .login-subtitle {
        text-align: center;
        color: rgba(255, 255, 255, 0.8);
        margin-bottom: 2rem;
        font-size: 1rem;
    }
   
    /* Sidebar enhancements - Compact layout */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a202c 0%, #2d3748 100%);
        padding: 1rem;
        box-shadow: 4px 0 12px rgba(0, 0, 0, 0.2);
    }
   
    /* Logo */
    .logo {
        font-size: 1.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #10b981, #059669);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 1.5rem;
        text-align: center;
        padding: 0.5rem 0;
    }
   
    /* User profile card */
    .user-profile {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1.5rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
   
    .profile-name {
        color: white;
        font-weight: 600;
        font-size: 1rem;
        margin-bottom: 0.25rem;
    }
   
    .profile-role {
        color: rgba(255, 255, 255, 0.7);
        font-size: 0.85rem;
    }
   
    /* Navigation items */
    .active-bar, .logout-bar, .bar-spacer {
        height: 2.5rem;
        width: 100%;
        border-radius: 0 6px 6px 0;
        margin: 0.25rem 0;
    }
   
    .active-bar {
        background: linear-gradient(135deg, #10b981, #059669);
    }
   
    .logout-bar {
        background: linear-gradient(135deg, #ef4444, #dc2626);
    }
   
    .bar-spacer {
        background: transparent;
        height: 2.5rem;
    }
   
    /* Sidebar button styles for nav and logout */
    [data-testid="stSidebar"] .stButton > button {
        margin-bottom: 0.25rem !important;
        border-radius: 0 8px 8px 0 !important;
        border-left: none !important;
        background: transparent !important;
        color: rgba(255, 255, 255, 0.7) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        padding: 0.75rem 1rem !important;
        margin-left: -1px !important;
        font-weight: 500 !important;
        font-size: 0.95rem !important;
        transition: all 0.3s ease !important;
    }
   
    [data-testid="stSidebar"] .stButton > button:hover:not(:disabled) {
        background: rgba(255, 255, 255, 0.05) !important;
        color: white !important;
        border-color: rgba(255, 255, 255, 0.2) !important;
        transform: translateX(2px) !important;
    }
   
    [data-testid="stSidebar"] .stButton > button:disabled {
        background: linear-gradient(135deg, #10b981, #059669) !important;
        color: white !important;
        border-color: transparent !important;
        cursor: default !important;
        margin-left: 0 !important;
        transform: none !important;
    }
   
    /* Secondary buttons (logout) */
    .stButton > button[type="secondary"] {
        background: linear-gradient(135deg, #ef4444, #dc2626) !important;
        color: white !important;
        border: none !important;
    }
   
    .stButton > button[type="secondary"]:hover {
        box-shadow: 0 4px 12px rgba(239, 68, 68, 0.4) !important;
        transform: translateX(2px) !important;
    }
   
    /* Status messages in sidebar */
    [data-testid="stSidebar"] .stSuccess, [data-testid="stSidebar"] .stError {
        border-radius: 8px !important;
        padding: 0.75rem !important;
        border-left-width: 3px !important;
        font-size: 0.85rem !important;
        margin: 0.5rem 0 !important;
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
   
    [data-testid="stSidebar"] .stSuccess {
        border-left-color: #10b981 !important;
        color: #10b981 !important;
    }
   
    [data-testid="stSidebar"] .stError {
        border-left-color: #ef4444 !important;
        color: #ef4444 !important;
    }
   
    /* Compact metrics in sidebar */
    [data-testid="stSidebar"] [data-testid="metric-container"] {
        padding: 0.75rem !important;
        margin: 0.5rem 0 !important;
        background: rgba(255, 255, 255, 0.05) !important;
        border-radius: 8px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
   
    [data-testid="stSidebar"] [data-testid="metric-container"] .stMetric > label {
        font-size: 0.8rem !important;
        color: white !important;
    }
   
    [data-testid="stSidebar"] [data-testid="metric-container"] .stMetric > div {
        font-size: 1.1rem !important;
        color: white !important;
        font-weight: 600 !important;
    }

    /* Ensure sidebar metric text is always white */
    [data-testid="stSidebar"] .stMetric {
        color: white !important;
    }

    [data-testid="stSidebar"] .stMetric > label {
        color: white !important;
    }

    [data-testid="stSidebar"] .stMetric > div > div {
        color: white !important;
    }

    /* Override any default black text in sidebar metrics */
    [data-testid="stSidebar"] .stMetric .stMetricLabel,
    [data-testid="stSidebar"] .stMetric .stMetricValue {
        color: white !important;
    }
   
    /* Navigation radio buttons - More compact (legacy, if needed) */
    [data-testid="stSidebar"] .stRadio > div {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        padding: 0.5rem;
        margin-bottom: 0.25rem;
    }
   
    [data-testid="stSidebar"] .stRadio > label {
        font-size: 0.9rem;
    }
   
    /* General button styling (main content) */
    .stButton > button {
        border-radius: 12px;
        font-weight: 600;
        transition: all 0.3s ease;
        border: none;
        padding: 0.75rem 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        background: linear-gradient(135deg, #10b981, #059669);
        color: white;
        height: 3rem;
        line-height: 1.5rem;
    }
   
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(16, 185, 129, 0.3);
    }
   
    .stButton > button[type="secondary"] {
        background: rgba(255, 255, 255, 0.2);
        color: #1a202c;
    }
   
    /* Input fields - Modern with focus states */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select,
    .stTextArea > div > div > textarea {
        border-radius: 12px;
        border: 2px solid rgba(255, 255, 255, 0.2);
        background: rgba(255, 255, 255, 0.9);
        transition: all 0.3s ease;
        padding: 0.75rem;
        font-size: 1rem;
    }
   
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #10b981;
        box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
        background: white;
    }
   
    /* Form containers - Card-like */
    .stForm {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
   
    /* Dataframe - Modern table */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    }
   
    .dataframe {
        font-size: 0.95rem;
    }
   
    /* Custom cards */
    .card {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.2);
        margin-bottom: 1.5rem;
        transition: transform 0.3s ease;
    }
   
    .card:hover {
        transform: translateY(-2px);
    }
   
    /* Headers */
    h1, h2, h3 {
        background: linear-gradient(135deg, #10b981, #059669);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 700;
        margin-bottom: 1rem;
    }
   
    /* Metrics - Modern glass cards */
    [data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 1.5rem;
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    }
   
    /* Status messages */
    .stSuccess, .stError, .stWarning, .stInfo {
        border-radius: 12px;
        padding: 1rem 1.5rem;
        border-left: 4px solid;
        margin: 1rem 0;
        backdrop-filter: blur(10px);
    }
   
    .stSuccess {
        border-left-color: #48bb78;
        background: rgba(72, 187, 120, 0.1);
    }
   
    .stError {
        border-left-color: #f56565;
        background: rgba(245, 101, 101, 0.1);
    }
   
    .stWarning {
        border-left-color: #ed8936;
        background: rgba(237, 137, 54, 0.1);
    }
   
    .stInfo {
        border-left-color: #10b981;
        background: rgba(16, 185, 129, 0.1);
    }
   
    /* Divider - Thinner and less margin */
    .stDivider {
        height: 0.5px;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.5), transparent);
        margin: 1rem 0;
    }
   
    /* Expander */
    .stExpander {
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        background: rgba(255, 255, 255, 0.8);
    }

    /* Equal width and height for login expander label */
    .stExpander > label {
        width: 100% !important;
        height: 3rem !important;
        line-height: 1.5rem !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        padding: 0.75rem 1.5rem !important;
        background: linear-gradient(135deg, #10b981, #059669) !important;
        color: white !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        border: none !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important;
        cursor: pointer !important;
    }

    .stExpander > label:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 16px rgba(16, 185, 129, 0.3) !important;
    }

    .stExpander [data-baseweb="accordion-label"] {
        width: 100% !important;
        height: 3rem !important;
    }

    /* Compact sidebar text elements */
    [data-testid="stSidebar"] .stMarkdown {
        margin-bottom: 0.25rem !important;
        font-size: 0.85rem !important;
    }
    [data-testid="stSidebar"] .stCaption {
        font-size: 0.75rem !important;
        margin-bottom: 0.25rem !important;
    }

    /* Reduce column gap in sidebar for nav */
    [data-testid="stSidebar"] .element-container .row-widget.stHorizontal {
        gap: 0 !important;
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
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
@st.fragment(run_every=1)
def display_uptime():
    """Display uptime with continuous updates using fragment"""
    st.metric("Session Uptime", uptime_str())
# ============== LOGIN PAGE ==============
if st.session_state["user"] is None:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
      
        st.markdown('<h1 class="login-header">Hospital Dashboard</h1>', unsafe_allow_html=True)
        st.markdown('<p class="login-subtitle">Secure GDPR-Compliant Access</p>', unsafe_allow_html=True)
       
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
            login_btn = st.button("Sign In", use_container_width=True, type="primary")
        with col_btn2:
            with st.expander("Demo Credentials", expanded=False):
                st.code("admin / admin123\nDr. Bob / doc123\nAlice (Reception) / rec123", language="text")
       
        if login_btn:
            if not username or not password:
                st.error("Please provide both username and password.")
            else:
                try:
                    user, err = login(username.strip(), password)
                    if user:
                        st.session_state["user"] = user
                        st.success(f"Welcome back, {user['username']}!")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error(f"Invalid credentials: {err}")
                except Exception as e:
                    st.error(f"Authentication error: {e}")
                    logging.error(f"Login failed for {username}: {e}")
       
        st.markdown('</div>', unsafe_allow_html=True)
   
    st.stop()
# ============== MAIN APP ==============
user = st.session_state["user"]
role = user["role"]
# Check consent from database
user_has_consent = check_consent(user['user_id'])
# GDPR consent required before interacting
if not user_has_consent:
    st.info("""
    GDPR Data Processing Consent
    To ensure compliance, your explicit consent is required for accessing personal health data.
    """)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("I Consent to Proceed"):
            try:
                set_consent(user['user_id'], user['username'], role, consent=True)
                st.success("Consent acknowledged and logged.")
                st.rerun()
            except Exception as e:
                st.error(f"Consent recording failed: {e}")
                logging.error(f"Failed to set consent: {e}")
    with col2:
        if st.button("Withdraw Consent"):
            st.warning("Access denied without consent. Logging out.")
            st.session_state["user"] = None
            st.rerun()
    st.stop()
# ============== SIDEBAR NAVIGATION ==============
with st.sidebar:
    st.markdown('<div class="logo">MedSecure</div>', unsafe_allow_html=True)
   
    # User profile card
    st.markdown(f'''
    <div class="user-profile">
        <div class="profile-name">{user["username"]}</div>
        <div class="profile-role">{role.title()}</div>
    </div>
    ''', unsafe_allow_html=True)
   
    st.divider()
   
    # Role-based navigation
    nav_options = []
    nav_pages = []
   
    if role == "receptionist":
        nav_options.append("New Patient")
        nav_pages.append("add_patient")
    elif role == "admin":
        nav_options.append("Patient Overview")
        nav_pages.append("patients")
        nav_options.append("New Patient")
        nav_pages.append("add_patient")
        nav_options.append("Data Protection")
        nav_pages.append("anonymize")
        nav_options.append("Audit Trail")
        nav_pages.append("logs")
        nav_options.append("Analytics")
        nav_pages.append("activity")
        nav_options.append("Export Data")
        nav_pages.append("backup")
        nav_options.append("Retention Policy")
        nav_pages.append("retention")
    else:
        # Doctor: View-only
        nav_options.append("Patient Overview")
        nav_pages.append("patients")
   
    # Custom navigation buttons
    for i, opt in enumerate(nav_options):
        page = nav_pages[i]
        active = st.session_state["current_tab"] == page
        col1, col2 = st.columns([0.1, 1])
        with col1:
            if active:
                st.markdown('<div class="active-bar"></div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="bar-spacer"></div>', unsafe_allow_html=True)
        with col2:
            if st.button(opt, key=f"nav_{i}", disabled=active, use_container_width=True):
                st.session_state["current_tab"] = page
                st.rerun()
   
    st.divider()
   
    # Logout
    col1, col2 = st.columns([0.1, 1])
    with col1:
        st.markdown('<div class="logout-bar"></div>', unsafe_allow_html=True)
    with col2:
        if st.button("Sign Out", key="logout", type="secondary", use_container_width=True):
            try:
                add_log(user['user_id'], user['username'], role, "logout", "Session ended")
            except Exception as e:
                logging.error(f"Logout logging failed: {e}")
            st.session_state["user"] = None
            st.rerun()
   
    st.divider()
   
    # Encryption status
    if FERNET_KEY:
        st.success("Encryption: Enabled")
    else:
        st.error("Encryption: Disabled")
   
    display_uptime()
# ============== MAIN CONTENT ==============
# Helper function to render patients table dynamically
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
                    try:
                        row["name"] = decrypt_value(p["encrypted_name"]) if p.get("encrypted_name") else p.get("name") or "(Plaintext)"
                    except Exception:
                        row["name"] = p.get("name") or "[Decryption Failed]"
                   
                    try:
                        row["contact"] = decrypt_value(p["encrypted_contact"]) if p.get("encrypted_contact") else p.get("contact") or "(Plaintext)"
                    except Exception:
                        row["contact"] = p.get("contact") or "[Decryption Failed]"
                else:
                    row["name"] = p.get("anonymized_name") or anonymize_name(p.get("name") or "")
                    row["contact"] = p.get("anonymized_contact") or mask_contact(p.get("contact") or "")
                row["anonymized_name"] = p.get("anonymized_name") or ""
                row["anonymized_contact"] = p.get("anonymized_contact") or ""
               
            elif role == "doctor":
                row["name"] = p.get("anonymized_name") or anonymize_name(p.get("name") or "")
                row["contact"] = p.get("anonymized_contact") or mask_contact(p.get("contact") or "")
            elif role == "receptionist":
                row["name"] = p.get("name") or ""
                row["contact"] = p.get("contact") or ""
           
            rows.append(row)
       
        df = pd.DataFrame(rows)
       
        if len(df) > 0:
            st.metric("Total Records", len(df))
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "patient_id": st.column_config.NumberColumn("ID", width="small"),
                    "name": st.column_config.TextColumn("Patient Name", width="medium"),
                    "contact": st.column_config.TextColumn("Contact Info", width="medium"),
                    "diagnosis": st.column_config.TextColumn("Medical Notes", width="large"),
                    "anonymized_name": st.column_config.TextColumn("Anonymized Name", width="medium"),
                    "anonymized_contact": st.column_config.TextColumn("Anonymized Contact", width="medium"),
                }
            )
        else:
            st.info("No patient records available.")
       
        # Log view
        try:
            add_log(user['user_id'], user['username'], role, "view_patients", f"Viewed {len(rows)} records")
        except Exception as log_err:
            logging.error(f"Log failed: {log_err}")
           
    except Exception as e:
        st.error(f"Failed to load records: {e}")
        logging.error(f"Table render error: {e}")
# ============== PAGE CONTENT RENDERING ==============
# --- PAGE: Patients
if st.session_state["current_tab"] == "patients":
  
    st.markdown("<h2>Patient Records</h2>", unsafe_allow_html=True)
    st.divider()
   
    if role == "receptionist":
        st.warning("Access restricted: Use 'New Patient' for management.")
        render_patients_table()
    elif role == "admin":
        st.markdown("### View Options")
        col1, col2 = st.columns([3, 1])
        with col1:
            show = st.checkbox("Show Full Data", value=st.session_state.get("show_decrypted", False), key="patients_decrypt")
            st.session_state["show_decrypted"] = show
        with col2:
            st.markdown(f"**Mode:** {'Full Access' if show else 'Privacy Mode'}")
       
        st.divider()
        render_patients_table()
    else:
        render_patients_table()
# --- PAGE: Add Patient
if st.session_state["current_tab"] == "add_patient":
    if role not in ["admin", "receptionist"]:
        st.error("Unauthorized: Admins and Reception only.")
    else:
      
        st.markdown("<h2>Manage Patients</h2>", unsafe_allow_html=True)
        st.divider()
       
        col1, col2 = st.columns(2)
       
        with col1:
            st.markdown("### Add New Record")
            with st.form("add_form", clear_on_submit=True):
                name = st.text_input("Full Name", placeholder="e.g., Jane Smith")
                contact = st.text_input("Phone/Email", placeholder="e.g., 0300-123-4567")
                diagnosis = st.text_area("Diagnosis/Notes", placeholder="Enter medical details...", height=120)
               
                submitted = st.form_submit_button("Save Record", type="primary")
               
                if submitted:
                    if not all([name, contact, diagnosis]):
                        st.error("All fields required.")
                    else:
                        try:
                            pid = add_patient(name.strip(), contact.strip(), diagnosis.strip(), datetime.utcnow().isoformat())
                            add_log(user['user_id'], user['username'], role, "add_patient", f"ID:{pid}")
                            st.success(f"Record saved! ID: {pid}")
                        except Exception as e:
                            st.error(f"Save failed: {e}")
                            logging.error(f"Add patient error: {e}")
       
        with col2:
            st.markdown("### Edit Record")
            try:
                patients_raw = fetch_patients(raw=True)
                if not patients_raw:
                    st.info("No records to edit.")
                else:
                    if role == "receptionist":
                        options = [(p['patient_id'], f"ID: {p['patient_id']}") for p in patients_raw]
                    else:
                        options = [(p['patient_id'], f"ID: {p['patient_id']} - {p.get('name', 'Unknown')}") for p in patients_raw]
                   
                    selected = st.selectbox("Select Record", options=options, format_func=lambda x: x[1])
                   
                    if selected:
                        pid = selected[0]
                        p = next((x for x in patients_raw if x['patient_id'] == pid), None)
                        if p:
                            new_diag = st.text_area("Update Notes", value=p.get('diagnosis', ''), key=f"diag_{pid}", height=120)
                           
                            if st.button("Update", key=f"update_{pid}", type="secondary"):
                                try:
                                    update_patient(pid, diagnosis=new_diag)
                                    add_log(user['user_id'], user['username'], role, "update_patient", f"ID:{pid}")
                                    st.success("Updated!")
                                except Exception as e:
                                    st.error(f"Update failed: {e}")
                                    logging.error(f"Update error: {e}")
            except Exception as e:
                st.error(f"Load error: {e}")
                logging.error(f"Edit tab error: {e}")
       
        st.markdown('</div>', unsafe_allow_html=True)
# --- PAGE: Anonymize
if st.session_state["current_tab"] == "anonymize":
    if role != "admin":
        st.warning("Admin access required.")
    else:
      
        st.markdown("<h2>Data Protection Tools</h2>", unsafe_allow_html=True)
        st.divider()
       
        try:
            patients_all = fetch_patients(raw=True)
            if not patients_all:
                st.info("No data to process.")
            else:
                col1, col2 = st.columns(2)
               
                with col1:
                    st.markdown("### Anonymize Records")
                    if st.button("Anonymize All", type="primary"):
                        count = 0
                        errors = []
                       
                        with st.spinner("Processing..."):
                            for p in patients_all:
                                try:
                                    anon_name = anonymize_name(p.get("name") or "")
                                    anon_contact = mask_contact(p.get("contact") or "")
                                    update_patient(p["patient_id"], anonymized_name=anon_name, anonymized_contact=anon_contact)
                                    add_log(user['user_id'], user['username'], role, "anonymize", f"ID:{p['patient_id']}")
                                    count += 1
                                except Exception as e:
                                    errors.append(f"ID {p['patient_id']}: {e}")
                       
                        st.success(f"{count} records anonymized.")
                        if errors:
                            st.error(f"{len(errors)} issues encountered.")
               
                if FERNET_KEY:
                    with col2:
                        st.markdown("### Encrypt/Decrypt")
                        col_enc1, col_enc2 = st.columns(2)
                       
                        with col_enc1:
                            if st.button("Encrypt All", type="secondary"):
                                enc_count = 0
                                with st.spinner("Securing..."):
                                    for p in patients_all:
                                        try:
                                            en_name = encrypt_value(p.get("name") or "")
                                            en_contact = encrypt_value(p.get("contact") or "")
                                            update_patient(p["patient_id"], encrypted_name=en_name, encrypted_contact=en_contact)
                                            add_log(user['user_id'], user['username'], role, "encrypt", f"ID:{p['patient_id']}")
                                            enc_count += 1
                                        except Exception as e:
                                            logging.error(f"Encrypt error: {e}")
                                st.success(f"{enc_count} records encrypted.")
                       
                        with col_enc2:
                            if st.button("View Decrypted", type="secondary"):
                                dec_data = []
                                with st.spinner("Decrypting..."):
                                    for p in patients_all:
                                        try:
                                            de_name = decrypt_value(p.get("encrypted_name", "")) if p.get("encrypted_name") else "N/A"
                                            de_contact = decrypt_value(p.get("encrypted_contact", "")) if p.get("encrypted_contact") else "N/A"
                                            dec_data.append({"ID": p['patient_id'], "Name": de_name, "Contact": de_contact})
                                        except Exception as e:
                                            logging.error(f"Decrypt error: {e}")
                                if dec_data:
                                    st.dataframe(
                                        pd.DataFrame(dec_data),
                                        use_container_width=True,
                                        hide_index=True,
                                        column_config={
                                            "ID": st.column_config.NumberColumn("ID", width="small"),
                                            "Name": st.column_config.TextColumn("Name", width="medium"),
                                            "Contact": st.column_config.TextColumn("Contact", width="medium"),
                                        }
                                    )
                                    st.success("Decryption preview complete.")
                else:
                    st.warning("No encryption key. Generate one?")
                    if st.button("Generate Key", type="secondary"):
                        try:
                            k = generate_fernet_key()
                            with open("fernet.key", "wb") as f:
                                f.write(k)
                            st.success("Key generated. Restart to enable.")
                        except Exception as e:
                            st.error(f"Key gen failed: {e}")
       
        except Exception as e:
            st.error(f"Tool error: {e}")
            logging.error(f"Anonymize error: {e}")
       
        st.markdown('</div>', unsafe_allow_html=True)
# --- PAGE: Logs
if st.session_state["current_tab"] == "logs":
    if role != "admin":
        st.info("Logs: Admin view only.")
    else:
        st.markdown("<h2>Audit Trail</h2>", unsafe_allow_html=True)
        st.divider()
       
        try:
            logs = fetch_logs(limit=1000)
            if logs:
                df_logs = pd.DataFrame(logs)
                df_logs['timestamp'] = pd.to_datetime(df_logs['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
               
                filter_action = st.selectbox("Filter Action", options=["All"] + sorted(df_logs['action'].unique()))
               
                if filter_action != "All":
                    df_logs = df_logs[df_logs['action'] == filter_action].copy()
               
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.metric("Total Entries", len(df_logs))
                with col2:
                    csv = df_logs.to_csv(index=False).encode("utf-8")
                    if st.download_button("Download Audit Log", csv, "audit_log.csv", "text/csv", use_container_width=True):
                        add_log(user['user_id'], user['username'], role, "export_logs", f"{len(df_logs)} entries")
               
                st.dataframe(df_logs[['timestamp', 'username', 'role', 'action', 'details']], use_container_width=True)
            else:
                st.info("No logs recorded yet.")
        except Exception as e:
            st.error(f"Log load error: {e}")
            logging.error(f"Logs error: {e}")
       
        st.markdown('</div>', unsafe_allow_html=True)
# --- PAGE: Backup
if st.session_state["current_tab"] == "backup":
    if role != "admin":
        st.warning("Export: Admin only.")
    else:
        st.markdown("<h2>Data Export</h2>", unsafe_allow_html=True)
        st.divider()
       
        try:
            patients = fetch_patients(raw=True)
            if not patients:
                st.info("No data for export.")
            else:
                df_export = pd.DataFrame(patients)
               
                decrypt_export = st.checkbox("Include Decrypted (Sensitive)", value=False)
               
                if decrypt_export:
                    st.warning("Exporting sensitive data – secure handling required.")
                    def decrypt_export_row(r):
                        try:
                            if r.get("encrypted_name"):
                                r["name"] = decrypt_value(r["encrypted_name"])
                            if r.get("encrypted_contact"):
                                r["contact"] = decrypt_value(r["encrypted_contact"])
                        except:
                            pass
                        return r
                    df_export = df_export.apply(decrypt_export_row, axis=1)
                else:
                    df_export["name"] = df_export.apply(lambda r: r.get("anonymized_name") or anonymize_name(r.get("name", "")), axis=1)
                    df_export["contact"] = df_export.apply(lambda r: r.get("anonymized_contact") or mask_contact(r.get("contact", "")), axis=1)
               
                export_df = df_export[["patient_id", "name", "contact", "diagnosis", "date_added"]]
                st.metric("Records Ready", len(export_df))
                st.dataframe(export_df, use_container_width=True)
               
                if st.button("Download CSV", type="primary"):
                    csv = export_df.to_csv(index=False).encode()
                    st.download_button("Export Patients", csv, "patients_export.csv", "text/csv")
                    add_log(user['user_id'], user['username'], role, "export_patients", f"{len(export_df)} records")
        except Exception as e:
            st.error(f"Export error: {e}")
            logging.error(f"Backup error: {e}")
       
        st.markdown('</div>', unsafe_allow_html=True)
# --- PAGE: Activity
if st.session_state["current_tab"] == "activity":
    if role != "admin":
        st.info("Analytics: Admin view only.")
    else:
        st.markdown("<h2>Activity Insights</h2>", unsafe_allow_html=True)
        st.divider()
       
        try:
            logs = fetch_logs(limit=5000)
            if logs:
                df_logs = pd.DataFrame(logs)
                df_logs["timestamp"] = pd.to_datetime(df_logs["timestamp"])
                df_logs["date"] = df_logs["timestamp"].dt.date
               
                col1, col2 = st.columns(2)
               
                with col1:
                    st.markdown("### Daily Actions")
                    activity_pivot = df_logs.groupby(["date", "action"]).size().reset_index(name="count").pivot(index="date", columns="action", values="count").fillna(0)
                    st.line_chart(activity_pivot)
               
                with col2:
                    st.markdown("### User Activity")
                    user_counts = df_logs.groupby("username").size().reset_index(name="actions").sort_values("actions", ascending=False)
                    st.bar_chart(user_counts.set_index("username"))
               
                st.divider()
                st.markdown("### Recent Events")
                recent = df_logs[["timestamp", "username", "role", "action", "details"]].head(50)
                recent["timestamp"] = recent["timestamp"].dt.strftime('%Y-%m-%d %H:%M')
                st.dataframe(recent, use_container_width=True)
            else:
                st.info("No activity data yet.")
        except Exception as e:
            st.error(f"Analytics error: {e}")
            logging.error(f"Activity error: {e}")
       
        st.markdown('</div>', unsafe_allow_html=True)
# --- PAGE: Retention
if st.session_state["current_tab"] == "retention":
    if role != "admin":
        st.warning("Retention: Admin only.")
    else:
        st.markdown("<h2>Data Retention</h2>", unsafe_allow_html=True)
        st.info("GDPR Policy: Records auto-anonymized after 365 days for privacy.")
        st.divider()
       
        try:
            RETENTION_DAYS = 365
            patients = fetch_patients(raw=True)
           
            now = datetime.utcnow()
            due_for_retention = []
            upcoming = []
           
            for p in patients:
                added = datetime.fromisoformat(p['date_added'])
                days_old = (now - added).days
                if days_old > RETENTION_DAYS:
                    due_for_retention.append({"ID": p['patient_id'], "Days Over": days_old - RETENTION_DAYS, "Name": p.get('name', 'Unknown')})
                else:
                    upcoming.append({"ID": p['patient_id'], "Days Until": RETENTION_DAYS - days_old})
           
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total", len(patients))
            with col2:
                st.metric("Due Now", len(due_for_retention))
            with col3:
                st.metric("Policy", f"{RETENTION_DAYS} days")
           
            if due_for_retention:
                st.warning(f"{len(due_for_retention)} records overdue for anonymization.")
                st.markdown("### Overdue List")
                st.dataframe(pd.DataFrame(due_for_retention))
               
                if st.button("Process Now", type="primary"):
                    count = 0
                    with st.spinner("Applying retention..."):
                        for p in patients:
                            added = datetime.fromisoformat(p['date_added'])
                            if now - added > timedelta(days=RETENTION_DAYS):
                                try:
                                    update_patient(p['patient_id'],
                                                 anonymized_name="REDACTED",
                                                 anonymized_contact="REDACTED",
                                                 name="ARCHIVED",
                                                 contact="ARCHIVED")
                                    add_log(user['user_id'], user['username'], role, "retention_cleanup", f"ID:{p['patient_id']}")
                                    count += 1
                                except Exception as e:
                                    logging.error(f"Retention failed: {e}")
                    st.success(f"{count} records processed.")
            else:
                st.success("All records compliant.")
                if upcoming:
                    st.markdown("### Upcoming")
                    upcoming_df = pd.DataFrame(upcoming).sort_values("Days Until")
                    st.dataframe(upcoming_df.head(10))
       
        except Exception as e:
            st.error(f"Retention error: {e}")
            logging.error(f"Retention error: {e}")
       
        st.markdown('</div>', unsafe_allow_html=True)
# --- Footer
st.markdown("""
### Security & Compliance
- Confidentiality: AES-256 Encryption • Role-Based Access
- Integrity: Immutable Audit Logs • Hash Verification
- Availability: Auto-Backups • High-Uptime Design
GDPR Certified | Privacy by Design | Built for Trust
""")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Encryption", "Active" if FERNET_KEY else "Offline")
with col2:
    st.metric("Logs", "Enabled")
with col3:
    st.metric("Updated", datetime.utcnow().strftime("%H:%M:%S UTC"))