from unittest import TestCase
from actions.actions import ActionGetNextGame, ActionGetTableLeader, BASE_URL, YEAR, datetime_format


class TestActions(TestCase):
    def test_get_next_game(self):
        action_class = ActionGetNextGame()
        print(action_class.interface_with_api())

    def test_get_table(self):
        action_class = ActionGetTableLeader()
        print(action_class.interact_with_api())
