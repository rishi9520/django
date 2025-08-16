
import streamlit as st

import bcrypt

st.set_page_config(
    page_title="Teacher Arrangement System",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

def set_global_font():
    """
    पूरी ऐप पर Poppins फॉन्ट लागू करने के लिए CSS इंजेक्ट करता है।
    """
    # 1. Poppins फॉन्ट को Google Fonts से इम्पोर्ट करें
    # हमने अलग-अलग मोटाई (300 से 700) के फॉन्ट मंगवाए हैं
    font_import_link = """
        <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    """

    # 2. पूरी ऐप पर फॉन्ट लागू करने के लिए CSS
    # '*' (यूनिवर्सल सिलेक्टर) का मतलब है - "हर एक HTML एलिमेंट पर"
    font_style_css = """
        <style>
            html, body, [class*="st-"], .st-emotion-cache-16txtl3, h1, h2, h3, h4, h5, h6, p, li, label, button, input, select, textarea {
                font-family: 'Poppins', sans-serif !important;
            }
        </style>
    """
    
    # फॉन्ट इम्पोर्ट लिंक और स्टाइल दोनों को HTML में इंजेक्ट करें
    st.markdown(font_import_link, unsafe_allow_html=True)
    st.markdown(font_style_css, unsafe_allow_html=True)

set_global_font()
def inject_tawkto_script():
    """Tawk.to chat widget script ko inject karta hai."""
    
    # Hum st.markdown ki jagah st.components.v1.html ka istemal karenge.
    # Yeh scripts inject karne ke liye zyada reliable (bharosemand) hai.
    import streamlit.components.v1 as components
    
    tawkto_script = """
    <!--Start of Tawk.to Script-->
    <script type="text/javascript">
    var Tawk_API=Tawk_API||{}, Tawk_LoadStart=new Date();
    (function(){
    var s1=document.createElement("script"),s0=document.getElementsByTagName("script")[0];
    s1.async=true;
    s1.src='https://embed.tawk.to/687226bbf5b51b190aaefe49/1ivuuekf3';
    s1.charset='UTF-8';
    s1.setAttribute('crossorigin','*');
    s0.parentNode.insertBefore(s1,s0);
    })();
    </script>
    <!--End of Tawk.to Script-->
    """
    components.html(tawkto_script, height=0)

from urllib.parse import quote
import streamlit.components.v1 as components
import pandas as pd
import os
import pathlib
from streamlit_lottie import st_lottie
import re  # Keeping original import
import json
import data_manager
import traceback
from auth import check_password
from mysql.connector import Error  #
from auto_marker import create_railway_optimized_automarker 
from components.dashboard import render_dashboard
from components.admin_controls import render_admin_page
from components.reports import render_reports_page
from components.arrangements import render_arrangements_page
from components.schedule_manager import render_schedule_manager_page
from components.teacher_management import render_teacher_management_page
from components.substitute_pool import render_substitute_pool_page
from components.coverage_tracking import render_coverage_tracking_page
from components.legal_pages import render_terms_and_conditions, render_contact_page
import streamlit.components.v1 as components
from urllib.parse import quote
from streamlit.components.v1 import html
def load_svg(file_path):
    """Load SVG content from a file"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except (FileNotFoundError, Exception) as e:
        print(f"Error loading SVG file {file_path}: {e}")
        return ""


def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


load_css("static/style.css")
from streamlit.web.server.server import Server

def get_school_id_from_hostname():
    """
    Railway dwara provide kiye gaye 'Host' header se school ID (subdomain) nikalta hai.
    """
    try:
        # Streamlit 1.18+ mein headers access karne ka standard tareeka
        session_info = Server.get_current()._get_session_info()
        # Railway is header ko set karta hai, jismein original host name hota hai.
        # Example: "school-a.skoolhub.in"
        host = session_info.headers.get('Host', '').lower()

        # Agar host aapke main domain par end hota hai
        if host and host.endswith("skoolhub.in"):
            subdomain = host.split('.')[0]
            # 'www' ya khali subdomain ko ignore karein
            if subdomain and subdomain != 'www':
                st.session_state['subdomain_school_id'] = subdomain
                print(f"DEBUG: Subdomain '{subdomain}' found from host '{host}'")
                return subdomain
        return None
    except Exception as e:
        # Agar local development mein chala rahe hain, to yeh fail ho sakta hai, jo theek hai.
        print(f"INFO: Could not get hostname, likely running locally. Error: {e}")
        return None

# Aap is function ko app ke shuru mein ek baar call kar sakte hain.
# Aur result ko session_state mein store kar sakte hain.


def serve_static_file(filename):
    filepath = os.path.join("static", filename)
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as file:
            st.markdown(
                f'<script type="application/json" id="{filename}">{file.read()}</script>',
                unsafe_allow_html=True,
            )
    else:
        print(f"Warning: Static file not found: {filepath}")


serve_static_file("manifest.json")


def create_styled_component(
    body_html_content, component_css_styles, height=100, font_awesome_needed=False
):
    font_awesome_link = (
        '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">'
        if font_awesome_needed
        else ""
    )

    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap" rel="stylesheet">
        {font_awesome_link}
        <style>
            body {{ margin: 0; padding: 0; font-family: 'Poppins', sans-serif; }}
            /* Add any other common body styles here if needed */
            {component_css_styles} 
        </style>
    </head>
    <body>
        {body_html_content}
    </body>
    </html>
    """
    components.html(full_html, height=height)




def svg_with_style(svg_content, color="currentColor", size=24):
    colored_svg = svg_content.replace('stroke="currentColor"', f'stroke="{color}"')
    colored_svg = colored_svg.replace('fill="currentColor"', f'fill="{color}"')
    return f"""<div style="display: inline-block; width: {size}px; height: {size}px;">{colored_svg}</div>"""


def load_lottie_file(filepath):
    try:
        if pathlib.Path(filepath).exists():
            with open(filepath, "r") as f:
                return json.load(f)
        else:
            return None
    except Exception as e:
        print(f"Error loading animation: {e}")
        return None


if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user" not in st.session_state:
    st.session_state.user = None
if "school_id" not in st.session_state:
    st.session_state.school_id = None
if "user_details" not in st.session_state:
    st.session_state.user_details = None
# if "school_details" not in st.session_state:
#     st.session_state.school_details = None
if 'subdomain_school_id' not in st.session_state:
    st.session_state.subdomain_school_id = get_school_id_from_hostname() 

if "current_page" not in st.session_state:
    st.session_state.current_page = "dashboard"
if "data_manager" not in st.session_state or st.session_state.data_manager is None:
    try:
        st.session_state.data_manager = data_manager.DataManager()
        print("DataManager instance initialized in session state.")
    except Exception as e:
        st.error(f"CRITICAL: Error initializing DataManager: {e}")
        st.session_state.data_manager = None

if "automarker" not in st.session_state:
    st.session_state.automarker = None

st.markdown(  # PWA Service Worker Script
    """
<script>
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/static/sw.js')
        .then(() => console.log('Service Worker Registered'))
        .catch(err => console.log('Service Worker Registration Failed:', err));
    }
</script>
""",
    unsafe_allow_html=True,
)


# --- Sidebar Content (MODIFIED Logout) ---
with st.sidebar:
    # Logo display logic (Keep as is)
    school_details_for_logo = st.session_state.get("school_details")
    logo_url = (
        school_details_for_logo.get("logourl") if school_details_for_logo else None
    )
    if logo_url:
        st.image(logo_url, width=150)
    else:
        st.image("attached_assets/logo.png", width=150)

    school_details = st.session_state.get("school_details")
    default_app_title = (
        "Skoolhub.in"  # Fallback title before login or if name not found
    )
    school_name_to_display = default_app_title
    if school_details and "school_name" in school_details:
        school_name_to_display = school_details["school_name"]
    if (
        st.session_state.authenticated
        and school_details
        and "school_name" in school_details
    ):
        # User is logged in and school details are available
        display_text = school_details["school_name"]
        title_tag = "h1"  # Use h2 as was in the previous full code
        margin_left = "10px"  # Margin as was in the previous full code
    else:
        # User is NOT logged in OR school details not available/incomplete
        # Display the general app title
        display_text = default_app_title
        title_tag = "h1"  # Use h2
        margin_left = "10px"  # Margin
    # Your SVG icon embedded directly
    sidebar_header_html = """
    <div style="
        display: flex; 
        align-items: center; 
        gap: 16px; /* Creates space between icon and text */
        padding: 5px 25px; /* Vertical and horizontal padding */
        margin-bottom: 35px; /* Space below the entire header */
        justify-content: center; /* Center the items horizontally */
    ">
        <svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" fill="silver" class="sidebar-icon" viewBox="0 0 16 16">
            <path d="M8.211 2.047a.5.5 0 0 0-.422 0l-7.5 3.5a.5.5 0 0 0 .025.917l7.5 3a.5.5 0 0 0 .372 0L14 7.14V13a1 1 0 0 0-1 1v2h3v-2a1 1 0 0 0-1-1V6.739l.686-.275a.5.5 0 0 0 .025-.917l-7.5-3.5Z"/>
            <path d="M4.176 9.032a.5.5 0 0 0-.656.327l-.5 1.7a.5.5 0 0 0 .294.605l4.5 1.8a.5.5 0 0 0 .372 0l4.5-1.8a.5.5 0 0 0 .294-.605l-.5-1.7a.5.5 0 0 0-.656-.327L8 10.466 4.176 9.032Z"/>
        </svg>
        <h1 style=" 
            padding: 0; 
            font-family: 'Poppins', sans-serif;
            font-size: 1.6rem;
            color:silver;
            font-weight: 700;
            background: linear-gradient(45deg, #FFFFFF, #D1D5DB) !important;
            -webkit-background-clip: text !important;
            -webkit-text-fill-color: transparent !important;
            text-shadow: 0px 2px 4px rgba(0, 0, 0, 0.2);
        ">
            {school_name_placeholder}
        </h1>
    </div>
    """
    # Use .format() to insert the dynamic school name

    formatted_html = sidebar_header_html.format(school_name_placeholder=display_text)
    st.markdown(
        formatted_html,
        unsafe_allow_html=True,
    )

    # --- Theme Toggle (Keep as is) ---
    if st.session_state.authenticated:

    # 1. सेशन स्टेट को शुरू करें (अगर पहले से नहीं है)
        if "dark_mode" not in st.session_state:
          st.session_state.dark_mode = False

    # 2. डार्क मोड के लिए विस्तृत CSS
        DARK_THEME_CSS = """
        <style>
            /* --- डार्क मोड के वैरिएबल --- */
            :root {
                --dark-bg-main: #0E1117;
                --dark-bg-secondary: #161B22;
                --dark-text-main: #CDD9E5;
                --dark-text-strong: #FFFFFF;
                --dark-text-light: #7d8590;
                --dark-border-color: #30363d;
                --dark-accent-color: #58a6ff;
            }
            
            /* --- ग्लोबल स्टाइल --- */
            body, .stApp {
                background-color: var(--dark-bg-main) !important;
                color: var(--dark-text-main) !important;
            }
            [data-testid="stSidebar"] {
                background-color: var(--dark-bg-secondary) !important;
                border-right: 1px solid var(--dark-border-color) !important;
            }
            h1, h2, h3, h4, h5, h6 {
                color: var(--dark-text-strong) !important;
            }
            p, li, label, .st-emotion-cache-16idsys p, .st-emotion-cache-1avcm0n p {
                color: var(--dark-text-main) !important;
            }

            /* --- बटन्स --- */
            .stButton>button {
                background-color: #21262d !important;
                color: var(--dark-text-main) !important;
                border: 1px solid var(--dark-border-color) !important;
            }
            .stButton>button:hover {
                border-color: var(--dark-accent-color) !important;
                color: var(--dark-accent-color) !important;
                background-color: #30363d !important;
            }
            .stDownloadButton>button {
                background-color: var(--dark-accent-color) !important;
                color: var(--dark-text-strong) !important;
            }
            
            /* --- इनपुट और सेलेक्ट बॉक्स --- */
            div[data-testid="stTextInput"] input, 
            div[data-testid="stSelectbox"] div[data-baseweb="select"] > div,
            div[data-testid="stDateInput"] input {
                background-color: var(--dark-bg-secondary) !important;
                color: var(--dark-text-main) !important;
                border: 1px solid var(--dark-border-color) !important;
            }

            /* --- डेटाफ्रेम और टेबल्स --- */
            div[data-testid="stDataFrame"] { border: 1px solid var(--dark-border-color); }
            .st-emotion-cache-1wbqy5l { background-color: var(--dark-bg-secondary); }
            .st-emotion-cache-a51556:hover { background-color: #21262d; }
            
            /* --- आपके कस्टम कॉम्पोनेन्ट --- */
            /* प्रोफ़ाइल कार्ड */
            .pro-card {
                background: rgba(33, 38, 45, 0.7) !important;
                backdrop-filter: blur(10px) !important;
                -webkit-backdrop-filter: blur(10px) !important;
                border: 1px solid var(--dark-border-color) !important;
            }
            .pro-title, .pro-info-item, .pro-avatar { color: var(--dark-text-strong) !important; }
            .pro-subtitle { color: var(--dark-text-light) !important; }
            .pro-info-item svg { color: var(--dark-accent-color) !important; }

            /* डैशबोर्ड कार्ड्स */
            .stat-v2-card, .feature1-card, .auto-absent-notice {
                background: var(--dark-bg-secondary) !important;
                border: 1px solid var(--dark-border-color) !important;
            }
            .stat-v2-card .title, .stat-v2-card .subtitle, 
            .feature1-description, .notice-text { 
                color: var(--dark-text-main) !important; 
            }
            .stat-v2-card .value, .feature1-title, .notice-title { 
                color: var(--dark-text-strong) !important; 
            }
            
            /* Lottie एनीमेशन */
            .stLottie div[role="img"] {
                 filter: invert(0.9) hue-rotate(180deg) brightness(1.2);
            }
         </style>
        """
    
    # 3. CSS को डायनामिक रूप से इंजेक्ट करें
    # अगर डार्क मोड ऑन है, तो CSS इंजेक्ट करो, वरना कुछ नहीं
        if st.session_state.dark_mode:
         st.markdown(DARK_THEME_CSS, unsafe_allow_html=True)
    
    # 4. थीम टॉगल बटन
        def toggle_theme():
         st.session_state.dark_mode = not st.session_state.dark_mode

        icon = ":material/light_mode:" if st.session_state.dark_mode else ":material/dark_mode:"
        button_text = "Enable Light Mode" if st.session_state.dark_mode else "Enable Dark Mode"

    # यह बटन अब सही से काम करेगा
        if st.button(
         f"{icon} {button_text}",
         key="theme_switch",
         on_click=toggle_theme,
         use_container_width=True,
        ):
        # on_click खुद ही rerun करता है, इसलिए यहाँ कुछ करने की ज़रूरत नहीं है
          pass
    
        st.divider()
        pages = {  # Keep original pages
            "dashboard": (":material/dashboard:", "Dashboard"),
            "billing": (":material/payment:", "Billing & Subscriptions"),
            "admin": (":material/admin_panel_settings:", "Administrative Controls"),
            "arrangements": (":material/swap_horiz:", "Arrangements"),
            "reports": (":material/bar_chart:", "Reports"),
           
            "schedule_manager": (":material/edit_calendar:", "Schedule Manager"),
            "teacher_management": (":material/person_add:", "Teacher Management"),
            "substitute_pool": (":material/people_alt:", "Substitute Teachers"),
            "coverage_tracking": (":material/analytics:", "Class Coverage"),
            "terms": (":material/gavel:", "Terms & Conditions"),
            "contact": (":material/contact_phone:", "Contact Us"),
        }
        for page, (icon, label_text) in pages.items():
            display_label = f"{icon} {label_text}"
            if st.button(display_label, key=f"nav_{page}", use_container_width=True):
                st.session_state.current_page = page
                st.rerun()
        st.divider()

        # --- User Profile Card (Keep as is) ---
        user_details = st.session_state.get("user_details")
        if user_details:
            first_letter = (
                user_details.get("name", "U")[0].upper()
                if user_details.get("name")
                else "U"
            )

        profile_card_html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            
            <!-- स्टेप 1: Poppins फॉन्ट को Google Fonts से इम्पोर्ट करें -->
            <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap" rel="stylesheet">
            
            <style>
                /* स्टेप 2: यहाँ Poppins फॉन्ट और अन्य स्टाइल लागू करें */
                body {{
                    font-family: 'Poppins', sans-serif;
                    background-color: transparent; /* ताकि यह साइडबार के रंग के साथ मिल जाए */
                    margin: 0;
                    padding: 0;
                }}
                
                .pro-card {{
                    background: rgba(44, 62, 80, 0.45); /* सेमी-ट्रांसपेरेंट डार्क बैकग्राउंड */
                    backdrop-filter: blur(12px);
                    -webkit-backdrop-filter: blur(12px);
                    border-radius: 20px;
                    padding: 25px;
                    border: 1px solid rgba(255, 255, 255, 0.18);
                    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2);
                    color: #ecf0f1; /* हल्का सफेद टेक्स्ट */
                }}
                
                .pro-header {{
                    display: flex;
                    align-items: center;
                    margin-bottom: 25px;
                    padding-bottom: 20px;
                    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                }}
                
                .pro-avatar {{
                    width: 60px; height: 60px;
                    background: linear-gradient(135deg, #8e44ad, #3498db); /* पर्पल-ब्लू ग्रेडिएंट */
                    border-radius: 50%;
                    display: flex; align-items: center; justify-content: center;
                    margin-right: 20px; font-size: 28px; font-weight: 700; color: white;
                    flex-shrink: 0;
                }}
                
                .pro-title-wrapper {{ line-height: 1.3; }}
                .pro-title {{ font-size:18px; font-weight: 600; margin: 0; color: #ffffff; }}
                .pro-subtitle {{ font-size: 0.85rem; font-weight: 500; color: #bdc3c7; text-transform: uppercase; }}
                .pro-info {{ display: flex; flex-direction: column; gap: 18px; }}
                .pro-info-item {{ display: flex; align-items: flex-start; font-size: 0.95rem; color: #ecf0f1; font-weight: 500; }}
                .pro-info-item svg {{ margin-right: 15px; margin-top: 3px; min-width: 18px; flex-shrink: 0; color: #3498db; }}
                .pro-info-item span {{ word-break: break-all; }}
            </style>
        </head>
        <body>
            <!-- प्रोफ़ाइल कार्ड का HTML -->
            <div class="pro-card">
                <div class="pro-header">
                    <div class="pro-avatar">{first_letter}</div>
                    <div class="pro-title-wrapper">
                        <h2 class="pro-title">{user_details.get('name', 'N/A')}</h2>
                        <p class="pro-subtitle">Administrator</p>
                    </div>
                </div>
                <div class="pro-info">
                    <div class="pro-info-item">
                        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="currentColor" viewBox="0 0 16 16"><path d="M6 3.5a.5.5 0 0 1 .5-.5h8a.5.5 0 0 1 .5.5v9a.5.5 0 0 1-.5-.5h-8a.5.5 0 0 1-.5-.5v-2a.5.5 0 0 0-1 0v2A1.5 1.5 0 0 0 6.5 14h8a1.5 1.5 0 0 0 1.5-1.5v-9A1.5 1.5 0 0 0 14.5 2h-8A1.5 1.5 0 0 0 5 3.5v2a.5.5 0 0 0 1 0v-2z"/><path d="M11.854 8.354a.5.5 0 0 0 0-.708l-3-3a.5.5 0 1 0-.708.708L10.293 7.5H1.5a.5.5 0 0 0 0 1h8.793l-2.147 2.146a.5.5 0 0 0 .708.708l3-3z"/></svg>
                        <span><strong>School ID:</strong> {st.session_state.get('school_id', 'N/A')}</span>
                    </div>
                    <div class="pro-info-item">
                        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="currentColor" viewBox="0 0 16 16"><path d="M.05 3.555A2 2 0 0 1 2 2h12a2 2 0 0 1 1.95 1.555L8 8.414.05 3.555ZM0 4.697v7.104l5.803-3.558L0 4.697ZM6.761 8.83l-6.57 4.027A2 2 0 0 0 2 14h12a2 2 0 0 0 1.808-1.144l-6.57-4.027L8 9.586l-1.239-.757Zm3.436-.586L16 11.803V4.697l-5.803 3.546Z"/></svg>
                        <span>{user_details.get('email', 'N/A')}</span>
                    </div>
                    <div class="pro-info-item">
                        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="currentColor" viewBox="0 0 16 16"><path fill-rule="evenodd" d="M1.885.511a1.745 1.745 0 0 1 2.612.163L6.29 2.98c.329.423.445.974.315 1.494l-.547 2.19a.678.678 0 0 0 .178.643l2.457 2.457a.678.678 0 0 0 .644.178l2.189-.547a1.745 1.745 0 0 1 1.494.315l2.306 1.794c.829.645.905 1.87.163 2.611l-1.034 1.034c-.74.74-1.846 1.065-2.877.702a18.634 18.634 0 0 1-7.01-4.42 18.634 18.634 0 0 1-4.42-7.009c-.362-1.03-.037-2.137.703-2.877L1.885.511z"/></svg>
                        <span>{user_details.get('phone', 'N/A')}</span>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        # कंपोनेंट को रेंडर करें और उसकी हाइट सेट करें
        components.html(profile_card_html, height=320)


        logout_icon = ":material/logout:"
        logout_label_text = "Logout"
        display_logout_label = f"{logout_icon} {logout_label_text}"

        if st.sidebar.button(
            display_logout_label,
            type="secondary",
            use_container_width=True,
            key="logout_button_key",
        ):

            keys_to_clear = [
                "authenticated",
                "user",
                "school_id",
                "user_details",
                "school_details",
                "current_page",
                "automarker" # ⭐️⭐️⭐️ FIX 3: Logout par automarker ko bhi clear karein ⭐️⭐️⭐️
            ]
            for key in keys_to_clear:
                if key in st.session_state:
                    del st.session_state[key]
            st.session_state.authenticated = False
            st.session_state.current_page = "dashboard"

            st.success("Logged out successfully.")
            st.rerun()

inject_tawkto_script()
if not st.session_state.authenticated:

    # lottie_animation = load_lottie_file("attached_assets/lottie_animation.json")
    # st_lottie(lottie_animation, height=130, key="login_lottie")

    st.markdown(  # Copied from original
        """
            <div style="text-align: center; margin-top: -70px;">
                <h1 style="font-weight: 700;
                background: linear-gradient(90deg, #1E3A8A, #3B82F6);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                 display: inline-block;">🎓 Teacher Attendance System</h1>
                <p style=" font-weight: 600;
        color: #6c7293;
        font-size: 1.1rem;">"Intelligent automation for school management with real-time arrangements"</p>
            </div>
            """,
        unsafe_allow_html=True,
    )
    subdomain_id = st.session_state.get('subdomain_school_id')
    # --- Normal Login Flow (MODIFIED DB handling) ---
    with st.form("login_form"):
        feature_badges_body_html = """
<div class="features-container">
    <div class="feature-badge">
        <i class="fas fa-award"></i>
        <span>Premium</span>
    </div>
    <div class="feature-badge">
        <i class="fas fa-bolt"></i>
        <span>Fast</span>
    </div>
    <div class="feature-badge">
        <i class="fas fa-shield-alt"></i>
        <span>Secure</span>
    </div>
</div>
"""

        # 2. Define the CSS styles for the badges
        feature_badges_css = """
:root {
    /* Define your CSS variables here if they are not globally defined */
    /* Agar yeh variables aapne pehle se main CSS block mein define kiye hain, to yahan dobara karne ki zaroorat nahi */
    --glass-border: rgba(255, 255, 255, 0.2); /* Example */
    --premium-gold: #FFD700; /* Example */
    --neon-blue: #00C9FF;    /* Example */
    --success-green: #28A745; /* Example */
}

.features-container {
    display: flex;
    justify-content: center;
    gap: 1.5rem;
    
    flex-wrap: wrap;
}

.feature-badge {
    background: linear-gradient(135deg, rgba(0, 212, 255, 0.1), rgba(139, 92, 246, 0.1)); 
    border: 1px solid var(--glass-border); 
    border-radius: 20px; 
    padding: 10px 20px; /* Thodi zyada padding */
    backdrop-filter: blur(8px); /* Thoda kam blur for better readability */
    display: flex; /* Icon aur text ko align karne ke liye */
    align-items: center;
    transition: transform 0.3s ease, box-shadow 0.3s ease; /* Hover effect */
}

.feature-badge:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
}

.feature-badge i {
    margin-right: 8px; /* Icon aur text ke beech space */
    font-size: 1.1rem; /* Icon ka size */
}

.feature-badge .fa-award {
    color: var(--premium-gold);
}
.feature-badge .fa-bolt {
    color: var(--neon-blue);
}
.feature-badge .fa-shield-alt {
    color: var(--success-green);
}

.feature-badge span {
    color: #141212; /* Text color */
    font-size: 0.95rem; /* Thoda sa bada font */
    font-weight: 600;
}
"""

        # 3. Call the helper function to render the component
        # Font Awesome ki zaroorat hai, isliye font_awesome_needed=True
        # Height ko badges ke content ke hisaab se adjust karein
        create_styled_component(
            body_html_content=feature_badges_body_html,
            component_css_styles=feature_badges_css,
            height=100,  # Aapko is height ko adjust karna pad sakta hai
            font_awesome_needed=True,
        )
        font_awesome_link = '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">'
        login_heading_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap" rel="stylesheet">
        {font_awesome_link} 
    <style>
        body {{
            
            padding: 0;
            margin-top:-40px;
            font-family: 'Poppins', sans-serif;
            display: flex; /* To center content */
            justify-content: center; /* To center content */
            align-items: center; /* To center content */
           
        }}
        .container {{
        
            text-align: center;
            /* margin-bottom: 2rem;  -- Yeh component ki height se control hoga */
        }}
        .login-prompt {{
            color: #475569; /* Removed !important, should not be needed here */
            font-weight: 600; /* 550 is not a standard value, 500 or 600 */
            font-family: 'Poppins', sans-serif; 
            font-size: 2.1rem;
            display: flex; /* For icon and text alignment */
            align-items: center;
            justify-content: center;
        }}
        .login-prompt .fas {{ /* Targeting Font Awesome icon */
            color: #8A2BE2; /* Example neon-purple, aap apna variable daal sakte hain ya seedha color */
            margin-right: 10px; /* Space between icon and text */
        }}
    </style>
</head>
<body>
    <div class="container">
        <p class="login-prompt">
            <i class="fas fa-user-check"></i>
            Please sign into your account
        </p>
        </div>
        </body>
        </html>
        """
        components.html(login_heading_html, height=100)
        st.markdown(
            """
                <style>
                    .input-with-icon {
                        display: flex;
                        align-items: center;
                        margin-bottom: -10px; /* Adjust to reduce space before input */
                    }
                    .input-with-icon i {
                        color: #3b82f6; /* Icon color */
                        margin-right: 10px;
                        font-size: 1.1rem;
                    }
                    .input-with-icon span {
                        font-weight: 600;
                        font-family: 'Poppins', sans-serif;
                        font-size: 1rem;
                        color: #475569;
                    }
                </style>
                <div class="input-with-icon">
                    <i class="fas fa-user"></i>
                    <span>Username</span>
                </div>
                """,
            unsafe_allow_html=True,
        )

        username = st.text_input(
            "Username_label",
            placeholder="Enter your username",
            help="Your registered username",
            key="login_username",
            label_visibility="collapsed",
        )
        st.markdown(
            """
                <div class="input-with-icon" style="margin-top: 1rem;">
                    <i class="fas fa-lock"></i>
                    <span>Password</span>
                </div>
                """,
            unsafe_allow_html=True,
        )
        password = st.text_input(
            "Password_label",
            type="password",
            placeholder="Enter your password",
            help="Your account password",
            key="login_password",
            label_visibility="collapsed",
        )
        st.markdown(
            """
                <div class="input-with-icon" style="margin-top: 1rem;">
                    <i class="fas fa-school"></i>
                    <span>School ID</span>
                </div>
                """,
            unsafe_allow_html=True,
        )
        if subdomain_id:
            st.text_input(
                "School ID_label",
                value=subdomain_id,  # Set the value from subdomain
                key="login_school_id",
                disabled=True,      # Disable the input
                label_visibility="collapsed",
            )
        else:
            # Agar subdomain se ID nahi mili, to user ko enter karne dein
            st.text_input(
                "School ID_label",
                placeholder="(School identifier)",
                key="login_school_id",
                label_visibility="collapsed",
            )

        remember_me = st.checkbox("Remember me")
        submitted = st.form_submit_button(
            "🚀 Sign In Securly", use_container_width=True
        )

        if submitted:
            form_username = st.session_state.login_username
            form_password = st.session_state.login_password
            form_school_id = st.session_state.login_school_id
            with st.spinner("🔐 Authenticating..."):
                user_details = check_password(
                        form_username, form_password, form_school_id
                )  # Pass only needed args
                print(f"DEBUG main.py: check_password returned: {user_details}")

                if user_details:
                    # Check if it's a subscription error
                    if isinstance(user_details, dict) and 'error' in user_details:
                        st.error(f"🚫 {user_details['error']}")
                        st.markdown("""
                        <div style="background: linear-gradient(135deg, #1e293b 0%, #334155 100%); 
                                    padding: 1.5rem; border-radius: 12px; margin: 1rem 0; text-align: center;">
                            <p style="color: white; margin: 0; font-size: 1.1rem;">
                                📞 <strong>Contact us for subscription plans:</strong>
                            </p>
                            <p style="color: #94a3b8; margin: 0.5rem 0 0 0;">
                                Email: rk.coders.help@gmail.com | Phone: +91 98765-43210
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        # User authentication successful - proceed with login
                        st.session_state.authenticated = True
                        st.session_state.user = form_username
                        st.session_state.school_id = form_school_id
                    data_manager_instance = st.session_state.data_manager
                    if data_manager_instance is None:
                        st.error("DataManager failed to initialize. Cannot proceed.")
                        st.session_state.authenticated = False
                    else:
                        st.session_state.user_details = user_details
                        school_details = data_manager_instance.get_school_details(
                            form_school_id
                        )

                        if school_details:
                            st.session_state.school_details = school_details
                        else:
                            st.warning(
                                f"Could not fetch details for school ID: {form_school_id}."
                            )
                            st.session_state.school_details = None
                        
                        # Initialize AutoMarker after successful login
                        try:
                            if st.session_state.get("automarker") is None:
                                print("INFO main.py: Initializing AutoMarker after successful login.")
                                st.session_state.automarker = create_railway_optimized_automarker(
                                    form_school_id, data_manager_instance
                                )
                                if st.session_state.automarker:
                                    print("SUCCESS: AutoMarker background thread started.")
                        except Exception as e:
                            print(f"WARNING: Could not initialize AutoMarker: {e}")
                            # Don't block login if AutoMarker fails

                        st.success("✅ Login successful! Welcome back!")
                        st.session_state.current_page = "dashboard"
                        st.rerun()
                else:
                    # Login Failed
                    st.error("Invalid School ID, username, or password.")
    new_user_section_body_html = """
    <div class="new-user-card">
        <p class="main-prompt">
            <i class="fas fa-user-plus"></i>
            New to Skoolhub? Contact Admin for access
        </p>
        <div class="features-inline">
            <span><i class="fas fa-shield-alt"></i> Secure</span>
            <span><i class="fas fa-check-circle"></i> Reliable</span>
            <span><i class="fas fa-star"></i> Professional</span>
        </div>
        <p class="copyright-text">
            © 2025 Skoolhub.in - Professional Teacher Management System
        </p>
    </div>
    """

    # 3. Define the CSS styles for this specific section
    new_user_section_css = """
    .new-user-card {
        text-align: center;
        margin-top: 7rem;
        padding: 1.5rem;
        
        
        font-family: 'Poppins', sans-serif;
        border-radius: 16px;
        /* If main page BG is dark, use rgba(255, 255, 255, 0.1) */
        backdrop-filter: blur(10px); /* Reduced blur from 15px for sharper text */
        border: 1px solid rgba(255, 255, 255, 0.12); /* Subtle border */
        
    }

    .main-prompt {
        color: #475569; 
        font-weight: 600;
        font-size: 1.1rem; /* Consistent font size */
        margin-bottom: 1.2rem; /* Adjusted margin */
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .main-prompt .fa-user-plus {
        color: black; /* Bright cyan */
        margin-right: 10px;
        font-size: 1.25rem;
    }

    .features-inline {
        display: flex;
        color: black;
        justify-content: center;
        gap: 2rem;
        margin: 1.2rem 0; /* Adjusted margin */
        flex-wrap: wrap;
    }

    .features-inline span {
        font-weight: 600;
        color: #6c7293;
        font-size: 0.9rem;
        font-weight: 500; /* Slightly less bold than main prompt */
        display: flex;
        align-items: center;
    }

    .features-inline i {
        margin-right: 7px;
        font-size: 0.95rem;
    }

    .features-inline .fa-shield-alt { color: #A78BFA; } /* Lighter purple */
    .features-inline .fa-check-circle { color: #34D399; } /* Lighter green */
    .features-inline .fa-star { color: #FBBF24; } /* Lighter gold/amber */

    .copyright-text {
        font-weight: 600;
        background: linear-gradient(90deg, #1E3A8A, #3B82F6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 0.85rem;
        margin-top: 1.2rem; /* Adjusted margin */
    }
    """

    # 4. Call the helper function
    create_styled_component(
        body_html_content=new_user_section_body_html,
        component_css_styles=new_user_section_css,
        height=260,  # Is height ko apne content ke anusaar adjust karein
        font_awesome_needed=True,
    )

    # Pricing Plans & Contact for Non-Logged Users
    st.markdown("---")
    st.markdown("### 💎 Choose Your Plan")
    st.write("Professional school management solutions starting from just ₹2,000/month")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("""
        **🎯 Smart School - ₹2,000/month**
        
        ✓ Auto Teacher Arrangements  
        ✓ WhatsApp Notifications  
        ✓ Basic Analytics  
        ✓ Up to 100 Teachers  
        ✓ Email Support
        
        *₹22,000/year (Save 8%)*
        """)
    
    with col2:
        st.success("""
        **👑 Premium School - ₹2,500/month** ⭐ RECOMMENDED
        
        ✓ Everything in Smart School  
        ✓ Advanced Analytics  
        ✓ Unlimited Teachers  
        ✓ Priority Support  
        ✓ Custom Integrations
        
        *₹27,000/year (Save 10%)*
        """)
    
    st.markdown("---")
    st.markdown("### 🚀 Ready to Get Started?")
    st.write("**Contact us for a FREE DEMO or to set up your school's attendance system today!**")
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.info("""
        **📞 Call/WhatsApp**
        
        **+91 9520496351**
        
        Available 9 AM - 8 PM
        """)
    
    with col4:
        st.info("""
        **📧 Email Support**
        
        **support@rkcoders.com**
        
        Quick Response Guaranteed
        """)
    
    st.success("⚡ Free Demo Setup • 📱 WhatsApp Integration • 🎯 Custom Training • 🚀 Same Day Deployment")
else:
    current_school_id = st.session_state.get("school_id")
    data_manager_instance = st.session_state.get("data_manager")

    if current_school_id is None or data_manager_instance is None:
        st.error(
            "Application state error. School ID or DataManager missing. Please log in again."
        )
        keys_to_clear = [
            "authenticated",
            "user",
            "school_id",
            "user_details",
            "school_details",
            "current_page",
            "automarker" # ⭐️⭐️⭐️ FIX 3 (part 2): Logout par automarker ko bhi clear karein ⭐️⭐️⭐️
        ]
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
        st.session_state.authenticated = False
        st.rerun()
    else:

        current_page = st.session_state.get("current_page", "dashboard")

        if current_page == "dashboard":
            render_dashboard(current_school_id, data_manager_instance)
        elif current_page == "admin":
            render_admin_page(current_school_id, data_manager_instance)
        elif current_page == "billing":
            from components.billing import render_billing_page
            render_billing_page()
        elif current_page == "arrangements":
            render_arrangements_page(current_school_id, data_manager_instance)
        elif current_page == "reports":
            render_reports_page(current_school_id, data_manager_instance)
        elif current_page == "schedule_manager":
            render_schedule_manager_page(current_school_id, data_manager_instance)
        elif current_page == "teacher_management":
            render_teacher_management_page(current_school_id, data_manager_instance)
        elif current_page == "substitute_pool":
            render_substitute_pool_page(current_school_id, data_manager_instance)
        elif current_page == "coverage_tracking":
            render_coverage_tracking_page(current_school_id, data_manager_instance)
        elif current_page == "terms":
            render_terms_and_conditions(current_school_id, data_manager_instance)
        elif current_page == "contact":
            render_contact_page(current_school_id, data_manager_instance)
        else:
            # Fallback to dashboard (Keep this logic)
            st.warning(f"Invalid page '{current_page}'. Redirecting to dashboard.")
            st.session_state.current_page = "dashboard"
            render_dashboard(current_school_id, data_manager_instance)
