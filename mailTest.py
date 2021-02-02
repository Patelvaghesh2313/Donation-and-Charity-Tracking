from flask import Flask
import os
from flask_mail import Mail, Message
import smtplib
from email.message import EmailMessage

EMAIL_ADDRESS = 'kingpatel8122@gmail.com'
EMAIL_PASSWORD = '347676747926vir'

msg = EmailMessage()
msg['Subject'] = "New Mail"
msg['From'] = EMAIL_ADDRESS
msg['To'] = EMAIL_ADDRESS
msg.set_content('How Are You ??')


with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
    smtp.starttls()
    smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)

    smtp.send_message(msg)