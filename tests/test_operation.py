import brownie
from brownie import Contract
import pytest


def test_operation(
    accounts, token, vault, strategy, strategist, amount, RELATIVE_APPROX, amountWithoutFee
):
    # Deposit to the vault
    token.approve(vault.address, amount, {"from": accounts[0]})
    vault.deposit(amount, {"from": accounts[0]})
    assert token.balanceOf(vault.address) == amount

    # harvest
    strategy.harvest()
    assert pytest.approx(strategy.estimatedTotalAssets(), rel=RELATIVE_APPROX) == amountWithoutFee

    # tend()
    strategy.tend()

    # withdrawal
    shares = vault.balanceOf(accounts[0])
    vault.withdraw(shares, accounts[0], 50, {"from": accounts[0]})
    assert pytest.approx(token.balanceOf(accounts[0]), rel=RELATIVE_APPROX) == amountWithoutFee


def test_emergency_exit(
    accounts, token, vault, strategy, strategist, amount, RELATIVE_APPROX, amountWithoutFee
):
    # Deposit to the vault
    token.approve(vault.address, amount, {"from": accounts[0]})
    vault.deposit(amount, {"from": accounts[0]})
    strategy.harvest()
    assert pytest.approx(strategy.estimatedTotalAssets(), rel=RELATIVE_APPROX) == amountWithoutFee

    # set emergency and exit
    strategy.setEmergencyExit()
    strategy.harvest()
    assert strategy.estimatedTotalAssets() < amount


def test_profitable_harvest(
    accounts, token, vault, strategy, strategist, amount, RELATIVE_APPROX, amountWithoutFee
):
    # Deposit to the vault
    token.approve(vault.address, amount, {"from": accounts[0]})
    vault.deposit(amount, {"from": accounts[0]})
    assert token.balanceOf(vault.address) == amount

    # harvest
    strategy.harvest()
    assert pytest.approx(strategy.estimatedTotalAssets(), rel=RELATIVE_APPROX) == amountWithoutFee

    # You should test that the harvest method is capable of making a profit.
    # TODO: uncomment the following lines.
    # strategy.harvest()
    # chain.sleep(3600 * 24)
    # assert pytest.approx(strategy.estimatedTotalAssets(), rel=RELATIVE_APPROX) == amount
    # assert token.balanceOf(vault.address) > 0


def test_change_debt(
    gov, token, vault, strategy, strategist, amount, RELATIVE_APPROX, rariFeeRate, amountWithoutFee
):
    # Deposit to the vault and harvest
    token.approve(vault.address, amount, {"from": gov})
    vault.deposit(amount, {"from": gov})
    vault.updateStrategyDebtRatio(strategy.address, 5_000, {"from": gov})
    strategy.harvest()
    half = int(amountWithoutFee / 2)

    assert pytest.approx(strategy.estimatedTotalAssets(), rel=RELATIVE_APPROX) == half

    vault.updateStrategyDebtRatio(strategy.address, 10_000, {"from": gov})
    strategy.harvest()
    assert pytest.approx(strategy.estimatedTotalAssets(), rel=RELATIVE_APPROX) == amountWithoutFee

    # With this sequence we first deposit 10k, then withdraw 5k. So the whole fee is taken from 10k
    vault.updateStrategyDebtRatio(strategy.address, 5_000, {"from": gov})
    strategy.harvest()
    fivekWithoutTenKFee = ((10_000 * (1e18 - rariFeeRate) / 1e18) - 5000)*1e18
    assert pytest.approx(strategy.estimatedTotalAssets(), rel=1e-4) == fivekWithoutTenKFee


def test_sweep(gov, vault, strategy, token, amount, weth, weth_amount):
    # Strategy want token doesn't work
    token.transfer(strategy, amount, {"from": gov})
    assert token.address == strategy.want()
    assert token.balanceOf(strategy) > 0
    with brownie.reverts("!want"):
        strategy.sweep(token, {"from": gov})

    # Vault share token doesn't work
    with brownie.reverts("!shares"):
        strategy.sweep(vault.address, {"from": gov})

    # TODO: If you add protected tokens to the strategy.
    # Protected token doesn't work
    # with brownie.reverts("!protected"):
    #     strategy.sweep(strategy.protectedToken(), {"from": gov})

    weth.transfer(strategy, weth_amount, {"from": gov})
    assert weth.address != strategy.want()
    assert weth.balanceOf(gov) == 0
    strategy.sweep(weth, {"from": gov})
    assert weth.balanceOf(gov) == weth_amount


def test_triggers(gov, vault, strategy, token, amount, weth, weth_amount):
    # Deposit to the vault and harvest
    token.approve(vault.address, amount, {"from": gov})
    vault.deposit(amount, {"from": gov})
    vault.updateStrategyDebtRatio(strategy.address, 5_000, {"from": gov})
    strategy.harvest()

    strategy.harvestTrigger(0)
    strategy.tendTrigger(0)
