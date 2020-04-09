from django.test import TestCase

from resource_hub.core.models import Contract

# from django.contrib.auth.models import User
# from django.utils.dateparse import parse_date

# from . import create_test_users


# class TestUser(TestCase):
#     @classmethod
#     def setUpTestData(cls):
#         create_test_users()

#     def test_person_first_name(self):
#         user = User.objects.get(username='testmate')
#         first_name = user.first_name
#         self.assertEqual('Test', first_name)

class TestContract(TestCase):
    def setUp(self):

        self.contract = Contract()

    def test_legal_moves(self):
        for node, edges in Contract.STATE_GRAPH.items():
            for other_node in edges:
                self.contract.state = node
                self.contract.move_to(other_node)
                self.assertEqual(self.contract.state, other_node)

    def test_illegal_moves(self):
        state = Contract.STATE
        moves = [
            (state.INIT, state.FINALIZED),
            (state.INIT, state.RUNNING),
            (state.RUNNING, state.CANCELED),
        ]
        for edge in moves:
            self.contract.state = edge[0]
            self.assertRaises(
                ValueError,
                self.contract.move_to, edge[1]
            )
