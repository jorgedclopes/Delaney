from __future__ import print_function

import datetime
from itertools import groupby
import logging
from googleapiclient.errors import HttpError

from src.google_client.activity.activity import get_activity, get_action_info, create_creds, format_info
from src.google_client.format.format_data import get_time, format_notification
from src.google_client.format.formatter import CustomFormatter

READONLY_SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly',
                   'https://www.googleapis.com/auth/drive.activity.readonly',
                   'https://www.googleapis.com/auth/contacts.readonly']

logger = logging.getLogger('main')
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(CustomFormatter())
logger.addHandler(ch)


def create_notification_messages(folder_name):
    creds = create_creds(READONLY_SCOPES)
    items = get_activity(creds, folder_name)
    if not items:
        logger.error('No files found.')
        return

    yesterday = (datetime.datetime.today() - datetime.timedelta(days=1)) \
        .strftime('%d/%m/%Y')

    info = [get_action_info(creds, item) for item in items
            if get_time(item.get('timestamp')) == yesterday]

    info.sort(key=format_info)
    grouped_info = groupby(info, key=format_info)

    if not any(info):
        return ['No activity found.']
    return [format_notification(v) for _, v in grouped_info]


def main():
    try:
        folder_name = 'Pathfinder - Legacy of Fire'
        messages = create_notification_messages(folder_name)
        for message in messages:
            logger.info(message)

    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        logger.fatal(f'An error occurred: {error}')


if __name__ == '__main__':
    main()
