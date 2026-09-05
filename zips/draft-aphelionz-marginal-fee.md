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

The key words "MUST", "SHOULD", and "SHOULD NOT" in this document are to be
interpreted as described in BCP 14 [^BCP14] when, and only when, they appear
in all capitals.

Fee terminology is as defined in ZIP 317 [^zip-0317]; "zatoshi" is as defined in
the Zcash protocol specification. [^protocol]


# Abstract

This ZIP reduces ZIP 317's [^zip-0317] `marginal_fee` from 5,000 to 1,000
zatoshis per logical action, lowering the minimal 2-action conventional fee from
10,000 to 2,000 zatoshis. It also removes the `weight_ratio_cap` constant from
ZIP 317's recommended block template construction algorithm, making a
transaction's selection weight proportional to its fee. All other ZIP 317
parameters and formulae are unchanged.


# Motivation

ZIP 317 was designed in late 2022, when ZEC near the design point *P* = $30 made
its 10,000-zatoshi minimum fee cost about $0.003. The parameters are static, so
fiat cost tracks price. At the price of record, $800 (2026-08-29) or ~26.7 *P*:

| `marginal_fee` | Min. tx fee    | Fiat cost   | vs. design point |
|----------------|----------------|-------------|------------------|
| 5,000          | 10,000 zats    | $0.0800     | 26.7x            |
| **1,000**      | **2,000 zats** | **$0.0160** | **5.3x**         |

The proposed fee exceeds the design-point fiat cost at any price above 5 *P*
($150), so this is a 5x reduction that does not restore the 2022 level.
`marginal_fee = 1000` was rejected during ZIP 317's design [^madars-1] as too
weak a deterrent at $30; at the price of record it costs 5.3x that value.

Separately, ZIP 317's recommended block template construction algorithm caps a
transaction's selection weight at `weight_ratio_cap` = 4 times that of a
transaction paying exactly the conventional fee, so fee paid beyond 4x the
conventional fee buys no additional selection probability. ZIP 317 describes
the value 4 as a compromise between no prioritization and arbitrary
prioritization by ability to pay: a chosen point, not a derived quantity.
Removing the cap makes selection weight proportional to fee at every level, so
a user who pays for priority receives what is paid for.


# Privacy Implications

The formula's structure is unchanged, so wallets pay the same amount for the
same transaction shape. If wallets adopt the new value at different times, the
fee segments by wallet software. To bound this window, wallets SHOULD switch
at the activation height given in the Deployment section rather than upon
release.

Removing `weight_ratio_cap` permits arbitrarily large selection multipliers.
Wallets SHOULD NOT expose fee multipliers outside a small discrete set of
recommended values; arbitrary fee values widen the fee value space and shrink
each value's anonymity set.


# Specification

## Changes to ZIP 317

In the parameter table of the **Fee calculation** section of ZIP 317
[^zip-0317], the entry

> `marginal_fee` | 5000 | zatoshis per logical action (as defined below)

is replaced with

> `marginal_fee` | 1000 | zatoshis per logical action (as defined below)

No other entry in the table changes. The `conventional_fee` formula and the
definition of `unpaid_actions` in the **Recommended algorithm for block
template construction** reference `marginal_fee` and require no wording
change.

In the event that ZIP 235 [^zip-0235] is activated, the fraction removed from 
circulation is unchanged: of a 2,000-zatoshi fee, 1,200 zatoshis will be 
removed from circulation and 800 must be claimed by the miner.

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

## Wallet and node adoption

Wallets SHOULD use `marginal_fee = 1000` from the activation height given in
the Deployment section. ZIP 317 fees are a convention, not a consensus rule, so
no network upgrade is required, and users MUST retain the ability to override
the fee.

Nodes SHOULD update relay and mempool eviction thresholds to the new value. No
change to the ZIP 401 [^zip-0401] `low_fee_penalty` is required.


# Rationale

**Why remove the cap rather than raise it.** Any cap is a chosen point. Of ZIP
317's two arguments that overpaying gains no significant advantage, only the
first depends on the cap; the second, that *c* times the fee on one transaction
occupies less block space than *c* transactions and so leaves more room for
others, is independent of it and carries the argument. The algorithm
discriminates among candidates only when they exceed a block's capacity, so the
cap's removal has no effect outside sustained contention.

**Precedent.** ZIP 313 [^zip-0313] set the conventional fee to 1,000 zatoshis in
2020 as a wallet convention with no network upgrade. Once ZIP 317 obsoleted it,
that fee bought zero paid actions (mitigated via the _block_unpaid_action_limit_)
and incurred the low fee penalty. Those hazards do not occur in the case of a
change that always decreases the conventional fee of a given transaction.

**Denial-of-service margin.** The deterrents against block-filling are
independent of the fee level: `block_unpaid_action_limit` bounds unpaid actions
per block, and ZIP 401 [^zip-0401] mempool cost limiting bounds memory
consumption. Reducing `marginal_fee` by a factor of 5 reduces the cost of
filling blocks by the same factor; at the price of record that cost remains
5.3x what it was at the ZIP 317 design point.


# Alternatives

**`marginal_fee` = 500.** Halves the minimum fee to 1,000 zatoshis, which
exceeds the design-point fiat cost only at prices above 10 *P* ($300). It was
suggested in review; this ZIP prefers 1,000 to retain twice the
denial-of-service margin at lower prices.

**`marginal_fee` = 100.** A 50x cut whose 200-zatoshi minimum fee falls below
the design-point cost at any price under 50 *P* ($1,500): too weak a deterrent.

**No change.** Fiat cost continues to track price; at the price of record the
minimum fee costs 26.7x the design point.


# Deployment

## Activation

Wallets and node relay policy SHOULD adopt `marginal_fee = 1000` at Mainnet
block height 3500000, expected in late September 2026. This ZIP changes no
consensus rule, so the height requires no network upgrade; it synchronizes the
switch, bounding the transition window described under Privacy Implications.
Releases containing the change SHOULD ship in advance of the activation height
and use the previous value until it is reached. On Testnet, implementations
SHOULD adopt the new value as soon as releases are available; no coordinated
height is specified.

Nodes and wallets on either value interoperate, so a missed height degrades
privacy of the transition, not correctness.


## Ordering

Relay policy updates MUST ship before wallet updates. A 2,000-zatoshi
transaction reaching a node still on `marginal_fee = 5000` is relayed, but it
incurs the ZIP 401 low fee penalty, and it counts 2 unpaid actions there, so it
is mined only where the producer's `block_unpaid_action_limit` configuration
permits unpaid actions. Deploy on Testnet before Mainnet.

Use of the block template construction algorithm is voluntary, and the
`weight_ratio_cap` removal needs no coordination: under partial adoption a
transaction paying *c* times the conventional fee receives weight *c* at
upgraded block producers and min(*c*, 4) elsewhere. Producers ordering
candidates greedily by fee are unaffected.


# References

[^BCP14]: [Information on BCP 14 — "RFC 2119: Key words for use in RFCs to Indicate Requirement Levels" and "RFC 8174: Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words"](https://www.rfc-editor.org/info/bcp14)

[^protocol]: [Zcash Protocol Specification, Version 2025.6.3 [NU6.1] or later](protocol/protocol.pdf)

[^zip-0235]: [ZIP 235: Remove 60% of Transaction Fees From Circulation](zip-0235)

[^zip-0313]: [ZIP 313: Reduce Conventional Transaction Fee to 1000 zatoshis](zip-0313)

[^zip-0317]: [ZIP 317: Proportional Transfer Fee Mechanism](zip-0317)

[^zip-0401]: [ZIP 401: Addressing Mempool Denial-of-Service](zip-0401)

[^madars-1]: [Madars Virza, concrete soft-fork proposal](https://forum.zcashcommunity.com/t/zip-reduce-default-shielded-transaction-fee-to-1000-zats/37566/89)
