from __future__ import print_function
import httplib2
import os
import io
import csv

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from apiclient.http import MediaIoBaseDownload
from oauth2client.file import Storage

downloads_dirname = "spreadsheet_downloads"
scores_dirname = "scores"
home_dir = os.path.expanduser('./')
downloads_dir = os.path.join(home_dir, downloads_dirname)
scores_dir = os.path.join(home_dir, scores_dirname)

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

def makeDirs():
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    if not os.path.exists(downloads_dir):
        os.makedirs(downloads_dir)
    if not os.path.exists(scores_dir):
        os.makedirs(scores_dir)
    
def get_credentials():
    credential_dir = os.path.join(home_dir, '.credentials')
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

def downloadFiles():
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
        for f in files:
            if 'Lab' in f['name']:
                fn = '%s/%s.csv' % (downloads_dir, f['name'])
                data = service.files().export(fileId=f['id'],
                                        mimeType=DST_MIMETYPE).execute()
                if data:
                    with open(fn, 'wb') as fd:
                        fd.write(data)
        return True
    else:
        return False

def gradeFile(fn, scoring):
    # open csv reader to read the downloaded spreadsheets, and then open a
    # csv write so that we can record the score of each student
    fn_download = os.path.join(downloads_dir, fn)
    input_csvfile = open(fn_download, newline='')
    reader = csv.reader(input_csvfile, delimiter=' ', quotechar='|')
    fn_scores = os.path.join(scores_dir, fn)
    output_csvfile = open(fn_scores, 'w+', newline='')
    writer = csv.writer(output_csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)

    header = reader.__next__()[0].split(',')
    header = header[:2] + ['score']
    writer.writerow(header)
    for row in reader:
        row = row[0].split(',')
        name = row[:2]
        row = row[2:]
        score = 0
        for i in range(len(row)):
            if row[i] == 'X':
                score += scoring[i]
        row = name + [score]
        writer.writerow(row)
    input_csvfile.close()
    output_csvfile.close()

def main():
    makeDirs()
    #if downloadFiles():
    dFiles = [f for f in os.listdir(downloads_dir) if
              os.path.isfile(os.path.join(downloads_dir, f))]
    # Read in scoring distributions
    f = open("scoring.txt")
    r = f.readlines()
    f.close()
    scores = {}
    for row in r:
        colon = row.find(':')
        name = row[:colon]
        s = row[colon + 1:]
        s = s.strip()
        s = s.split()
        s = [int(x) for x in s]
        scores[name] = s

    print(scores)
    for f in dFiles:
        name = f[:f.find('.')]
        gradeFile(f, scores[name])


if __name__=='__main__':
    main()
