"""
Email service for sending OTP and other notifications
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from datetime import datetime

class EmailService:
    def __init__(self):
        # Email configuration from environment variables
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.email_user = os.getenv('EMAIL_USER', '')
        self.email_password = os.getenv('EMAIL_PASSWORD', '')
        self.from_name = os.getenv('FROM_NAME', 'Jishu Backend')
        
    def send_otp_email(self, to_email, otp, user_name=None):
        """Send OTP email to user"""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = f"{self.from_name} <{self.email_user}>"
            msg['To'] = to_email
            msg['Subject'] = "Your OTP for Jishu Backend"
            
            # Email body
            body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #2c3e50;">🔐 Your OTP Code</h2>
                    
                    <p>Hello {user_name or 'User'},</p>
                    
                    <p>Your One-Time Password (OTP) for Jishu Backend is:</p>
                    
                    <div style="background-color: #f8f9fa; padding: 20px; text-align: center; border-radius: 8px; margin: 20px 0;">
                        <h1 style="color: #007bff; font-size: 32px; margin: 0; letter-spacing: 5px;">{otp}</h1>
                    </div>
                    
                    <p><strong>⏰ This OTP will expire in 10 minutes.</strong></p>
                    
                    <p>If you didn't request this OTP, please ignore this email.</p>
                    
                    <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                    
                    <p style="color: #666; font-size: 12px;">
                        This is an automated email from Jishu Backend. Please do not reply to this email.
                        <br>
                        Generated at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC
                    </p>
                </div>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(body, 'html'))
            
            # Send email
            if self.email_user and self.email_password:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                server.starttls()
                server.login(self.email_user, self.email_password)
                text = msg.as_string()
                server.sendmail(self.email_user, to_email, text)
                server.quit()
                return True, "OTP email sent successfully"
            else:
                # For development/testing - just print OTP
                print(f"📧 OTP Email (Development Mode)")
                print(f"To: {to_email}")
                print(f"OTP: {otp}")
                print(f"Expires in: 10 minutes")
                print("-" * 40)
                return True, "OTP email sent (development mode)"
                
        except Exception as e:
            print(f"❌ Failed to send OTP email: {str(e)}")
            return False, f"Failed to send OTP email: {str(e)}"
    
    def send_welcome_email(self, to_email, user_name):
        """Send welcome email to new user"""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = f"{self.from_name} <{self.email_user}>"
            msg['To'] = to_email
            msg['Subject'] = "Welcome to Jishu Backend!"
            
            # Email body
            body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #28a745;">🎉 Welcome to Jishu Backend!</h2>
                    
                    <p>Hello {user_name},</p>
                    
                    <p>Welcome to Jishu Backend! Your account has been successfully created.</p>
                    
                    <p>You can now access all features of our platform using your email address.</p>
                    
                    <div style="background-color: #e8f5e8; padding: 15px; border-radius: 8px; margin: 20px 0;">
                        <p style="margin: 0;"><strong>✅ Your account is now active and ready to use!</strong></p>
                    </div>
                    
                    <p>If you have any questions or need assistance, please don't hesitate to contact our support team.</p>
                    
                    <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                    
                    <p style="color: #666; font-size: 12px;">
                        Thank you for choosing Jishu Backend!
                        <br>
                        Generated at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC
                    </p>
                </div>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(body, 'html'))
            
            # Send email
            if self.email_user and self.email_password:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                server.starttls()
                server.login(self.email_user, self.email_password)
                text = msg.as_string()
                server.sendmail(self.email_user, to_email, text)
                server.quit()
                return True, "Welcome email sent successfully"
            else:
                # For development/testing
                print(f"📧 Welcome Email (Development Mode)")
                print(f"To: {to_email}")
                print(f"User: {user_name}")
                print("-" * 40)
                return True, "Welcome email sent (development mode)"
                
        except Exception as e:
            print(f"❌ Failed to send welcome email: {str(e)}")
            return False, f"Failed to send welcome email: {str(e)}"

# Global email service instance
email_service = EmailService()
