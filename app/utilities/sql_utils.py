from app.utilities.database import db

def map_class_to_dict(class_table):
    skip_fields = ["_sa_instance_state", "id", "email", "reviewed", "created_date", "updated_date"]
    return {key.title().replace('_', ' '): value for key, value in class_table.__dict__.items() if key not in skip_fields}

def map_class_to_dict_all(class_table):
    skip_fields = ["_sa_instance_state"]
    return {key.title().replace('_', ' '): value for key, value in class_table.__dict__.items() if key not in skip_fields}
