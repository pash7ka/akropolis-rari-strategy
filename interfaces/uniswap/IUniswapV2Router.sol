// SPDX-License-Identifier: AGPL-3.0

pragma solidity 0.6.12;

interface IUniswapV2Router {

    function WETH() external view returns(address);

    function swapExactTokensForTokens(
    uint amountIn,
    uint amountOutMin,
    address[] calldata path,
    address to,
    uint deadline
    ) external returns (uint[] memory amounts);

    function swapTokensForExactTokens(
    uint amountOut,
    uint amountInMax,
    address[] calldata path,
    address to,
    uint deadline
    ) external returns (uint[] memory amounts);

}
