import streamlit as st
from datetime import datetime
import pytz
def initialize_theme():
    """Initialize theme settings in session state"""
    if "dark_mode" not in st.session_state:
        st.session_state.dark_mode = False



def toggle_theme():
    """Toggle between light and dark mode"""
    st.session_state.dark_mode = not st.session_state.dark_mode

def apply_theme():
    """Apply the current theme to the app"""
    # Set theme based on dark mode toggle
    if st.session_state.get("dark_mode", False):
        # Dark theme
        st.markdown("""
        <style>
            :root {
                --main-bg-color: #1E1E1E;
                --secondary-bg-color: #2D2D2D;
                --text-color: #E0E0E0;
                --accent-color: #4B89DC;
            }
            
            .main .block-container {
                background-color: var(--main-bg-color);
                color: var(--text-color);
            }
            
            .st-emotion-cache-1avcm0n {
                background-color: var(--secondary-bg-color);
                color: var(--text-color);
            }
            
            .st-emotion-cache-18ni7ap {
                background-color: var(--secondary-bg-color);
                color: var(--text-color);
            }
            
            .st-emotion-cache-1d0aukl {
                color: var(--text-color);
            }
            
            .st-emotion-cache-10trblm {
                color: var(--text-color);
            }
            
            /* Sidebar styles */
            .st-emotion-cache-16txtl3 {
                background-color: var(--secondary-bg-color);
            }
            
            /* Form and input styles */
            .st-emotion-cache-q8sbsg {
                color: var(--text-color);
            }
            
            /* Buttons */
            .st-b7 {
                background-color: var(--accent-color);
            }
        </style>
        """, unsafe_allow_html=True)
    else:
        # Light theme (default)
        st.markdown("""
        <style>
            :root {
                --main-bg-color: #FFFFFF;
                --secondary-bg-color: #F0F2F6;
                --text-color: #262730;
                --accent-color: #3B82F6;
            }
        </style>
        """, unsafe_allow_html=True)