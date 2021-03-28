# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List
from requests import get
from datetime import date
YEAR = str(date.today().year - 1)
import json

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

BASE_URL = 'http://www.openligadb.de/api'


class ActionGetTeamRanking(Action):

    def name(self) -> Text:
        return "action_get_team_ranking"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        request_url = BASE_URL + '/getbltable/bl1/' + YEAR
        response = get(request_url)
        if response.ok and not response.is_redirect:
            result = json.loads(response.content.decode())
            table_leader = result[0]

            utterance = f"""
                {table_leader["TeamName"]} führt die Tabelle mit {table_leader["Points"]} Punkten an und hat einen Vorsprung von
                {table_leader["Points"] - result[1]["Points"]} Punkten vor dem Tabellen-Zweiten {result[1]["TeamName"]}
            """.replace('\n', ' ')

            dispatcher.utter_message(text=utterance)
        else:
            dispatcher.utter_message(text="Es tut mir Leid, ich konnte die Tabelle nicht finden.")
        return []
