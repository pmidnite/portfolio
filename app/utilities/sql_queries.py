from app.utilities.database import db

def map_class_to_dict(class_table):
    return {key.title().replace('_', ' '): value for key, value in class_table.__dict__.items() if not key.startswith('_')}
