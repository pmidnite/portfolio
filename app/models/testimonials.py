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
        "Reviewed": "N"(By Admin only)
    }
    '''

    @staticmethod
    def fetch_testimonial():
        return list(mongo.db.testimonials.find())

    @staticmethod
    def fetch_exact_testimonial(name, company):
        return list(mongo.db.testimonials.find({"Name": name, "Email": company}))

    @staticmethod
    def insert_or_update_testimonial(payload):
        payload.update({"Reviewed": "N"})
        mongo.db.testimonials.update_one({"Name": payload["Name"],
                                          "Email": payload.get("Email")},
                                         {"$set": payload},
                                         upsert=True)

    @staticmethod
    def delete_testimonial(payload):
        mongo.db.testimonials.delete_one({"Name": payload["Name"], "Email": payload.get("Email")})

    @staticmethod
    def review_testimonial(name, company, is_reviewed="N"):
        mongo.db.testimonials.update_one({"Name": name, "Email": company},
                                         {"$set": {"Reviewed": is_reviewed}},
                                         upsert=True)
