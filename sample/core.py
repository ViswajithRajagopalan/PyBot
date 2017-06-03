import json
import random
import asyncio
import arrow
import httplib2
import os
import feedparser
#from googleapiclient.discovery import build
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from discord.ext import commands

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
        else:  # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


description = '''PyCalendar'''
bot = commands.Bot(command_prefix='?', description=description)


def getService():
    """Retourne l'objet qui va nous permettre de communiquer avec l'API Google Calendar."""

    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    return discovery.build('calendar', 'v3', http=http)

@bot.event
async def on_ready():

    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('the service is started')
    print('------')
    print('------')


@bot.event
async def on_command_error(error, ctx):
    raise error
    await bot.send_message(ctx.message.author, error)


@bot.command()
async def q(query):
    """Recherche un évènement qui contient la string
        Eg. ?q test"""

    service = getService()  # on récupère le service
    loop =  asyncio.get_event_loop()
    events = await loop.run_in_executor(None, event_query, service, 'primary', query, arrow.utcnow())

    for event in events["items"]:
        await success(event)


@bot.command()
async def update(id, *params):
    """Met à jour un évènement du calendrier
        Eg. ?update id test de math1B"""

    service = getService()  # on récupère le service
    loop =  asyncio.get_event_loop()
    event = await loop.run_in_executor(None, event_get, service, 'primary', id)
    event['summary'] = " ".join(params)
    updated_event = await loop.run_in_executor(None, event_update, service, 'primary', id, event)

    await bot.say("Event portant l'id `{}` à bien été mise à jour dans le calendrier".format(id))
    await success(updated_event)


@bot.command()
async def delete(id):
    """Suppression d'un évènement.
        Eg. ?delete id"""

    service = getService()  # on récupère le service
    loop =  asyncio.get_event_loop()
    res = await loop.run_in_executor(None, event_delete, service, 'primary', id)

    print(res)
    if not res:
        await bot.say("Event avec l'id `{}` à bien été supprimé dans le calendrier".format(id))
    else:
        await bot.say("`Id incorrect...`")


@bot.command()
async def add(*message):
    """Ajout rapide d'un évènement
        Eg. ?add rdv chez le médecin le 5 juin à 15h"""

    if not message:
        await bot.say(":flushed:  ```veuillez insérer un événement en paramètre \n"
                      "Eg. ?add rdz chez le medecin le 23 juin à 15h```")
    else:
        service = getService() # on récupère le service
        created_event = service.events().quickAdd(
           calendarId='primary',
           text=" ".join(message)).execute()

        await bot.say(":mailbox: Nouvel enregistrement {}".format(created_event['htmlLink']))
        await success(created_event)


@bot.command()
async def date(timeMin):
    """Chercher un évènement par rapport à une date.
        Eg. ?date 2017-03-23"""

    # on vérifie si la date rentré est correct
    if isValidDate(timeMin) is False:
        await bot.say(":fearful: `La date entrée n'est pas dans le bon format... `\n"
                      "Format attendu : `Y-m-d` \n "
                      "**Eg. 2017-04-13**")
    else:
        dateMin = arrow.get(timeMin)
        dateMax = dateMin.replace(hour=23, minutes=59, seconds=59)
        print(dateMin, dateMax)
        await showList(dateMax, dateMin)


@bot.command()
async def day():
    """Affiche les évènements du jour.
        Eg. ?day"""
    print(bot.user)
    await showList(nextDay())


@bot.command()
async def weeks():
    """Affiche les évènements de la semaine.
        Eg. ?weeks"""
    print(nextDay(7))
    await showList(nextDay(7))


@bot.command()
async def month():
    """Affiche les évènements du mois.
        Eg. ?month"""
    await showList(nextDay(28))


async def success(event):
    emojy = ":date:"
    dateArr = refactorDate(event)
    date = ' '.join(dateArr)
    summary = event['summary']
    id = event['id']
    await bot.say("{} *{}*  \t :id: `{}` \n"
                  "```-> {}\n```".format(emojy, date, id, summary))

async def showList(dateMax, dateMin = False):
    """Affiche la liste des évènements selon les bornes choisies."""

    if dateMin is False:
        dateMin = arrow.utcnow() # on récupère la date d'ajd

    service = getService()  # on récupère le service
    page_token = None
    while True:
        service = getService()  # on récupère le service
        loop = asyncio.get_event_loop()
        events = await loop.run_in_executor(None, event_list, service, 'primary', page_token, dateMin, dateMax)

        # on vérifie si il y a des events...
        if not events['items']:
            await bot.say(":sunglasses: **rien à l'horizon**")
            before = ":newspaper2: le matin :  "
            msg = infoMatin()
            await bot.say("{} {}".format(before, msg))
            break
        await bot.say("`L'opération peut prendre un certain temps...`")
        for event in events['items']:
            await success(event)

        page_token = events.get('nextPageToken')
        if not page_token:
            await bot.say("`Fin de la recherche`")
            break


def infoMatin():

    python_wiki_rss_url = "http://www.lematin.ch/monde/rss.html"
    feeds = feedparser.parse(python_wiki_rss_url)
    mapFeed=[]
    for feed in feeds["entries"]:
        mapFeed.append(feed["title"] + "\n " + feed["link"])

    return random.choice(mapFeed)


def nextDay(d=1):
    """Retourne le jour + days"""
    # obligé de mettre .to("Europe...) sinon l'heure est en retard de 2h00...
    return arrow.utcnow().to("Europe/Zurich").replace(day=d, hours=23, minutes=59, seconds=59)


def isValidDate(datestring):
    """Vérifie si le format de la date est correct"""

    try:
        datetime.datetime.strptime(datestring, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def refactorDate(event):
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


def event_list(service, calendarId, page_token, dateMin, dateMax):
    return service.events().list(calendarId='primary',
                                   pageToken=page_token,
                                   orderBy='startTime',
                                   singleEvents=True,
                                   timeMin=dateMin,
                                   timeMax=dateMax).execute()


def event_query(service, calendarId, q, timeMin):
    return service.events().list(calendarId=calendarId, q=q, timeMin=timeMin).execute()


def event_get(service, calendarId, id):
    return service.events().get(calendarId=calendarId, eventId=id).execute()


def event_update(service, calendarId, id, event):
    return service.events().update(calendarId=calendarId, eventId=id, body=event).execute()


def event_delete(service, calendarId, id):
    return service.events().delete(calendarId=calendarId, eventId=id).execute()

def main():
    with open('config.json') as json_data:
        d = json.load(json_data)
        bot.run(d["token"])
