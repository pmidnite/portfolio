from flask_mail import Mail, Message
from threading import Thread
from app.utilities.logger import get_logger

logger = get_logger(__name__)
mail = Mail()

def mail_config(app):
    mail.init_app(app)
    return mail

def send_async_email_thread(app, msg):
    with app.app_context():
        try:
            mail.send(msg)
            logger.info(f"Email '{msg.subject}' sent successfully in background.")
        except Exception as e:
            logger.error(f"Failed to send email '{msg.subject}' in background: {str(e)}")

def send_email_async(app, msg):
    thread = Thread(target=send_async_email_thread, args=(app, msg))
    thread.start()
    return thread