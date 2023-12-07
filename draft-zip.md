```
ZIP: 
Title: Deposit 60% of transaction fees to the Zcash Sustainability Fund
Owners: Jason McGee <jason@shieldedlabs.com>
        Mark Henderson <mark@equilibrium.co>
        Tomek Piotrowski <tomek@eiger.co>
        Mariusz Pilarek <mariusz@eiger.co>
Original-Authors: Nathan Wilcox
Credits:
Status: Draft
Category: Ecosystem
Created: 2023-09-21
License: BSD-2-Clause
```

# Terminology

The key words “MUST”, “SHOULD”, “SHOULD NOT”, “MAY”, “RECOMMENDED”, “OPTIONAL”, and “REQUIRED” in this document are to be interpreted as described in RFC 2119. [1]

The term “network upgrade” in this document is to be interpreted as described in ZIP 200. [2]

The term “Block Rewards” in this document is to be interpreted as described in ZIP TBD [3]

The term “Issuance” in this document is to be interpreted as described in ZIP TBD [3]

“We” - the ZIP authors, owners listed in the above front matter

“`ZSF_BALANCE_AFTER[h]`” is balance of the Zcash Sustainability Fund as defined in ZIP ###

# Abstract

This ZIP proposes a modification to transaction fees, diverting 60% of transaction fees back into the `ZSF_BALANCE_AFTER[h]`, while  the destination of the remaining 40% is unchanged and goes to the block miner. This proposal effectively “unmints” a portion of transaction fees, contributing to a deflationary effect and offering long-term support for the Zcash network.

This ZIP attempts to establish a symbiotic relationship between miner incentives and sustained network growth. It achieves this by splitting transaction fees: 40% goes directly to miners, incentivizing them to include transactions, while the remaining 60% is deposited into the  `ZSF_BALANCE_AFTER[h]`. This approach mitigates a "bootstrapping problem", a problem that arises when 100% of transaction fees go to the ZSF and miners are not incentivized to include transactions in block. This ZIP navigates this problem by ensuring miners continue to receive direct rewards for including transactions, while still contributing to the ZSF.

Implementing this change allows the ZSF to accrue value earlier. By ensuring a consistent source of funding, the ZSF contributes to bolstering the Zcash network’s long-term security and sustainability.

This ZIP depends on the ZIP introducing the Zcash Sustainability Fund (ZIP-XXX). This ZIP does not by itself introduce any use for the fees added to the ZSF. This could be introduced via subsidy smoothing (ZIP-YYY), or some other mechanism.

# Motivation

While ZIP-XXX (Establishing the Zcash Sustainability Fund) describes a method by which funds can be added to the Zcash Sustainability Fund by a voluntary `ZSF_DEPOSIT` transaction field. The default value of this field is zero and it is left up to the app, wallet, and mining software implementers to make use of it.

This ZIP takes a much more explicit and non-optional approach, mandating at the protocol level that 60% of transaction fees be deposited into the ZSF. As noted above, implementing this change allows the ZSF to accrue value earlier and contribute to future network sustainability.

If ZIPs ### and ### are accepted, the system looks something like this:

At Every New Block:
- `ZSF_DEPOSIT` amount is deposited into the ZSF
- Block rewards come from the ZSF
- Transaction fees (inputs - outputs) paid to miner

After the features described in this ZIP are activated (changed parts in bold):

At Every New Block:
- `ZSF_DEPOSIT` amount is deposited into the ZSF
- Block rewards come from the ZSF
- **40% of transaction fees (inputs - outputs) paid to miner**
- **60% of transaction fees (inputs - outputs) deposited into the ZSF**

This has a multitude of benefits:

1. **Network Sustainability**: This mechanism involves temporarily reducing the supply of ZEC similar to asset burning in Ethereum’s EIP-1559, but with potential long-term sustainability benefits as the redistribution of deposits contributes to issuance rewards and network development, making it an attractive option for current and future Zcash users.
2. **Ecosystem Benefits of Longer Time Horizons**: A reliable and long-term functioning Zcash blockchain allows users to make secure long-term plans, leading to a sustainable and virtuous adoption cycle, rather than being influenced by short-term trends.
3. **Incentivizing Transaction Inclusion**: By providing a 40% share of transaction fees to miners, this ZIP maintains incentives for miners to prioritize including transactions in their blocks. This helps ensure the efficient processing of transactions and supports a robust and responsive network.
4. **Future-Proofing the Network**: Diverting transaction fees into the ZSF is a forward-looking approach that prepares the Zcash network for future challenges and opportunities. It establishes a financial buffer that can be instrumental in addressing unforeseen issues and seizing strategic advantages as the Zcash ecosystem evolves.

# Requirements

- For each block, at least 60% (rounded down) of the total fees are be paid to the ZSF.
- No restrictions are placed on the destination of the remaining proportion of fees.
- Any fractions are rounded in favour of the miner.

# Specification

## Consensus Rule Changes

The coinbase transaction at block height `height` MUST have a `zsfDeposit` that is greater than or equal to `floor(TransactionFees(height) * 6 / 10)`, where `TransactionFees(height)` is the sum of the the remaining value in the transparent transaction value pool of the non-coinbase transactions in the block at `height`.

TODO ZIP Editors:
- work out how to deal with pre-v6 transactions which don't have the zsfDeposit() field. For example, by requiring the remaining value in the transparent transaction value pool of a coinbase transaction to be greater than or equal to 60% of the fee
- consider imposing this requirement on v6 transactions instead of an explicit `ZSF_DEPOSIT` field requirement
- work out the necessary protocol spec changes.

# Deployment

The implementation of this ZIP MUST be deployed at the same time or after the Zcash Sustainability Fund (ZIP-XXX), and subsidy smoothing  (ZIP-YYY).

# Rationale

We believe that the change made by this ZIP is ultimately a very minor change to the protocol, and quite simple in terms of implementation overhead. Additionally – and at the time of this writing – transaction fees are so small that 60% will likely not have a major impact.

If transaction fees were to increase, future ZIPs can be written to change the 60%/40% split. Finding the optimal fee split may require an iterative approach involving adjustments based on real-world data and network dynamics.

In the future, other ZIPs may be written to fund the ZSF in various ways, including but not limited to:
- ZSA fees
- dApp-specific fees and donations
- “Storage fees” for any future data availability
- Cross-chain bridge usage / Cross-chain messaging
- Note sorting micro-transactional fees

## Estimated impact on miners

Over 105,120 blocks starting at block 2216606, there were 344,647 transactions with an average of 20.18 logical actions (see ZIP-317 [4]). The total fees paid to miners, assuming the ZIP-317 regime, would be 336.50 ZEC.
105,120 blocks is approximately 3 months of blocks. Extrapolating to a year, we would expect 1,346.00 ZEC in fees paid to miners. If 60% of these fees were diverted to the ZSF, that would be 807.60 ZEC per year. [5]

## Future Implications

Looking into the future, there may come a time when the transaction fees become greater than the block reward issuance. At that time we may need to reconsider the 60/40 split. However, this will likely not be the case for the next 8-10 years due to forcasts based on issuance models and network traffic.

# References

[1] RFC-2119: https://datatracker.ietf.org/doc/html/rfc2119

[2] ZIP 200: https://zips.z.cash/zip-0200

[3] ZIP TBD: The Zcash Sustainability Fund ZIP (Placeholder)

[4] ZIP 317: https://zips.z.cash/zip-0317

[5] https://github.com/eigerco/zsf-fee-estimator