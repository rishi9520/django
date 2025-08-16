import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
import plotly.express as px


def render_reports_page(school_id, data_manager_module):  # Renamed for clarity
    """
    Render the reports page, fetching data from the database.
    """
    data_manager_instance = st.session_state.data_manager

    # Check if DataManager instance is available
    if data_manager_instance is None:
        st.error("DataManager instance not available. Please report this issue.")
        return  # Cannot proceed without DataManager instance

    st.markdown(
        """
        <div style="margin-top: 20px; margin-bottom: 30px;color:#1e3a8a;">
            <h1 style="display: flex; align-items: center; gap: 10px;">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 3v18M3 12h18M3 6h18M3 18h18"/>
                </svg>
                Reports
            </h1>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <h3 style="display: flex; align-items: center; gap: 10px; color: #2C3E50;">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
                <line x1="16" y1="2" x2="16" y2="6"/>
                <line x1="8" y1="2" x2="8" y2="6"/>
                <line x1="3" y1="10" x2="21" y2="10"/>
            </svg>
            Select Date Range
        </h3>
    """,
        unsafe_allow_html=True,
    )

    # Date range selection (Keep)
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "Start Date", date.today() - timedelta(days=7), key="report_start_date"
        )  # Add key
    with col2:
        end_date = st.date_input(
            "End Date", date.today(), key="report_end_date"
        )  # Add key

    if end_date < start_date:
        st.error("🚨End date should be after start date")
        return

    # Load attendance data for the selected date range from DB
    try:
        # data_manager_instance.get_attendance_report needs (connection, school_id, start_date, end_date)
        attendance_df = data_manager_instance.get_attendance_report(
            school_id, start_date=start_date, end_date=end_date
        )

        # Convert date column to date objects if needed by downstream logic (Pandas operation)
        # It might already be date objects if read_query handles it, but ensure robustness
        if not attendance_df.empty and "date" in attendance_df.columns:
            try:
                attendance_df["date"] = pd.to_datetime(attendance_df["date"]).dt.date
            except Exception:
                print("Failed to convert attendance date column to date objects.")
                # Continue with original column if conversion fails

        # The entire fetched data IS the filtered data by date range
        filtered_df = attendance_df.copy()  # Use copy to avoid SettingWithCopyWarning

    except Exception as e:
        st.error(f"Error loading attendance data for reports: {str(e)}")
        st.error(f"Error loading attendance data for reports: {e}")
        return  # Stop rendering report if data loading fails

    # Fetch all teachers data for analysis and merging (Needed in tabs 2 and 3)
    try:
        # data_manager_instance.get_all_teachers needs (connection, school_id)
        all_teachers_list = data_manager_instance.get_all_teachers(school_id)
        # Convert list to DataFrame for easier merging and processing
        teachers_df = pd.DataFrame(all_teachers_list)

        # Extract teacher IDs and names for filters and lookups
        teacher_ids = (
            teachers_df["teacher_id"].tolist()
            if not teachers_df.empty and "teacher_id" in teachers_df.columns
            else []
        )
        teacher_names = {
            t.get("teacher_id"): t.get("name") for t in all_teachers_list
        }  # Map ID to name

    except Exception as e:
        st.error(f"Error loading teacher data for reports: {str(e)}")
        # Continue, but teacher data will be empty
        teachers_df = pd.DataFrame()
        teacher_ids = []
        teacher_names = {}

    # Create tabs after filtering and fetching data
    tab1, tab2, tab3 = st.tabs(["Attendance Summary", "Teacher Analysis", "Raw Data"])

    with tab1:
        # --- Attendance Summary (Updated) ---
        st.markdown(
            """
        <h3 style="display: flex; align-items: center; gap: 10px; color: #2C3E50;">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
                <line x1="16" y1="2" x2="16" y2="6"/>
                <line x1="8" y1="2" x2="8" y2="6"/>
                <line x1="3" y1="10" x2="21" y2="10"/>
            </svg>
            Attendance Summary
        </h3>
        """,
            unsafe_allow_html=True,
        )
        # Set default values in case filtered_df is empty
        total_records = 0
        present_count = 0
        absent_count = 0
        auto_marked = 0

        if not filtered_df.empty:
            # Summary statistics (Pandas logic remains)
            total_records = len(filtered_df)

            if "status" in filtered_df.columns:
                present_count = len(filtered_df[filtered_df["status"] == "present"])
                absent_count = len(filtered_df[filtered_df["status"] == "absent"])
            else:
                print("Status column missing in filtered_df for summary.")

            if "is_auto" in filtered_df.columns:
                # Ensure 'is_auto' is boolean before filtering
                try:
                    filtered_df["is_auto"] = filtered_df["is_auto"].astype(bool)
                    auto_marked = len(filtered_df[filtered_df["is_auto"] == True])
                except Exception:
                    print("Could not convert 'is_auto' to boolean for summary filter.")
                    # Fallback filter if conversion fails
                    auto_marked = len(
                        filtered_df[
                            filtered_df["is_auto"].astype(str).str.lower() == "true"
                        ]
                    )

            else:
                print("Is_auto column missing in filtered_df for summary.")

            # Custom CSS for stat cards (Keep)
            st.markdown(
                """
        <style>
        /* ... (Keep your stat card styles here) ... */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        .stat-card {
            background: linear-gradient(135deg, #ffffff, #f8f9fa); border-radius: 20px; padding: 25px; flex: 1; min-width: 200px; box-shadow: 0 8px 30px rgba(0,0,0,0.08); border: 1px solid rgba(0,0,0,0.06); position: relative; overflow: hidden; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); backdrop-filter: blur(10px); margin: 10px; height: 160px;
        }
        .stat-card:hover { transform: translateY(-5px) scale(1.02); box-shadow: 0 12px 40px rgba(0,0,0,0.12); }
        .stat-card::before { content: ''; position: absolute; inset: 0; border-radius: 20px; padding: 2px; background: linear-gradient(90deg, rgba(255,255,255,0.2), rgba(255,255,255,0.6)); -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0); mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0); -webkit-mask-composite: xor; mask-composite: exclude; }
        .stat-number { font-size: 36px; font-weight: 800; margin: 10px 0; font-family: 'Inter', system-ui, sans-serif; background: linear-gradient(45deg, #333, #666); -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; }
        .stat-label { color: #666; font-size: 15px; font-weight: 600; text-transform: uppercase; letter-spacing: 1.2px; margin-bottom: 20px; font-family: 'Inter', system-ui, sans-serif; }
        .stat-trend { position: absolute; bottom: 20px; right: 20px; width: 60px; height: 30px; opacity: 0.2; } .stat-trend path { stroke: currentColor; stroke-width: 2; fill: none; }
        .stat-icon { position: absolute; bottom: 20px; right: 20px; width: 30px; height: 30px; }
        </style>
        """,
                unsafe_allow_html=True,
            )

            # Display metrics in new design (Keep)
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.markdown(
                    f"""
                <div class="stat-card">
                    <div class="stat-number">{total_records}</div>
                    <div class="stat-label">Total Records</div>
                    <div class="stat-icon">
                        <svg viewBox="0 0 24 24" width="24" height="24"><rect x="2" y="13" width="4" height="8" fill="#1976D2"/><rect x="8" y="9" width="4" height="12" fill="#2196F3"/><rect x="14" y="5" width="4" height="16" fill="#64B5F6"/><rect x="20" y="2" width="4" height="19" fill="#90CAF9"/></svg>
                    </div>
                </div>
            """,
                    unsafe_allow_html=True,
                )

            with col2:
                st.markdown(
                    f"""
                <div class="stat-card">
                    <div class="stat-number">{present_count}</div>
                    <div class="stat-label">Present Records</div>
                    <div class="stat-icon">
                        <svg viewBox="0 0 24 24" width="24" height="24"><rect x="2" y="13" width="4" height="8" fill="#388E3C"/><rect x="8" y="9" width="4" height="12" fill="#4CAF50"/><rect x="14" y="5" width="4" height="16" fill="#81C784"/><rect x="20" y="2" width="4" height="19" fill="#A5D6A7"/></svg>
                    </div>
                </div>
            """,
                    unsafe_allow_html=True,
                )

            with col3:
                st.markdown(
                    f"""
                <div class="stat-card">
                    <div class="stat-number">{absent_count}</div>
                    <div class="stat-label">Absent Records</div> 
                    <div class="stat-icon">
                        <svg viewBox="0 0 24 24" width="24" height="24"><rect x="2" y="13" width="4" height="8" fill="#C62828"/><rect x="8" y="9" width="4" height="12" fill="#F44336"/><rect x="14" y="5" width="4" height="16" fill="#E57373"/><rect x="20" y="2" width="4" height="19" fill="#FFCDD2"/></svg>
                    </div>
                </div>
            """,
                    unsafe_allow_html=True,
                )

            with col4:
                st.markdown(
                    f"""
                <div class="stat-card">
                    <div class="stat-number">{auto_marked}</div>
                    <div class="stat-label">Auto Marked Records</div> 
                    <div class="stat-icon">
                        <svg viewBox="0 0 24 24" width="24" height="24"><rect x="2" y="13" width="4" height="8" fill="#6A1B9A"/><rect x="8" y="9" width="4" height="12" fill="#9C27B0"/><rect x="14" y="5" width="4" height="16" fill="#BA68C8"/><rect x="20" y="2" width="4" height="19" fill="#E1BEE7"/></svg>
                    </div>
                </div>
            """,
                    unsafe_allow_html=True,
                )

            st.divider()
            # 🔹 Two-column layout for tables (Keep)
            col1_tab1, col2_tab1 = st.columns([1, 1])  # Use distinct variable names

            # 🔹 LEFT: Detailed Records (Updated)
            with col1_tab1:
                if not filtered_df.empty:
                    st.markdown(
                        """
                <h3 style="display: flex; align-items: center; gap: 10px; color: #2C3E50;">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                        <polyline points="14 2 14 8 20 8"/>
                        <line x1="16" y1="13" x2="8" y2="13"/>
                        <line x1="16" y1="17" x2="8" y2="17"/>
                        <polyline points="10 9 9 9 8 9"/>
                    </svg>
                    Detailed Records
                </h3>
            """,
                        unsafe_allow_html=True,
                    )
                    st.dataframe(
                        filtered_df,  # Display the date-filtered data directly
                        column_config={  # Ensure column names match attendance table in DB
                            "teacher_id": st.column_config.Column(
                                "Teacher ID", help="Unique identifier for each teacher"
                            ),
                            "date": st.column_config.DateColumn("📅Date"),
                            "status": st.column_config.Column("📌Status"),
                            "timestamp": st.column_config.TimeColumn("⏰Time"),
                            "is_auto": st.column_config.CheckboxColumn("🤖Auto Marked"),
                            "id": None,  # Hide internal ID
                        },
                        hide_index=True,
                        use_container_width=True,  # Use container width
                    )
                else:
                    st.info("⚠️No records found for the selected date range")

            # 🔹 RIGHT: Recent Activity (Updated)
            with col2_tab1:
                try:
                    st.markdown(
                        """
                <h3 style="display: flex; align-items: center; gap: 10px; color: #2C3E50;">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/>
                    </svg>
                    Recent Activity
                </h3>
            """,
                        unsafe_allow_html=True,
                    )
                    # Fetch recent attendance records from DB (e.g., last 20)
                    # data_manager_instance.get_recent_attendance needs (connection, school_id, limit)
                    recent_records = data_manager_instance.get_recent_attendance(
                        school_id, limit=20
                    )

                    if not recent_records.empty:
                        # Convert timestamp to display format (Pandas logic remains)
                        # Ensure 'timestamp' column exists before converting
                        if "timestamp" in recent_records.columns:
                            recent_records["display_time"] = pd.to_datetime(
                                recent_records["timestamp"]
                            ).dt.strftime("%I:%M %p")

                            # Display dataframe (Select relevant columns)
                            display_cols = [
                                "date",
                                "teacher_id",
                                "status",
                                "display_time",
                                "is_auto",
                            ]
                            existing_display_cols = [
                                col
                                for col in display_cols
                                if col in recent_records.columns
                            ]

                            st.dataframe(
                                recent_records[existing_display_cols],
                                column_config={  # Ensure column names match the DataFrame columns
                                    "date": "📅Date",
                                    "teacher_id": "👨‍🏫Teacher ID",
                                    "status": "📌Status",
                                    "display_time": "⏰Time",
                                    "is_auto": "🤖Auto Marked",
                                },
                                hide_index=True,
                                use_container_width=True,  # Use container width
                            )
                        else:
                            st("Timestamp column missing in recent records data.")
                    else:
                        st.info("No recent activity")

                except Exception as e:
                    st.error(f"Error loading recent attendance data: {str(e)}")
                    st.error(
                        f"Error loading recent attendance data for tab1 right column: {e}"
                    )

            # 🔹 Attendance trend chart (Updated)
            st.markdown(
                """
            <h3 style="display: flex; align-items: center; gap: 10px; color: #2C3E50;">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M3 3v18h18"/>
                    <path d="M18.7 8l-5.1 5.2-2.8-2.7L7 14.3"/>
                </svg>
                Attendance Trend
            </h3>
        """,
                unsafe_allow_html=True,
            )
            # Use the date-filtered attendance data for the trend chart
            if (
                not filtered_df.empty
                and "date" in filtered_df.columns
                and "status" in filtered_df.columns
            ):
                try:
                    # Group by date and status and unstack (Pandas logic remains)
                    daily_attendance = (
                        filtered_df.groupby(["date", "status"])
                        .size()
                        .unstack(fill_value=0)
                    )

                    # Create Plotly line chart (Plotly logic remains)
                    fig = px.line(daily_attendance, title="Daily Attendance Trend")
                    fig.update_layout(
                        margin=dict(l=0, r=0, t=40, b=0), height=350
                    )  # Keep layout
                    st.plotly_chart(fig, use_container_width=True)

                except Exception as e:
                    st.error(f"Error creating attendance trend chart: {str(e)}")
                    st.error(f"Error creating attendance trend chart: {e}")
            else:
                st.info("No data available for attendance trend chart.")

    with tab2:
        # --- Teacher Analysis (Updated) ---
        st.subheader("Teacher Analysis")

        if teachers_df.empty:
            st.info("No teacher data available for analysis.")
        elif filtered_df.empty:
            st.info("No attendance data available for the selected date range.")
        else:
            # --- MERGE LOGIC START ---
            if "teacher_id" not in filtered_df.columns:
                st.error(
                    "Internal Error: 'teacher_id' column missing in attendance data."
                )
            elif "teacher_id" not in teachers_df.columns:
                st.error(
                    "Internal Error: 'teacher_id' column missing in teachers list."
                )
            else:
                filtered_df_with_names = pd.merge(
                    filtered_df,
                    teachers_df[["teacher_id", "name"]],
                    on="teacher_id",
                    how="left",
                )

                if "name" in filtered_df_with_names.columns:
                    # 'Unknown' naam ke saath teacher_id bhi jod do taaki pehchan ho sake
                    filtered_df_with_names["name"] = filtered_df_with_names.apply(
                        lambda row: (
                            f"Unknown ({row['teacher_id']})"
                            if pd.isna(row["name"])
                            else row["name"]
                        ),
                        axis=1,
                    )
                else:
                    filtered_df_with_names["name"] = filtered_df_with_names[
                        "teacher_id"
                    ]
                # --- MERGE LOGIC END ---

                if "status" in filtered_df_with_names.columns:
                    teacher_summary = (
                        filtered_df_with_names.groupby(["teacher_id", "name", "status"])
                        .size()
                        .reset_index(name="count")
                    )

                    teacher_pivot = teacher_summary.pivot_table(
                        index=["teacher_id", "name"],
                        columns="status",
                        values="count",
                    ).reset_index()

                    if "present" not in teacher_pivot.columns:
                        teacher_pivot["present"] = 0
                    if "absent" not in teacher_pivot.columns:
                        teacher_pivot["absent"] = 0
                    teacher_pivot = teacher_pivot.fillna(0)

                    teacher_pivot["total"] = (
                        teacher_pivot["present"] + teacher_pivot["absent"]
                    )

                    teacher_pivot["attendance_rate"] = 0.0
                    non_zero_total_mask = teacher_pivot["total"] > 0
                    teacher_pivot.loc[non_zero_total_mask, "attendance_rate"] = (
                        (
                            teacher_pivot.loc[non_zero_total_mask, "present"]
                            / teacher_pivot.loc[non_zero_total_mask, "total"]
                        )
                        * 100
                    ).round(1)

                    teacher_pivot = teacher_pivot.sort_values(
                        "attendance_rate", ascending=False
                    )

                    # --- CHART KO BEHTAR BANANE KA CODE START ---
                    st.markdown("#### Attendance Rate by Teacher")
                    fig3 = px.bar(
                        teacher_pivot,
                        x="name",
                        y="attendance_rate",
                        labels={
                            "name": "Teacher Name",
                            "attendance_rate": "Attendance Rate (%)",
                        },
                        color="attendance_rate",
                        color_continuous_scale=["#d32f2f", "#ffeb3b", "#2e7d32"],
                        range_color=[0, 100],
                        text_auto=".1f",
                        height=500,
                    )
                    fig3.update_traces(textangle=0, textposition="outside")
                    fig3.update_layout(
                        xaxis_title="Teacher",
                        yaxis_title="Attendance Rate (%)",
                        xaxis_tickangle=-45,
                        margin=dict(l=0, r=0, t=40, b=150),
                    )
                    st.plotly_chart(fig3, use_container_width=True)
                    # --- CHART KO BEHTAR BANANE KA CODE END ---

                    # --- TABLE KO BEHTAR BANANE KA CODE START ---
                    st.markdown("#### Teacher Attendance Details")
                    display_df = teacher_pivot.rename(
                        columns={
                            "name": "Teacher",
                            "present": "Present Days",
                            "absent": "Absent Days",
                            "total": "Total Records",
                            "attendance_rate": "Attendance Rate (%)",
                        }
                    )
                    st.dataframe(
                        display_df[
                            [
                                "Teacher",
                                "Present Days",
                                "Absent Days",
                                "Total Records",
                                "Attendance Rate (%)",
                            ]
                        ],
                        column_config={
                            "Attendance Rate (%)": st.column_config.ProgressColumn(
                                "Attendance Rate",
                                help="Teacher's attendance percentage in the selected date range.",
                                format="%.1f%%",
                                min_value=0,
                                max_value=100,
                            ),
                        },
                        use_container_width=True,
                        hide_index=True,
                    )
                    # --- TABLE KO BEHTAR BANANE KA CODE END ---

                    # --- NAYA FEATURE: TOP/BOTTOM PERFORMERS ---
                    st.divider()
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("##### 🏆 Top 5 Punctual Teachers")
                        top_5 = teacher_pivot.sort_values(
                            "attendance_rate", ascending=False
                        ).head(5)
                        st.dataframe(
                            top_5[["name", "attendance_rate"]].rename(
                                columns={
                                    "name": "Teacher",
                                    "attendance_rate": "Attendance (%)",
                                }
                            ),
                            hide_index=True,
                            use_container_width=True,
                        )
                    with col2:
                        st.markdown("##### ⚠️ Top 5 Most Absent Teachers")
                        bottom_5 = teacher_pivot.sort_values(
                            "absent", ascending=False
                        ).head(5)
                        st.dataframe(
                            bottom_5[["name", "absent"]].rename(
                                columns={"name": "Teacher", "absent": "Absent Days"}
                            ),
                            hide_index=True,
                            use_container_width=True,
                        )
                    # --- NAYA FEATURE END ---

                else:
                    st.info("Required 'status' column missing in data for analysis.")
    with tab3:
        # --- Raw Attendance Data (Updated) ---
        st.subheader("Raw Attendance Data")

        # Display the raw data with filters (Filters based on filtered_df)
        filter_col1_tab3, filter_col2_tab3 = st.columns(
            2
        )  # Use distinct variable names

        with filter_col1_tab3:
            status_filter = st.selectbox(
                "Filter by Status",
                ["All", "present", "absent"],
                key="raw_status_filter",  # Add key
            )

        # Prepare teacher filter options using fetched teacher names and IDs
        teacher_filter_options = ["All"] + [
            f"{name} ({tid})"
            for tid, name in teacher_names.items()
            if name is not None  # Handle cases where name might be None
        ]
        # Add IDs without names if name is None but ID exists
        for tid in teacher_ids:
            if tid not in teacher_names and tid not in teacher_filter_options:
                teacher_filter_options.append(f"Unknown ({tid})")
        # Sort options alphabetically, keeping "All" first
        teacher_filter_options[1:] = sorted(teacher_filter_options[1:])

        with filter_col2_tab3:
            teacher_filter = st.selectbox(
                "Filter by Teacher",
                teacher_filter_options,
                key="raw_teacher_filter",  # Add key
            )

        # Apply additional filters to the already date-filtered data (filtered_df)
        display_df_raw = filtered_df.copy()  # Start with the date-filtered data

        if status_filter != "All":
            if "status" in display_df_raw.columns:
                display_df_raw = display_df_raw[
                    display_df_raw["status"] == status_filter
                ]
            else:
                print("Status column missing for raw data status filter.")

        if teacher_filter != "All":
            # Extract teacher ID from the selected filter string "Name (ID)" or "Unknown (ID)"
            try:
                teacher_id_to_filter = (
                    teacher_filter.split("(")[-1].replace(")", "").strip()
                )
                if "teacher_id" in display_df_raw.columns:
                    display_df_raw = display_df_raw[
                        display_df_raw["teacher_id"] == teacher_id_to_filter
                    ]
                else:
                    print("Teacher_id column missing for raw data teacher filter.")
            except Exception:
                print(f"Could not parse teacher ID from filter: {teacher_filter}")
                display_df_raw = (
                    pd.DataFrame()
                )  # Filter results in empty if parsing fails

        # Sort by date and timestamp (Pandas logic)
        if not display_df_raw.empty and "timestamp" in display_df_raw.columns:
            display_df_raw = display_df_raw.sort_values("timestamp", ascending=False)
        else:
            print("Timestamp column missing or data empty for raw data sort.")

        # Replace teacher_id with teacher name where possible for display
        if not display_df_raw.empty and "teacher_id" in display_df_raw.columns:
            # Merge with teacher names DataFrame
            if (
                not teachers_df.empty
                and "teacher_id" in teachers_df.columns
                and "name" in teachers_df.columns
            ):
                # Add 'name' column by merging
                display_df_raw = pd.merge(
                    display_df_raw,
                    teachers_df[["teacher_id", "name"]],
                    on="teacher_id",
                    how="left",
                )
                # Rename the new 'name' column for display
                display_df_raw.rename(columns={"name": "Teacher"}, inplace=True)
                # Reorder columns to put 'Teacher' next to 'Teacher ID' or instead of it
                # Let's put 'Teacher' instead of 'Teacher ID' in the final display
                display_df_raw["Teacher ID"] = display_df_raw[
                    "teacher_id"
                ]  # Keep original ID in case needed

            else:
                # If teacher names DataFrame is empty or missing columns, just use teacher_id
                display_df_raw["Teacher"] = display_df_raw[
                    "teacher_id"
                ]  # Use ID as name fallback

        # Select columns to display and rename (Keep)
        # Ensure required columns exist before selecting
        final_display_cols = []
        col_rename_map = {}

        # Define desired final columns and their source/rename
        desired_final_cols = [
            "Date",
            "Teacher",
            "Teacher ID",
            "Status",
            "Timestamp",
            "Auto-marked",
        ]
        source_cols_map = {
            "Date": "date",
            "Teacher": "Teacher",  # This column is created above
            "Teacher ID": "teacher_id",  # Or "Teacher ID" if renamed earlier
            "Status": "status",
            "Timestamp": "timestamp",
            "Auto-marked": "is_auto",
        }

        for final_name, source_name in source_cols_map.items():
            if source_name in display_df_raw.columns:
                final_display_cols.append(source_name)
                col_rename_map[source_name] = final_name
            elif (
                final_name in display_df_raw.columns
            ):  # Check if a column was already renamed like 'Teacher'
                final_display_cols.append(final_name)  # Use the already renamed column
                # No rename needed in this case as it's already the final name
            else:
                print(
                    f"Source column '{source_name}' not found for raw data display as '{final_name}'."
                )

        # Handle renaming and selection based on available columns
        if final_display_cols:
            renamed_df = display_df_raw[final_display_cols].rename(
                columns=col_rename_map
            )
            # Ensure boolean column ('Auto-marked') is displayed nicely if it exists
            if "Auto-marked" in renamed_df.columns:
                renamed_df["Auto-marked"] = renamed_df["Auto-marked"].map(
                    {True: "✅", False: "❌"}
                )  # Display check/cross marks
        else:
            renamed_df = pd.DataFrame()  # Empty if no columns to display

        if not renamed_df.empty:
            st.dataframe(
                renamed_df, use_container_width=True, hide_index=True
            )  # Hide index
        else:
            st.info("No raw attendance data available based on selected filters.")

        # Export option (Updated for DB)
        st.divider()  # Add a divider before export button
        if st.button(
            "Export Filtered Data", use_container_width=True, key="raw_export_button"
        ):  # Add key
            try:
                # Export the *filtered* data (renamed_df)
                if not renamed_df.empty:
                    csv_string = renamed_df.to_csv(index=False).encode("utf-8")
                    filename = f"raw_attendance_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

                    st.download_button(
                        label="Download CSV File",  # Changed label slightly
                        data=csv_string,
                        file_name=filename,
                        mime="text/csv",
                        key=f"raw_download_button_{datetime.now().strftime('%Y%m%d%H%M%S')}",  # Ensure unique key
                    )
                else:
                    st.info("No data to export.")

            except Exception as e:
                st.error(f"Export failed: {str(e)}")
                st.error(f"Raw data export failed: {e}")


# --- END OF FILE reports.py ---
# test line to trigger git