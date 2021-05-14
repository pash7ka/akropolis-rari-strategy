# Rari Strategy for Yearn Vaults

## Description
This strategy is based on [Yearn Strategy Brownie Mix](https://github.com/yearn/brownie-strategy-mix/tree/99aba02f6ef83054d73629d850ab2ac5333d330b) and extends [BaseStrategy](https://github.com/yearn/yearn-vaults/blob/v0.3.5/contracts/BaseStrategy.sol).

It support [Rari Capital](https://rari.capital) [Stable](https://app.rari.capital/pools/stable) and [Yield](https://app.rari.capital/pools/stable) pools and can be added to USDC (Rari Stable Pool) and DAI, USDC, USDT, mUSD (Rari Yield Pool) Yearn vaults.

## Rari Pools addresses
Rari Stable Pool Fund Manager Proxy: [0xC6BF8C8A55f77686720E0a88e2Fd1fEEF58ddf4a](https://etherscan.io/address/0xC6BF8C8A55f77686720E0a88e2Fd1fEEF58ddf4a#readProxyContract)

Rari Stable Pool (RSPT) Token Proxy: [0x016bf078ABcaCB987f0589a6d3BEAdD4316922B0](https://etherscan.io/address/0x016bf078abcacb987f0589a6d3beadd4316922b0#readProxyContract)

Rari Yield Pool Fund Manager Proxy: [0x59FA438cD0731EBF5F4cDCaf72D4960EFd13FCe6](https://etherscan.io/address/0x59FA438cD0731EBF5F4cDCaf72D4960EFd13FCe6#readProxyContract)

Rari Yield Pool (RYPT) Token Proxy: [0x3baa6B7Af0D72006d3ea770ca29100Eb848559ae](https://etherscan.io/address/0x3baa6b7af0d72006d3ea770ca29100eb848559ae#readProxyContract)

RariGovernanceTokenDistributor Proxy: [0x9C0CaEb986c003417D21A7Daaf30221d61FC1043](https://etherscan.io/address/0x9c0caeb986c003417d21a7daaf30221d61fc1043#readProxyContract)

Rari Governance Token (RGT) Proxy: [0xD291E7a03283640FDc51b121aC401383A46cC623](https://etherscan.io/address/0xD291E7a03283640FDc51b121aC401383A46cC623#code)

## Strategy workflow
- When `adjustPosition()` is called and some `want` tokens are available, startegy deposits them to the Rari pool and receives corresponding RSPT/RYPT token, which corresponds to startegy's share in the pool.
- When `liquidatePosition()` is called strategy claims RGT tokens ans swaps the to `want` using Uniswap V2 and if more `want` has to be returned, it withdraws from the rari pool. Note: Rari pool may take withdrawal fee, wich is currently zero for Stable pool and 0.5% for Yield pool. Also interest fee is applied to yileds transparently for the startegy. Ocasionally the startegy may report some loss because of this withdrawal fee.
- When `prepareReturn()` is called, strategy basically does same thing as with `liquidatePosition()`.
- After each call to above methods startegy updates it's stored estimated funds, because during `estimatedTotalAssets()` call this information from Rari pools is not available since they require non-static call to get balance.

## Contract structure
There is a base contract for all pools: [BaseRariStrategy](/contracts/BaseRariStrategy.sol) which is extended by [StableRariStrategy](/contracts/StableRariStrategy.sol) for Stable pool and [YieldRariStrategy](/contracts/YieldRariStrategy.sol) for Yield pool.

## Deployment
1. Deploy [StableRariStrategy] or [YieldRariStrategy] 
2. Call `setRari()` to set address of Fund Manager, RGT and symbol of the `want` currency
3. Call `setUniswap()` to set address of Uniswap controller used to swap RGT







