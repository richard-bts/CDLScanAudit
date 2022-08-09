from scanaudit import mail 
from flask_mail import Message
from scanaudit.config import config

import os

config = config['development']
def send_error_email():
    file_name = 'error.log'
    subject = 'Scan Audit Error'
    msg = Message(
                    sender=str(config.MAIL_DEFAULT_SENDER),
                    subject=subject,
                    recipients = config.SUPPORT
                )
    msg.body = 'There was a server error when trying to perform the scan audit report. Please check app log to see error'
    if file_name in os.listdir():
        file = open(file_name, 'rb')
        msg.attach(file_name, 'text/plain', file.read())
    mail.send(msg)
    return 'Administrator has been contacted.'