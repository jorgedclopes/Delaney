import datetime
import logging

logger = logging.getLogger('format')
logger.setLevel(logging.INFO)


def get_person_id(file):
    return file.get('actors')[0].get('user').get('knownUser').get('personName')


def display_name(person):
    return person.get("names")[0].get("displayName")
    # throws TypeError if it doesn't find the data


def get_time(arg_time):
    return datetime.datetime.fromisoformat(arg_time) \
        .replace(hour=0, minute=0, second=0, microsecond=0).strftime("%d/%m/%Y")


def format_notification(v):
    info_list = list(v)
    info_count = len(info_list)
    time = get_time(info_list[0].get('time'))
    notification_message = "On this day of {}, {} {} on file \"{}\" a total of {} time(s)." \
        .format(time,
                info_list[0].get('name'),
                info_list[0].get('action'),
                info_list[0].get('filename'),
                info_count)
    return notification_message
