# --- START OF FILE arrangements.py ---

import streamlit as st
import pandas as pd
from datetime import datetime, date


def render_arrangements_page(
    school_id, data_manager_instance  # Accept DataManager instance directly
):
    """
    Render the arrangements management page.
    Args:
        school_id: The ID of the logged-in school.
        data_manager_instance: The initialized DataManager instance.
    """
    # DataManager instance is passed as argument now, no need to fetch from session state again here
    # data_manager_instance = st.session_state.data_manager # Removed this line

    # Check if DataManager instance is available (should be, as it's passed)
    if data_manager_instance is None:
        st.error(
            "System error: DataManager instance not available for Arrangements page."
        )
        return  # Cannot proceed without DataManager instance

    st.markdown(
        """<div class="card-title" style="display: flex; align-items: center;color:#1e3a8a;">
        <h1><svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" fill="currentColor" viewBox="0 0 16 16" style="margin-right: 5px;">
          <path d="M10 1.5a.5.5 0 0 0-.5-.5h-3a.5.5 0 0 0-.5.5v1a.5.5 0 0 0 .5.5h3a.5.5 0 0 0 .5-.5v-1Zm-5 0A1.5 1.5 0 0 1 6.5 0h3A1.5.5 0 0 1 11 1.5v1A1.5 1.5 0 0 1 9.5 4h-3A1.5 1.5 0 0 1 5 2.5v-1Zm-2 0h1v1A2.5 2.5 0 0 0 6.5 5h3A2.5 2.5 0 0 0 12 2.5v-1h1a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2v-10a2 2 0 0 1 2-2Z"/>
          <path d="M4.5 8a.5.5 0 0 0 0 1h7a.5.5 0 0 0 0-1h-7Zm0 2.5a.5.5 0 0 0 0 1h7a.5.5 0 0 0 0-1h-7Z"/>
        </svg>
        Arrangements</H1> <!-- Changed H! to H1 -->
    </div>""",
        unsafe_allow_html=True,
    )

    today = date.today()

    # Check if arrangements are suspended - Use DataManager instance
    # data_manager_instance.is_arrangement_suspended needs (school_id, date_obj)
    # Assuming it returns True/False and handles its own connection
    is_suspended = data_manager_instance.is_arrangement_suspended(school_id, today)

    if is_suspended:
        st.warning(f"⚠️ Arrangements are currently suspended for today, {today}.")

    # Create tabs for different arrangement views
    auto_tab, manual_tab = st.tabs(["Auto Arrangements", "Manual Arrangements"])

    with auto_tab:
        # Pass school_id, DataManager instance, today's date, and suspension status
        display_auto_arrangements(
            school_id,
            data_manager_instance,
            today,
            is_suspended,
        )

    with manual_tab:
        # Pass school_id, DataManager instance, today's date, and suspension status
        create_manual_arrangements(
            school_id,
            data_manager_instance,
            today,
            is_suspended,
        )


# Modify helper functions to accept school_id, DataManager instance, etc.
# Removed db_connection parameter.
def display_auto_arrangements(
    school_id,
    data_manager_instance,
    today,  # Use date object
    is_suspended,
):
    """Display automatically generated arrangements"""

    if is_suspended:
        # Message already shown in main render function, but maybe repeat here?
        # st.warning("⚠️ Arrangements are currently suspended for today")
        return  # Exit function if suspended

    # Ensure DataManager instance is available
    if data_manager_instance is None:
        st.error(
            "System error: DataManager instance not available for Auto Arrangements."
        )
        return

    # Get today's absent teachers - Use DataManager instance
    # data_manager_instance.get_absent_teachers needs (school_id, date_str)
    # Assuming it returns a list of teacher_ids (strings) or empty list []
    absent_teachers_list = data_manager_instance.get_absent_teachers(
        school_id, str(today)  # Pass date as string
    )

    if not absent_teachers_list:  # Check if the list is empty
        st.info("No absences marked for today. No auto arrangements needed yet.")
        return  # Exit function if no absent teachers

    # The list is not empty, proceed to show arrangements

    st.subheader("Today's Arrangements")

    # Show current arrangements - Use DataManager instance
    # data_manager_instance.get_todays_arrangements needs (school_id, date_obj)
    # Assuming it returns a Pandas DataFrame or empty DataFrame pd.DataFrame()
    arrangements_df = data_manager_instance.get_todays_arrangements(
        school_id, today  # Pass date object
    )

    # Check if the DataFrame is empty using .empty property
    if not arrangements_df.empty:
        # DataFrame is not empty, display it

        # Define custom formatting based on match quality (Keep as is)
        # This function is correct for styling
        def get_match_color(quality):
            quality_lower = quality.lower() if isinstance(quality, str) else ""
            if quality_lower == "ideal":
                return "#28a745"  # Green
            elif quality_lower == "acceptable":
                return "#ffc107"  # Yellow
            elif quality_lower in [
                "suboptimal",
                "last resort",
            ]:  # Consider suboptimal and last resort as problematic
                return "#fd7e14"  # Orange
            elif quality_lower == "manual":  # Manual assignment style
                return "#007bff"  # Blue
            else:  # Includes "unassigned", None, empty, other statuses
                return "#dc3545"  # Red

        # Apply formatting to dataframe (Keep as is)
        # Ensure column names match your DB table column names AND what get_todays_arrangements returns in the DataFrame.
        # Based on previous fixes, DB columns use _id suffix and arrangement_date.
        # DataManager read_query with dictionary=True should return these names.
        st.dataframe(
            arrangements_df,  # Use the DataFrame from DB data
            column_config={
                "absent_teacher_id": st.column_config.TextColumn(
                    "Absent ID"
                ),  # Use correct column name
                "absent_name": st.column_config.TextColumn("Absent Name"),
                "absent_category": st.column_config.TextColumn("Absent Category"),
                "replacement_teacher_id": st.column_config.TextColumn(  # Use correct column name
                    "Replacement ID"
                ),
                "replacement_name": st.column_config.TextColumn("Replacement Name"),
                "replacement_category": st.column_config.TextColumn(
                    "Replacement Category"
                ),
                "class": st.column_config.TextColumn("Class"),
                "period": st.column_config.NumberColumn("Period"),
                "match_quality": st.column_config.TextColumn(
                    "Match Quality",
                    help="Quality of the replacement teacher match.",
                    width="medium",
                ),
                "status": st.column_config.TextColumn("Status"),
                "arrangement_date": st.column_config.DateColumn(
                    "Date"
                ),  # Use correct column name
                "arrangement_id": None,  # Hide the primary key ID column
            },
            hide_index=True,
            use_container_width=True,
            # Add styling for match quality if needed, e.g., via apply function before dataframe
            # .style.apply(lambda row: ['background-color: %s' % get_match_color(row['match_quality'])] * len(row), axis=1)
        )
        # Match quality explanation markdown (Ensure it's placed here or nearby if desired)
        st.markdown(
            """
        <div style="font-size: 0.9em; color: #555; margin-top: 10px;">
        Match Quality: <span style="color: #28a745;">Ideal</span>, <span style="color: #ffc107;">Acceptable</span>, <span style="color: #fd7e14;">Suboptimal/Last Resort</span>, <span style="color: #007bff;">Manual</span>, <span style="color: #dc3545;">Unassigned</span>
        </div>
        """,
            unsafe_allow_html=True,
        )
        with st.expander("About Teacher Categories and Match Quality Criteria"):
            st.markdown(
                """
             ### Teacher Categories
             Teachers are categorized into three groups:
             - **PGT**: Post Graduate Teachers
             - **TGT**: Trained Graduate Teachers
             - **PRT**: Primary Teachers

             ### Match Quality Criteria (Based on Search Order)
             The system prioritizes finding replacements in a specific order. The 'Match Quality' reflects the *type* of match found:
             - **Ideal**: Usually same category, same subject.
             - **Acceptable**: Could be same category different subject, or different category same subject (depending on hierarchy, e.g., TGT replacing PGT subject match).
             - **Suboptimal**: Less ideal category/subject matches.
             - **Last Resort**: Any available teacher when other criteria fail.
             - **Manual**: Arrangement was created manually.
             - **Unassigned**: No replacement found.

             Exact criteria and priority depend on the system's configuration.
             """,
                unsafe_allow_html=True,
            )  # Keep original markdown content and add details about types

    else:
        # If the DataFrame is empty
        st.info("No arrangements have been made yet for today.")


# Modify helper functions to accept school_id, DataManager instance, etc.
# Removed db_connection parameter.
def create_manual_arrangements(
    school_id,
    data_manager_instance,
    today,  # Use date object
    is_suspended,
):
    """Create manual arrangements for teachers (e.g., half-day leave)"""

    st.subheader("Create Manual Arrangement")
    st.markdown(
        """
    Use this form to create manual arrangements for specific periods, such as when a teacher takes half-day leave or
    needs to be absent for specific periods only.
    """
    )

    # Ensure DataManager instance is available
    if data_manager_instance is None:
        st.error(
            "System error: DataManager instance not available for Manual Arrangements."
        )
        return

    # Get all teachers - Use DataManager instance
    # data_manager_instance.get_all_teachers needs (school_id)
    # Assuming it returns a list of dicts {teacher_id, name, category, ...} or empty list []
    all_teachers_list = data_manager_instance.get_all_teachers(school_id)

    if not all_teachers_list:
        st.error("No teachers found for this school.")
        return  # Exit if no teachers

    # Prepare options list with name and ID (Keep as is)
    # Ensure handling potential None/NaN values in teacher data
    teacher_options = ["-- Select --"] + [  # Add a default empty option
        f"{t.get('name', 'N/A')} ({t.get('teacher_id', 'N/A')}) - {t.get('category', 'N/A')}"
        for t in all_teachers_list
        if t and t.get("teacher_id")  # Only include if teacher_id exists
    ]
    teacher_ids_map = {  # Map display string to teacher_id
        f"{t.get('name', 'N/A')} ({t.get('teacher_id', 'N/A')}) - {t.get('category', 'N/A')}": t.get(
            "teacher_id"
        )
        for t in all_teachers_list
        if t and t.get("teacher_id")
    }
    teacher_details_map = {  # Map teacher_id to full details dict
        t.get("teacher_id"): t for t in all_teachers_list if t and t.get("teacher_id")
    }

    # Define the periods (Keep as is)
    periods = [1, 2, 3, 4, 5, 6, 7]

    # Setup the form for manual arrangement (Keep form structure)
    with st.form("manual_arrangement_form"):
        st.markdown("### Select Teachers and Period")

        col1, col2 = st.columns(2)

        with col1:
            # Absent Teacher Selection
            # Ensure default "-- Select --" option is handled
            absent_teacher_selection = st.selectbox(
                "Select Absent Teacher",
                options=teacher_options,
                key="absent_teacher_select",
            )
            # Get the actual teacher ID if an option is selected
            absent_teacher_id = teacher_ids_map.get(absent_teacher_selection)

            # Period Selection
            period = st.selectbox(
                "Select Period",
                options=["-- Select --"] + periods,
                key="period_select",  # Add default option
            )

    if is_suspended:
        st.warning("⚠️ Arrangements are currently suspended for today")

    # Create tabs for different arrangement views
    auto_tab, manual_tab = st.tabs(["Auto Arrangements", "Manual Arrangements"])

    with auto_tab:
        # Pass school_id, DataManager instance, today, is_suspended to helper function
        display_auto_arrangements(
            school_id,
            data_manager_instance,
            today,
            is_suspended,
        )

    with manual_tab:
        # Pass school_id, DataManager instance, today, is_suspended to helper function
        create_manual_arrangements(
            school_id,
            data_manager_instance,
            today,
            is_suspended,
        )


# Modify helper functions to accept school_id, AND DataManager instance
def display_auto_arrangements(
    school_id,
    data_manager_instance,
    today,
    is_suspended,
):
    """Display automatically generated arrangements"""

    # Check if DataManager instance is available (safety check)
    if data_manager_instance is None:
        st.error("DataManager instance not available for auto arrangements display.")
        return

    if is_suspended:
        # Warning is already shown in render_arrangements_page, but show again here for clarity
        st.warning("⚠️ Arrangements are currently suspended for today")
        return

    # Get today's absent teachers - Use DataManager instance
    # DataManager.get_absent_teachers handles its own connection
    # It returns a list of teacher_ids or an empty list []
    absent_teachers_list = data_manager_instance.get_absent_teachers(
        school_id, str(today)  # Ensure date is passed as string
    )

    # Check if the list is empty
    if not absent_teachers_list:
        st.info("No absences marked for today, so no automatic arrangements needed.")
        return

    # The list is not empty, proceed to show arrangements
    st.subheader("Today's Arrangements")

    # Show current arrangements - Use DataManager instance
    # DataManager.get_todays_arrangements handles its own connection
    # It returns a Pandas DataFrame or an empty DataFrame
    arrangements_df = data_manager_instance.get_todays_arrangements(
        school_id, today  # Pass date object or compatible format
    )

    # Check if the returned DataFrame is empty
    # <<< CORRECTED: Check if DataFrame is NOT empty using .empty property >>>
    if not arrangements_df.empty:
        # Define custom formatting based on match quality (Keep as is)
        # This function will be applied later if needed, not directly in dataframe config
        def get_match_color(quality):
            quality_lower = quality.lower() if isinstance(quality, str) else ""
            if quality_lower == "ideal":
                return "background-color: #d4edda; color: #155724;"  # Green background
            elif quality_lower == "acceptable":
                return "background-color: #fff3cd; color: #856404;"  # Yellow background
            elif quality_lower == "suboptimal":
                return "background-color: #f8d7da; color: #721c24;"  # Red background
            elif quality_lower == "manual":
                return "background-color: #cce5ff; color: #004085;"  # Blue background
            elif quality_lower == "unassigned":
                return "background-color: #e2e3e5; color: #383d41;"  # Grey background
            else:
                return ""  # No special styling

        # Apply formatting to dataframe (Keep as is, ensure column names match DB)
        # Note: Styling applied using Styler later if needed, st.dataframe column_config is for display options
        st.dataframe(
            arrangements_df,  # Use the DataFrame from DB data
            column_config={  # Ensure column names match your arrangements table in DB / query result
                "arrangement_id": None,  # Hide auto-increment ID if it's in the dataframe
                "arrangement_date": st.column_config.DateColumn(
                    "Date"
                ),  # Use arrangement_date
                "absent_teacher_id": st.column_config.TextColumn(
                    "Absent Teacher ID"
                ),  # Use absent_teacher_id
                "absent_name": st.column_config.TextColumn("Absent Teacher Name"),
                "absent_category": st.column_config.TextColumn("Absent Category"),
                "replacement_teacher_id": st.column_config.TextColumn(
                    "Replacement Teacher ID"
                ),  # Use replacement_teacher_id
                "replacement_name": st.column_config.TextColumn(
                    "Replacement Teacher Name"
                ),
                "replacement_category": st.column_config.TextColumn(
                    "Replacement Category"
                ),
                "class": st.column_config.TextColumn("Class"),
                "period": st.column_config.NumberColumn("Period"),
                "status": st.column_config.TextColumn("Status"),
                "match_quality": st.column_config.TextColumn(
                    "Match Quality",
                    help="Quality of the replacement match.",
                    width="medium",
                ),
                # "date": None, # Remove or hide if arrangement_date is used
                # "id": None, # Hide auto-increment ID if name is 'id'
            },
            hide_index=True,
            use_container_width=True,  # Use container width for better scaling
        )

        # Display explanation for match quality (Keep as is)
        with st.expander("About Teacher Categories and Match Quality"):
            st.markdown(
                """
            ### Teacher Categories
            Teachers are categorized into three groups:
            - **PGT**: Post Graduate Teachers
            - **TGT**: Trained Graduate Teachers
            - **PRT**: Primary Teachers

            ### Match Quality Criteria (Based on Search Order)
            - **Ideal**: Same category, same subject match.
            - **Acceptable**: Lower/Higher category with same subject OR same category with different subject.
            - **Suboptimal**: More distant category/subject matches.
            - **Last Resort**: Any available teacher when others fail.
            - **Manual**: Assigned manually by an administrator.
            - **Unassigned**: No replacement found or explicitly left unassigned.

            The system prioritizes finding replacements based on a defined order (Ideal > Acceptable > Suboptimal > Last Resort).
            """,
                unsafe_allow_html=True,  # Keep original markdown content
            )
    else:
        st.info("No arrangements have been made yet for today.")


# Modify helper functions to accept school_id, AND DataManager instance
def create_manual_arrangements(
    school_id,
    data_manager_instance,
    today,
    is_suspended,
):
    """Create manual arrangements for teachers (e.g., half-day leave)"""

    st.subheader("Create Manual Arrangement")
    st.markdown(
        """
    Use this form to create manual arrangements for specific periods, such as when a teacher takes half-day leave or
    needs to be absent for specific periods only.
    """
    )

    # Check if DataManager instance is available (safety check)
    if data_manager_instance is None:
        st.error("DataManager instance not available for manual arrangements.")
        return

    if is_suspended:
        st.warning("⚠️ Arrangements are currently suspended for today")
        # Decide if you want to allow manual arrangements even if suspended
        # For now, let's allow the form to show, but maybe add a note.
        st.info(
            "Note: Arrangements are suspended, but you can still create manual assignments."
        )

    # Get all teachers - Use DataManager instance
    # DataManager.get_all_teachers handles its own connection.
    # It returns a list of dicts [{teacher_id, name, category, ...}] or [].
    all_teachers_list = data_manager_instance.get_all_teachers(school_id)

    if not all_teachers_list:
        st.error("No teachers found for this school.")
        return

    # Prepare options list with name and ID (Keep as is)
    # Ensure teacher_id, name, category keys exist in the dictionaries returned by get_all_teachers
    teacher_options = [
        f"{t.get('name', 'N/A')} ({t.get('teacher_id', 'N/A')}) - {t.get('category', 'N/A')}"
        for t in all_teachers_list
    ]
    # Create a map from the display string back to the teacher_id
    teacher_ids_map = {
        f"{t.get('name', 'N/A')} ({t.get('teacher_id', 'N/A')}) - {t.get('category', 'N/A')}": t.get(
            "teacher_id"
        )
        for t in all_teachers_list
    }
    # Create a map from teacher_id to full details dictionary
    teacher_details_map = {
        t.get("teacher_id"): t
        for t in all_teachers_list
        if t.get("teacher_id") is not None  # Map only if teacher_id exists
    }

    # Define the periods (Keep as is)
    periods = list(range(1, 8))  # Periods 1 to 7

    # Setup the form for manual arrangement (Keep form structure)
    with st.form("manual_arrangement_form"):
        st.markdown("### Select Teachers and Period")

        col1, col2 = st.columns(2)

        with col1:
            # Absent Teacher Selection
            absent_teacher_selection = st.selectbox(
                "Select Absent Teacher",
                options=[""] + teacher_options,  # Add empty option
                key="absent_teacher_select",
                index=0,  # Default to empty option
            )

            # Extract teacher ID from selection string using the map
            # Use get() safely, returns None if key not found (e.g., empty selection)
            absent_teacher_id = teacher_ids_map.get(absent_teacher_selection)

            # Period Selection
            period = st.selectbox(
                "Select Period",
                options=[""] + periods,
                key="period_select",
                index=0,  # Add empty option
            )

            # Class Selection
            class_name = st.text_input("Class Name/Section", key="class_name_input")

        with col2:
            # Replacement Teacher Selection
            # Filter out the absent teacher from replacement options (Keep as is)
            # Ensure absent_teacher_id is valid before filtering
            replacement_options = [""] + [  # Add empty option
                opt
                for opt in teacher_options
                if absent_teacher_id is not None
                and teacher_ids_map.get(opt) != absent_teacher_id
            ]
            # If no absent teacher is selected, replacement_options should probably be all teachers + unassigned option
            if absent_teacher_id is None:
                replacement_options = [""] + teacher_options

            # Add an explicit "UNASSIGNED" option for manual unassignment
            replacement_options.append("UNASSIGNED (No Replacement)")

            replacement_teacher_selection = st.selectbox(
                "Select Replacement Teacher",
                options=replacement_options,
                key="replacement_teacher_select",
                index=0,  # Default to empty
            )

            # Extract teacher ID from selection
            # Use get() safely, returns None if key not found (e.g., empty or UNASSIGNED selection)
            replacement_teacher_id = teacher_ids_map.get(replacement_teacher_selection)

            # Handle the explicit "UNASSIGNED" selection
            if replacement_teacher_selection == "UNASSIGNED (No Replacement)":
                replacement_teacher_id = "UNASSIGNED"  # Use a specific string/value to indicate manual unassignment

            # Optional date selection (defaults to today)
            use_different_date = st.checkbox(
                "Use Different Date", value=False, key="use_different_date_check"
            )
            if use_different_date:
                selected_date = st.date_input(
                    "Select Date", value=today, key="selected_date_input"
                )
            else:
                selected_date = today

        # Submit button
        submitted = st.form_submit_button("Create Arrangement")

        if submitted:
            # --- Validate Inputs ---
            if (
                not absent_teacher_id
                or not class_name
                or not selected_date
                or period == ""
            ):
                st.error("Please select Absent Teacher, Period, Class Name, and Date.")
            elif (
                replacement_teacher_id is None
                and replacement_teacher_selection != "UNASSIGNED (No Replacement)"
            ):
                # This case happens if an option was selected but not found in map (shouldn't happen with correct map)
                # Or if 'UNASSIGNED' wasn't specifically selected, but no teacher was picked
                st.error("Please select a valid Replacement Teacher or 'UNASSIGNED'.")
            else:
                # --- Inputs are Valid, Proceed to Create Arrangement ---

                # Get full details for names and categories from the map fetched earlier
                # Handle case where absent_teacher_id or replacement_teacher_id might be 'UNASSIGNED' or None
                absent_teacher_details = teacher_details_map.get(absent_teacher_id)
                replacement_teacher_details = teacher_details_map.get(
                    replacement_teacher_id
                )  # This will be None if replacement_teacher_id is 'UNASSIGNED' or None

                # Get names and categories, handling potential None/missing details
                absent_teacher_name = (
                    absent_teacher_details.get("name")
                    if absent_teacher_details
                    else absent_teacher_id
                )  # Use ID if name missing
                absent_category = (
                    absent_teacher_details.get("category")
                    if absent_teacher_details
                    else None
                )

                # Handle replacement details based on selection
                if (
                    replacement_teacher_id is None
                    or replacement_teacher_id == "UNASSIGNED"
                ):
                    # Manual Unassignment
                    replacement_teacher_id_to_pass = None  # Store as None in DB
                    replacement_name_to_pass = "UNASSIGNED"
                    replacement_category_to_pass = None
                    status_to_pass = "UNASSIGNED"
                    match_quality_to_pass = (
                        "Manual Unassigned"  # Specific quality for manual unassigned
                    )
                else:
                    # Manual Assignment with a replacement
                    replacement_teacher_id_to_pass = (
                        replacement_teacher_id  # Use the actual ID
                    )
                    replacement_name_to_pass = (
                        replacement_teacher_details.get("name")
                        if replacement_teacher_details
                        else replacement_teacher_id
                    )  # Use ID if name missing
                    replacement_category_to_pass = (
                        replacement_teacher_details.get("category")
                        if replacement_teacher_details
                        else None
                    )
                    status_to_pass = "MANUAL"  # Or "ASSIGNED" as per your status types
                    match_quality_to_pass = "Manual"  # Quality for manual assignment

                # Call the data_manager function to create the manual arrangement
                # DataManager.create_manual_arrangement handles its own connection and saving
                # Ensure it takes correct arguments
                success = data_manager_instance.create_manual_arrangement(
                    school_id=school_id,
                    absent_teacher=absent_teacher_id,  # The original absent teacher ID
                    absent_name=absent_teacher_name,
                    absent_category=absent_category,
                    replacement_teacher=replacement_teacher_id_to_pass,  # The chosen replacement ID (or None)
                    replacement_name=replacement_name_to_pass,
                    replacement_category=replacement_category_to_pass,
                    period=period,  # Pass the integer period
                    class_name=class_name,
                    current_date=selected_date,  # Pass date object
                    status=status_to_pass,
                    match_quality=match_quality_to_pass,
                )

                # --- Process Save Result ---
                if success:
                    st.success(
                        f"Manual arrangement created successfully for period {period} on {selected_date}."
                    )

                    st.subheader(
                        f"Arrangements for {selected_date.strftime('%Y-%m-%d')}"
                    )
                    # Fetch arrangements again - Use DataManager instance
                    # DataManager.get_todays_arrangements should handle its own connection and return DataFrame
                    all_arrangements_for_date_df = (
                        data_manager_instance.get_todays_arrangements(
                            school_id, selected_date  # Pass date object
                        )
                    )
                    # <<< Use .empty check for DataFrame >>>
                    if not all_arrangements_for_date_df.empty:
                        # Display using st.dataframe
                        st.dataframe(
                            all_arrangements_for_date_df,
                            column_config={  # Ensure column names match your arrangements table in DB / query result
                                "arrangement_id": None,  # Hide if exists
                                "arrangement_date": st.column_config.DateColumn("Date"),
                                "absent_teacher_id": st.column_config.TextColumn(
                                    "Absent Teacher ID"
                                ),
                                "absent_name": st.column_config.TextColumn(
                                    "Absent Teacher Name"
                                ),
                                "absent_category": st.column_config.TextColumn(
                                    "Absent Category"
                                ),
                                "replacement_teacher_id": st.column_config.TextColumn(
                                    "Replacement Teacher ID"
                                ),
                                "replacement_name": st.column_config.TextColumn(
                                    "Replacement Teacher Name"
                                ),
                                "replacement_category": st.column_config.TextColumn(
                                    "Replacement Category"
                                ),
                                "class": st.column_config.TextColumn("Class"),
                                "period": st.column_config.NumberColumn("Period"),
                                "status": st.column_config.TextColumn("Status"),
                                "match_quality": st.column_config.TextColumn(
                                    "Match Quality"
                                ),
                            },
                            hide_index=True,
                            use_container_width=True,
                        )
                    else:
                        st.info(
                            f"No arrangements found for {selected_date.strftime('%Y-%m-%d')}."
                        )

                else:
                    st.error("Failed to create manual arrangement. Database error.")
# test line to trigger git