import streamlit as st
import pandas as pd
from db import attendance_col, leaves_col
from modules import communication  # Import the new communication module
from datetime import datetime, date

def show_employee_dashboard():
    """
    Displays a personalized dashboard for the logged-in employee,
    including a summary, messaging, and company info.
    """
    st.title(f"My Dashboard")
    user_info = st.session_state.user_info
    employee_id = user_info['employee_id']

    # --- NEW: Show the latest company-wide announcement ---
    communication.show_announcement_banner()
    st.divider()

    # --- Main Dashboard Sections using Tabs ---
    tab1, tab2, tab3 = st.tabs(["📊 My Summary", "✉️ My Messages", "🗓️ Upcoming Holidays"])

    with tab1:
        st.subheader("Your Performance Snapshot")
        # --- Quick Stats Row ---
        col1, col2 = st.columns(2)
        with col1:
            # Calculate attendance percentage for the current month
            today = date.today()
            start_of_month = today.replace(day=1).strftime('%Y-%m-%d')
            
            present_days = attendance_col.count_documents({
                "employee_id": employee_id,
                "date": {"$gte": start_of_month},
                "status": "present"
            })
            # Use the current day of the month as the number of working days so far
            total_work_days_so_far = today.day 
            attendance_percentage = (present_days / total_work_days_so_far) * 100 if total_work_days_so_far > 0 else 0
            st.metric("This Month's Attendance", f"{attendance_percentage:.1f}%")

        with col2:
            pending_leaves = leaves_col.count_documents({"employee_id": employee_id, "status": "pending"})
            st.metric("Pending Leave Requests", pending_leaves)

        st.divider()

        st.subheader("My Recent Leave Status")
        records = list(leaves_col.find({"employee_id": employee_id}).sort("applied_at", -1).limit(5))
        if not records:
            st.info("You have no recent leave applications.")
        else:
            df = pd.DataFrame(records)
            df['start_date'] = pd.to_datetime(df['start_date']).dt.strftime('%d-%b-%Y')
            df['end_date'] = pd.to_datetime(df['end_date']).dt.strftime('%d-%b-%Y')
            st.dataframe(df[['start_date', 'leave_type', 'status']], use_container_width=True, hide_index=True)
        
        st.info("To apply for a new leave or view your full history, please use the 'Leave Management' page in the sidebar. 🌴")

    with tab2:
        # --- NEW: Employee Chat Panel ---
        communication.show_employee_communication_panel()

    with tab3:
        st.subheader("Upcoming Company Holidays")
        # In a real application, this data would come from the database
        holidays = {
            "Diwali": "2025-11-01",
            "Christmas Day": "2025-12-25",
            "New Year's Day": "2026-01-01",
            "Republic Day": "2026-01-26"
        }
        for holiday, hdate in holidays.items():
            st.markdown(f"- **{holiday}**: {datetime.strptime(hdate, '%Y-%m-%d').strftime('%A, %d %B %Y')}")
        
        st.divider()
        st.subheader("Company Documents")
        st.info("This section is a placeholder for accessing your documents.")
        st.button("View Company Policy PDF", use_container_width=True)