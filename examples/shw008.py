import arrow

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import logging

from  argos import argosClient

logging.basicConfig(level=logging.WARNING)
logger = argosClient.logger
logger.setLevel(logging.DEBUG)

# Glider Echo
api = argosClient.ArgosPlatformInfo(credentials="argos_login.txt")
info = api.retrieve(platformId='286360', number_of_days_from_now=3)


age = (arrow.get() - arrow.get(info["bestMsgDate"])).total_seconds()/86400



# --- Configuration ---
SMTP_SERVER = "smtp.hereon.de"
SMTP_PORT = 587
SENDER_EMAIL = "gliderman@hereon.de"
SENDER_PASSWORD = "your_app_password"   # use an app password, not your login password

RECEIVER_EMAIL = "lucas.merckelbach@hereon.de"
SUBJECT = "Argos message received for SHW008"
BODY = "It seems there is an argos message received for glider SHW008."


def send_email():
    # Build the email
    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECEIVER_EMAIL
    msg["Subject"] = SUBJECT
    msg.attach(MIMEText(BODY, "plain"))

    # Connect and send
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()  # encrypt the connection
            server.ehlo()
            #server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")



if age < 1:
    send_email()
