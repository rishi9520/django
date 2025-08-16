
import streamlit as st
from datetime import datetime, date, time
import pandas as pd
# ⭐️⭐️⭐️ FIX: AutoMarker ko import karne ki ab yahan zaroorat nahi hai ⭐️⭐️⭐️
# from auto_marker import AutoMarker 
import data_manager


def render_admin_page(
    school_id, data_manager_instance
):  # Renamed data_manager arg to data_manager_module for clarity
    """
    Render admin control panel, fetching data from the database.
    """

    data_manager_instance = st.session_state.data_manager
    if data_manager_instance is None:
        st.error("DataManager instance not available. Please report this issue.")
        st.warning(
            "Admin Controls render failed: DataManager instance missing in session state."
        )
        return  # Cannot proceed without DataManager instance

    st.markdown(
        """
    <h1 style="display: flex; align-items: center;color:#1e3a8a;">
        <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" fill="currentColor" style="margin-right: 10px;" viewBox="0 0 24 24">
  <path d="M3 17v2h6v-2H3zM3 5v2h10V5H3zm10 16v-2h8v-2h-8v-2h-2v6h2zM7 9v2H3v2h4v2h2V9H7zm14 4v-2H11v2h10zm-6-4h2V7h4V5h-4V3h-2v6z"/>
</svg>
        Administrative Controls
    </h1>
    """,
        unsafe_allow_html=True,
    )
    tab1, tab2, tab3 = st.tabs(
        ["Auto-marking Settings", "User Management", "System Settings"]
    )

    # Inject Custom CSS for styling (Combined and Organized)
    st.markdown(
        """
    <style>
    /* Base Styles and Fonts - Ensure Poppins is available */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    body { font-family: 'Poppins', sans-serif; }

    /* Streamlit Element Overrides */
    /* Hide Streamlit footer and header */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    /* header {visibility: hidden;}  Commented out as it hides Streamlit's built-in header, which might be needed for deploy button etc. */

    /* Common Card/Container Styles */
    .st-emotion-cache-fk4zow { /* Target Streamlit's main content area */
        padding-top: 0px !important;
        padding-right: 1rem !important;
        padding-left: 1rem !important;
        padding-bottom: 1rem !important;
    }
    div[data-testid="stVerticalBlock"] > div > div { /* Target inner vertical blocks */
         # border: 1px solid red; /* For debugging layout */
         # margin-bottom: 10px; /* Add spacing between blocks */
    }


    /* Custom Button Styling (Applied to Streamlit buttons via class) */
    /* Streamlit default button classes can change, target by attributes if needed */
    /* Example: button[kind="primary"] or button[kind="secondary"] */

    button.st-emotion-cache-1r6p0uf { /* Target Primary buttons by example class */
        background: linear-gradient(90deg, #1E3A8A, #3B82F6) !important;
        color: white !important;
        border: none !important;
        border-radius: 5px !important;
        padding: 10px 20px !important;
        transition: all 0.3s ease !important;
        font-weight: 700 !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.15);
    }
     button.st-emotion-cache-1r6p0uf:hover {
        opacity: 0.9; transform: translateY(-2px); box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }

    button.st-emotion-cache-1r6p0uf[kind="secondary"] { /* Target Secondary buttons */
        background: linear-gradient(90deg, #ff6f61, #de425b) !important;
         color: white !important; border: none !important; font-weight: 700 !important;
         box-shadow: 0 2px 5px rgba(0,0,0,0.15);
     }
      button.st-emotion-cache-1r6p0uf[kind="secondary"]:hover {
        opacity: 0.9; transform: translateY(-2px); box-shadow: 0 4px 8px rgba(0,0,0,0.2);
     }


    /* Card Titles & Headers */
    .card-title h1, .card-title h2, .card-title h3 {
        font-weight: 700; color: #1E3A8A; /* Example color */
    }
     .card-title { /* Ensure this class is applied to the parent div */
         margin-top: 20px; margin-bottom: 20px;
     }

    /* Section Headers within tabs */
    h2, h3 {
         color: #2C3E50; /* Default color for h2/h3 */
         margin-top: 1.5rem; margin-bottom: 1rem;
    }
    h3 { font-size: 1.3rem; }


    /* Specific Section Headers (from your code) */
    .section-header {
        background: linear-gradient(90deg, #ff6f61, #de425b); color: white; padding: 12px 20px; border-radius: 10px;
        margin: 20px 0 15px 0; font-weight: 700; font-size:20px; display: flex; justify-content: space-between; align-items: center;
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    .section-header svg { fill: white !important; }

    /* Dataframes */
    div[data-testid="stDataFrame"] {
         margin-bottom: 20px;
    }


    /* Example style from Attendance Marking Form */
    .teacher-card { background: linear-gradient(135deg, #ffffff, #e3f2fd); border-radius: 16px; padding: 18px; margin: 15px 0; border: 1px solid rgba(209, 217, 230, 0.5); box-shadow: 0 6px 16px rgba(0,0,0,0.1); }


    </style>
    """,
        unsafe_allow_html=True,
    )

    # --- Tab Content ---

    with tab1:
        # --- Auto-Marked Absences Today (Updated for DB) ---
        st.markdown(
            """
    <h2 style="display: flex; align-items: center;">
        <svg xmlns="http://www.w3.org/2000/svg" width="35" height="35" fill="black" style="margin-right: 10px;" viewBox="0 0 24 24">
          <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4zm7 4h-6v-2h6v2z"/>
        </svg>
        Auto-Marked Absences Today
    </h2>
    """,
            unsafe_allow_html=True,
        )
        today = date.today()
        attendance_df = data_manager_instance.get_todays_attendance(school_id)
        if (
            not attendance_df.empty
            and "is_auto" in attendance_df.columns
            and "status" in attendance_df.columns
        ):
            try:
                attendance_df["is_auto"] = attendance_df["is_auto"].astype(bool)
            except Exception:
                st.warning(
                    "Could not convert 'is_auto' to boolean for auto-marked filter."
                )
                auto_marked = attendance_df[
                    (attendance_df["is_auto"].astype(str).str.lower() == "true")
                    & (attendance_df["status"] == "absent")
                ].copy()
            else:
                auto_marked = attendance_df[
                    (attendance_df["is_auto"] == True)
                    & (attendance_df["status"] == "absent")
                ].copy()

            if not auto_marked.empty:
                if "timestamp" in auto_marked.columns:
                    auto_marked["display_time"] = pd.to_datetime(
                        auto_marked["timestamp"]
                    ).dt.strftime("%I:%M %p")

                    display_cols = ["teacher_id", "display_time", "status"]
                    existing_display_cols = [
                        col for col in display_cols if col in auto_marked.columns
                    ]

                    st.dataframe(
                        auto_marked[existing_display_cols],
                        column_config={
                            "teacher_id": "Teacher ID",
                            "display_time": "Time",
                            "status": "Status",
                        },
                        hide_index=True,
                        use_container_width=True,
                    )
                else:
                    st.warning("Timestamp column missing in auto-marked data.")
            else:
                st.info("No auto-marked absences for today")
        else:
            st.info(
                "No attendance data available or columns missing for auto-marked filter."
            )

        st.divider()
        st.markdown(
            """
    <h3 style="display: flex; align-items: center;">
        <svg xmlns="http://www.w3.org/2000/svg" width="30" height="30" fill="currentColor" style="margin-right: 8px;" viewBox="0 0 24 24">
            <path d="M12 2C6.486 2 2 6.486 2 12s4.486 10 10 10 10-4.486 10-10S17.514 2 12 2zm0 18c-4.411 0-8-3.589-8-8s3.589-8 8-8 8 3.589 8 8-3.589 8-8 8z"/>
            <path d="M13 7h-2v5.414l3.293 3.293 1.414-1.414L13 11.586V7z"/>
            <path d="M14.5 14.5v3l3-1.5-3-1.5z"/>
        </svg>
        Auto-Absence Settings
    </h3>
    """,
            unsafe_allow_html=True,
        )
        
        # ⭐️⭐️⭐️ FIX: AutoMarker object ko session se safely get karein ⭐️⭐️⭐️
        automarker_instance = st.session_state.get("automarker")

        if automarker_instance:
            timing = automarker_instance.get_timing()  # AutoMarker method

            st.write(
                "The system will automatically mark all unmarked teachers as absent at the configured time."
            )

            col1, col2, col3 = st.columns([1, 1, 1])
            # Time settings
            with col1:
                display_hour = (
                    timing["hour"] if timing["hour"] <= 12 else timing["hour"] - 12
                )
                if display_hour == 0:  # 0 hour (midnight) should be 12 AM
                    display_hour = 12

                hour = st.number_input(
                    "Hour",
                    min_value=1,
                    max_value=12,
                    value=display_hour,
                    step=1,
                    key="automark_hour",
                )
            with col2:
                minute = st.number_input(
                    "Minute",
                    min_value=0,
                    max_value=59,
                    value=timing["minute"],
                    step=1,
                    key="automark_minute",
                )
            with col3:
                ampm = st.selectbox(
                    "AM/PM",
                    ["AM", "PM"],
                    index=(
                        0 if timing["hour"] < 12 else 1
                    ),  # Index 0 for AM (<12), 1 for PM (>=12)
                    key="automark_ampm",
                )

            save_hour = hour
            if ampm == "PM" and hour != 12:  # 12 PM is noon (hour 12)
                save_hour = hour + 12
            elif ampm == "AM" and hour == 12:  # 12 AM is midnight (hour 0)
                save_hour = 0

            enabled = st.checkbox(
                "Enable Auto-Marking",
                value=timing.get("enabled", True),
                key="automark_enabled",  # Use .get with default True
            )

            if st.button(
                "Save Timing", use_container_width=True, key="save_automark_timing"
            ):
                # Use the local variable 'automarker_instance'
                success = automarker_instance.set_timing(
                    save_hour, minute, enabled
                )
                if success:
                    st.success("Auto-mark timing updated!")
                else:
                    st.error("Failed to update auto-mark timing.")
                st.rerun()

            updated_timing = automarker_instance.get_timing()
            current_time_obj = datetime.strptime(
                f"{updated_timing['hour']:02d}:{updated_timing['minute']:02d}", "%H:%M"
            )
            display_time = current_time_obj.strftime("%I:%M %p")
            st.info(
                f"Current Setting: "
                f"{'🟢 Enabled' if updated_timing.get('enabled', True) else '🔴 Disabled'} at "  # Use .get with default
                f"{display_time}"
            )

        else:
            st.error("Auto-marking settings not available due to initialization error. Please check server logs.")

        st.divider()

        # Suspend/Resume buttons
        suspended_after_rerun = data_manager_instance.is_arrangement_suspended(
            school_id, today
        )

        if st.button(
            (
                "✋ Stop Today's Arrangements"
                if not suspended_after_rerun
                else "▶️ Resume Arrangements"
            ),
            type="primary" if not suspended_after_rerun else "secondary",
            use_container_width=True,
            key="toggle_arr_suspension",
        ):
            if suspended_after_rerun:
                success = data_manager_instance.resume_arrangements(school_id, today)
                if success:
                    st.success("Arrangements resumed for today!")
                else:
                    st.error("Failed to resume arrangements.")
            else:
                success = data_manager_instance.suspend_arrangements(school_id, today)
                if success:
                    st.success("Arrangements suspended for today!")
                else:
                    st.error("Failed to suspend arrangements.")

            st.rerun()

        if suspended_after_rerun:
            st.warning("⚠️ Arrangements are currently suspended for today")
        else:
            st.info("✅ Arrangements are active for today")

    with tab2:
        # --- User Management (Updated for DB) ---
        st.subheader("User Management")

        try:
            # Get all teachers using DataManager instance
            users_list = data_manager_instance.get_all_teachers(school_id)
            users_df = pd.DataFrame(users_list)

            st.write("All Registered Teachers:")

            filter_col1, filter_col2 = st.columns(2)

            # Ensure 'category' column exists before trying unique()
            categories = (
                ["All"] + sorted(users_df["category"].dropna().unique().tolist())
                if not users_df.empty and "category" in users_df.columns
                else ["All"]  # Provide default categories if column is missing
            )

            with filter_col1:
                filter_category = st.selectbox(
                    "Filter by Category", categories, key="user_filter_category"
                )

            with filter_col2:
                search_term = st.text_input(
                    "Search by Name or ID", key="user_search_term"
                )

            filtered_df = users_df.copy()

            if filter_category != "All":
                if "category" in filtered_df.columns:  # Check again before filtering
                    filtered_df = filtered_df[
                        filtered_df["category"].astype(str).str.lower()
                        == filter_category.lower()
                    ]
                else:
                    st.warning("Category column not available for filtering.")
                    filtered_df = (
                        pd.DataFrame()
                    )  # Show empty if filtering by category fails

            if search_term:
                name_match = pd.Series(
                    [False] * len(filtered_df), index=filtered_df.index
                )  # Ensure index alignment
                id_match = pd.Series(
                    [False] * len(filtered_df), index=filtered_df.index
                )  # Ensure index alignment

                if "name" in filtered_df.columns:
                    name_match = (
                        filtered_df["name"]
                        .astype(str)
                        .str.contains(search_term, case=False, na=False)
                    )

                if "teacher_id" in filtered_df.columns:
                    id_match = (
                        filtered_df["teacher_id"]
                        .astype(str)
                        .str.contains(search_term, case=False, na=False)
                    )
                # Apply filter only if either name or id match series were actually created
                if not name_match.empty or not id_match.empty:
                    # Combine matches - handle cases where one match series is empty
                    if name_match.empty:
                        filtered_df = filtered_df[id_match]
                    elif id_match.empty:
                        filtered_df = filtered_df[name_match]
                    else:
                        filtered_df = filtered_df[name_match | id_match]
                else:
                    # If both match series are empty (e.g., no name/teacher_id columns), don't filter
                    pass  # Keep filtered_df as is

            if not filtered_df.empty:
                display_cols = filtered_df.columns.tolist()
                if "password" in display_cols:  # Remove password column if it exists
                    display_cols.remove("password")
                if (
                    "id" in display_cols
                ):  # Remove primary key 'id' if it exists and isn't needed for display
                    try:
                        display_cols.remove("id")
                    except ValueError:
                        pass  # Ignore if 'id' wasn't there

                st.dataframe(
                    filtered_df[display_cols], use_container_width=True, hide_index=True
                )
            else:
                st.info("No users match the selected filters.")

        except Exception as e:
            st.error(f"Error loading users from database: {str(e)}")
            st.warning(f"Error loading users for Admin tab2: {e}")

    with tab3:
        # --- System Settings (Updated for DB) ---
        st.subheader("System Settings")

        # Suspended dates management
        st.write("Manage Suspended Arrangement Dates:")

        try:
            # Get suspended dates using DataManager instance
            suspended_dates_df = data_manager_instance.get_suspended_dates(school_id)

            if not suspended_dates_df.empty and "date" in suspended_dates_df.columns:
                st.write("Current suspended dates:")

                # Ensure date column is date objects and sort
                try:
                    # Handle potential mixed types or errors during conversion robustly
                    suspended_dates_df["date"] = pd.to_datetime(
                        suspended_dates_df["date"], errors="coerce"
                    ).dt.date
                    suspended_dates_df = suspended_dates_df.dropna(
                        subset=["date"]
                    )  # Drop rows where date conversion failed
                    suspended_dates_df = suspended_dates_df.sort_values(by="date")
                except Exception as e:
                    st.warning(f"Could not sort suspended dates: {e}")

                if not suspended_dates_df.empty:
                    for (
                        index,
                        row,
                    ) in suspended_dates_df.iterrows():
                        col1, col2 = st.columns([3, 1])

                        date_to_display = row["date"]
                        # Ensure it's a date object or convertible for display
                        if isinstance(date_to_display, date):
                            date_to_display_str = date_to_display.strftime("%Y-%m-%d")
                        else:
                            # Fallback in case conversion partially failed
                            date_to_display_str = str(date_to_display)

                        with col1:
                            st.write(date_to_display_str)

                        with col2:
                            # Use a unique key for each button based on the date string
                            if st.button(
                                "Remove", key=f"remove_suspended_{date_to_display_str}"
                            ):
                                # Resume arrangements using DataManager instance
                                success = data_manager_instance.resume_arrangements(
                                    school_id, date_to_display_str
                                )
                                if success:
                                    st.success(
                                        f"Removed suspension for {date_to_display_str}"
                                    )
                                else:
                                    st.error(
                                        f"Failed to remove suspension for {date_to_display_str}"
                                    )
                                st.rerun()  # Rerun after removal

                else:
                    st.info("No valid suspended dates to display.")

            else:
                st.info("No dates are currently suspended.")

        except Exception as e:
            st.error(f"Error loading suspended dates from database: {str(e)}")
            st.warning(f"Error loading suspended dates for Admin tab3: {e}")

        st.write("Add a new suspended date:")

        add_suspended_date = st.date_input(
            "Select Date to Suspend", key="add_suspended_date_input"
        )

        if st.button(
            "Suspend Arrangements for Selected Date",
            use_container_width=True,
            key="suspend_date_button",
        ):
            date_str = add_suspended_date.strftime("%Y-%m-%d")

            # Check if already suspended using DataManager instance
            if data_manager_instance.is_arrangement_suspended(school_id, date_str):
                st.warning(f"Arrangements are already suspended for {date_str}")
            else:
                # Suspend using DataManager instance
                success = data_manager_instance.suspend_arrangements(
                    school_id, date_str
                )
                if success:
                    st.success(f"Arrangements suspended for {date_str}")
                else:
                    st.error(f"Failed to suspend arrangements for {date_str}")
                st.rerun()  # Rerun after suspension

        # --- Database backup/export (Updated for DB) ---
        st.divider()
        st.subheader("Data Export")

        export_type = st.selectbox(
            "Select Data to Export",
            ["Attendance Records", "Teacher Information", "Arrangements"],
            key="export_data_type",
        )

        if st.button("Export Data", use_container_width=True, key="export_data_button"):
            try:
                current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
                df_to_export = pd.DataFrame()
                filename = f"export_{current_time}.csv"

                if export_type == "Attendance Records":
                    # Check if get_all_attendance method exists in your DataManager
                    if hasattr(data_manager_instance, "get_all_attendance"):
                        df_to_export = data_manager_instance.get_all_attendance(
                            school_id
                        )
                        filename = f"attendance_export_{current_time}.csv"
                    else:
                        st.error("DataManager method 'get_all_attendance' not found.")
                        st.warning(
                            "Data export failed: get_all_attendance method missing."
                        )
                        df_to_export = pd.DataFrame()  # Ensure empty DF on error

                elif export_type == "Teacher Information":
                    # get_all_teachers exists
                    df_to_export = data_manager_instance.get_all_teachers(school_id)
                    # Convert list of dicts to DataFrame explicitly if get_all_teachers returns list
                    if isinstance(df_to_export, list):
                        df_to_export = pd.DataFrame(df_to_export)
                    if "password" in df_to_export.columns:
                        df_to_export = df_to_export.drop(columns=["password"])
                    # Remove 'id' column if it exists and is not needed for export
                    if "id" in df_to_export.columns:
                        try:
                            df_to_export = df_to_export.drop(columns=["id"])
                        except ValueError:
                            pass  # Ignore if 'id' wasn't there
                    filename = f"teachers_export_{current_time}.csv"

                elif export_type == "Arrangements":
                    # Check if get_all_arrangements method exists
                    if hasattr(data_manager_instance, "get_all_arrangements"):
                        df_to_export = data_manager_instance.get_all_arrangements(
                            school_id
                        )
                        filename = f"arrangements_export_{current_time}.csv"
                    else:
                        st.error("DataManager method 'get_all_arrangements' not found.")
                        st.warning(
                            "Data export failed: get_all_arrangements method missing."
                        )
                        df_to_export = pd.DataFrame()  # Ensure empty DF on error

                if not df_to_export.empty:
                    csv_string = df_to_export.to_csv(index=False).encode("utf-8")

                    # Use a more robust key for download button
                    download_key = f"download_button_{export_type}_{current_time}_{len(csv_string)}"  # Add size to key

                    st.download_button(
                        label="Download CSV File",
                        data=csv_string,
                        file_name=filename,
                        mime="text/csv",
                        key=download_key,
                    )
                else:
                    st.info(f"No data available for export type: {export_type}")

            except Exception as e:
                st.error(f"Data Export failed: {str(e)}")
                st.warning(f"Data export failed for {export_type} in Admin tab3: {e}")