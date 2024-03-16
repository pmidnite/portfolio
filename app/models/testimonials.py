from app import mongo


class Testimonials:
    '''
    Sample Payload
    --------------
    {
        "Name": "Siddharth",
        "Designation": "Software Developer",
        "Company": "ABC Infotech Pvt Ltd",
        "Testimony": "He is a exceptional team player, available to guide and help at all time",
        "Reveiwed": "N"(Admin only)
    }
    '''
    
    @staticmethod
    def fetch_testimonial():
        return list(mongo.db.testimonials.find())
    
    @staticmethod
    def fetch_exact_testimonial(name, company):
        return list(mongo.db.testimonials.find({"Name": name, "Company": company}))
    
    @staticmethod
    def insert_or_update_testimonial(payload):
        mongo.db.testimonials.update_one({"Name": payload["Name"]},
                                         {"$set": payload},
                                         upsert=True)
        
    @staticmethod
    def delete_testimonial(payload):
        mongo.db.testimonials.delete_one({"Name": payload["Name"], "Company": payload.get("Company")})
        
    @staticmethod
    def review_testimonial(name, company, is_reviewed="N"):
        mongo.db.testimonials.update_one({"Name": name, "Company": company},
                                         {"$set": {"Reviewed": is_reviewed}},
                                         upsert=True)