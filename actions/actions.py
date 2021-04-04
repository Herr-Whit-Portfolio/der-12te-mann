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
        try:
            results = self.send_request(self.BASE_URL + self.endpoint + self.YEAR)
            team_index = self.find_team_index(results, tracker.get_slot('team_name'))
            team_stats = results[team_index]
            team_stats['TeamRank'] = team_index
            utterance = self.format_utterance(team_stats)
            return tidy_string(utterance)
        except KeyError or AssertionError:
            return self.apology

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
            return self.format_utterance(results)
        except KeyError or AssertionError:
            return self.apology

    def format_utterance(self, results):
        day = datetime.datetime.strptime(results[0]['MatchDateTime'], self.datetime_format).date()
        utterance = f"Die folgenden Spiele finden am {results[0]['Group']['GroupName']} ({day}) statt:\n"
        for result in results:
            time = datetime.datetime.strptime(result['MatchDateTime'], self.datetime_format).time()
            utterance += tidy_string(f"""
                                        {time}: {result['Team1']['TeamName']} gegen {result['Team2']['TeamName']}
                                    """) + '\n'
        return utterance





"""
Alle Teams einer Liga:

    https://www.openligadb.de/api/getavailableteams/bl1/2016
"""

"""
Spiele des 8. Spieltages der ersten Bundesliga 2016/2017:
https://www.openligadb.de/api/getmatchdata/bl1/2016/8
"""


class ActionGetPreviousGames(FootballBotAction):
    endpoint = '/getmatchdata/bl1/%(year)s/%(game_day)s'
    apology = "Es tut mir Leid, ich konnte kein Spiel finden."
    history_length = 3

    def name(self) -> Text:
        return "action_get_previous_games"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        utterance = self.interact_with_api(tracker)
        dispatcher.utter_message(text=utterance)
        return []

    def interact_with_api(self, tracker):
        try:
            games, team_name = self.aggregate_games(tracker)
            utterance = self.format_utterance(games, team_name)
            return utterance
        except KeyError or AssertionError:
            return self.apology

    def format_utterance(self, results, team_name):
        utterance = f"In den letzten {self.history_length} Spieltagen spielte {team_name} {len(results)} Spiele:\n"
        for result in results:
            time = datetime.datetime.strptime(result['MatchDateTime'], self.datetime_format).time()
            date = datetime.datetime.strptime(result['MatchDateTime'], self.datetime_format).date()
            utterance += tidy_string(f"""
                                        {date}, {time}: {result['Team1']['TeamName']} gegen {result['Team2']['TeamName']}; 
                                        {result['MatchResults'][0]['PointsTeam1']} - {result['MatchResults'][0]['PointsTeam2']}
                                    """) + '\n'
        return utterance

    def aggregate_games(self, tracker):
        game_day = self.get_game_day()
        team_name = self.find_full_team_name(tracker)
        past_game_days = [game_day - i for i in range(1, self.history_length + 1)]
        day_infos = list()
        for day in past_game_days:
            results = self.send_request(self.BASE_URL + self.endpoint % {'year': str(self.YEAR), 'game_day': str(day)})
            day_info = self.filter_team_info(results, team_name)
            day_infos.append(day_info)
        return day_infos, team_name

    def get_game_day(self):
        next_game_endpoint = '/getmatchdata/bl1'
        results = self.send_request(self.BASE_URL + next_game_endpoint)
        return results[0]['Group']['GroupOrderID']

    @staticmethod
    def filter_team_info(game_day, team_name):
        for game in game_day:
            if game["Team1"]['TeamName'] == team_name or game["Team2"]['TeamName'] == team_name:
                return game

    def find_full_team_name(self, tracker):
        table_endpoint = '/getbltable/bl1/' + self.YEAR
        table = self.send_request(self.BASE_URL + table_endpoint)
        index = self.find_team_index(table, tracker.get_slot('team_name'))
        full_team_name = table[index]['TeamName']
        return full_team_name

    @staticmethod
    def find_team_index(table, team_name):
        table_names = [entry['TeamName'] for entry in table]
        word_level_edit_distances = list()

        for name in table_names:
            word_level_edit_distances.append(min([nltk.edit_distance(word, team_name) for word in name.split(' ')]))

        return word_level_edit_distances.index(min(word_level_edit_distances))

