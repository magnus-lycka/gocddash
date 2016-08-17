#!/usr/bin/env python3

import re
from email.mime.text import MIMEText

from gocddash.util.app_config import get_app_config, create_app_config
import smtplib

def send_prime_suspect_email(pipeline, suspect_list):
    create_app_config()
    sender_user = get_app_config().cfg['SMTP_USER']
    print("Setting up server")
    # server = smtplib.SMTP(get_app_config().cfg['SMTP_SERVER'])
    print("Done setting up server\n")

    title = "{} is broken in GO. If you pushed to this recently, please investigate.".format(pipeline.pipeline_name)

    base_go_url = get_app_config().cfg['PUBLIC_GO_SERVER_URL']
    base_dashboard_link = get_app_config().cfg['PUBLIC_DASH_URL']
    insights_link = "{}insights/{}".format(base_dashboard_link, pipeline.pipeline_name)
    go_overview_link = "{}tab/pipeline/history/{}".format(base_go_url, pipeline.pipeline_name)

    msg_content = "<h2>{}<h2>\n" \
                  "Link to insights: {} \n" \
                  "Link to GO.CD Overview: {} \n" \
                  "Link to GO.CD Test Summary: {} \n".format(title, insights_link, go_overview_link, "placeholder")
    message = MIMEText(msg_content, 'html')

    suspect_list = get_suspects(suspect_list)
    recipients = [*suspect_list]
    # recipients = [';placeholder@pagero.com', 'placeholder@pagero.com']  # For test purposes
    print(recipients)
    message['From'] = 'Pagero Dashboard'
    message['To'] = ', '.join(recipients)
    message['Subject'] = '{} broken in GO'.format(pipeline.pipeline_name)

    msg_full = message.as_string()

    # Add link to insights page in Email

    # server.sendmail(sender_user, recipients, msg_full)
    print("\n -----MESSAGE FULL-----")
    print(msg_full)
    # server.quit()


def get_suspects(perpetrator_data):
    suspect_emails = {re.search('<(.*)>', row[3]).group(1) for row in perpetrator_data}  # Extract the email address from perpetrator_data into a set
    return suspect_emails

