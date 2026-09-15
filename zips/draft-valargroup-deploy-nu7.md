```
ZIP: Unassigned
Title: Deployment of the NU7 Network Upgrade
Owners: Dev Ojha <dev@valargroup.dev>
Status: Draft
Category: Consensus / Network
Created: 2026-09-15
License: MIT
Discussions-To: <https://forum.zcashcommunity.com/t/nu7-coinholder-vote/56912>
```


# Terminology

The key words "MUST" and "MUST NOT" in this document are to be interpreted as
described in BCP 14 [^BCP14] when, and only when, they appear in all capitals.

The term "network upgrade" is to be interpreted as described in ZIP 200.
[^zip-0200]

The character § is used when referring to sections of the Zcash Protocol
Specification. [^protocol]

The terms "Mainnet" and "Testnet" are to be interpreted as described in
§ 3.12 'Mainnet and Testnet'. [^protocol-networks]

"ZEC/TAZ" refers to the native currency of Zcash on a given network: ZEC on
Mainnet and TAZ on Testnet.

$\mathsf{MAX\_MONEY}$, as defined in § 5.3 'Constants', is the maximum
permitted ZEC/TAZ supply measured in zatoshi. [^protocol-constants]

"Issued Supply" at a given height means the sum of all chain value pool
balances at that height, as calculated in § 4.17 'Chain Value Pool Balances'.
[^protocol-chainvaluepoolbalances]

"Scheduled Block Subsidy" means the block subsidy determined by the existing
halving schedule, after applying the changes in ZIP 218. [^zip-0218]

"NSM reserve" means a consensus-tracked balance of ZEC/TAZ removed from
circulation by the Network Sustainability Mechanism (NSM). The NSM reserve is
not a spendable chain value pool and is not included in Issued Supply.


# Abstract

This proposal defines the deployment of the NU7 network upgrade. NU7 reduces
the block target spacing from 75 seconds to 25 seconds and introduces
per-pool and global shielded action limits, as specified in ZIP 218. It also
deploys a halving-preserving variant of ZIP 234: 60% of transaction fees are
removed from circulation into the NSM reserve beginning at NU7 activation,
and are reissued through future block subsidies beginning in February 2031.
The scheduled halving curve is unchanged. [^zip-0234]

NU7 introduces no new transaction format. Once NU7 activates, version 4
transactions are invalid, while version 5 and version 6 transactions remain
valid. Because Sprout transfers can only be represented by version 4
transactions, funds remaining in the Sprout pool become unspendable.

The changes do not increase the ZEC supply cap. Funds paid from the NSM reserve
were previously removed from circulation in equal amount. The reserve is
public consensus state and introduces no new transaction-level data.


# Motivation

NU7 is deliberately limited to changes that have strong coinholder support
and can be deployed without another transaction-format migration. Faster
blocks reduce confirmation latency, while the action limits in ZIP 218 bound
the validation and shielded synchronization costs enabled by the increased
block frequency.

The NSM redirects part of each block's transaction fees from immediate miner
revenue into a non-discretionary reserve. Beginning in February 2031, that
reserve supplements the scheduled block subsidy along a continuous decay curve.
This supports the long-term security budget while preserving both the existing
halving schedule and the supply cap.

Rejecting version 4 transactions completes the deprecation of Sprout. It is left
for future ZIPs to propose recoverability of those funds.


# Requirements

NU7 is intended to:

1. reduce confirmation latency without increasing the issuance rate per unit
   of wall-clock time;
2. bound the per-block and aggregate costs of shielded actions;
3. preserve the existing block-subsidy halving schedule;
4. remove the floor of 60% of aggregate transaction fees from circulation, so
   that rounding favors the miner;
5. begin predictable, non-discretionary reissuance of those fees in February
   2031 without exceeding the amount previously removed;
6. preserve the ZEC supply cap;
7. introduce no new transaction format; and
8. make version 4 transactions invalid at NU7 activation.


# Specification

## NU7 consensus changes

The primary sources of information about NU7 consensus protocol changes are:

* The Zcash Protocol Specification. [^protocol]
* ZIP 200: Network Upgrade Mechanism. [^zip-0200]
* ZIP 218: 25-second Block Target Spacing. [^zip-0218]
* The halving-preserving variant of ZIP 234 described in this ZIP and based on
  the Shielded Labs proposal. [^halving-preserving-pr]

The network handshake and peer management mechanisms defined in ZIP 201 also
apply to this upgrade. [^zip-0201]

NU7 deploys all of the consensus changes specified in ZIP 218. The NSM and
transaction-version changes are specified below. Where those changes conflict
with ZIP 234 or ZIP 235 as currently written, this ZIP takes precedence for
NU7. [^zip-0234] [^zip-0235]

## NSM reserve

For a block at height $\mathsf{height}$, let
$\mathsf{TransactionFees}(\mathsf{height})$ be the total transaction fees in
the block, excluding its coinbase transaction, measured in zatoshi.

Define the contribution to the NSM reserve as:

$$
\mathsf{NSMFeeContribution}(\mathsf{height}) :=
\mathsf{floor}\!\left(
  \frac{6 \cdot \mathsf{TransactionFees}(\mathsf{height})}{10}
\right).
$$

This calculation is performed on the aggregate fees for the block. Rounding
therefore favors the miner. The remaining fees are:

$$
\mathsf{MinerFees}(\mathsf{height}) :=
\mathsf{TransactionFees}(\mathsf{height}) -
\mathsf{NSMFeeContribution}(\mathsf{height}).
$$

Prior to NU7 activation, nodes MUST initialize the NSM reserve balance to zero.
For every block from NU7 activation onward, the coinbase transaction MUST be
balanced using $\mathsf{MinerFees}$ in place of $\mathsf{TransactionFees}$,
and the NSM reserve balance MUST increase by
$\mathsf{NSMFeeContribution}$, subject to the reissuance rule below. This
modifies the full-claim rule deployed in ZIP 236. [^zip-0236]

In particular, the total input value of the coinbase transaction defined in
§ 7.1.2 'Transaction Consensus Rules' MUST be calculated as: [^protocol-txnconsensus]

$$
\mathsf{BlockSubsidy}(\mathsf{height}) +
\mathsf{MinerFees}(\mathsf{height}) +
\mathsf{totalDeferredInput}(\mathsf{height}).
$$

The definition of the total output value and the requirement that the total
input and output values of the coinbase transaction be equal are unchanged.

The NSM reserve MUST NOT be treated as a spendable chain value pool and MUST
NOT be included in the Issued Supply calculation in § 4.17 'Chain Value Pool
Balances'. Its balance is denominated in zatoshi and MUST NOT become negative
or exceed $\mathsf{MAX\_MONEY}$.

No source other than $\mathsf{NSMFeeContribution}$ contributes to the NSM
reserve in NU7. In particular, NU7 does not deploy the voluntary-removal bundle
specified by ZIP 233. [^zip-0233]

## Halving-preserving NSM reissuance

Define:

$$
\mathsf{NSM\_SUBSIDY\_FRACTION} :=
\frac{1375}{10{,}000{,}000{,}000}.
$$

Let $\mathsf{NSMReissuanceHeight}$ be the activation height for NSM
reissuance on the relevant network. It is specified under
[NU7 network constants](#nu7networkconstants) and corresponds to a date in
February 2031.

Let $\mathsf{NSMReserveAfter}(\mathsf{height})$ be the NSM reserve balance
after the block at $\mathsf{height}$ has been applied, and define the balance
before NU7 activation to be zero. Define:

$$
\mathsf{NSMSubsidy}(\mathsf{height}) :=
\begin{cases}
0, & \textsf{if } \mathsf{height} < \mathsf{NSMReissuanceHeight}, \\
\mathsf{ceiling}\!\left(
  \mathsf{NSM\_SUBSIDY\_FRACTION} \cdot
  \mathsf{NSMReserveAfter}(\mathsf{height} - 1)
\right), & \textsf{otherwise}.
\end{cases}
$$

The NSM reserve balance after a block MUST be calculated as:

$$
\begin{aligned}
\mathsf{NSMReserveAfter}(\mathsf{height}) := {} &
\mathsf{NSMReserveAfter}(\mathsf{height} - 1) \\
&+ \mathsf{NSMFeeContribution}(\mathsf{height}) \\
&- \mathsf{NSMSubsidy}(\mathsf{height}).
\end{aligned}
$$

Apply ZIP 218's block-subsidy changes first, then rename the resulting
$\mathsf{BlockSubsidy}(\mathsf{height})$ function to
$\mathsf{ScheduledBlockSubsidy}(\mathsf{height})$ without changing its
definition. Define the final block subsidy as:

$$
\mathsf{BlockSubsidy}(\mathsf{height}) :=
\mathsf{ScheduledBlockSubsidy}(\mathsf{height}) +
\mathsf{NSMSubsidy}(\mathsf{height}).
$$

All existing allocations that are defined as a proportion of the block
subsidy MUST use this final value. Thus, while any funding stream is active,
its allocation applies to the sum of the scheduled subsidy and NSM subsidy.

The coefficient is the 25-second-block analogue of ZIP 234's decay
coefficient. It causes approximately half of a reserve balance to be reissued
over one post-NU7 halving interval when no additional fees are contributed.
Rounding the NSM subsidy upward ensures that any positive reserve balance is
eventually reissued.

## Transaction version deprecation

NU7 defines no new transaction version and makes no change to the encoding or
digest algorithms of version 5 or version 6 transactions.

For every transaction in a block at a height greater than or equal to the NU7
activation height, the transaction version number MUST be 5 or 6. A node MUST
reject a block containing a version 4 transaction. After NU7 activation on a
network, a node MUST also reject version 4 transactions submitted for mempool
acceptance or relay on that network.

Since Sprout JoinSplits can only be encoded in version 4 transactions, no
Sprout funds can be spent after NU7 activation. The Sprout chain value pool
balance remains part of consensus accounting, but MUST NOT be transferred to
the NSM reserve or otherwise reallocated by this ZIP.

## NU7 network constants

The following network upgrade constants are defined for NU7: [^zip-0200]

CONSENSUS_BRANCH_ID
: TBD

ACTIVATION_HEIGHT (NU7)
: Testnet: TBD
: Mainnet: TBD

NSM_REISSUANCE_HEIGHT
: Testnet: TBD (corresponding to February 2031)
: Mainnet: TBD (corresponding to February 2031)

MIN_NETWORK_PROTOCOL_VERSION (NU7)
: Testnet: TBD
: Mainnet: TBD

For each network, nodes compatible with NU7 activation on that network MUST
advertise a network protocol version greater than or equal to the corresponding
MIN_NETWORK_PROTOCOL_VERSION.

## Backward compatibility

Before NU7 activates on a network, NU7 and pre-NU7 nodes can connect to each
other. NU7 nodes will prefer other NU7 nodes, so pre-NU7 nodes will gradually
be disconnected approaching activation.

Once NU7 activates, NU7 nodes will disconnect peers that advertise a lower
network protocol version. Blocks produced under the pre-NU7 consensus rules
may also be rejected because of the new target spacing, subsidy calculation,
action limits, fee allocation, or transaction-version rule.

Version 5 and version 6 transactions remain structurally unchanged. This does
not imply that a transaction is valid across NU7 activation, because its
signatures commit to a consensus branch ID.


# Rationale

## Coinholder and ZCAP polling

The August and September 2026 NU7 polls asked five scope questions: whether to
preserve halvings or smooth issuance; when NSM reissuance should begin; when
version 4 transactions should be disabled; whether to deploy ZIP 218; and
whether to ship promptly with only features ready by the September 30
deadline. The poll announcement records the complete questions and response
options. [^nu7-poll-questions]

Approximately 2.4 million ZEC participated in the coinholder poll, representing
about 66% of the eligible shielded ZEC at the snapshot height. The selected
answers were overwhelming: [^nu7-poll-results]

| Question | Selected coinholder answer | Share of participating ZEC |
|----------|----------------------------|----------------------------|
| NSM issuance | Preserve halvings | 98.9% |
| NSM start date | February 2031 | 96.6% |
| Version 4 deprecation | At NU7 activation | 97.3% |
| ZIP 218 | Deploy 25-second blocks and action limits | 99.9% |
| Scope and readiness | Ship promptly without features missing the deadline | 99.3% |

The ZCAP results broadly supported the same reduced NU7 scope, but were less
decisive on issuance policy. On the issuance-curve question, 57 members chose
smoothing and 54 chose preserving halvings, so neither option received a
majority. The clear divergence concerned the reissuance start date: 67 ZCAP
members selected "as soon as possible", while 31 selected February 2031.
[^nu7-poll-results]

This ZIP follows the coinholder result by preserving halvings and beginning
reissuance in February 2031, while recording the differing ZCAP preference.
These polls are evidence of community sentiment; network upgrades ultimately
activate through adoption of compatible node software under the network
upgrade mechanism.

In the absence of a single outcome shared by both polls, the protocol could
either select February 2031 or leave the reissuance start date unspecified.
The former gives the protocol a definite outcome supported overwhelmingly by
coinholders. It also addresses the apparent preference of ZCAP members who
favored reissuance as soon as possible better than specifying no date at all.
The period before February 2031 leaves approximately five years in which a
later governance decision can move the start date earlier if there is
sufficient support for doing so.

## Rationale for the fee-only reserve

ZIP 235 proposes removing 60% of aggregate transaction fees and leaving the
remainder available to the miner. [^zip-0235] The NU7 form records the removed
fees directly in consensus state instead of requiring an explicit transaction
field. This permits the selected policy without a new transaction format.

ZIP 233's voluntary-removal mechanism depends on an additional transaction
bundle. Limiting the NU7 reserve to transaction fees keeps that mechanism out
of scope and preserves the poll's commitment to avoid transaction-format
changes.

## Rationale for preserving halvings

The Shielded Labs halving-preserving proposal demonstrates how to add a
decaying NSM subsidy on top of the scheduled subsidy without smoothing the
scheduled halving curve. [^halving-preserving-pr] This ZIP narrows that design
to fees accumulated after NU7 activation and delays reissuance until February
2031.

ZIP 234's coefficient is calibrated for 75-second blocks. ZIP 218 triples the
number of blocks per halving interval, so using that coefficient unchanged
would reissue the reserve approximately three times as quickly. The coefficient
$1375 / 10{,}000{,}000{,}000$ fits signed 64-bit fixed-point arithmetic when
multiplied by $\mathsf{MAX\_MONEY}$ and leaves approximately 50.007% of a
reserve after 5,040,000 blocks, closely preserving the intended four-year
half-life.

For each post-NU7 block, the increase in Issued Supply caused by these rules is
the Scheduled Block Subsidy plus the NSM subsidy, minus the NSM fee
contribution. The change in the NSM reserve is the fee contribution minus the
NSM subsidy. Therefore, the sum of Issued Supply and the NSM reserve changes by
exactly the Scheduled Block Subsidy. This invariant ensures that NSM
reissuance cannot increase the scheduled supply cap.

## Rationale for no new transaction format

Avoiding a new format limits parser and wallet disruption in the upgrade
immediately following the introduction of version 6 in NU6.3. [^zip-0229]
The fee contribution is a block-level consensus calculation and therefore does
not require a new field in ordinary or coinbase transactions.

## Rationale for version 4 rejection

Version 4 is the only remaining format that supports Sprout JoinSplits. Making
it invalid at NU7 activation gives a simple consensus boundary for Sprout
deprecation. Leaving the Sprout balance unspendable, rather than reallocating
it, matches the poll's explicit decision to leave disposition of those funds
outside its scope. [^nu7-poll-questions]


# Deployment

This ZIP is proposed for deployment with NU7 on Mainnet and Testnet. The
activation heights, branch ID, reissuance heights, and minimum network protocol
versions remain to be assigned.


# Open issues

* Assign the NU7 consensus branch ID and activation heights.
* Assign the Mainnet and Testnet heights corresponding to the selected
  February 2031 reissuance date.
* Assign the minimum network protocol versions.
* Add reference implementations and test vectors for the NSM reserve.


# References

[^BCP14]: [Information on BCP 14 — "RFC 2119: Key words for use in RFCs to Indicate Requirement Levels" and "RFC 8174: Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words"](https://www.rfc-editor.org/info/bcp14)

[^protocol]: [Zcash Protocol Specification, Version 2026.8.0 [NU6.3] or later](protocol/protocol.pdf)

[^protocol-networks]: [Zcash Protocol Specification, Version 2026.8.0 [NU6.3]. Section 3.12: Mainnet and Testnet](protocol/protocol.pdf#networks)

[^protocol-chainvaluepoolbalances]: [Zcash Protocol Specification, Version 2026.8.0 [NU6.3]. Section 4.17: Chain Value Pool Balances](protocol/protocol.pdf#chainvaluepoolbalances)

[^protocol-constants]: [Zcash Protocol Specification, Version 2026.8.0 [NU6.3]. Section 5.3: Constants](protocol/protocol.pdf#constants)

[^protocol-txnconsensus]: [Zcash Protocol Specification, Version 2026.8.0 [NU6.3]. Section 7.1.2: Transaction Consensus Rules](protocol/protocol.pdf#txnconsensus)

[^zip-0200]: [ZIP 200: Network Upgrade Mechanism](zip-0200.rst)

[^zip-0201]: [ZIP 201: Network Peer Management for Overwinter](zip-0201.rst)

[^zip-0218]: [ZIP 218: 25-second Block Target Spacing](zip-0218.md)

[^zip-0229]: [ZIP 229: Version 6 Transaction Format](zip-0229.md)

[^zip-0233]: [ZIP 233: Network Sustainability Mechanism: Removing Funds From Circulation](zip-0233.md)

[^zip-0234]: [ZIP 234: Network Sustainability Mechanism: Issuance Smoothing](zip-0234.md)

[^zip-0235]: [ZIP 235: Remove 60% of Transaction Fees From Circulation](zip-0235.md)

[^zip-0236]: [ZIP 236: Blocks should balance exactly](zip-0236.rst)

[^halving-preserving-pr]: [Shielded Labs PR 1354: Halving-preserving variant of ZIP 234](https://github.com/zcash/zips/pull/1354)

[^nu7-poll-questions]: [NU7 Coinholder Vote: poll questions and scope](https://forum.zcashcommunity.com/t/nu7-coinholder-vote/56912)

[^nu7-poll-results]: [NU7 Sentiment Polls Results](https://forum.zcashcommunity.com/t/nu7-sentiment-polls-results/57590)
