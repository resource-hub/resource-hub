from ..jobs import settle_claims
from ..models import Claim, SettlementLog
from .test_models import BaseContractTest


class TestSettleClaims(BaseContractTest):
    def test_settle_claims(self):
        self.contract.settlement_logs.create()
        settle_claims()
        open_claims = self.contract.claim_set.filter(status=Claim.STATUS.OPEN)
        self.assertEqual(len(open_claims), self.no_of_claims//2)
        self.assertEqual(self.contract.state, self.contract.STATE.RUNNING)
