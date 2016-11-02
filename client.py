from bson.objectid import ObjectId


class Clients:
    def __init__(self, db):
        self.db = db
        self.clients = []

    def list(self):
        return self.db.find()

    def find_by_id(self, client_id):
        client = self.db.find({'_id': ObjectId(client_id)})
        print(client)
        return client

    def add(self, client):
        res = self.db.insert_one(client)
        if res.inserted_id:
            return True
        else:
            return False

    def update(self, client_id, client_updated):
        res = self.db.update({'_id': ObjectId(client_id)}, {"$set": client_updated}, upsert=False)
        print(res)
        return True

    def delete(self, client_id):
        client = self.db.delete_one({'_id': ObjectId(client_id)})
        return client.deleted_count == 1

    def delete_all(self):
        self.db.remove({})
