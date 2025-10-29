import streamlit as st
import pandas as pd
from db import leaves_col, users_col
from datetime import datetime, time
from bson.objectid import ObjectId
import requests 
import json     

# --- NEW: Real AI Letter Generation Function (using Ollama) ---
def get_ai_generated_reason(prompt, user_name):
    """
    Calls a local Ollama model to generate a formal leave letter.
    """
    st.toast("🤖 Contacting local AI... please wait.")
    
    ollama_url = "http://localhost:11434/api/generate"
    model_to_use = "llama3" 
    
    full_prompt = f"""
    You are an employee named {user_name}. 
    Write a formal leave letter to your manager based *only* on the following user prompt.
    The letter must be professional, concise, and start with "Dear [Manager Name],"
    
    User's Prompt: "{prompt}"
    
    Your formal letter:
    """

    payload = {
        "model": model_to_use,
        "prompt": full_prompt,
        "stream": False 
    }

    try:
        response = requests.post(ollama_url, json=payload)
        response.raise_for_status() 
        
        response_data = response.json()
        generated_text = response_data.get("response", "")
        
        generated_text = generated_text.strip().strip('"')
        
        st.toast("✅ AI letter generated!", icon="✨")
        return generated_text

    except requests.exceptions.ConnectionError:
        st.error("Connection Failed: Your Ollama server is not running.")
        return f"---ERROR: Could not connect to Ollama at {ollama_url}. Please start your local server.---\n\nUser Prompt: {prompt}"
    except Exception as e:
        st.error(f"Ollama API Error: {e}")
        return f"---ERROR: {e}---\n\nUser Prompt: {prompt}"


# --- (Placeholder) Leave Balance Function ---
def get_leave_balance(employee_id):
    """
    Simulates fetching a user's leave balance.
    """
    balance = {
        "casual": 10,
        "sick": 8,
        "earned": 12
    }
    return balance

# --- Helper Function for Admin Tabs ---
def display_leave_requests(status_to_display):
    """
    Reusable function to display leave requests in the admin tabs.
    """
    requests = list(leaves_col.find({"status": status_to_display}).sort("applied_at", -1))
    
    if not requests:
        st.info(f"No {status_to_display} leave applications found.")
        return

    for leave in requests:
        applicant_user = users_col.find_one({"employee_id": leave['employee_id']})
        applicant_name = applicant_user.get("full_name", "Unknown User") if applicant_user else "Unknown User"
        
        with st.container(border=True):
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown(f"**Applicant:** {applicant_name} (`{leave['employee_id']}`)")
                st.write(f"**Type:** {leave.get('leave_type', 'N/A').capitalize()}")
                st.write(f"**Dates:** {leave['start_date'].strftime('%d-%b-%Y')} ({leave.get('start_day_type')}) to {leave['end_date'].strftime('%d-%b-%Y')} ({leave.get('end_day_type')})")
                st.info(f"**Reason:**\n\n{leave.get('reason', 'N/A')}")

                if leave.get("attachment_filename"):
                    st.success(f"📎 Attached File: {leave['attachment_filename']}")
            
            with col2:
                if status_to_display == "pending":
                    st.write("---") 
                    if st.button("Approve", key=f"approve_{leave['_id']}", width='stretch'):
                        leaves_col.update_one({"_id": ObjectId(leave['_id'])}, {"$set": {"status": "approved"}})
                        st.rerun()
                    if st.button("Reject", key=f"reject_{leave['_id']}", type="primary", width='stretch'):
                        leaves_col.update_one({"_id": ObjectId(leave['_id'])}, {"$set": {"status": "rejected"}})
                        st.rerun()
                else:
                    st.markdown(f"**Status:** {status_to_display.capitalize()}")


# --- Main Page Function ---
def show_leaves_page():
    st.title("🌴 Leave Management")
    user_info = st.session_state.user_info
    user_role = user_info['role']

    if "generated_reason" not in st.session_state:
        st.session_state.generated_reason = ""
    if "ai_prompt_text" not in st.session_state:
        st.session_state.ai_prompt_text = ""

    # --- ADMIN / HR / MANAGER VIEW ---
    if user_role in ['admin', 'hr', 'manager']:
        st.subheader("Review Leave Applications")
        
        tab1, tab2, tab3 = st.tabs(["⏳ Pending", "✅ Approved", "❌ Rejected"])

        with tab1:
            display_leave_requests("pending")
        with tab2:
            display_leave_requests("approved")
        with tab3:
            display_leave_requests("rejected")
    
    # --- EMPLOYEE VIEW ---
    if user_role == 'employee':
        
        # --- 1. Leave Balance ---
        st.subheader("Your Leave Balance")
        balance = get_leave_balance(user_info['employee_id'])
        kpi1, kpi2, kpi3 = st.columns(3)
        kpi1.metric("Casual Leave", f"{balance['casual']} Days")
        kpi2.metric("Sick Leave", f"{balance['sick']} Days")
        kpi3.metric("Earned Leave", f"{balance['earned']} Days")
        st.divider()

        # --- 2. Application Form ---
        st.subheader("Apply for a New Leave")
        
        # --- 3. AI GENERATOR (MOVED OUTSIDE THE FORM) ---
        st.markdown("#### 🤖 AI Letter Generator")
        st.caption("Describe your reason below, and let AI write a formal letter for you.")
        
        ai_prompt = st.text_input(
            "Describe your leave reason (e.g., 'I have a high fever and need 2 days off')", 
            key="ai_prompt_text"
        )
        
        if st.button("✨ Generate AI Reason", width='stretch'):
            if st.session_state.ai_prompt_text:
                st.session_state.generated_reason = get_ai_generated_reason(
                    st.session_state.ai_prompt_text, 
                    user_info.get('full_name', 'Employee')
                )
            else:
                st.warning("Please enter a description for the AI.")
            st.rerun()
        
        st.divider()

        # --- THE FORM STARTS HERE ---
        with st.form("Leave Application Form"):
            leave_type = st.selectbox(
                "Leave. Type", 
                ["Casual", "Sick", "Earned", "Maternity", "Paternity", "Loss of Pay (LOP)"]
            )
            
            c1, c2 = st.columns(2)
            with c1:
                start_date = st.date_input("Start Date", min_value=datetime.today())
                start_day_type = st.selectbox("Start Day", ["Full Day", "First Half", "Second Half"], key="start_day")
            with c2:
                end_date = st.date_input("End Date", min_value=start_date)
                end_day_type = st.selectbox("End Day", ["Full Day", "First Half", "Second Half"], key="end_day")
            
            reason = st.text_area(
                "Reason for Leave (You can edit the AI's generation)", 
                value=st.session_state.generated_reason, 
                height=250
            )
            
            attachment = st.file_uploader("Attach Document (e.g., Doctor's Note)", type=["pdf", "jpg", "png"])
            
            st.divider()
            
            submitted = st.form_submit_button("Submit Application", width='stretch')
            
            if submitted:
                if not reason or "---ERROR:" in reason:
                    st.error("Please provide a valid reason for your leave.")
                elif start_date > end_date:
                    st.error("Error: Start date must be before or the same as the end date.")
                else:
                    file_name = attachment.name if attachment else None
                    
                    leaves_col.insert_one({
                        "employee_id": user_info['employee_id'],
                        "leave_type": leave_type.lower(),
                        "start_date": datetime.combine(start_date, time.min),
                        "end_date": datetime.combine(end_date, time.min),
                        "start_day_type": start_day_type.lower(),
                        "end_day_type": end_day_type.lower(),
                        "reason": reason, 
                        "attachment_filename": file_name,
                        "status": "pending", 
                        "applied_at": datetime.now()
                    })
                    
                    st.session_state.generated_reason = ""
                    # --- THIS IS THE FIX ---
                    # We comment out the line that causes the crash.
                    # st.session_state.ai_prompt_text = "" 
                    # --- END OF FIX ---
                    
                    st.success("Your leave application has been submitted successfully!")
                    st.rerun()

    # --- HISTORY (Visible to all) ---
    st.divider()
    st.subheader("Leave Application History")
    
    query = {}
    if user_role == 'employee':
        query = {"employee_id": user_info['employee_id']}
        
    records = list(leaves_col.find(query).sort("applied_at", -1))
    
    if not records:
        st.info("No leave records found.")
    else:
        df = pd.DataFrame(records)
        df['start_date'] = pd.to_datetime(df['start_date']).dt.strftime('%d-%b-%Y')
        df['end_date'] = pd.to_datetime(df['end_date']).dt.strftime('%d-%b-%Y')
        df['applied_at'] = pd.to_datetime(df['applied_at']).dt.strftime('%d-%b-%Y')
        
        df['status'] = df['status'].str.capitalize()
        df['leave_type'] = df['leave_type'].str.capitalize()
        
        # 1. RENAME the columns in the DataFrame FIRST
        df = df.rename(columns={
            "start_date": "Start Date", 
            "end_date": "End Date",
            "leave_type": "Type", 
            "status": "Status"
        })

        # 2. NOW, build the display_cols list using the NEW names
        if user_role != 'employee':
            def get_username(eid):
                user = users_col.find_one({"employee_id": eid})
                return user.get("full_name", "Unknown") if user else "Unknown"
            
            df['Applicant'] = df['employee_id'].apply(get_username)
            
            if 'attachment_filename' not in df.columns:
                df['attachment_filename'] = pd.NA
            df["Attachment"] = df["attachment_filename"].apply(lambda x: "Yes" if pd.notna(x) else "No")
            
            display_cols = ["Applicant", "Start Date", "End Date", "Type", "Status", "Attachment"]
        else:
            display_cols = ["Start Date", "End Date", "Type", "Status"]

        # 3. Finally, display the DataFrame
        st.dataframe(df[display_cols], use_container_width=True, hide_index=True)