
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


def switchPerso(command):
    '''Switch personnel qui va appeler nos fonctions pour nous. DRY'''
    switch = {
        "insert": insert,
        "delete": delete,
        "quickadd": quickadd,
        "day": day,
        "weeks": weeks,
        "month": month,
        "listEvent": listEvent,
    }
    return switch.get(command)() # execute la fonction


def insert():
    '''Insère un élément dans le calendrier'''
    print("insert() function called")


def delete():
    '''Supprime un élément dans le calendrier'''
    print("delete() function called")


def quickadd():
    '''insère un évévement rapidement avec une simple string contenant une date'''
    print("quickadd() function called")
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)
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

    while (True):
        print("essayer les commandes suivantes : input, delete, quickAdd, weeks, day, month")
        command = input("insérer la commande : ")
        switchPerso(command)



if __name__ == '__main__':
    main()
