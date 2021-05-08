// SPDX-License-Identifier: AGPL-3.0

pragma solidity 0.6.12;
pragma experimental ABIEncoderV2;

interface IRariETHFundManager {

    /**
     * @dev Contract of the RariFundToken.
     */
    function rariFundToken() external view returns(address);

    /**
     * @notice Returns the fund's total investor balance (all RFT holders' funds but not unclaimed fees) of all currencies in USD (scaled by 1e18).
     * @dev Ideally, we can add the `view` modifier, but Compound's `getUnderlyingBalance` function (called by `getRawFundBalance`) potentially modifies the state.
     */
    function getFundBalance() external returns (uint256);

     /**
     * @notice Returns the total amount of interest accrued by past and current RFT holders (excluding the fees paid on interest) in USD (scaled by 1e18).
     * @dev Ideally, we can add the `view` modifier, but Compound's `getUnderlyingBalance` function (called by `getRawFundBalance`) potentially modifies the state.
     */
    function getInterestAccrued() external returns (int256);

     /**
     * @dev Returns the interest fee rate (proportion of interest accrued that is taken as a service fee (scaled by 1e18)).
     */
    function getInterestFeeRate() external view returns (uint256);  

     /**
     * @notice Returns the amount of interest fees accrued by beneficiaries in USD (scaled by 1e18).
     * @dev Ideally, we can add the `view` modifier, but Compound's `getUnderlyingBalance` function (called by `getRawFundBalance`) potentially modifies the state.
     */
    function getInterestFeesGenerated() external returns (int256);
   
     /**
     * @notice Returns the total balance in USD (scaled by 1e18) of `account`.
     * @dev Ideally, we can add the `view` modifier, but Compound's `getUnderlyingBalance` function (called by `getRawFundBalance`) potentially modifies the state.
     * @param account The account whose balance we are calculating.
     */
    function balanceOf(address account) external returns (uint256);


    /**
     * @notice Deposits ETH to RariFund in exchange for REPT
     * @return Boolean indicating success.
     */
    function deposit() external payable returns (bool);

    /**
     * @notice Deposits funds from `msg.sender` (RariFundProxy) to RariFund in exchange for REPT minted to `to`.
     * @return Boolean indicating success.
     */
    function depositTo(address to) external payable returns (bool);

    /**
     * @notice Withdraws funds from RariFund in exchange for REPT.
     * You may only withdraw currencies held by the fund (see `getRawFundBalance(string currencyCode)`).
     * Please note that you must approve RariFundManager to burn of the necessary amount of REPY.
     * @param amount The amount of tokens to be withdrawn.
     * @return Boolean indicating success.
     */
    function withdraw(uint256 amount) external returns (bool);

    /**
     * @dev Withdraws funds from RariFund to `msg.sender` (RariFundProxy) in exchange for REPT burned from `from`.
     * Please note that you must approve RariFundManager to burn of the necessary amount of REPT.
     * @param from The address from which REPT will be burned.
     * @param amount The amount of tokens to be withdrawn.
     * @return Boolean indicating success.
     */
    function withdrawFrom(address from, uint256 amount) external returns (bool);
    
}
