import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "myworkproject215@gmail.com"
SMTP_PASSWORD = "zzrrinoxsbaisptn"
TO = "myworkproject215@gmail.com"

msg = MIMEMultipart("alternative")
msg["Subject"] = "Test Email from LeadAggregator"
msg["From"] = SMTP_USER
msg["To"] = TO
msg.attach(MIMEText("<h1>It works</h1>", "html"))

try:
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.ehlo()
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SMTP_USER, TO, msg.as_string())
        print("Email sent successfully")
except Exception as e:
    print(f"Failed: {e}")