import schedule
import time
from mysql.connector import Error
import pandas as pd
import traceback
import threading
from datetime import datetime, date
import data_manager
import pytz
import streamlit as st
import os

class AutoMarker:
    def __init__(self, school_id, data_manager_instance, ui_update_callback=None):
        """Railway-optimized AutoMarker with timezone handling"""
        self.school_id = school_id
        self.data_manager_instance = data_manager_instance
        self.running = False
        self.ui_update_callback = ui_update_callback
        
        # ✅ FIXED: Railway timezone handling
        self.timezone = pytz.timezone('Asia/Kolkata')  # IST for Railway
        
        # Load timing settings
        try:
            if self.data_manager_instance is None:
                raise ValueError("DataManager instance is None")

            saved_timing = self.data_manager_instance.get_auto_marking_timing(self.school_id)
            self._hour = saved_timing.get("hour", 10)
            self._minute = saved_timing.get("minute", 0)
            self._enabled = saved_timing.get("enabled", False)
            
            print(f"INFO AutoMarker: Initialized for school {self.school_id} - Time: {self._hour:02d}:{self._minute:02d}, Enabled: {self._enabled}")
        except Exception as e:
            print(f"ERROR AutoMarker init: {e}")
            self._hour = 10
            self._minute = 0
            self._enabled = False

    def get_timing(self):
        return {"hour": self._hour, "minute": self._minute, "enabled": self._enabled}

    def set_timing(self, hour, minute, enabled=True):
        """✅ FIXED: Railway-optimized timing setting with proper timezone"""
        print(f"INFO AutoMarker: Setting timing for school {self.school_id} to {hour:02d}:{minute:02d}, Enabled: {enabled}")
        
        try:
            if not self.data_manager_instance:
                print("ERROR: DataManager instance missing")
                return False

            # Save to database
            success = self.data_manager_instance.set_auto_marking_timing(
                self.school_id, hour, minute, enabled
            )
            
            if success:
                # Update internal state
                self._hour = hour
                self._minute = minute
                self._enabled = enabled
                
                # ✅ CRITICAL: Restart scheduler for Railway
                self.restart_scheduler()
                print(f"SUCCESS: Timing saved and scheduler restarted for {self.school_id}")
                return True
            else:
                print(f"ERROR: Failed to save timing for {self.school_id}")
                return False
                
        except Exception as e:
            print(f"CRITICAL ERROR setting timing: {e}")
            traceback.print_exc()
            return False

    def mark_absences(self):
        try:
            ist_now = datetime.now(self.timezone)
            today_date = ist_now.date()
            print(f"\n--- ✅ AutoMarker (Batch Process) STARTED for {self.school_id} at {ist_now.strftime('%Y-%m-%d %H:%M:%S %Z')} ---")

            if today_date.weekday() == 6: # Sunday
                print("INFO: Today is Sunday, skipping auto-marking.")
                return

            if not self.data_manager_instance: return

            today_str = str(today_date)
            if not self.data_manager_instance.get_present_teachers(self.school_id, today_str):
                print("INFO: No teachers present today, assuming holiday.")
                return

            marked_teachers_today = set(self.data_manager_instance.get_all_marked_teacher_ids_for_date(self.school_id, today_str))
            all_teachers = self.data_manager_instance.get_all_teachers(self.school_id)
            if not all_teachers: return

            teachers_to_mark_absent = [
                teacher.get("teacher_id") for teacher in all_teachers 
                if teacher.get("teacher_id") and teacher.get("teacher_id") not in marked_teachers_today
            ]

            if teachers_to_mark_absent:
                print(f"INFO: Found {len(teachers_to_mark_absent)} unmarked teachers to process: {teachers_to_mark_absent}")
                attendance_updates = [(teacher_id, 'absent') for teacher_id in teachers_to_mark_absent]
                
                success_count = self.data_manager_instance.bulk_update_attendance(self.school_id, attendance_updates, is_auto=True)
                
                if success_count > 0:
                    print(f"INFO: Successfully bulk marked {success_count} teachers as absent.")
                    print(f"INFO: Proceeding to create arrangements for all {success_count} absent teachers.")
                    self.data_manager_instance.process_bulk_arrangements(self.school_id, teachers_to_mark_absent, today_date)
            else:
                print("INFO: All teachers are already marked. No action needed.")

            print(f"--- ✅ AutoMarker (Batch Process) COMPLETED for {self.school_id} ---")
            if self.ui_update_callback: self.ui_update_callback()

        except Exception as e:
            print(f"CRITICAL ERROR in mark_absences (Final Fix): {e}")
            traceback.print_exc()

    def schedule_job(self):
        """✅ RAILWAY-OPTIMIZED job scheduling"""
        if not self._enabled:
            print(f"INFO: Auto-marking disabled for {self.school_id}")
            job_tag = f"automark_{self.school_id}"
            schedule.clear(job_tag)
            return

        job_time = f"{self._hour:02d}:{self._minute:02d}"
        job_tag = f"automark_{self.school_id}"

        # Clear existing jobs
        existing_jobs = schedule.get_jobs(job_tag)
        if existing_jobs:
            print(f"INFO: Clearing {len(existing_jobs)} existing jobs for {job_tag}")
            schedule.clear(job_tag)

        # ✅ RAILWAY FIX: Schedule with proper timezone awareness
        try:
            schedule.every().day.at(job_time, "Asia/Kolkata").do(self.mark_absences).tag(job_tag) # Timezone added
            print(f"SUCCESS: Scheduled job {job_tag} at {job_time} IST")
            print(f"INFO: Total scheduled jobs: {len(schedule.get_jobs(job_tag))}")
        except Exception as e:
            print(f"ERROR scheduling job: {e}")

    def start(self):
        """✅ RAILWAY-OPTIMIZED startup"""
        if not self.running:
            print(f"INFO: Starting AutoMarker for school {self.school_id}")
            self.running = True
            
            # ✅ CRITICAL: Start scheduler thread as daemon for Railway
            self.scheduler_thread = threading.Thread(
                target=self._run_scheduler, 
                daemon=True,  # Important for Railway
                name=f"AutoMarker-{self.school_id}"
            )
            self.scheduler_thread.start()
            
            # Schedule the job
            self.schedule_job()
            print(f"SUCCESS: AutoMarker started for {self.school_id}")
        else:
            print(f"INFO: AutoMarker already running for {self.school_id}")

    def stop(self):
        """✅ RAILWAY-OPTIMIZED stop"""
        if self.running:
            print(f"INFO: Stopping AutoMarker for {self.school_id}")
            self.running = False
            
            # Clear scheduled jobs
            job_tag = f"automark_{self.school_id}"
            schedule.clear(job_tag)
            print(f"INFO: Cleared jobs for {job_tag}")
        else:
            print(f"INFO: AutoMarker not running for {self.school_id}")

    def restart_scheduler(self):
        """✅ CRITICAL: Railway restart fix"""
        print(f"INFO: Restarting scheduler for {self.school_id}")
        
        # Clear old jobs first
        job_tag = f"automark_{self.school_id}"
        schedule.clear(job_tag)
        
        # Re-schedule if enabled
        if self._enabled and self.running:
            self.schedule_job()
            print(f"SUCCESS: Scheduler restarted for {self.school_id}")
        else:
            print(f"INFO: Scheduler not restarted - enabled: {self._enabled}, running: {self.running}")

    def _run_scheduler(self):
        """✅ RAILWAY-OPTIMIZED scheduler loop"""
        print(f"INFO: Scheduler thread started for {self.school_id}")
        
        while self.running:
            try:
                # Run pending jobs
                schedule.run_pending()
                
                # ✅ RAILWAY OPTIMIZATION: Longer sleep to reduce CPU usage
                time.sleep(30)  # Check every 30 seconds instead of 1 second
                
            except Exception as e:
                print(f"ERROR in scheduler loop: {e}")
                time.sleep(60)  # Wait longer on error

        print(f"INFO: Scheduler thread stopped for {self.school_id}")

    def get_next_run_time(self):
        """Get next scheduled run time in IST"""
        try:
            job_tag = f"automark_{self.school_id}"
            jobs = schedule.get_jobs(job_tag)
            if jobs:
                next_run = jobs[0].next_run
                if next_run:
                    # 'schedule' library with timezone returns timezone-aware datetime objects
                    return next_run.strftime("%Y-%m-%d %H:%M:%S %Z")
            return "Not scheduled"
        except Exception as e:
            print(f"ERROR getting next run time: {e}")
            return "Error"

    def is_running(self):
        """Check if AutoMarker is active"""
        return self.running and self._enabled

    def get_status(self):
        """Get comprehensive AutoMarker status"""
        return {
            "running": self.running,
            "enabled": self._enabled,
            "scheduled_time": f"{self._hour:02d}:{self._minute:02d}",
            "next_run": self.get_next_run_time(),
            "timezone": "Asia/Kolkata (IST)",
            "thread_alive": hasattr(self, 'scheduler_thread') and self.scheduler_thread.is_alive()
        }

# ✅ RAILWAY DEPLOYMENT HELPER
def create_railway_optimized_automarker(school_id, data_manager_instance):
    """Factory function for Railway deployment"""
    try:
        automarker = AutoMarker(school_id, data_manager_instance)
        
        # Auto-start for Railway
        if os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("IS_RAILWAY", "false").lower() == "true":
            print("INFO: Railway environment detected, auto-starting AutoMarker")
            automarker.start()
            
        return automarker
    except Exception as e:
        print(f"ERROR creating AutoMarker: {e}")
        return None