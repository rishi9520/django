
import streamlit as st
from datetime import datetime
import pytz
def get_ist_today():
    """
    Returns the current date in the 'Asia/Kolkata' (IST) timezone.
    This function is crucial for ensuring date consistency across different server timezones.
    """
    # Define the Indian Standard Timezone
    ist = pytz.timezone('Asia/Kolkata')
    
    # Get the current time in UTC and then convert it to IST
    ist_now = datetime.now(ist)
    
    # Return only the date part
    return ist_now.date()
