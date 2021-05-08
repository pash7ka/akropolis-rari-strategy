// SPDX-License-Identifier: AGPL-3.0

pragma solidity 0.6.12;
pragma experimental ABIEncoderV2;

interface IRariFundManager {

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
     * @dev Returns the fee rate on interest (proportion of raw interest accrued scaled by 1e18).
     */
    function getInterestFeeRate() external view returns (uint256);

     /**
     * @notice Returns the amount of interest fees accrued by beneficiaries in USD (scaled by 1e18).
     * @dev Ideally, we can add the `view` modifier, but Compound's `getUnderlyingBalance` function (called by `getRawFundBalance`) potentially modifies the state.
     */
    function getInterestFeesGenerated() external returns (int256);

     /**
     * @dev Returns the withdrawal fee rate (proportion of every withdrawal taken as a service fee scaled by 1e18).
     */
    function getWithdrawalFeeRate() external view returns (uint256);  
    
     /**
     * @notice Returns the total balance in USD (scaled by 1e18) of `account`.
     * @dev Ideally, we can add the `view` modifier, but Compound's `getUnderlyingBalance` function (called by `getRawFundBalance`) potentially modifies the state.
     * @param account The account whose balance we are calculating.
     */
    function balanceOf(address account) external returns (uint256);


    /**
     * @notice Deposits funds to the Rari Yield Pool in exchange for RFT.
     * You may only deposit currencies accepted by the fund (see `isCurrencyAccepted(string currencyCode)`).
     * Please note that you must approve RariFundManager to transfer at least `amount`.
     * @param currencyCode The currency code of the token to be deposited.
     * @param amount The amount of tokens to be deposited.
     */
    function deposit(string calldata currencyCode, uint256 amount) external;

    /**
     * @notice Deposits funds from `msg.sender` to the Rari Yield Pool in exchange for RFT minted to `to`.
     * You may only deposit currencies accepted by the fund (see `isCurrencyAccepted(string currencyCode)`).
     * Please note that you must approve RariFundManager to transfer at least `amount`.
     * @param to The address that will receieve the minted RFT.
     * @param currencyCode The currency code of the token to be deposited.
     * @param amount The amount of tokens to be deposited.
     */
    function depositTo(address to, string calldata currencyCode, uint256 amount) external;

     /**
     * @notice Withdraws funds from the Rari Yield Pool in exchange for RFT.
     * You may only withdraw currencies held by the fund (see `getRawFundBalance(string currencyCode)`).
     * Please note that you must approve RariFundManager to burn of the necessary amount of RFT.
     * @param currencyCode The currency code of the token to be withdrawn.
     * @param amount The amount of tokens to be withdrawn.
     * @return The amount withdrawn after the fee.
     */
    function withdraw(string calldata currencyCode, uint256 amount) external returns (uint256);

    /**
     * @dev Withdraws multiple currencies from the Rari Yield Pool to `msg.sender` (RariFundProxy) in exchange for RFT burned from `from`.
     * You may only withdraw currencies held by the fund (see `getRawFundBalance(string currencyCode)`).
     * Please note that you must approve RariFundManager to burn of the necessary amount of RFT.
     * @param from The address from which RFT will be burned.
     * @param currencyCodes The currency codes of the tokens to be withdrawn.
     * @param amounts The amounts of the tokens to be withdrawn.
     * @return Array of amounts withdrawn after fees.
     */
    function withdrawFrom(address from, string[] calldata currencyCodes, uint256[] calldata amounts) external returns (uint256[] memory);

}
