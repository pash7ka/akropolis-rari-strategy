# TODO: Add tests that show proper migration of the strategy to a newer one
#       Use another copy of the strategy to simulate the migration
#       Show that nothing is lost!

import pytest

def test_migration(
    token, vault, strategy, amount, Strategy, strategist, gov, RELATIVE_APPROX, amountWithoutFee, rari, uniswap, rariFeeRate,
):
    # Deposit to the vault and harvest
    token.approve(vault.address, amount, {"from": gov})
    vault.deposit(amount, {"from": gov})
    strategy.harvest()
    assert pytest.approx(strategy.estimatedTotalAssets(), rel=RELATIVE_APPROX) == amountWithoutFee

    # migrate to a new strategy
    new_strategy = strategist.deploy(Strategy, vault)
    new_strategy.setRari(rari["fundManager"], rari["currencyCode"], rari["govToken"], {"from": gov})
    new_strategy.setUniswap(uniswap["router"], {"from": gov})


    strategy.migrate(new_strategy.address, {"from": gov})
    new_strategy.updateStoredDepositedBalance()

    assert (
        pytest.approx(new_strategy.estimatedTotalAssets(), rel=RELATIVE_APPROX) == amountWithoutFee
    )
