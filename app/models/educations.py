# Model educations.py

from app import mongo

class Education:
    '''
    Sample Payload
    --------------
    {
        "Email": "nsarfaraz@email.com",
        "Start Year": "2012",
        "Address": "Asansol, West Bengal",
        "Degree": "Bachelor Of Technology",
        "Passing Year": "2016",
        "University": "West Bengal University Of Technology"
    }
    '''

    @staticmethod
    def fetch_education():
        return list(mongo.db.educations.find())
    
    @staticmethod
    def fetch_exact_education(email, year=None):
        if year:
            return list(mongo.db.educations.find({'Email': email, 'Start Year': year}))
        else:
            return list(mongo.db.educations.find({'Email': email}))
    
    @staticmethod
    def insert_or_update_education(payload):
        mongo.db.educations.update_one({'Email': payload['Email'], 'Start Year': payload['Start Year']},
                                       {'$set': payload}, upsert=True)

    @staticmethod
    def delete_education(payload):
        mongo.db.educations.delete_one({'Email': payload['Email']})