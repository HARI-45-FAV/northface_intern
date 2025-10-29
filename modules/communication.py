import streamlit as st
from db import announcements_col, chats_col, users_col
from datetime import datetime

# -------------------------------
# 🔹 COMPANY ANNOUNCEMENT SECTION
# -------------------------------

def show_announcement_banner():
    """Finds the latest active announcement and displays it as a banner."""
    latest_announcement = announcements_col.find_one(
        {"is_active": True},
        sort=[("posted_at", -1)]
    )
    if latest_announcement:
        st.info(f"**📢 Announcement:** {latest_announcement['message']}")


# -------------------------------
# 🔹 HR COMMUNICATION PANEL
# -------------------------------

def show_hr_communication_panel():
    """HR dashboard: Chat with employees + Post announcements."""
    try:
        hr_user = st.session_state.user_info
        
        # ✅ Validate HR user data
        if not hr_user or 'employee_id' not in hr_user:
            st.error("HR user information is invalid. Please log in again.")
            return
        
        hr_id = hr_user['employee_id']

        tab1, tab2 = st.tabs(["💬 Chat with Employees", "📢 Post an Announcement"])

        # --- Tab 1: HR ↔ Employee Chat ---
        with tab1:
            st.subheader("Chat with Employees")
            all_employees = list(users_col.find({"role": "employee"}, {"full_name": 1, "employee_id": 1}))

            if not all_employees:
                st.warning("No employees found in the database.")
                return

            employee_map = {emp['full_name']: emp['employee_id'] for emp in all_employees}
            selected_name = st.selectbox("Select an employee to chat with", options=list(employee_map.keys()))

            if selected_name:
                selected_emp_id = employee_map[selected_name]

                # ✅ Create sorted participant list for consistent querying
                participants = sorted([hr_id, selected_emp_id])

                # ✅ Fetch existing chat - using _id lookup to avoid participants field issues
                chat_thread = chats_col.find_one({
                    "$and": [
                        {"participants": hr_id},
                        {"participants": selected_emp_id}
                    ]
                })

                # Display chat history
                if chat_thread and "messages" in chat_thread:
                    for msg in chat_thread["messages"]:
                        sender_name = "You" if msg["sender_id"] == hr_id else selected_name
                        st.chat_message("user" if sender_name != "You" else "assistant").write(
                            f"**{sender_name}:** {msg['message']}"
                        )

                # Send a new message
                new_message = st.text_input("Your message:", key=f"chat_{selected_emp_id}")
                if st.button("Send", key=f"send_{selected_emp_id}"):
                    if new_message.strip():
                        message_doc = {
                            "sender_id": hr_id,
                            "message": new_message.strip(),
                            "timestamp": datetime.now()
                        }

                        # ✅ If chat exists, only push message using _id
                        if chat_thread:
                            chats_col.update_one(
                                {"_id": chat_thread["_id"]},
                                {"$push": {"messages": message_doc}}
                            )
                        else:
                            # Create new chat with sorted participants
                            chats_col.insert_one({
                                "participants": participants,
                                "messages": [message_doc],
                                "created_at": datetime.now()
                            })

                        st.success("Message sent!")
                        st.rerun()

        # --- Tab 2: Company Announcements ---
        with tab2:
            st.subheader("Company-Wide Announcements")

            with st.form("announcement_form", clear_on_submit=True):
                message = st.text_area("Enter your announcement here:")
                submitted = st.form_submit_button("Post Announcement")

                if submitted and message.strip():
                    # Deactivate previous announcements
                    announcements_col.update_many({"is_active": True}, {"$set": {"is_active": False}})

                    # Insert new announcement
                    announcements_col.insert_one({
                        "posted_by": hr_id,
                        "posted_at": datetime.now(),
                        "message": message.strip(),
                        "is_active": True
                    })
                    st.success("✅ Announcement posted successfully!")
    
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.error("There may be corrupted data in the database. Please run the diagnostic script.")
        if st.button("Clear corrupted chats"):
            # Emergency cleanup
            chats_col.delete_many({
                "$or": [
                    {"participants": {"$exists": False}},
                    {"participants": None},
                    {"participants": {"$not": {"$type": "array"}}},
                ]
            })
            st.success("Cleanup attempted. Please refresh the page.")


# -------------------------------
# 🔹 EMPLOYEE COMMUNICATION PANEL
# -------------------------------

def show_employee_communication_panel():
    """Employee dashboard: Chat with HR."""
    try:
        employee_user = st.session_state.user_info
        
        # ✅ Validate employee user data
        if not employee_user or 'employee_id' not in employee_user:
            st.error("Employee user information is invalid. Please log in again.")
            return
        
        emp_id = employee_user['employee_id']
        
        st.subheader("✉️ Messages with HR")

        hr_user = users_col.find_one({"role": "hr"})
        if not hr_user:
            st.error("No HR user found in the system.")
            return

        hr_id = hr_user['employee_id']
        
        # ✅ Create sorted participant list
        participants = sorted([hr_id, emp_id])

        # ✅ Fetch existing chat using $and to avoid conflicts
        chat_thread = chats_col.find_one({
            "$and": [
                {"participants": hr_id},
                {"participants": emp_id}
            ]
        })

        if chat_thread and "messages" in chat_thread:
            for msg in chat_thread["messages"]:
                sender_name = "You" if msg["sender_id"] == emp_id else "HR"
                st.chat_message("user" if sender_name != "You" else "assistant").write(
                    f"**{sender_name}:** {msg['message']}"
                )
        else:
            st.info("You have no messages yet. Send a message to start a conversation with HR.")

        # New message input
        new_message = st.text_input("Your message to HR:")
        if st.button("Send", key="send_to_hr"):
            if new_message.strip():
                message_doc = {
                    "sender_id": emp_id,
                    "message": new_message.strip(),
                    "timestamp": datetime.now()
                }

                # ✅ If chat exists, only push message using _id
                if chat_thread:
                    chats_col.update_one(
                        {"_id": chat_thread["_id"]},
                        {"$push": {"messages": message_doc}}
                    )
                else:
                    # Create new chat with sorted participants
                    chats_col.insert_one({
                        "participants": participants,
                        "messages": [message_doc],
                        "created_at": datetime.now()
                    })

                st.success("Message sent!")
                st.rerun()
    
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.error("There may be corrupted data in the database. Please run the diagnostic script.")