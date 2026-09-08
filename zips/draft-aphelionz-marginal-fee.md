    ZIP: Unassigned
    Title: Reduce Marginal Fee to 1000 Zatoshis and Remove the Weight Ratio Cap
    Owners: Mark Henderson <mark@shieldedlabs.net>
    Status: Draft
    Category: Standards / Wallet
    Updates: ZIP 317
    Created: 2026-04-06
    License: MIT
    Discussions-To: <TBD>
    Pull-Request: <TBD>


# Terminology

The key words "MUST", and "SHOULD" in this document are to be interpreted as
described in BCP 14 [^BCP14] when, and only when, they appear in all capitals.

Fee terminology is as defined in ZIP 317 [^zip-0317]; "zatoshi" is as defined in
the Zcash protocol specification. [^protocol]

# Abstract

This ZIP cuts ZIP 317's [^zip-0317] `marginal_fee` from 5,000 to 1,000
zatoshis per logical action, so the minimum conventional fee drops from
10,000 to 2,000 zatoshis. It also removes `weight_ratio_cap` from ZIP 317's
block template algorithm, so paying a higher fee always buys proportionally
more chance of being selected. Nothing else in ZIP 317 changes.

# Motivation

ZIP 317's fee was set in late 2022, when ZEC was about $30 and the minimum
fee of 10,000 zatoshis cost about a third of a cent in USD. The fee is fixed
in zatoshis, so when the price went up, so did the fee. At $800 (the price on
2026-08-29) the minimum fee costs 8 cents.

Cutting `marginal_fee` to 1,000 brings the minimum fee to 2,000 zatoshis,
about 1.6 cents. Even after a 5x cut, it is still 5x more than it was when
ZEC was $30. It only gets cheaper than the 2022 fee if ZEC falls below $150.

Separately, ZIP 317's block template algorithm caps a transaction's weight at
4x that of a transaction paying the conventional fee. Paying more than 4x
buys nothing. ZIP 317 itself describes the 4 as a compromise rather than a
derived number. Removing the cap means that if you pay more, you get more.

# Privacy Implications

*Privacy:* If wallets switch to the new fee at different times, the fee
reveals which wallet software made the transaction. To keep that window
short, wallets SHOULD switch at the activation height given under
Deployment, not when the release ships.

# Specification

## Changes to ZIP 317

In the parameter table of the **Fee calculation** section of ZIP 317
[^zip-0317], the entry

> `marginal_fee` | 5000 | zatoshis per logical action (as defined below)

is replaced with

> `marginal_fee` | 1000 | zatoshis per logical action (as defined below)

No other entry in the table changes.

If ZIP 235 [^zip-0235] activates, the fraction removed from circulation is
unchanged: of a 2,000-zatoshi fee, 1,200 zatoshis are removed and 800 go to
the miner.

## Removal of `weight_ratio_cap`

In the section **Recommended algorithm for block template construction** of
ZIP 317, the sentence

> Define constants `weight_ratio_cap` = 4 and `block_unpaid_action_limit` = 50.

is replaced with

> Define the constant `block_unpaid_action_limit` = 50.

and in step 2 of the algorithm, the definition

> `tx.weight_ratio = min(max(1, tx.fee) / conventional_fee(tx), weight_ratio_cap)`

is replaced with

> `tx.weight_ratio = max(1, tx.fee) / conventional_fee(tx)`

In the section **Rationale for block template construction algorithm**, the
paragraph beginning "The weighting in step 2 does not create a situation", its
two numbered list items, and the paragraph beginning "The rationale for
choosing `weight_ratio_cap` = 4" are replaced with:

> The weighting in step 2 prioritizes transactions in direct proportion to fee
> paid. Overpaying does not disadvantage other users' transactions in
> aggregate: an adversary who pays *c* times the conventional fee for one
> transaction, rather than the conventional fee for each of *c* transactions,
> is more likely to get each transaction into a block relative to competing
> transactions, but those transactions take up less block space, all else
> (e.g. choice of input or output types) being equal, leaving more block space
> for the other users' transactions.

## Interaction with the `getstandardfee` RPC endpoint

zebrad's `getstandardfee` RPC endpoint reports the ZIP 317 `marginal_fee`.
Implementations providing this or an equivalent endpoint MUST report 1,000
zatoshis per logical action from the activation height given in the
Deployment section.

# Rationale

**Why 1,000.** A 5x cut still leaves the fee 5x above its 2022
dollar cost.

**Why remove the cap instead of raising it.** In practice, there is nothing
to prevent miners from including transactions with higher fees in preference
to transactions with lower fees, regardless of what is written in ZIP 317.

**Precedent.** ZIP 313 [^zip-0313] changed the conventional fee in 2020 the
same way: a wallet convention, no network upgrade.

# Deployment

Relay policy and block template updates MUST ship before wallets adopt the new
fee: a 2,000-zatoshi transaction counts 2 unpaid actions under the old parameters,
and producers configured with `block_unpaid_action_limit = 0` will not mine it.
Node operators need no coordination and SHOULD update as soon as releases are
available.

Wallets SHOULD adopt `marginal_fee = 1000` at Mainnet block height 3500000,
expected in late September 2026.

# References

[^BCP14]: [Information on BCP 14 — "RFC 2119: Key words for use in RFCs to Indicate Requirement Levels" and "RFC 8174: Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words"](https://www.rfc-editor.org/info/bcp14)

[^protocol]: [Zcash Protocol Specification, Version 2025.6.3 [NU6.1] or later](protocol/protocol.pdf)

[^zip-0235]: [ZIP 235: Remove 60% of Transaction Fees From Circulation](zip-0235)

[^zip-0313]: [ZIP 313: Reduce Conventional Transaction Fee to 1000 zatoshis](zip-0313)

[^zip-0317]: [ZIP 317: Proportional Transfer Fee Mechanism](zip-0317)

[^zip-0401]: [ZIP 401: Addressing Mempool Denial-of-Service](zip-0401)
