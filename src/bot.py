from __future__ import print_function

import datetime
from itertools import groupby
import json
import logging
from googleapiclient.errors import HttpError

from activity import get_activity, get_action_info, create_creds
from src.formatter import CustomFormatter

READONLY_SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly',
                   'https://www.googleapis.com/auth/drive.activity.readonly',
                   'https://www.googleapis.com/auth/contacts.readonly']
SCOPES = ['https://www.googleapis.com/auth/drive.admin.labels']

logger = logging.getLogger('main')
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(CustomFormatter())
logger.addHandler(ch)


def get_time(individual_info):
    return datetime.datetime.fromisoformat(individual_info.get('time')) \
                .replace(hour=0, minute=0, second=0, microsecond=0).strftime("%d/%m/%Y")


def main():
    creds = create_creds(READONLY_SCOPES)

    try:
        folder_name = 'Pathfinder - Legacy of Fire'
        items = get_activity(creds, folder_name)
        if not items:
            logger.error('No files found.')
            return

        info = [get_action_info(creds, item) for item in items]

        def key(individual_info):
            entry_time = get_time(individual_info)
            action = individual_info.get('action')
            file = individual_info.get('filename')
            name = individual_info.get('name')
            return "{}{}{}{}".format(entry_time, action, file, name)

        info.sort(key=key)
        grouped_info = groupby(info, key=key)
        logger.info(json.dumps(info, indent=2))
        for _, v in grouped_info:
            info_list = list(v)
            info_count = len(info_list)
            time = get_time(info_list[0])

            logger.info("On this day of {}, {} {} on file \"{}\" a total of {} time(s)."
                        .format(time,
                                info_list[0].get('name'),
                                info_list[0].get('action'),
                                info_list[0].get('filename'),
                                info_count))

    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        logger.fatal(f'An error occurred: {error}')


if __name__ == '__main__':
    main()
