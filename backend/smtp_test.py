import smtplib
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

load_dotenv()

smtp_server = os.getenv("SMTP_SERVER")
smtp_port = int(os.getenv("SMTP_PORT"))
smtp_username = os.getenv("SMTP_USER_NAME")
smtp_password = os.getenv("SMTP_PASSWORD")

msg = MIMEText("Marisa")
msg['Subject'] = "Test Email"
msg['From'] = "noreply.tripnshare@gmail.com"
msg['To'] = "rekrut.fedosenko@gmail.com"

try:
    with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
        print("Connected to SMTP server")
        server.login(smtp_username, smtp_password)
        print("Login successful")
        server.send_message(msg)
        print("Email sent successfully!")
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")


