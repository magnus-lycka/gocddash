#!/usr/bin/env python3

import re
import smtplib
from email.mime.text import MIMEText

from gocddash.util.app_config import get_app_config, create_app_config


def send_prime_suspect_email(pipeline, suspect_list):
    create_app_config()
    sender_user = get_app_config().cfg['SMTP_USER']  # sender@server.com
    sender_passwd = get_app_config().cfg['SMTP_PASSWD']  # 'senderPassword'
    print("Setting up server")
    server = smtplib.SMTP(get_app_config().cfg['SMTP_SERVER'])
    print("Done setting up server\n")

    print("Before title")
    title = "{} is broken in GO. If you pushed to this recently, please investigate.".format(pipeline)  #TODO: Change to .name when done testing
    msg_content = "<h2>{title} > <font color='red'>OK</font></h2>\n".format(title=title)
    message = MIMEText(msg_content, 'html')

    message['From'] = 'Hej <sender@server>'
    message['To'] = 'Receiver Name <receiver@server>'
    print(*suspect_list)
    message['To'] = "Hej <sender@server>"
    message['Subject'] = 'Any subject'

    msg_full = message.as_string()

    # Add link to insights page in Email

    print("Before tls")
    # server.starttls()
    print("Before login")
    server.login(sender_user, sender_passwd)
    print("Passed login")
    server.sendmail(sender_user, ['receiver@server'], msg_full)
    server.quit()


def send_emails_to_perpetrators(perpetrator_data):
    suspect_emails = {re.search('<(.*)>', row[3]).group(1) for row in perpetrator_data}  # Extract the email address from perpetrator_data into a set
    # print(suspect_emails)

if __name__ == '__main__':
    send_prime_suspect_email("Test", ['suspect_1', 'suspect_2', 'yoltocola-suspect'])
