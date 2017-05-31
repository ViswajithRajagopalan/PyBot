from __future__ import print_function

import discord
from discord.ext import commands
import json
import arrow
import httplib2
import os
from datetime import datetime, timezone
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


from discord.ext import commands
description = '''PyCalendar'''
bot = commands.Bot(command_prefix='?', description=description)

@bot.event
async def on_ready():

    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('the service is started')
    print('------')


@bot.event
async def on_command_error(error, ctx):
        await bot.send_message(ctx.message.author, error)

@bot.command()
async def update(id, *params):
    """Met à jour un événement du calendrier
        Eg. ?update id test de math1B"""


    service = await getService()  # on récupère le service
    event = service.events().get(calendarId='primary', eventId=id).execute()
    event['summary'] = " ".join(params)
    updated_event = service.events().update(calendarId='primary', eventId=event['id'], body=event).execute()

    await bot.say("Event portant l'id `{}` à bien été mise à jour dans le calendrier".format(id))


@bot.command()
async def delete(id):
    """Suppression d'un event.
        Eg. ?delete id"""

    service = await getService()  # on récupère le service
    res = service.events().delete(calendarId='primary', eventId=id).execute()
    if not res:
        await bot.say("Event avec l'id `{}` à bien été supprimé dans le calendrier".format(id))
    else:
        await bot.say("`Id incorrect...`")



@bot.command()
async def quick(*message):
    """Ajout rapide d'un événement
        Eg. ?quick rdz chez le medecin le 5 juin à 15h"""

    if not message:
        await bot.say(":flushed:  ```veuillez insérer un événement en paramètre \n"
                      "Eg. ?quick rdz chez le medecin le 23 juin à 15h```")
    else:
        service = await getService() # on récupère le service
        created_event = service.events().quickAdd(
           calendarId='primary',
           text=" ".join(message)).execute()

        await bot.say(":mailbox: Nouvelle enregistrement {}".format(created_event['htmlLink']))

async def getService():
    """Va nous retourner l'objet qui va nous permettre de communiquer avec l'api calendar."""

    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)
    return service

@bot.command()
async def date(timeMin):
    """Chercher un event par rapport à une date.
        Eg. ?date 2017-03-23"""

    # on vérifie si la date rentré est correct
    if await isValidDate(timeMin) is False:
        await bot.say(":fearful: `La date entrée n'est pas dans le bon format... `\n"
                      "Format attendu : `Y-m-d` \n "
                      "**Eg. 2017-04-13**")
    else:
        dateMin = arrow.get(timeMin).to("Europe/Zurich")
        dateMax = dateMin.replace(hour=23, minutes=59, seconds=59)
        print(dateMin, dateMax)
        await showList(dateMax, dateMin)
        await showList(dateMax, dateMin)


async def isValidDate(datestring):
    """Vérifie si le format de la date est correct"""

    try:
        datetime.datetime.strptime(datestring, '%Y-%m-%d')
        return True
    except ValueError:
        return False


@bot.command()
async def day():
    """Affiche les événements du jour.
        Eg. ?day"""

    dateMax = arrow.utcnow().to("Europe/Zurich").replace(hours=23, minutes=59, seconds=59)
    await showList(dateMax)

@bot.command()
async def weeks():
    """Affiche les événements de la semaine.
        Eg. ?weeks"""

    dateMax = arrow.utcnow().to("Europe/Zurich").replace(days=7, hours=23, minutes=59, seconds=59)
    await showList(dateMax)

@bot.command()
async def month():
    """Affiche les événements du mois.
        Eg. ?month"""

    dateMax = arrow.utcnow().to("Europe/Zurich").replace(days=28, hours=23, minutes=59, seconds=59)
    await showList(dateMax)

async def showList(dateMax, dateMin = False):
    """Affiche la liste des events selon bornes choisies."""

    if dateMin is False:
        dateMin = arrow.utcnow().to("Europe/Zurich") # on récupère la date d'ajd

    service = await getService()  # on récupère le service
    page_token = None
    while True:
        events = service.events().list(calendarId='primary',
                                       pageToken=page_token,
                                       orderBy='startTime',
                                       singleEvents=True,
                                       timeMin=dateMin,
                                       timeMax=dateMax).execute()

        # on vérifie si il y a des events...
        if not events['items']:
            await bot.say(":sunglasses: **rien à l'horizon** ")
            break
        await bot.say("`L'opération peut prendre un certain temps...`")
        for event in events['items']:
            emojy = ":date:"
            dateArr = await refactorDate(event)
            date = ' '.join(dateArr)
            summary = event['summary']
            id = event['id']
            await bot.say("{} *{}*  \t :id: `{}` \n"
                          "```-> {}\n```".format(emojy, date, id, summary))

        page_token = events.get('nextPageToken')
        if not page_token:
            await bot.say("`Fin de la recherche`")
            break


async def refactorDate(event):
    """Fonction qui nous retourne la date selon le format dd-mm-yyyy"""

    dateArr = None
    if "date" in event['end']:  # on vérifie si l'évenement est sur toute la journée
        '''Le format event['end'][date] renvoie le format yyyyy-mm-dd'''
        dateArr = arrow.get(event['start']['date']).format("DD-MM-YYYY")
        dateArr += " toute la journée"
    else:
        '''Le format event['end']['dateTime] renvoie le format yyyy-mm-ddTHH-MM-S'''
        timeMax = arrow.get(event['end']['dateTime']).format("HH:mm")
        timeMin = arrow.get(event['start']['dateTime']).format("DD-MM-YYYY | HH:mm")
        dateArr = " ".join((timeMin, " à ", timeMax))

    return dateArr

with open('config.json') as json_data:
    d = json.load(json_data)
    bot.run(d["token"])

