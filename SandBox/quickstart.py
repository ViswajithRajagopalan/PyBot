
from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import datetime

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Calendar API Python Quickstart'


def get_credentials():
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
                                   'calendar-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def main():
    """Shows basic usage of the Google Calendar API.

    Creates a Google Calendar API service object and outputs a list of the next
    10 events on the user's calendar.
    """
    '''Si le fichier credentials n'existe pas il vas nous rediriger sur une page 
        de connection pour obtenir ce fichier '''
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time

    print("Bienvenu, dans le calendrier partagé du Samiral Crew")
    commands = [
        "insert",
        "delete",
        "quickadd",
        "day",
        "weeks",
        "month",
        "listEvent",
    ]

    def insert():
        '''Insère un élément dans le calendrier'''
        print("insert() function called")


    def delete():
        '''Supprime un élément dans le calendrier'''
        print("delete() function called")

    def quickadd():
        '''insère un évévement rapidement avec une simple string contenant une date'''
        print("quickadd() function called")
        service.events().quickAdd(
            calendarId='primary',
            text=input(' -> ')).execute()

    def day():
        '''Retourne les events du jour'''
        print("day() function called")

    def weeks():
        '''Retourne les events de la semaine'''
        print("weeks() function called")

    def month():
        '''Retourne les events du mois'''
        print("month() function called")

    def listEvent():
        '''Affiche les nbEvents les plus récents'''
        print("listEvent() function called")
        eventsResult = service.events().list(
             calendarId='primary', timeMin=now, maxResults=input("nbEvent ? "), singleEvents=True,
             orderBy='startTime').execute()
        events = eventsResult.get('items', [])

        if not events:
            print('No upcoming events found.')
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'], event['id'])

    while (True):
        print("essayer les commandes suivantes : input, delete, quickAdd, weeks, day, month")
        command = input("insérer la commande : ")
        if command == "insert":
            insert()
        elif command == "delete":
            delete()
        elif command == "quickadd":
            quickadd()
        elif command == "day":
            day()
        elif command == "weeks":
            weeks()
        elif command == "month":
            month()
        elif command == "listEvent":
            listEvent()
        else:
            print("Is not a command available")


    print('Getting the upcoming 10 events')

    # #ajoute un événement rapidement
    # created_event = service.events().quickAdd(
    #     calendarId='primary',
    #     text='Axel medecin vendredi 19 à 17h').execute()
    # #delete un event
    # service.events().delete(calendarId='primary', eventId='8843q3pq6rqpjdif9vo0c1kgk8').execute()
    #
    # #récupère une liste liste d'événement
    # eventsResult = service.events().list(
    #     calendarId='primary', timeMin=now, maxResults=10, singleEvents=True,
    #     orderBy='startTime').execute()
    # events = eventsResult.get('items', [])
    #
    # if not events:
    #     print('No upcoming events found.')
    # for event in events:
    #     start = event['start'].get('dateTime', event['start'].get('date'))
    #     print(start, event['summary'], event['id'])
    #
    #
    # # Refer to the Python quickstart on how to setup the environment:
    # # https://developers.google.com/google-apps/calendar/quickstart/python
    # # Change the scope to 'https://www.googleapis.com/auth/calendar' and delete any
    # # stored credentials.
    # '''Ici on prepare notre requête pour l'insertion avec les différent champs suivant summary, description, ...'''
    # event = {
    #   'summary': 'Test de python',
    #   'description': 'Toute la matière vu au début de l\'année',
    #   'start': {
    #     'dateTime': datetime.datetime.utcnow().isoformat() + 'Z',
    #     'timeZone' : 'Europe/Zurich'
    #   },
    #   'end': {
    #     'dateTime': datetime.datetime.utcnow().isoformat() + 'Z',
    #       'timeZone': 'Europe/Zurich'
    #   },
    #   'recurrence': [
    #     'RRULE:FREQ=DAILY;COUNT=2'
    #   ],
    #   'reminders': {
    #     'useDefault': False,
    #     'overrides': [
    #       {'method': 'email', 'minutes': 24 * 60},
    #       {'method': 'popup', 'minutes': 10},
    #     ],
    #   },
    # }
    #
    # event = service.events().insert(calendarId='primary', body=event).execute()
    # print('Event created: %s' % (event.get('htmlLink')))


if __name__ == '__main__':
    main()
