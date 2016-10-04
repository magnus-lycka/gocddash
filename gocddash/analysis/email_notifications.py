"""This module is used for sending email alerts to addresses in the "Prime Suspects" list on the dashboard.
If an address appears in the prime suspect list and has not received an email, an email alert will be sent.

"""

import re
from email.mime.text import MIMEText

from gocddash.console_parsers.git_history_comparison import get_git_comparison
from gocddash.util.app_config import get_app_config, create_app_config
from .domain import get_pipeline_head, get_latest_failure_streak, create_email_notification_sent
from .data_access import get_connection

import smtplib


def send_prime_suspect_email(latest_pipeline, streak, suspect_list):
    create_app_config()
    sender_user = get_app_config().cfg['SMTP_USER']
    print("Setting up server")
    server = smtplib.SMTP(get_app_config().cfg['SMTP_SERVER'])
    print("Done setting up server\n")

    msg_body = (
        "{} broke in GO at pipeline counter {}, and is currently at counter {}. "
        "If you pushed to this or any upstream recently, please investigate."
        .format(latest_pipeline.pipeline_name, streak.pass_counter+1, latest_pipeline.pipeline_counter)
    )

    base_go_url = get_app_config().cfg['PUBLIC_GO_SERVER_URL']
    base_dashboard_link = get_app_config().cfg['PUBLIC_DASH_URL']
    insights_link = "{}insights/{}".format(base_dashboard_link, latest_pipeline.pipeline_name)
    go_overview_link = "{}tab/pipeline/history/{}".format(base_go_url, latest_pipeline.pipeline_name)

    msg_content = "<p>{}</p>" \
                  "<p>Link to insights: {}</p>" \
                  "<p>Link to GO Overview: {}</p>".format(msg_body, insights_link, go_overview_link)
    message = MIMEText(msg_content, 'html')

    recipients = get_suspects(suspect_list)

    message['From'] = 'Go.CD Dashboard <{}>'.format(sender_user)
    message['To'] = ', '.join(recipients)
    message['Subject'] = '{} broken in GO'.format(latest_pipeline.pipeline_name)

    msg_full = message.as_string()

    print("\n Sending email to: {}".format(recipients))
    server.sendmail(sender_user, recipients, msg_full)
    print("\n Email sent!")
    print("\n -----MESSAGE FULL-----")
    print(msg_full)
    server.quit()


def get_suspects(perpetrator_data):
    all_rows = []
    for _, rows in perpetrator_data:
        all_rows.extend(rows)
    suspect_emails = {re.search('<(.*)>', row[1]).group(1) for row in all_rows}
    return suspect_emails


def build_email_notifications(pipeline_name):
    latest_pipeline = get_pipeline_head(pipeline_name)
    if not latest_pipeline.is_success() and not get_connection().email_notification_sent_for_current_streak(
            pipeline_name):
        print("\n -----SENDING EMAILS FOR {}-----".format(pipeline_name))
        streak = get_latest_failure_streak(pipeline_name)
        perpetrator_data = get_git_comparison(pipeline_name, streak.pass_counter + 1,
                                              streak.pass_counter, "")
        try:
            send_prime_suspect_email(latest_pipeline, streak, perpetrator_data)
            create_email_notification_sent(pipeline_name, streak.pass_counter + 1)
        except Exception as error:
            # TODO: Narrow down to expected exception classes. We don't want to hide bugs e.g. NameError.
            print("Could not send email for pipeline " + pipeline_name)
            print(error)
