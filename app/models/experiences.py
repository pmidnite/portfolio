from app import mongo

class Experiences:
    '''
    Sample Payload
    -----------------
    {
        "Email": "nsarfaraz@email.com",
        "Company Name": "Zeomega Infotech Pvt Ltd",
        "Address": "Bengaluru, India",
        "Start Year": "2017",
        "End Year": "2018",
        "Designation": "Software Developer Trainee",
        "Description": "ETL WSO2 REST and SOAP API development and support using SOA architecture for client using tools like WSO2 ESB, RabbitMQ, IS Server and API Manager."
    }
    '''

    @staticmethod
    def fetch_experience():
        return list(mongo.db.experiences.find().sort("Start Year", -1))

    @staticmethod
    def fetch_exact_experience(email, year, sort_by_col="Start Year"):
        if year:
            return list(mongo.db.experiences.find({"Email": email, "Start Year": year}))
        else:
            return list(mongo.db.experiences.find({"Email": email}).sort(sort_by_col, -1))

    @staticmethod
    def insert_or_update_experience(payload):
        if len(payload) > 1:
            for load in payload:
                mongo.db.experiences.update_one({"Email": load['Email'], "Start Year": load["Start Year"]},
                                               {'$set': load},
                                               upsert=True)
        else:
            mongo.db.experiences.update_one({"Email": payload['Email'], "Start Year": payload["Start Year"]},
                                            {'$set': payload},
                                            upsert=True)

    @staticmethod
    def delete_experience(payload):
        mongo.db.experiences.delete_one({"Email": payload["Email"], "Start Year": payload["Start Year"]})
