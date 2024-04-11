from app.utilities.database import db


class Certification(db.Model):
    '''
    Certification DB structure Model
    cert_name: Title for the certification(Mandatory)
    cert_logo: Certification image name from the static image certs directory(Mandatory)
    cert_url: Certification public url(Non-Mandatory)
    cert_type: Certification type[Programing Language, Networking, Cybersecurity](Mandatory)
    '''
    __tablename__ = "certification"

    id = db.Column(db.Integer, primary_key=True)
    cert_name = db.Column(db.String(250), unique=True, nullable=False)
    cert_logo = db.Column(db.String(450), nullable=False)
    cert_url = db.Column(db.String(450), nullable=True)
    cert_type = db.Column(db.String(100), nullable=False)
