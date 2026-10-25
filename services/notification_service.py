from models.notification import Notification
from models.reminder import Reminder
from models.appointment import Appointment
from models.vaccination import Vaccination
from models.insurance import InsurancePolicy
from datetime import datetime, timedelta

def create_notification(user_id, type, title, message, link=None):
    return Notification.create(user_id, type, title, message, link)

def get_unread_count(user_id):
    return Notification.get_unread_count(user_id)

def mark_as_read(notification_id, user_id):
    return Notification.mark_read(notification_id, user_id)

def mark_all_read(user_id):
    return Notification.mark_all_read(user_id)

def generate_reminders(user_id):
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)
    
    # Medicine reminders
    today_reminders = Reminder.get_today(user_id)
    for rem in today_reminders:
        if rem['status'] == 'pending':
            create_notification(
                user_id, 'reminder', 
                f"Medicine Reminder: {rem['medicine_name']}",
                f"Don't forget to take {rem['medicine_name']} at {rem['reminder_time']}",
                f"/medicines/{rem['medicine_id']}"
            )
            
    # Appointments tomorrow
    upcoming_appts = Appointment.get_upcoming(user_id)
    for appt in upcoming_appts:
        appt_date = datetime.strptime(appt['visit_date'], '%Y-%m-%d').date()
        if appt_date == tomorrow:
            create_notification(
                user_id, 'appointment',
                f"Upcoming Appointment",
                f"Appointment with Dr. {appt['doctor_name']} tomorrow at {appt['visit_time']}",
                f"/appointments/{appt['id']}"
            )
            
    # Expiring insurances
    expiring_policies = InsurancePolicy.get_expiring(user_id, days=30)
    for policy in expiring_policies:
        create_notification(
            user_id, 'insurance',
            "Insurance Renewal Due",
            f"Policy {policy['provider']} expires on {policy['expiry_date']}",
            f"/insurance/{policy['id']}"
        )
