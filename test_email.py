import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

# Get SMTP settings from .env file
SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")
EMAIL_FROM = os.getenv("EMAIL_FROM", "")
EMAIL_TO = [e.strip() for e in os.getenv("EMAIL_TO","").split(",") if e.strip()]

print("SMTP Configuration:")
print(f"Host: {SMTP_HOST}")
print(f"Port: {SMTP_PORT}")
print(f"User: {SMTP_USER}")
print(f"Password: {'*' * len(SMTP_PASS) if SMTP_PASS else 'Not set'}")
print(f"From: {EMAIL_FROM}")
print(f"To: {EMAIL_TO}")

if not (SMTP_HOST and SMTP_PORT and SMTP_USER and SMTP_PASS and EMAIL_FROM and EMAIL_TO):
    print("\n[ERROR] SMTP not fully configured in .env file")
    exit(1)

try:
    print("\nConnecting to SMTP server...")
    server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
    server.set_debuglevel(1)  # Enable debug output
    
    print("Starting TLS...")
    server.starttls()
    
    print("Logging in...")
    server.login(SMTP_USER, SMTP_PASS)
    
    # Create test email
    print("Creating test email...")
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Test Email - Bangalore Job Bot"
    msg["From"] = EMAIL_FROM
    msg["To"] = ", ".join(EMAIL_TO)
    
    html_body = """
    <div style='font-family:system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif;'>
      <h2>Test Email from Bangalore Data Analyst Job Bot</h2>
      <p>This is a test email to verify that the SMTP configuration is working correctly.</p>
      <p>If you received this email, your email configuration is working!</p>
    </div>
    """
    
    msg.attach(MIMEText(html_body, "html"))
    
    # Send email
    print("Sending email...")
    server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
    print("Email sent successfully!")
    
    # Close connection
    server.quit()
    print("SMTP connection closed.")
    
except Exception as e:
    print(f"\n[ERROR] Failed to send email: {e}")