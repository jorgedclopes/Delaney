import logging

logger = logging.getLogger('format')
logger.setLevel(logging.INFO)


def get_person_id(file):
    return file.get('actors')[0].get('user').get('knownUser').get('personName')


def display_name(person):
    return person.get("names")[0].get("displayName")
    # throws TypeError if it doesn't find the data

