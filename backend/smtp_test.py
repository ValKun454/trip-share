import smtplib
from email.mime.text import MIMEText

smtp_server = "email-smtp.eu-north-1.amazonaws.com"
smtp_port = 587
smtp_username = "AKIARVLSN67PDGFYPXOO"
smtp_password = "BBS89rHQ0HTIzul3MTTJJRnlgRDoMF1Pt7qlZwmNaZza"

msg = MIMEText("Marisa")
msg['Subject'] = "Test Email"
msg['From'] = "@gmail.com"
msg['To'] = "@gmail.com"

with smtplib.SMTP(smtp_server, smtp_port) as server:
    server.starttls()
    server.login(smtp_username, smtp_password)
    server.send_message(msg)
