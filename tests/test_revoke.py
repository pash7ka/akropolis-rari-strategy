import pytest

def test_revoke_strategy_from_vault(
    token, vault, strategy, amount, user, gov, RELATIVE_APPROX, amountWithoutFee
):
    # Deposit to the vault and harvest
    token.approve(vault.address, amount, {"from": user})
    vault.deposit(amount, {"from": user})
    strategy.harvest()
    assert pytest.approx(strategy.estimatedTotalAssets(), rel=RELATIVE_APPROX) == amountWithoutFee

    # In order to pass this tests, you will need to implement prepareReturn.
    vault.revokeStrategy(strategy.address, {"from": gov})
    strategy.harvest()
    assert pytest.approx(token.balanceOf(vault.address), rel=RELATIVE_APPROX) == amountWithoutFee


def test_revoke_strategy_from_strategy(
    token, vault, strategy, amount, user, gov, RELATIVE_APPROX, amountWithoutFee
):
    # Deposit to the vault and harvest
    token.approve(vault.address, amount, {"from": user})
    vault.deposit(amount, {"from": user})
    strategy.harvest()
    assert pytest.approx(strategy.estimatedTotalAssets(), rel=RELATIVE_APPROX) == amountWithoutFee

    strategy.setEmergencyExit()
    strategy.harvest()
    assert pytest.approx(token.balanceOf(vault.address), rel=RELATIVE_APPROX) ==amountWithoutFee
