# model about.py
from app import mongo

class About:
    '''
    Sample Payload
    --------------
    {
        "Email": "nsarfaraz@email.com",
        "Current Designation": "Developer",
        "Long Description": "I am Full Stack Developer.",
        "Phone": "9876543210",
        "Profile Image Link": "https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/postman/postman-original.svg",
        "Short Description": "I am a Developer",
        "Website Link": "http://google.com"
    }
    '''

    @staticmethod
    def insert_or_update(payload):
        mongo.db.about.update_one({'Email': payload['Email']}, {'$set': payload}, upsert=True)

    @staticmethod
    def fetch_about():
        return list(mongo.db.about.find())
    
    @staticmethod
    def fetch_exact_about(email):
        return list(mongo.db.about.find({'Email': email}))
    
    @staticmethod
    def delete_about(del_email):
        mongo.db.about.delete_one({'Email': del_email['Email']})
