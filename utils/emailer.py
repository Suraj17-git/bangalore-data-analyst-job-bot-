
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

# Load environment variables at module level to ensure they're available
load_dotenv()

def send_email(subject, html_body):
    # Get SMTP settings from environment variables at runtime
    SMTP_HOST = os.getenv("SMTP_HOST", "")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER = os.getenv("SMTP_USER", "")
    # Remove any spaces from the password as Gmail app passwords sometimes have spaces in the display format
    # but should be used without spaces
    SMTP_PASS = os.getenv("SMTP_PASS", "").replace(" ", "")
    EMAIL_FROM = os.getenv("EMAIL_FROM", "")
    EMAIL_TO = [e.strip() for e in os.getenv("EMAIL_TO","").split(",") if e.strip()]
    
    if not (SMTP_HOST and SMTP_PORT and SMTP_USER and SMTP_PASS and EMAIL_FROM and EMAIL_TO):
        print("[warn] SMTP not configured — skipping email. To send emails, fill .env and provide SMTP credentials.")
        print(subject)
        return
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = EMAIL_FROM
    msg["To"] = ", ".join(EMAIL_TO)
    msg.attach(MIMEText(html_body, "html"))
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
        print(f"[info] Email sent successfully to {', '.join(EMAIL_TO)}")
