import csv
import mysql.connector
from mysql.connector import Error
import os
import argparse
from datetime import datetime
import traceback
import re

DB_HOST = os.getenv("MYSQLHOST")
DB_PORT_STR = os.getenv("MYSQLPORT")
DB_USER = os.getenv("MYSQLUSER")
DB_PASSWORD = os.getenv("MYSQLPASSWORD")
DB_NAME = os.getenv("MYSQLDATABASE")
DB_PORT = 4000
if DB_PORT_STR and DB_PORT_STR.isdigit():
    DB_PORT = int(DB_PORT_STR)
elif DB_PORT_STR:
    print(
        f"WARNING: MYSQLPORT environment variable ('{DB_PORT_STR}') is not a valid number. Connection might use default or fail if DB_PORT remains None and connector requires it."
    )


def create_db_connection():
    """
    MySQL database connection establish karta hai
    """
    connection = None
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
        )
        if connection.is_connected():
            print("MySQL Database connection successful")
        return connection
    except Error as e:
        print(f"Error connecting to MySQL Database: {e}")
        return None


# --- Helper to execute single insert query (WITHOUT COMMIT) ---
def _execute_single_insert_no_commit(connection, query, params):  # Naam badla
    """
    SQL INSERT query execute karta hai, lekin COMMIT nahi karta.
    Returns: True if successful, False otherwise.
    """
    # connection check pehle hi kar lena chahiye jahan se call ho raha hai
    # if not connection or not connection.is_connected():
    #     print("Error: No valid database connection for _execute_single_insert_no_commit.")
    #     return False

    cursor = None  # cursor ko bahar define karein taaki finally mein access ho sake
    try:
        cursor = connection.cursor()
        cursor.execute(query, params)
        # connection.commit() # <<<<<<<<<<< YEH LINE HATA DI GAYI HAI >>>>>>>>>>>>>
        return True
    except Error as e:
        if e.errno == mysql.connector.errorcode.ER_DUP_ENTRY:  # Duplicate entry
            print(
                f"Warning (not committed yet): Duplicate entry for query: {query[:70]}... with params {params[:2]}... Error: {e}"
            )
            # Agar ON DUPLICATE KEY UPDATE hai, toh yeh error nahi aana chahiye,
            # balki update hona chahiye. Agar simple INSERT hai aur key duplicate hai, tab yeh error aayega.
            # Is case mein, hum ise False return kar sakte hain taaki pata chale ki insert nahi hua.
            return False  # Ya True agar ON DUPLICATE KEY UPDATE ise handle kar lega
        else:
            print(
                f"Error staging insert query: {query[:70]}... with params {params[:2]}... Error: {e}"
            )
            # Rollback yahan nahi, main import function mein batch ke fail hone par hoga
        return False
    finally:
        if cursor:
            cursor.close()


# --- Helper to execute single insert query ---
def execute_insert(connection, query, params):
    """
    SQL INSERT query execute karta hai.
    Returns: True if successful, False otherwise.
    """
    cursor = connection.cursor()
    try:
        cursor.execute(query, params)
        connection.commit()
        # print(f"Inserted row: {params}") # Uncomment for debugging inserts
        return True
    except Error as e:
        # Handle specific errors if needed, e.g., duplicate entries
        if e.errno == mysql.connector.errorcode.ER_DUP_ENTRY:
            print(
                f"Warning: Duplicate entry ignored for query: {query} with params {params}. Error: {e}"
            )
        else:
            print(
                f"Error executing insert query: {query} with params {params}. Error: {e}"
            )
            connection.rollback()  # Rollback the transaction on error
        return False
    finally:
        cursor.close()


# --- Data Import Functions per table ---


def import_schools(connection, file_path):
    print(f"Importing {file_path} into schools...")
    insert_query = """
    INSERT INTO schools (school_id, school_name, address, email, api_key, logourl)
    VALUES (%s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        school_name = VALUES(school_name),
        address = VALUES(address),
        email = VALUES(email),
        api_key = VALUES(api_key),
        logourl = VALUES(logourl);
    """
    try:
        with open(file_path, mode="r", encoding="utf-8") as file:
            reader = csv.reader(file)
            header = next(reader)  # Skip header row
            for row in reader:
                # Ensure row has enough columns
                if len(row) < 6:
                    print(f"Skipping malformed row in {file_path}: {row}")
                    continue

                # Handle empty strings for potentially nullable columns
                params = (
                    row[0] if row[0] else None,  # school_id
                    row[1] if row[1] else None,  # school_name
                    row[2] if row[2] else None,  # address
                    row[3] if row[3] else None,  # email
                    row[4] if row[4] else None,  # api_key (handle empty as NULL)
                    row[5] if row[5] else None,  # logourl (handle empty as NULL)
                )
                execute_insert(connection, insert_query, params)
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
    except Exception as e:
        print(f"Error importing {file_path}: {e}")


def import_admins(connection, school_id_arg, file_path, batch_size=100):
    print(
        f"Importing {file_path} into admins for school {school_id_arg} (Batch Size: {batch_size})..."
    )

    # Query se `role` hata diya gaya hai.
    # `name` ko backticks (`) mein daala gaya hai.
    # `admins` table mein ek naya column 'email' add karna pad sakta hai.
    insert_query = """
    INSERT INTO admins (school_id, username, password, `name`, phone, email)
    VALUES (%s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        password = VALUES(password), 
        `name` = VALUES(`name`),
        phone = VALUES(phone),
        email = VALUES(email);
    """

    rows_batch = []
    total_rows_processed_from_csv = 0
    total_successful_db_operations = 0

    try:
        with open(file_path, mode="r", encoding="utf-8") as file:
            reader = csv.reader(file)
            try:
                header = next(reader)
            except StopIteration:
                print(f"Warning: CSV file {file_path} is empty. Skipping.")
                return

            for row_num, row in enumerate(reader):
                total_rows_processed_from_csv += 1

                # Ab hum 6 columns check karenge
                if len(row) < 6:
                    print(
                        f"Skipping malformed CSV row #{row_num+1} in {file_path}: {row}"
                    )
                    continue

                # CSV ke school_id (row[4]) ko `school_id_arg` par prathmikta denge
                current_school_id = row[4].strip() if row[4] else school_id_arg

                params = (
                    current_school_id,  # school_id (CSV se ya argument se)
                    row[0].strip() if row[0] else None,  # username (CSV index 0)
                    row[1].strip() if row[1] else None,  # password (CSV index 1)
                    row[2].strip() if row[2] else None,  # name (CSV index 2)
                    row[3].strip() if row[3] else None,  # phone (CSV index 3)
                    row[5].strip() if row[5] else None,  # email (CSV index 5)
                )
                rows_batch.append(params)

                if len(rows_batch) >= batch_size:
                    staged_for_commit_count = 0
                    for p_batch_item in rows_batch:
                        if _execute_single_insert_no_commit(
                            connection, insert_query, p_batch_item
                        ):
                            staged_for_commit_count += 1

                    if staged_for_commit_count > 0:
                        try:
                            connection.commit()
                            print(
                                f"Committed batch of {staged_for_commit_count} operations for admins."
                            )
                            total_successful_db_operations += staged_for_commit_count
                        except Error as e_commit:
                            print(
                                f"Error committing batch for admins: {e_commit}. Rolling back."
                            )
                            connection.rollback()

                    rows_batch = []

            if rows_batch:
                staged_for_commit_count = 0
                for p_batch_item in rows_batch:
                    if _execute_single_insert_no_commit(
                        connection, insert_query, p_batch_item
                    ):
                        staged_for_commit_count += 1

                if staged_for_commit_count > 0:
                    try:
                        connection.commit()
                        print(
                            f"Committed final batch of {staged_for_commit_count} operations for admins."
                        )
                        total_successful_db_operations += staged_for_commit_count
                    except Error as e_commit:
                        print(
                            f"Error committing final batch for admins: {e_commit}. Rolling back."
                        )
                        connection.rollback()

            print(f"Finished importing admins from {file_path}.")
            print(f"Total rows processed from CSV: {total_rows_processed_from_csv}.")
            print(
                f"Total successful database insert/update operations: {total_successful_db_operations}."
            )

    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
    except Exception as e:
        print(f"An unexpected error occurred while importing {file_path}: {e}")
        traceback.print_exc()
        if connection and connection.is_connected():
            connection.rollback()


def import_users(connection, school_id_arg, file_path, batch_size=100):
    print(
        f"Importing {file_path} into users for school {school_id_arg} (Batch Size: {batch_size})..."
    )

    # `name` ko backticks (`) mein daala gaya hai kyunki yeh ek SQL keyword hai.
    insert_query = """
    INSERT INTO users (school_id, teacher_id, `name`, biometric_code, phone, category) 
    VALUES (%s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        `name` = VALUES(`name`),
        biometric_code = VALUES(biometric_code),
        phone = VALUES(phone),
        category = VALUES(category),
        school_id = VALUES(school_id)
    """

    rows_batch = []
    total_rows_processed_from_csv = 0
    total_successful_db_operations = 0

    try:
        with open(file_path, mode="r", encoding="utf-8") as file:
            reader = csv.reader(file)
            try:
                header = next(reader)
            except StopIteration:
                print(f"Warning: CSV file {file_path} is empty. Skipping.")
                return

            for row_num, row in enumerate(reader):
                total_rows_processed_from_csv += 1

                # Ab hum 5 columns check karenge
                if len(row) < 5:
                    print(
                        f"Skipping malformed CSV row #{row_num+1} in {file_path}: {row}"
                    )
                    continue

                # Parameters ab naye CSV structure ke hisaab se banenge
                params = (
                    school_id_arg,  # school_id script se aayega
                    row[0].strip() if row[0] else None,  # teacher_id (CSV index 0)
                    row[1].strip() if row[1] else None,  # name (CSV index 1)
                    row[2].strip() if row[2] else None,  # biometric_code (CSV index 2)
                    row[3].strip() if row[3] else None,  # phone (CSV index 3)
                    row[4].strip() if row[4] else None,  # category (CSV index 4)
                )
                rows_batch.append(params)

                if len(rows_batch) >= batch_size:
                    staged_for_commit_count = 0
                    for p_batch_item in rows_batch:
                        if _execute_single_insert_no_commit(
                            connection, insert_query, p_batch_item
                        ):
                            staged_for_commit_count += 1

                    if staged_for_commit_count > 0:
                        try:
                            connection.commit()
                            print(
                                f"Committed batch of {staged_for_commit_count} operations for users."
                            )
                            total_successful_db_operations += staged_for_commit_count
                        except Error as e_commit:
                            print(
                                f"Error committing batch for users: {e_commit}. Rolling back."
                            )
                            connection.rollback()

                    rows_batch = []

            if rows_batch:
                staged_for_commit_count = 0
                for p_batch_item in rows_batch:
                    if _execute_single_insert_no_commit(
                        connection, insert_query, p_batch_item
                    ):
                        staged_for_commit_count += 1

                if staged_for_commit_count > 0:
                    try:
                        connection.commit()
                        print(
                            f"Committed final batch of {staged_for_commit_count} operations for users."
                        )
                        total_successful_db_operations += staged_for_commit_count
                    except Error as e_commit:
                        print(
                            f"Error committing final batch for users: {e_commit}. Rolling back."
                        )
                        connection.rollback()

            print(f"Finished importing users from {file_path}.")
            print(f"Total rows processed from CSV: {total_rows_processed_from_csv}.")
            print(
                f"Total successful database insert/update operations: {total_successful_db_operations}."
            )

    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
    except Exception as e:
        print(f"An unexpected error occurred while importing {file_path}: {e}")
        traceback.print_exc()
        if connection and connection.is_connected():
            connection.rollback()


def import_daily_schedules(connection, school_id, file_path, day_of_week, batch_size=200):
    print(f"Importing {file_path} for {day_of_week} into daily_schedules...")

    # Step 1: Delete existing data for this school and day
    try:
        with connection.cursor() as cursor:
            delete_query = "DELETE FROM daily_schedules WHERE school_id = %s AND day_of_week = %s"
            cursor.execute(delete_query, (school_id, day_of_week))
            connection.commit()
            print(f"Deleted existing records for {school_id} - {day_of_week}.")
    except Error as e_del:
        print(f"Error deleting records: {e_del}")
        connection.rollback()
        return

    # Step 2: Prepare a SAHI INSERT query
    # Isme 'class' column hai, aur column ke naam CSV se match karte hain.
    insert_query = """
    INSERT INTO daily_schedules (school_id, day_of_week, teacher_id, name, category, classes, subject, period_number, class_info)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) 
    """

    rows_to_insert = []
    try:
        with open(file_path, mode="r", encoding="utf-8") as file:
            reader = csv.reader(file)
            header = next(reader)
            # CSV header se period columns ka pata lagao
            period_cols_header = header[5:] # period1 se shuru hone wale columns

            for csv_row in reader:
                # CSV se data nikalo
                teacher_id = csv_row[0].strip()
                name = csv_row[1].strip()
                category = csv_row[2].strip()
                classes = csv_row[3].strip() # Ye naya 'classes' column hai
                subject = csv_row[4].strip() # Ye 'subject' column hai

                # Har period ke liye ek alag row banao
                for i, period_col_name in enumerate(period_cols_header):
                    period_number = int(re.search(r'\d+', period_col_name).group()) # 'period1' se 1 nikalo
                    class_info = csv_row[5 + i].strip() if len(csv_row) > (5 + i) else None
                    
                    # Agar period 'Free' nahi hai, tabhi row banao
                    if class_info and class_info.upper() != 'FREE':
                        params = (
                            school_id, day_of_week, teacher_id, name, category, 
                            classes, subject, period_number, class_info
                        )
                        rows_to_insert.append(params)

        # Batch insert using executemany for speed
        if rows_to_insert:
            with connection.cursor() as cursor:
                cursor.executemany(insert_query, rows_to_insert)
                connection.commit()
                print(f"Successfully inserted {cursor.rowcount} period entries for {day_of_week}.")

    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
    except Exception as e:
        print(f"Error during import: {e}")
        traceback.print_exc()
        connection.rollback()

# --- Main Import Logic ---
if __name__ == "__main__":
    # Setup command-line argument parsing
    parser = argparse.ArgumentParser(
        description="Import CSV data into MySQL/TiDB database."  # Description thoda general rakha
    )
    parser.add_argument(
        "--school_id", required=True, help="The school ID for the data."
    )
    # Option 1: Process all CSVs in a directory
    parser.add_argument(
        "--csv_dir",
        help="Directory containing all CSV files for this school to import (processes all known CSVs).",
    )
    # Option 2: Process a single specific CSV file for a specific table
    parser.add_argument(
        "--csv_file",
        help="Path to a specific CSV file to import.",
    )
    parser.add_argument(
        "--table_name",
        help="Name of the database table to import the specific CSV file into (required if --csv_file is used).",
    )

    args = parser.parse_args()

    school_id_to_import = args.school_id

    # Validate arguments: EITHER --csv_dir OR (--csv_file AND --table_name) must be provided
    if args.csv_dir and (args.csv_file or args.table_name):
        parser.error(
            "Cannot use --csv_dir with --csv_file or --table_name. Use one mode or the other."
        )
        exit(1)  # Exit script
    if args.csv_file and not args.table_name:
        parser.error("--table_name is required when --csv_file is specified.")
        exit(1)  # Exit script
    if not args.csv_dir and not args.csv_file:
        parser.error(
            "Either --csv_dir or --csv_file (with --table_name) must be specified."
        )
        exit(1)  # Exit script

    print(f"--- Starting CSV Import Process for School ID: {school_id_to_import} ---")

    db_connection = create_db_connection()

    if not db_connection:  # Agar connection fail hota hai toh yahin se exit
        print("\nDatabase connection failed. CSV Import aborted.")
        exit(1)

    if args.csv_dir:
        schools_csv_path_for_check = os.path.join(args.csv_dir, "schools.csv")
        if os.path.exists(schools_csv_path_for_check):
            print(
                f"\n--- Stage: Ensuring 'schools' table is up-to-date from: {schools_csv_path_for_check} ---"
            )
            import_schools(
                db_connection, schools_csv_path_for_check
            )  # import_schools school_id argument nahi leta
        else:
            print(
                f"INFO: schools.csv not found in --csv_dir '{args.csv_dir}'. Assuming target school '{school_id_to_import}' already exists in DB."
            )
    elif args.csv_file and args.table_name.lower() == "schools":
        # Agar user specifically schools.csv import kar raha hai
        print(f"\n--- Stage: Importing specific schools file: {args.csv_file} ---")
        if os.path.exists(args.csv_file):
            import_schools(db_connection, args.csv_file)
        else:
            print(f"ERROR: Specified schools.csv file not found: {args.csv_file}")
            db_connection.close()
            exit(1)

    cursor = None
    school_exists_in_db = False
    try:
        cursor = db_connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT school_id FROM schools WHERE school_id = %s", (school_id_to_import,)
        )
        result = cursor.fetchone()
        if result:
            school_exists_in_db = True
    except Error as e_check:
        print(f"Error checking for school_id '{school_id_to_import}': {e_check}")
    finally:
        if cursor:
            cursor.close()

    if not school_exists_in_db:
        print(
            f"\nCRITICAL ERROR: School ID '{school_id_to_import}' NOT FOUND in the 'schools' table."
        )
        print(
            "Please ensure the school exists in the database (e.g., by importing schools.csv first or ensuring it's pre-populated)."
        )
        db_connection.close()
        exit(1)

    print(
        f"\n--- Confirmed School ID '{school_id_to_import}' exists in 'schools' table. ---"
    )

    # --- Mode 1: Import a single specified CSV file ---
    if args.csv_file and args.table_name:
        print(
            f"--- Importing single file: {args.csv_file} into table: {args.table_name} ---"
        )
        csv_file_path = args.csv_file

        if not os.path.exists(csv_file_path):
            print(f"ERROR: Specified CSV file not found: {csv_file_path}")
        else:
            target_table = args.table_name.lower()
            if target_table == "users":
                import_users(db_connection, school_id_to_import, csv_file_path)
            elif target_table == "admins":
                import_admins(db_connection, school_id_to_import, csv_file_path)
            # elif target_table == "arrangements":
            #     import_arrangements(db_connection, school_id_to_import, csv_file_path)
            # elif target_table == "attendance":
            #     import_attendance(db_connection, school_id_to_import, csv_file_path)
            # elif (
            #     target_table == "schedules_summary" or target_table == "schedules"
            # ):  # schedules.csv ke liye
            #     import_schedules_summary(
            #         db_connection, school_id_to_import, csv_file_path
            #     )
            # elif target_table == "workload_counter":
            #     import_workload_counter(
            #         db_connection, school_id_to_import, csv_file_path
            #     )
            # elif target_table == "coverage_tracking":
            #     import_coverage_tracking(
            #         db_connection, school_id_to_import, csv_file_path
            #     )
            # elif target_table == "substitutes":
            #     import_substitutes(db_connection, school_id_to_import, csv_file_path)
            # elif target_table == "suspended_dates":
            #     import_suspended_dates(
            #         db_connection, school_id_to_import, csv_file_path
            #     )
            # elif target_table == "timing":
            #     import_timing(db_connection, school_id_to_import, csv_file_path)
            # daily_schedules ke liye alag se handle karna padega agar file ka naam day specific hai
            # Ya fir user ko table_name mein 'schedule_monday' jaisa kuch dena hoga
            elif target_table.startswith("schedule_"):
                day_name_from_table = target_table.split("_")[
                    -1
                ]  # Aakhiri part day hoga
                valid_days = [
                    "monday",
                    "tuesday",
                    "wednesday",
                    "thursday",
                    "friday",
                    "saturday",
                ]
                if day_name_from_table in valid_days:
                    import_daily_schedules(
                        db_connection,
                        school_id_to_import,
                        csv_file_path,
                        day_name_from_table.capitalize(),
                    )
                else:
                    print(
                        f"ERROR: Invalid day '{day_name_from_table}' in table_name for daily schedule. Expected format 'schedule_dayname'."
                    )
            elif (
                target_table == "schools"
            ):  # Agar specifically schools.csv import karna ho (upar handle ho chuka hai, par yahan bhi rakh sakte hain)
                print(
                    "INFO: schools.csv should have been handled already if it was the target."
                )
                if not os.path.exists(csv_file_path):  # Double check
                    import_schools(db_connection, csv_file_path)
            else:
                print(
                    f"ERROR: Importing into table '{args.table_name}' is not supported for single file import or table name not recognized."
                )

    # --- Mode 2: Import all CSVs from a directory (original behavior) ---
    elif args.csv_dir:
        csv_data_directory = args.csv_dir
        print(
            f"--- Importing all relevant CSV files from directory: {csv_data_directory} ---"
        )

        # (Aapka original import_tasks wala loop yahan aa jayega)
        # schools.csv ko pehle hi (school_id check se pehle) handle kar liya gaya hai agar --csv_dir mode hai

        import_tasks_for_dir_mode = [  # schools.csv is handled above
            (import_admins, "admins.csv", False),
            (import_users, "users.csv", False),
            # (import_arrangements, "arrangements.csv", False),
            # (import_attendance, "attendance.csv", False),
            (import_daily_schedules, "schedule_{day}.csv", True),
            # (import_schedules_summary, "schedules.csv", False),
            # (import_workload_counter, "workload_counter.csv", False),
            # (import_coverage_tracking, "coverage_tracking.csv", False),
            # (import_substitutes, "substitutes.csv", False),
            # (import_suspended_dates, "suspended_dates.csv", False),
            # (import_timing, "timing.csv", False),
        ]

        days_for_schedule = [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
        ]

        for import_func, csv_pattern, needs_day_loop in import_tasks_for_dir_mode:
            if needs_day_loop:
                for day_name in days_for_schedule:
                    specific_csv_filename = csv_pattern.format(day=day_name)
                    csv_file_path = os.path.join(
                        csv_data_directory, specific_csv_filename
                    )
                    if os.path.exists(csv_file_path):
                        import_func(
                            db_connection,
                            school_id_to_import,
                            csv_file_path,
                            day_name.capitalize(),
                        )
                    else:
                        print(
                            f"INFO: CSV file not found for {day_name.capitalize()} schedule: {csv_file_path}. Skipping."
                        )
            else:
                csv_file_path = os.path.join(csv_data_directory, csv_pattern)
                if os.path.exists(csv_file_path):
                    import_func(db_connection, school_id_to_import, csv_file_path)
                else:
                    print(
                        f"INFO: CSV file not found: {csv_file_path}. Skipping import for {csv_pattern}."
                    )

    db_connection.close()
    print("\n--- CSV Import process finished. ---")
# test line to trigger git