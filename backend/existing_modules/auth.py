
import streamlit as st
from datetime import date
import bcrypt
from mysql.connector import Error
import data_manager

def validate_domain_access(school_id, current_domain):
    """
    Check karta hai ki given school_id wala admin us domain se login kar sakta hai ya nahi
    """
    if not current_domain or not school_id:
        return True  # Local development ke liye fallback
    
    # Database se school ka domain check karein
    connection = data_manager.create_db_connection()
    if connection:
        try:
            query = "SELECT domin FROM schools WHERE school_id = %s"
            result = data_manager.read_query(connection, query, (school_id,))
            connection.close()
            
            if result and result[0]['domin'] == current_domain:
                print(f"DEBUG: Domain access validated for {school_id} on {current_domain}")
                return True
            else:
                print(f"WARNING: Domain access denied for {school_id} on {current_domain}")
                return False
        except Exception as e:
            print(f"ERROR: Error validating domain access: {e}")
            return False
    return False

def check_password(username, entered_plain_password, school_id):
    dm_instance = st.session_state.get("data_manager")
    if dm_instance is None:
        st.error("System error: Database manager not initialized.")
        return None

    # Domain validation - Check if user is accessing from correct domain
    current_domain = st.session_state.get('current_domain')
    if current_domain and not validate_domain_access(school_id, current_domain):
        print(f"ERROR auth.py: Domain access denied for school {school_id} on domain {current_domain}")
        return {'error': 'Access denied: You can only login from your school\'s official domain.'}

    try:
        user_data_from_db = dm_instance.get_user_details(school_id, username)

        if user_data_from_db:
            hashed_password_str_from_db = user_data_from_db.get("password")

            if not hashed_password_str_from_db:
                return None

            entered_password_bytes = entered_plain_password.encode("utf-8")
            hashed_password_bytes_from_db = hashed_password_str_from_db.encode("utf-8")

            if bcrypt.checkpw(entered_password_bytes, hashed_password_bytes_from_db):
                # Password sahi hai! Ab subscription check karo.
                print(f"INFO auth.py: Password MATCHED for user '{username}'. Checking subscription...")
                
                # Naya Subscription Check Logic
                subscription_status = check_subscription_status(school_id)
                
                if subscription_status['is_valid']:
                    print(f"INFO auth.py: Subscription valid for school '{school_id}'. Login successful.")
                    return user_data_from_db  # Sab a_sahi hai, user data return karo
                else:
                    # Password sahi hai, lekin subscription mein dikkat hai
                    print(f"ERROR auth.py: Subscription invalid for school '{school_id}'. Reason: {subscription_status['message']}")
                    return {'error': subscription_status['message']} # Error message return karo
            else:
                return None  # Galat password
        else:
            return None  # User nahi mila
            
    except Exception as e_auth_main:
        print(f"CRITICAL ERROR auth.py: {e_auth_main}")
        import traceback
        traceback.print_exc()
        st.error("An unexpected error occurred during login.")
        return None

def check_subscription_status(school_id):
    """Check karta hai ki school ke paas valid subscription hai ya nahi."""
    # Demo school ko hamesha access do
    if school_id == 'S001':
        return {'is_valid': True, 'message': 'Access granted for demo school.'}
        
    dm_instance = st.session_state.get("data_manager")
    if not dm_instance:
        return {'is_valid': False, 'message': 'System error: Cannot verify subscription.'}
        
    connection = dm_instance.create_db_connection()
    if connection:
        try:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute(
                    "SELECT * FROM subscriptions WHERE school_id = %s AND status = 'active' ORDER BY end_date DESC LIMIT 1",
                    (school_id,)
                )
                subscription = cursor.fetchone()
            
            if subscription:
                if subscription.get('end_date') and subscription.get('end_date') >= date.today():
                    return {'is_valid': True, 'message': 'Subscription is active.'}
                else:
                    return {'is_valid': False, 'message': 'Your subscription has expired. Please renew.'}
            else:
                return {'is_valid': False, 'message': 'No active subscription found. Please purchase a plan.'}
        except Exception as e:
            print(f"ERROR checking subscription: {e}")
            return {'is_valid': False, 'message': 'Could not verify subscription due to a database error.'}
        finally:
            if connection.is_connected():
                connection.close()
    
    # Agar DB connection fail ho, to fallback. False return karna behtar hai.
    return {'is_valid': False, 'message': 'Could not connect to the server to verify subscription.'}