# services/email_service.py
import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Template

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.sender_email = os.getenv('GMAIL_USER')
        self.sender_password = os.getenv('GMAIL_APP_PASSWORD')
        self.smtp_server = os.getenv('GMAIL_SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('GMAIL_SMTP_PORT', 587))
        
        # Log initialization
        if self.sender_email and self.sender_password:
            logger.info(f"Email service initialized with {self.sender_email} on {self.smtp_server}:{self.smtp_port}")
        else:
            logger.warning("Email service initialized without credentials - will operate in development mode")
        
    def send_verification_email(self, to_email, user_name, verification_url):
        """
        Send verification email to user who just registered
        
        Args:
            to_email (str): Recipient's email address
            user_name (str): Recipient's name
            verification_url (str): URL for email verification
            
        Returns:
            bool: True if the email was sent successfully, False otherwise
        """
        logger.info(f"Preparing verification email for {to_email}")
        
        # Check if email credentials are configured
        if not self.sender_email or not self.sender_password:
            logger.warning("Email configuration missing. Verification email not sent.")
            # For development, print the verification URL to console
            logger.info(f"DEVELOPMENT MODE: Verification URL for {to_email}: {verification_url}")
            return True
            
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = 'Verify Your Email - Parasara Jyotish'
            msg['From'] = self.sender_email
            msg['To'] = to_email
            
            # Email template
            html_template = """
            <!DOCTYPE html>
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #6B46C1;">Welcome to Parasara Jyotish</h2>
                    <p>Hello {{ name }},</p>
                    <p>Thank you for signing up! Please verify your email address to complete your registration.</p>
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{{ verification_url }}" 
                           style="background-color: #6B46C1; color: white; padding: 12px 24px; 
                                  text-decoration: none; border-radius: 5px; display: inline-block;">
                            Verify Email Address
                        </a>
                    </div>
                    <p>Or copy and paste this link in your browser:</p>
                    <p style="word-break: break-all;">{{ verification_url }}</p>
                    <p>This verification link will expire in 24 hours.</p>
                    <p>If you didn't create an account, please ignore this email.</p>
                    <hr style="border: 1px solid #eee; margin: 20px 0;">
                    <p style="color: #666; font-size: 12px;">
                        This is an automated message, please do not reply.
                    </p>
                </div>
            </body>
            </html>
            """
            
            # Render template
            template = Template(html_template)
            html_content = template.render(
                name=user_name,
                verification_url=verification_url
            )
            
            # Also create a plain text version
            text_content = f"""
            Hello {user_name},
            
            Thank you for signing up! Please verify your email address to complete your registration.
            
            You can verify your email by clicking the link below or copy-paste it into your browser:
            {verification_url}
            
            This verification link will expire in 24 hours.
            
            If you didn't create an account, please ignore this email.
            """
            
            # Attach text and HTML versions
            part1 = MIMEText(text_content, 'plain')
            part2 = MIMEText(html_content, 'html')
            msg.attach(part1)
            msg.attach(part2)
            
            # Create SMTP connection and send email
            if self.smtp_port == 465:
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            else:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                server.ehlo()
                server.starttls()
                server.ehlo()
            
            server.login(self.sender_email, self.sender_password)
            server.sendmail(
                self.sender_email,
                to_email,
                msg.as_string()
            )
            server.quit()
            
            logger.info(f"Email successfully sent to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email to {to_email}: {str(e)}")
            # Still print the verification URL to console for testing
            logger.info(f"DEVELOPMENT MODE: Verification URL for {to_email}: {verification_url}")
            return False
            
    def send_password_reset_email(self, to_email, user_name, reset_url):
        """Send password reset email"""
        # Log the request
        logger.info(f"Password reset requested for {to_email}")
        
        # Similar implementation as verification email
        # For now, just log the URL in development mode
        if not self.sender_email or not self.sender_password:
            logger.warning("Email configuration missing. Password reset email not sent.")
            logger.info(f"DEVELOPMENT MODE: Password reset URL for {to_email}: {reset_url}")
            return True
            
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = 'Reset Your Password - Parasara Jyotish'
            msg['From'] = self.sender_email
            msg['To'] = to_email
            
            # Email template
            html_template = """
            <!DOCTYPE html>
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #6B46C1;">Reset Your Password</h2>
                    <p>Hello {{ name }},</p>
                    <p>We received a request to reset your password.</p>
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{{ reset_url }}" 
                           style="background-color: #6B46C1; color: white; padding: 12px 24px; 
                                  text-decoration: none; border-radius: 5px; display: inline-block;">
                            Reset Password
                        </a>
                    </div>
                    <p>Or copy and paste this link in your browser:</p>
                    <p style="word-break: break-all;">{{ reset_url }}</p>
                    <p>This link will expire in 24 hours.</p>
                    <p>If you didn't request a password reset, please ignore this email.</p>
                    <hr style="border: 1px solid #eee; margin: 20px 0;">
                    <p style="color: #666; font-size: 12px;">
                        This is an automated message, please do not reply.
                    </p>
                </div>
            </body>
            </html>
            """
            
            # Render template
            template = Template(html_template)
            html_content = template.render(
                name=user_name,
                reset_url=reset_url
            )
            
            # Also create a plain text version
            text_content = f"""
            Hello {user_name},
            
            We received a request to reset your password.
            
            You can reset your password by clicking the link below or copy-paste it into your browser:
            {reset_url}
            
            This link will expire in 24 hours.
            
            If you didn't request a password reset, please ignore this email.
            """
            
            # Attach text and HTML versions
            part1 = MIMEText(text_content, 'plain')
            part2 = MIMEText(html_content, 'html')
            msg.attach(part1)
            msg.attach(part2)
            
            # Create SMTP connection and send email
            if self.smtp_port == 465:
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            else:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                server.ehlo()
                server.starttls()
                server.ehlo()
            
            server.login(self.sender_email, self.sender_password)
            server.sendmail(
                self.sender_email,
                to_email,
                msg.as_string()
            )
            server.quit()
            
            logger.info(f"Password reset email sent to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending password reset email: {str(e)}")
            # Still print the reset URL to console for testing
            logger.info(f"DEVELOPMENT MODE: Password reset URL for {to_email}: {reset_url}")
            return False
            
    def send_contact_notification(self, to_email, user_name, user_email, message):
        """Send notification when a new contact form is submitted"""
        logger.info(f"Sending contact form notification for {user_email}")
        
        if not self.sender_email or not self.sender_password:
            logger.warning("Email configuration missing. Contact notification not sent.")
            return True
            
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = 'New Contact Form Submission - Parasara Jyotish'
            msg['From'] = self.sender_email
            msg['To'] = to_email
            
            # Email template
            html_template = """
            <!DOCTYPE html>
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #6B46C1;">New Contact Form Submission</h2>
                    <p>You have received a new contact form submission:</p>
                    
                    <div style="background-color: #f9f9f9; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <p><strong>Name:</strong> {{ name }}</p>
                        <p><strong>Email:</strong> {{ email }}</p>
                        <p><strong>Message:</strong></p>
                        <p>{{ message }}</p>
                    </div>
                    
                    <p>Please respond to this inquiry at your earliest convenience.</p>
                    <hr style="border: 1px solid #eee; margin: 20px 0;">
                    <p style="color: #666; font-size: 12px;">
                        This is an automated message from your website.
                    </p>
                </div>
            </body>
            </html>
            """
            
            # Render template
            template = Template(html_template)
            html_content = template.render(
                name=user_name,
                email=user_email,
                message=message or "No message provided"
            )
            
            # Also create a plain text version
            text_content = f"""
            New Contact Form Submission
            
            Name: {user_name}
            Email: {user_email}
            
            Message:
            {message or "No message provided"}
            
            Please respond to this inquiry at your earliest convenience.
            """
            
            # Attach text and HTML versions
            part1 = MIMEText(text_content, 'plain')
            part2 = MIMEText(html_content, 'html')
            msg.attach(part1)
            msg.attach(part2)
            
            # Create SMTP connection and send email
            if self.smtp_port == 465:
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            else:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                server.ehlo()
                server.starttls()
                server.ehlo()
            
            server.login(self.sender_email, self.sender_password)
            server.sendmail(
                self.sender_email,
                to_email,
                msg.as_string()
            )
            server.quit()
            
            logger.info(f"Contact notification email sent to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending contact notification email: {str(e)}")
            return False
