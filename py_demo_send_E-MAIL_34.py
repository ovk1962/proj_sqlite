#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  py_demo_send_E-MAIL_34
#
# import necessary packages
# https://www.google.com/settings/security/lesssecureapps

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

# create message object instance
msg = MIMEMultipart()

message = "Thank you"

# setup the parameters of the message
password    = '20066002' #"your_password"
msg['From'] = 'mobile.ovk@gmail.com' #"your_address"
msg['To']   = 'mobile.ovk@gmail.com' #"to_address"
msg['Subject'] = "Subscription"

# add in the message body
msg.attach(MIMEText(message, 'plain'))

try:
    #create server
    server = smtplib.SMTP('smtp.gmail.com: 587')# 587
    server.ehlo()
    server.starttls()

    # Login Credentials for sending the mail
    server.login(msg['From'], password)

    # send the message via the server.
    server.sendmail(msg['From'], msg['To'], msg.as_string())

    server.quit()

    print("Successfully sent email to %s:" % (msg['To']))

except Exception as ex:
    print('Something went wrong...\n', ex)

