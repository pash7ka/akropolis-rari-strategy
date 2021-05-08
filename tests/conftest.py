import pytest
from brownie import config
from brownie import interface
from brownie import Contract


#@pytest.fixture(params=["stable", "yield", "ethereum"])
@pytest.fixture(params=["stable", "yield"])
def rariPoolType(request):
    yield request.param

@pytest.fixture
def rari(rariPoolType):
    rariPoolOptions = {
        "stable": {
            "fundManager":"0xC6BF8C8A55f77686720E0a88e2Fd1fEEF58ddf4a",
            "currencyCode":"USDC",
            "govToken":"0xD291E7a03283640FDc51b121aC401383A46cC623"
        },
        "yield": {
            "fundManager":"0x59FA438cD0731EBF5F4cDCaf72D4960EFd13FCe6",
            "currencyCode":"DAI",
            "govToken":"0xD291E7a03283640FDc51b121aC401383A46cC623"
        },
        "ethereum": {
            "fundManager":"0xD6e194aF3d9674b62D1b30Ec676030C23961275e",
            "currencyCode":"WETH",
            "govToken":"0xD291E7a03283640FDc51b121aC401383A46cC623"
        },
    }
    yield rariPoolOptions[rariPoolType]

@pytest.fixture
def protected_tokens(rari):
    rariFundManager = Contract(rari["fundManager"])
    rft = rariFundManager.rariFundToken()
    rgt = rari["govToken"]
    yield [rft, rgt]

@pytest.fixture
def uniswap():
    router_address = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"
    yield Contract(router_address)

@pytest.fixture
def gov(accounts):
    yield accounts.at("0xFEB4acf3df3cDEA7399794D0869ef76A6EfAff52", force=True)

@pytest.fixture
def user(accounts):
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
def token(rari):
    tokensForPool = {
        "DAI":  "0x6b175474e89094c44da98b954eedeac495271d0f",
        "USDC": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
        "WETH": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
    }
    currencyCode = rari["currencyCode"]
    token_address = tokensForPool[currencyCode]
    yield Contract(token_address)


@pytest.fixture
def reserve(accounts):
    # In order to get some funds for the token you are about to use,
    # it impersonate an exchange address to use it's funds.
    yield accounts.at("0xd551234ae421e3bcba99a0da6d736074f22192ff", force=True)

@pytest.fixture
def amount(accounts, token, user, reserve, rariPoolType):
    amount = 10_000 * 10 ** token.decimals()

    if rariPoolType == "ethereum":
        reserve.transfer(token, amount)     # transfer amount of ETH to WETH contract, this will return WETH to reserve
    
    token.transfer(user, amount, {"from": reserve})

    yield amount


@pytest.fixture
def weth():
    token_address = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
    yield Contract(token_address)

@pytest.fixture
def weth_amout(user, weth):
    weth_amout = 10 ** weth.decimals()
    user.transfer(weth, weth_amout)
    yield weth_amout


@pytest.fixture
def vault(pm, gov, rewards, guardian, management, token):
    Vault = pm(config["dependencies"][0]).Vault
    vault = guardian.deploy(Vault)
    vault.initialize(token, gov, rewards, "", "", guardian)
    vault.setDepositLimit(2 ** 256 - 1, {"from": gov})
    vault.setManagement(management, {"from": gov})
    yield vault


@pytest.fixture
def strategyContract(StableRariStrategy, YieldRariStrategy, EthRariStrategy, rariPoolType):
    strategyContracts = {
        "stable": StableRariStrategy,
        "yield": YieldRariStrategy,
        "ethereum": EthRariStrategy
    }
    yield strategyContracts[rariPoolType]

@pytest.fixture
def strategy(strategist, keeper, vault, strategyContract, gov, rari, uniswap, rariPoolType):
    strategy = strategist.deploy(strategyContract, vault)
    strategy.setKeeper(keeper)
    vault.addStrategy(strategy, 10_000, 0, 2 ** 256 - 1, 1_000, {"from": gov})

    strategy.setRari(rari["fundManager"], rari["currencyCode"], rari["govToken"], {"from": gov})
    strategy.setUniswap(uniswap, {"from": gov})

    yield strategy

@pytest.fixture
def rariFeeRate(rari, rariPoolType):
    if rariPoolType == 'ethereum':
        feeRate = 0
    else:
        fundManager = interface.IRariFundManager(rari["fundManager"])
        feeRate = fundManager.getWithdrawalFeeRate()
    
    yield feeRate

@pytest.fixture
def amountWithoutFee(rariFeeRate, amount):
    return amount * (1e18 - rariFeeRate) / 1e18

@pytest.fixture(scope="session")
def RELATIVE_APPROX():
    yield 1e-5
