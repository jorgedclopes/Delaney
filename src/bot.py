from __future__ import print_function

import os.path
from typing import List

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
READONLY_SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly',
                   'https://www.googleapis.com/auth/drive.activity.readonly']
SCOPES = ['https://www.googleapis.com/auth/drive.admin.labels']


def get_folder_content(service, parent):
    return service.files().list(fields='files(name, id, mimeType, parents, modifiedTime)',
                                q="'{}' in parents".format(parent)).execute()


def filter_folders(file_list):
    return (el for el in file_list if el['mimeType'] == 'application/vnd.google-apps.folder')


def flatten_list(arg_list):
    return [item for sublist in arg_list for item in sublist]


def get_files(creds, parent_name):
    service = build('drive', 'v3', credentials=creds)
    print(parent_name)
    folder = service.files().list(fields='files(name, id, mimeType)',
                                  q="mimeType = 'application/vnd.google-apps.folder' and "
                                    "name contains '{}'".format(parent_name)).execute()
    folder_name = folder.get('files')[0].get('name')
    folder_id = folder.get('files')[0].get('id')
    print("{} {}".format(folder_name, folder_id))
    # get directory content
    # filter folders
    # if not empty -> for each repeat
    content = get_folder_content(service, folder_id).get('files')
    sub_folders = list(filter_folders(content))
    sub_folder_ids = [sf['id'] for sf in sub_folders]
    files = [el for el in content if not (el['id'] in sub_folder_ids)]
    sub_files = flatten_list([get_files(creds, f.get('name')) for f in sub_folders])
    print("Subfolders: {}".format(sub_folders))
    print("Files: {}".format(files))
    print("Content: {}".format(content))
    print("Subfiles: {}".format(sub_files))
    if sub_files:
        files.extend(sub_files)

    return files


# Create label
# Add label to file under directory recursively
# Query files with label
def main():
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    creds = create_creds(READONLY_SCOPES)

    try:
        items = get_files(creds, 'Pathfinder - Legacy of Fire')
        if not items:
            print('No files found.')
            return
        print('\nFiles:')
        for item in items:
            # print(item)
            print('{0} {1}, {2}'.format(item['name'], item['parents'], item['mimeType']))
    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        print(f'An error occurred: {error}')


def create_creds(scope: List[str]):
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', scope)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', scope)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds


if __name__ == '__main__':
    main()
