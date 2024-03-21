# model about.py
from app import mongo

class About:
    '''
    Sample Payload
    --------------
    {
        "Current Designation": "Lead Software Developer",
        "Short Description": "I am working as a Lead Full Stack Developer in a leading healthcare product company ZeOmega, orchestrating end-to-end development of product modules. I oversee the development of comprehensive solutions while maintaining a keen interest in cybersecurity.  Passionate about cybersecurity, I actively seeking opportunities to enhance my knowledge and skill in this domain for defenses against potential threats, safeguarding sensitive information and computer forensics.",
        "Description": "As a Lead Software Developer in a healthcare company, I adeptly manage diverse modules of our products while ensuring seamless client support. Additionally, I excel in offering technical assistance and guidance to my team members, fostering strong relationships built on trust and reliability. I've collaborated with cross-functional teams to deliver high-quality solutions that address different challenges. My multifaceted experience encompasses the intricacies of healthcare software development coupled with a proactive approach to client engagement, driving innovation and enhancing operational efficiency.",
        "Phone": "9641157205",
        "Email": "nsarfaraz@email.com",
        "Website": "http://google.com",
        "Current Company": "ZeOmega Infotech Pvt Ltd",
        "Birthday": "25 February 1994",
        "City": "Bengaluru, India",
        "Degree": "Bachelor Of Technology",
        "Self Facts": "As someone who may not fit the conventional mold of being photogenic, I bring a depth of thoughtfulness and introspection to every interaction. My focus lies not in outward appearance but in cultivating meaningful connections and delivering impactful results. Through thoughtful analysis and consideration, I approach challenges with insight and empathy, striving to create genuine value in all endeavors."
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
