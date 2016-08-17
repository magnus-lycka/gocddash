#!/usr/bin/env python3

import re
from email.mime.text import MIMEText

from gocddash.console_parsers.git_blame_compare import get_git_comparison
from gocddash.util.app_config import get_app_config, create_app_config
from .domain import get_pipeline_head, get_latest_failure_streak, create_email_notification_sent
from .data_access import get_connection

import smtplib


def send_prime_suspect_email(latest_pipeline, start_of_failing_streak, suspect_list):
    create_app_config()
    sender_user = get_app_config().cfg['SMTP_USER']
    print("Setting up server")
    server = smtplib.SMTP(get_app_config().cfg['SMTP_SERVER'])
    print("Done setting up server\n")

    title = "{} broke in GO at pipeline counter {}, and is currently at counter {}. If you pushed to this recently, please investigate.".format(latest_pipeline.pipeline_name, start_of_failing_streak.start_counter, latest_pipeline.pipeline_counter)

    base_go_url = get_app_config().cfg['PUBLIC_GO_SERVER_URL']
    base_dashboard_link = get_app_config().cfg['PUBLIC_DASH_URL']
    insights_link = "{}insights/{}".format(base_dashboard_link, latest_pipeline.pipeline_name)
    go_overview_link = "{}tab/pipeline/history/{}".format(base_go_url, latest_pipeline.pipeline_name)

    msg_content = "<p>{}</p>" \
                  "<p>Link to insights: {}</p>" \
                  "<p>Link to GO Overview: {}</p>".format(title, insights_link, go_overview_link)
    message = MIMEText(msg_content, 'html')

    recipients = get_suspects(suspect_list)
    # recipients = [';placeholder@pagero.com', 'placeholder@pagero.com']
    print("\n Sent email to: {}".format(recipients))
    message['From'] = 'Go.CD Dashboard <{}>'.format(sender_user)
    message['To'] = ', '.join(recipients)
    message['Subject'] = '{} broken in GO'.format(latest_pipeline.pipeline_name)

    msg_full = message.as_string()

    server.sendmail(sender_user, recipients, msg_full)
    print("\n -----MESSAGE FULL-----")
    print(msg_full)
    server.quit()


def get_suspects(perpetrator_data):
    suspect_emails = {re.search('<(.*)>', row[3]).group(1) for row in perpetrator_data}  # Extract the email address from perpetrator_data into a set
    return suspect_emails

def build_email_notifications(pipeline_name):
    latest_pipeline = get_pipeline_head(pipeline_name)
    if not latest_pipeline.is_success() and not get_connection().email_notification_sent_for_current_streak(pipeline_name):
        print("\n -----SENDING EMAILS FOR {}-----".format(pipeline_name))
        start_of_red_streak = get_latest_failure_streak(pipeline_name)
        perpetrator_data = get_git_comparison(pipeline_name, start_of_red_streak.start_counter,
                                              start_of_red_streak.start_counter - 1, "")
        try:
            send_prime_suspect_email(latest_pipeline, start_of_red_streak, perpetrator_data)
            create_email_notification_sent(pipeline_name, start_of_red_streak.start_counter)
        except Exception:
            print("Could not send email for pipeline " + pipeline_name)