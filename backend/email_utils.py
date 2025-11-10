import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from jose import jwt
import os
from dotenv import load_dotenv

load_dotenv()

# SMTP Configuration from .env
SMTP_SERVER = os.getenv("SMPT_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USERNAME = os.getenv("SMPT_USER_NAME")
SMTP_PASSWORD = os.getenv("SMPT_PASSWORD")
SENDER_EMAIL = "12qwarew2qs@gmail.com"  # Update this with your verified SES email

# Token settings
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
VERIFICATION_TOKEN_EXPIRE_HOURS = 24


def create_verification_token(email: str) -> str:
    """Create a verification token that expires in 24 hours"""
    expire = datetime.utcnow() + timedelta(hours=VERIFICATION_TOKEN_EXPIRE_HOURS)
    to_encode = {"sub": email, "exp": expire, "type": "email_verification"}
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token


def verify_verification_token(token: str) -> str | None:
    """
    Verify the token and return the email if valid
    Returns None if token is invalid or expired
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        token_type: str = payload.get("type")

        if email is None or token_type != "email_verification":
            return None
        return email
    except jwt.JWTError:
        return None


def send_verification_email(email: str, username: str, verification_token: str):
    """Send verification email with activation link"""

    # Construct the verification URL
    # Update this with your actual frontend/backend URL
    verification_url = f"http://localhost:8000/api/verify?token={verification_token}"

    # Create email message
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Verify your email address"
    msg['From'] = SENDER_EMAIL
    msg['To'] = email

    # Plain text version
    text = f"""
    Hey {username}!

    Thanks for signing up! Please verify your email address by clicking the link below:

    {verification_url}

    This link will expire in 24 hours.

    If you didn't sign up for this account, just ignore this email.
    """

    # HTML version (prettier)
    html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
          <h2 style="color: #4CAF50;">Welcome, {username}!</h2>
          <p>Thanks for signing up! Please verify your email address by clicking the button below:</p>

          <div style="text-align: center; margin: 30px 0;">
            <a href="{verification_url}"
               style="background-color: #4CAF50;
                      color: white;
                      padding: 12px 30px;
                      text-decoration: none;
                      border-radius: 5px;
                      display: inline-block;">
              Verify Email
            </a>
          </div>

          <p style="color: #666; font-size: 14px;">
            Or copy and paste this link into your browser:<br>
            <a href="{verification_url}">{verification_url}</a>
          </p>

          <p style="color: #666; font-size: 12px; margin-top: 30px;">
            This link will expire in 24 hours.<br>
            If you didn't sign up for this account, just ignore this email.
          </p>
        </div>
      </body>
    </html>
    """

    # Attach both versions
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')
    msg.attach(part1)
    msg.attach(part2)

    # Send email
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False
