from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.exc import OperationalError
from app.utilities.logger import get_logger

logger = get_logger()


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


def create_database(app):
    db.init_app(app)
    logger.info("Database initialization started")

    with app.app_context():
        try:
            db.create_all()
            logger.info("Database tables created successfully")
        except OperationalError as e:
            # DB may not be available at startup time (e.g., during flask db init/migrate)
            # This is non-fatal — Flask-Migrate manages schema separately
            logger.warning(
                f"Could not connect to database at startup (tables not created): {str(e)}. "
                "Ensure the database is running before serving requests."
            )
        except Exception as e:
            logger.error({"error": str(e), "error_type": type(e).__name__})
            raise
