.. sample documentation master file, created by
   sphinx-quickstart on Mon Apr 16 21:22:43 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to sample's documentation!
==================================

Contents:

.. toctree::
   :maxdepth: 2



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

===================
How to use the bot
===================

Example of conversation :
-------------------------
**Get some help**
User : help
Bot : new | quick | delete | search | today | week | month | listEvent
      link documentation

**Add a new event to the calendar**
User : new
Bot : event title ?
User : test de Python
Bot : event description ?
User : all of the subject
Bot : data ? (format dd.mm.yyyy)
User : 23.04.2017
Bot : New event add_.
.. _New event add: #

**Get list event**
User : today
Bot : today - calendar
      test de python : all of the subject


User : week */same with the command month/*
Bot : week - calendar
      Monday 23 mai 2017
         -> test de python : all of the subject

      Wednesday 25 mai 2017
         -> labo 6  : Assignment


**Use search**
User : search "labo"
bot : search - ["labo"]
      Wednesday 25 mai 2017
         -> labo 6  : Assignment

**use listEvent**
User : listEvent
bot : nbEvent ?
User : 3
bot : show you the first 3 events