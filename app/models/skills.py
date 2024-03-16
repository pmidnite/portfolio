# Model for Skills
from app import mongo

class Skills:
    '''
    Sample Payload
    --------------
    {
        "Skill Name": "Python",
        "Skill Logo": "https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/python/python-original-wordmark.svg"
    }
    '''

    @staticmethod
    def fetch_skills():
        return list(mongo.db.skills.find())
    
    @staticmethod
    def fetch_exact_skill(name):
        return list(mongo.db.skills.find({"Skill Name": name}))
    
    @staticmethod
    def insert_or_update_skill(payload):
        if len(payload) > 1:
            for load in payload:
                mongo.db.skills.update_one({"Skill Name": load["Skill Name"]}, {"$set": load}, upsert=True)
        else:
            mongo.db.skills.update_one({"Skill Name": payload["Skill Name"]}, {"$set": payload}, upsert=True)

    @staticmethod
    def delete_skill(payload):
        mongo.db.skills.delete_one({"Skill Name": payload["Skill Name"]})