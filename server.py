from flask import Flask, request, jsonify, send_file
from flask_restful import Resource, Api
from pymongo import MongoClient
from bson import json_util
import json
from client import Clients
from api import readSheet
from api import writeSheet


# ** APP **
app = Flask(__name__)
# api = Api(app)


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response


# ** APP CONSTANT **
client_states = ("Prospect", "Projet en cours", "Projet terminé", "Partenaire")


# ** DATABASE CONFIG **
db_client = MongoClient('localhost', 27017)
db = db_client.python

# ** INIT **
clients = Clients(db.clients)

# api.add_resource(List, '/api/client/list')
# ** ROUTING **
@app.route("/")
def index():
    return send_file("templates/index.html")


# ** API **
@app.route('/api/client/list')
def api_list_clients():
    client_list = json.loads(json_util.dumps(clients.list()))
    return jsonify({'client_list': client_list})

# Export
@app.route('/api/client/export')
def api_export_clients():
    client_list = json.loads(json_util.dumps(clients.list()))
    client_list_display = jsonify({'client_list': client_list})

    for i in range(len(client_list)) :
        j = i+1
        user_company = client_list[i]['company']
        user_firstname = client_list[i]['firstname']
        user_lastname = client_list[i]['lastname']
        user_state = client_list[i]['state']
        values = [[user_company, user_firstname, user_lastname, user_state],]
        range_name = 'A'+str(j)+':D'
        writeSheet(values, range_name)

    return client_list_display

# Import
@app.route('/api/client/import')
def api_import_clients():
    values = readSheet()
    # Liste comprenant les users enregistres sur le GoogleSheet
    users_to_import_json = jsonify(values['valueRanges'][0]['values'])

    #Nombre de users
    user_number = len(values['valueRanges'][0]['values'])

    print(user_number)
    return users_to_import_json

# Get by id - WORK
@app.route('/api/client/<client_id>')
def api_get_client(client_id):
    client = json.loads(json_util.dumps(clients.find_by_id(client_id)))
    return jsonify({'success': True if client else False, 'client': client[0]})


# Add - WORK
@app.route('/api/client/add', methods=['POST'])
def api_add_client():
    data = request.get_json()
    return jsonify({'success': clients.add(data['newClient'])})


# Delete - WORK
@app.route('/api/client/delete/<client_id>')
def remove_client(client_id):
    return jsonify({'success': clients.delete(client_id)})


# Edit
@app.route('/api/client/edit/<client_id>', methods=['POST'])
def edit_client(client_id):
    print(client_id)
    data = request.get_json()
    return jsonify({'success': clients.update(client_id, data['client'])})


# Remove all
@app.route('/api/client/delete/all')
def remove_all():
    clients.delete_all()
    return True


# ** Run server **
if __name__ == "__main__":
    app.run()
