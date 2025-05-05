# test_email.py
import os
import smtplib
import email
from email import mime
from email.mime import text
from email.mime import multipart
MIMEText = text.MIMEText
MIMEMultipart = multipart.MIMEMultipart
from dotenv import load_dotenv
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def test_email_connection():
    """Test email connection with detailed logging"""
    sender_email = os.getenv('GMAIL_USER')
    password = os.getenv('GMAIL_APP_PASSWORD')
    smtp_server = os.getenv('GMAIL_SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.getenv('GMAIL_SMTP_PORT', 587))
    
    # Print configuration
    logger.info(f"Email Configuration:")
    logger.info(f"  SMTP Server: {smtp_server}")
    logger.info(f"  SMTP Port: {smtp_port}")
    logger.info(f"  Sender Email: {sender_email}")
    logger.info(f"  App Password: {'Set' if password else 'Not Set'}")
    
    # Check if we have all necessary credentials
    if not all([sender_email, password, smtp_server, smtp_port]):
        logger.error("Missing email configuration. Please set all required environment variables.")
        return False
    
    try:
        # Create a test email
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'Test Email From Astroved App'
        msg['From'] = sender_email
        recipient = input("Enter recipient email address: ")
        msg['To'] = recipient
        
        # Create email content
        text = "This is a test email from the Astroved app to verify email functionality."
        html = """
        <html>
        <body>
            <h2>Email Test from Astroved</h2>
            <p>This is a test email from the Astroved app to verify email functionality.</p>
            <p>If you can see this, the email service is working correctly!</p>
        </body>
        </html>
        """
        
        # Attach parts
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')
        msg.attach(part1)
        msg.attach(part2)
        
        # Connect to server
        logger.info(f"Connecting to SMTP server {smtp_server}:{smtp_port}...")
        
        if smtp_port == 465:
            # SSL connection
            server = smtplib.SMTP_SSL(smtp_server, smtp_port)
            logger.info("Using SSL connection")
        else:
            # Start TLS connection
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.ehlo()
            server.starttls()
            server.ehlo()
            logger.info("Using TLS connection")
        
        # Login
        logger.info("Attempting to log in...")
        server.login(sender_email, password)
        logger.info("Login successful")
        
        # Send email
        logger.info(f"Sending test email to {recipient}...")
        server.sendmail(sender_email, recipient, msg.as_string())
        logger.info("Email sent successfully!")
        
        # Close connection
        server.quit()
        logger.info("SMTP connection closed")
        
        return True
        
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        return False

if __name__ == "__main__":
    print("Email Test Script")
    print("=================")
    result = test_email_connection()
    if result:
        print("\nEmail test completed successfully!")
    else:
        print("\nEmail test failed. Check the logs for details.")