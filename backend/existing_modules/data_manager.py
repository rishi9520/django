import os
from utils import get_ist_today
import platform
import pandas as pd
import time
import mysql.connector
from mysql.connector import Error
from datetime import datetime, date
import certifi
import streamlit as st
import whatsapp_service
import traceback

from arrangement_logic import ArrangementLogic

if platform.system() == "Windows" or os.getenv("ENV", "DEV") == "DEV":
    from dotenv import load_dotenv
    load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT", 4000))
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

# ✅ RAILWAY-OPTIMIZED Connection Function
def create_db_connection():
    """Railway-optimized database connection with fast retry logic"""
    if not all([DB_HOST, DB_USER, DB_PASSWORD, DB_NAME]):
        print("ERROR: Database environment variables are not fully set.")
        return None

    max_retries = 2
    for attempt in range(max_retries):
        try:
            print(f"--- Attempting Railway DB connection ({attempt + 1}/{max_retries}) ---")
            connection = mysql.connector.connect(
                host=DB_HOST,
                port=DB_PORT,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME,
                connect_timeout=8,
                autocommit=True,
                use_unicode=True,
                charset='utf8mb4',
                auth_plugin='mysql_native_password'
            )
            if connection.is_connected():
                print("--- Railway DB Connection Successful! ---")
                return connection
            
        except Error as e:
            print(f"ERROR on attempt {attempt + 1}: Could not connect to database: {e}")
            if attempt == max_retries - 1:
                print(f"Database Connection Failed after {max_retries} attempts")
                return None
            
            print("--- Waiting 2 seconds before retrying... ---")
            time.sleep(2)
            
    return None

def execute_query(connection, query, params=None):
    """Railway-optimized execute query with enhanced error handling"""
    if connection is None or not connection.is_connected():
        print("ERROR execute_query: Received invalid or closed connection.")
        return False

    try:
        with connection.cursor() as cursor:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            connection.commit() if not connection.autocommit else None
            return True

    except mysql.connector.Error as e:
        print(f"ERROR execute_query: MySQL Error: {e}")
        print(f"Query: {query[:100]}...")
        try:
            connection.rollback()
        except Error as rb_err:
            print(f"ERROR execute_query: Error during rollback: {rb_err}")
        return False

    except Exception as e:
        print(f"ERROR execute_query: Unexpected error: {e}")
        traceback.print_exc()
        try:
            connection.rollback()
        except Error:
            pass
        return False

def read_query(connection, query, params=None):
    """Railway-optimized read query with enhanced performance"""
    if connection is None or not connection.is_connected():
        print("ERROR read_query: Received invalid or closed connection.")
        return []

    try:
        with connection.cursor(dictionary=True) as cursor:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchall()

    except mysql.connector.Error as e:
        print(f"ERROR read_query: MySQL Error: {e}")
        print(f"Query: {query[:100]}...")
        return []

    except Exception as e:
        print(f"ERROR read_query: Unexpected error: {e}")
        traceback.print_exc()
        return []

# ✅ RAILWAY-OPTIMIZED DataManager Class
class DataManager:
    def __init__(self):
        print("--- DataManager initialized (Railway Optimized) ---")
        self.arrangement_logic = ArrangementLogic(self)

 
        
    def get_suspended_dates(self, school_id):
        """Fetches suspended arrangement dates for a specific school from the database."""
        print(f"DEBUG DataManager: Getting suspended dates for school={school_id}")
        connection = None
        suspended_dates_df = pd.DataFrame()

        try:
            connection = create_db_connection()
            if connection is None or not connection.is_connected():
                print(
                    f"ERROR DataManager.get_suspended_dates: DB connection failed for school {school_id}. Cannot fetch suspended dates."
                )
                return suspended_dates_df

            print(f"DEBUG DataManager.get_suspended_dates: DB connection obtained.")

            query = "SELECT date FROM suspended_dates WHERE school_id = %s;"
            params = (school_id,)

            result = read_query(connection, query, params)

            if result:
                suspended_dates_df = pd.DataFrame(result)
                print(
                    f"DEBUG DataManager.get_suspended_dates: Fetched {len(suspended_dates_df)} suspended dates."
                )
                if "date" in suspended_dates_df.columns:
                    try:
                        suspended_dates_df["date"] = pd.to_datetime(
                            suspended_dates_df["date"]
                        ).dt.date
                        print(
                            "DEBUG DataManager.get_suspended_dates: Converted 'suspended_date' column to date objects."
                        )
                    except Exception as e:
                        print(
                            f"WARNING DataManager.get_suspended_dates: Could not convert 'date' column to date objects: {e}"
                        )
                else:
                    print(
                        "WARNING DataManager.get_suspended_dates: 'date' column not found in result."
                    )

            else:
                print(
                    f"INFO DataManager.get_suspended_dates: No suspended dates found for school {school_id}."
                )

            return suspended_dates_df

        except Exception as e:
            print(
                f"ERROR DataManager.get_suspended_dates: Unexpected error getting suspended dates from DB for school {school_id}: {e}"
            )
            import traceback

            traceback.print_exc()
            return suspended_dates_df

        finally:
            if connection and connection.is_connected():
                try:
                    connection.close()
                    print(f"DEBUG DataManager.get_suspended_dates: Connection closed.")
                except Error as e:
                    print(
                        f"ERROR DataManager.get_suspended_dates: Failed to close connection: {e}"
                    )

    def _save_arrangements(self, new_arrangements_list):
        """
        ✅ FIXED: Saves arrangements using executemany for better performance.
        """
        print(f"DEBUG DataManager: Attempting to save {len(new_arrangements_list)} arrangements")
        
        if not new_arrangements_list:
            print("INFO DataManager: No new arrangements to save")
            return True

        connection = None
        try:
            connection = create_db_connection()
            if connection is None or not connection.is_connected():
                print(f"ERROR DataManager._save_arrangements: DB connection failed")
                return False

            # This query will attempt to insert a new arrangement. 
            # If an arrangement for the same school, date, and period already exists, it will be updated.
            # This requires a UNIQUE constraint on (school_id, date, period).
            # ALTER TABLE arrangements ADD UNIQUE KEY `unique_arrangement` (`school_id`, `date`, `period`);
            query = """
                INSERT INTO arrangements (school_id, date, absent_teacher, absent_name, absent_category, replacement_teacher, replacement_name, replacement_category, class, period, status, match_quality) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE 
                    absent_teacher=VALUES(absent_teacher), absent_name=VALUES(absent_name), absent_category=VALUES(absent_category),
                    replacement_teacher=VALUES(replacement_teacher), replacement_name=VALUES(replacement_name), replacement_category=VALUES(replacement_category),
                    class=VALUES(class), status=VALUES(status), match_quality=VALUES(match_quality);
            """
            
            params_to_insert = [
                (
                    arr.get("school_id"), arr.get("date"), arr.get("absent_teacher"),
                    arr.get("absent_name"), arr.get("absent_category"), arr.get("replacement_teacher"),
                    arr.get("replacement_name"), arr.get("replacement_category"), arr.get("class"),
                    arr.get("period"), arr.get("status"), arr.get("match_quality")
                )
                for arr in new_arrangements_list
            ]
            
            with connection.cursor() as cursor:
                cursor.executemany(query, params_to_insert)
                connection.commit()
                # executemany in MySQL Connector/Python with ON DUPLICATE KEY UPDATE returns 1 for an insert, 2 for an update.
                # So cursor.rowcount can be more than the number of rows. We'll just check if it's non-negative.
                success_count = cursor.rowcount
                print(f"SUCCESS: Bulk saved/updated arrangements. Rowcount: {success_count}")
                return True
        
        except Exception as e:
            print(f"ERROR DataManager._save_arrangements: {e}")
            traceback.print_exc()
            if connection:
                connection.rollback()
            return False
        finally:
            if connection and connection.is_connected():
                connection.close()
    
    # ... [Keep all your other DataManager methods as they are] ...
    # get_user_details, mark_attendance, suspend_arrangements, etc.
    # The rest of your file is okay.

    # [ PASTE THE REST OF YOUR data_manager.py FILE HERE ]
    # Make sure to copy all other methods like get_todays_attendance, get_auto_marking_timing, get_user_details etc.
    # The code below is a placeholder for you to paste the rest of your file.

    def get_todays_attendance(self, school_id):
        """Get today's attendance (Railway optimized)"""
        print(f"DEBUG DataManager: Getting today's attendance for school {school_id}")
        today = get_ist_today()
        return self.get_attendance_report(school_id, start_date=today, end_date=today)

    def get_auto_marking_timing(self, school_id):
        """Get auto-marking timing (Railway optimized)"""
        print(f"DEBUG DataManager: Fetching auto-marking timing for school {school_id}")
        connection = None
        timing_data = {}
        try:
            connection = create_db_connection()
            if connection is None or not connection.is_connected():
                print(f"ERROR DataManager.get_auto_marking_timing: DB connection failed for school {school_id}")
                return timing_data

            print(f"DEBUG DataManager.get_auto_marking_timing: DB connection obtained for school {school_id}")
            query = "SELECT hour, minute, enabled FROM timing WHERE school_id = %s LIMIT 1"
            params = (school_id,)
            result = read_query(connection, query, params)

            if result:
                timing_data = result[0]
                print(f"DEBUG DataManager.get_auto_marking_timing: Found timing data: {timing_data}")
            else:
                print(f"INFO DataManager.get_auto_marking_timing: No timing data found for school {school_id}")
            return timing_data
        except Exception as e:
            print(f"ERROR DataManager.get_auto_marking_timing: Exception for school {school_id}: {e}")
            traceback.print_exc()
            return timing_data
        finally:
            if connection and connection.is_connected():
                try:
                    connection.close()
                except Exception as e_close:
                    print(f"ERROR DataManager.get_auto_marking_timing: Failed to close connection: {e_close}")

    def get_arrangement_time(self, school_id):
        """Get arrangement creation time for a specific school from the database."""
        print(
            f"DEBUG DataManager: Fetching timing for school {school_id} using get_arrangement_time"
        )
        connection = None
        timing_data = {
            "hour": 10,
            "minute": 0,
            "enabled": True,
        }
        try:
            connection = create_db_connection()
            if connection is None or not connection.is_connected():
                print(
                    f"ERROR DataManager.get_arrangement_time: Failed to get DB connection for school {school_id}. Returning defaults."
                )
                return timing_data

            query = "SELECT hour, minute, enabled FROM timing WHERE school_id = %s"
            params = (school_id,)
            result = read_query(connection, query, params)

            if result:
                timing_data = result[0]
                if "enabled" in timing_data:
                    timing_data["enabled"] = bool(timing_data["enabled"])
            else:
                print(
                    f"INFO DataManager.get_arrangement_time: No timing found for school {school_id}. Returning defaults."
                )
            return timing_data
        except Exception as e:
            print(
                f"ERROR DataManager.get_arrangement_time: Error fetching timing for school {school_id}: {e}"
            )
            return timing_data
        finally:
            if connection and connection.is_connected():
                try:
                    connection.close()
                except Error as e:
                    print(
                        f"ERROR DataManager.get_arrangement_time: Failed to close connection: {e}"
                    )

    def set_arrangement_time(self, school_id, hour, minute):
        """Set arrangement creation time for a specific school in the database."""
        print(
            f"DEBUG DataManager: Attempting to set timing for school {school_id} to {hour}:{minute:02d}"
        )
        connection = None
        success = False
        try:
            connection = create_db_connection()
            if connection is None or not connection.is_connected():
                print(
                    f"ERROR DataManager.set_arrangement_time: Failed to get DB connection for school {school_id}. Cannot save timing."
                )
                return success

            hour_int = int(hour)
            minute_int = int(minute)
            query = """
                INSERT INTO timing (school_id, hour, minute, enabled)
                VALUES (%s, %s, %s, TRUE)
                ON DUPLICATE KEY UPDATE
                    hour = VALUES(hour),
                    minute = VALUES(minute),
                    enabled = VALUES(enabled);
            """
            params = (school_id, hour_int, minute_int)
            success = execute_query(connection, query, params)
            if success:
                print(
                    f"INFO DataManager.set_arrangement_time: Timing successfully set/updated for school {school_id}."
                )
        except ValueError:
            print(
                "ERROR DataManager.set_arrangement_time: Hour and minute must be integers."
            )
            success = False
        except Exception as e:
            print(
                f"ERROR DataManager.set_arrangement_time: Unexpected error setting timing for school {school_id}: {e}"
            )
            traceback.print_exc()
            success = False
        finally:
            if connection and connection.is_connected():
                try:
                    connection.close()
                except Error as e:
                    print(
                        f"ERROR DataManager.set_arrangement_time: Failed to close connection: {e}"
                    )
        return success

    def set_auto_marking_timing(self, school_id, hour, minute, enabled):
        """Set auto-marking timing (Railway optimized)"""
        print(f"DEBUG DataManager: Setting auto-marking timing for school {school_id}")
        connection = None
        try:
            connection = create_db_connection()
            if connection is None or not connection.is_connected():
                print(f"ERROR DataManager.set_auto_marking_timing: DB connection failed for school {school_id}")
                return False

            query = "REPLACE INTO timing (school_id, hour, minute, enabled) VALUES (%s, %s, %s, %s)"
            params = (school_id, hour, minute, enabled)
            success = execute_query(connection, query, params)
            
            if success:
                print(f"SUCCESS DataManager.set_auto_marking_timing: Updated timing for school {school_id}")
            return success
        except Exception as e:
            print(f"ERROR DataManager.set_auto_marking_timing: Exception for school {school_id}: {e}")
            traceback.print_exc()
            return False
        finally:
            if connection and connection.is_connected():
                try:
                    connection.close()
                except Exception as e_close:
                    print(f"ERROR DataManager.set_auto_marking_timing: Failed to close connection: {e_close}")

    def is_arrangement_suspended(self, school_id, date_obj):
        """Check if arrangements are suspended (Railway optimized)"""
        print(f"DEBUG DataManager: Checking arrangement suspension for school={school_id}, date={date_obj}")
        connection = None
        is_suspended_flag = False
        try:
            connection = create_db_connection()
            if connection is None or not connection.is_connected():
                print(f"ERROR DataManager.is_arrangement_suspended: DB connection failed for school {school_id}")
                return False

            date_str = str(date_obj)
            query = "SELECT COUNT(*) as suspension_count FROM suspended_dates WHERE school_id = %s AND date = %s"
            params = (school_id, date_str)
            result = read_query(connection, query, params)

            if result and isinstance(result, list) and len(result) > 0:
                count = result[0].get("suspension_count", 0)
                if count is not None and count > 0:
                    is_suspended_flag = True
                    print(f"INFO DataManager.is_arrangement_suspended: Arrangements ARE suspended for {date_str}")
                else:
                    print(f"INFO DataManager.is_arrangement_suspended: Arrangements are NOT suspended for {date_str}")
            else:
                print(f"INFO DataManager.is_arrangement_suspended: No suspension record found for {date_str}")
                is_suspended_flag = False

            return is_suspended_flag
        except Exception as e:
            print(f"ERROR DataManager.is_arrangement_suspended: Unexpected error for school {school_id}: {e}")
            traceback.print_exc()
            return False
        finally:
            if connection and connection.is_connected():
                try:
                    connection.close()
                except Exception as e_close:
                    print(f"ERROR DataManager.is_arrangement_suspended: Failed to close connection: {e_close}")

    def get_absent_teachers(self, school_id, date_str):
        """Get absent teachers (Railway optimized with DISTINCT)"""
        print(f"DEBUG DataManager: Getting absent teachers for school={school_id}, date={date_str}")
        connection = None
        try:
            connection = create_db_connection()
            if connection is None or not connection.is_connected():
                print(f"ERROR DataManager.get_absent_teachers: DB connection failed for school {school_id}")
                return []

            query = "SELECT DISTINCT teacher_id FROM attendance WHERE school_id = %s AND date = %s AND status = 'absent'"
            params = (school_id, date_str)
            result = read_query(connection, query, params)
            
            absent_list = [row["teacher_id"] for row in result] if result else []
            print(f"DEBUG DataManager.get_absent_teachers: Found {len(absent_list)} absent teachers")
            return absent_list
        except Exception as e:
            print(f"ERROR DataManager.get_absent_teachers: Exception for school {school_id}: {e}")
            traceback.print_exc()
            return []
        finally:
            if connection and connection.is_connected():
                try:
                    connection.close()
                except Exception as e_close:
                    print(f"ERROR DataManager.get_absent_teachers: Failed to close connection: {e_close}")

    def get_present_teachers(self, school_id, date_str):
        """Get present teachers (Railway optimized)"""
        print(f"DEBUG DataManager: Getting present teachers for school={school_id}, date={date_str}")
        connection = None
        try:
            connection = create_db_connection()
            if connection is None or not connection.is_connected():
                print(f"ERROR DataManager.get_present_teachers: DB connection failed for school {school_id}")
                return []

            query = "SELECT DISTINCT teacher_id FROM attendance WHERE school_id = %s AND date = %s AND status = 'present'"
            params = (school_id, date_str)
            result = read_query(connection, query, params)
            
            present_list = [row["teacher_id"] for row in result] if result else []
            print(f"DEBUG DataManager.get_present_teachers: Found {len(present_list)} present teachers")
            return present_list
        except Exception as e:
            print(f"ERROR DataManager.get_present_teachers: Exception for school {school_id}: {e}")
            traceback.print_exc()
            return []
        finally:
            if connection and connection.is_connected():
                try:
                    connection.close()
                except Exception as e_close:
                    print(f"ERROR DataManager.get_present_teachers: Failed to close connection: {e_close}")

    def get_all_marked_teacher_ids_for_date(self, school_id, date_str):
        """Get all marked teacher IDs (Railway optimized)"""
        print(f"DEBUG DataManager: Getting all marked teachers for school={school_id}, date={date_str}")
        connection = None
        try:
            connection = create_db_connection()
            if connection is None or not connection.is_connected():
                print(f"ERROR DataManager.get_all_marked_teacher_ids_for_date: DB connection failed")
                return []

            query = "SELECT DISTINCT teacher_id FROM attendance WHERE school_id = %s AND date = %s"
            params = (school_id, date_str)
            result = read_query(connection, query, params)
            
            marked_list = [row["teacher_id"] for row in result] if result else []
            print(f"DEBUG DataManager.get_all_marked_teacher_ids_for_date: Found {len(marked_list)} marked teachers")
            return marked_list
        except Exception as e:
            print(f"ERROR DataManager.get_all_marked_teacher_ids_for_date: Exception: {e}")
            traceback.print_exc()
            return []
        finally:
            if connection and connection.is_connected():
                try:
                    connection.close()
                except Exception as e_close:
                    print(f"ERROR DataManager.get_all_marked_teacher_ids_for_date: Failed to close connection: {e_close}")

    def get_all_teachers(self, school_id):
        """Get all teachers (Railway optimized)"""
        print(f"DEBUG DataManager: Getting all teachers for school={school_id}")
        connection = None
        try:
            connection = create_db_connection()
            if connection is None or not connection.is_connected():
                print(f"ERROR DataManager.get_all_teachers: DB connection failed for school {school_id}")
                return []

            query = "SELECT teacher_id, name, category, phone, biometric_code FROM users WHERE school_id = %s"
            params = (school_id,)
            result = read_query(connection, query, params)
            
            teachers_list = result if result else []
            print(f"DEBUG DataManager.get_all_teachers: Found {len(teachers_list)} teachers")
            return teachers_list
        except Exception as e:
            print(f"ERROR DataManager.get_all_teachers: Exception for school {school_id}: {e}")
            traceback.print_exc()
            return []
        finally:
            if connection and connection.is_connected():
                try:
                    connection.close()
                except Exception as e_close:
                    print(f"ERROR DataManager.get_all_teachers: Failed to close connection: {e_close}")

    def load_teacher_schedules(self, school_id, specific_day=None):
        """
        Loads and pivots the daily schedule for a specific day into a wide format.
        This is the primary source for teacher schedules and their subjects for the day.
        """
        if not specific_day:
            specific_day = datetime.now().strftime('%A')
        
        print(f"DEBUG DataManager: Loading schedule for school {school_id} on {specific_day}")
        
        connection = None
        try:
            connection = create_db_connection()
            if not connection:
                return pd.DataFrame()

            # This query fetches the schedule in a "long" format.
            query = """
                SELECT teacher_id, name,classes, category, subject, period_number, class_info
                FROM daily_schedules
                WHERE school_id = %s AND day_of_week = %s
                ORDER BY teacher_id, period_number;
            """
            params = (school_id, specific_day)
            long_format_result = read_query(connection, query, params)

            if not long_format_result:
                print(f"INFO: No daily schedule found for {specific_day}.")
                return pd.DataFrame()

            # Convert the long format to a wide format DataFrame
            schedule_df_long = pd.DataFrame(long_format_result)
            
            # Pivot the table to get periods as columns
            schedule_df_wide = schedule_df_long.pivot_table(
                index=['teacher_id', 'name', 'category', 'subject'],
                columns='period_number',
                values='class_info',
                aggfunc='first'
            ).reset_index()

            # Rename the pivoted columns from numbers (1, 2, 3) to "period1", "period2", etc.
            schedule_df_wide.columns = ['teacher_id', 'name', 'category', 'subject'] + [f'period{col}' for col in schedule_df_wide.columns[4:]]

            # Fill any empty period slots with 'FREE'
            for i in range(1, 8):
                period_col = f'period{i}'
                if period_col not in schedule_df_wide.columns:
                    schedule_df_wide[period_col] = 'FREE'
            
            schedule_df_wide.fillna('FREE', inplace=True)
            
            print(f"SUCCESS: Loaded and pivoted schedule for {len(schedule_df_wide)} teachers.")
            return schedule_df_wide

        except Exception as e:
            print(f"CRITICAL ERROR in load_teacher_schedules: {e}")
            traceback.print_exc()
            return pd.DataFrame()
        finally:
            if connection and connection.is_connected():
                connection.close()
                
    def get_todays_arrangements(self, school_id, current_date=None):
        """Get today's arrangements (Railway optimized)"""
        if not current_date:
            current_date = get_ist_today()
        
        print(f"DEBUG DataManager: Getting arrangements for school={school_id}, date={current_date}")
        connection = None
        try:
            connection = create_db_connection()
            if connection is None or not connection.is_connected():
                print(f"ERROR DataManager.get_todays_arrangements: DB connection failed for school {school_id}")
                return pd.DataFrame()

            query = "SELECT * FROM arrangements WHERE school_id = %s AND date = %s"
            params = (school_id, str(current_date))
            result = read_query(connection, query, params)
            
            if result:
                arrangements_df = pd.DataFrame(result)
                print(f"DEBUG DataManager.get_todays_arrangements: Found {len(arrangements_df)} arrangements")
                return arrangements_df
            
            print(f"DEBUG DataManager.get_todays_arrangements: No arrangements found for {current_date}")
            return pd.DataFrame()
        except Exception as e:
            print(f"ERROR DataManager.get_todays_arrangements: Exception for school {school_id}: {e}")
            traceback.print_exc()
            return pd.DataFrame()
        finally:
            if connection and connection.is_connected():
                try:
                    connection.close()
                except Exception as e_close:
                    print(f"ERROR DataManager.get_todays_arrangements: Failed to close connection: {e_close}")

    def get_multiple_teachers_workload(self, school_id, teacher_ids):
        """Get multiple teachers' workload (Railway optimized)"""
        if not teacher_ids:
            return []
        
        print(f"DEBUG DataManager: Getting workload for {len(teacher_ids)} teachers in school {school_id}")
        connection = None
        try:
            connection = create_db_connection()
            if connection is None or not connection.is_connected():
                print(f"ERROR DataManager.get_multiple_teachers_workload: DB connection failed for school {school_id}")
                return []

            placeholders = ",".join(["%s"] * len(teacher_ids))
            query = f"SELECT teacher_id, workload_count FROM workload_counter WHERE school_id = %s AND teacher_id IN ({placeholders})"
            params = [school_id] + teacher_ids
            result = read_query(connection, query, params)
            
            workload_list = result if result else []
            print(f"DEBUG DataManager.get_multiple_teachers_workload: Found workload for {len(workload_list)} teachers")
            return workload_list
        except Exception as e:
            print(f"ERROR DataManager.get_multiple_teachers_workload: Exception for school {school_id}: {e}")
            traceback.print_exc()
            return []
        finally:
            if connection and connection.is_connected():
                try:
                    connection.close()
                except Exception as e_close:
                    print(f"ERROR DataManager.get_multiple_teachers_workload: Failed to close connection: {e_close}")

    def update_teacher_workload(self, school_id, teacher_id, increment=1):
        """Update teacher workload (Railway optimized)"""
        print(f"DEBUG DataManager: Updating workload for teacher {teacher_id} in school {school_id}")
        connection = None
        try:
            connection = create_db_connection()
            if connection is None or not connection.is_connected():
                print(f"ERROR DataManager.update_teacher_workload: DB connection failed for school {school_id}")
                return False

            query = """INSERT INTO workload_counter (school_id, teacher_id, workload_count) 
                       VALUES (%s, %s, %s) 
                       ON DUPLICATE KEY UPDATE workload_count = workload_count + %s"""
            params = (school_id, teacher_id, increment, increment)
            success = execute_query(connection, query, params)
            
            if success:
                print(f"SUCCESS DataManager.update_teacher_workload: Updated workload for teacher {teacher_id}")
            return success
        except Exception as e:
            print(f"ERROR DataManager.update_teacher_workload: Exception for teacher {teacher_id}: {e}")
            traceback.print_exc()
            return False
        finally:
            if connection and connection.is_connected():
                try:
                    connection.close()
                except Exception as e_close:
                    print(f"ERROR DataManager.update_teacher_workload: Failed to close connection: {e_close}")

    def get_user_details_by_teacher_id(self, school_id, teacher_id):
        """Get user details by teacher ID (Railway optimized)"""
        print(f"DEBUG DataManager: Getting user details for teacher={teacher_id}, school={school_id}")
        connection = None
        try:
            connection = create_db_connection()
            if connection is None or not connection.is_connected():
                print(f"ERROR DataManager.get_user_details_by_teacher_id: DB connection failed for school {school_id}")
                return None

            query = "SELECT id, name, phone, teacher_id, category FROM users WHERE school_id = %s AND teacher_id = %s LIMIT 1"
            params = (school_id, teacher_id)
            result = read_query(connection, query, params)

            if result:
                user_data = result[0]
                print(f"DEBUG DataManager.get_user_details_by_teacher_id: Found user: {user_data.get('name')}")
                return user_data
            else:
                print(f"INFO DataManager.get_user_details_by_teacher_id: No user found for teacher_id '{teacher_id}'")
                return None
        except Exception as e:
            print(f"ERROR DataManager.get_user_details_by_teacher_id: Exception for teacher {teacher_id}: {e}")
            traceback.print_exc()
            return None
        finally:
            if connection and connection.is_connected():
                try:
                    connection.close()
                except Exception as e_close:
                    print(f"ERROR DataManager.get_user_details_by_teacher_id: Failed to close connection: {e_close}")

    def get_user_details(self, school_id, username):
        """Get admin user details by username for a specific school from the database (Railway optimized)"""
        print(f"DEBUG DataManager: Getting admin user details for username={username}, school={school_id}")
        connection = None
        try:
            connection = create_db_connection()
            if connection is None or not connection.is_connected():
                print(f"ERROR DataManager.get_user_details: DB connection failed for school {school_id}")
                return None

            print(f"DEBUG DataManager.get_user_details: DB connection obtained")

            query = "SELECT id, username, name, phone, email, password FROM admins WHERE school_id = %s AND username = %s"
            params = (school_id, username)
            result = read_query(connection, query, params)

            print(f"DEBUG DataManager.get_user_details: read_query returned: {result}")

            if result:
                user_data = result[0]
                print(f"DEBUG DataManager.get_user_details: Found user: {user_data.get('name')}")
                return user_data
            else:
                print(f"INFO DataManager.get_user_details: No admin user found for username '{username}' in school '{school_id}'")
                return None
        except Exception as e:
            print(f"ERROR DataManager.get_user_details: Exception for username {username} in school {school_id}: {e}")
            import traceback
            traceback.print_exc()
            return None
        finally:
            if connection and connection.is_connected():
                try:
                    connection.close()
                    print(f"DEBUG DataManager.get_user_details: Connection closed")
                except Exception as e_close:
                    print(f"ERROR DataManager.get_user_details: Failed to close connection: {e_close}")

    def get_attendance(self, school_id, teacher_id, date_str):
        """Get attendance record (Railway optimized)"""
        print(f"DEBUG DataManager: Getting attendance for teacher={teacher_id}, date={date_str}, school={school_id}")
        connection = None
        try:
            connection = create_db_connection()
            if connection is None or not connection.is_connected():
                print(f"ERROR DataManager.get_attendance: DB connection failed for school {school_id}")
                return None

            query = "SELECT * FROM attendance WHERE school_id = %s AND teacher_id = %s AND date = %s LIMIT 1"
            params = (school_id, teacher_id, date_str)
            result = read_query(connection, query, params)

            if result:
                attendance_record = result[0]
                print(f"DEBUG DataManager.get_attendance: Found attendance record for {teacher_id}")
                return attendance_record
            else:
                print(f"INFO DataManager.get_attendance: No attendance found for teacher {teacher_id} on {date_str}")
                return None
        except Exception as e:
            print(f"ERROR DataManager.get_attendance: Exception for teacher {teacher_id}: {e}")
            traceback.print_exc()
            return None
        finally:
            if connection and connection.is_connected():
                try:
                    connection.close()
                except Exception as e_close:
                    print(f"ERROR DataManager.get_attendance: Failed to close connection: {e_close}")

    def has_attendance(self, school_id, teacher_id, date_str):
        """Check if attendance exists (Railway optimized)"""
        print(f"DEBUG DataManager: Checking attendance for teacher={teacher_id}, date={date_str}, school={school_id}")
        connection = None
        try:
            connection = create_db_connection()
            if connection is None or not connection.is_connected():
                print(f"ERROR DataManager.has_attendance: DB connection failed for school {school_id}")
                return False

            query = "SELECT COUNT(*) as count FROM attendance WHERE school_id = %s AND teacher_id = %s AND date = %s"
            params = (school_id, teacher_id, date_str)
            result = read_query(connection, query, params)

            if result:
                count = result[0]['count']
                has_record = count > 0
                print(f"DEBUG DataManager.has_attendance: Teacher {teacher_id} has attendance: {has_record}")
                return has_record
            else:
                print(f"INFO DataManager.has_attendance: No attendance check result for teacher {teacher_id}")
                return False
        except Exception as e:
            print(f"ERROR DataManager.has_attendance: Exception for teacher {teacher_id}: {e}")
            traceback.print_exc()
            return False
        finally:
            if connection and connection.is_connected():
                try:
                    connection.close()
                except Exception as e_close:
                    print(f"ERROR DataManager.has_attendance: Failed to close connection: {e_close}")

    def get_attendance_report(self, school_id, start_date=None, end_date=None, teacher_id_filter=None):
        """Get attendance report (Railway optimized)"""
        print(f"DEBUG DataManager: Getting attendance report for school={school_id}")
        connection = None
        try:
            connection = create_db_connection()
            if connection is None or not connection.is_connected():
                print(f"ERROR DataManager.get_attendance_report: DB connection failed for school {school_id}")
                return []

            query = "SELECT * FROM attendance WHERE school_id = %s"
            params = [school_id]
            
            if start_date:
                query += " AND date >= %s"
                params.append(str(start_date))
            if end_date:
                query += " AND date <= %s"
                params.append(str(end_date))
            if teacher_id_filter:
                query += " AND teacher_id = %s"
                params.append(teacher_id_filter)
            
            query += " ORDER BY date DESC, timestamp DESC"
            result = read_query(connection, query, params)
            
            if result:
                report_df = pd.DataFrame(result)
                print(f"DEBUG DataManager.get_attendance_report: Found {len(report_df)} attendance records.")
                return report_df
            else:
                print(f"INFO DataManager.get_attendance_report: No attendance records found for the given criteria.")
                return pd.DataFrame() # Return an empty DataFrame
        except Exception as e:
            print(f"ERROR DataManager.get_attendance_report: An unexpected error occurred: {e}")
            traceback.print_exc()
            return pd.DataFrame() # Return an empty DataFrame on error
        finally:
            if connection and connection.is_connected():
                try:
                    connection.close()
                except Exception as e_close:
                    print(f"ERROR DataManager.get_attendance_report: Failed to close connection: {e_close}")
                    
    def mark_attendance(self, school_id, teacher_id, date_str, status, is_auto_mark=False):
        """Mark attendance (Railway optimized)"""
        print(f"DEBUG DataManager: Marking attendance for teacher={teacher_id}, status={status}, school={school_id}")
        connection = None
        try:
            connection = create_db_connection()
            if connection is None or not connection.is_connected():
                print(f"ERROR DataManager.mark_attendance: DB connection failed for school {school_id}")
                return False

            query = """INSERT INTO attendance (school_id, teacher_id, date, status, timestamp, is_auto) 
                       VALUES (%s, %s, %s, %s, %s, %s)
                       ON DUPLICATE KEY UPDATE status = VALUES(status), timestamp = VALUES(timestamp), is_auto = VALUES(is_auto)"""
            params = (school_id, teacher_id, date_str, status, datetime.now(), is_auto_mark)
            success = execute_query(connection, query, params)
            
            if success:
                print(f"SUCCESS DataManager.mark_attendance: Marked {teacher_id} as {status}")
            return success
        except Exception as e:
            print(f"ERROR DataManager.mark_attendance: Exception for teacher {teacher_id}: {e}")
            traceback.print_exc()
            return False
        finally:
            if connection and connection.is_connected():
                try:
                    connection.close()
                except Exception as e_close:
                    print(f"ERROR DataManager.mark_attendance: Failed to close connection: {e_close}")

    def suspend_arrangements(self, school_id, date_obj):
        """Suspend arrangements for a date (Railway optimized)"""
        print(f"DEBUG DataManager: Suspending arrangements for school={school_id}, date={date_obj}")
        connection = None
        try:
            connection = create_db_connection()
            if connection is None or not connection.is_connected():
                print(f"ERROR DataManager.suspend_arrangements: DB connection failed for school {school_id}")
                return False

            date_str = str(date_obj)
            query = "INSERT IGNORE INTO suspended_dates (school_id, date) VALUES (%s, %s)"
            params = (school_id, date_str)
            success = execute_query(connection, query, params)

            if success:
                print(f"INFO DataManager.suspend_arrangements: Successfully suspended arrangements for {date_str}")
            return success
        except Exception as e:
            print(f"ERROR DataManager.suspend_arrangements: Exception for school {school_id}: {e}")
            traceback.print_exc()
            return False
        finally:
            if connection and connection.is_connected():
                try:
                    connection.close()
                except Exception as e_close:
                    print(f"ERROR DataManager.suspend_arrangements: Failed to close connection: {e_close}")

    def resume_arrangements(self, school_id, date_obj):
        """Resume arrangements for a date (Railway optimized)"""
        print(f"DEBUG DataManager: Resuming arrangements for school={school_id}, date={date_obj}")
        connection = None
        try:
            connection = create_db_connection()
            if connection is None or not connection.is_connected():
                print(f"ERROR DataManager.resume_arrangements: DB connection failed for school {school_id}")
                return False

            date_str = str(date_obj)
            query = "DELETE FROM suspended_dates WHERE school_id = %s AND date = %s"
            params = (school_id, date_str)
            success = execute_query(connection, query, params)

            if success:
                print(f"INFO DataManager.resume_arrangements: Successfully resumed arrangements for {date_str}")
            return success
        except Exception as e:
            print(f"ERROR DataManager.resume_arrangements: Exception for school {school_id}: {e}")
            traceback.print_exc()
            return False
        finally:
            if connection and connection.is_connected():
                try:
                    connection.close()
                except Exception as e_close:
                    print(f"ERROR DataManager.resume_arrangements: Failed to close connection: {e_close}")

    def get_recent_attendance(self, school_id, limit=20):
        """Get recent attendance records for a specific school from the database."""
        print(
            f"DEBUG DataManager: Getting recent attendance for school={school_id}, limit={limit}"
        )
        connection = None  # Initialize connection
        attendance_df = pd.DataFrame()  # Initialize return as empty DataFrame

        try:
            connection = create_db_connection()
            if connection is None or not connection.is_connected():
                print(
                    f"ERROR DataManager.get_recent_attendance: DB connection failed for school {school_id}. Cannot fetch recent attendance."
                )
                return attendance_df  # Return empty DataFrame on connection failure

            print(f"DEBUG DataManager.get_recent_attendance: DB connection obtained.")

            query = """
                SELECT date, teacher_id, status, timestamp, is_auto
                FROM attendance WHERE school_id = %s
                ORDER BY timestamp DESC LIMIT %s;
            """  # Use date, order by timestamp
            params = (school_id, int(limit))  # Ensure limit is integer

            result = read_query(connection, query, params)

            if result:
                attendance_df = pd.DataFrame(result)
                print(
                    f"DEBUG DataManager.get_recent_attendance: Fetched {len(attendance_df)} recent attendance records."
                )

            else:
                print(
                    f"INFO DataManager.get_recent_attendance: No recent attendance records found for school {school_id}."
                )
                # attendance_df remains empty DataFrame

            return attendance_df  # Return DataFrame (empty or with data)

        except Exception as e:
            print(
                f"ERROR DataManager.get_recent_attendance: Unexpected error getting recent attendance for school {school_id}: {e}"
            )
            import traceback

            traceback.print_exc()
            return attendance_df  # Return empty DataFrame on error

        finally:
            if connection and connection.is_connected():
                try:
                    connection.close()
                    print(
                        f"DEBUG DataManager.get_recent_attendance: Connection closed."
                    )
                except Error as e:
                    print(
                        f"ERROR DataManager.get_recent_attendance: Failed to close connection: {e}"
                    )

    def create_manual_arrangement(
        self,
        school_id,
        absent_teacher,
        absent_name,
        absent_category,
        replacement_teacher,
        replacement_name,
        replacement_category,
        period,
        class_name,
        current_date=None,
        status="MANUAL",
        match_quality="Manual",
    ):
        """Create a manual arrangement for a specific period in the database."""
        print(
            f"DEBUG DataManager: Creating manual arrangement for school: {school_id}, absent={absent_teacher}, replacement={replacement_teacher}, period={period}"
        )
        save_success = False
        try:
            date_to_save = current_date if current_date is not None else get_ist_today()
            date_str = str(date_to_save)

            arrangement = {
                "school_id": school_id,
                "date": date_str,
                "absent_teacher": absent_teacher,
                "absent_name": absent_name,
                "absent_category": absent_category,
                "replacement_teacher": replacement_teacher,
                "replacement_name": replacement_name,
                "replacement_category": replacement_category,
                "class": class_name,
                "period": period,
                "status": status,
                "match_quality": match_quality,
            }

            save_success = self._save_arrangements([arrangement])

            if save_success:
                print(
                    f"INFO DataManager: Manual arrangement saved successfully for school {school_id}."
                )
                if replacement_teacher:
                    self.update_teacher_workload(school_id, replacement_teacher)
                
                # Trigger WhatsApp notification for manual arrangement
                if replacement_teacher and replacement_name:
                    school_details = self.get_school_details(school_id)
                    school_name = school_details.get("school_name", "Your School") if school_details else "Your School"
                    teacher_details = self.get_user_details_by_teacher_id(school_id, replacement_teacher)
                    if teacher_details and teacher_details.get("phone"):
                        manual_detail_text = f"Period {period}: {class_name}"
                        whatsapp_service.send_manual_arrangement_notification(
                            replacement_name,
                            teacher_details.get("phone"),
                            manual_detail_text,
                            school_name
                        )
            else:
                print(
                    f"ERROR DataManager: Failed to save manual arrangement for school {school_id}."
                )
            return save_success
        except Exception as e:
            print(
                f"CRITICAL ERROR DataManager: Unexpected error creating manual arrangement for school {school_id}: {e}"
            )
            traceback.print_exc()
            return False

    def get_teacher_workload(self, school_id, teacher_id):
        """Get teacher workload (Railway optimized)"""
        print(f"DEBUG DataManager: Getting workload for teacher={teacher_id}, school={school_id}")
        connection = None
        try:
            connection = create_db_connection()
            if connection is None or not connection.is_connected():
                print(f"ERROR DataManager.get_teacher_workload: DB connection failed for school {school_id}")
                return 0

            query = "SELECT workload_count FROM workload_counter WHERE school_id = %s AND teacher_id = %s LIMIT 1"
            params = (school_id, teacher_id)
            result = read_query(connection, query, params)
            
            if result:
                workload = result[0]['workload_count']
                print(f"DEBUG DataManager.get_teacher_workload: Teacher {teacher_id} has workload {workload}")
                return workload
            else:
                print(f"DEBUG DataManager.get_teacher_workload: No workload found for teacher {teacher_id}")
                return 0
        except Exception as e:
            print(f"ERROR DataManager.get_teacher_workload: Exception for teacher {teacher_id}: {e}")
            traceback.print_exc()
            return 0
        finally:
            if connection and connection.is_connected():
                try:
                    connection.close()
                except Exception as e_close:
                    print(f"ERROR DataManager.get_teacher_workload: Failed to close connection: {e_close}")

    def get_school_details(self, school_id):
        """Get school details (Railway optimized)"""
        print(f"DEBUG DataManager: Getting school details for school={school_id}")
        connection = None
        try:
            connection = create_db_connection()
            if connection is None or not connection.is_connected():
                print(f"ERROR DataManager.get_school_details: DB connection failed for school {school_id}")
                return None

            query = "SELECT * FROM schools WHERE school_id = %s LIMIT 1"
            params = (school_id,)
            result = read_query(connection, query, params)
            
            if result:
                school_details = result[0]
                print(f"DEBUG DataManager.get_school_details: Found school: {school_details.get('school_name')}")
                return school_details
            else:
                print(f"INFO DataManager.get_school_details: No school found for school_id '{school_id}'")
                return None
        except Exception as e:
            print(f"ERROR DataManager.get_school_details: Exception for school {school_id}: {e}")
            traceback.print_exc()
            return None
        finally:
            if connection and connection.is_connected():
                try:
                    connection.close()
                except Exception as e_close:
                    print(f"ERROR DataManager.get_school_details: Failed to close connection: {e_close}")

    def get_school_api_key(self, school_id):
        """Get school API key (Railway optimized)"""
        print(f"DEBUG DataManager: Fetching API key for school_id={school_id}")
        connection = None
        try:
            connection = create_db_connection()
            if connection is None or not connection.is_connected():
                print(f"ERROR DataManager.get_school_api_key: DB connection failed for school {school_id}")
                return None

            query = "SELECT api_key FROM schools WHERE school_id = %s LIMIT 1"
            params = (school_id,)
            result = read_query(connection, query, params)

            if result and result[0].get("api_key"):
                api_key = result[0]["api_key"]
                print(f"DEBUG DataManager.get_school_api_key: Found API key for school {school_id}")
                return api_key
            else:
                print(f"INFO DataManager.get_school_api_key: No API key found for school {school_id}")
                return None
        except Exception as e:
            print(f"ERROR DataManager.get_school_api_key: Exception for school {school_id}: {e}")
            traceback.print_exc()
            return None
        finally:
            if connection and connection.is_connected():
                try:
                    connection.close()
                except Exception as e_close:
                    print(f"ERROR DataManager.get_school_api_key: Failed to close connection: {e_close}")

    def bulk_mark_attendance(self, school_id, attendance_data_list):
        """Bulk mark attendance (Railway optimized)"""
        if not attendance_data_list:
            return 0

        print(f"DEBUG DataManager: Bulk marking attendance for {len(attendance_data_list)} teachers in school {school_id}")
        connection = None
        try:
            connection = create_db_connection()
            if connection is None or not connection.is_connected():
                print(f"ERROR DataManager.bulk_mark_attendance: DB connection failed for school {school_id}")
                return 0

            cursor = connection.cursor()
            db_timestamp = datetime.now()
            today_str = str(get_ist_today())

            update_query = """
                INSERT INTO attendance (school_id, teacher_id, date, status, timestamp, is_auto)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE status = VALUES(status), timestamp = VALUES(timestamp), is_auto = VALUES(is_auto)
            """

            records_to_process = []
            for teacher_id, status in attendance_data_list:
                records_to_process.append(
                    (school_id, teacher_id, today_str, status, db_timestamp, False)
                )

            cursor.executemany(update_query, records_to_process)
            connection.commit()

            processed_count = cursor.rowcount
            print(f"SUCCESS: Bulk marked attendance for {processed_count} records")
            return processed_count

        except Exception as e:
            print(f"ERROR DataManager.bulk_mark_attendance: Exception: {e}")
            traceback.print_exc()
            if connection:
                connection.rollback()
            return 0
        finally:
            if connection and connection.is_connected():
                try:
                    connection.close()
                except Exception as e_close:
                    print(f"ERROR DataManager.bulk_mark_attendance: Failed to close connection: {e_close}")

    def bulk_update_attendance(self, school_id, attendance_updates_list, is_auto=False):
        """
        ✅ FINAL VERSION: Ek saath kai teachers ki attendance ko INSERT ya UPDATE karta hai.
        Requires a UNIQUE KEY on (school_id, teacher_id, date) in the attendance table.
        """
        if not attendance_updates_list: 
            return 0
        
        connection = create_db_connection()
        if not connection: 
            return 0
            
        try:
            db_timestamp = datetime.now()
            today_str = get_ist_today().strftime('%Y-%m-%d')
            
            query = """
                INSERT INTO attendance (school_id, teacher_id, date, status, timestamp, is_auto)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE 
                    status = VALUES(status), 
                    timestamp = VALUES(timestamp), 
                    is_auto = VALUES(is_auto);
            """
            
            records_to_process = [
                (school_id, teacher_id, today_str, status, db_timestamp, is_auto) 
                for teacher_id, status in attendance_updates_list
            ]
            
            with connection.cursor() as cursor:
                cursor.executemany(query, records_to_process)
                connection.commit()
                
                # MySQL mein, ON DUPLICATE KEY UPDATE ke liye rowcount 1 (insert) ya 2 (update) return karta hai.
                # Hum actual process kiye gaye records ki sankhya return karenge.
                print(f"SUCCESS: Bulk update completed. DB Rowcount: {cursor.rowcount}")
                return len(records_to_process)
                
        except Error as e:
            print(f"CRITICAL ERROR in bulk_update_attendance: {e}")
            if connection: connection.rollback()
            return 0
        finally:
            if connection: connection.close()
    def process_bulk_arrangements(self, school_id, list_of_absent_teachers, arrangement_date):
        """
        ✅ FINAL GOLDEN FIX v4: Creates arrangements period-by-period, updating the busy list in real-time within the period loop.
        """
        if not list_of_absent_teachers:
            print("INFO: No absent teachers for bulk arrangement.")
            return True
        print(f"--- ✅ Starting FINAL Bulk Arrangement Processing v4 for {len(list_of_absent_teachers)} teachers ---")
        
        try:
            if self.is_arrangement_suspended(school_id, arrangement_date):
                print(f"INFO: Arrangements suspended for {arrangement_date}.")
                return True

            schedules_df = self.load_teacher_schedules(school_id, specific_day=arrangement_date.strftime('%A'))
            if schedules_df.empty:
                print(f"ERROR: No schedule for {arrangement_date.strftime('%A')}. Cannot process.")
                return False

            all_arrangements_to_save = []
            all_replacements_to_notify = {}
            
            self.delete_arrangements_for_date(school_id, arrangement_date)
            
            # --- ✅ PERIOD-BY-PERIOD LOOP (YAHAN HAI ASLI FIX) ---
            for period in range(1, 8):
                print(f"\n--- Processing Arrangements for Period {period} ---")
                
                # Har naye period ke liye, "is period mein busy" list ko khaali karo
                assigned_in_this_period = []

                for absent_teacher_id in list_of_absent_teachers:
                    
                    absent_row = schedules_df[schedules_df["teacher_id"].astype(str).str.upper() == str(absent_teacher_id).upper()]
                    if absent_row.empty: continue
                    absent_details = absent_row.iloc[0]
                    
                    class_info = absent_details.get(f"period{period}", 'FREE')
                    if not class_info or str(class_info).strip().upper() == "FREE":
                        continue
                        
                    # Replacement dhoondho. Is baar hum 'assigned_in_this_period' list bhej rahe hain.
                    repl_id, repl_cat, repl_name, absent_name, match_quality = self.arrangement_logic.find_replacement_teacher(
                        school_id=school_id, 
                        absent_teacher_id=absent_teacher_id, 
                        period=period,
                        schedules_df=schedules_df,
                        all_absent_today=list_of_absent_teachers,
                        assigned_in_this_period=assigned_in_this_period  # <<< YEH HAI ASLI BADLAAV
                    )
                    
                    # ✅ AGAR REPLACEMENT MILA, TO USE TURANT BUSY LIST MEIN DAALO
                    if repl_id:
                        assigned_in_this_period.append(repl_id)

                    arrangement_dict = {
                        "school_id": school_id, "date": str(arrangement_date),
                        "absent_teacher": absent_teacher_id, "absent_name": absent_name,
                        "absent_category": absent_details.get("category"),
                        "replacement_teacher": repl_id, "replacement_name": repl_name or "UNASSIGNED",
                        "replacement_category": repl_cat, "class": class_info, "period": period,
                        "status": "ASSIGNED" if repl_id else "UNASSIGNED",
                        "match_quality": match_quality,
                    }
                    all_arrangements_to_save.append(arrangement_dict)

                    if repl_id:
                        if repl_id not in all_replacements_to_notify:
                            all_replacements_to_notify[repl_id] = {"name": repl_name, "details": []}
                        arrangement_line = f"Period {period}: {class_info} (for {absent_name})"
                        all_replacements_to_notify[repl_id]["details"].append(arrangement_line)
            
            if all_arrangements_to_save:
                save_success = self._save_arrangements(all_arrangements_to_save)
                if save_success:
                    print(f"SUCCESS: Bulk saved {len(all_arrangements_to_save)} new arrangement rows.")
                    self.send_bulk_whatsapp_notifications(school_id, all_replacements_to_notify)
                    return True
            return False
        except Exception as e:
            print(f"CRITICAL ERROR in process_bulk_arrangements: {e}")
            traceback.print_exc()
            return False
    def delete_arrangements_for_date(self, school_id, date_to_delete):
        """Ek specific date ke saare arrangements delete karta hai."""
        connection = create_db_connection()
        if not connection: return False
        try:
            query = "DELETE FROM arrangements WHERE school_id = %s AND date = %s"
            return execute_query(connection, query, (school_id, str(date_to_delete)))
        finally:
            if connection: connection.close()

    def send_bulk_whatsapp_notifications(self, school_id, replacements_to_notify):
        """Ek saath saare replacement teachers ko WhatsApp bhejta hai."""
        if not replacements_to_notify: return
        school_details = self.get_school_details(school_id)
        school_name = school_details.get("school_name", "Your School") if school_details else "Your School"
        for repl_id, data in replacements_to_notify.items():
            teacher_details = self.get_user_details_by_teacher_id(school_id, repl_id)
            if teacher_details and teacher_details.get("phone"):
                whatsapp_service.send_arrangement_notification(data["name"], teacher_details.get("phone"), data["details"], school_name)
