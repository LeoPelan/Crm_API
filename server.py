from flask import Flask, request, jsonify, send_file
from flask_restful import Resource, Api
from pymongo import MongoClient
from bson import json_util
import json
from client import Clients
from sheet import Sheets

# ** APP **
app = Flask(__name__)


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response


# ** APP CONSTANT **
client_states = {'prospect': 'Prospect',
                 'progress': 'Projet en cours',
                 'complete': 'Projet terminé',
                 'partner': 'Partenaire'}
sheet_id = '1ZpAQEw9SH3r6uxRHiNiFIv8IGX767QKQGBt_1ajqb_U'

# ** DATABASE CONFIG **
db_client = MongoClient('localhost', 27017)
db = db_client.python

# ** INIT **
clients = Clients(db.clients)
sheets = Sheets(sheet_id)


# ** ROUTING **
@app.route("/")
def index():
    return send_file("templates/index.html")


# ** API **
# List - WORK
@app.route('/api/client/list')
def api_list_clients():
    client_list = json.loads(json_util.dumps(clients.list()))
    return jsonify({'client_list': client_list})


# Export
@app.route('/api/client/export')
def api_export_clients():
    client_list = json.loads(json_util.dumps(clients.list()))

    for i in range(len(client_list)):
        j = i+1
        user_company = client_list[i]['company']
        user_firstname = client_list[i]['firstname']
        user_lastname = client_list[i]['lastname']
        user_state = client_list[i]['state']
        values = [[user_company, user_firstname, user_lastname, user_state],]
        range_name = 'A'+str(j)+':D'
        sheets.write_sheet(values, range_name)

    return jsonify({'success': True})


# Import
@app.route('/api/client/import')
def api_import_clients():
    # Liste comprenant les users enregistres sur le GoogleSheet
    values = sheets.read_sheet()
    users_to_import = values['valueRanges'][0]['values']

    # Nombre d'utilisateurs ajoutés
    users_added = 0
    insert_error = False

    for i in range(len(users_to_import)):
        # 1 on transforme le tableau en dictionnaire
        criteria = {'company': users_to_import[i][0],
                    'firstname': users_to_import[i][1],
                    'lastname': users_to_import[i][2],
                    'state': users_to_import[i][3]}

        # 2 on teste l'existence en bdd
        res = json.loads(json_util.dumps(clients.find_by_criteria(criteria)))

        # 3 si il n'y a pas de résultat pour les critères de recherche de notre utilisateur courant
        if not res:
            # on l'ajoute
            if clients.add(criteria):
                # on incrémente le compteur d'utilisateur ajouté
                users_added += 1
            # Une erreur est survenue lors de l'ajout
            else:
                insert_error = True

    return jsonify({'success': not insert_error, 'users_added': users_added})


# Get by id - WORK
@app.route('/api/client/<client_id>')
def api_get_client(client_id):
    client = json.loads(json_util.dumps(clients.find_by_id(client_id)))
    return jsonify({'success': True if client else False, 'client': client[0]})


# Search
@app.route('/api/client/search')
def api_search_client():
    criteria = dict()

    if 'company' in request.args:
        criteria['company'] = request.args.get('company')

    if 'lastname' in request.args:
        criteria['lastname'] = request.args.get('lastname')

    if 'firstname' in request.args:
        criteria['firstname'] = request.args.get('firstname')

    if 'state' in request.args:
        criteria['state'] = request.args.get('state')

    res = json.loads(json_util.dumps(clients.find_by_criteria(criteria)))

    return jsonify({'success': True if res else False, 'client_list': res})


# Get by name - WORK
@app.route('/api/client/name/<name>')
def api_get_client_by_name(name):
    res = json.loads(json_util.dumps(clients.find_by_name(name)))
    return jsonify({'success': True if res else False, 'client_list': res})


# Get by company - WORK
@app.route('/api/client/company/<company>')
def api_get_client_by_company(company):
    res = json.loads(json_util.dumps(clients.find_by_company(company)))
    return jsonify({'success': True if res else False, 'client_list': res})


# Get by state - WORK
@app.route('/api/client/state/<state>')
def api_get_client_by_state(state):
    res = json.loads(json_util.dumps(clients.find_by_state(state)))
    return jsonify({'success': True if res else False, 'client_list': res})


# Add - WORK
@app.route('/api/client/add', methods=['POST'])
def api_add_client():
    data = request.get_json()
    return jsonify({'success': clients.add(data['newClient'])})


# Delete - WORK
@app.route('/api/client/delete/<client_id>')
def remove_client(client_id):
    return jsonify({'success': clients.delete(client_id)})


# Edit - WORK
@app.route('/api/client/edit/<client_id>', methods=['POST'])
def edit_client(client_id):
    print(client_id)
    data = request.get_json()
    return jsonify({'success': clients.update(client_id, data['client'])})


# Remove all - WORK
@app.route('/api/client/delete/all')
def remove_all():
    clients.delete_all()
    return True


# ** Run server **
if __name__ == "__main__":
    app.run()
