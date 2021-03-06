import brownie
from brownie import Contract
import pytest


def test_operation(
    accounts, token, vault, strategy, strategist, user, amount, RELATIVE_APPROX, amountWithoutFee
):
    # Deposit to the vault
    token.approve(vault.address, amount, {"from": user})
    vault.deposit(amount, {"from": user})
    assert token.balanceOf(vault.address) == amount

    # harvest
    strategy.harvest()
    assert pytest.approx(strategy.estimatedTotalAssets(), rel=RELATIVE_APPROX) == amountWithoutFee

    # tend()
    strategy.tend()

    # withdrawal
    shares = vault.balanceOf(user)
    vault.withdraw(shares, user, 50, {"from": user})
    assert pytest.approx(token.balanceOf(user), rel=RELATIVE_APPROX) == amountWithoutFee


def test_emergency_exit(
    accounts, token, vault, strategy, strategist, user, amount, RELATIVE_APPROX, amountWithoutFee
):
    # Deposit to the vault
    token.approve(vault.address, amount, {"from": user})
    vault.deposit(amount, {"from": user})
    strategy.harvest()
    assert pytest.approx(strategy.estimatedTotalAssets(), rel=RELATIVE_APPROX) == amountWithoutFee

    # set emergency and exit
    strategy.setEmergencyExit()
    strategy.harvest()
    assert strategy.estimatedTotalAssets() < amount


def test_profitable_harvest(
    accounts, token, vault, strategy, user, strategist, gov, amount, RELATIVE_APPROX, chain, amountWithoutFee, reserve, weth, uniswap, rari
):
    # Deposit to the vault
    token.approve(vault.address, amount, {"from": user})
    vault.deposit(amount, {"from": user})
    assert token.balanceOf(vault.address) == amount

    # Harvest 1: Send funds through the strategy
    strategy.harvest()
    assert pytest.approx(strategy.estimatedTotalAssets(), rel=RELATIVE_APPROX) == amountWithoutFee
    before_pps = vault.pricePerShare()

    # Add some code before harvest #2 to simulate earning yield
    # We are simulating RGT yield distributed to strategy
    eth_profit_amount = 2*1e18
    token.transfer(user, amount, {"from": reserve})
    uniswap.swapExactETHForTokens(0, [weth, rari["govToken"]], strategy, (chain[-1]["timestamp"]+300), {"amount":eth_profit_amount, "from":reserve})
    rgt = Contract(rari["govToken"])
    assert rgt.balanceOf(strategy) > 0

    # Harvest 2: Realize profit
    strategy.harvest()
    chain.sleep(3600 * 6)  # 6 hrs needed for profits to unlock
    chain.mine(1)    
    profit = token.balanceOf(vault.address)  # Profits go to vault

    assert strategy.estimatedTotalAssets() + profit > amount
    assert vault.pricePerShare() > before_pps

    # Check that we can actually return to the vault more than was deposited
    vault.updateStrategyDebtRatio(strategy.address, 0, {"from": gov})   # Order Strategy to return everything to vault
    strategy.harvest()
    assert token.balanceOf(vault.address) > amount


def test_change_debt(
    gov, token, vault, strategy, strategist, user, amount, RELATIVE_APPROX, rariFeeRate, amountWithoutFee
):
    # Deposit to the vault and harvest
    token.approve(vault.address, amount, {"from": user})
    vault.deposit(amount, {"from": user})
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
    fivekWithoutTenKFee = ((10_000 * (1e18 - rariFeeRate) / 1e18) - 5000)*(10**token.decimals())
    # accuracy is reduces for this test because some unknown yield may be received during the test
    assert pytest.approx(strategy.estimatedTotalAssets(), rel=1e-4) == fivekWithoutTenKFee


def test_sweep(gov, vault, strategy, token, user, amount, weth, weth_amout, protected_tokens):
    # Strategy want token doesn't work
    token.transfer(strategy, amount, {"from": user})
    assert token.address == strategy.want()
    assert token.balanceOf(strategy) > 0
    with brownie.reverts("!want"):
        strategy.sweep(token, {"from": gov})

    # Vault share token doesn't work
    with brownie.reverts("!shares"):
        strategy.sweep(vault.address, {"from": gov})

    # Protected token doesn't work
    for protectedToken in protected_tokens:
        with brownie.reverts("!protected"):
            strategy.sweep(protectedToken, {"from": gov})

    before_balance = weth.balanceOf(gov)
    weth.transfer(strategy, weth_amout, {"from": user})
    assert weth.address != strategy.want()
    assert weth.balanceOf(user) == 0
    strategy.sweep(weth, {"from": gov})
    assert weth.balanceOf(gov) == weth_amout + before_balance


def test_triggers(
    gov, vault, strategy, token, amount, user, weth, weth_amout, strategist
):
    # Deposit to the vault and harvest
    token.approve(vault.address, amount, {"from": user})
    vault.deposit(amount, {"from": user})
    vault.updateStrategyDebtRatio(strategy.address, 5_000, {"from": gov})
    strategy.harvest()

    strategy.harvestTrigger(0)
    strategy.tendTrigger(0)