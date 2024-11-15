"""
abstract: Minimal test example
    Simple state test using minimal components.

"""
import pytest

from ethereum_test_tools import Account, Alloc
from ethereum_test_tools import Opcodes as Op
from ethereum_test_tools import StateTestFiller, Transaction

pytestmark = pytest.mark.valid_from("Cancun")


def test_simple(
    state_test: StateTestFiller,
    pre: Alloc,
):
    """
    Minimal test using a single transaction and a single storage check.
    """
    # Deploy the contract.
    contract_address_2 = pre.deploy_contract(Op.SSTORE(0, 1) + Op.STOP)
    contract_address_1 = pre.deploy_contract(Op.CALL(address=contract_address_2) + Op.STOP)

    # Fund the sender of the transaction.
    sender = pre.fund_eoa()

    # Craft the transaction.
    tx = Transaction(
        to=contract_address_1,
        sender=sender,
        gas_limit=100_000,
        value=1,
    )

    # Check the post state was updated
    post = {
        contract_address_2: Account(
            balance=0,
            storage={0: 1},
        ),
    }

    # Fill the state test.
    state_test(
        pre=pre,
        tx=tx,
        post=post,
    )