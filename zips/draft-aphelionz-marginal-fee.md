    ZIP: Unassigned
    Title: Reduce Marginal Fee to 1000 Zatoshis and Raise the Weight Ratio Cap to 10
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
10,000 to 2,000 zatoshis. It also raises `weight_ratio_cap` in ZIP 317's
block template algorithm from 4 to 10, so that the fee cut does not narrow
the range as sharply. Nothing else in ZIP 317 changes.

# Motivation

ZIP 317's fee was set in late 2022, when ZEC was about $30 and the minimum
fee of 10,000 zatoshis cost about a third of a cent in USD. The fee is fixed
in zatoshis, so when the price went up, so did the fee. At $800 (the price on
2026-08-29) the minimum fee costs 8 cents.

Cutting `marginal_fee` to 1,000 brings the minimum fee to 2,000 zatoshis,
about 1.6 cents. Even after a 5x cut, it is still 5x more than it was when
ZEC was $30. It only gets cheaper than the 2022 fee if ZEC falls below $150.

Additionally, `weight_ratio_cap` is a multiple of the conventional fee, so
cutting `marginal_fee` shrinks the range of inclusion-influencing fees from
10,000 - 40,000 zatoshis to 2,000 - 8,000. Raising `weight_ratio_cap` to 10
widens that range to 2,000 - 20,000, still below the today's maximum. It also
keeps transactions from wallets that have not yet updated, which pay 5x the
new conventional fee, from being clamped at the cap.

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

## Change to `weight_ratio_cap`

In the section **Recommended algorithm for block template construction** of
ZIP 317, the sentence

> Define constants `weight_ratio_cap` = 4 and `block_unpaid_action_limit` = 50.

is replaced with

> Define constants `weight_ratio_cap` = 10 and `block_unpaid_action_limit` = 50.

In the section **Rationale for block template construction algorithm**, the
paragraph beginning "The rationale for choosing `weight_ratio_cap` = 4" is
replaced with:

> The rationale for choosing `weight_ratio_cap` = 10 is as a compromise between
> not allowing any prioritization of transactions relative to those that pay the
> conventional fee, and allowing arbitrary prioritization based on ability to
> pay. Because the cap is a multiple of the conventional fee, the fee at which a
> transaction's weight ratio saturates falls with `marginal_fee`. A cap of 10 at
> `marginal_fee` = 1000 places that point below where it was at
> `weight_ratio_cap` = 4 and `marginal_fee` = 5000.

## Interaction with the `getstandardfee` RPC endpoint

zebrad's `getstandardfee` RPC endpoint reports the ZIP 317 `marginal_fee`.
Implementations providing this or an equivalent endpoint MUST report 1,000
zatoshis per logical action from the activation height given in the
Deployment section.

# Rationale

**Why a `marginal_fee` of 1,000.** A 5x cut still leaves the fee 5x above its 2022
dollar cost.

**Why a `weight_ratio_cap` of 10.** Like the 4 it replaces, 10 is a compromise
rather than a derived number. The one hard constraint is that the new maximum
stay at or below today's 40,000 zatoshis, which bounds the cap at 20; 10 leaves
room to move further later.

**Precedent.** ZIP 313 [^zip-0313] changed the conventional fee in 2020 the
same way: a wallet convention, no network upgrade.

# Deployment

Node implementations MUST ship the new relay policy before wallets adopt the new
fee. `block_unpaid_action_limit` is 0 in both zebra and zakura and is not
operator-configurable, so an un-upgraded node will not relay a 2,000-zatoshi
transaction at all, since it counts 2 unpaid actions under the old parameters.

Wallets SHOULD adopt `marginal_fee = 1000` at Mainnet block height 3590000,
expected in mid December 2026. This is past the end-of-service halt of
both zebra v6.3.0 (height 3564960) and zakura v1.3.1 (height 3501339), by
which point operators still running MUST have moved to a release carrying
the new policy.

The `weight_ratio_cap` change affects block producers only and has no wallet
dependency, so the two parameter changes can be adopted in either order.

# References

[^BCP14]: [Information on BCP 14 — "RFC 2119: Key words for use in RFCs to Indicate Requirement Levels" and "RFC 8174: Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words"](https://www.rfc-editor.org/info/bcp14)

[^protocol]: [Zcash Protocol Specification, Version 2025.6.3 [NU6.1] or later](protocol/protocol.pdf)

[^zip-0235]: [ZIP 235: Remove 60% of Transaction Fees From Circulation](zip-0235)

[^zip-0313]: [ZIP 313: Reduce Conventional Transaction Fee to 1000 zatoshis](zip-0313)

[^zip-0317]: [ZIP 317: Proportional Transfer Fee Mechanism](zip-0317)
