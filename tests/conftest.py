import pytest
from brownie import config
from brownie import interface
from brownie import Contract

@pytest.fixture
def rari():
    yield {
        "fundManager":"0x59fa438cd0731ebf5f4cdcaf72d4960efd13fce6",
        "currencyCode":"DAI",
        "govToken":"0xD291E7a03283640FDc51b121aC401383A46cC623"
    }

@pytest.fixture
def uniswap():
    yield {
        "router":"0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"
    }

@pytest.fixture
def gov(accounts):
    yield accounts[0]


@pytest.fixture
def rewards(accounts):
    yield accounts[1]


@pytest.fixture
def guardian(accounts):
    yield accounts[2]


@pytest.fixture
def management(accounts):
    yield accounts[3]


@pytest.fixture
def strategist(accounts):
    yield accounts[4]


@pytest.fixture
def keeper(accounts):
    yield accounts[5]


@pytest.fixture
def token():
    token_address = "0x6b175474e89094c44da98b954eedeac495271d0f"  # this should be the address of the ERC-20 used by the strategy/vault (DAI)
    yield Contract(token_address)


@pytest.fixture
def amount(accounts, token):
    amount = 10_000 * 10 ** token.decimals()
    # In order to get some funds for the token you are about to use,
    # it impersonate an exchange address to use it's funds.
    reserve = accounts.at("0xd551234ae421e3bcba99a0da6d736074f22192ff", force=True)
    token.transfer(accounts[0], amount, {"from": reserve})
    yield amount


@pytest.fixture
def weth():
    token_address = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
    yield Contract(token_address)


@pytest.fixture
def weth_amount(gov, weth):
    weth_amount = 10 ** weth.decimals()
    gov.transfer(weth, weth_amount)
    yield weth_amount


@pytest.fixture
def vault(pm, gov, rewards, guardian, management, token):
    Vault = pm(config["dependencies"][0]).Vault
    vault = guardian.deploy(Vault)
    vault.initialize(token, gov, rewards, "", "", guardian)
    vault.setDepositLimit(2 ** 256 - 1, {"from": gov})
    vault.setManagement(management, {"from": gov})
    yield vault


@pytest.fixture
def strategy(strategist, keeper, vault, Strategy, gov, rari, uniswap):
    strategy = strategist.deploy(Strategy, vault)
    strategy.setKeeper(keeper)
    vault.addStrategy(strategy, 10_000, 0, 2 ** 256 - 1, 1_000, {"from": gov})

    strategy.setRari(rari["fundManager"], rari["currencyCode"], rari["govToken"], {"from": gov})
    strategy.setUniswap(uniswap["router"], {"from": gov})

    yield strategy

@pytest.fixture
def rariFeeRate(rari):
    fundManager = interface.IRariFundManager(rari["fundManager"])
    feeRate = fundManager.getWithdrawalFeeRate()
    yield feeRate

@pytest.fixture
def amountWithoutFee(rariFeeRate, amount):
    return amount * (1e18 - rariFeeRate) / 1e18

@pytest.fixture(scope="session")
def RELATIVE_APPROX():
    yield 1e-5
