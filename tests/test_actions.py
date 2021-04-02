from unittest import TestCase, skip
from actions.actions import ActionGetNextGame, ActionGetTableLeader, ActionGetTeamStats

@skip('Limit print statements')
class TestActions(TestCase):
    def test_get_next_game(self):
        action_class = ActionGetNextGame()
        print(action_class.interact_with_api())

    def test_get_table(self):
        action_class = ActionGetTableLeader()
        print(action_class.interact_with_api())


class TestActionGetTeamStats(TestCase):
    def test_interact_with_api(self):
        domain = {'team_name': 'Bayer'}
        action_class = ActionGetTeamStats()
        utterance = action_class.interact_with_api(domain)
        print(utterance)
        self.assertIsInstance(utterance, str)
        self.assertEqual('Bayer Leverkusen', utterance[:16])
    @skip
    def test_find_team_index(self):
        self.fail()
