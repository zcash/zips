
    ZIP: Unassigned
    Title: Reduce Block Target Spacing from 25 to 20 Seconds
    Owners: Dev Ojha <dev@valargroup.dev>
            Evan Forbes <evan@valargroup.dev>
    Status: Draft
    Category: Consensus
    Created: 2026-11-04
    License: MIT
    Discussions-To: <https://forum.zcashcommunity.com/t/proposal-lower-zcash-block-target-spacing-from-25s-to-20s/59035>


# Terminology

The key words "MUST", "MUST NOT", and "SHOULD" in this document are to be
interpreted as described in BCP 14 [^BCP14] when, and only when, they appear
in all capitals.

The terms "block chain", "consensus branch", and "network upgrade" follow
ZIP 200. [^zip-0200] The character § refers to sections of the Zcash Protocol
Specification. [^protocol]

"Block target spacing" means the interval between blocks targeted by the
difficulty adjustment algorithm. Actual block intervals vary.

The "25-second baseline" means the rules after NU7, including ZIP 218's
25-second target spacing and ZIP 237's subsidy definitions. [^zip-0218]
[^zip-0237]

An "orphan block" is a valid mined block that does not remain on the selected
chain. This document reports "orphan blocks per accepted block" separately
from the fraction of all mined blocks that become orphaned.

"Reach 90%" means the time for a block to reach 90% of the specified node
sample. "Effective old-tip mining time" means the accumulated mining work
spent on the old tip, expressed as seconds of the whole network's mining power.

MB means 1,000,000 bytes.


# Abstract

This proposal reduces block target spacing from 25 to 20 seconds in a
network upgrade after NU7. It builds on ZIP 218 and lowers its per-block
shielded action limits and global shielded budget by 20%, from 330 to 264
Orchard-protocol actions and from 300 to 240 Sapling inputs and outputs.
[^zip-0218] [^zip-0259] The block size limit is unchanged.

The change reduces the expected wait for a first confirmation by 20%.
Shielded throughput, worst-case light wallet bandwidth, and trial decryptions
per day are unchanged, apart from 25% more block headers. It adjusts the
difficulty averaging window, issuance parameters, and duration-based node
defaults to the new spacing. Shorter inclusion intervals can expose finer
transaction timing information.

# Motivation

A 20-second target reduces the expected wait for a first confirmation by
five seconds. ZIP 218 chose its shielded action limits to bound worst-case
light wallet sync bandwidth and trial decryptions per day. [^zip-0218]
Scaling those limits with the target spacing keeps these bounds, so mobile
and other light wallets pay only for the additional block headers.
This proposal evaluates that incremental trade-off from ZIP 218's baseline.


# Privacy Implications

ZIP 218 identifies timing and anchor-depth privacy effects. [^zip-0218]
Shorter blocks give observers finer timing information without changing what
individual shielded transactions reveal.

A three-block anchor depth spans an expected 60 seconds instead of 75.
A rollback past the anchor invalidates the transaction. A replacement spending
the same notes exposes the same nullifiers, linking the two transactions.
Ordinary orphan-block measurements do not bound rollback depth.

The smaller per-block action limits do not change the maximum shielded
throughput per unit time. Under sustained demand for a pool, ZIP 218's
observation that the limits can delay transactions and make their timing more
distinguishable continues to apply. [^zip-0218]

# Requirements

- Reduce target spacing from 25 to 20 seconds after NU7.
- Preserve approximately the difficulty averaging duration and issuance schedule,
  including partial halving intervals, subject to integer rounding.
- Preserve ZIP 218's worst-case shielded throughput, compact sync bandwidth for
  shielded data, and trial decryptions per day.
- Preserve historical consensus rules and integrate the transition with ZIP 237
  and active funding-stream schedules.

# Specification

This section applies to the post-NU7 rules of ZIPs 218 and 237.
[^zip-0218] [^zip-0237] Implementations MUST retain all pre-activation rules
at heights below the new activation height.

## Activation and target spacing

Define the following constants:

$$\mathsf{TwentySecondActivationHeight} : \mathbb{N}$$
$$\mathsf{TwentySecondPoWTargetSpacing} : \mathbb{N} := 20 \text{ seconds}$$
$$\mathsf{TwentySecondSpacingRatio} : \mathbb{Q}_{>0} := 25/20 = 5/4$$

A separate deployment ZIP will assign $\mathsf{TwentySecondActivationHeight}$
for each network. It MUST be strictly greater than that network's
$\mathsf{NU7ActivationHeight}$. No NU7 activation constant changes.

For a height $h \in \mathbb{N}$ at or above this activation height, define:

$$\mathsf{PoWTargetSpacing}(h) := \mathsf{TwentySecondPoWTargetSpacing}.$$

For $h < \mathsf{TwentySecondActivationHeight}$, retain ZIP 218's
definition of $\mathsf{PoWTargetSpacing}$.
In particular, $\mathsf{PostNU7PoWTargetSpacing}$ remains 25 seconds.

## Difficulty averaging window

The difficulty adjustment algorithm (DAA) averages over 128 blocks after
activation, replacing ZIP 218's 102-block window. The larger block count
preserves approximately the same expected averaging duration at the shorter
target spacing.

Define:

$$\mathsf{TwentySecondPoWAveragingWindow} : \mathbb{N} := 128.$$

For $h \geq \mathsf{TwentySecondActivationHeight}$, define:

$$\mathsf{PoWAveragingWindow}(h) := \mathsf{TwentySecondPoWAveragingWindow}.$$

For $h < \mathsf{TwentySecondActivationHeight}$, retain ZIP 218's
averaging window, including 102 blocks after NU7 activation. All uses of this
function in the difficulty algorithm use the height of the block under
consideration.

The averaging window includes pre-activation blocks when its lookback crosses
the activation height. Implementations MUST NOT reset it at activation.
ZIP 218's difficulty formulae therefore use:

- a 128-block lookback for $\mathsf{MeanTarget}(h)$;
- $\mathsf{ActualTimespan}(h) = \mathsf{MedianTime}(h) - \mathsf{MedianTime}(h-128)$;
- $\mathsf{AveragingWindowTimespan}(h) = 128\times20 = 2{,}560$ seconds.

The median-time span, damping factor, adjustment bounds, and proof-of-work
limit remain unchanged. Implementations MUST apply the existing difficulty
algorithm with these height-dependent inputs from the activation block;
there is no separate difficulty reset.

## Halving interval and scheduled subsidy

Define:

$$\mathsf{TwentySecondHalvingInterval} : \mathbb{N} := \mathsf{PostNU7HalvingInterval}\cdot 5/4 = 6{,}300{,}000.$$

For the following formula, let $A_{20} = \mathsf{TwentySecondActivationHeight}$,
$A_7 = \mathsf{NU7ActivationHeight}$, and
$A_B = \mathsf{BlossomActivationHeight}$. These are nonnegative integer heights.
For $h \geq A_{20}$, define:

$$\mathsf{Halving}(h) := \left\lfloor \frac{A_B-\mathsf{SlowStartShift}}{840{,}000} +\frac{A_7-A_B}{1{,}680{,}000} +\frac{A_{20}-A_7}{5{,}040{,}000} +\frac{h-A_{20}}{6{,}300{,}000} \right\rfloor.$$

The denominators are the pre-Blossom, post-Blossom, post-NU7, and 20-second
halving intervals, respectively. For $h < A_{20}$, retain ZIP 218's halving
function, including its slow-start cases. Implementations MUST preserve the fractional progress through the
halving interval at activation. They MUST NOT restart an interval at $A_{20}$.

For $h \geq A_{20}$, replace ZIP 237's scheduled subsidy with:

$$\mathsf{ScheduledBlockSubsidy}(h) := \left\lfloor \frac{\mathsf{MaxBlockSubsidy}}{2\cdot3\cdot(5/4)\cdot 2^{\mathsf{Halving}(h)}} \right\rfloor.$$

The factors 2, 3, and $5/4$ are the Blossom, NU7, and 20-second spacing
ratios, respectively. The result is a nonnegative integer number of zatoshi.
Implementations MUST use the exact rational ratio $5/4$ and apply the floor only to the complete
expression. Multiplying an already-rounded 25-second subsidy by $4/5$ can
produce a different answer.

For example, at halving index 3 the scheduled subsidy changes from
26,041,666 zatoshi to 20,833,333 zatoshi. Flooring
$26{,}041{,}666\times4/5$ would incorrectly produce 20,833,332 zatoshi.

## Integration with ZIP 237

For $h \geq A_{20}$, redefine ZIP 237's $\mathsf{HalvingInterval}(h)$ to return
$\mathsf{TwentySecondHalvingInterval}$. Retain its earlier cases for $h<A_{20}$.
Its existing fraction formula then gives:

$$\mathsf{BLOCK\_SUBSIDY\_FRACTION}(h) = \frac{\lfloor 6{,}931{,}680{,}000 / 6{,}300{,}000\rfloor}{10^{10}} = \frac{1100}{10^{10}}.$$

Retain ZIP 237's definition:

$$\mathsf{BlockSubsidy}(h) := \mathsf{ScheduledBlockSubsidy}(h) + \mathsf{AdditionalBlockSubsidy}(h).$$

Implementations MUST carry the existing NSM Value Balance through activation.
They MUST NOT reseed it or recompute historical balances under the new spacing.
ZIP 237's additional-subsidy ceiling and balance-update rules continue to apply.

**Open specification item:** define the NSM reissuance trigger for an
activation before reissuance starts. ZIP 259's fixed trigger heights use the
25-second issuance curve. The amended trigger must use the 20-second curve
and reissuance fraction. Its reference reserve must use cumulative scheduled
issuance through $h-1$, retaining each historical era's integer rounding.
If reissuance starts before this upgrade, retain that activated state.

## Shielded pool action limits

Define the following constants:

$$\mathsf{TwentySecondGlobalShieldedBudget} : \mathbb{N} := 264$$
$$\mathsf{TwentySecondOrchardProtocolBlockActionLimit} : \mathbb{N} := 264$$
$$\mathsf{TwentySecondSaplingBlockIOLimit} : \mathbb{N} := 240$$

Each value is the corresponding ZIP 218 constant multiplied by $4/5$, which is
exact for all three. [^zip-0218]

For each block at height $h \geq A_{20}$, ZIP 218's per-pool limits and
global shielded budget MUST be enforced with these constants in place of
$\mathsf{GlobalShieldedBudget}$, $\mathsf{OrchardProtocolBlockActionLimit}$,
and $\mathsf{SaplingBlockIOLimit}$, respectively. That is:

- $\sum_{\mathit{tx} \in \mathit{block}} \mathit{nActionsOrchard}(\mathit{tx}) \leq 264$;
- $\sum_{\mathit{tx} \in \mathit{block}} \mathit{nActionsIronwood}(\mathit{tx}) \leq 264$;
- $\sum_{\mathit{tx} \in \mathit{block}} (\mathit{nSpendsSapling}(\mathit{tx}) + \mathit{nOutputsSapling}(\mathit{tx})) \leq 240$;
- the shielded cost of the block, as defined by ZIP 218, is at most 264.

The definition of shielded cost, the per-pool structure of the limits, and the
2 MB block size limit are unchanged. For blocks at heights $h < A_{20}$,
ZIP 218's limits of 330, 330, and 300 continue to apply.

### Transactions exceeding a block limit at activation

A transaction that by itself would violate any of these limits cannot be
included in any block at a height $h \geq A_{20}$. This includes transactions
that satisfy ZIP 218's limits, such as one with 300 Orchard actions.

Nodes SHOULD NOT admit such a transaction to their mempool, or relay it, if
the candidate next block's height is at or above $A_{20}$. Nodes SHOULD evict
such transactions from their mempool when the candidate next block's height
reaches $A_{20}$. Wallets SHOULD NOT create such a transaction for a target
height at or above $A_{20}$.

## Minimum difficulty blocks on Testnet

Retain ZIP 218's threshold of $18 \cdot \mathsf{PoWTargetSpacing}(h)$ seconds,
evaluated with the new spacing. At and after $A_{20}$, the threshold is
therefore $18 \times 20 = 360$ seconds, rather than ZIP 218's 450 seconds.
A block qualifies only if its timestamp is strictly more than this threshold
after the preceding block's timestamp. Thus a gap of 360 seconds does not
qualify, while a gap of 361 seconds does. In that case the block's `nBits`
MUST equal $\mathsf{ToCompact}(\mathsf{PoWLimit})$, following ZIP 218.
This rule does not affect Mainnet.

Existing timestamp-validity bounds and local-clock tolerances remain unchanged.
The Testnet minimum-difficulty exception remains subject to those rules.

## Non-consensus node behaviour

When converting a height range to expected elapsed time, implementations
SHOULD use the target spacing applicable to each block. The expected time
from an accepted tip at height $a$ to height $b>a$ is
$\sum_{h=a+1}^{b} \mathsf{PoWTargetSpacing}(h)$, including the new spacing
for the activation block. Policies defined as elapsed durations SHOULD
retain those durations across activation.

### Transaction expiry

Wallets SHOULD increase the default expiry delta from 120 to 150 blocks.
Choose the default using the transaction's target height, which is the next
block height after the chain tip. Use 150 when that height is at or above
$A_{20}$; otherwise retain the prior default. Compute expiry relative to the
target height as specified by ZIP 218. Wallets SHOULD preserve an explicit
user-configured delta across activation.

### Block-count-based defaults

Implementations SHOULD use the following post-activation defaults where
they expose the corresponding settings. The table scales duration-based
values by $5/4$ relative to ZIP 218. Larger rollback windows conform.

| Constant | 25-second baseline | 20-second recommendation |
|----------|--------------------|--------------------------|
| `MAX_REORG_LENGTH` | At least 600 | At least 750 |
| `MAX_BLOCKS_IN_TRANSIT_PER_PEER` | 48 | 60 |
| `BLOCK_DOWNLOAD_WINDOW` | 3072 | 3840 |
| `MIN_BLOCKS_TO_KEEP` | 864 | 1080 |

The consensus coinbase maturity remains 100 blocks. This proposal leaves
`TX_EXPIRING_SOON_THRESHOLD` at 3 and
`NETWORK_UPGRADE_PEER_PREFERENCE_BLOCK_PERIOD` at 1728, following ZIP 218.

### Anchor selection depth

Wallets SHOULD retain ZIP 315's recommended anchor depth of 3 blocks.
[^zip-0315] Its expected duration changes from 75 to 60 seconds.


# Rationale

## Capacity and resource costs

ZIP 218 chose its shielded action limits so that worst-case light wallet sync
bandwidth does not increase relative to the pre-NU7 protocol. [^zip-0218]
Retaining those per-block limits at 20 seconds would raise the maximum number
of shielded actions per day, and with it worst-case compact sync bandwidth and
trial decryptions, by 25%. This proposal instead scales the limits by $4/5$,
so the daily maxima are unchanged. All three ZIP 218 values are multiples of
5, so no rounding is needed.

Using ZIP 218's compact-field model, which excludes serialization and
transport overhead, with $86{,}400/20 = 4{,}320$ blocks per day:

| Metric | 25-second baseline | 20-second proposal |
|--------|--------------------|--------------------|
| Blocks per day | 3,456 | 4,320 |
| Max Orchard + Ironwood actions/block | 330 | 264 |
| Max Sapling IOs/block | 300 | 240 |
| Max Orchard + Ironwood actions/day | 1,140,480 | 1,140,480 |
| Orchard or Ironwood compact BW/day | 168.79 MB | 168.79 MB |
| Sapling compact BW/day | 120.27 MB | 120.27 MB |
| Compact block headers/day | 0.31 MB | 0.39 MB |
| **Worst-case total BW/day** | **169.10 MB** | **169.18 MB** |
| Worst-case trial decrypts/day | \~2.3M | \~2.3M |

The binding constraint remains a block filled with Orchard or Ironwood
actions: $264 \times 148 \times 4{,}320 + 90 \times 4{,}320 = 169.18\textsf{ MB/day}$.
The only increase is the 25% more compact block headers, approximately
78 kB per day. The trial decryption count, counting both internal and external
incoming viewing keys as in ZIP 218, is $2 \times 264 \times 4{,}320 = 2{,}280{,}960$
per account per day, identical to ZIP 218.

These figures describe worst-case compact sync bandwidth when blocks fill the
shielded action budget. They do not establish a daily download requirement
for every wallet.

Maximum shielded throughput is also unchanged. Two-action Orchard or Ironwood
transactions remain limited to $\lfloor 264/2 \rfloor / 20 = 6.6$ transactions
per second, and four-IO Sapling transactions to $\lfloor 240/4 \rfloor / 20 = 3.0$
transactions per second, as in ZIP 218. The benefit of this proposal is lower
latency, not more shielded capacity.

The worst-case shielded verification work per block falls by 20%, while
the worst-case shielded verification work per unit time is approximately
unchanged. Batch verification amortizes some cost across a block, so slightly
smaller blocks may verify somewhat less efficiently per action. Fixed per-block
costs, such as header validation, chain state updates, and propagation
round trips, increase by 25% per unit time. Syncing blocks produced during a
given time offline requires processing 25% more headers.

The 2 MB block size limit is unchanged, so the maximum transparent data per
unit time increases by 25%. This affects full node bandwidth and storage, but
not light wallets that download only compact blocks.

## Orphan blocks and effective propagation time

With ZIP-218, there was measured work to evaluate the orphan rate, and re-org
rate in highly distributed testnets with full 2MB blocks. We repeat that
methodology, using 2 action Ironwood transactions until the original ZIP-218
limit, and then transparent transactions afterwards. These distributed networks
contain 80 equal-weighted miners, evenly spread across 12 regions (including
US-east, US-west, Australia, Amsterdam, London, Frankfurt, Bangalore,
Singapore). [^zip-0218]
[^propagation-report]

With 20s full blocks, with an all Zakura node network work as above, we
measured 1.9% orphan rates. This was using the older ZIP-218 action count, so
thereby having a higher verification load due to the increased number of ZKP's.
For reference this value is currently 1.45% on Zakura {TODO: Update this old
benchmark to latest}.

Since NU7 went live, we've seen orphan rate increase from 0.66% to 0.83%,
albeit block utilization is not constant in these time periods. The 0.66%
orphan rate is measured from a time period where blocks were on average 53kb
large, whereas the 0.85% is from a time period of 10kb on average.

## Difficulty averaging duration

ZIP 218's 102-block window at 25 seconds spans an expected 2,550 seconds.
The equivalent count at 20 seconds is 127.5 blocks. This proposal rounds
up to 128, giving 2,560 seconds, about 0.39% longer.

This proposal preserves the averaging duration because mining hash rate can
vary. Reducing that duration would change the DAA's response to hash rate
changes as well as changing block target spacing.

## Issuance and schedule continuity

The interval change preserves its expected duration:

$$6{,}300{,}000\times20=5{,}040{,}000\times25\text{ seconds}.$$

The halving formula retains progress through the 25-second era. Scaling the
unrounded scheduled subsidy by $4/5$ preserves the expected issuance rate
before rounding. Integer rounding changes the realized schedule.

The NSM fraction changes from $1375/10^{10}$ to $1100/10^{10}$, also a factor
of $4/5$. ZIP 237's ceiling and evolving balance mean this does not establish
exact equality of reissuance per unit of wall-clock time.

**Open specification item:** amend the funding-stream end heights and address
period calculations in ZIPs 207 and 214 for a second spacing transition.
[^zip-0207] [^zip-0214] Preserve fractional progress through the active address
period and define integer-boundary rounding. Keep ended streams ended and
ensure recipient lists cover every extended period. The deployment height
and schedule amendments must be settled together; changing NU7 constants
retroactively is invalid.


# Deployment

Deploy this proposal in a separate network upgrade after NU7. ZIP 259 defines
NU7's deployment; this proposal does not replace that deployment. [^zip-0259]
A separate deployment ZIP will assign this upgrade's activation heights and
consensus branch IDs.

Before this ZIP advances to Proposed status, resolve the funding-stream and
NSM reissuance-height specification items. Complete the activation and
rounding analysis against the selected deployment parameters.


# References

[^BCP14]: [Information on BCP 14](https://www.rfc-editor.org/info/bcp14)

[^protocol]: [Zcash Protocol Specification](protocol/protocol.pdf)

[^zip-0200]: [ZIP 200: Network Upgrade Mechanism](zip-0200.rst)

[^zip-0207]: [ZIP 207: Funding Streams](https://zips.z.cash/zip-0207)

[^zip-0214]: [ZIP 214: Consensus rules for a Zcash Development Fund](https://zips.z.cash/zip-0214)

[^zip-0218]: [ZIP 218: 25-second Block Target Spacing](https://zips.z.cash/zip-0218)

[^zip-0237]: [ZIP 237: Network Sustainability Mechanism: Halving-Preserving Issuance](https://zips.z.cash/zip-0237)

[^zip-0259]: [ZIP 259: Deployment of the NU7 Network Upgrade](https://zips.z.cash/zip-0259)

[^zip-0315]: [ZIP 315: Best Practices for Wallet Implementations](zip-0315.rst)

[^propagation-report]: [Zcash Block Time Reduction Appears Safe for NU7 w/ Zebra Only Devnet](https://forum.zcashcommunity.com/t/zcash-block-time-reduction-appears-safe-for-nu7-w-zebra-only-devnet/55586)
