from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
  pass

db = SQLAlchemy(model_class=Base)

def create_database(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()
    print(' * DB Exists!!!')