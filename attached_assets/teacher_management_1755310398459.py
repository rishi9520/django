import streamlit as st
import pandas as pd
from data_manager import create_db_connection, read_query, execute_query


def render_teacher_management_page(school_id, data_manager_instance):
    """Render the complete teacher management page"""
    st.title("👨‍🏫 Teacher Management")
    st.markdown("### Manage Teachers - Add, Edit, Delete and View All Teachers")
    
    # Create main tabs for teacher operations
    teacher_tabs = st.tabs(["📋 View All Teachers", "➕ Add New Teacher", "✏️ Edit Teacher", "🗑️ Delete Teacher"])
    
    # Tab 1: View All Teachers
    with teacher_tabs[0]:
        st.markdown("#### All Teachers in School")
        teachers_df = get_all_teachers(school_id, data_manager_instance)
        
        if not teachers_df.empty:
            # Display total count
            st.info(f"Total Teachers: {len(teachers_df)}")
            
            # Add search/filter functionality
            col1, col2 = st.columns(2)
            with col1:
                search_term = st.text_input("🔍 Search by Name or Teacher ID", "")
            with col2:
                category_filter = st.selectbox("Filter by Category", ["All", "TGT", "PGT", "PRT"])
            
            # Apply filters
            filtered_df = teachers_df.copy()
            if search_term:
                filtered_df = filtered_df[
                    filtered_df['name'].str.contains(search_term, case=False, na=False) |
                    filtered_df['teacher_id'].str.contains(search_term, case=False, na=False)
                ]
            
            if category_filter != "All":
                filtered_df = filtered_df[filtered_df['category'] == category_filter]
            
            # Display filtered results
            if not filtered_df.empty:
                st.dataframe(
                    filtered_df,
                    column_config={
                        "teacher_id": st.column_config.TextColumn("Teacher ID", width="small"),
                        "name": st.column_config.TextColumn("Name", width="medium"),
                        "phone": st.column_config.TextColumn("Phone", width="small"),
                        "category": st.column_config.TextColumn("Category", width="small"),
                        "biometric_code": st.column_config.TextColumn("Biometric Code", width="small"),
                    },
                    hide_index=True,
                    use_container_width=True,
                )
                
                # Export functionality
                csv = filtered_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Teacher List (CSV)",
                    data=csv,
                    file_name=f"teachers_list_{school_id}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No teachers match your search criteria.")
        else:
            st.info("No teachers found in the database.")
    
    # Tab 2: Add New Teacher
    with teacher_tabs[1]:
        st.markdown("#### Add New Teacher to School")
        
        with st.form("add_teacher_form", clear_on_submit=True):
            st.info("ℹ️ All fields marked with * are mandatory")
            
            col1, col2 = st.columns(2)
            with col1:
                teacher_id = st.text_input("Teacher ID *", 
                                         help="Unique identifier for the teacher (e.g., T001, MATH001)",
                                         placeholder="Enter unique teacher ID")
                name = st.text_input("Full Name *", 
                                   help="Complete name of the teacher",
                                   placeholder="Enter teacher's full name")
                category = st.selectbox("Category *", ["TGT", "PGT", "PRT"], 
                                      help="TGT: Trained Graduate Teacher, PGT: Post Graduate Teacher, PRT: Primary Teacher")
            
            with col2:
                phone = st.text_input("Phone Number *", 
                                    help="10-digit mobile number", 
                                    placeholder="Enter 10-digit phone number",
                                    max_chars=10)
                biometric_code = st.text_input("Biometric Code", 
                                             help="Code used in biometric attendance system (optional)",
                                             placeholder="Enter biometric device code")
            
            submitted = st.form_submit_button("➕ Add Teacher", type="primary")
            
            if submitted:
                # Validation
                errors = []
                
                if not teacher_id or not teacher_id.strip():
                    errors.append("Teacher ID is required")
                
                if not name or not name.strip():
                    errors.append("Teacher name is required")
                
                if not phone or not phone.strip():
                    errors.append("Phone number is required")
                elif len(phone.strip()) != 10:
                    errors.append("Phone number must be exactly 10 digits")
                elif not phone.strip().isdigit():
                    errors.append("Phone number must contain only digits")
                
                if errors:
                    for error in errors:
                        st.error(f"❌ {error}")
                else:
                    # Check if teacher ID already exists
                    if check_teacher_id_exists(school_id, teacher_id.strip(), data_manager_instance):
                        st.error(f"❌ Teacher ID '{teacher_id.strip()}' already exists. Please use a different ID.")
                    else:
                        success = add_teacher(school_id, teacher_id.strip(), name.strip(), 
                                            phone.strip(), category, biometric_code.strip(), data_manager_instance)
                        if success:
                            st.success(f"✅ Teacher {name.strip()} added successfully!")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error("❌ Failed to add teacher. Please try again.")
    
    # Tab 3: Edit Teacher
    with teacher_tabs[2]:
        st.markdown("#### Edit Teacher Information")
        
        teachers_df = get_all_teachers(school_id, data_manager_instance)
        
        if not teachers_df.empty:
            # Teacher selection
            teacher_options = {row['teacher_id']: f"{row['teacher_id']} - {row['name']} ({row['category']})" 
                             for _, row in teachers_df.iterrows()}
            
            selected_teacher = st.selectbox("Select Teacher to Edit", 
                                          options=list(teacher_options.keys()),
                                          format_func=lambda x: teacher_options[x])
            
            if selected_teacher:
                teacher_data = teachers_df[teachers_df['teacher_id'] == selected_teacher].iloc[0]
                
                with st.form("edit_teacher_form"):
                    st.info(f"Editing: {teacher_data['name']} (ID: {teacher_data['teacher_id']})")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        new_name = st.text_input("Full Name *", value=teacher_data['name'])
                        new_category = st.selectbox("Category *", ["TGT", "PGT", "PRT"], 
                                                  index=get_category_index(teacher_data.get('category', 'TGT')))
                    
                    with col2:
                        new_phone = st.text_input("Phone Number *", value=teacher_data.get('phone', ''),
                                                max_chars=10)
                        new_biometric_code = st.text_input("Biometric Code", 
                                                         value=teacher_data.get('biometric_code', ''))
                    
                    submitted = st.form_submit_button("💾 Update Teacher", type="primary")
                    
                    if submitted:
                        # Validation
                        errors = []
                        
                        if not new_name or not new_name.strip():
                            errors.append("Teacher name is required")
                        
                        if not new_phone or not new_phone.strip():
                            errors.append("Phone number is required")
                        elif len(new_phone.strip()) != 10:
                            errors.append("Phone number must be exactly 10 digits")
                        elif not new_phone.strip().isdigit():
                            errors.append("Phone number must contain only digits")
                        
                        if errors:
                            for error in errors:
                                st.error(f"❌ {error}")
                        else:
                            success = update_teacher(school_id, selected_teacher, new_name.strip(), 
                                                   new_phone.strip(), new_category, new_biometric_code.strip(), 
                                                   data_manager_instance)
                            if success:
                                st.success(f"✅ Teacher {new_name.strip()} updated successfully!")
                                st.rerun()
                            else:
                                st.error("❌ Failed to update teacher.")
        else:
            st.info("No teachers available to edit.")
    
    # Tab 4: Delete Teacher
    with teacher_tabs[3]:
        st.markdown("#### Delete Teacher")
        st.warning("⚠️ **Warning:** Deleting a teacher will also remove all their schedule entries and attendance records.")
        
        teachers_df = get_all_teachers(school_id, data_manager_instance)
        
        if not teachers_df.empty:
            teacher_options = {row['teacher_id']: f"{row['teacher_id']} - {row['name']} ({row['category']})" 
                             for _, row in teachers_df.iterrows()}
            
            selected_teacher = st.selectbox("Select Teacher to Delete", 
                                          options=list(teacher_options.keys()),
                                          format_func=lambda x: teacher_options[x])
            
            if selected_teacher:
                teacher_data = teachers_df[teachers_df['teacher_id'] == selected_teacher].iloc[0]
                
                # Show teacher details
                st.error(f"🗑️ **You are about to delete:**")
                st.write(f"**Name:** {teacher_data['name']}")
                st.write(f"**Teacher ID:** {selected_teacher}")
                st.write(f"**Category:** {teacher_data['category']}")
                st.write(f"**Phone:** {teacher_data.get('phone', 'N/A')}")
                
                st.error("**This action cannot be undone!**")
                
                # Double confirmation
                confirm = st.checkbox("I understand that this action cannot be undone")
                
                if confirm:
                    if st.button("🗑️ **DELETE TEACHER**", type="secondary", use_container_width=True):
                        success = delete_teacher(school_id, selected_teacher, data_manager_instance)
                        if success:
                            st.success(f"✅ Teacher {teacher_data['name']} deleted successfully!")
                            st.rerun()
                        else:
                            st.error("❌ Failed to delete teacher. They may have existing records.")
        else:
            st.info("No teachers available to delete.")


def get_category_index(category):
    """Get index for category dropdown"""
    categories = ["TGT", "PGT", "PRT"]
    category_mapping = {
        'P.G.T': 'PGT',
        'T.G.T': 'TGT', 
        'P.R.T': 'PRT',
        'Primary': 'PRT',
        'Secondary': 'TGT',
        'Senior Secondary': 'PGT',
        'Admin': 'TGT',
        'Support': 'TGT'
    }
    
    mapped_category = category_mapping.get(category, category)
    if mapped_category not in categories:
        mapped_category = 'TGT'
    
    try:
        return categories.index(mapped_category)
    except ValueError:
        return 0


def get_all_teachers(school_id, data_manager_instance):
    """Get all teachers from the users table"""
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


def check_teacher_id_exists(school_id, teacher_id, data_manager_instance):
    """Check if teacher ID already exists"""
    connection = create_db_connection()
    if connection is None:
        return False
    
    try:
        query = "SELECT COUNT(*) as count FROM users WHERE school_id = %s AND teacher_id = %s"
        result = read_query(connection, query, (school_id, teacher_id))
        return result[0]['count'] > 0 if result else False
    finally:
        if connection and connection.is_connected():
            connection.close()


def add_teacher(school_id, teacher_id, name, phone, category, biometric_code, data_manager_instance):
    """Add a new teacher to the users table"""
    connection = create_db_connection()
    if connection is None:
        return False
    
    try:
        query = """INSERT INTO users (school_id, teacher_id, name, phone, category, biometric_code) 
                   VALUES (%s, %s, %s, %s, %s, %s)"""
        return execute_query(connection, query, (school_id, teacher_id, name, phone, category, biometric_code))
    finally:
        if connection and connection.is_connected():
            connection.close()


def update_teacher(school_id, teacher_id, name, phone, category, biometric_code, data_manager_instance):
    """Update teacher details in the users table"""
    connection = create_db_connection()
    if connection is None:
        return False
    
    try:
        query = """UPDATE users SET name = %s, phone = %s, category = %s, biometric_code = %s 
                   WHERE school_id = %s AND teacher_id = %s"""
        return execute_query(connection, query, (name, phone, category, biometric_code, school_id, teacher_id))
    finally:
        if connection and connection.is_connected():
            connection.close()


def delete_teacher(school_id, teacher_id, data_manager_instance):
    """Delete teacher from the users table"""
    connection = create_db_connection()
    if connection is None:
        return False
    
    try:
        # First delete related schedule entries
        delete_schedule_query = "DELETE FROM daily_schedule WHERE school_id = %s AND teacher_id = %s"
        execute_query(connection, delete_schedule_query, (school_id, teacher_id))
        
        # Then delete the teacher
        query = "DELETE FROM users WHERE school_id = %s AND teacher_id = %s"
        return execute_query(connection, query, (school_id, teacher_id))
    finally:
        if connection and connection.is_connected():
            connection.close()