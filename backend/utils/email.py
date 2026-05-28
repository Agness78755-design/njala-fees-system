"""
Email Utility — Flask-Mail Integration
"""
from flask_mail import Mail, Message
from flask import current_app, render_template_string
from datetime import datetime

mail = Mail()

class EmailService:
    """Email service for sending notifications"""
    
    @staticmethod
    def send_payment_receipt(user_email, user_name, amount, reference, payment_method):
        """Send payment receipt email"""
        subject = f"Payment Receipt - Njala University Fees Portal"
        
        html_body = f"""
        <html>
            <body style="font-family: 'DM Sans', sans-serif; line-height: 1.6; color: #333;">
                <h2 style="color: #1e5c2e;">Payment Confirmation</h2>
                <p>Dear {user_name},</p>
                <p>Your payment has been successfully received and processed.</p>
                
                <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                    <tr style="background: #f0f4f1;">
                        <td style="padding: 10px; border: 1px solid #ddd;"><strong>Reference Number</strong></td>
                        <td style="padding: 10px; border: 1px solid #ddd;">{reference}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border: 1px solid #ddd;"><strong>Amount</strong></td>
                        <td style="padding: 10px; border: 1px solid #ddd;">SLL {amount:,}</td>
                    </tr>
                    <tr style="background: #f0f4f1;">
                        <td style="padding: 10px; border: 1px solid #ddd;"><strong>Payment Method</strong></td>
                        <td style="padding: 10px; border: 1px solid #ddd;">{payment_method}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border: 1px solid #ddd;"><strong>Date & Time</strong></td>
                        <td style="padding: 10px; border: 1px solid #ddd;">{datetime.utcnow().strftime('%d %B %Y, %H:%M UTC')}</td>
                    </tr>
                </table>
                
                <p>Your receipt has been saved in your account dashboard. You can download it anytime.</p>
                
                <p style="margin-top: 30px; color: #666; font-size: 0.9em;">
                    If you have any questions, contact: <a href="mailto:finance@njala.edu.sl">finance@njala.edu.sl</a><br>
                    © Njala University Finance Office
                </p>
            </body>
        </html>
        """
        
        return EmailService.send_email(user_email, subject, html_body)
    
    @staticmethod
    def send_payment_reminder(user_email, user_name, amount_due, due_date):
        """Send fee payment reminder"""
        subject = "Fee Payment Reminder - Njala University"
        
        html_body = f"""
        <html>
            <body style="font-family: 'DM Sans', sans-serif; line-height: 1.6; color: #333;">
                <h2 style="color: #d4821a;">Payment Reminder</h2>
                <p>Dear {user_name},</p>
                <p style="color: #c0392b; font-weight: bold;">You have an outstanding fee balance that requires payment.</p>
                
                <div style="background: #fef3e2; border-left: 4px solid #d4821a; padding: 15px; margin: 20px 0;">
                    <p style="margin: 0;"><strong>Outstanding Amount:</strong> SLL {amount_due:,}</p>
                    <p style="margin: 10px 0 0 0;"><strong>Due Date:</strong> {due_date}</p>
                </div>
                
                <p>Please log in to your student portal and make payment to avoid complications with exam clearance.</p>
                
                <p>
                    <a href="https://njala-fees.edu.sl/dashboard" 
                       style="display: inline-block; background: #1e5c2e; color: white; padding: 10px 20px; 
                              text-decoration: none; border-radius: 5px;">
                        Pay Now →
                    </a>
                </p>
                
                <p style="margin-top: 30px; color: #666; font-size: 0.9em;">
                    Questions? Contact Finance Office: <a href="mailto:finance@njala.edu.sl">finance@njala.edu.sl</a>
                </p>
            </body>
        </html>
        """
        
        return EmailService.send_email(user_email, subject, html_body)
    
    @staticmethod
    def send_welcome_email(user_email, user_name, student_id):
        """Send welcome email to new student"""
        subject = "Welcome to Njala University Fees Portal"
        
        html_body = f"""
        <html>
            <body style="font-family: 'DM Sans', sans-serif; line-height: 1.6; color: #333;">
                <h2 style="color: #1e5c2e;">Welcome to Njala University</h2>
                <p>Hello {user_name},</p>
                <p>Your account has been successfully created on the Njala University Fees Management Portal.</p>
                
                <h3 style="color: #256b36;">Your Account Details:</h3>
                <ul style="background: #f0f4f1; padding: 20px; border-radius: 5px;">
                    <li><strong>Student ID:</strong> {student_id}</li>
                    <li><strong>Portal URL:</strong> njala-fees.edu.sl</li>
                    <li><strong>Email:</strong> {user_email}</li>
                </ul>
                
                <h3 style="color: #256b36;">Quick Start:</h3>
                <ol>
                    <li>Log in with your Student ID and password</li>
                    <li>View your fee structure and payment schedule</li>
                    <li>Make payments via Orange Money, Africell, or Bank Transfer</li>
                    <li>Download receipts anytime from your dashboard</li>
                </ol>
                
                <p style="margin-top: 30px; color: #666; font-size: 0.9em;">
                    Need help? Email: <a href="mailto:finance@njala.edu.sl">finance@njala.edu.sl</a><br>
                    Phone: +232 22 000 000
                </p>
            </body>
        </html>
        """
        
        return EmailService.send_email(user_email, subject, html_body)
    
    @staticmethod
    def send_email(recipient, subject, html_body):
        """Send email using Flask-Mail"""
        try:
            msg = Message(
                subject=subject,
                recipients=[recipient],
                html=html_body,
                sender=current_app.config.get('MAIL_DEFAULT_SENDER', 'finance@njala.edu.sl')
            )
            mail.send(msg)
            return {'success': True, 'message': 'Email sent successfully'}
        except Exception as e:
            print(f"Email Error: {str(e)}")
            return {'success': False, 'error': str(e)}


def init_mail(app):
    """Initialize mail extension with app"""
    mail.init_app(app)
