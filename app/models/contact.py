from app import mongo

class Contact:
    '''
    Sample Payload
    --------------
    {
    	"Name" : "Subham Kumar",
    	"Email" : "kumars@email.com",
    	"Subject" : "Hello",
    	"Message" : "Hey Want to get in contact with you. Mail me back once you get this."
    }
    '''

    @staticmethod
    def fetch_contact():
        return list(mongo.db.contact.find())

    @staticmethod
    def fetch_exact_contact(email):
        return list(mongo.db.contact.find({"Email": email}))

    @staticmethod
    def insert_contact(payload):
        mongo.db.contact.insert_one(payload)

    @staticmethod
    def delete_contact(payload):
        mongo.db.contact.delete_one({"Email": payload["Email"]})
