// SPDX-License-Identifier: AGPL-3.0

pragma solidity 0.6.12;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

interface WETH is IERC20 {
	function deposit() external payable;
    function withdraw(uint wad) external;
}