    ZIP: Unassigned
    Title: Reduce Marginal Fee to 1000 Zatoshis
    Owners: Mark Henderson <mark@shieldedlabs.net>
    Status: Draft
    Category: Standards / Wallet
    Updates: ZIP 317
    Created: 2026-04-06
    License: MIT
    Discussions-To: <TBD>
    Pull-Request: <TBD>


# Terminology

The key words "MUST" and "SHOULD" in this document are to be interpreted as
described in BCP 14 [^BCP14] when, and only when, they appear in all capitals.

Fee terminology is as defined in ZIP 317 [^zip-0317]; "zatoshi" is as defined in
the Zcash protocol specification. [^protocol]


# Abstract

This ZIP reduces ZIP 317's [^zip-0317] `marginal_fee` from 5,000 to 1,000
zatoshis per logical action, lowering the minimal 2-action conventional fee from
10,000 to 2,000 zatoshis. All other ZIP 317 parameters and formulae are
unchanged.


# Motivation

ZIP 317 was designed in late 2022, when ZEC near the design point *P* = $30 made
its 10,000-zatoshi minimum fee cost about $0.003. The parameters are static, so
fiat cost tracks price. At the price of record, $472 (2026-08-11) or ~15.7 *P*:

| `marginal_fee` | Min. tx fee    | Fiat cost   | vs. design point |
|----------------|----------------|-------------|------------------|
| 5,000          | 10,000 zats    | $0.0472     | 15.7x            |
| **1,000**      | **2,000 zats** | **$0.0094** | **3.1x**         |

The proposed fee exceeds the design-point fiat cost at any price above 5 *P*
($150), so this is a 5x reduction that does not restore the 2022 level.
`marginal_fee = 1000` was rejected during ZIP 317's design [^madars-1] as too
weak a deterrent at $30; at the price of record it costs 3.1x that value.


# Privacy Implications

The formula's structure is unchanged, so wallets pay the same amount for the
same transaction shape. In transition, wallets split between 5,000 and 1,000 are
distinguishable by fee; the mitigation is coordinated deployment.


# Specification

## Changes to ZIP 317

In the **Fee calculation** table of ZIP 317 [^zip-0317], the `marginal_fee` row
changes from 5000 to 1000 zatoshis per logical action.

Every other ZIP 317 parameter, the `conventional_fee` formula, and the
RECOMMENDED block template construction algorithm are unchanged; `unpaid_actions`
is defined in terms of `marginal_fee` and reflects the new value automatically.

In the event that ZIP 235 [^zip-0235] is activated, the fraction removed from 
circulation is unchanged: of a 2,000-zatoshi fee, 1,200 zatoshis will be 
removed from circulation and 800 must be claimed by the miner.

## Interaction with the `getstandardfee` RPC endpoint

The v0 estimator behind the `getstandardfee` RPC endpoint specifies a
synthetic fill `floor` of 1,000 zatoshis per action: this ZIP's `marginal_fee`.
The two MUST be kept consistent.

## Wallet and node adoption

Wallets SHOULD use `marginal_fee = 1000` upon this ZIP reaching Active status.
ZIP 317 fees are a convention, not a consensus rule, so no network upgrade is
required, and users MUST retain the ability to override the fee.

Nodes SHOULD update relay and mempool eviction thresholds to the new value, and
the ZIP 401 [^zip-0401] `low_fee_penalty` SHOULD be recalibrated. Node
implementations MUST support a configuration option overriding the relay-policy
`marginal_fee`, defaulting to 1,000, so operators can revert without a software
update.


# Rationale

**Why a power of 10.** A discrete alphabet (100, 1,000, 10,000) reduces fee
entropy, simplifies UX, and gives a dynamic fee mechanism natural tier
boundaries. 500 and 2,500 are off it; 100 is a 50x cut, too low for spam
deterrence at any plausible price. Even 500 would cost 1.6x the design point at
the price of record, so alphabet alignment, not denial-of-service headroom, is
the argument against it.

**Precedent.** ZIP 313 [^zip-0313] set the conventional fee to 1,000 zatoshis in
2020 as a wallet convention with no network upgrade. Once ZIP 317 obsoleted it,
that fee bought zero paid actions (mitigated via the _block_unpaid_action_limit_)
and incurred the low fee penalty. Those hazards do not occur in the case of a
change that always decreases the conventional fee of a given transaction.

**Why this is safe.** The other defense layers are independent of the fee level:
`block_unpaid_action_limit` caps underpriced actions at 50 per block and Zebra
enforces 0, ZIP 401 eviction bounds memory denial of service, and ZIP 235 burn
makes sustained spam permanently costly. Filling 2 MB blocks costs *N* x *C* / 5
per hour against a design-point *C* ~$144/hour, so ~$453/hour at the price of
record.


# Deployment

## Schedule

This ZIP changes no consensus rule: `marginal_fee` is a wallet convention and a
node relay policy parameter, so deployment needs no activation height, no
network upgrade, and no coordination with any upgrade schedule. Only the ZIP
process and ordinary release cycles bind, which makes a Mainnet target of
2026-10-01 achievable:

| Date       | Milestone                                                          |
|------------|--------------------------------------------------------------------|
| 2026-08-25 | `Discussions-To` filled, PR opened upstream                        |
| 2026-09-01 | Node implementations land the relay policy change and the override |
| 2026-09-08 | Testnet                                                            |
| 2026-09-22 | Wallet releases using `marginal_fee = 1000`                        |
| 2026-10-01 | Mainnet default                                                    |

There is no flag day: slipping a milestone delays the date without affecting
correctness, since nodes and wallets on either value interoperate.


## Ordering

Relay policy updates SHOULD ship before or with wallet updates; a 2,000-zatoshi
transaction reaching a node still on `marginal_fee = 5000` is relayed and mined,
but incurs the ZIP 401 low fee penalty. Deploy on Testnet before Mainnet.


# References

[^BCP14]: [Information on BCP 14 — "RFC 2119: Key words for use in RFCs to Indicate Requirement Levels" and "RFC 8174: Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words"](https://www.rfc-editor.org/info/bcp14)

[^protocol]: [Zcash Protocol Specification, Version 2025.6.3 [NU6.1] or later](protocol/protocol.pdf)

[^zip-0235]: [ZIP 235: Remove 60% of Transaction Fees From Circulation](zip-0235)

[^zip-0313]: [ZIP 313: Reduce Conventional Transaction Fee to 1000 zatoshis](zip-0313)

[^zip-0317]: [ZIP 317: Proportional Transfer Fee Mechanism](zip-0317)

[^zip-0401]: [ZIP 401: Addressing Mempool Denial-of-Service](zip-0401)

[^madars-1]: [Madars Virza, concrete soft-fork proposal](https://forum.zcashcommunity.com/t/zip-reduce-default-shielded-transaction-fee-to-1000-zats/37566/89)
