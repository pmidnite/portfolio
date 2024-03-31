from flask_mail import Mail

mail = Mail()

def mail_config(app):
    mail.init_app(app)
    return mail