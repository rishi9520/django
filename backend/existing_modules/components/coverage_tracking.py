import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os


def render_coverage_tracking_page(school_id, data_manager):
    """Render the class coverage tracking page"""
    st.markdown(
        """<div style="margin-right: 5px;color:#1e3a8a;"class="card-title">
           <H1> <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" fill="currentColor" viewBox="0 0 24 24" style="margin-right: 10px;">
                <path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"/>
                <path d="M12 12v.01M12 16v.01M12 8v.01M16 12v.01M16 16v.01M16 8v.01M8 12v.01M8 16v.01M8 8v.01"/>
            </svg>
            <span>Class Coverage Tracking</span></h!>
        </div>""",
        unsafe_allow_html=True,
    )

    # Create tabs for different sections
    tab1, tab2, tab3 = st.tabs(
        ["Coverage Dashboard", "Record Coverage", "Historical Analysis"]
    )

    # Function to load coverage data
    def load_coverage_data():
        if os.path.exists("coverage_tracking.csv"):
            try:
                df = pd.read_csv("coverage_tracking.csv")
                # Convert date column to datetime if it exists
                if "date" in df.columns:
                    df["date"] = pd.to_datetime(df["date"])
                return df
            except Exception as e:
                st.error(f"Error loading coverage data: {str(e)}")
                return pd.DataFrame()
        else:
            # Create default structure if file doesn't exist
            df = pd.DataFrame(
                {
                    "date": [],
                    "period": [],
                    "class_name": [],
                    "section": [],
                    "subject": [],
                    "original_teacher_id": [],
                    "replacement_teacher_id": [],
                    "status": [],
                    "notes": [],
                }
            )
            df.to_csv("coverage_tracking.csv", index=False)
            return df

    # Function to save coverage data
    def save_coverage_data(df):
        df.to_csv("coverage_tracking.csv", index=False)

    # Load coverage data
    coverage_df = load_coverage_data()

    # Tab 1: Coverage Dashboard
    with tab1:
        st.markdown("### Class Coverage Overview")

        # Date filter
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "Start Date", value=(datetime.now() - timedelta(days=7)).date()
            )
        with col2:
            end_date = st.date_input("End Date", value=datetime.now().date())

        # Filter by date range
        filtered_df = coverage_df.copy()
        if not filtered_df.empty and "date" in filtered_df.columns:
            filtered_df = filtered_df[
                (filtered_df["date"].dt.date >= start_date)
                & (filtered_df["date"].dt.date <= end_date)
            ]

        if filtered_df.empty:
            st.info("No coverage data available for the selected date range.")
        else:
            # Summary statistics
            covered_count = len(filtered_df[filtered_df["status"] == "Covered"])
            uncovered_count = len(filtered_df[filtered_df["status"] == "Uncovered"])
            total_classes = len(filtered_df)
            coverage_rate = (
                (covered_count / total_classes * 100) if total_classes > 0 else 0
            )

            # Display summary metrics in cards
            st.markdown(
                """
            <style>
            .metric-container {
                display: flex;
                justify-content: space-between;
                gap: 20px;
                margin-bottom: 25px;
            }
            .metric-card {
                background: linear-gradient(135deg, #ffffff, #f0f9ff);
                border-radius: 16px;
                padding: 20px;
                flex: 1;
                box-shadow: 0 6px 16px rgba(0,0,0,0.1);
                border: 1px solid rgba(209, 217, 230, 0.5);
                text-align: center;
                transition: transform 0.3s ease;
            }
            .metric-card:hover {
                transform: translateY(-5px);
            }
            .metric-value {
                font-size: 32px;
                font-weight: 700;
                margin: 10px 0;
            }
            .metric-label {
                font-size: 16px;
                color: #6b7280;
                margin-bottom: 5px;
            }
            .coverage-good {
                color: #059669;
            }
            .coverage-medium {
                color: #d97706;
            }
            .coverage-poor {
                color: #dc2626;
            }
            </style>
            """,
                unsafe_allow_html=True,
            )

            coverage_class = (
                "coverage-good"
                if coverage_rate >= 90
                else "coverage-medium" if coverage_rate >= 75 else "coverage-poor"
            )

            st.markdown(
                f"""
            <div class="metric-container">
                <div class="metric-card">
                    <div class="metric-label">Total Classes</div>
                    <div class="metric-value">{total_classes}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Covered Classes</div>
                    <div class="metric-value" style="color: #059669;">{covered_count}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Uncovered Classes</div>
                    <div class="metric-value" style="color: #dc2626;">{uncovered_count}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Coverage Rate</div>
                    <div class="metric-value {coverage_class}">{coverage_rate:.1f}%</div>
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )

            # Coverage by period
            st.subheader("Coverage by Period")

            period_coverage = filtered_df.pivot_table(
                index="period", columns="status", aggfunc="size", fill_value=0
            ).reset_index()

            # Calculate total and coverage percentage
            if (
                "Covered" in period_coverage.columns
                and "Uncovered" in period_coverage.columns
            ):
                period_coverage["Total"] = (
                    period_coverage["Covered"] + period_coverage["Uncovered"]
                )
                period_coverage["Coverage %"] = (
                    period_coverage["Covered"] / period_coverage["Total"] * 100
                ).round(1)
            elif "Covered" in period_coverage.columns:
                period_coverage["Total"] = period_coverage["Covered"]
                period_coverage["Coverage %"] = 100.0
            elif "Uncovered" in period_coverage.columns:
                period_coverage["Total"] = period_coverage["Uncovered"]
                period_coverage["Coverage %"] = 0.0

            # Create the bar chart
            fig = px.bar(
                period_coverage,
                x="period",
                y=(
                    ["Covered", "Uncovered"]
                    if "Covered" in period_coverage.columns
                    and "Uncovered" in period_coverage.columns
                    else (
                        ["Covered"]
                        if "Covered" in period_coverage.columns
                        else ["Uncovered"]
                    )
                ),
                title="Class Coverage by Period",
                labels={
                    "period": "Period",
                    "value": "Number of Classes",
                    "variable": "Status",
                },
                color_discrete_map={"Covered": "#10b981", "Uncovered": "#ef4444"},
            )

            fig.update_layout(barmode="stack")

            st.plotly_chart(fig, use_container_width=True)

            # Add line chart for coverage percentage
            if "Coverage %" in period_coverage.columns:
                fig2 = px.line(
                    period_coverage,
                    x="period",
                    y="Coverage %",
                    markers=True,
                    title="Coverage Percentage by Period",
                    labels={"period": "Period", "Coverage %": "Coverage Rate (%)"},
                )

                fig2.update_traces(
                    line=dict(color="#3b82f6", width=3), marker=dict(size=10)
                )

                st.plotly_chart(fig2, use_container_width=True)

            # Coverage by subject
            st.subheader("Coverage by Subject")

            subject_coverage = filtered_df.pivot_table(
                index="subject", columns="status", aggfunc="size", fill_value=0
            ).reset_index()

            # Calculate total and coverage percentage
            if (
                "Covered" in subject_coverage.columns
                and "Uncovered" in subject_coverage.columns
            ):
                subject_coverage["Total"] = (
                    subject_coverage["Covered"] + subject_coverage["Uncovered"]
                )
                subject_coverage["Coverage %"] = (
                    subject_coverage["Covered"] / subject_coverage["Total"] * 100
                ).round(1)

                # Sort by coverage percentage
                subject_coverage = subject_coverage.sort_values(
                    "Coverage %", ascending=False
                )

                # Create the horizontal bar chart
                fig3 = px.bar(
                    subject_coverage,
                    y="subject",
                    x=["Covered", "Uncovered"],
                    title="Class Coverage by Subject",
                    labels={
                        "subject": "Subject",
                        "value": "Number of Classes",
                        "variable": "Status",
                    },
                    color_discrete_map={"Covered": "#10b981", "Uncovered": "#ef4444"},
                    orientation="h",
                )

                fig3.update_layout(barmode="stack")

                st.plotly_chart(fig3, use_container_width=True)

            # Recent uncovered classes
            st.subheader("Recent Uncovered Classes")

            uncovered_classes = filtered_df[
                filtered_df["status"] == "Uncovered"
            ].sort_values("date", ascending=False)

            if uncovered_classes.empty:
                st.success("No uncovered classes in the selected date range! 🎉")
            else:
                # Display in a formatted table with custom styles
                st.markdown(
                    """
                <style>
                .uncovered-table {
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                    border-radius: 10px;
                    overflow: hidden;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
                }
                .uncovered-table th {
                    background-color: #f43f5e;
                    color: white;
                    text-align: left;
                    padding: 12px 15px;
                    font-weight: 600;
                }
                .uncovered-table td {
                    padding: 10px 15px;
                    border-bottom: 1px solid #e5e7eb;
                }
                .uncovered-table tr:nth-child(even) {
                    background-color: #fef2f2;
                }
                .uncovered-table tr:hover {
                    background-color: #fee2e2;
                }
                .uncovered-table tr:last-child td {
                    border-bottom: none;
                }
                </style>
                """,
                    unsafe_allow_html=True,
                )

                # Display only first 10 records
                uncovered_display = uncovered_classes.head(10)

                # Format date for display
                uncovered_display["date"] = uncovered_display["date"].dt.strftime(
                    "%Y-%m-%d"
                )

                # Select and rename columns for display
                display_cols = [
                    "date",
                    "period",
                    "class_name",
                    "section",
                    "subject",
                    "original_teacher_id",
                ]
                display_names = [
                    "Date",
                    "Period",
                    "Class",
                    "Section",
                    "Subject",
                    "Original Teacher",
                ]

                if len(uncovered_display) > 0:
                    table_html = "<table class='uncovered-table'><thead><tr>"

                    # Add headers
                    for col_name in display_names:
                        table_html += f"<th>{col_name}</th>"

                    table_html += "</tr></thead><tbody>"

                    # Add rows
                    for _, row in uncovered_display.iterrows():
                        table_html += "<tr>"
                        for col in display_cols:
                            table_html += f"<td>{row[col]}</td>"
                        table_html += "</tr>"

                    table_html += "</tbody></table>"

                    st.markdown(table_html, unsafe_allow_html=True)

                    if len(uncovered_classes) > 10:
                        st.caption(
                            f"Showing 10 out of {len(uncovered_classes)} uncovered classes."
                        )

    # Tab 2: Record Coverage
    with tab2:
        st.markdown("### Record Class Coverage")

        # Get teacher list from users.csv
        users_df = (
            pd.read_csv("users.csv") if os.path.exists("users.csv") else pd.DataFrame()
        )

        # Check if we're in edit mode
        if "edit_coverage_index" not in st.session_state:
            st.session_state.edit_coverage_index = None

        # Edit mode selector
        edit_mode = st.checkbox("Edit Existing Coverage Record")

        if edit_mode and not coverage_df.empty:
            # Format date for display
            if "date" in coverage_df.columns:
                display_df = coverage_df.copy()
                display_df["date_str"] = display_df["date"].dt.strftime("%Y-%m-%d")
                display_options = [
                    f"{row['date_str']} - Period {row['period']} - {row['class_name']}{row['section']} - {row['subject']}"
                    for _, row in display_df.iterrows()
                ]

                coverage_selection = st.selectbox(
                    "Select Record to Edit",
                    options=range(len(display_options)),
                    format_func=lambda x: display_options[x],
                )

                # Load the selected coverage data
                selected_row = display_df.iloc[coverage_selection]
                st.session_state.edit_coverage_index = coverage_selection
            else:
                st.warning("No valid coverage data available to edit.")
                selected_row = pd.Series()
                st.session_state.edit_coverage_index = None
        else:
            selected_row = pd.Series(
                {
                    "date": pd.Timestamp(datetime.now().date()),
                    "period": 1,
                    "class_name": "",
                    "section": "",
                    "subject": "",
                    "original_teacher_id": "",
                    "replacement_teacher_id": None,
                    "status": "Uncovered",
                    "notes": "",
                }
            )
            st.session_state.edit_coverage_index = None

        # Create form for adding/editing
        with st.form("coverage_form"):
            col1, col2 = st.columns(2)

            with col1:
                if isinstance(selected_row.get("date"), pd.Timestamp):
                    default_date = selected_row.get("date").date()
                else:
                    default_date = datetime.now().date()

                record_date = st.date_input("Date", value=default_date)

                period = st.number_input(
                    "Period",
                    min_value=1,
                    max_value=8,
                    value=int(selected_row.get("period", 1)),
                )

                class_name = st.text_input(
                    "Class Name", value=selected_row.get("class_name", "")
                )

                section = st.text_input(
                    "Section", value=selected_row.get("section", "")
                )

            with col2:
                subject = st.text_input(
                    "Subject", value=selected_row.get("subject", "")
                )

                # Create teacher options for selection
                if (
                    not users_df.empty
                    and "teacher_id" in users_df.columns
                    and "name" in users_df.columns
                ):
                    teacher_options = [
                        {"id": row["teacher_id"], "name": row["name"]}
                        for _, row in users_df.iterrows()
                        if "teacher_id" in row and "name" in row
                    ]

                    teacher_ids = [t["id"] for t in teacher_options]
                    teacher_display = {
                        t["id"]: f"{t['name']} ({t['id']})" for t in teacher_options
                    }

                    # Default to first teacher if none selected
                    default_teacher_index = 0
                    if selected_row.get("original_teacher_id") in teacher_ids:
                        default_teacher_index = teacher_ids.index(
                            selected_row.get("original_teacher_id")
                        )

                    original_teacher_id = st.selectbox(
                        "Original Teacher",
                        options=teacher_ids,
                        format_func=lambda x: teacher_display.get(x, x),
                        index=default_teacher_index,
                    )

                    # For replacement teacher, add "None" option
                    replacement_options = ["None"] + teacher_ids
                    replacement_display = {"None": "None (Uncovered)"}
                    replacement_display.update(teacher_display)

                    # Default to "None" if no replacement
                    default_replacement_index = 0
                    if selected_row.get("replacement_teacher_id") in teacher_ids:
                        default_replacement_index = (
                            teacher_ids.index(
                                selected_row.get("replacement_teacher_id")
                            )
                            + 1
                        )

                    replacement_selection = st.selectbox(
                        "Replacement Teacher",
                        options=replacement_options,
                        format_func=lambda x: replacement_display.get(x, x),
                        index=default_replacement_index,
                    )

                    replacement_teacher_id = (
                        None
                        if replacement_selection == "None"
                        else replacement_selection
                    )
                else:
                    original_teacher_id = st.text_input(
                        "Original Teacher ID",
                        value=selected_row.get("original_teacher_id", ""),
                    )

                    replacement_input = st.text_input(
                        "Replacement Teacher ID (leave blank if uncovered)",
                        value=(
                            ""
                            if pd.isna(selected_row.get("replacement_teacher_id"))
                            else selected_row.get("replacement_teacher_id", "")
                        ),
                    )

                    replacement_teacher_id = (
                        None if replacement_input == "" else replacement_input
                    )

                status = (
                    "Covered" if replacement_teacher_id is not None else "Uncovered"
                )

            notes = st.text_area("Notes", value=selected_row.get("notes", ""))

            submitted = st.form_submit_button("Save Coverage Record")

            if submitted:
                if (
                    not class_name
                    or not section
                    or not subject
                    or not original_teacher_id
                ):
                    st.error(
                        "Class Name, Section, Subject, and Original Teacher are required fields."
                    )
                else:
                    # Prepare new data
                    new_data = {
                        "date": pd.Timestamp(record_date),
                        "period": period,
                        "class_name": class_name,
                        "section": section,
                        "subject": subject,
                        "original_teacher_id": original_teacher_id,
                        "replacement_teacher_id": replacement_teacher_id,
                        "status": status,
                        "notes": notes,
                    }

                    # Update or add new record
                    if st.session_state.edit_coverage_index is not None:
                        # Update existing
                        coverage_df.iloc[st.session_state.edit_coverage_index] = (
                            new_data
                        )
                        success_msg = f"Updated coverage record for {class_name}{section} period {period}"
                    else:
                        # Add new
                        coverage_df = pd.concat(
                            [coverage_df, pd.DataFrame([new_data])], ignore_index=True
                        )
                        success_msg = f"Added new coverage record for {class_name}{section} period {period}"

                    # Save back to CSV
                    save_coverage_data(coverage_df)
                    st.success(success_msg)

                    # Reset edit state
                    st.session_state.edit_coverage_index = None

                    # Refresh the form
                    st.rerun()

    # Tab 3: Historical Analysis
    with tab3:
        st.markdown("### Historical Coverage Analysis")

        if coverage_df.empty or "date" not in coverage_df.columns:
            st.info("Not enough historical data available for analysis.")
        else:
            # Convert date to datetime for analysis
            coverage_df["date"] = pd.to_datetime(coverage_df["date"])

            # Weekly analysis
            st.subheader("Weekly Coverage Trend")

            # Group by week and calculate coverage metrics
            coverage_df["week"] = coverage_df["date"].dt.isocalendar().week
            coverage_df["year"] = coverage_df["date"].dt.isocalendar().year

            weekly_data = (
                coverage_df.groupby(["year", "week"])
                .agg(
                    total=("status", "count"),
                    covered=("status", lambda x: (x == "Covered").sum()),
                    week_start=("date", "min"),
                )
                .reset_index()
            )

            weekly_data["coverage_rate"] = (
                weekly_data["covered"] / weekly_data["total"] * 100
            ).round(1)
            weekly_data["week_label"] = weekly_data["week_start"].dt.strftime("%b %d")

            # Sort by date
            weekly_data = weekly_data.sort_values("week_start")

            # Create the combined chart
            fig4 = go.Figure()

            # Add bar chart for total classes
            fig4.add_trace(
                go.Bar(
                    x=weekly_data["week_label"],
                    y=weekly_data["total"],
                    name="Total Classes",
                    marker_color="#94a3b8",
                )
            )

            # Add bar chart for covered classes
            fig4.add_trace(
                go.Bar(
                    x=weekly_data["week_label"],
                    y=weekly_data["covered"],
                    name="Covered Classes",
                    marker_color="#10b981",
                )
            )

            # Add line chart for coverage rate
            fig4.add_trace(
                go.Scatter(
                    x=weekly_data["week_label"],
                    y=weekly_data["coverage_rate"],
                    name="Coverage Rate (%)",
                    yaxis="y2",
                    line=dict(color="#3b82f6", width=3),
                    marker=dict(size=8),
                )
            )

            # Update layout
            fig4.update_layout(
                title="Weekly Coverage Trend",
                xaxis_title="Week Starting",
                yaxis_title="Number of Classes",
                yaxis2=dict(
                    title="Coverage Rate (%)",
                    title_font=dict(color="#3b82f6"),
                    tickfont=dict(color="#3b82f6"),
                    overlaying="y",
                    side="right",
                    range=[0, 100],
                ),
                legend=dict(
                    orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
                ),
                barmode="group",
            )

            st.plotly_chart(fig4, use_container_width=True)

            # Day of week analysis
            st.subheader("Coverage by Day of Week")

            # Add day of week
            coverage_df["day_of_week"] = coverage_df["date"].dt.day_name()

            # Correct order for days of week
            day_order = [
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
                "Sunday",
            ]

            # Group by day of week
            day_data = (
                coverage_df.groupby("day_of_week")
                .agg(
                    total=("status", "count"),
                    covered=("status", lambda x: (x == "Covered").sum()),
                )
                .reset_index()
            )

            # Calculate coverage rate
            day_data["coverage_rate"] = (
                day_data["covered"] / day_data["total"] * 100
            ).round(1)

            # Sort by day of week
            day_data["day_order"] = day_data["day_of_week"].apply(
                lambda x: day_order.index(x) if x in day_order else 999
            )
            day_data = day_data.sort_values("day_order")

            # Create the chart
            fig5 = px.bar(
                day_data,
                x="day_of_week",
                y=["covered", "total"],
                barmode="group",
                title="Coverage by Day of Week",
                labels={
                    "day_of_week": "Day",
                    "value": "Number of Classes",
                    "variable": "Type",
                },
                color_discrete_map={"covered": "#10b981", "total": "#94a3b8"},
            )

            # Add coverage rate line
            fig5.add_scatter(
                x=day_data["day_of_week"],
                y=day_data["coverage_rate"],
                mode="lines+markers",
                name="Coverage Rate (%)",
                yaxis="y2",
                line=dict(color="#3b82f6", width=3),
                marker=dict(size=10),
            )

            # Update layout
            fig5.update_layout(
                xaxis_title="Day of Week",
                yaxis_title="Number of Classes",
                yaxis2=dict(
                    title="Coverage Rate (%)",
                    title_font=dict(color="#3b82f6"),
                    tickfont=dict(color="#3b82f6"),
                    overlaying="y",
                    side="right",
                    range=[0, 100],
                ),
            )

            st.plotly_chart(fig5, use_container_width=True)

            # Class coverage heatmap
            st.subheader("Class Period Coverage Heatmap")

            # Create pivot table for heatmap
            heatmap_data = pd.pivot_table(
                coverage_df,
                values="status",
                index="class_name",
                columns="period",
                aggfunc=lambda x: (x == "Covered").mean() * 100,
                fill_value=0,
            )

            # Sort classes by overall coverage
            heatmap_data["total"] = heatmap_data.mean(axis=1)
            heatmap_data = heatmap_data.sort_values("total", ascending=False)
            heatmap_data = heatmap_data.drop(columns=["total"])

            # Create heatmap
            fig6 = px.imshow(
                heatmap_data,
                labels=dict(x="Period", y="Class", color="Coverage %"),
                x=[f"Period {i}" for i in heatmap_data.columns],
                y=heatmap_data.index,
                color_continuous_scale="RdYlGn",
                range_color=[0, 100],
                title="Class Coverage Rate by Period (%)",
            )

            # Update layout
            fig6.update_layout(
                xaxis_title="Period",
                yaxis_title="Class",
                coloraxis_colorbar=dict(title="Coverage %", ticksuffix="%"),
            )

            st.plotly_chart(fig6, use_container_width=True)
# test line to trigger git