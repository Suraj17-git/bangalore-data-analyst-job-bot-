import os
import sys
from dotenv import load_dotenv
from utils.emailer import send_email

# Load environment variables
load_dotenv()

# Check environment variables
SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = os.getenv("SMTP_PORT", "")
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")
EMAIL_FROM = os.getenv("EMAIL_FROM", "")
EMAIL_TO = os.getenv("EMAIL_TO", "")

print("Environment variables:")
print(f"SMTP_HOST: {SMTP_HOST}")
print(f"SMTP_PORT: {SMTP_PORT}")
print(f"SMTP_USER: {SMTP_USER}")
print(f"SMTP_PASS: {'*' * len(SMTP_PASS) if SMTP_PASS else 'Not set'}")
print(f"EMAIL_FROM: {EMAIL_FROM}")
print(f"EMAIL_TO: {EMAIL_TO}")

# Test sending email using the same function as job_search.py
print("\nAttempting to send test email using utils.emailer.send_email...")
try:
    subject = "Test Email from Bangalore Job Bot"
    html_body = """
    <div style='font-family:system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif;'>
      <h2>Test Email from Bangalore Data Analyst Job Bot</h2>
      <p>This is a test email to verify that the email sending functionality is working correctly.</p>
      <p>If you received this email, your email configuration is working!</p>
    </div>
    """
    
    send_email(subject, html_body)
    print("Email function completed without errors.")
except Exception as e:
    print(f"Error sending email: {e}")