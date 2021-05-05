// SPDX-License-Identifier: AGPL-3.0
pragma solidity 0.6.12;
pragma experimental ABIEncoderV2;

import  "../interfaces/rari/IRariGovernanceTokenDistributor.sol";
import  "../interfaces/rari/IRariETHFundManager.sol";
import  "../interfaces/WETH.sol";
import  "./BaseRariStrategy.sol";

contract EthRariStrategy is BaseRariStrategy {
    constructor(address _vault) public BaseRariStrategy(_vault) {
    }

    function rariPoolType() internal override returns(IRariGovernanceTokenDistributor.RariPool) {
        return IRariGovernanceTokenDistributor.RariPool.Ethereum;
    }

    function withdrawalFee(uint256 usdAmount) internal override returns(uint256) {
        return 0;
    }

    function rariDeposit(uint256 amount) internal override {
        WETH(address(want)).withdraw(amount);
        IRariETHFundManager(address(rari)).deposit{value: amount}();
    }

    function rariWithdraw(uint256 amount) internal override {
        IRariETHFundManager(address(rari)).withdraw(amount);
        WETH(address(want)).deposit{value: amount}();
    }

    function swapRGT() internal override {
        uint256 rgtBalance = rariGovToken.balanceOf(address(this));
        if(rgtBalance == 0) return;

        address[] memory path = new address[](2);

        path[0] = address(rariGovToken);
        path[1] = address(weth);
        uniswap.swapExactTokensForTokens(rgtBalance, 0, path, address(this), block.timestamp);
    }

}
