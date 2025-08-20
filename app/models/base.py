from app.utilities.database import db
from sqlalchemy import inspect
from sqlalchemy.exc import SQLAlchemyError
from app.utilities.logger import get_logger

logger = get_logger()


class BaseModel(db.Model):
    """
    Base model class that provides common functionality for all models
    """
    __abstract__ = True

    def save(self):
        """
        Save the current instance to database.
        Returns True if successful, False otherwise.
        """
        try:
            db.session.add(self)
            db.session.commit()
            logger.info(f"Successfully saved {self.__class__.__name__} instance")
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Error saving {self.__class__.__name__}: {str(e)}")
            return False
        except Exception as e:
            db.session.rollback()
            logger.error(f"Unexpected error saving {self.__class__.__name__}: {str(e)}")
            return False

    def delete(self):
        """
        Delete the current instance from database.
        Returns True if successful, False otherwise.
        """
        try:
            db.session.delete(self)
            db.session.commit()
            logger.info(f"Successfully deleted {self.__class__.__name__} instance")
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Error deleting {self.__class__.__name__}: {str(e)}")
            return False
        except Exception as e:
            db.session.rollback()
            logger.error(f"Unexpected error deleting {self.__class__.__name__}: {str(e)}")
            return False

    def update(self, **kwargs):
        """
        Update the current instance with provided keyword arguments.
        Returns True if successful, False otherwise.
        """
        try:
            for key, value in kwargs.items():
                if hasattr(self, key):
                    setattr(self, key, value)
            db.session.commit()
            logger.info(f"Successfully updated {self.__class__.__name__} instance")
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Error updating {self.__class__.__name__}: {str(e)}")
            return False
        except Exception as e:
            db.session.rollback()
            logger.error(f"Unexpected error updating {self.__class__.__name__}: {str(e)}")
            return False

    def to_dict(self, exclude_fields=None):
        """
        Convert the current instance to a dictionary.

        Args:
            exclude_fields (list): List of field names to exclude from the dictionary

        Returns:
            dict: Dictionary representation of the instance
        """
        exclude_fields = exclude_fields or ['_sa_instance_state']

        result = {}
        for column in inspect(self.__class__).columns:
            column_name = column.name
            if column_name not in exclude_fields:
                value = getattr(self, column_name)
                # Handle datetime objects
                if hasattr(value, 'isoformat'):
                    value = value.isoformat()
                result[column_name] = value

        return result

    @classmethod
    def get_by_id(cls, record_id):
        """
        Get a record by its ID.

        Args:
            record_id: The ID of the record to retrieve

        Returns:
            Instance of the model or None if not found
        """
        try:
            return cls.query.get(record_id)
        except SQLAlchemyError as e:
            logger.error(f"Error getting {cls.__name__} by ID {record_id}: {str(e)}")
            return None

    @classmethod
    def get_all(cls, limit=None, offset=None):
        """
        Get all records with optional pagination.

        Args:
            limit (int): Maximum number of records to return
            offset (int): Number of records to skip

        Returns:
            List of model instances
        """
        try:
            query = cls.query
            if offset:
                query = query.offset(offset)
            if limit:
                query = query.limit(limit)
            return query.all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting all {cls.__name__} records: {str(e)}")
            return []

    @classmethod
    def get_all_dict(cls, limit=None, offset=None, exclude_fields=None):
        """
        Get all records as dictionaries with optional pagination.

        Args:
            limit (int): Maximum number of records to return
            offset (int): Number of records to skip
            exclude_fields (list): List of field names to exclude from dictionaries

        Returns:
            List of dictionaries representing model instances
        """
        records = cls.get_all(limit=limit, offset=offset)
        return [record.to_dict(exclude_fields=exclude_fields) for record in records]

    @classmethod
    def count(cls):
        """
        Get the total count of records in the table.

        Returns:
            int: Total number of records
        """
        try:
            return cls.query.count()
        except SQLAlchemyError as e:
            logger.error(f"Error counting {cls.__name__} records: {str(e)}")
            return 0

    @classmethod
    def exists(cls, **kwargs):
        """
        Check if a record exists with the given conditions.

        Args:
            **kwargs: Field names and values to filter by

        Returns:
            bool: True if record exists, False otherwise
        """
        try:
            return cls.query.filter_by(**kwargs).first() is not None
        except SQLAlchemyError as e:
            logger.error(f"Error checking if {cls.__name__} exists: {str(e)}")
            return False

    @classmethod
    def create(cls, **kwargs):
        """
        Create a new instance and save it to the database.

        Args:
            **kwargs: Field names and values for the new instance

        Returns:
            The created instance if successful, None otherwise
        """
        try:
            instance = cls(**kwargs)
            if instance.save():
                return instance
            return None
        except Exception as e:
            return None
