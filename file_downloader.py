from __future__ import print_function
import httplib2
import os
import io

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from apiclient.http import MediaIoBaseDownload
from oauth2client.file import Storage

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/drive-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/drive'
CLIENT_SECRET_FILE = 'client_secrets.json'
APPLICATION_NAME = 'Python'


def get_credentials():
    home_dir = os.path.expanduser('./')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'drive-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
    return credentials


# ID of the 1113 folder
folder_id = '0B_LUTW8XEjWDNmE5UFhZSDhMN1U'

SRC_MIMETYPE = 'application/vnd.google-apps.spreadsheet'
DST_MIMETYPE = 'text/csv'

credentials = get_credentials()
http = credentials.authorize(httplib2.Http())
service = discovery.build('drive', 'v3', http=http)

files = service.files().list(q='mimeType="%s" and "%s" in parents' %
                        (SRC_MIMETYPE, folder_id)).execute().get('files', [])
if files:
    home_dir = os.path.expanduser('./')
    files_dir = os.path.join(home_dir, 'spreadsheet_downloads')
    if not os.path.exists(files_dir):
        os.makedirs(files_dir)

    for f in files:
        if 'Lab' in f['name']:
            fn = 'spreadsheet_downloads/%s.csv' % f['name']
            data = service.files().export(fileId=f['id'],
                                    mimeType=DST_MIMETYPE).execute()
            if data:
                with open(fn, 'wb') as fd:
                    fd.write(data)
