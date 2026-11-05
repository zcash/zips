
    ZIP: Unassigned
    Title: Reduce Block Target Spacing from 25 to 20 Seconds
    Owners: Dev Ojha <dev@valargroup.dev>
            Evan Forbes <evan@valargroup.dev>
    Status: Draft
    Category: Consensus
    Created: 2026-11-04
    License: MIT


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
[^zip-0237] This is the baseline for the proposed transition, rather than
a claim that NU7 has already activated on every network.

A "stale block" is a valid mined block that does not remain on the selected
chain. This document reports "stale blocks per accepted block" separately
from the fraction of all mined blocks that become stale.

"Reach 90%" means the time for a block to reach 90% of the specified node
sample. "Effective old-tip mining time" means the accumulated mining work
spent on the old tip, expressed as seconds of the whole network's mining power.

MB means 1,000,000 bytes. TPS means transactions per second.


# Abstract

This proposal reduces Zcash's block target spacing from 25 seconds to
20 seconds in a network upgrade after NU7. It builds on ZIP 218, which
specifies the 25-second target for NU7. [^zip-0218] [^zip-0259]

The change reduces the expected wait for a first confirmation by 20%.
It provides 25% more blocks per unit of time. The proposal inherits the
2 MB block size limit and ZIP 218's shielded action limits. With those limits,
two-action Orchard capacity rises from 6.6 to 8.25 transactions per second.
The corresponding maximum daily compact sync payload also rises by 25%.

The proposal extends the halving interval by a factor of 5/4 and scales the
scheduled subsidy by 4/5 before integer rounding. It adjusts ZIP 237's
reissuance fraction to the new interval. It increases the difficulty averaging
window from 102 to 128 blocks to preserve approximately its existing duration.
It also adjusts node defaults that represent durations.

The proposal preserves the shielded transaction formats and action accounting
of the baseline. Shorter inclusion intervals can change timing information
visible to observers. This draft leaves deployment-dependent funding and
reissuance schedules, implementation vectors, and new measurements open for
completion before submission for Proposed status.


# Motivation

With a 25-second target, a user who needs one confirmation waits about
25 seconds under stable conditions. A 20-second target reduces that wait
by five seconds. Applications that need a small number of confirmations
benefit from the shorter intervals.

The proposal adds capacity through 25% more blocks per unit of time. It
retains the per-block limits already established by ZIP 218. This raises
both capacity and sustained processing costs by 25% relative to the
25-second baseline. The incremental cost is the central trade-off for this ZIP.

ZIP 218 established the initial block-spacing reduction and shielded resource
limits. This proposal asks whether the network has sufficient propagation
and validation margin for a further reduction to 20 seconds. It does not
prescribe lower confirmation counts or add a finality mechanism.


# Privacy Implications

This proposal preserves the baseline's shielded encryption and proof systems.
More frequent blocks can give observers finer information about inclusion
times. Fewer transactions per block at a fixed demand can also affect timing
analysis. Privacy review should assess those effects without treating a block
as the boundary of the shielded anonymity set.

The inherited action limits continue to constrain work per block. The higher
block frequency raises the maximum daily wallet sync work by 25%. The analysis
below distinguishes compact-field payload from all wallet traffic.


# Requirements

- Reduce block target spacing from 25 seconds to 20 seconds after NU7.
- Preserve the expected scheduled issuance and halving durations, subject to
  integer rounding, including progress through the halving interval at activation.
- Preserve ZIP 218's block size limit and shielded action accounting.
- Preserve approximately the baseline's difficulty averaging duration.
- Account for the 25% increase in maximum sustained processing and sync work.
- Integrate the transition with ZIP 237 and active funding-stream schedules.
- Leave historical consensus rules intact.


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

At earlier heights, retain ZIP 218's definition of $\mathsf{PoWTargetSpacing}$.
In particular, $\mathsf{PostNU7PoWTargetSpacing}$ remains 25 seconds.

## Difficulty averaging window

Define:

$$\mathsf{TwentySecondPoWAveragingWindow} : \mathbb{N} := 128.$$

For $h \geq \mathsf{TwentySecondActivationHeight}$, define:

$$\mathsf{PoWAveragingWindow}(h) := \mathsf{TwentySecondPoWAveragingWindow}.$$

At earlier heights, retain ZIP 218's definition, including its 102-block
post-NU7 window. All uses of this function in the difficulty algorithm use
the height of the block under consideration.

The averaging window includes pre-activation blocks when its lookback crosses
the activation height. Implementations MUST NOT reset it at activation.
The median-time span and adjustment bounds remain unchanged. The difficulty
algorithm moves toward the new spacing through ordinary retargeting.

## Halving interval and scheduled subsidy

Define:

$$\mathsf{TwentySecondHalvingInterval} : \mathbb{N}
:= \mathsf{PostNU7HalvingInterval}\cdot 5/4 = 6{,}300{,}000.$$

For the following formula, let $A_{20} = \mathsf{TwentySecondActivationHeight}$,
$A_7 = \mathsf{NU7ActivationHeight}$, and
$A_B = \mathsf{BlossomActivationHeight}$. These are nonnegative integer heights.
For $h \geq A_{20}$, define:

$$
\mathsf{Halving}(h) := \left\lfloor
\frac{A_B-\mathsf{SlowStartShift}}{\mathsf{PreBlossomHalvingInterval}}
+\frac{A_7-A_B}{\mathsf{PostBlossomHalvingInterval}}
+\frac{A_{20}-A_7}{\mathsf{PostNU7HalvingInterval}}
+\frac{h-A_{20}}{\mathsf{TwentySecondHalvingInterval}}
\right\rfloor.
$$

For $h < A_{20}$, retain the prior halving function, including its slow-start
cases. Implementations MUST preserve the fractional progress through the
halving interval at activation. They MUST NOT restart an interval at $A_{20}$.

For $h \geq A_{20}$, replace ZIP 237's scheduled subsidy with:

$$
\mathsf{ScheduledBlockSubsidy}(h) := \left\lfloor
\frac{\mathsf{MaxBlockSubsidy}}
{\mathsf{BlossomPoWTargetSpacingRatio}\cdot
 \mathsf{NU7PoWTargetSpacingRatio}\cdot
 \mathsf{TwentySecondSpacingRatio}\cdot 2^{\mathsf{Halving}(h)}}
\right\rfloor.
$$

The result is a nonnegative integer number of zatoshi. Implementations MUST
use the exact rational ratio $5/4$ and apply the floor only to the complete
expression. Multiplying an already-rounded 25-second subsidy by $4/5$ can
produce a different answer.

For example, at halving index 3 the scheduled subsidy changes from
26,041,666 zatoshi to 20,833,333 zatoshi. Flooring
$26{,}041{,}666\times4/5$ would incorrectly produce 20,833,332 zatoshi.

## Integration with ZIP 237

For $h \geq A_{20}$, redefine ZIP 237's $\mathsf{HalvingInterval}(h)$ to return
$\mathsf{TwentySecondHalvingInterval}$. Retain its earlier cases for $h<A_{20}$.
Its existing fraction formula then gives:

$$\mathsf{BLOCK\_SUBSIDY\_FRACTION}(h)
= \frac{\lfloor 6{,}931{,}680{,}000 / 6{,}300{,}000\rfloor}{10^{10}}
= \frac{1100}{10^{10}}.$$

Retain ZIP 237's definition:

$$\mathsf{BlockSubsidy}(h) := \mathsf{ScheduledBlockSubsidy}(h)
+ \mathsf{AdditionalBlockSubsidy}(h).$$

Implementations MUST carry the existing NSM Value Balance through activation.
They MUST NOT reseed it or recompute historical balances under the new spacing.
ZIP 237's additional-subsidy ceiling and balance-update rules continue to apply.

**Open specification item:** If this upgrade precedes NSM reissuance, its
reissuance-height rule needs an explicit amendment using the new scheduled
issuance curve and fraction. ZIP 259's fixed heights were calculated for
25-second blocks. This draft does not yet choose the amended trigger.
If reissuance has already started, the transition must retain that activated
state. Resolve both cases before this ZIP advances to Proposed status.

## Inherited shielded limits

Implementations MUST continue to enforce ZIP 218's shielded action limits
and global budget. This proposal introduces no new action accounting.
The inherited parameters are:

| Parameter | Value before and after this upgrade |
|-----------|-------------------------------------|
| Global shielded budget | 330 |
| Orchard-protocol action limit per pool | 330 |
| Sapling inputs plus outputs | 300 |
| Sprout JoinSplits | 0 |
| Block size limit | 2,000,000 bytes |

Orchard and Ironwood actions share the global budget as specified in ZIP 218.
This proposal does not activate any transaction format or pool.

## Minimum difficulty blocks on Testnet

Retain ZIP 218's 450-second elapsed-time threshold after this upgrade.
A block qualifies only if its timestamp is strictly more than 450 seconds
after the preceding block's timestamp. In that case its `nBits` MUST equal
$\mathsf{ToCompact}(\mathsf{PoWLimit})$, following ZIP 218.

At and after $A_{20}$, this fixed threshold replaces the expression
$18\cdot\mathsf{PoWTargetSpacing}(h)$. Thus 450 seconds does not qualify,
while 451 seconds does. This rule does not affect Mainnet.

## Non-consensus node behaviour

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
This recommendation does not guarantee protection against reorganizations.


# Rationale

## Incremental benefits and costs

The relevant comparison is 25 seconds versus 20 seconds. The upgrade reduces
the expected wait for a block by 20% and increases capacity per unit of time
by 25%. Retaining the per-block action limits also increases maximum daily
shielded sync work by 25%.

Scaling the action limits down by 20% would preserve the prior daily shielded
capacity. This draft instead retains those limits to obtain the additional
throughput. New measurements should assess the resulting sustained load.

## Stale blocks and effective propagation time

The initial investigation uses the previous post's model:
$\phi = \tau_{\mathrm{eff}}/T$, where $T$ is target spacing and $\phi$ is
expected stale blocks per accepted block. [^propagation-report]

Effective old-tip mining time accumulates the mining work still spent on
the old tip during propagation. For example, half the network mining the
old tip for one second contributes 0.5 effective seconds.

If dissemination rises linearly from 0% to 90% over 1.56 seconds, the
old-tip mining share falls from 100% to 10%. Its average is 55%, giving:

$$\tau_{\mathrm{eff}}\approx1.56\times0.55=0.858\text{ seconds}.$$

At 20 seconds, this gives $\phi\approx0.858/20=4.29\%$. It assumes nodes
represent mining work and omits any material tail after reaching 90%.
Remaining old-tip mining after that percentile adds to the effective time.

Under Poisson discovery, the chance of another block anywhere within
1.56 seconds is $1-e^{-1.56/20}\approx7.50\%$. That includes blocks found
by miners who already received the new tip. The effective-time model counts
only old-tip work. Its probability of at least one competitor is
$1-e^{-0.858/20}\approx4.20\%$, distinct from the expected count of 4.29%.

The rough 25-second baseline is about 3.2%. Scaling that rounded value alone
gives 4.0% at 20 seconds. The initial near-full-block analysis gives a mean
reach-90% time near 1.56 seconds, corresponding to 3.43% at 25 seconds and
4.29% at 20 seconds under the same proxy. These are theoretical estimates,
not measured 20-second stale rates.

**TODO: publish the reproducible near-full-block analysis and add a stable
reference.** Its current filter is height at least 400 and block body size
at least 1,990,000 bytes, with 621 block hashes. State the observed-node
coverage and propagation timestamp semantics. Add matched 25-second and
20-second runs, propagation percentiles, the tail, stale counts, and
reorganization depths. The reach proxy does not predict reorganization depth.

## Block processing time

The inherited limits preserve per-block validation bounds. The shorter target
requires processing 25% more worst-case blocks per unit of time. Full 2 MB
blocks contribute 100,000 bytes per second at 20 seconds, versus 80,000 at
25 seconds, before protocol overhead and retransmission.

**TODO: insert current verification and sustained-load measurements.** Cover
Orchard, Sapling, mixed-pool, and transparent workloads. Record revisions,
hardware, thread counts, block composition, and timing distributions.
Distinguish cold verification from use of transactions verified in the mempool.

## Shielded sync bandwidth analysis

The estimates below use the ZIP 218's compact-field model:
148 bytes per Orchard action, 32 bytes per Sapling spend, 116 bytes per
Sapling output, and approximately 90 bytes per compact block header.
[^zip-0218] They exclude transaction framing, serialization
overhead, memos, full-transaction fetches, and transport overhead.

An Orchard-only block contributes at most $330 \times 148 = 48{,}840$
bytes of compact action fields. An all-output Sapling block contributes
$300 \times 116 = 34{,}800$ bytes. These maxima cannot occur in the same
block because both pools consume the global budget. Under this field model,
Orchard maximizes compact Sapling-and-Orchard payload per budget unit.

| Metric | ZIP 218 baseline (25 seconds) | This proposal (20 seconds) |
|--------|--------------------|--------------------|
| Expected blocks/day | 3,456 | 4,320 |
| Orchard compact action fields/day | 168.79104 MB | 210.98880 MB |
| Sapling compact output fields/day, all-output workload | 120.26880 MB | 150.33600 MB |
| Approximate compact headers/day | 0.31104 MB | 0.38880 MB |
| Maximum compact fields plus headers/day in this model | 169.10208 MB | 211.37760 MB |
| Trial decryptions/day, two IVKs per Orchard action | 2,280,960 | 2,851,200 |

The 20-second estimate increases the 25-second baseline by 25%, from
169.10208 MB/day to 211.37760 MB/day under this field model. Compact header
traffic increases by 0.07776 MB/day. These are capacity estimates for the
specified workloads, not forecasts of ordinary wallet traffic.

**TODO: insert updated wallet sync measurements.** Validate the baseline,
serialized compact block sizes, trial decryption counts, and workload
assumptions. Include mixed-pool workloads and account separately for traffic
outside the compact-field model.

## Normal transaction throughput

For two-action Orchard transactions, the limit permits
$\lfloor 330 / 2 \rfloor = 165$ transactions per block:

$$165 / 20 = 8.25 \text{ TPS}.$$

The corresponding 25-second capacity is 6.6 TPS. For Sapling transactions
with two spends and two outputs, the limit permits 75 transactions per
block, or 3.75 TPS at 20 seconds instead of 3 TPS at 25 seconds.
These are separate single-pool capacities. Mixed-pool workloads share the
global budget and remain subject to the block size limit.

## Fee incentives and DoS resistance

The global budget bounds shielded counts regardless of the fee a miner
accepts. It does not reserve capacity for a particular pool or guarantee
transaction inclusion.

ZIP 317's conventional fee counts Sapling logical actions using the maximum
of spends and outputs. This proposal's Sapling budget counts their sum.
[^zip-0317] A transaction with two Sapling spends and two outputs therefore
uses four budget units but contributes two Sapling logical actions to the
fee calculation. Equal fees per budget unit across pools do not follow from
ZIP 317. This proposal leaves fee policy unchanged.

## Difficulty averaging duration

ZIP 218's 102-block window at 25 seconds spans an expected 2,550 seconds.
The equivalent count at 20 seconds is 127.5 blocks. This proposal rounds
up to 128, giving 2,560 seconds, about 0.39% longer. A 127-block window
would give 2,540 seconds. Keeping 102 blocks would shorten the duration
to 2,040 seconds.

**TODO: simulate activation from the 25-second target and 102-block window
to the 20-second target and 128-block window.** Include hash rate shocks,
network splits, timestamp effects, and recovery criteria.

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
[^zip-0207] [^zip-0214] Preserve elapsed periods and define rounding of
remaining durations at activation. Audit address-list bounds and other
height-based schedules. The new deployment height and schedule amendments
must be settled together; changing NU7 constants retroactively is invalid.


# Reference implementation

**TODO: link the implementation and activation vectors.** Cover the 25-to-20
transition, 102-to-128 averaging window, exact subsidy rounding, partial
halving intervals, funding schedules, NSM state continuity, and Testnet's
450/451-second boundary. Experiment configurations alone do not establish
an interoperable consensus implementation.


# Deployment

Deploy this proposal in a separate network upgrade after NU7. ZIP 259 defines
NU7's deployment; this proposal does not replace that deployment. [^zip-0259]
A future deployment ZIP will assign activation heights and consensus branch
IDs for this upgrade. This draft does not assign a network upgrade number.

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

[^zip-0317]: [ZIP 317: Proportional Transfer Fee Mechanism](zip-0317.rst)

[^propagation-report]: [Zcash Block Time Reduction Appears Safe for NU7 w/ Zebra Only Devnet](https://forum.zcashcommunity.com/t/zcash-block-time-reduction-appears-safe-for-nu7-w-zebra-only-devnet/55586)
