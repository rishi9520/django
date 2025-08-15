# --- START OF FILE schedule_manager.py ---

import streamlit as st
import pandas as pd
from datetime import datetime, date
import mysql.connector


def render_schedule_manager_page(school_id, data_manager_module):
    """
    Render the schedule management page, fetching data from the database.
    """
    data_manager_instance = st.session_state.data_manager

    # Check if DataManager instance is available
    if data_manager_instance is None:
        st.error("DataManager instance not available. Please report this issue.")
        return

    st.markdown(
        """<div style="margin-right: 5px;color:#1e3a8a;"class="card-title ">
            <h1><svg xmlns="http://www.w3.org/2000/svg" width="35" height="35" fill="currentColor" viewBox="0 0 16 16" style="margin-right: 5px;color:#1e3a8a;">
                <path d="M11 6.5a.5.5 0 0 1 .5-.5h1a.5.5 0 0 1 .5.5v1a.5.5 0 0 1-.5.5h-1a.5.5 0 0 1-.5-.5v-1zm-3 0a.5.5 0 0 1 .5-.5h1a.5.5 0 0 1 .5.5v1a.5.5 0 0 1-.5.5h-1a.5.5 0 0 1-.5-.5v-1zm-5 3a.5.5 0 0 1 .5-.5h1a.5.5 0 0 1 .5.5v1a.5.5 0 0 1-.5.5h-1a.5.5 0 0 1-.5-.5v-1zm3 0a.5.5 0 0 1 .5-.5h1a.5.5 0 0 1 .5.5v1a.5.5 0 0 1-.5.5h-1a.5.5 0 0 1-.5-.5v-1z"/>
                <path d="M3.5 0a.5.5 0 0 1 .5.5V1h8V.5a.5.5 0 0 1 1 0V1h1a2 2 0 0 1 2 2v11a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V3a2 2 0 0 1 2-2h1V.5a.5.5 0 0 1 .5-.5zM1 4v10a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V4H1z"/>
            </svg>
            Schedule Manager</h1>
        </div>""",
        unsafe_allow_html=True,
    )

    st.markdown("### Manage Daily Schedules and Weekly Assignments")

    # Create main tabs for different sections - removed Teacher Management
    main_tabs = st.tabs(["📅 View Daily Schedules", "📝 Daily Schedule Management"])
    
    # Tab 1: Daily Schedule Viewer (existing functionality)
    with main_tabs[0]:
        st.subheader("View Teacher Schedules for Each Day")
        
        # Day selection
        day_names_dict = {
            0: "Monday",
            1: "Tuesday", 
            2: "Wednesday",
            3: "Thursday",
            4: "Friday",
            5: "Saturday",
        }

        # Create tabs for each day
        tabs = st.tabs([day_names_dict[day] for day in sorted(day_names_dict.keys())])

        # Handle each tab (day)
        for day_idx in sorted(day_names_dict.keys()):
            day_name = day_names_dict[day_idx]
            with tabs[day_idx]:
                display_day_schedule(school_id, data_manager_instance, day_name)
    
    # Tab 2: Daily Schedule Management  
    with main_tabs[1]:
        render_daily_schedule_management(school_id, data_manager_instance)


def display_day_schedule(school_id, data_manager_instance, day_name):
    """
    Display schedules for a specific day.
    """
    # Load schedule data for the day
    schedule_df = data_manager_instance.load_teacher_schedules(
        school_id=school_id, specific_day=day_name
    )

    # Check if the fetched data is from the daily schedule or the summary
    is_daily_schedule = not schedule_df.empty and all(
        col in schedule_df.columns for col in [f"period{i}" for i in range(5, 8)]
    )

    if not schedule_df.empty:
        if is_daily_schedule:
            st.info(f"Showing Daily Schedule for {day_name}.")
            # Display the current schedule (Daily Schedule format)
            st.dataframe(
                schedule_df,
                column_config={
                    "teacher_id": st.column_config.TextColumn("Teacher ID"),
                    "name": st.column_config.TextColumn("Name"),
                    "subject": st.column_config.TextColumn("Subject"),
                    "category": st.column_config.TextColumn("Category"),
                    "period1": st.column_config.TextColumn("Period 1"),
                    "period2": st.column_config.TextColumn("Period 2"),
                    "period3": st.column_config.TextColumn("Period 3"),
                    "period4": st.column_config.TextColumn("Period 4"),
                    "period5": st.column_config.TextColumn("Period 5"),
                    "period6": st.column_config.TextColumn("Period 6"),
                    "period7": st.column_config.TextColumn("Period 7"),
                },
                hide_index=True,
                use_container_width=True,
            )
        else:
            st.warning(
                f"No specific schedule found for {day_name}. Showing fallback schedule."
            )
            # Display the fallback schedule (Legacy/Summary format)
            st.dataframe(
                schedule_df,
                column_config={
                    "teacher_id": st.column_config.TextColumn("Teacher ID"),
                    "name": st.column_config.TextColumn("Name"),
                    "subject": st.column_config.TextColumn("Subject"),
                    "category": st.column_config.TextColumn("Category"),
                    "period1": st.column_config.TextColumn("Period 1"),
                    "period2": st.column_config.TextColumn("Period 2"),
                    "period3": st.column_config.TextColumn("Period 3"),
                    "period4": st.column_config.TextColumn("Period 4"),
                },
                hide_index=True,
                use_container_width=True,
            )
    else:
        st.info(f"No schedule entries available for {day_name}.")


def render_daily_schedule_management(school_id, data_manager_instance):
    """Render daily schedule management interface"""
    st.subheader("Daily Schedule Management")
    
    # Create sub-tabs for schedule operations
    schedule_tabs = st.tabs(["📋 View Schedules", "➕ Add Schedule", "✏️ Edit Schedule", "🗑️ Delete Schedule"])
    
    # Tab 1: View Daily Schedules
    with schedule_tabs[0]:
        st.markdown("#### All Daily Schedules")
        
        # Filter options
        col1, col2 = st.columns(2)
        with col1:
            day_filter = st.selectbox("Filter by Day", 
                                    ["All", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"])
        with col2:
            teacher_filter = st.text_input("Filter by Teacher ID (optional)")
        
        schedules_df = get_daily_schedules(school_id, data_manager_instance, day_filter, teacher_filter)
        
        if not schedules_df.empty:
            st.info(f"Found {len(schedules_df)} schedule entries")
            st.dataframe(
                schedules_df,
                column_config={
                    "schedule_id": st.column_config.NumberColumn("ID"),
                    "teacher_id": st.column_config.TextColumn("Teacher ID"),
                    "day_of_week": st.column_config.TextColumn("Day"),
                    "period_number": st.column_config.NumberColumn("Period"),
                    "subject": st.column_config.TextColumn("Subject"),
                    "class_name": st.column_config.TextColumn("Class"),
                },
                hide_index=True,
                use_container_width=True,
            )
        else:
            st.info("No daily schedules found.")
    
    # Tab 2: Add Full Day Schedule (Bulk)
    with schedule_tabs[1]:
        st.markdown("#### Add Full Day Schedule for Teacher")
        st.info("💡 Add all 7 periods for a teacher in one go")
        
        # Get list of teachers for dropdown
        teachers_df = get_all_teachers(school_id, data_manager_instance)
        teacher_options = {row['teacher_id']: f"{row['teacher_id']} - {row['name']} ({row['category']})" 
                         for _, row in teachers_df.iterrows()} if not teachers_df.empty else {}
        
        if teacher_options:
            with st.form("add_full_schedule_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    selected_teacher = st.selectbox("Select Teacher *", 
                                                  options=list(teacher_options.keys()),
                                                  format_func=lambda x: teacher_options[x])
                
                with col2:
                    day_of_week = st.selectbox("Day of Week *", 
                                             ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"])
                
                # Load existing schedule for this teacher and day
                existing_schedule = get_teacher_day_schedule(school_id, selected_teacher, day_of_week, data_manager_instance)
                
                st.markdown("#### Schedule for All 7 Periods")
                st.markdown("*Enter subject and class for each period. Leave blank for free periods.*")
                
                if existing_schedule:
                    st.info(f"⚠️ Teacher {selected_teacher} already has some periods scheduled for {day_of_week}")
                    with st.expander("View Existing Schedule"):
                        for period_data in existing_schedule:
                            st.write(f"Period {period_data['period_number']}: {period_data['subject']} - {period_data['class_name']}")
                
                # Create 7 period inputs
                periods_data = []
                cols = st.columns(2)
                
                for period in range(1, 8):
                    with cols[(period-1) % 2]:
                        st.markdown(f"**Period {period}**")
                        
                        # Pre-fill if existing data
                        existing_entry = next((e for e in existing_schedule if e['period_number'] == period), None) if existing_schedule else None
                        default_subject = existing_entry['subject'] if existing_entry else ""
                        default_class = existing_entry['class_name'] if existing_entry else ""
                        
                        subject = st.text_input(f"Subject", key=f"subject_{period}", 
                                              value=default_subject, 
                                              placeholder="e.g., Mathematics")
                        class_name = st.text_input(f"Class", key=f"class_{period}", 
                                                 value=default_class,
                                                 placeholder="e.g., IX-A")
                        periods_data.append({
                            'period': period,
                            'subject': subject.strip(),
                            'class_name': class_name.strip()
                        })
                
                submitted = st.form_submit_button("📅 Add/Update Full Day Schedule", type="primary")
                
                if submitted:
                    # First delete existing entries for this teacher and day
                    delete_teacher_day_schedule(school_id, selected_teacher, day_of_week, data_manager_instance)
                    
                    # Filter out empty periods
                    valid_periods = [p for p in periods_data if p['subject'] and p['class_name']]
                    
                    if valid_periods:
                        success_count = 0
                        errors = []
                        
                        # Add each period
                        for period_data in valid_periods:
                            success = add_daily_schedule(school_id, selected_teacher, day_of_week, 
                                                       period_data['period'], period_data['subject'], 
                                                       period_data['class_name'], data_manager_instance)
                            if success:
                                success_count += 1
                            else:
                                errors.append(f"Period {period_data['period']}")
                        
                        if success_count > 0:
                            st.success(f"✅ Added/Updated {success_count} schedule entries successfully!")
                            if errors:
                                st.warning(f"⚠️ Failed to add periods: {', '.join(errors)}")
                            st.rerun()
                        else:
                            st.error("❌ Failed to add any schedule entries. Please check for errors.")
                    else:
                        st.error("❌ Please fill at least one period with both subject and class.")
        else:
            st.warning("⚠️ No teachers found. Please add teachers first from Teacher Management page.")
    
    # Tab 3: Edit Daily Schedule
    with schedule_tabs[2]:
        st.markdown("#### Edit Daily Schedule Entry")
        
        schedules_df = get_daily_schedules(school_id, data_manager_instance)
        
        if not schedules_df.empty:
            # Create unique identifier for each schedule entry
            schedule_options = {}
            for _, row in schedules_df.iterrows():
                key = f"{row['schedule_id']}"
                value = f"ID:{row['schedule_id']} - {row['teacher_id']} - {row['day_of_week']} - Period {row['period_number']} - {row['subject']}"
                schedule_options[key] = value
            
            selected_schedule = st.selectbox("Select Schedule to Edit", 
                                           options=list(schedule_options.keys()),
                                           format_func=lambda x: schedule_options[x])
            
            if selected_schedule:
                schedule_data = schedules_df[schedules_df['schedule_id'] == int(selected_schedule)].iloc[0]
                
                # Get teachers for dropdown
                teachers_df = get_all_teachers(school_id, data_manager_instance)
                teacher_options = {row['teacher_id']: f"{row['teacher_id']} - {row['name']}" 
                                 for _, row in teachers_df.iterrows()}
                
                with st.form("edit_schedule_form"):
                    st.info(f"Editing Schedule ID: {selected_schedule}")
                    
                    current_teacher_idx = list(teacher_options.keys()).index(schedule_data['teacher_id']) if schedule_data['teacher_id'] in teacher_options else 0
                    new_teacher = st.selectbox("Teacher", 
                                             options=list(teacher_options.keys()),
                                             format_func=lambda x: teacher_options[x],
                                             index=current_teacher_idx)
                    
                    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
                    current_day_idx = days.index(schedule_data['day_of_week']) if schedule_data['day_of_week'] in days else 0
                    new_day = st.selectbox("Day of Week", days, index=current_day_idx)
                    
                    new_period = st.selectbox("Period Number", [1, 2, 3, 4, 5, 6, 7], 
                                            index=schedule_data['period_number'] - 1)
                    new_subject = st.text_input("Subject", value=schedule_data['subject'])
                    new_class = st.text_input("Class Name", value=schedule_data['class_name'])
                    
                    submitted = st.form_submit_button("Update Schedule Entry")
                    
                    if submitted:
                        success = update_daily_schedule(selected_schedule, new_teacher, new_day, 
                                                      new_period, new_subject, new_class, data_manager_instance)
                        if success:
                            st.success("Schedule entry updated successfully!")
                            st.rerun()
                        else:
                            st.error("Failed to update schedule entry.")
        else:
            st.info("No schedules available to edit.")
    
    # Tab 4: Delete Daily Schedule
    with schedule_tabs[3]:
        st.markdown("#### Delete Daily Schedule Entry")
        
        schedules_df = get_daily_schedules(school_id, data_manager_instance)
        
        if not schedules_df.empty:
            # Create unique identifier for each schedule entry
            schedule_options = {}
            for _, row in schedules_df.iterrows():
                key = f"{row['schedule_id']}"
                value = f"ID:{row['schedule_id']} - {row['teacher_id']} - {row['day_of_week']} - Period {row['period_number']} - {row['subject']}"
                schedule_options[key] = value
            
            selected_schedule = st.selectbox("Select Schedule to Delete", 
                                           options=list(schedule_options.keys()),
                                           format_func=lambda x: schedule_options[x])
            
            if selected_schedule:
                schedule_data = schedules_df[schedules_df['schedule_id'] == int(selected_schedule)].iloc[0]
                
                st.warning(f"⚠️ You are about to delete schedule entry:")
                st.info(f"Teacher: {schedule_data['teacher_id']}, Day: {schedule_data['day_of_week']}, Period: {schedule_data['period_number']}, Subject: {schedule_data['subject']}")
                st.error("This action cannot be undone!")
                
                if st.button("🗑️ Delete Schedule Entry", type="secondary"):
                    success = delete_daily_schedule(selected_schedule, data_manager_instance)
                    if success:
                        st.success("Schedule entry deleted successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to delete schedule entry.")
        else:
            st.info("No schedules available to delete.")


# Helper functions for database operations

def get_all_teachers(school_id, data_manager_instance):
    """Get all teachers from the users table"""
    from data_manager import create_db_connection, read_query
    
    connection = create_db_connection()
    if connection is None:
        return pd.DataFrame()
    
    try:
        query = "SELECT teacher_id, name, phone, category, biometric_code FROM users WHERE school_id = %s ORDER BY name"
        result = read_query(connection, query, (school_id,))
        return pd.DataFrame(result)
    finally:
        if connection and connection.is_connected():
            connection.close()


def get_daily_schedules(school_id, data_manager_instance, day_filter="All", teacher_filter=""):
    """Get daily schedules from the daily_schedule table"""
    from data_manager import create_db_connection, read_query
    
    connection = create_db_connection()
    if connection is None:
        return pd.DataFrame()
    
    try:
        query = "SELECT * FROM daily_schedule WHERE school_id = %s"
        params = [school_id]
        
        if day_filter != "All":
            query += " AND day_of_week = %s"
            params.append(day_filter)
        
        if teacher_filter:
            query += " AND teacher_id = %s"
            params.append(teacher_filter)
        
        query += " ORDER BY day_of_week, teacher_id, period_number"
        
        result = read_query(connection, query, params)
        return pd.DataFrame(result)
    finally:
        if connection and connection.is_connected():
            connection.close()


def get_teacher_day_schedule(school_id, teacher_id, day_of_week, data_manager_instance):
    """Get existing schedule for a teacher on a specific day"""
    from data_manager import create_db_connection, read_query
    
    connection = create_db_connection()
    if connection is None:
        return []
    
    try:
        query = "SELECT * FROM daily_schedule WHERE school_id = %s AND teacher_id = %s AND day_of_week = %s ORDER BY period_number"
        result = read_query(connection, query, (school_id, teacher_id, day_of_week))
        return result
    finally:
        if connection and connection.is_connected():
            connection.close()


def delete_teacher_day_schedule(school_id, teacher_id, day_of_week, data_manager_instance):
    """Delete all schedule entries for a teacher on a specific day"""
    from data_manager import create_db_connection, execute_query
    
    connection = create_db_connection()
    if connection is None:
        return False
    
    try:
        query = "DELETE FROM daily_schedule WHERE school_id = %s AND teacher_id = %s AND day_of_week = %s"
        return execute_query(connection, query, (school_id, teacher_id, day_of_week))
    finally:
        if connection and connection.is_connected():
            connection.close()


def add_daily_schedule(school_id, teacher_id, day_of_week, period_number, subject, class_name, data_manager_instance):
    """Add a new daily schedule entry"""
    from data_manager import create_db_connection, execute_query
    
    connection = create_db_connection()
    if connection is None:
        return False
    
    try:
        query = """INSERT INTO daily_schedule (school_id, teacher_id, day_of_week, period_number, subject, class_name) 
                   VALUES (%s, %s, %s, %s, %s, %s)"""
        return execute_query(connection, query, (school_id, teacher_id, day_of_week, period_number, subject, class_name))
    finally:
        if connection and connection.is_connected():
            connection.close()


def update_daily_schedule(schedule_id, teacher_id, day_of_week, period_number, subject, class_name, data_manager_instance):
    """Update daily schedule entry"""
    from data_manager import create_db_connection, execute_query
    
    connection = create_db_connection()
    if connection is None:
        return False
    
    try:
        query = """UPDATE daily_schedule SET teacher_id = %s, day_of_week = %s, period_number = %s, 
                   subject = %s, class_name = %s WHERE schedule_id = %s"""
        return execute_query(connection, query, (teacher_id, day_of_week, period_number, subject, class_name, schedule_id))
    finally:
        if connection and connection.is_connected():
            connection.close()


def delete_daily_schedule(schedule_id, data_manager_instance):
    """Delete daily schedule entry"""
    from data_manager import create_db_connection, execute_query
    
    connection = create_db_connection()
    if connection is None:
        return False
    
    try:
        query = "DELETE FROM daily_schedule WHERE schedule_id = %s"
        return execute_query(connection, query, (schedule_id,))
    finally:
        if connection and connection.is_connected():
            connection.close()