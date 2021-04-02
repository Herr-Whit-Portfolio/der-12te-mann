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

import json

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import re
from abc import abstractmethod

import nltk


def tidy_string(string):
    string = re.sub('[\n\r ]+', ' ', string)
    return string.strip(' ')


class FootballBotAction(Action):
    BASE_URL = 'http://www.openligadb.de/api'
    YEAR = str(date.today().year - 1)
    datetime_format = '%Y-%m-%dT%H:%M:%S'
    apology = "Upps! Da ist was schiefgelaufen. Ich kann dir leider keine Antwort geben."

    @property
    def endpoint(self):
        raise NotImplementedError

    @abstractmethod
    def name(self) -> Text:
        return 'ABC_Football_Bot'

    @abstractmethod
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        pass

    @abstractmethod
    def interact_with_api(self, **domain):
        pass

    @staticmethod
    def send_request(request_url):
        response = get(request_url)
        assert response.ok and not response.is_redirect
        result = json.loads(response.content.decode())
        return result


class ActionGetTableLeader(FootballBotAction):
    endpoint = '/getbltable/bl1/'
    apology = "Es tut mir Leid, ich konnte die Tabelle nicht finden."

    def name(self) -> Text:
        return "action_get_table_leader"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        utterance = self.interact_with_api()
        dispatcher.utter_message(text=utterance)
        return []

    def interact_with_api(self):
        try:
            result = self.send_request(self.BASE_URL + self.endpoint + self.YEAR)
            table_leader = result[0]
            utterance = f"""
                                    {table_leader["TeamName"]} führt die Tabelle mit {table_leader["Points"]} Punkten an und hat einen Vorsprung von
                                    {table_leader["Points"] - result[1]["Points"]} Punkten vor dem Tabellen-Zweiten {result[1]["TeamName"]}
                                """
            return tidy_string(utterance)
        except KeyError or AssertionError:
            return self.apology


class ActionGetTeamStats(FootballBotAction):
    apology = "Es tut mir Leid, ich konnte die Statistiken nicht finden."
    endpoint = '/getbltable/bl1/'

    def name(self) -> Text:
        return "action_get_team_stats"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        utterance = self.interact_with_api(tracker)
        dispatcher.utter_message(text=utterance)
        return []

    def interact_with_api(self, tracker):
        #try:
        results = self.send_request(self.BASE_URL + self.endpoint + self.YEAR)
        team_index = self.find_team_index(results, tracker.get_slot('team_name'))
        team_stats = results[team_index]
        team_stats['TeamRank'] = team_index
        utterance = self.format_utterance(team_stats)
        return tidy_string(utterance)
        #except KeyError or AssertionError:
          #  return self.apology

    @staticmethod
    def format_utterance(stats):
        utterance = f"""
            {stats['TeamName']} ist auf dem {stats['TeamRank']}. Platz mit  {stats['Points']} Punkten. 
        """
        return utterance

    @staticmethod
    def find_team_index(table, team_name):
        table_names = [entry['TeamName'] for entry in table]
        word_level_edit_distances = list()

        for name in table_names:
            word_level_edit_distances.append(min([nltk.edit_distance(word, team_name) for word in name.split(' ')]))

        return word_level_edit_distances.index(min(word_level_edit_distances))



"""
Die aktuelle Group (entspricht z.B. bei der Fussball-Bundesliga dem 'Spieltag') des als Parameter zu übergebenden leagueShortcuts (z.B. 'bl1'):

    https://www.openligadb.de/api/getcurrentgroup/bl1

Der aktuelle Spieltag wird jeweils zur Hälfte der Zeit zwischen dem letzten Spiel des letzten Spieltages und dem ersten Spiel des nächsten Spieltages erhöht.
"""


class ActionGetNextGame(FootballBotAction):
    endpoint = '/getmatchdata/bl1'
    apology = "Es tut mir Leid, ich konnte kein Spiel finden."

    def name(self) -> Text:
        return "action_get_next_game"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        utterance = self.interact_with_api()
        dispatcher.utter_message(text=utterance)
        return []

    def interact_with_api(self):
        try:
            results = self.send_request(self.BASE_URL + self.endpoint)
            day = datetime.datetime.strptime(results[0]['MatchDateTime'], self.datetime_format).date()
            utterance = f"Die folgenden Spiele finden am {results[0]['Group']['GroupName']} ({day}) statt:\n"
            for result in results:
                time = datetime.datetime.strptime(result['MatchDateTime'], self.datetime_format).time()
                utterance += tidy_string(f"""
                                        {time}: {result['Team1']['TeamName']} gegen {result['Team2']['TeamName']}
                                    """) + '\n'
            return utterance
        except KeyError or AssertionError:
            return self.apology





"""
Alle Teams einer Liga:

    https://www.openligadb.de/api/getavailableteams/bl1/2016
"""