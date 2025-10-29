import streamlit as st
from db import users_col
import base64

def show_profile_page():
    st.title("User Profile")
    current_user = st.session_state.user_info

    # --- Employee Selection for Admins/HR ---
    if current_user['role'] in ['admin', 'hr']:
        employee_list = list(users_col.find({}, {"username": 1}))
        employee_usernames = [emp['username'] for emp in employee_list]
        selected_username = st.selectbox("Select Employee to View Profile", options=employee_usernames,
                                           index=employee_usernames.index(current_user['username']))
        profile_data = users_col.find_one({"username": selected_username})
    else:
        profile_data = users_col.find_one({"employee_id": current_user['employee_id']})

    if not profile_data:
        st.error("Profile not found.")
        return

    # --- Display Profile Information (Using .get() for safety) ---
    col1, col2 = st.columns([1, 2])
    with col1:
        # Provide a default placeholder image if profile_pic_url is missing
        default_image = "https://placehold.co/400x400/cccccc/FFFFFF/png?text=No+Image"
        st.image(profile_data.get("profile_pic_url", default_image), width=200)

    with col2:
        st.subheader(profile_data.get("full_name", "N/A"))
        st.write(f"**Job Title:** {profile_data.get('job_title', 'N/A')}")
        st.write(f"**Department:** {profile_data.get('department', 'N/A')}")
        st.write(f"**Employee ID:** {profile_data.get('employee_id', 'N/A')}")
        st.write(f"**Email:** {profile_data.get('email', 'N/A')}")
        st.write(f"**Contact:** {profile_data.get('contact_number', 'N/A')}")

    st.divider()

    # --- Edit Profile (Visible to Admin/HR and user themselves) ---
    is_own_profile = (current_user['employee_id'] == profile_data.get('employee_id'))
    if current_user['role'] in ['admin', 'hr'] or is_own_profile:
        with st.expander("📝 Edit Profile Information"):
            with st.form("edit_profile_form"):
                new_full_name = st.text_input("Full Name", value=profile_data.get("full_name", ""))
                new_job_title = st.text_input("Job Title", value=profile_data.get("job_title", ""))
                new_department = st.text_input("Department", value=profile_data.get("department", ""))
                new_contact = st.text_input("Contact Number", value=profile_data.get("contact_number", ""))
                new_email = st.text_input("Email Address", value=profile_data.get("email", ""))

                # --- Image Upload for Admin/HR ---
                if current_user['role'] in ['admin', 'hr']:
                    uploaded_image = st.file_uploader("Upload new profile picture", type=["png", "jpg", "jpeg"])

                submitted = st.form_submit_button("Update Information")
                if submitted:
                    update_data = {
                        "full_name": new_full_name, "job_title": new_job_title,
                        "department": new_department, "contact_number": new_contact,
                        "email": new_email
                    }
                    if 'uploaded_image' in locals() and uploaded_image is not None:
                        encoded_image = base64.b64encode(uploaded_image.getvalue()).decode('utf-8')
                        update_data["profile_pic_url"] = f"data:image/png;base64,{encoded_image}"

                    users_col.update_one({"_id": profile_data['_id']}, {"$set": update_data})
                    st.success("Profile updated successfully!")
                    st.rerun()