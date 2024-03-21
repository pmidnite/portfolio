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


class MappedSkills:
    '''
    Mapped Skill Payload
    --------------------
    {
        "Email": "nsarfaraz@email.com",
        "Skill Names": "Python, Angularjs"
    }
    '''

    @staticmethod
    def insert_or_update_mapped_skill(payload):
        mongo.db.skills_map.update_one({"Email": payload["Email"]},
            {"$set": payload},
            upsert=True)

    @staticmethod
    def fetch_exact_mapped_skill(email):
        return list(mongo.db.skills_map.find({"Email": email}))

    @staticmethod
    def fetch_mapped_skill():
        return list(mongo.db.skills_map.find())

    @staticmethod
    def delete_mapped_skill(email):
        mongo.db.skills_map.delete_one({"Email": email})
