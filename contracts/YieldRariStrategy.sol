// SPDX-License-Identifier: AGPL-3.0
pragma solidity 0.6.12;
pragma experimental ABIEncoderV2;

import  "../interfaces/rari/IRariGovernanceTokenDistributor.sol";
import  "./BaseRariStrategy.sol";

contract YieldRariStrategy is BaseRariStrategy {
    constructor(address _vault) public BaseRariStrategy(_vault) {
    }

    function rariPoolType() internal override returns(IRariGovernanceTokenDistributor.RariPool) {
        return IRariGovernanceTokenDistributor.RariPool.Yield;
    }
}
