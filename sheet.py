from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage


class Sheets:
    def __init__(self, sheet_id):
        try:
            import argparse
            self.flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
        except ImportError:
            self.flags = None

        self.SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
        self.CLIENT_SECRET_FILE = 'client_secret.json'
        self.APPLICATION_NAME = 'Google Sheets API Python Quickstart'

        self.credentials = self.get_credentials()
        self.sheet_id = sheet_id

        self.range_names = 'A1:D'
        self.discovery_url = ('https://sheets.googleapis.com/$discovery/rest?'
                         'version=v4')

        self.value_input_option = 'RAW'

    # Get credentials
    def get_credentials(self):
        """Gets valid user credentials from storage.

        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth2 flow is completed to obtain the new credentials.

        Returns:
            Credentials, the obtained credential.
        """
        home_dir = os.path.expanduser('~')
        credential_dir = os.path.join(home_dir, '.credentials')

        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)

        credential_path = os.path.join(credential_dir,
                                       'sheets.googleapis.com-python-quickstart.json')

        store = Storage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(self.CLIENT_SECRET_FILE, self.SCOPES)
            flow.user_agent = self.APPLICATION_NAME
            if self.flags:
                credentials = tools.run_flow(flow, store, self.flags)
            else:  # Needed only for compatibility with Python 2.6
                credentials = tools.run(flow, store)
            print('Storing credentials to ' + credential_path)

        return credentials

    # Read sheet
    def read_sheet(self):
        http = self.credentials.authorize(httplib2.Http())
        service = discovery.build('sheets', 'v4', http=http, discoveryServiceUrl=self.discovery_url)
        result = service.spreadsheets().values().batchGet(spreadsheetId=self.sheet_id, ranges=self.range_names).execute()
        return result

    # White sheet
    def write_sheet(self, values, range_name):
        body = {
            'values': values
        }

        http = self.credentials.authorize(httplib2.Http())
        service = discovery.build('sheets', 'v4', http=http,
                                  discoveryServiceUrl=self.discovery_url)

        service.spreadsheets().values().update(
            spreadsheetId=self.sheet_id, range=range_name,
            valueInputOption=self.value_input_option, body=body).execute()
