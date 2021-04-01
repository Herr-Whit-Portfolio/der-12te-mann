# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

"""
Alle Teams einer Liga:

    https://www.openligadb.de/api/getavailableteams/bl1/2016
"""
# This is a simple example for a custom action which utters "Hello World!"
import datetime
from typing import Any, Text, Dict, List
from requests import get
from datetime import date
#YEAR = str(date.today().year - 1)
#datetime_format = '%Y-%m-%dT%H:%M:%SZ'
import json

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import re
#BASE_URL = 'http://www.openligadb.de/api'


def tidy_string(string):
    string = re.sub('[\n\r ]+', ' ', string)
    return string.strip(' ')


class FootballAction(Action):
    def __init__(self):
        self.YEAR = str(date.today().year - 1)
        self.datetime_format = '%Y-%m-%dT%H:%M:%SZ'
        self.BASE_URL = 'http://www.openligadb.de/api'


class ActionGetTableLeader(FootballAction):

    def name(self) -> Text:
        return "action_get_table_leader"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        apology = "Es tut mir Leid, ich konnte die Tabelle nicht finden."
        request_url = self.BASE_URL + '/getbltable/bl1/' + self.YEAR
        response = get(request_url)
        if response.ok and not response.is_redirect:
            result = json.loads(response.content.decode())
            table_leader = result[0]

            try:
                utterance = f"""
                                {table_leader["TeamName"]} führt die Tabelle mit {table_leader["Points"]} Punkten an und hat einen Vorsprung von
                                {table_leader["Points"] - result[1]["Points"]} Punkten vor dem Tabellen-Zweiten {result[1]["TeamName"]}
                            """
                dispatcher.utter_message(text=tidy_string(utterance))
            except KeyError:
                dispatcher.utter_message(text=apology)
        else:
            dispatcher.utter_message(text=apology)
        return []


"""
Die aktuelle Group (entspricht z.B. bei der Fussball-Bundesliga dem 'Spieltag') des als Parameter zu übergebenden leagueShortcuts (z.B. 'bl1'):

    https://www.openligadb.de/api/getcurrentgroup/bl1

Der aktuelle Spieltag wird jeweils zur Hälfte der Zeit zwischen dem letzten Spiel des letzten Spieltages und dem ersten Spiel des nächsten Spieltages erhöht.
"""


class ActionGetNextGame(FootballAction):

    def name(self) -> Text:
        return "action_get_next_game"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        utterance = self.interface_with_api()
        dispatcher.utter_message(text=utterance)
        return []

    def interface_with_api(self):
        apology = "Es tut mir Leid, ich konnte kein Spiel finden."
        request_url = self.BASE_URL + '/getmatchdata/bl1'
        response = get(request_url)
        if response.ok and not response.is_redirect:
            results = json.loads(response.content.decode())

            try:
                day = datetime.datetime.strptime(results[0]['MatchDateTimeUTC'], self.datetime_format).date()
                utterance = f"Die folgenden Spiele finden am {results[0]['Group']['GroupName']} ({day}) statt:\n"
                for result in results:
                    time = datetime.datetime.strptime(result['MatchDateTimeUTC'], self.datetime_format).time()
                    utterance += tidy_string(f"""
                                            {time}: {result['Team1']['TeamName']} gegen {result['Team2']['TeamName']}
                                        """) + '\n'
                return utterance
            except KeyError:
                return apology
        else:
            return apology



"""
Alle Teams einer Liga:

    https://www.openligadb.de/api/getavailableteams/bl1/2016
"""