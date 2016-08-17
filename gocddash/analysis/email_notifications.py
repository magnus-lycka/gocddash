#!/usr/bin/env python3

import re
import smtplib
from email.mime.text import MIMEText

from gocddash.util.app_config import get_app_config, create_app_config


def send_prime_suspect_email(pipeline, suspect_list):
    create_app_config()
    sender_user = get_app_config().cfg['SMTP_USER']
    print("Setting up server")
    server = smtplib.SMTP(get_app_config().cfg['SMTP_SERVER'])
    print("Done setting up server\n")

    title = "{} is broken in GO. If you pushed to this recently, please investigate.".format(pipeline.pipeline_name)

    base_go_url = get_app_config().cfg['GO_SERVER_URL']
    base_dashboard_link = get_app_config().cfg['PUBLIC_DASH_URL']
    insights_link = "{}insights/{}".format(base_dashboard_link, pipeline.name)
    go_overview_link = "{}tab/pipeline/history/{}".format(base_go_url, pipeline.name)

    msg_content = "<h2>{} ></h2>\n" \
                  "Link to insights: {} \n" \
                  "Link to GO.CD Overview: {} \n" \
                  "Link to GO.CD Test Summary: {} \n".format(title, insights_link, go_overview_link, "placeholder")
    message = MIMEText(msg_content, 'html')

    message['From'] = 'Hej <sender@server>'
    message['To'] = 'Receiver Name <receiver@server>'
    print(*suspect_list)
    message['To'] = "Hej <sender@server>"
    message['Subject'] = 'Any subject'

    msg_full = message.as_string()

    # Add link to insights page in Email

    # server.sendmail(sender_user, ['receiver@server'], msg_full)
    print("\n -----MESSAGE FULL-----")
    print(msg_full)
    server.quit()


def send_emails_to_perpetrators(perpetrator_data):
    suspect_emails = {re.search('<(.*)>', row[3]).group(1) for row in perpetrator_data}  # Extract the email address from perpetrator_data into a set
    # print(suspect_emails)

if __name__ == '__main__':
    send_prime_suspect_email("Test", ['suspect_1', 'suspect_2', 'yoltocola-suspect'])
