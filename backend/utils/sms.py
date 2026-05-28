"""
SMS Utility — Twilio Integration
"""
import os
from twilio.rest import Client
from flask import current_app

class SMSService:
    """SMS service for sending notifications"""
    
    def __init__(self):
        """Initialize Twilio client"""
        self.account_sid = current_app.config.get('TWILIO_ACCOUNT_SID')
        self.auth_token = current_app.config.get('TWILIO_AUTH_TOKEN')
        self.from_number = current_app.config.get('TWILIO_PHONE_NUMBER')
        
        if self.account_sid and self.auth_token:
            self.client = Client(self.account_sid, self.auth_token)
        else:
            self.client = None
    
    def send_payment_confirmation(self, phone_number, amount, reference):
        """Send payment confirmation SMS"""
        message = f"Dear Student, Payment of SLL {amount:,} (Ref: {reference}) received. Thank you for choosing Njala University. Balance available at portal."
        return self.send_sms(phone_number, message)
    
    def send_payment_reminder(self, phone_number, amount_due, due_date):
        """Send fee payment reminder"""
        message = f"Reminder: You have an outstanding fee balance of SLL {amount_due:,} due by {due_date}. Pay online at njala-fees.edu.sl"
        return self.send_sms(phone_number, message)
    
    def send_exam_clearance_notice(self, phone_number):
        """Send exam clearance requirement notice"""
        message = "Important: Clear all outstanding fees before taking exams. Visit njala-fees.edu.sl to pay now."
        return self.send_sms(phone_number, message)
    
    def send_payment_failed_notification(self, phone_number, reference, reason=""):
        """Send payment failure notification"""
        message = f"Payment {reference} failed. Reason: {reason}. Please try again or contact finance@njala.edu.sl"
        return self.send_sms(phone_number, message)
    
    def send_sms(self, phone_number, message):
        """Send SMS message"""
        if not self.client:
            print(f"[SMS] No Twilio configured. Would send to {phone_number}: {message}")
            return {'success': True, 'message': 'SMS queued (dev mode)'}
        
        try:
            msg = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=phone_number
            )
            return {
                'success': True,
                'message_sid': msg.sid,
                'status': msg.status
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def send_bulk_sms(self, phone_numbers, message):
        """Send SMS to multiple recipients"""
        results = []
        for phone in phone_numbers:
            result = self.send_sms(phone, message)
            results.append({
                'phone': phone,
                'sent': result.get('success', False)
            })
        return results


def send_sms_notification(phone_number, notification_type, **kwargs):
    """Helper function to send SMS notifications"""
    sms = SMSService()
    
    notification_handlers = {
        'payment_confirmation': lambda: sms.send_payment_confirmation(
            phone_number,
            kwargs.get('amount'),
            kwargs.get('reference')
        ),
        'payment_reminder': lambda: sms.send_payment_reminder(
            phone_number,
            kwargs.get('amount_due'),
            kwargs.get('due_date')
        ),
        'exam_clearance': lambda: sms.send_exam_clearance_notice(phone_number),
        'payment_failed': lambda: sms.send_payment_failed_notification(
            phone_number,
            kwargs.get('reference'),
            kwargs.get('reason', '')
        ),
    }
    
    handler = notification_handlers.get(notification_type)
    if handler:
        return handler()
    else:
        return {'success': False, 'error': f'Unknown notification type: {notification_type}'}
