from __future__ import print_function

import os.path
from datetime import datetime
from typing import List

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
READONLY_SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly',
                   'https://www.googleapis.com/auth/drive.activity',
                   'https://www.googleapis.com/auth/contacts.readonly']
SCOPES = ['https://www.googleapis.com/auth/drive.admin.labels']


def get_activity(creds, name):
    drive_service = build('drive', 'v3', credentials=creds)
    folder = drive_service.files().list(fields='files(name, id, mimeType)',
                                        q="mimeType = 'application/vnd.google-apps.folder' and "
                                          "name contains '{}'".format(name)).execute()
    folder_id = folder['files'][0]['id']
    activity_service = build('driveactivity',
                             'v2',
                             credentials=creds)
    datetime.utcnow()
    item = {'ancestorName': "items/{}".format(folder_id)}
    result = activity_service.activity().query(body=item).execute()
    return result['activities']


def get_person_id(file):
    return file.get('actors')[0].get('user').get('knownUser').get('personName')


def display_name(person):
    return person.get("names")[0].get("displayName")
    # throws TypeError if it doesn't find the data


def get_contacts(creds, name):
    people_service = build('people', 'v1', credentials=creds)
    results = people_service.people().get(resourceName=name, personFields="names,emailAddresses,nicknames").execute()
    return results


def get_action_info(creds, activity):
    person_id = get_person_id(activity)
    timestamp = activity.get('timestamp')
    try:
        contact = get_contacts(creds, person_id)
        person_name = display_name(contact)
        return [person_name,
                list(activity.get('primaryActionDetail').keys())[0],
                timestamp
                ]
    except (TypeError, AttributeError):
        return


# Create label
# Add label to file under directory recursively
# Query files with label
def main():
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    creds = create_creds(READONLY_SCOPES)

    try:
        items = get_activity(creds, 'Pathfinder - Legacy of Fire')
        if not items:
            print('No files found.')
            return

        # print(json.dumps(items, indent=4))
        info = [get_action_info(creds, item) for item in items]
        for i in info:
            print(i)
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
