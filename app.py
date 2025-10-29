import streamlit as st
from db import users_col
from auth import verify_password, hash_password
from datetime import datetime
from streamlit_option_menu import option_menu  # Import the new menu component

# Import all modules
from modules import attendance, leaves, employee_dashboard, admin_hr_dashboard, profile_page

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="HRMS Pro",
    page_icon="🏢",
    layout="wide"
)

# --- FUNCTION TO LOAD CSS & FONT AWESOME ICONS ---
def load_css_and_icons(file_name):
    """Loads a local CSS file and the Font Awesome icon library."""
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    st.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">', unsafe_allow_html=True)

# Load the custom styles
load_css_and_icons("style.css")

# --- SESSION STATE & AUTH FUNCTIONS ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_info' not in st.session_state: st.session_state.user_info = None

def login_user(username, password):
    """Authenticates user and updates session state."""
    user_data = users_col.find_one({"username": username})
    if user_data and verify_password(password, user_data['password_hash']):
        st.session_state.logged_in = True
        st.session_state.user_info = {
            "username": user_data['username'],
            "role": user_data['role'],
            "employee_id": user_data['employee_id']
        }
        st.rerun()
    else:
        st.error("❌ Invalid username or password")

def logout_user():
    """Logs out user by clearing session state."""
    st.session_state.logged_in = False
    st.session_state.user_info = None
    st.rerun()

# --- LOGIN / SIGN UP LANDING PAGE ---
if not st.session_state.logged_in:
    st.markdown('<h1 class="gradient-text" style="text-align: center;">Streamline Your Workforce Management</h1>', unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #d3d3d3;'>Real-time attendance, intelligent leave management, and powerful analytics to unlock your team's full potential.</p>", unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="glassmorphism">', unsafe_allow_html=True)
        choice = st.radio("", ["Get Started Now (Sign Up)", "Login"], horizontal=True, label_visibility="collapsed")

        if choice == "Login":
            with st.form("login_form"):
                username = st.text_input("Username", placeholder="Enter your username").lower()
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                if st.form_submit_button("Login", use_container_width=True):
                    login_user(username, password)
        else:  # Sign Up
            with st.form("signup_form", clear_on_submit=True):
                new_username = st.text_input("Username", placeholder="Choose a username").lower()
                new_full_name = st.text_input("Full Name", placeholder="Enter your full name")
                new_email = st.text_input("Email", placeholder="Enter your email")
                new_password = st.text_input("Password", type="password", placeholder="Create a strong password")
                new_employee_id = st.text_input("Employee ID", placeholder="Enter your unique employee ID")
                if st.form_submit_button("Create Account", use_container_width=True):
                    if not all([new_username, new_full_name, new_email, new_password, new_employee_id]):
                        st.error("Please fill out all fields.")
                    else:
                        hashed_pass = hash_password(new_password)
                        users_col.insert_one({
                            "username": new_username, "full_name": new_full_name, "email": new_email,
                            "password_hash": hashed_pass, "employee_id": new_employee_id,
                            "role": "employee", "join_date": datetime.now()
                        })
                        st.success("Account created! Please switch to the Login tab.")
        st.markdown('</div>', unsafe_allow_html=True)

    st.divider()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric(label="Employees Onboarded", value="50,000+")
    col2.metric(label="Companies Trust Us", value="2,500+")
    col3.metric(label="Attendance Accuracy", value="99.8%")
    col4.metric(label="Productivity Gain", value="35%")

# --- MAIN APPLICATION AFTER LOGIN ---
else:
    user = st.session_state.user_info
    
    # --- NEW: Sidebar Navigation with streamlit-option-menu ---
    with st.sidebar:
        st.title(f"Welcome, {user['username'].capitalize()}!")
        st.write(f"**Role:** {user['role'].capitalize()}")
        st.divider()

        # This is the new, corrected menu. It's clean and directly returns the selected page name.
        page = option_menu(
            menu_title="Main Menu",
            options=["Dashboard", "Attendance", "Leave Management", "My Profile"],
            icons=["kanban", "clock-history", "calendar-check", "person-circle"], # Bootstrap icons
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {"padding": "0!important", "background-color": "transparent"},
                "icon": {"color": "#CFA2FF", "font-size": "1.2rem"},
                "nav-link": {"font-size": "1.1rem", "text-align": "left", "margin":"0px", "--hover-color": "#5f187b"},
                "nav-link-selected": {"background-color": "#8a2be2"},
            }
        )
        
        st.divider()
        st.button("Logout", on_click=logout_user, use_container_width=True)

    # --- DYNAMIC PAGE ROUTING (This logic remains the same) ---
    if page == "Dashboard":
        if user['role'] == 'employee':
            employee_dashboard.show_employee_dashboard()
        elif user['role'] in ['admin', 'hr', 'manager']:
            admin_hr_dashboard.show_admin_hr_dashboard()
    elif page == "Attendance":
        attendance.show_attendance_page()
    elif page == "Leave Management":
        leaves.show_leaves_page()
    elif page == "My Profile":
        profile_page.show_profile_page()