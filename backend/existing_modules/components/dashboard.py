import streamlit as st
from data_manager import DataManager
import pandas as pd
from datetime import datetime, date, time
import json
import streamlit.components.v1 as components
from streamlit.components.v1 import html
import os
import plotly.graph_objects as go
import plotly.express as px
import calendar
from streamlit_lottie import st_lottie
from utils import get_ist_today

def get_calendar_dates():
    if "calendar_date" not in st.session_state:
        st.session_state.calendar_date = datetime.now()
    return st.session_state.calendar_date


def change_month(delta):
    current = get_calendar_dates()
    new_date = current.replace(day=1)
    if delta > 0:
        # Move to next month
        if new_date.month == 12:
            new_date = new_date.replace(year=new_date.year + 1, month=1)
        else:
            new_date = new_date.replace(month=new_date.month + 1)
    else:
        # Move to previous month
        if new_date.month == 1:
            new_date = new_date.replace(year=new_date.year - 1, month=12)
        else:
            new_date = new_date.replace(month=new_date.month - 1)
    st.session_state.calendar_date = new_date


def generate_calendar_days(current_date):
    cal = calendar.monthcalendar(current_date.year, current_date.month)
    html = ""
    today = datetime.now().day
    current_month = datetime.now().month
    current_year = datetime.now().year

    # First add weekday headers
    weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    for weekday in weekdays:
        html += f'<div class="calendar-weekday">{weekday}</div>'

    # Then add days
    for week in cal:
        for day in week:
            if day == 0:
                html += '<div class="calendar-day empty"></div>'
            elif (
                day == today
                and current_date.month == current_month
                and current_date.year == current_year
            ):
                html += f'<div class="calendar-day today">{day}</div>'
            else:
                html += f'<div class="calendar-day">{day}</div>'

    return html


def render_dashboard(school_id, data_manager):
    """
    Render the dashboard page, fetching data from the database.
    """

    user_details = st.session_state.get("user_details")
    if not user_details:
        st.error("Logged-in user details not found in session state.")
        st.warning("Dashboard render failed: user_details missing in session state.")
        # This might indicate a problem in the login process if authentication was successful
        return  # Exit if user details not available

    today = get_ist_today()
    data_manager_instance = st.session_state.data_manager
    auto_timing_data = data_manager_instance.get_arrangement_time(
        school_id
    )  # This returns a dict {"hour": h, "minute": m, "enabled": b}

    def load_lottie_file(filepath: str):
        with open(filepath, "r") as f:
            return json.load(f)

    # Safely extract hour, minute, enabled
    auto_hour = auto_timing_data.get("hour", 10)
    auto_minute = auto_timing_data.get("minute", 30)
    auto_absent_enabled = auto_timing_data.get(
        "enabled", True
    )  # Default to True if not in DB

    # Today's date string for display
    today_date_display = datetime.now().strftime("%A, %B %d, %Y")
    col_welcome, col_animation = st.columns([3, 1])
    with col_welcome:
        st.markdown(
            f"""
        <style>
        .logo-container {{
            display: flex;
            align-items: center;
            text-align:left;
            margin-top: -100px;
            animation: fadeInUp 0.8s ease-out forwards;
        }}
        @keyframes fadeInUp {{
            from {{
                opacity: 0;
                transform: translateY(20px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        .logo-container img {{
            width: 50px;
            height: 50px;
            margin-right: 10px;
        }}
        .welcome-text {{
            font-size: 2.2rem;
            font-weight: 700;
            background: linear-gradient(90deg, #1E3A8A, #3B82F6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 5px;
        }}
        iframe.st-emotion-cache-1tvzk6f.e1begtbc0 {{
        /* margin-top: -130px !important; /* Isko abhi comment karte hain */
        transform: translateY(-110px) !important; /* Iski jagah yeh try karein */
        margin-bottom: -150px !important; /* Yeh theek hai agar neeche ka space kam kar raha hai */
        padding-right: 0 !important; /* "none" ki jagah "0" use karein */
        display: block !important; /* Ensures it behaves like a block, helps with margins */
        position: relative; /* Can help ensure transform and margins behave as expected */
        z-index: 1;
        
        }}
        .welcome-subtext {{
            font-weight: 600;
            color: #6c7293;
            font-size: 1.1rem;
        }}
        </style>
        <div class="logo-container">
            <div>
                <h1 class="welcome-text">Hi, welcome back!</h1>
                <p class="welcome-subtext">Your teacher analytics dashboard - {today.strftime('%A, %d %B %Y')}</p>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col_animation:
        try:
            lottie_animation = load_lottie_file(
                "attached_assets/lottie_animation2.json"
            )
            st_lottie(lottie_animation, height=170, width=170, key="dashboard_lottie2")
        except Exception as e:
            st.write("🏫")

    # Get current user's details

    stat_styles = """
      <style>
    /* Common Card Styles */
     @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    .stat-card {
        text-align: left;
        box-shadow: 0 8px 16px rgba(0,0,0,0.15);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        padding: 1.8rem;
        display: flex;
        justify-content: space-between;
        font-weight: 600;
        # border-radius: 1rem;
        margin-bottom: 25px;
        opacity: 1;
        transform: translateY(0);
        overflow: hidden;
        position: relative;
    }
    
    .stat-card:before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(255, 255, 255, 0);
        transition: all 0.3s ease;
        z-index: 1;
    }
    
    .stat-card:hover {
        transform: translateY(-10px);
        box-shadow: 0 15px 30px rgba(0,0,0,0.25);
    }
    
    .stat-card:hover:before {
        background: rgba(255, 255, 255, 0.1);
    }
    
    .stat-content {
        flex-grow: 1;
        position: relative;
        z-index: 2;
    }
    
    .stat-icon {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background-color: rgba(255, 255, 255, 0.2);
        display: flex;
        align-items: center;
        justify-content: center;
        position: relative;
        z-index: 2;
        transition: all 0.3s ease;
    }
    
    .stat-card:hover .stat-icon {
        transform: scale(1.1) rotate(10deg);
        background-color: rgba(255, 255, 255, 0.3);
    }
    
    .card-title {
        font-size: 32px;
        font-weight: 700;
        margin-bottom: 30px;
        margin-top: 40px;
    }

    /* Animation Effects with enhanced gradients */
    .total-teachers {
        background: linear-gradient(135deg, #FF8F00, #FFC107);
        animation: pulse 2s infinite alternate;
    }

    .present-today {
        background: linear-gradient(135deg, #E91E63, #F06292);
        animation: pulse 2.3s infinite alternate;
    }

    .absent-today {
        background: linear-gradient(135deg, #2196F3, #64B5F6);
        animation: pulse 2.6s infinite alternate;
    }
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-of-type(2) {
        # background-color: white !important;
        box-sizing: border-box !important;
        /* Resetting potential Streamlit margins/paddings that interfere */
         /* Adjust if there's unwanted external spacing */
        # margin-right: -50px !important;
        margin-left:10px !important;
        boarder-radius:none !important;
    }
  
       
        
        /* Animation keyframes */
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        @keyframes slideInFromLeft {
            from { transform: translateX(-30px); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        
        @keyframes slideInFromRight {
            from { transform: translateX(30px); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        
        @keyframes float {
            0% { transform: translateY(0px); }
            50% { transform: translateY(-10px); }
            100% { transform: translateY(0px); }
        }
        
        @keyframes pulse {
            0% { box-shadow: 0 8px 16px rgba(0,0,0,0.15); }
            100% { box-shadow: 0 12px 24px rgba(0,0,0,0.25); }
        }
    .feature1-card {
            background: white;
            border-radius: 16px; 
            padding: 25px;
            margin: 15px 0;
            box-shadow: 
                0 10px 15px -3px rgba(0, 0, 0, 0.1),
                0 4px 6px -2px rgba(0, 0, 0, 0.05);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            transform-style: preserve-3d;
            perspective: 1000px;
            position: relative;
            border: 1px solid rgba(209, 213, 219, 0.3);
        }
        
        .feature1-card:hover {
            transform: translateY(-10px) rotateX(5deg) rotateY(5deg);
            box-shadow: 
                0 20px 25px -5px rgba(0, 0, 0, 0.1),
                0 10px 10px -5px rgba(0, 0, 0, 0.04);
        }
        
        .feature1-card::after {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            border-radius: 16px;
            background: linear-gradient(
                135deg, 
                rgba(255, 255, 255, 0.3) 0%, 
                rgba(255, 255, 255, 0) 50%
            );
            z-index: 1;
            pointer-events: none;
        }
        
        .feature1-icon {
            background: linear-gradient(135deg, #667eea, #764ba2);
            width: 60px;
            height: 60px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 15px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }
        
        .feature1-title {
            font-size: 20px;
            font-weight: 600;
            margin-bottom: 10px;
            color: #1a202c;
            position: relative;
            z-index: 2;
        }
        
        .feature1-description {
            line-height: 1.6;
            position: relative;
            z-index: 2;
            font-weight: 600;
            color: #6c7293;
            font-size: 1.1rem;"
        }
          /* Attendance timing notification */
        .auto-absent-notice {
            background: linear-gradient(135deg, #FEF3C7, #FEF9C3);
            border-left: 5px solid #F59E0B;
            padding: 16px 20px;
            border-radius: 8px;
            margin: 30px 0;
            display: flex;
            align-items: center;
        }
        
        .notice-icon {
            min-width: 40px;
            height: 40px;
            border-radius: 50%;
            background: #FEF3C7;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 16px;
            border: 2px solid #F59E0B;
        }
        
        .notice-content {
            flex: 1;
        }
        
        .notice-title {
            font-size: 1.1rem;
            font-weight: 600;
            color: #92400E;
            margin: 0 0 5px 0;
        }
        
        .notice-text {
            font-size: 0.95rem;
            color: #92400E;
            margin: 0;
            opacity: 0.9;
        }
</style>
    """
    st.markdown(stat_styles, unsafe_allow_html=True)
    timing_settings = data_manager_instance.get_auto_marking_timing(school_id)
    reminder_time_str = "N/A"
    # Check karo ki settings mili ya nahi
    if timing_settings and "hour" in timing_settings and "minute" in timing_settings:
        db_hour = timing_settings.get("hour")
        db_minute = timing_settings.get("minute")
        db_enabled = timing_settings.get(
            "enabled", False
        )  # Default to False if 'enabled' key missing

        print(
            f"DEBUG Dashboard: Fetched timing - {db_hour}:{db_minute}, Enabled={db_enabled}"
        )

        if db_enabled:
            try:
                reminder_time_obj = time(db_hour, db_minute)
                reminder_time_str = reminder_time_obj.strftime(
                    "%I:%M %p"
                )  # Format: HH:MM AM/PM (e.g., 10:00 AM)
            except ValueError:
                # Agar invalid hour/minute save hua hai database mein
                print(
                    f"ERROR Dashboard: Invalid time fetched from DB: {db_hour}:{db_minute}"
                )
                reminder_time_str = (
                    f"{db_hour:02d}:{db_minute:02d}"  # Fallback to HH:MM format
                )
    st.markdown(
        f"""
        <div class="auto-absent-notice">
            <div class="notice-icon">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="#F59E0B" viewBox="0 0 16 16">
                  <path d="M8 16A8 8 0 1 0 8 0a8 8 0 0 0 0 16zm.93-9.412-1 4.705c-.07.34.029.533.304.533.194 0 .487-.07.686-.246l-.088.416c-.287.346-.92.598-1.465.598-.703 0-1.002-.422-.808-1.319l.738-3.468c.064-.293.006-.399-.287-.47l-.451-.081.082-.381 2.29-.287zM8 5.5a1 1 0 1 1 0-2 1 1 0 0 1 0 2z"/>
                </svg>
            </div>
            <div class="notice-content">
                <h3 class="notice-title">Auto-Absent Marking Reminder</h3>
                <p class="notice-text">
                     Teachers who have not marked their attendance by <b>{reminder_time_str}</b> will be automatically marked as absent.
                                Please ensure all staff members record their attendance before this time.
                </p>
            </div>
        </div>
    """,
        unsafe_allow_html=True,
    )
    # Statistics
    (
        col1,
        col2,
    ) = st.columns({1.6, 3})
    data_manager_instance = st.session_state.data_manager
    all_teachers_list = data_manager_instance.get_all_teachers(school_id)
    total_teachers = len(all_teachers_list) if all_teachers_list else 0
    present_today_list = data_manager_instance.get_present_teachers(school_id, today)
    present_today = len(present_today_list) if present_today_list else 0

    absent_today_list = data_manager_instance.get_absent_teachers(school_id, today)
    absent_today = len(absent_today_list) if absent_today_list else 0

    with col1:
        # This CSS block contains all the new styling for the cards
        st.markdown(
            """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap');
            
            .stat-v2-card {
                font-family: 'Poppins', sans-serif;
                color: white;
                padding: 25px;
                border-radius: 16px;
                position: relative;
                overflow: hidden;
                transition: transform 0.3s ease, box-shadow 0.3s ease;
                margin-bottom: 25px;
                box-shadow: 0 10px 20px rgba(0,0,0,0.1);
            }
            .stat-v2-card:hover {
                transform: translateY(-10px);
                box-shadow: 0 15px 30px rgba(0,0,0,0.2);
            }
            .stat-v2-card .icon-bg {
                position: absolute;
                top: -20px;
                right: -20px;
                font-size: 100px;
                opacity: 0.15;
                transform: rotate(-20deg);
                pointer-events: none;
            }
            .stat-v2-card .title {
                font-weight: 600;
                font-size: 1.1rem;
                margin: 0 0 5px 0;
            }
            .stat-v2-card .value {
                font-weight: 700;
                font-size: 3rem;
                line-height: 1;
                margin: 0;
            }
            .stat-v2-card .subtitle {
                font-weight: 400;
                font-size: 0.9rem;
                opacity: 0.8;
                margin-top: 8px;
            }
            
            /* Card Specific Gradients */
            .total-teachers-v2 { background: linear-gradient(135deg, #4f46e5, #7c3aed); }
            .present-today-v2 { background: linear-gradient(135deg, #059669, #10b981); }
            .absent-today-v2 { background: linear-gradient(135deg, #dc2626, #ef4444); }
        </style>
        """,
            unsafe_allow_html=True,
        )

        # Card 1: Total Teachers
        st.markdown(
            f"""
        <div class="stat-v2-card total-teachers-v2">
            <div class="icon-bg">👥</div>
            <div class="title">Total Teachers</div>
            <div class="value">{total_teachers}</div>
            <div class="subtitle">Registered in the school</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Card 2: Present Today
        st.markdown(
            f"""
        <div class="stat-v2-card present-today-v2">
            <div class="icon-bg">✅</div>
            <div class="title">Present Today</div>
            <div class="value">{present_today}</div>
            <div class="subtitle">Marked as present</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Card 3: Absent Today
        st.markdown(
            f"""
        <div class="stat-v2-card absent-today-v2">
            <div class="icon-bg">❌</div>
            <div class="title">Absent Today</div>
            <div class="value">{absent_today}</div>
            <div class="subtitle">Marked as absent</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    def load_lottie_file(filepath: str):
        with open(filepath, "r") as f:
            return json.load(f)

    with col2:
        st.markdown(
            "<div style='margin-top: 79px;'></div>", unsafe_allow_html=True
        )  # Add vertical space

        try:
            lottie_animation = load_lottie_file("attached_assets/lottie_animation.json")
            st_lottie(lottie_animation, height=580, width=620, key="dashboard_lottie")
        except Exception as e:
            st.write("🏫")

    st.markdown(
        "<h2 style='margin-top: 40px; margin-bottom: 20px; font-size: 24px;'>Management Features</h2>",
        unsafe_allow_html=True,
    )
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
            <div class="feature1-card">
                <div class="feature1-icon">
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="white" viewBox="0 0 16 16">
                        <path d="M8 8a3 3 0 1 0 0-6 3 3 0 0 0 0 6Zm2-3a2 2 0 1 1-4 0 2 2 0 0 1 4 0Zm4 8c0 1-1 1-1 1H3s-1 0-1-1 1-4 6-4 6 3 6 4Zm-1-.004c-.001-.246-.154-.986-.832-1.664C11.516 10.68 10.289 10 8 10c-2.29 0-3.516.68-4.168 1.332-.678.678-.83 1.418-.832 1.664h10Z"/>
                    </svg>
                </div>
                <h3 class="feature1-title">Teacher Attendance</h3>
                <p class="feature1-description">
                    Mark and track teacher attendance with real-time updates.
                    View historical attendance patterns and identify trends.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
            <div class="feature1-card">
                <div class="feature1-icon">
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="white" viewBox="0 0 16 16">
                        <path d="M0 5a5.002 5.002 0 0 0 4.027 4.905 6.46 6.46 0 0 1 .544-2.073C3.695 7.536 3.132 6.864 3 5.91h-.5v-.426h.466V5.05c0-.046 0-.093.004-.135H2.5v-.427h.511C3.236 3.24 4.213 2.5 5.681 2.5c.316 0 .59.031.819.085v.733a3.46 3.46 0 0 0-.815-.082c-.919 0-1.538.466-1.734 1.252h1.917v.427h-1.98c-.003.046-.003.097-.003.147v.422h1.983v.427H3.93c.118.602.468 1.03 1.005 1.229a6.5 6.5 0 0 1 4.97-3.113A5.002 5.002 0 0 0 0 5zm16 5.5a5.5 5.5 0 1 1-11 0 5.5 5.5 0 0 1 11 0zm-7.75 1.322c.069.835.746 1.485 1.964 1.562V14h.54v-.62c1.259-.086 1.996-.74 1.996-1.69 0-.865-.563-1.31-1.57-1.54l-.426-.1V8.374c.54.06.884.347.966.745h.948c-.07-.804-.779-1.433-1.914-1.502V7h-.54v.629c-1.076.103-1.808.732-1.808 1.622 0 .787.544 1.288 1.45 1.493l.358.085v1.78c-.554-.08-.92-.376-1.003-.787H8.25zm1.96-1.895c-.532-.12-.82-.364-.82-.732 0-.41.311-.719.824-.809v1.54h-.005zm.622 1.044c.645.145.943.38.943.796 0 .474-.37.8-1.02.86v-1.674l.077.018z"/>
                    </svg>
                </div>
                <h3 class="feature1-title">Class Arrangements</h3>
                <p class="feature1-description">
                    Automatically generate intelligent class arrangements for absent teachers.
                    Ensure no class goes uncovered with smart teacher selection.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            """
            <div class="feature1-card">
                <div class="feature1-icon">
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="white" viewBox="0 0 16 16">
                        <path d="M14.5 3a.5.5 0 0 1 .5.5v9a.5.5 0 0 1-.5.5h-13a.5.5 0 0 1-.5-.5v-9a.5.5 0 0 1 .5-.5h13zm-13-1A1.5 1.5 0 0 0 0 3.5v9A1.5 1.5 0 0 0 1.5 14h13a1.5 1.5 0 0 0 1.5-1.5v-9A1.5 1.5 0 0 0 14.5 2h-13z"/>
                        <path d="M7 5.5a.5.5 0 0 1 .5-.5h5a.5.5 0 0 1 0 1h-5a.5.5 0 0 1-.5-.5zm-1.496-.854a.5.5 0 0 1 0 .708l-1.5 1.5a.5.5 0 0 1-.708 0l-.5-.5a.5.5 0 1 1 .708-.708l.146.147 1.146-1.147a.5.5 0 0 1 .708 0zM7 9.5a.5.5 0 0 1 .5-.5h5a.5.5 0 0 1 0 1h-5a.5.5 0 0 1-.5-.5zm-1.496-.854a.5.5 0 0 1 0 .708l-1.5 1.5a.5.5 0 0 1-.708 0l-.5-.5a.5.5 0 0 1 .708-.708l.146.147 1.146-1.147a.5.5 0 0 1 .708 0z"/>
                    </svg>
                </div>
                <h3 class="feature1-title">SMS Notifications</h3>
                <p style="margin-top:10px;"class="feature1-description">
                    Automatically notify teachers about their attendance status and arrangements.
                    Real-time communication ensures everyone stays informed.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    if "data_manager" not in st.session_state:
        st.session_state.data_manager = DataManager()

    st.markdown(
        """<div class="card-title">
            <svg xmlns="http://www.w3.org/2000/svg" width="25" height="25" fill="currentColor" viewBox="0 0 16 16" style="margin-right: 5px;">
                <path d="M15 14s1 0 1-1-1-4-5-4-5 3-5 4 1 1 1 1h8Zm-7.978-1A.261.261 0 0 1 7 12.996c.001-.264.167-1.03.76-1.72C8.312 10.629 9.282 10 11 10c1.717 0 2.687.63 3.24 1.276.593.69.758 1.457.76 1.72l-.008.002a.274.274 0 0 1-.014.002H7.022ZM11 7a2 2 0 1 0 0-4 2 2 0 0 0 0 4Zm3-2a3 3 0 1 1-6 0 3 3 0 0 1 6 0ZM6.936 9.28a5.88 5.88 0 0 0-1.23-.247A7.35 7.35 0 0 0 5 9c-4 0-5 3-5 4 0 .667.333 1 1 1h4.216A2.238 2.238 0 0 1 5 13c0-1.01.377-2.042 1.09-2.904.243-.294.526-.569.846-.816ZM4.92 10A5.493 5.493 0 0 0 4 13H1c0-.26.164-1.03.76-1.724.545-.636 1.492-1.256 3.16-1.275ZM1.5 5.5a3 3 0 1 1 6 0 3 3 0 0 1-6 0Zm3-2a2 2 0 1 0 0 4 2 2 0 0 0 0-4Z"/>
            </svg>
            Arrangements
        </div>""",
        unsafe_allow_html=True,
    )

    if not data_manager_instance.is_arrangement_suspended(school_id, today):
        arrangements = data_manager_instance.get_todays_arrangements(school_id, today)
        if not arrangements.empty:
            st.dataframe(
                arrangements,
                column_config={
                    "absent_teacher": "Absent Teacher",
                    "replacement_teacher": "Replacement Teacher",
                    "class": "Class",
                    "period": "Period",
                    "status": "Status",
                },
                hide_index=True,
            )
        else:
            st.info("No arrangements required")
    else:
        st.warning

    # Weekly attendance summary (for admins)
    col1, col2 = st.columns(2)
    with col1:
        # if st.session_state.role == "admin":
        st.markdown(
            """<div class="card-title">
                <svg xmlns="http://www.w3.org/2000/svg" width="25" height="25" fill="currentColor" viewBox="0 0 16 16" style="margin-right: 5px;">
                    <path d="M3.5 0a.5.5 0 0 1 .5.5V1h8V.5a.5.5 0 0 1 1 0V1h1a2 2 0 0 1 2 2v11a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V3a2 2 0 0 1 2-2h1V.5a.5.5 0 0 1 .5-.5zM1 4v10a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V4H1z"/>
                    <path d="M6.854 8.146a.5.5 0 1 0-.708.708L7.293 10H4.5a.5.5 0 0 0 0 1h2.793l-1.147 1.146a.5.5 0 0 0 .708.708l2-2a.5.5 0 0 0 0-.708l-2-2M8 13a1 1 0 1 1 0-2 1 1 0 0 1 0 2z"/>
                </svg>
                Weekly Summary
            </div>""",
            unsafe_allow_html=True,
        )

        # Get data for the past week
        end_date = today  # Assuming 'today' is defined
        start_date = end_date - pd.Timedelta(days=6)

        # CORRECTED CALL: Pass db_connection and school_id first
        weekly_data = data_manager_instance.get_attendance_report(
            school_id,
            start_date=str(start_date),
            end_date=str(end_date),  # <-- Corrected call
        )

        if not weekly_data.empty:
            # Group by date and status (Pandas logic remains)
            summary = (
                weekly_data.groupby(["date", "status"]).size().reset_index(name="count")
            )
            pivot_data = summary.pivot(
                index="date", columns="status", values="count"
            ).reset_index()

            # Fill NaN with 0
            if "present" not in pivot_data.columns:
                pivot_data["present"] = 0
            if "absent" not in pivot_data.columns:
                pivot_data["absent"] = 0

            pivot_data = pivot_data.fillna(0)

            # Create a bar chart (Plotly logic remains)
            fig = go.Figure()

            fig.add_trace(
                go.Bar(
                    x=pivot_data["date"],
                    y=pivot_data["present"],
                    name="Present",
                    marker_color="#2e7d32",
                )
            )

            fig.add_trace(
                go.Bar(
                    x=pivot_data["date"],
                    y=pivot_data["absent"],
                    name="Absent",
                    marker_color="#d32f2f",
                )
            )

            fig.update_layout(
                barmode="stack",
                title="Weekly Attendance",
                xaxis_title="Date",
                yaxis_title="Number of Teachers",
                legend=dict(
                    orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
                ),
                margin=dict(l=0, r=0, t=40, b=0),
                height=350,
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available for the past week.")
    with col2:
        # if st.session_state.role == "admin":
        st.markdown(
            """<div class="card-title">
                <svg xmlns="http://www.w3.org/2000/svg" width="25" height="25" fill="currentColor" viewBox="0 0 16 16" style="margin-right: 5px; vertical-align: middle;">
       <path d="M1 11a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1v3a1 1 0 0 1-1 1H2a1 1 0 0 1-1-1v-3zm5-4a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1v7a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1V7zm5-5a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1h-2a1 1 0 0 1-1-1V2z"/>
        </svg>
                Manual Vs Auto Absent
            </div>""",
            unsafe_allow_html=True,
        )
        data_manager_instance = st.session_state.data_manager  # Get the instance

        end_date_chart = today  # Assuming 'today' is already defined as get_ist_today()
        start_date_chart = end_date_chart - pd.Timedelta(days=30)
        attendance_df_chart = data_manager_instance.get_attendance_report(
            school_id, str(start_date_chart), str(end_date_chart)
        )
        if not attendance_df_chart.empty:
            # --- Data Validation ---
            # Check for required columns before proceeding
            if (
                "is_auto" not in attendance_df_chart.columns
                or "date" not in attendance_df_chart.columns
                or "status"
                not in attendance_df_chart.columns  # Status is needed for filtering 'absent'
            ):
                st.error(
                    "⚠️ Required columns ('is_auto', 'date', 'status') missing from attendance data for chart."
                )
                st.warning(
                    "Missing required columns in attendance data fetched for col2 chart"
                )
                marking_df = (
                    pd.DataFrame()
                )  # Ensure marking_df exists but is empty on error
            else:
                # Ensure 'is_auto' is boolean
                try:
                    # Convert 'is_auto' column to boolean, handling potential missing/malformed values
                    attendance_df_chart["is_auto"] = attendance_df_chart[
                        "is_auto"
                    ].astype(bool)
                except Exception as e:
                    st.warning(
                        f"⚠️ Issue converting 'is_auto' to boolean for chart: {e}"
                    )
                    # Fallback conversion if direct cast fails
                    attendance_df_chart["is_auto"] = attendance_df_chart[
                        "is_auto"
                    ].apply(
                        lambda x: (
                            str(x).strip().lower() == "true" if pd.notna(x) else False
                        )  # Handle potential NaN/None
                    )

                # Filter for only 'absent' records as the chart is Manual vs Auto Absent
                absent_records_chart = attendance_df_chart[
                    attendance_df_chart["status"] == "absent"
                ].copy()  # Use .copy() to avoid SettingWithCopyWarning

                # --- Aggregation ---
                # Group by date and is_auto status for absent records
                if not absent_records_chart.empty:
                    summary_chart = (
                        absent_records_chart.groupby(["date", "is_auto"])
                        .size()
                        .reset_index(name="count")
                    )
                    pivot_data_chart = summary_chart.pivot(
                        index="date", columns="is_auto", values="count"
                    ).reset_index()

                    # Rename columns 0=False (Manual), 1=True (Auto)
                    pivot_data_chart.rename(
                        columns={False: "manual_marked", True: "auto_marked"},
                        inplace=True,
                    )

                    # Fill NaN with 0
                    if "manual_marked" not in pivot_data_chart.columns:
                        pivot_data_chart["manual_marked"] = 0
                    if "auto_marked" not in pivot_data_chart.columns:
                        pivot_data_chart["auto_marked"] = 0

                    marking_df = pivot_data_chart.fillna(0)

                    # Ensure counts are integers
                    marking_df[["auto_marked", "manual_marked"]] = marking_df[
                        ["auto_marked", "manual_marked"]
                    ].astype(int)

                    # Convert date to datetime and sort
                    try:
                        marking_df["date"] = pd.to_datetime(marking_df["date"])
                        marking_df = marking_df.sort_values(by="date")
                    except Exception as e:
                        st.warning(f"⚠️ Date parsing issue for chart: {e}.")
                        st.warning(f"Date parsing error in col2 chart: {e}")

                else:
                    marking_df = (
                        pd.DataFrame()
                    )  # Empty if no absent records in the range

        else:
            # Display message if attendance_df_chart was empty from DB
            st.info(
                "ℹ️ No attendance data available in the selected range for Manual vs Auto-Marked chart."
            )
            marking_df = (
                pd.DataFrame()
            )  # Ensure marking_df is defined as empty even if initial fetch failed
        if not marking_df.empty:
            # Create Plotly figure (Keep Plotly logic)
            fig1 = px.bar(
                marking_df,
                x="date",
                y=["manual_marked", "auto_marked"],
                labels={"value": "Number of Records", "variable": "Marking Type"},
                color_discrete_map={
                    "manual_marked": "#0ea5e9",  # Blueish
                    "auto_marked": "#f59e0b",  # Orange
                },
                barmode="stack",
            )

            # Update layout (Keep layout)
            fig1.update_layout(
                xaxis_title="Date",
                yaxis_title="Number of Records",
                legend_title="Marking Type",
                height=350,
                margin=dict(t=30, l=0, r=0, b=0),
                xaxis=dict(tickformat="%b %d, %Y"),
                legend=dict(
                    orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
                ),
            )

            # Display chart *inside* the column (Keep)
            st.plotly_chart(fig1, use_container_width=True)
        else:
            # Display message *inside* the column if no data
            st.info("ℹ️ Not enough data for Manual vs Auto-Marked chart.")

    # Custom CSS for the teacher attendance table
    st.markdown(
        """
<style>
    .teacher-card {
        background: linear-gradient(135deg, #ffffff, #e3f2fd);
        border-radius: 16px;
        padding: 18px;
        margin: 15px 0;
        border: 1px solid rgba(209, 217, 230, 0.5);
        box-shadow: 0 6px 16px rgba(0,0,0,0.1);
        display: flex;
        align-items: center;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        position: relative;
        overflow: hidden;
        z-index: 1;
    }
    
    .teacher-card:before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.05), rgba(147, 197, 253, 0.1));
        opacity: 0;
        transition: opacity 0.4s ease;
        z-index: -1;
    }
    
    .teacher-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 12px 24px rgba(0,0,0,0.15);
        border-color: rgba(59, 130, 246, 0.3);
    }
    
    .teacher-card:hover:before {
        opacity: 1;
    }
    
    .teacher-checkbox {
        margin-right: 18px;
        transform: scale(1.2);
    }
    
    .teacher-info {
        flex-grow: 1;
        padding-right: 15px;
        transition: all 0.3s ease;
    }
    
    .teacher-card:hover .teacher-info {
        transform: translateX(5px);
    }
    
    .teacher-name {
        font-weight: 700;
        font-size: 18px;
        color: #2c3e50;
        margin-bottom: 4px;
        position: relative;
        display: inline-block;
    }
    
    .teacher-name:after {
        content: '';
        position: absolute;
        bottom: -2px;
        left: 0;
        width: 0;
        height: 2px;
        background: linear-gradient(90deg, #3b82f6, #93c5fd);
        transition: width 0.3s ease;
    }
    
    .teacher-card:hover .teacher-name:after {
        width: 100%;
    }
    
    .teacher-id {
        color: #64748b;
        font-size: 14px;
        margin-top: 4px;
        display: flex;
        align-items: center;
    }
    
    .teacher-id:before {
        content: '🆔';
        margin-right: 5px;
        font-size: 12px;
        opacity: 0.7;
    }
    
    .teacher-status {
        padding: 8px 16px;
        border-radius: 12px;
        font-size: 14px;
        font-weight: 600;
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        display: flex;
        align-items: center;
        justify-content: center;
        min-width: 100px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    .status-present {
        background: linear-gradient(135deg, #10b981, #34d399);
        color: white;
    }
    
    .status-present:hover {
        background: linear-gradient(135deg, #059669, #10b981);
        transform: scale(1.05);
        box-shadow: 0 4px 8px rgba(16, 185, 129, 0.3);
    }
    
    .status-absent {
        background: linear-gradient(135deg, #ef4444, #f87171);
        color: white;
    }
    
    .status-absent:hover {
        background: linear-gradient(135deg, #dc2626, #ef4444);
        transform: scale(1.05);
        box-shadow: 0 4px 8px rgba(239, 68, 68, 0.3);
    }
    
    .status-unmarked {
        background: linear-gradient(135deg, #9ca3af, #d1d5db);
        color: #1f2937;
    }
    
    .status-unmarked:hover {
        background: linear-gradient(135deg, #6b7280, #9ca3af);
        color: white;
        transform: scale(1.05);
        box-shadow: 0 4px 8px rgba(156, 163, 175, 0.3);
    }
    .section-header {
        background: linear-gradient(90deg, #ff6f61, #de425b);
        color: white;
        padding: 12px 20px;
        border-radius: 10px;
        margin: 20px 0 15px 0;
        font-weight: 700;
        font-size:20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    .select-all-btn {
        background: #66bb6a;
        color: white;
        border: none;
        padding: 7px 14px;
        border-radius: 6px;
        cursor: pointer;
        font-size: 14px;
        transition: background 0.3s ease-in-out;
    }
    .select-all-btn:hover {
        background: #43a047;

    }
    #  .scroll-container {
    #     max-height: 400px;
    #     overflow-y: auto;
    # }
    /* Calendar Styles */
        .calendar-container {
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .calendar-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        
        .calendar-title {
            font-size: 18px;
            font-weight: 600;
            color: #1a202c;
        }
        
        .calendar-nav {
            display: flex;
            gap: 10px;
        }
        
        .calendar-btn {
            background: #f3f4f6;
            border: none;
            border-radius: 8px;
            padding: 8px 12px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s ease;
        }
        
        .calendar-btn:hover {
            background: #e5e7eb;
        }
        
        .calendar-grid {
            display: grid;
            grid-template-columns: repeat(7, 1fr);
            gap: 8px;
        }
        
        .calendar-weekday {
            text-align: center;
            font-weight: 600;
            color: #6b7280;
            padding: 8px 0;
            font-size: 14px;
        }
        
        .calendar-day {
            text-align: center;
            padding: 10px 0;
            border-radius: 8px;
            transition: all 0.2s ease;
            cursor: pointer;
        }
        
        .calendar-day:hover {
            background: #f3f4f6;
        }
        
        .calendar-day.today {
            background: #e0e7ff;
            color: #4338ca;
            font-weight: 600;
        }
        
        .calendar-day.empty {
            visibility: hidden;
        }
    </style>
    """,
        unsafe_allow_html=True,
    )

    current_date = get_calendar_dates()
    month_name = current_date.strftime("%B %Y")
    calendar_days = generate_calendar_days(current_date)

    st.markdown(
        f"""
        <div class="dashboard-card">
            <div class="calendar-container">
                <div class="calendar-header">
                    <div class="calendar-title">{month_name}</div>
                    <div class="calendar-nav">
                        <button class="calendar-btn" onclick="prevMonth()">
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                                <path fill-rule="evenodd" d="M11.354 1.646a.5.5 0 0 1 0 .708L5.707 8l5.647 5.646a.5.5 0 0 1-.708.708l-6-6a.5.5 0 0 1 0-.708l6-6a.5.5 0 0 1 .708 0z"/>
                            </svg>
                        </button>
                        <button class="calendar-btn" onclick="nextMonth()">
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                                <path fill-rule="evenodd" d="M4.646 1.646a.5.5 0 0 1 .708 0l6 6a.5.5 0 0 1 0 .708l-6 6a.5.5 0 0 1-.708-.708L10.293 8 4.646 2.354a.5.5 0 0 1 0-.708z"/>
                            </svg>
                        </button>
                    </div>
                </div>
                <div class="calendar-grid">
                    {calendar_days}
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Calendar navigation buttons JavaScript
    st.markdown(
        """
        <script>
            function prevMonth() {
                window.parent.postMessage({type: 'streamlit:setComponentValue', value: -1}, '*');
            }
            
            function nextMonth() {
                window.parent.postMessage({type: 'streamlit:setComponentValue', value: 1}, '*');
            }
        </script>
        """,
        unsafe_allow_html=True,
    )
    data_manager_instance = st.session_state.data_manager

    # Ensure 'today' date is defined if needed (should be defined at the top of render_dashboard)
    today = get_ist_today()
    all_teachers_list_for_form = data_manager_instance.get_all_teachers(school_id)
    users_df = pd.DataFrame(all_teachers_list_for_form)
    attendance_today_df_form = data_manager_instance.get_attendance_report(
        school_id, start_date=today, end_date=today
    )
    marked_teachers_status = {}
    marked_teachers = []  # Initialize marked_teachers list

    if not attendance_today_df_form.empty:
        if (
            "teacher_id" in attendance_today_df_form.columns
            and "status" in attendance_today_df_form.columns
        ):
            marked_teachers_status = attendance_today_df_form.set_index("teacher_id")[
                "status"
            ].to_dict()
            # Also populate marked_teachers list for the logic that uses it
            marked_teachers = attendance_today_df_form["teacher_id"].tolist()

    # Create time objects for comparison
    # Assuming auto_hour and auto_minute are defined
    AUTO_ABSENT_TIME_OBJ = datetime.strptime(
        f"{auto_hour}:{auto_minute}", "%H:%M"
    ).time()
    current_system_time = datetime.now().time()

    # Initialize 'attendance_data' in session state if it doesn't exist
    if "attendance_data" not in st.session_state:
        st.session_state.attendance_data = {}

    # Initialize select all checkbox state
    if "mark_all_present" not in st.session_state:
        st.session_state.mark_all_present = False

    # Select all checkbox (Affects initial state on render)
    all_present = st.checkbox(
        " Mark all as present",
        value=st.session_state.mark_all_present,
        key="mark_all_present",
    )

    if not all_teachers_list_for_form:
        st.info("No teachers found for marking attendance.")
    else:
        # Create a form for marking attendance (Keep form structure)
        with st.form("admin_attendance_form"):
            st.markdown(
                """<div class='section-header'> 
            <div class="stat-icoon"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="white" viewBox="0 0 16 16">
                    <path d="M8 8a3 3 0 1 0 0-6 3 3 0 0 0 0 6Zm2-3a2 2 0 1 1-4 0 2 2 0 0 1 4 0Zm4 8c0 1-1 1-1 1H3s-1 0-1-1 1-4 6-4 6 3 6 4Zm-1-.004c-.001-.246-.154-.986-.832-1.664C11.516 10.68 10.289 10 8 10c-2.29 0-3.516.68-4.168 1.332-.678.678-.83 1.418-.832 1.664h10Z"/>
                </svg></div>
                <b>Teacher Attendance</B></div>""",
                unsafe_allow_html=True,
            )
            attendance_data_to_save = {}

            for teacher in all_teachers_list_for_form:
                teacher_id = teacher.get("teacher_id")
                teacher_name = teacher.get("name")

                if not teacher_id:
                    continue

                status = marked_teachers_status.get(teacher_id, "unmarked")
                initial_checkbox_state = all_present or (status == "present")

                st.markdown(
                    f"""
                <div class='teacher-card'>
                    <div class='teacher-info'>
                        <div class='teacher-name'>{teacher_name}</div>
                        <div class='teacher-id'>ID: {teacher_id}</div>
                    </div>
                    <div class='teacher-status status-{status}'>
                        {status.capitalize()}
                    </div>
                </div>
                """,
                    unsafe_allow_html=True,
                )

                is_present = st.checkbox(
                    f"Present",
                    value=initial_checkbox_state,
                    key=f"teacher_{teacher_id}_present_checkbox_form",
                )

                if is_present:
                    attendance_data_to_save[teacher_id] = "present"
                else:
                    attendance_data_to_save[teacher_id] = "absent"

            # --- Validation based on Auto-Absent Time (Keep this logic) ---

            submitted = st.form_submit_button(
                "Save Attendance", use_container_width=True
            )

            if submitted:
                # --- FINAL LOGIC FOR ATTENDANCE UPDATE ---
                
                # attendance_data_to_save mein har teacher ke liye checkbox ki current state hai ('present' ya 'absent')
                
                attendance_to_update_list = []

                for teacher_id, desired_status_from_checkbox in attendance_data_to_save.items():
                    
                    # Database mein teacher ka purana (original) status kya tha?
                    # marked_teachers_status humne form ke upar pehle hi fetch kar liya tha.
                    original_db_status = marked_teachers_status.get(teacher_id, "unmarked")

                    # Sirf unhi records ko update list mein daalo jinka status sach mein badla hai.
                    # Yeh logic bilkul sahi hai.
                    if original_db_status != desired_status_from_checkbox:
                        print(f"CHANGE DETECTED for {teacher_id}: From '{original_db_status}' -> To '{desired_status_from_checkbox}'")
                        attendance_to_update_list.append(
                            (teacher_id, desired_status_from_checkbox)
                        )

                # Agar update list mein kuch hai, tabhi database operation karo.
                if attendance_to_update_list:
                    print(f"INFO: Found {len(attendance_to_update_list)} teachers with status changes. Updating them in bulk.")

                    # data_manager_instance.bulk_update_attendance ab sahi se kaam karega
                    # kyunki database mein UNIQUE KEY constraint hai.
                    success_count = data_manager_instance.bulk_update_attendance(
                        school_id, attendance_to_update_list
                    )

                    # success_count ab actual updated records ki sankhya return karega.
                    if success_count > 0:
                        st.success(f"✅ Attendance updated for {success_count} teachers.")
                        # Page ko turant refresh karo taaki naya data dikhe.
                        st.rerun() 
                    else:
                        st.error("❌ Failed to update attendance. A database error may have occurred. Please check server logs.")
                else:
                    # Agar koi badlaav nahi hua, to user ko batao.
                    st.info("ℹ️ No changes were made to the attendance.")

    st.markdown(
        """
        <div style=" 
             padding: 10px 20px; border-radius: 10px; margin: 25px 0 15px 0; 
             color:#1e3a8a; font-weight: 600; font-size: 20px; 
             box-shadow: 0 4px 10px rgba(0,0,0,0.1);">
            <div style="display: flex; align-items: center;color:#1e3a8a;">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="white" style="margin-right: 10px;" viewBox="0 0 16 16">
                    <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z"/>
                    <path d="M10.97 4.97a.235.235 0 0 0-.02.022L7.477 9.417 5.384 7.323a.75.75 0 0 0-1.06 1.06L6.97 11.03a.75.75 0 0 0 1.079-.02l3.992-4.99a.75.75 0 0 0-1.071-1.05z"/>
                </svg>
                Detailed Attendance
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Get attendance data for today from database
    data_manager_instance = st.session_state.data_manager  # Get the instance
    attendance_for_table_df = data_manager_instance.get_attendance_report(
        school_id, start_date=today, end_date=today
    )

    # Fetch all teachers' names to merge
    all_teachers_list_names = data_manager_instance.get_all_teachers(
        school_id
    )  # Use instance
    teachers_names_df = pd.DataFrame(all_teachers_list_names)

    # Merge attendance data with teacher names
    if not attendance_for_table_df.empty and not teachers_names_df.empty:
        merged_df = pd.merge(
            attendance_for_table_df,
            teachers_names_df[["teacher_id", "name"]],
            on="teacher_id",
            how="left",
        )
    else:
        merged_df = pd.DataFrame()

    # Filter out unmarked teachers - only show present or absent in the table
    if not merged_df.empty:
        if "status" in merged_df.columns:
            filtered_df = merged_df[merged_df["status"].isin(["present", "absent"])]
        else:
            filtered_df = pd.DataFrame()
            st.warning("Status column missing in attendance data for table.")
    else:
        filtered_df = pd.DataFrame()

    if not filtered_df.empty:
        # Select and rename columns for display
        display_cols = ["date", "name", "teacher_id", "status", "timestamp"]
        existing_display_cols = [
            col for col in display_cols if col in filtered_df.columns
        ]

        display_df = filtered_df[existing_display_cols].copy()

        col_rename_map = {
            "date": "Date",
            "name": "Name",
            "teacher_id": "Teacher ID",
            "status": "Status",
            "timestamp": "Timestamp",
        }
        display_df.rename(columns=col_rename_map, inplace=True)

        # Display the dataframe
        st.dataframe(display_df, use_container_width=True)
    else:
        st.info(
            "No attendance data (Present or Absent) available to display for today."
        )
# test line to trigger git