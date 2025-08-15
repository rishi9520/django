import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime
import os


def render_substitute_pool_page(school_id, data_manager_instance):
    """Render the substitute teacher pool management page"""
    st.markdown(
        """<div style="margin-right: 5px;color:#1e3a8a;"class="card-title">
           <h1> <svg xmlns="http://www.w3.org/2000/svg" width="40"color:#1e3a8a; height="40" fill="currentColor" viewBox="0 0 24 24" style="margin-right: 10px;">
                <path d="M17 3a4 4 0 0 1 4 4v10a4 4 0 0 1-4 4H7a4 4 0 0 1-4-4V7a4 4 0 0 1 4-4h10z"/>
                <circle cx="9" cy="9" r="2"/>
                <path d="M15 8h2v2h-2z"/>
                <path d="M15 12h2v2h-2z"/>
                <path d="M7 18h10c0-3.314-2.686-6-6-6H9c-1.657 0-3 1.343-3 3s1.343 3 3 3z"/>
            </svg>
            <span>Substitute Teacher Pool</span><?h1>
        </div>""",
        unsafe_allow_html=True,
    )

    # Create tabs for different sections
    tab1, tab2, tab3 = st.tabs(
        ["Available Substitutes", "Add/Edit Substitute", "Performance Metrics"]
    )

    # Function to load substitutes data
    def load_substitutes():
        file_path = "substitutes.csv"
        default_columns = [
            "substitute_id",
            "name",
            "phone",
            "subject_expertise",
            "qualification",
            "availability",
            "rating",
            "category",
            "notes",
        ]
        if os.path.exists(file_path):
            try:
                df = pd.read_csv(file_path)
                # Ensure all default columns exist, add if missing
                for col in default_columns:
                    if col not in df.columns:
                        df[col] = np.nan  # or appropriate default like "" or 0
                # Ensure correct data types if necessary (e.g., rating as float)
                if "rating" in df.columns:
                    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
                # Ensure phone is string
                if "phone" in df.columns:
                    df["phone"] = (
                        df["phone"].astype(str).replace(r"\.0$", "", regex=True)
                    )  # Handle potential float conversion
                return df[default_columns]  # Return with columns in expected order
            except pd.errors.EmptyDataError:
                st.warning(f"{file_path} is empty. Initializing with default columns.")
                return pd.DataFrame(columns=default_columns)
            except Exception as e:
                st.error(f"Error loading substitutes data from {file_path}: {str(e)}")
                st.info("Creating a new empty dataframe structure.")
                return pd.DataFrame(columns=default_columns)
        else:
            # Create default structure if file doesn't exist
            st.info(f"{file_path} not found. Creating a new file.")
            df = pd.DataFrame(columns=default_columns)
            try:
                df.to_csv(file_path, index=False)
            except Exception as e:
                st.error(f"Could not create {file_path}: {e}")
            return df

    # Tab 1: Available Substitutes List
    with tab1:
        st.markdown("### Available Substitute Teachers")

        # Load data
        substitutes_df = load_substitutes()

        if substitutes_df.empty:
            st.info("No substitute teachers have been added yet.")
        else:
            # Ensure 'rating' column exists and handle potential NaNs before filtering/displaying
            if "rating" not in substitutes_df.columns:
                substitutes_df["rating"] = np.nan
            else:
                substitutes_df["rating"] = pd.to_numeric(
                    substitutes_df["rating"], errors="coerce"
                )

            # Ensure 'subject_expertise' is string for .str accessor
            if "subject_expertise" in substitutes_df.columns:
                substitutes_df["subject_expertise"] = substitutes_df[
                    "subject_expertise"
                ].astype(str)
            else:
                substitutes_df["subject_expertise"] = ""

            # Ensure 'category' is string
            if "category" in substitutes_df.columns:
                substitutes_df["category"] = substitutes_df["category"].astype(str)
            else:
                substitutes_df["category"] = ""

            # Ensure 'availability' is string
            if "availability" in substitutes_df.columns:
                substitutes_df["availability"] = substitutes_df["availability"].astype(
                    str
                )
            else:
                substitutes_df["availability"] = ""

            # Filter controls
            col1, col2, col3 = st.columns(3)
            with col1:
                # --- Safely create subject list ---
                all_subjects_flat = []
                if not substitutes_df["subject_expertise"].dropna().empty:
                    try:
                        all_subjects_flat = list(
                            set(
                                subj.strip()
                                for subjects in substitutes_df["subject_expertise"]
                                .dropna()
                                .astype(str)  # Ensure string type
                                for subj in subjects.split(",")
                                if subj.strip()  # Split and strip non-empty subjects
                            )
                        )
                    except Exception as e:
                        st.warning(f"Could not parse subjects: {e}")
                        all_subjects_flat = []

                subject_filter = st.selectbox(
                    "Filter by Subject Expertise",
                    ["All"] + sorted(all_subjects_flat),  # Sort for better UI
                )
                # --- End safe subject list ---

            with col2:
                category_filter = st.selectbox(
                    "Filter by Category",
                    ["All"]
                    + sorted(list(substitutes_df["category"].dropna().unique())),
                )

            with col3:
                # Get unique availability options from the data + standard ones
                availability_options = ["All", "MWF", "TTh", "All Days", "Weekends"]
                if not substitutes_df["availability"].dropna().empty:
                    data_avail = list(substitutes_df["availability"].dropna().unique())
                    availability_options = ["All"] + sorted(
                        list(set(availability_options + data_avail))
                    )

                availability_filter = st.selectbox(
                    "Filter by Availability", availability_options
                )

            # Apply filters
            filtered_df = substitutes_df.copy()

            if subject_filter != "All":
                # Handle potential NaN values safely during string operations
                filtered_df = filtered_df[
                    filtered_df["subject_expertise"].str.contains(
                        subject_filter,
                        na=False,
                        case=False,  # Added case=False for better matching
                    )
                ]

            if category_filter != "All":
                filtered_df = filtered_df[filtered_df["category"] == category_filter]

            if availability_filter != "All":
                filtered_df = filtered_df[
                    filtered_df["availability"] == availability_filter
                ]

            # Display teachers with fancy cards
            if filtered_df.empty:
                st.warning("No substitute teachers match the selected filters.")
            else:
                st.markdown(
                    """
                <style>
                .substitute-card {
                    background: linear-gradient(135deg, #ffffff, #f5f7fa);
                    border-radius: 16px;
                    padding: 20px;
                    margin: 15px 0;
                    border: 1px solid rgba(209, 217, 230, 0.5);
                    box-shadow: 0 6px 16px rgba(0,0,0,0.1);
                    transition: all 0.3s ease;
                    position: relative;
                }
                .substitute-card:hover {
                    transform: translateY(-5px);
                    box-shadow: 0 10px 20px rgba(0,0,0,0.15);
                }
                .sub-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 10px;
                }
                .sub-name {
                    font-size: 18px;
                    font-weight: 600;
                    color: #1e3a8a;
                }
                .sub-id {
                    font-size: 14px;
                    color: #6b7280;
                }
                .rating-badge {
                    background-color: #fef3c7;
                    color: #92400e;
                    padding: 3px 10px;
                    border-radius: 12px;
                    font-weight: 500;
                    font-size: 14px;
                }
                .sub-details {
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 10px;
                    margin-top: 12px;
                }
                .sub-detail-item {
                    margin-bottom: 8px;
                }
                .detail-label {
                    font-size: 14px;
                    color: #6b7280;
                    margin-bottom: 3px;
                }
                .detail-value {
                    font-size: 15px;
                    color: #111827;
                }
                .category-badge {
                    position: absolute;
                    top: 15px;
                    right: 15px;
                    background-color: #e0e7ff;
                    color: #4338ca;
                    font-size: 14px;
                    font-weight: 500;
                    padding: 3px 10px;
                    border-radius: 12px;
                }
                </style>
                """,
                    unsafe_allow_html=True,
                )

                for _, sub in filtered_df.iterrows():
                    current_rating = sub.get("rating")
                    if pd.isna(current_rating):
                        rating_display = "N/A"
                        rating_color = "grey"  # Or some default
                        background_color = "#f3f4f6"  # Default background
                        text_color = "#6b7280"  # Default text
                    else:
                        rating_display = (
                            f"{current_rating:.1f}"  # Format to 1 decimal place
                        )
                        if current_rating >= 4.5:
                            rating_color = "green"
                            background_color = "#dcfce7"
                            text_color = "#166534"
                        elif current_rating >= 3.5:
                            rating_color = "orange"
                            background_color = "#fef3c7"
                            text_color = "#92400e"
                        else:
                            rating_color = "red"
                            background_color = "#fee2e2"
                            text_color = "#991b1b"

                    st.markdown(
                        f"""
                    <div class="substitute-card">
                        <div class="category-badge">{sub.get("category", "")}</div>
                        <div class="sub-header">
                            <div>
                                <div class="sub-name">{sub.get("name", "")}</div>
                                <div class="sub-id">ID: {sub.get("substitute_id", "")}</div>
                            </div>
                            <div class="rating-badge" style="background-color: {background_color}; color: {text_color};">
                                ★ {rating_display}
                            </div>
                        </div>
                        <div class="sub-details">
                            <div class="sub-detail-item">
                                <div class="detail-label">Phone</div>
                                <div class="detail-value">{sub.get("phone", "")}</div>
                            </div>
                            <div class="sub-detail-item">
                                <div class="detail-label">Availability</div>
                                <div class="detail-value">{sub.get("availability", "")}</div>
                            </div>
                            <div class="sub-detail-item">
                                <div class="detail-label">Subject Expertise</div>
                                <div class="detail-value">{sub.get("subject_expertise", "")}</div>
                            </div>
                            <div class="sub-detail-item">
                                <div class="detail-label">Qualification</div>
                                <div class="detail-value">{sub.get("qualification", "")}</div>
                            </div>
                        </div>
                        <div style="margin-top: 10px;">
                            <div class="detail-label">Notes</div>
                            <div class="detail-value" style="font-style: italic;">{sub.get("notes", "")}</div>
                        </div>
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )

    # Tab 2: Add/Edit Substitute
    with tab2:
        st.markdown("### Add or Edit Substitute Teacher")

        substitutes_df = load_substitutes()

        # Ensure 'rating' is numeric for slider default value
        if "rating" in substitutes_df.columns:
            substitutes_df["rating"] = pd.to_numeric(
                substitutes_df["rating"], errors="coerce"
            )
        else:
            substitutes_df["rating"] = np.nan

        # Check if we're editing an existing substitute
        if "edit_substitute_id" not in st.session_state:
            st.session_state.edit_substitute_id = None

        # Edit mode selector
        edit_mode = st.checkbox("Edit Existing Substitute")

        sub_data = {}  # Initialize sub_data dictionary

        if edit_mode and not substitutes_df.empty:
            # Create options list checking for NaNs in name
            options = substitutes_df["substitute_id"].tolist()
            format_func = (
                lambda x: f"{substitutes_df[substitutes_df['substitute_id'] == x]['name'].fillna('Unnamed').values[0]} ({x})"
            )

            substitute_selection = st.selectbox(
                "Select Substitute to Edit",
                options=options,
                format_func=format_func,
                key="edit_select",  # Add a key to help streamlit track changes
            )

            if substitute_selection:  # Check if something is selected
                # Load the selected substitute data
                selected_rows = substitutes_df[
                    substitutes_df["substitute_id"] == substitute_selection
                ]
                if not selected_rows.empty:
                    sub_data = selected_rows.iloc[0].to_dict()
                    # Ensure phone is treated as string for the form field
                    sub_data["phone"] = str(sub_data.get("phone", ""))
                    st.session_state.edit_substitute_id = substitute_selection
                else:
                    st.warning(
                        f"Could not find data for selected ID: {substitute_selection}"
                    )
                    st.session_state.edit_substitute_id = (
                        None  # Reset if data not found
                    )
            else:
                st.session_state.edit_substitute_id = None  # Reset if nothing selected

        if (
            not st.session_state.edit_substitute_id
        ):  # If not editing or selection failed
            # Generate next ID based on existing numeric parts
            if (
                not substitutes_df.empty
                and "substitute_id" in substitutes_df.columns
                and substitutes_df["substitute_id"].notna().any()
            ):
                # Extract numeric part, handle non-numeric IDs gracefully
                numeric_ids = pd.to_numeric(
                    substitutes_df["substitute_id"].str.extract(
                        r"(\d+)$", expand=False
                    ),
                    errors="coerce",
                )
                max_id = numeric_ids.max()
                next_id_num = int(max_id + 1) if pd.notna(max_id) else 1
            else:
                next_id_num = 1
            new_sub_id = f"SUB{str(next_id_num).zfill(3)}"

            sub_data = {
                "substitute_id": new_sub_id,
                "name": "",
                "phone": "",
                "subject_expertise": "",
                "qualification": "",
                "availability": "All Days",
                "rating": 4.0,  # Default rating for new entries
                "category": "TGT",
                "notes": "",
            }
            st.session_state.edit_substitute_id = (
                None  # Explicitly set to None for add mode
            )

        # Create form for adding/editing
        # Use a key based on edit mode to force form reset when switching modes
        form_key = f"substitute_form_{st.session_state.edit_substitute_id or 'new'}"
        with st.form(form_key):
            col1, col2 = st.columns(2)

            with col1:
                name = st.text_input("Name", value=sub_data.get("name", ""))
                # Ensure phone value is string
                phone_value = (
                    str(sub_data.get("phone", "")).replace(".0", "")
                    if pd.notna(sub_data.get("phone"))
                    else ""
                )
                phone = st.text_input("Phone", value=phone_value)
                subject_expertise = st.text_input(
                    "Subject Expertise (comma separated)",
                    value=sub_data.get("subject_expertise", ""),
                )
                qualification = st.text_input(
                    "Qualification", value=sub_data.get("qualification", "")
                )

            with col2:
                avail_options = ["All Days", "MWF", "TTh", "Weekends"]
                current_avail = sub_data.get("availability", "All Days")
                try:
                    avail_index = avail_options.index(current_avail)
                except ValueError:
                    avail_index = 0  # Default to 'All Days' if current value not in standard options

                availability = st.selectbox(
                    "Availability",
                    options=avail_options,
                    index=avail_index,
                )

                cat_options = ["PGT", "TGT", "PRT"]
                current_cat = sub_data.get("category", "TGT")
                try:
                    cat_index = cat_options.index(current_cat)
                except ValueError:
                    cat_index = 1  # Default to 'TGT'

                category = st.selectbox(
                    "Category",
                    options=cat_options,
                    index=cat_index,
                )

                # Ensure rating is float for slider, handle NaN
                rating_value = sub_data.get("rating", 4.0)
                if pd.isna(rating_value):
                    rating_value = 4.0  # Default if NaN

                rating = st.slider("Rating", 1.0, 5.0, float(rating_value), 0.1)

            notes = st.text_area("Notes", value=sub_data.get("notes", ""))

            # Hidden ID (read-only for user)
            st.text_input(
                "Substitute ID", value=sub_data.get("substitute_id"), disabled=True
            )
            substitute_id = sub_data.get("substitute_id")  # Get the ID for processing

            submitted = st.form_submit_button("Save Substitute")

            if submitted:
                if not name or not phone:
                    st.error("Name and Phone are required fields.")
                elif len(phone) != 10 or not phone.isdigit():
                    st.error("Please enter a valid 10-digit phone number.")
                else:
                    # Prepare new data dictionary
                    new_data_dict = {
                        "substitute_id": substitute_id,  # Use the ID from form start
                        "name": name,
                        "phone": phone,  # Keep as string
                        "subject_expertise": subject_expertise,
                        "qualification": qualification,
                        "availability": availability,
                        "rating": rating,  # Keep as float
                        "category": category,
                        "notes": notes,
                    }

                    success_msg = None  # Initialize success message

                    # ------------- CORE FIX START -------------
                    try:
                        if st.session_state.edit_substitute_id:
                            # Update existing
                            mask = (
                                substitutes_df["substitute_id"]
                                == st.session_state.edit_substitute_id
                            )
                            row_indices = substitutes_df.index[
                                mask
                            ].tolist()  # Get the actual index label(s)

                            if len(row_indices) == 1:
                                row_index = row_indices[0]
                                # Create a list of values in the correct column order
                                values_in_order = [
                                    new_data_dict.get(col)
                                    for col in substitutes_df.columns
                                ]
                                # Assign the list to the specific row index using .loc
                                substitutes_df.loc[row_index] = values_in_order
                                success_msg = f"Updated substitute teacher: {name} ({substitute_id})"
                            elif len(row_indices) > 1:
                                st.error(
                                    f"Error: Found multiple ({len(row_indices)}) substitutes with ID {st.session_state.edit_substitute_id}. Cannot update safely. Please check data."
                                )
                            else:
                                st.error(
                                    f"Error: Could not find substitute with ID {st.session_state.edit_substitute_id} to update. It might have been deleted."
                                )

                        else:
                            # Add new
                            # Check if ID already exists (shouldn't happen with generation logic, but good practice)
                            if substitute_id in substitutes_df["substitute_id"].values:
                                st.error(
                                    f"Error: Substitute ID {substitute_id} already exists. Cannot add duplicate."
                                )
                            else:
                                # Ensure the new_data_dict has keys matching DataFrame columns
                                new_df_row = pd.DataFrame(
                                    [new_data_dict], columns=substitutes_df.columns
                                )
                                substitutes_df = pd.concat(
                                    [substitutes_df, new_df_row], ignore_index=True
                                )
                                success_msg = f"Added new substitute teacher: {name} ({substitute_id})"

                        # Save back to CSV only if an add/update operation was potentially successful
                        if success_msg:
                            substitutes_df.to_csv("substitutes.csv", index=False)
                            st.success(success_msg)
                            st.session_state.edit_substitute_id = (
                                None  # Reset edit state
                            )
                            st.rerun()  # Rerun to clear form and update lists

                    except Exception as e:
                        st.error(f"An error occurred during saving: {e}")
                    # ------------- CORE FIX END -------------

    # Tab 3: Performance Metrics
    with tab3:
        st.markdown("### Substitute Teacher Performance Metrics")

        substitutes_df = load_substitutes()

        if substitutes_df.empty:
            st.info("No substitute teachers have been added yet.")
        else:
            # Ensure 'rating' is numeric for plotting, handle NaNs by filtering
            if "rating" in substitutes_df.columns:
                substitutes_df["rating"] = pd.to_numeric(
                    substitutes_df["rating"], errors="coerce"
                )
                plot_df_rating = substitutes_df.dropna(subset=["rating"])
            else:
                plot_df_rating = pd.DataFrame(
                    columns=substitutes_df.columns
                )  # Empty df if no rating col

            if not plot_df_rating.empty:
                # Ratings distribution
                st.subheader("Ratings Distribution")

                fig = px.bar(
                    plot_df_rating,
                    x="name",
                    y="rating",
                    color="rating",
                    color_continuous_scale=[
                        "#fee2e2",
                        "#fef3c7",
                        "#dcfce7",
                    ],  # Redish, Yellowish, Greenish
                    color_continuous_midpoint=3.0,  # Optional: set midpoint for color scale
                    range_color=[1, 5],
                    labels={"name": "Substitute Teacher", "rating": "Rating"},
                    title="Substitute Teacher Ratings",
                    text="rating",  # Show rating value on bars
                )
                fig.update_traces(texttemplate="%{text:.1f}", textposition="outside")
                fig.update_layout(
                    xaxis_title="Substitute Teacher",
                    yaxis_title="Rating",
                    yaxis_range=[0, 5.5],  # Extend range slightly for text visibility
                    coloraxis_showscale=False,
                    xaxis={"categoryorder": "total descending"},  # Sort bars by rating
                )

                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No ratings data available to display.")

            # Category Distribution
            st.subheader("Category Distribution")
            if (
                "category" in substitutes_df.columns
                and not substitutes_df["category"].dropna().empty
            ):
                category_counts = (
                    substitutes_df["category"].dropna().value_counts().reset_index()
                )
                category_counts.columns = [
                    "Category",
                    "Count",
                ]  # Rename columns for clarity

                fig2 = px.pie(
                    category_counts,
                    values="Count",
                    names="Category",
                    title="Substitute Teachers by Category",
                    color="Category",
                    color_discrete_map={
                        "PGT": "#3b82f6",  # Blue
                        "TGT": "#10b981",  # Green
                        "PRT": "#f59e0b",  # Amber
                    },
                )
                fig2.update_traces(textposition="inside", textinfo="percent+label")
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("No category data available to display.")

            # Subject expertise
            st.subheader("Subject Expertise Distribution")
            if (
                "subject_expertise" in substitutes_df.columns
                and not substitutes_df["subject_expertise"].dropna().empty
            ):
                # Extract all subjects from the comma-separated list safely
                all_subjects = []
                for subjects in (
                    substitutes_df["subject_expertise"].dropna().astype(str)
                ):
                    all_subjects.extend(
                        [s.strip() for s in subjects.split(",") if s.strip()]
                    )  # Ensure not empty strings

                if all_subjects:
                    subject_counts = (
                        pd.Series(all_subjects).value_counts().reset_index()
                    )
                    subject_counts.columns = ["Subject", "Count"]  # Rename columns

                    fig3 = px.bar(
                        subject_counts,
                        x="Subject",
                        y="Count",
                        title="Subject Expertise Distribution",
                        color="Count",
                        color_continuous_scale=px.colors.sequential.Viridis,
                        text="Count",
                    )
                    fig3.update_layout(
                        xaxis_title="Subject", yaxis_title="Number of Teachers"
                    )
                    fig3.update_traces(textposition="outside")
                    st.plotly_chart(fig3, use_container_width=True)
                else:
                    st.info("No subject expertise data entered.")
            else:
                st.info("No subject expertise data available to display.")


# --- Example of how to run this page (if it's not your main app file) ---
# if __name__ == "__main__":
#     # Set page config (optional, do it once at the start of your app)
#     # st.set_page_config(layout="wide")
#     render_substitute_pool_page()
