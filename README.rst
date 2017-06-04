============================
What is discordcalendarbot ?
============================

discordcalendarbot is a Discord bot that manage a Google shared calendar.

====================
How to use the bot ?
====================

Installation
------------

$ pip install discordcalendarbot

Configuration
-------------

Insert your Discord bot token in the conf.py file.
Insert your Google Calendar API informations in the client_secret.json file.

Launching
---------

$ python -m discordcalendarbot

Comands availaible
------------------

Every command start with '?' character.

**Get some help**

?help

**Add a new event to the calendar**

?add your_event

example : ?add Dentist tommorow at 5 o'clock

**Delete an event of the calendar**

?delete event_id

**Update an event of the calendar**

?update event_id

**Search events containing a given word or sentence**

?q your_word

example : ?s Dentist

**Show event at a given date**

?date YYYY-MM-DD

**Show events of the day/week/month**

?day

?week

?month
