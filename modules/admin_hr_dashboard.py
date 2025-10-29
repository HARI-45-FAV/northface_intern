import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from db import users_col, leaves_col, attendance_col
from modules import communication
from auth import hash_password
from datetime import datetime, timedelta
from bson.objectid import ObjectId
import calendar

# --- Helper Function for Calendar Heatmap ---
def get_attendance_heatmap_data():
    """Aggregates attendance data for a calendar heatmap."""
    start_date = datetime.now() - timedelta(days=180)
    attendance_data = list(attendance_col.find(
        {"punch_in": {"$gte": start_date}, "status": "present"},
        {"date": 1}
    ))
    
    if not attendance_data:
        return pd.DataFrame(columns=['date', 'count'])

    df = pd.DataFrame(attendance_data)
    df['date'] = pd.to_datetime(df['date']).dt.normalize()
    daily_counts = df.groupby(df['date']).size().reset_index(name='count')
    return daily_counts

def create_calendar_heatmap(df):
    """Creates a Plotly calendar heatmap."""
    if df.empty:
        return go.Figure()

    start_date = df['date'].min()
    end_date = df['date'].max()
    all_days = pd.date_range(start=start_date, end=end_date, freq='D').normalize()
    
    calendar_df = pd.DataFrame(all_days, columns=['date'])
    calendar_df = calendar_df.merge(df, on='date', how='left').fillna(0)
    
    dates = calendar_df['date']
    counts = calendar_df['count']
    
    fig = go.Figure(go.Heatmap(
        z=counts,
        x=dates,
        y=[''] * len(dates), # Single row
        colorscale='Greens',
        hovertext=[f"{d.strftime('%A, %b %d')}: {c} Present" for d, c in zip(dates, counts)],
        hoverinfo='text',
        showscale=True,
        colorbar=dict(title='Present')
    ))
    
    fig.update_layout(
        title="Company Attendance Heatmap (Last 6 Months)",
        xaxis=dict(title='Date', tickformat='%b %Y', dtick="M1"),
        yaxis=dict(showticklabels=False),
        height=150,
        margin=dict(l=0,r=0,t=40,b=10)
    )
    return fig

# --- Main Dashboard Function ---
def show_admin_hr_dashboard():
    st.markdown('## 🧭 Management Dashboard', unsafe_allow_html=True)
    user_info = st.session_state.user_info

    communication.show_announcement_banner()
    st.divider()

    if user_info['role'] == 'admin':
        tab1, tab2, tab3 = st.tabs(["👥 User Management", "📈 Analytics", "⚙️ System Logs"])
    else:
        tab1, tab2, tab3 = st.tabs(["🌟 Employee Hub", "📈 Analytics", "✉️ Communication"])

    # --- TAB 1: User Management / Employee Overview ---
    with tab1:
        if user_info['role'] == 'admin':
            st.subheader("Create & Manage Employee Accounts")
            with st.expander("➕ Add New Employee"):
                with st.form("new_employee_form", clear_on_submit=True):
                    col1, col2 = st.columns(2)
                    with col1:
                        full_name = st.text_input("Full Name")
                        username = st.text_input("Username").lower()
                        temp_password = st.text_input("Temporary Password", type="password")
                        role = st.selectbox("Role", ["employee", "manager", "hr"])
                    with col2:
                        email = st.text_input("Email")
                        employee_id = st.text_input("Employee ID (unique)")
                        department = st.text_input("Department")
                        job_title = st.text_input("Job Title")
                    submitted = st.form_submit_button("Create Account", width='stretch') # Updated
                    if submitted:
                        if not all([full_name, username, temp_password, role, email, employee_id, department, job_title]):
                            st.error("Please fill out all fields.")
                        elif users_col.find_one({"username": username}):
                            st.error(f"Username '{username}' already exists.")
                        elif users_col.find_one({"employee_id": employee_id}):
                            st.error(f"Employee ID '{employee_id}' already exists.")
                        else:
                            hashed_pass = hash_password(temp_password)
                            users_col.insert_one({
                                "username": username, "full_name": full_name, "email": email,
                                "password_hash": hashed_pass, "employee_id": employee_id, "role": role,
                                "department": department, "job_title": job_title, "join_date": datetime.now(),
                                "profile_pic_url": "https://placehold.co/400x400/cccccc/FFFFFF/png?text=New"
                            })
                            st.success(f"✅ Account for {full_name} created!")
                            st.balloons()
            
            st.divider()
            st.subheader("Existing Employees")
            all_users_admin = list(users_col.find({}))
            for user in all_users_admin:
                with st.container(border=True):
                    col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
                    col1.write(f"**{user.get('full_name', 'N/A')}** (`{user.get('username', 'N/A')}`)")
                    col2.write(f"Role: **{user.get('role', 'N/A').capitalize()}**")
                    options = ["employee", "manager", "hr", "admin"]
                    index = options.index(user.get('role', 'employee')) if user.get('role', 'employee') in options else 0
                    new_role = col3.selectbox(
                        "Change Role", options=options, index=index,
                        key=f"role_{user['_id']}", label_visibility="collapsed"
                    )
                    if new_role != user.get('role'):
                        users_col.update_one({"_id": user['_id']}, {"$set": {"role": new_role}})
                        st.toast(f"Updated {user['full_name']}'s role to {new_role.capitalize()}")
                        st.rerun()
                    if col4.button("🗑️ Delete", key=f"del_{user['_id']}", type="primary"):
                        if user['employee_id'] == user_info['employee_id']:
                            st.error("Cannot delete your own account.")
                        else:
                            users_col.delete_one({"_id": user['_id']})
                            st.toast(f"Deleted {user['full_name']}")
                            st.rerun()

        elif user_info['role'] == 'hr':
            st.subheader("🌟 Employee Hub")
            st.markdown("A quick-glance overview of key employee metrics.")
            
            all_users = list(users_col.find({"role": {"$ne": "admin"}}).sort("full_name", 1))
            
            departments = ["All"] + sorted(list(users_col.distinct("department")))
            selected_dept = st.selectbox("Filter by Department", options=departments)
            
            if selected_dept != "All":
                all_users = [user for user in all_users if user.get("department") == selected_dept]
                
            for user in all_users:
                with st.container(border=True):
                    emp_id = user.get("employee_id")
                    if not emp_id: continue
                    
                    col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
                    
                    with col1:
                        st.markdown(f"**{user.get('full_name', 'N/A')}**")
                        st.caption(f"{user.get('job_title', 'N/A')} | `{user.get('department', 'N/A')}`")
                        st.write(f"ID: `{emp_id}`")
                    
                    att_records = list(attendance_col.find({"employee_id": emp_id}))
                    total_days = len(att_records)
                    present_days = len([r for r in att_records if r.get("status") == "present"])
                    attendance_pct = (present_days / total_days * 100) if total_days > 0 else 0
                    
                    worked_hours = 0
                    for r in att_records:
                        if isinstance(r.get("worked_hours"), (int, float)):
                            worked_hours += r.get("worked_hours", 0)
                    avg_hours = (worked_hours / present_days) if present_days > 0 else 0
                    
                    total_leave = leaves_col.count_documents({"employee_id": emp_id, "status": "approved"})

                    with col2:
                        st.metric("Attendance", f"{attendance_pct:.1f}%")
                    with col3:
                        st.metric("Avg. Hours", f"{avg_hours:.1f} hrs")
                    with col4:
                        st.metric("Total Leave", f"{total_leave} days")


    # --- TAB 2: Analytics ---
    with tab2:
        st.subheader("📊 Company Analytics")

        total_employees = users_col.count_documents({})
        pending_leaves = leaves_col.count_documents({"status": "pending"})
        
        all_attendance = list(attendance_col.find({}, {"status": 1}))
        avg_attendance_pct = 0
        if all_attendance:
            df_att = pd.DataFrame(all_attendance)
            total_records = len(df_att)
            present_records = len(df_att[df_att['status'] == 'present'])
            avg_attendance_pct = (present_records / total_records * 100) if total_records > 0 else 0

        kpi1, kpi2, kpi3 = st.columns(3)
        kpi1.metric("Total Employees", total_employees)
        kpi2.metric("Pending Leave Requests", pending_leaves, delta_color="inverse")
        kpi3.metric("Avg. Company Attendance", f"{avg_attendance_pct:.1f}%")

        st.divider()
        
        chart_col1, chart_col2 = st.columns(2)
        with chart_col1:
            st.markdown("#### Employees by Department")
            dept_data = list(users_col.aggregate([{"$group": {"_id": "$department", "count": {"$sum": 1}}}]))
            if dept_data:
                df_dept = pd.DataFrame(dept_data).rename(columns={'_id': 'Department', 'count': 'Employees'})
                fig_bar = px.bar(df_dept, x='Department', y='Employees', text_auto=True)
                fig_bar.update_layout(margin=dict(l=0,r=0,t=0,b=0))
                st.plotly_chart(fig_bar, use_container_width=True)

            st.markdown("#### Leave Type Distribution")
            leave_data = list(leaves_col.aggregate([
                {"$match": {"status": "approved"}},
                {"$group": {"_id": "$leave_type", "count": {"$sum": 1}}}
            ]))
            if leave_data:
                df_leave_pie = pd.DataFrame(leave_data).rename(columns={'_id': 'Leave Type', 'count': 'Count'})
                fig_pie = px.pie(df_leave_pie, names='Leave Type', values='Count', hole=0.3)
                fig_pie.update_layout(margin=dict(l=0,r=0,t=0,b=0))
                st.plotly_chart(fig_pie, use_container_width=True)

        with chart_col2:
            st.markdown("#### Attendance % vs. Approved Leave")
            all_users = list(users_col.find({}))
            perf_data = []
            for user in all_users:
                emp_id = user.get("employee_id")
                if not emp_id: continue
                
                att_records = list(attendance_col.find({"employee_id": emp_id}))
                total_days = len(att_records)
                present_days = len([r for r in att_records if r.get("status") == "present"])
                attendance_pct = (present_days / total_days * 100) if total_days > 0 else 0
                total_leave = leaves_col.count_documents({"employee_id": emp_id, "status": "approved"})
                
                perf_data.append({
                    "Employee": user.get('full_name', 'N/A'),
                    "Department": user.get('department', 'N/A'),
                    "Attendance %": attendance_pct,
                    "Total Leave Days": total_leave
                })
                
            if perf_data:
                df_perf = pd.DataFrame(perf_data)
                fig_scatter = px.scatter(
                    df_perf, x="Attendance %", y="Total Leave Days",
                    color="Department", hover_name="Employee",
                    title="Attendance vs. Leave (Hover for Details)"
                )
                fig_scatter.update_layout(margin=dict(l=0,r=0,t=40,b=0))
                st.plotly_chart(fig_scatter, use_container_width=True)
            else:
                st.info("Not enough data for performance scatter plot.")

        st.divider()
        heatmap_data = get_attendance_heatmap_data()
        if not heatmap_data.empty:
            st.plotly_chart(create_calendar_heatmap(heatmap_data), use_container_width=True)
        else:
            st.info("Not enough attendance data for a heatmap.")

    # --- TAB 3: Communication / System Logs ---
    with tab3:
        if user_info['role'] == 'hr':
            communication.show_hr_communication_panel()
        elif user_info['role'] == 'admin':
            st.subheader("⚙️ System & Audit Logs")
            st.warning("Feature under development. This is a placeholder.")
            if st.button("Force Database Backup (Placeholder)", width='stretch'): # Updated
                st.toast("Backup initiated...")
            if st.button("View Recent System Logs (Placeholder)", width='stretch'): # Updated
                st.info("Showing last 5 system events (placeholder):")
                st.json({
                    "events": [
                        {"timestamp": "2025-10-15 10:00", "user": "admin", "action": "Changed user roles."},
                        {"timestamp": "2025-10-14 18:00", "user": "admin", "action": "Deleted inactive accounts."},
                        {"timestamp": "2025-10-13 09:00", "user": "hr", "action": "Published company announcement."}
                    ]
                })