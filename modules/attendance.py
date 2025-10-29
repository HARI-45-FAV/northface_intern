import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px  # <-- Added this import
from db import attendance_col, users_col
from datetime import datetime, timedelta
import calendar

# --- HELPER 1: PERSONAL HEATMAP ---
def create_personal_heatmap(employee_id):
    """Creates a Plotly calendar heatmap for a single employee."""
    start_date = datetime.now() - timedelta(days=180)
    attendance_data = list(attendance_col.find(
        {"employee_id": employee_id, "punch_in": {"$gte": start_date}},
        {"date": 1, "status": 1, "worked_hours": 1}
    ))
    
    if not attendance_data:
        return None 

    df = pd.DataFrame(attendance_data)

    if 'worked_hours' not in df.columns: df['worked_hours'] = 0
    if 'status' not in df.columns: df['status'] = 'unknown'
    if 'date' not in df.columns: df['date'] = pd.NaT
    
    df['date'] = pd.to_datetime(df['date']).dt.normalize()
    df['day_str'] = df['date'].dt.strftime('%Y-%m-%d')
    df['worked_hours'] = pd.to_numeric(df['worked_hours'], errors='coerce').fillna(0)
    
    all_days = pd.date_range(start=start_date.date(), end=datetime.now().date(), freq='D').normalize()
    calendar_df = pd.DataFrame(all_days, columns=['date'])
    
    calendar_df = calendar_df.merge(df, on='date', how='left')
    calendar_df['status'] = calendar_df['status'].fillna('absent')
    calendar_df['worked_hours'] = calendar_df['worked_hours'].fillna(0)
    
    def map_status_to_value(row):
        if row['status'] == 'present':
            return 0.1 + (row['worked_hours'] / 8.0) 
        elif row['status'] == 'absent':
            if row['date'].weekday() >= 5: 
                return -0.5
            return 0 
        return 0.05 

    calendar_df['color_value'] = calendar_df.apply(map_status_to_value, axis=1)
    
    dates = calendar_df['date']
    counts = calendar_df['color_value']
    
    fig = go.Figure(go.Heatmap(
        z=counts,
        x=dates,
        y=[''] * len(dates), 
        colorscale=[
            [0, 'rgb(230, 75, 75)'],  # Absent
            [0.01, 'rgb(240, 240, 240)'], # Weekend
            [0.05, 'rgb(255, 224, 130)'], # Leave/Other
            [0.1, 'rgb(173, 230, 173)'],  # Present
            [1, 'rgb(0, 100, 0)'],     # Full Day
        ],
        customdata=calendar_df[['status', 'worked_hours']],
        hovertemplate="<b>%{x|%A, %b %d}</b><br>Status: %{customdata[0]}<br>Hours: %{customdata[1]:.1f}<extra></extra>",
        showscale=False
    ))
    
    fig.update_layout(
        title="Attendance (Last 180 Days)",
        xaxis=dict(tickformat='%b %Y', dtick="M1"),
        yaxis=dict(showticklabels=False),
        height=150,
        margin=dict(l=0,r=0,t=40,b=10)
    )
    return fig

# --- NEW HELPER 2: WEEKLY HOURS BAR CHART ---
def create_weekly_hours_chart(employee_id):
    """Creates a bar chart of weekly worked hours for the last 60 days."""
    start_date = datetime.now() - timedelta(days=60)
    records = list(attendance_col.find(
        {"employee_id": employee_id, "date": {"$gte": start_date.strftime("%Y-%m-%d")}},
        {"date": 1, "worked_hours": 1}
    ))
    
    if not records:
        return None
        
    df = pd.DataFrame(records)
    if 'worked_hours' not in df.columns:
        df['worked_hours'] = 0
        
    df['date'] = pd.to_datetime(df['date'])
    df['worked_hours'] = pd.to_numeric(df['worked_hours'], errors='coerce').fillna(0)
    
    df.set_index('date', inplace=True)
    
    # Resample by week (W), summing the hours
    weekly_hours = df['worked_hours'].resample('W').sum().reset_index()
    weekly_hours['Week'] = weekly_hours['date'].dt.strftime('Week of %b %d')
    
    fig = px.bar(
        weekly_hours, 
        x='Week', 
        y='worked_hours', 
        title='Weekly Worked Hours (Last 60 Days)',
        text='worked_hours'
    )
    fig.update_traces(texttemplate='%{text:.1f}h', textposition='outside')
    fig.update_layout(
        yaxis_title='Total Hours', 
        xaxis_title=None,
        height=300,
        margin=dict(l=0,r=0,t=40,b=10)
    )
    return fig

# --- NEW HELPER 3: STATUS PIE CHART ---
def create_status_pie_chart(employee_id):
    """Creates a pie chart of attendance status for the last 30 days."""
    start_date = datetime.now() - timedelta(days=30)
    records = list(attendance_col.find(
        {"employee_id": employee_id, "date": {"$gte": start_date.strftime("%Y-%m-%d")}},
        {"status": 1}
    ))
    
    if not records:
        return None
        
    df = pd.DataFrame(records)
    if 'status' not in df.columns:
        df['status'] = 'unknown'
        
    status_counts = df['status'].value_counts().reset_index()
    status_counts.columns = ['status', 'count']
    
    fig = px.pie(
        status_counts, 
        names='status', 
        values='count', 
        title='Status (Last 30 Days)',
        hole=0.3
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(
        height=300,
        margin=dict(l=0,r=0,t=40,b=10),
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
    )
    return fig

# --- NEW: Reusable Dashboard Function ---
def show_employee_attendance_dashboard(employee_id, employee_name):
    """
    Displays the complete visual dashboard for a given employee.
    """
    st.header(f"📊 Dashboard for {employee_name}")
    
    # --- PERSONAL KPIS ---
    start_30_days = datetime.now() - timedelta(days=30)
    my_records = list(attendance_col.find({
        "employee_id": employee_id,
        "date": {"$gte": start_30_days.strftime("%Y-%m-%d")}
    }))
    
    avg_hours = 0
    present_days = 0
    on_time_days = 0

    if my_records:
        df_30 = pd.DataFrame(my_records)

        if 'worked_hours' not in df_30.columns: df_30['worked_hours'] = 0
        if 'status' not in df_30.columns: df_30['status'] = None
        if 'punch_in' not in df_30.columns: df_30['punch_in'] = pd.NaT

        df_30['worked_hours'] = pd.to_numeric(df_30['worked_hours'], errors='coerce').fillna(0)
        
        present_df = df_30[df_30['status'] == 'present']
        present_days = len(present_df)
        
        if not present_df.empty:
            worked_days_df = present_df[present_df['worked_hours'] > 0]
            if not worked_days_df.empty:
                avg_hours = worked_days_df['worked_hours'].mean()
            
            present_df['punch_in_time'] = pd.to_datetime(present_df['punch_in'], errors='coerce').dt.time
            on_time_days = len(present_df[present_df['punch_in_time'] <= pd.to_datetime('09:30:00').time()])

    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Avg. Work Hours", f"{avg_hours:.1f} hrs")
    kpi2.metric("Total Days Present", f"{present_days} days")
    kpi3.metric("On-Time Punches", f"{on_time_days} days")

    # --- PERSONAL HEATMAP ---
    personal_heatmap = create_personal_heatmap(employee_id)
    if personal_heatmap:
        st.plotly_chart(personal_heatmap, use_container_width=True)

    st.divider()

    # --- NEW CHARTS ---
    st.subheader("Trends & Snapshot")
    col1, col2 = st.columns(2)
    with col1:
        pie_chart = create_status_pie_chart(employee_id)
        if pie_chart:
            st.plotly_chart(pie_chart, use_container_width=True)
        else:
            st.info("Not enough data for a status pie chart.")
            
    with col2:
        bar_chart = create_weekly_hours_chart(employee_id)
        if bar_chart:
            st.plotly_chart(bar_chart, use_container_width=True)
        else:
            st.info("Not enough data for a weekly hours chart.")


# --- MAIN PAGE FUNCTION ---
def show_attendance_page():
    st.title("🕒 Attendance Portal")
    user_info = st.session_state.user_info
    user_role = user_info["role"]

    # --- PUNCH-IN/OUT (Only for employees) ---
    if user_role == "employee":
        employee_id = user_info["employee_id"]
        today_str = datetime.today().strftime("%Y-%m-%d")
        today_record = attendance_col.find_one({"employee_id": employee_id, "date": today_str})

        st.write(f"📅 Today: **{datetime.today().strftime('%A, %d %B %Y')}**")
        col1, col2 = st.columns(2)

        with col1:
            if not today_record:
                if st.button("✅ Punch In", width='stretch'): 
                    attendance_col.insert_one({
                        "employee_id": employee_id, "date": today_str,
                        "punch_in": datetime.now(), "status": "present"
                    })
                    st.success("Punched in successfully!")
                    st.rerun()
            else:
                punch_in_time = today_record.get("punch_in")
                if isinstance(punch_in_time, datetime):
                    st.info(f"🟢 Punched in at **{punch_in_time.strftime('%H:%M:%S')}**")
                else:
                    st.info("🟢 Punched in (time unavailable)")

        with col2:
            if today_record and "punch_out" not in today_record:
                if st.button("🕔 Punch Out", width='stretch'): 
                    punch_out_time = datetime.now()
                    punch_in_time = today_record.get("punch_in")
                    worked_hours = None
                    if isinstance(punch_in_time, datetime):
                        worked_duration = punch_out_time - punch_in_time
                        worked_hours = round(worked_duration.total_seconds() / 3600, 2)
                    
                    attendance_col.update_one(
                        {"_id": today_record["_id"]},
                        {"$set": {"punch_out": punch_out_time, "worked_hours": worked_hours}}
                    )
                    st.success(f"Punched out successfully! ⏱ Worked {worked_hours} hrs today.")
                    st.rerun()
            elif today_record and "punch_out" in today_record:
                punch_out_time = today_record.get("punch_out")
                if isinstance(punch_out_time, datetime):
                    st.success(f"🔴 Punched out at **{punch_out_time.strftime('%H:%M:%S')}**")
                else:
                    st.success("🔴 Punched out (time unavailable)")

        if today_record and "punch_out" not in today_record:
            punch_in_time = today_record.get("punch_in")
            if isinstance(punch_in_time, datetime):
                elapsed = datetime.now() - punch_in_time
                # --- BUG FIX WAS HERE (divod -> divmod) ---
                hours, remainder = divmod(int(elapsed.total_seconds()), 3600)
                minutes, _ = divmod(remainder, 60)
                st.info(f"🧭 You’ve been working for **{hours}h {minutes}m**")

        st.divider()

    # --- ATTENDANCE DASHBOARD & HISTORY (Visible to all) ---
    
    selected_employee_id = user_info["employee_id"]
    selected_full_name = user_info.get("full_name", "Employee")

    if user_role in ["admin", "hr", "manager"]:
        st.subheader("Select Employee to View")
        employee_list = list(users_col.find({}, {"employee_id": 1, "username": 1, "full_name": 1}))
        if not employee_list:
            st.error("No employee data found.")
            return
            
        employee_map = {f"{emp.get('full_name', 'N/A')} ({emp.get('username', 'N/A')})": emp.get("employee_id") for emp in employee_list}
        
        current_user_key = f"{user_info.get('full_name', 'N/A')} ({user_info.get('username', 'N/A')})"
        options = list(employee_map.keys())
        index = 0
        if current_user_key in options:
            index = options.index(current_user_key)

        selected_user_display = st.selectbox(
            "Select Employee", 
            options=options,
            index=index
        )
        selected_employee_id = employee_map.get(selected_user_display)
        selected_full_name = selected_user_display.split(' (')[0] # Get the name part
        
        if not selected_employee_id:
            st.warning("Could not find employee. Defaulting to your records.")
            selected_employee_id = user_info["employee_id"]
            selected_full_name = user_info.get("full_name", "Employee")
    
    # --- NEW: Call the reusable dashboard function ---
    show_employee_attendance_dashboard(selected_employee_id, selected_full_name)

    st.divider()

    # --- Detailed History Table (Visible to all) ---
    st.subheader("📋 Detailed History Table")
    records = list(attendance_col.find({"employee_id": selected_employee_id}).sort("date", -1))

    if not records:
        st.info("No attendance records found.")
        return

    df = pd.DataFrame(records)

    required_cols = ["date", "punch_in", "punch_out", "worked_hours", "status"]
    for col in required_cols:
        if col not in df.columns:
            df[col] = pd.NaT if col in ["punch_in", "punch_out"] else None

    def fmt_time(value):
        if pd.isna(value):
            return "N/A"
        if isinstance(value, datetime):
            return value.strftime("%H:%M:%S")
        return "N/A"

    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.strftime("%d-%b-%Y")
    df["punch_in"] = pd.to_datetime(df["punch_in"], errors='coerce').apply(fmt_time)
    df["punch_out"] = pd.to_datetime(df["punch_out"], errors='coerce').apply(fmt_time)
    df["worked_hours"] = pd.to_numeric(df["worked_hours"], errors='coerce').fillna(0).round(2)
    df["status"] = df["status"].fillna("N/A").str.capitalize()

    display_df = df[["date", "status", "punch_in", "punch_out", "worked_hours"]]
    st.dataframe(display_df, use_container_width=True, hide_index=True)