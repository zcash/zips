```
ZIP: unassigned
Title: Comparable-based Fee Market
Owners: Mark Henderson <mark@shieldedlabs.net>
        Zooko Wilcox <zooko@shieldedlabs.net>
        Nathan Wilcox <nate@shieldedlabs.net>
Status: Draft
Category: Consensus / Standards
Created: 2026-01-11
License: MIT 
```

# Terminology

The key words "SHOULD", and "MUST" in this document
are to be interpreted as described in BCP 14 [^BCP14] when, and only when, they
appear in all capitals.

The character § is used when referring to sections of the Zcash Protocol Specification.
[^protocol]

The terms "actions", "conventional fee", and "marginal fee" are defined as in ZIP 317. [^zip-0317]

The term "reorg buffer" refers to the number of blocks prior to the chain tip that are excluded from consideration to mitigate reorganization risk.

The term "lookback window" refers to the number of blocks prior to the chain tip used to calculate statistics useful for fee calculation from comparable transactions.

The term "fee floor" (or "floor") refers to the minimum price allowed in the fee calculation.

The term "priority multiplier" (or "multiplier") refers to the factor by which a transaction's fee is multiplied if the user opts for priority processing.

The term "comparables" (or "comps") refers to previous transactions used to determine the appropriate fee for a new transaction based on their fees and actions.

The Version 6 transaction fields `nIssueActions`, `fee`, and `nExpiryHeight` are as defined in ZIP-230. [^zip-0230]

# Abstract

This ZIP introduces a dynamic pricing mechanism based on a median calculation
of comparable prices that users have paid in previous blocks.

The mechanism can ship first as simple node and wallet policy changes, and
consensus hardening can follow in a later network upgrade. The design preserves
Zcash's core privacy assumptions and adds no explicit on-chain metadata beyond
the paid fee.

# Motivation

The price of ZEC has become more volatile and risen sharply, raising
transaction fees along with it to prices users have begun to find questionable.
Additionally, new environmental factors such as new levels of adoption, and the
emergence of Zcash Digital Asset Treasuries may hint at increased volume over
the foreseeable future.

While there are short-term solutions available (the simplest of which would
simply be to lower the ZIP-317 marginal fee), this may be inadequate over a
longer period of time and require periodic tuning. Thus, a dynamic fee
calculation is required both to weather short-term volatility, and also to
adjust the marginal fee dynamically over time.

TODO: Justify the complexity of this approach relative to adjusting the ZIP 317
marginal fee. At present, marginal fee adjustments across the ecosystem are a
bit of a challenge, in particular, raising the marginal fee definitely requires
wallets to update. An automatic fee adjustment mechanism handles this.

# Privacy Implications

This design attempts to minimize information leakage about the user while still
providing user discretion on paying a premium rate for priority processing,
resulting in a better user experience.

The combined effects of an additional bit of user choice (priority vs standard)
and powers of 10 quantization of fees result in an overall reduction of fee
entropy leakage.

This design likely requires trust in the lightwallet's relay of the fees, which
is compatible with the existing wallet app threat model. [^wallet-threat-model]

# Requirements

A successful design and implementation is one that:

- Does not leak information that can be used to segment the user base.
- Only uses public information to compute the conventional fee.
- Has the fee remain roughly economically stable, even though the economic
  power of ZEC can fluctuate substantially.
- Provides a clear and consistent user experience:
    - Fees are easy to understand and explain
    - Fees are kept low and adjust rarely
    - Transactions are reliable under uncongested network conditions
    - Prioritizes higher value transactions when the network is congested
- Incentivizes miners to include legitimate transactions in blocks
- Responds quickly to congestion and slowly returns to normal prices
- Makes griefing expensive:
    - Preventing legitimate transactions requires paying a price higher than
      legitimate users are willing to pay
    - Prevents miners from gaming the protocol by making users pay more
- Is easy to implement and deploy:
    - Compatible with current and planned network upgrades i.e. ZIP-235’s NSM
      contributions and ZIP-317’s action-based accounting.
    - Policy-first, hardened by minimal consensus upgrades later
    - Uses a stateless design, with minimal calculations
- Does not substantively degrade user experience compared to the status quo.

# Specification

## Notation

Let $\mathsf{median}(S)$ and $\mathsf{mean}$ be as defined in §7.7.3 ‘Difficulty Adjustment’ [^protocol-diffadjustment].

## Marginal Fee Calculation

This specification defines several new parameters that are used to calculate
the new marginal fee.

| Parameter | Value | Units |
| --- | --- | --- |
| `reorg_buffer` | 5 | blocks |
| `lookback_window` | 50 | blocks |
| `fee_floor` | 10 | zats per action |

Let `chain_tip` be the height of the latest known block.

Let `T` be the sequence of transactions in the blocks with heights `[chain_tip - reorg_buffer - lookback_window ... chain_tip - reorg_buffer]`.

The new suggested marginal fee is calculated as $\mathsf{median}(T_fee)$. The
conventional fee calculation remains unchanged as per ZIP-317. [^zip-0317]

<details>
<summary>Rationale</summary>
- A reorg buffer of 5 blocks is chosen to balance the need to mitigate
  reorganization risk with the desire to use recent transaction data for fee
  calculation.
- A lookback window of 50 blocks (roughly the last hour based on the difficulty
  algorithm) is selected to provide a sufficient sample size of recent
  transactions while still being responsive to changes in network conditions. 
- The median is chosen as the method for calculating the marginal fee because
  it is robust against outliers and provides a more accurate representation of
  typical transaction fees paid by users. By ensuring that 50% of transactions
  pay at least the median fee, we can reasonably assume that miners are
  incentivized to include transactions paying this fee in their blocks.
</details>

## Synthetic Actions

Given the same sequence of transactions `T` as defined above, let synthetic action
`S` be defined as an action with a `S_fee = fee_floor` and a size of
$\mathsf{mean}(T_size)$.

When calculating the median fee, if a block has unused capacity (i.e., fewer
actions than the maximum allowed), we fill the empty space with synthetic
actions, and then perform the median calculation.

<details>
<summary>Rationale</summary>
- By using the average size of real actions for synthetic actions, we ensure
  that the fee calculation remains realistic and reflective of actual network
  conditions.
</details>

## New Rules

The following rules can be enforced by relay policy initially, and later
hardened into consensus rules in a future network upgrade.

- The per-action fee MUST be at least `fee_floor` zats.
- The per-action fee MUST be a power of 10.
- The wallet MUST set `nExpiryHeight` such that `chain_tip + reorg_buffer < nExpiryHeight < chain_tip + lookback_window + reorg_buffer`,

<details>
<summary>Rationale</summary>
- Setting an expiry height within this range ensures that mispriced
  transactions don't linger in the mempool for too long.
</details>

## Wallet Construction

Any transaction UX (wallet or other interface) SHOULD offer the user the standard median fee, and a priority fee of `median_fee_per_action * priority_multiplier`.

# Reference Implementation

More information is available at https://fees.shieldedinfra.net.


# References

[^BCP14]: [Information on BCP 14 - "RFC 2119: Key words for use in RFCs to Indicate Requirement Levels" and "RFC 8174: Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words"](https://www.rfc-editor.org/info/bcp14)

[^zip-0317]: [ZIP-317: Proportional Transfer Fee Mechanism](https://zips.z.cash/zip-0317)

[^zip-0230]: [ZIP-230: Version 6 Transaction Format](https://zips.z.cash/zip-0230)

[^wallet-threat-model]: [Zcash Wallet App Threat Model](https://zcash.readthedocs.io/en/latest/rtd_pages/wallet_threat_model.html)
