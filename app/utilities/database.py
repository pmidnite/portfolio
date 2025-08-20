from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from app.utilities.logger import get_logger

logger = get_logger()

class Base(DeclarativeBase):
  pass

db = SQLAlchemy(model_class=Base)

def create_database(app):
    try:
        db.init_app(app)
        logger.info("Database initialization started")

        with app.app_context():
            db.create_all()

        logger.info("Database tables created successfully")

    except Exception as e:
        logger.error({"error": str(e), "error_type": type(e).__name__})
        raise
