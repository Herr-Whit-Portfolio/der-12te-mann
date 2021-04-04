from unittest import TestCase, skip
from actions.actions import ActionGetNextGame, ActionGetTableLeader, ActionGetTeamStats, ActionGetPreviousGames

class FakeTracker():
    def get_slot(self, key):
        slots = {
            'team_name': 'Bayer'
        }
        return slots[key]
tracker = FakeTracker()

@skip('Limit print statements')
class TestActionGetNextGame(TestCase):
    def test_get_next_game(self):
        action_object = ActionGetNextGame()
        print(action_object.interact_with_api())

    def test_get_table(self):
        action_object = ActionGetTableLeader()
        print(action_object.interact_with_api())

@skip
class TestActionGetTeamStats(TestCase):
    def test_interact_with_api(self):
        action_object = ActionGetTeamStats()
        utterance = action_object.interact_with_api(tracker)
        print(utterance)
        self.assertIsInstance(utterance, str)
        self.assertEqual('Bayer Leverkusen', utterance[:16])


    def test_find_team_index(self):
        self.fail()


class TestActionGetPreviousGames(TestCase):
    def test_find_team_name(self):
        action_object = ActionGetPreviousGames()
        name = action_object.find_full_team_name(tracker)
        self.assertIsInstance(name, str)
        self.assertEqual('Bayer Leverkusen', name)

    def test_aggregate_games(self):
        action_object = ActionGetPreviousGames()
        games, _ = action_object.aggregate_games(tracker)
        for game in games:
            self.assertTrue(game['Team1']['TeamName'] == 'Bayer Leverkusen' or game['Team2']['TeamName'] == 'Bayer Leverkusen')

    def test_interact_with_api(self):
        action_object = ActionGetPreviousGames()
        self.assertEqual(27, action_object.get_game_day())
        utterance = action_object.interact_with_api(tracker)
        print(utterance)
        self.assertIsInstance(utterance, str)
        #self.assertEqual('Bayer Leverkusen', utterance[:16])
