import json
import logging
import time
import os.path
from typing import List

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from format_data import get_person_id, display_name

logger = logging.getLogger('activity')
logger.setLevel(logging.INFO)


def get_activity(creds, name):
    drive_service = build('drive', 'v3', credentials=creds)
    folder = drive_service.files().list(fields='files(name, id, mimeType)',
                                        q="mimeType = 'application/vnd.google-apps.folder' and "
                                          "name contains '{}'".format(name)).execute()
    folder_id = folder['files'][0]['id']
    activity_service = build('driveactivity',
                             'v2',
                             credentials=creds)
    item = {'ancestorName': "items/{}".format(folder_id)}
    result = activity_service.activity().query(body=item).execute()
    return result['activities']


def get_contacts(creds, name, retries=0):
    # This function can be called quite frequently,
    people_service = build('people', 'v1', credentials=creds)
    try:
        results = people_service.people()\
            .get(resourceName=name, personFields="names,emailAddresses,nicknames")\
            .execute()
    except HttpError:
        if retries >= 3:
            raise RecursionError("Too many retries attempted")
        logger.warning('Too many requests, waiting 1 minute.')
        time.sleep(60)
        return get_contacts(creds, name, retries+1)
    return results


def get_action_info(creds, activity):
    try:
        person_id = get_person_id(activity)
        timestamp = activity.get('timestamp')
        action = list(activity.get('primaryActionDetail').keys())[0]
        contact = get_contacts(creds, person_id)
        person_name = display_name(contact)
        file_name = activity.get('targets')[0].get('driveItem').get('title') \
            if action != "comment" \
            else activity.get('targets')[0].get('fileComment').get('parent').get('title')
        return {"name": person_name,
                "action": action,
                "time": timestamp,
                "filename": file_name
        }
    except (TypeError, AttributeError) as error:
        logger.error(error)
        logger.error(json.dumps(activity, indent=2))
        return


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
