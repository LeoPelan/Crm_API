from bson.objectid import ObjectId


class Clients:
    def __init__(self, db):
        self.db = db
        self.clients = []

    def list(self):
        return self.db.find()

    def find_by_criteria(self, criteria):
        clients = self.db.find(criteria)
        return clients

    def find_by_id(self, client_id):
        client = self.db.find({'_id': ObjectId(client_id)})
        return client

    def find_by_name(self, name):
        clients = self.db.find({'lastname': name})
        return clients

    def find_by_company(self, company):
        clients = self.db.find({'company': company})
        return clients

    def find_by_state(self, state):
        clients = self.db.find({'state': state})
        return clients

    def add(self, client):
        res = self.db.insert_one(client)
        if res.inserted_id:
            return True
        else:
            return False

    def update(self, client_id, client_updated):
        res = self.db.update({'_id': ObjectId(client_id)}, {"$set": client_updated}, upsert=False)
        return res['nModified'] > 0

    def delete(self, client_id):
        client = self.db.delete_one({'_id': ObjectId(client_id)})
        return client.deleted_count == 1

    def delete_all(self):
        self.db.remove({})
