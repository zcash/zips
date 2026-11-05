
    ZIP: Unassigned
    Title: 20-second Block Target Spacing
    Owners: Dev Ojha <dev@valargroup.dev>
            Evan Forbes <evan@valargroup.dev>
    Status: Draft
    Category: Consensus
    Created: 2026-11-04
    License: MIT


# Terminology

The key words "MUST", "MUST NOT", "SHOULD", and "SHOULD NOT" in this document
are to be interpreted as described in BCP 14 [^BCP14] when, and only when,
they appear in all capitals.

The terms "block chain", "consensus rule change", "consensus branch", and
"network upgrade" follow ZIP 200. [^zip-0200]

"Block target spacing" means the interval between blocks targeted by the
difficulty adjustment algorithm. Actual block intervals vary.

The character § refers to sections of the Zcash Protocol Specification.
The terms "Mainnet" and "Testnet" follow § 3.12. [^protocol-networks]

A "stale block" is a valid mined block that does not remain on the selected
chain. A "stale block rate" is the fraction of valid mined blocks that become
stale over a stated measurement interval.

MB means 1,000,000 bytes. TPS means transactions per second.


# Abstract

This proposal reduces Zcash's block target spacing from 75 seconds to
20 seconds at NU7 activation. It follows the 25-second proposal's approach
to subsidy scaling, difficulty adjustment, and shielded pool action limits.
[^25-second-proposal] The 20-second target replaces the proposed 25-second
target; this ZIP does not assume an intervening upgrade to 25-second blocks.

The change reduces the expected wait for a first confirmation and increases
block capacity per unit of time. It retains the 2 MB block size limit and
the earlier proposal's per-block shielded limits: a global budget of 330,
330 Orchard actions, 300 Sapling inputs plus outputs, and 25 Sprout
JoinSplits. These limits support up to 8.25 two-action Orchard transactions
per second under an Orchard-only workload.

The proposal scales the subsidy and halving interval to preserve the
expected issuance schedule, subject to integer rounding. It increases the
difficulty averaging window to 64 blocks to approximate the existing
wall-clock window. It also updates node defaults that represent durations.

The shielded limits constrain wallet sync work under sustained load.
Shorter blocks can change transaction timing information visible to
observers. This draft leaves slots for measurements of 20-second block
propagation, stale blocks, verification, wallet sync, and difficulty recovery.


# Motivation

Users who need one confirmation currently wait an average of 75 seconds
under stable conditions. A 20-second target reduces that expected wait by
73.3%. Relative to the proposed 25-second target, it reduces the wait by
20% and provides 25% more blocks per unit of time.

At the same 2 MB block size limit, the network can carry 3.75 times as many
block bytes per unit of time as at 75 seconds. The shielded action limits
constrain the shielded portion of that capacity. With the same per-block
limits as the 25-second proposal, the additional blocks also provide 25%
more shielded capacity per unit of time.

This proposal retains the earlier proposal's scope and analysis categories.
The additional measurements will establish how much validation and
propagation margin remains at 20 seconds. The proposal does not add a
finality mechanism or prescribe a reduction in confirmation counts.
Applications still need confirmation policies suited to their rollback risk.


# Privacy Implications

This proposal does not change shielded transaction encryption or proof
systems. More frequent blocks can give observers finer information about
transaction inclusion times. Fewer transactions per block at a fixed demand
can also affect timing analysis. The privacy review should assess these
effects without treating a block as the boundary of the shielded anonymity set.

The action limits constrain the work that an attacker can impose on wallets
through shielded sync. The bandwidth estimates below cover compact Sapling
and Orchard fields. They do not establish a bound on all wallet traffic.


# Requirements

- Reduce the expected wait for a first confirmation to 20 seconds under
  stable hash rate and network conditions.
- Preserve the expected issuance and halving schedule in wall-clock time,
  subject to integer rounding.
- Retain the 2 MB block size limit and the 25-second proposal's shielded
  action limits.
- Keep worst-case shielded sync work below the pre-upgrade baseline under
  the same workload and accounting model.
- Preserve approximately the existing difficulty averaging duration.
- Define the activation behavior for Mainnet and Testnet.


# Specification

This section specifies changes to the Zcash Protocol Specification.
[^protocol] Rules before NU7 activation remain unchanged.

All activation heights, halving intervals, averaging windows, and action
limits defined here are nonnegative integers. Target spacings are positive
integer numbers of seconds. The spacing ratio is a positive rational number.
Block subsidies are nonnegative integer numbers of zatoshi.

## Consensus changes

### Block target spacing

In § 2 'Notation', add $\mathsf{NU7ActivationHeight}$
and $\mathsf{PostNU7PoWTargetSpacing}$ to the list of
integer constants.

In § 5.3 'Constants', define:

$$\mathsf{PostNU7PoWTargetSpacing} := 20 \text{ seconds}$$

For a given network (production or test), define
$\mathsf{NU7ActivationHeight}$ as the height at which
this network upgrade activates on that network, as specified in a
separate deployment ZIP.

Define:

$$\mathsf{NU7PoWTargetSpacingRatio} := \mathsf{PostBlossomPoWTargetSpacing} \;/\; \mathsf{PostNU7PoWTargetSpacing} = 15/4$$

Define $\mathsf{IsNU7Activated}(\mathsf{height})$ to
return true if
$\mathsf{height} \geq \mathsf{NU7ActivationHeight}$,
otherwise false.

In § 7.7.3 'Difficulty adjustment', redefine $\mathsf{PoWTargetSpacing}$
as:

$$
\mathsf{PoWTargetSpacing}(\mathsf{height}) :=
  \begin{cases}
    \mathsf{PreBlossomPoWTargetSpacing},                  &\text{if not } \mathsf{IsBlossomActivated}(\mathsf{height}) \\\\
    \mathsf{PostBlossomPoWTargetSpacing},                  &\text{if } \mathsf{IsBlossomActivated}(\mathsf{height}) \text{ and not } \mathsf{IsNU7Activated}(\mathsf{height}) \\\\
    \mathsf{PostNU7PoWTargetSpacing}        &\text{otherwise}
  \end{cases}
$$

### Averaging window [averaging-window]

In § 2 'Notation', add $\mathsf{PostNU7PoWAveragingWindow}$ to the
list of integer constants.

In § 5.3 'Constants', define:

$$\mathsf{PostNU7PoWAveragingWindow} := 64$$

In § 7.7.3 'Difficulty adjustment', redefine
$\mathsf{PoWAveragingWindow}$ as a height-dependent function:

$$
\mathsf{PoWAveragingWindow}(\mathsf{height}) :=
  \begin{cases}
    17,                                  &\text{if not } \mathsf{IsNU7Activated}(\mathsf{height}) \\\\
    \mathsf{PostNU7PoWAveragingWindow}   &\text{otherwise}
  \end{cases}
$$

All other references to $\mathsf{PoWAveragingWindow}$ in
§ 7.7.3 'Difficulty adjustment' that previously took the constant
value 17 are reinterpreted as
$\mathsf{PoWAveragingWindow}(\mathsf{height})$ for the height of the
block under consideration. This includes the size of the averaging
window used to compute the average target threshold and the average
block timespan.

### Halving interval and block subsidy

Define:

$$\mathsf{PostNU7HalvingInterval} := \lfloor \mathsf{PostBlossomHalvingInterval} \cdot \mathsf{NU7PoWTargetSpacingRatio} \rfloor = 6{,}300{,}000$$

For heights below $\mathsf{SlowStartShift}$, retain
$\mathsf{Halving}(\mathsf{height}) = 0$. For all other heights, redefine
the $\mathsf{Halving}$ function as:

$$
\mathsf{Halving}(\mathsf{height}) :=
  \begin{cases}
    \left\lfloor \dfrac{\mathsf{height} - \mathsf{SlowStartShift}}{\mathsf{PreBlossomHalvingInterval}} \right\rfloor,
      &\text{if not } \mathsf{IsBlossomActivated}(\mathsf{height}) \\\\[1.5ex]
    \left\lfloor \dfrac{\mathsf{BlossomActivationHeight} - \mathsf{SlowStartShift}}{\mathsf{PreBlossomHalvingInterval}}
      + \dfrac{\mathsf{height} - \mathsf{BlossomActivationHeight}}{\mathsf{PostBlossomHalvingInterval}} \right\rfloor,
      &\text{if } \mathsf{IsBlossomActivated}(\mathsf{height}) \text{ and not } \mathsf{IsNU7Activated}(\mathsf{height}) \\\\[1.5ex]
    \left\lfloor \dfrac{\mathsf{BlossomActivationHeight} - \mathsf{SlowStartShift}}{\mathsf{PreBlossomHalvingInterval}}
      + \dfrac{\mathsf{NU7ActivationHeight} - \mathsf{BlossomActivationHeight}}{\mathsf{PostBlossomHalvingInterval}}
      + \dfrac{\mathsf{height} - \mathsf{NU7ActivationHeight}}{\mathsf{PostNU7HalvingInterval}} \right\rfloor,
      &\text{otherwise}
  \end{cases}
$$

Redefine $\mathsf{BlockSubsidy}$ to add a case for post-activation
heights. The prior Blossom case in § 7.8 'Calculation of Block Subsidy
and Founders' Reward', currently written as "otherwise", must be
amended to "if $\mathsf{IsBlossomActivated}(\mathsf{height})$ and not
$\mathsf{IsNU7Activated}(\mathsf{height})$":

$$
\mathsf{BlockSubsidy}(\mathsf{height}) :=
  \begin{cases}
    \ldots &\text{(prior cases, with the Blossom case amended as above)} \\\\[1ex]
    \mathsf{floor}\left(\dfrac{\mathsf{MaxBlockSubsidy}}{\mathsf{BlossomPoWTargetSpacingRatio} \cdot \mathsf{NU7PoWTargetSpacingRatio} \cdot 2^{\mathsf{Halving}(\mathsf{height})}}\right),
      &\text{if } \mathsf{IsNU7Activated}(\mathsf{height})
  \end{cases}
$$

Implementations MUST evaluate the spacing ratio as the exact rational number
$15/4$. They MUST apply the floor only after evaluating the complete subsidy
expression. Integer division of 75 by 20 before this calculation would give
an incorrect subsidy.

For example, at halving index 2, the post-Blossom subsidy is 156,250,000
zatoshi. The post-NU7 subsidy becomes:

$$\left\lfloor 156{,}250{,}000 \times 4 / 15 \right\rfloor
  = 41{,}666{,}666 \text{ zatoshi}.$$

Rounding removes $2/3$ zatoshi per block in this example. Over a full
6,300,000-block interval at that subsidy, the difference from the unrounded
schedule is 0.042 ZEC. The formula uses the actual halving index at each
height; this example does not fix the activation height.

### Shielded pool action limits

Define the following constants in § 5.3 'Constants':

$$\mathsf{GlobalShieldedBudget} := 330$$
$$\mathsf{OrchardBlockActionLimit} := 330$$
$$\mathsf{SaplingBlockIOLimit} := 300$$
$$\mathsf{SproutBlockJoinSplitLimit} := 25$$

For each block at height $\mathsf{height}$ where
$\mathsf{IsNU7Activated}(\mathsf{height})$, validators MUST enforce the following limits:

**Per-pool limits:**

- The total number of Orchard actions across all transactions in the
  block MUST NOT exceed $\mathsf{OrchardBlockActionLimit}$. That is,
  $\sum_{\mathit{tx} \in \mathit{block}} \mathit{nActionsOrchard}(\mathit{tx}) \leq 330$.

- The total number of Sapling inputs and outputs across all
  transactions in the block MUST NOT exceed
  $\mathsf{SaplingBlockIOLimit}$. That is,
  $\sum_{\mathit{tx} \in \mathit{block}} (\mathit{nSpendsSapling}(\mathit{tx}) + \mathit{nOutputsSapling}(\mathit{tx})) \leq 300$.

- The total number of Sprout JoinSplits across all transactions in
  the block MUST NOT exceed $\mathsf{SproutBlockJoinSplitLimit}$. That
  is,
  $\sum_{\mathit{tx} \in \mathit{block}} \mathit{nJoinSplit}(\mathit{tx}) \leq 25$.

**Global shielded budget:**

In addition to the per-pool limits, the total shielded cost across all
pools in a block MUST NOT exceed $\mathsf{GlobalShieldedBudget}$. The
shielded cost of a block is defined as:

$$\sum_{\mathit{tx}} \mathit{nActionsOrchard}(\mathit{tx}) \;+\; \sum_{\mathit{tx}} (\mathit{nSpendsSapling}(\mathit{tx}) + \mathit{nOutputsSapling}(\mathit{tx})) \;+\; 2 \times \sum_{\mathit{tx}} \mathit{nJoinSplit}(\mathit{tx}) \;\leq\; 330$$

where the factor of 2 for Sprout JoinSplits reflects that each
JoinSplit produces 2 shielded outputs.

This global budget bounds the combined shielded counts regardless of which
combination of pools a block contains.

These limits do not apply to the transparent components of
transactions. The overall 2 MB block size limit continues to apply as
before.


## Effect on difficulty adjustment

The difficulty adjustment algorithm uses the new target spacing and
averaging window starting with the activation block. Its lookback includes
pre-activation blocks where the window crosses the activation height.
Implementations MUST NOT reset the window at activation or require that
all 64 blocks come from the new consensus branch.

The parameter $\mathsf{PoWMedianBlockSpan}$ remains unchanged.
The existing adjustment bounds continue to apply. The algorithm adjusts
the difficulty toward the new spacing through ordinary retargeting;
this proposal does not introduce a separate difficulty reset.

## Minimum difficulty blocks on Testnet

The Testnet minimum-difficulty threshold continues to use
$6 \cdot \mathsf{PoWTargetSpacing}(\mathsf{height})$ seconds, following
ZIP 205 and ZIP 208. [^zip-0205] [^zip-0208]
After activation, this threshold is $6 \times 20 = 120$ seconds.

## Non-consensus node behaviour

### Default expiry delta

Node implementations that create transactions SHOULD change the default
expiry delta from 40 to 150 blocks after activation. This preserves an
expected expiry duration of 50 minutes. If the user sets `-txexpirydelta`,
implementations SHOULD use that value before and after activation.

### Block-count-based constants

Implementations SHOULD use the following post-activation defaults where
they expose the corresponding settings. These defaults scale duration-based
values by $15/4$ and retain the earlier proposal's other values.
Implementations SHOULD NOT interpret these defaults as a change to
consensus rules.

| Constant | Before activation | After activation | Rationale |
|----------|-------------------|------------------|-----------|
| `COINBASE_MATURITY` | 100 | 100 | Retain the consensus maturity rule |
| `MAX_REORG_LENGTH` | 99 | 99 | Retain the relationship to coinbase maturity |
| `TX_EXPIRING_SOON_THRESHOLD` | 3 | 3 | Retain the block-count threshold |
| `MAX_BLOCKS_IN_TRANSIT_PER_PEER` | 16 | 60 | Scale by 15/4 |
| `BLOCK_DOWNLOAD_WINDOW` | 1024 | 3840 | Scale by 15/4 |
| `MIN_BLOCKS_TO_KEEP` | 288 | 1080 | Preserve about six hours of blocks |
| `NETWORK_UPGRADE_PEER_PREFERENCE_BLOCK_PERIOD` | 1728 | 1728 | Retain the block-count period |

### Anchor selection depth

Wallets SHOULD retain ZIP 315's recommended anchor selection depth of
3 blocks. [^zip-0315] At 20 seconds, that depth represents an expected
60 seconds instead of 225 seconds at 75 seconds or 75 seconds at 25 seconds.
This recommendation does not guarantee protection against reorganizations.


# Rationale

## Choice of 20 seconds

The proposal carries forward the 25-second design with a shorter target.
The shorter target provides another 20% reduction in the expected wait for
a block. Retaining the same per-block shielded limits also raises their
per-day capacity and cost by 25% relative to the 25-second proposal.

Reducing the action limits in proportion to the target spacing would retain
the 25-second proposal's daily shielded capacity. This draft instead retains
the per-block limits to obtain the additional throughput. The measurements
below will support review of this choice.

## Stale block rate

Shorter block intervals give miners less time to receive and validate a
block before another miner finds a competing block. The relevant evidence
includes propagation latency, validation latency, hash rate distribution,
and network topology.

The 25-second proposal provides historical context. Its results are not
measurements of this proposal. An Ethereum proof-of-work stale block rate
is a comparison point, not a universal safety threshold.

**TODO: insert the 20-second experiment results.** Record the source
revisions, node implementations, node count, regions, CPU allocations,
mining calibration, block composition, measurement duration, and trace
coverage. Report observed block spacing, stale block rate, the definition
and rate of forks, reorganization depths, and propagation percentiles.
Include a comparable 25-second run where available.

## Block processing time

The per-block shielded limits match the 25-second proposal. The shorter
spacing therefore increases the frequency of worst-case blocks without
increasing their permitted shielded action counts. The network must sustain
25% more block-processing work per unit of time than under that proposal.

Full 2 MB blocks at 20-second spacing contribute 100,000 bytes per second
(0.8 Mbit/s) of block data before protocol overhead and retransmission.
A full node also needs capacity for transaction relay, peer fanout, state
updates, and catching up after downtime.

**TODO: insert current block verification benchmarks.** Cover Orchard,
Sapling, Sprout, mixed-pool, and transparent workloads within the limits.
Report hardware, software revisions, thread counts, block composition,
sample counts, and timing distributions. Distinguish cold verification from
verification that uses transactions already verified in the mempool.

## Shielded sync bandwidth analysis

The estimates below use the 25-second proposal's compact-field model:
148 bytes per Orchard action, 32 bytes per Sapling spend, 116 bytes per
Sapling output, and approximately 90 bytes per compact block header.
[^25-second-proposal] They exclude transaction framing, serialization
overhead, memos, full-transaction fetches, and transport overhead.

An Orchard-only block contributes at most $330 \times 148 = 48{,}840$
bytes of compact action fields. An all-output Sapling block contributes
$300 \times 116 = 34{,}800$ bytes. These maxima cannot occur in the same
block because both pools consume the global budget. Under this field model,
Orchard maximizes compact Sapling-and-Orchard payload per budget unit.

| Metric | 25-second proposal | 20-second proposal |
|--------|--------------------|--------------------|
| Expected blocks/day | 3,456 | 4,320 |
| Orchard compact action fields/day | 168.79104 MB | 210.98880 MB |
| Sapling compact output fields/day, all-output workload | 120.26880 MB | 150.33600 MB |
| Approximate compact headers/day | 0.31104 MB | 0.38880 MB |
| Maximum compact fields plus headers/day in this model | 169.10208 MB | 211.37760 MB |
| Trial decryptions/day, two IVKs per Orchard action | 2,280,960 | 2,851,200 |

The 20-second estimate is approximately 21.9% below the earlier proposal's
pre-upgrade baseline of 270.5 MB/day under its accounting assumptions.
The extra compact header traffic relative to 75-second blocks is about
0.28512 MB/day. These estimates do not bound Sprout wallet synchronization.

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

## Difficulty averaging window [difficulty-averaging-window]

The 75-second target with a 17-block window spans an expected 1,275 seconds.
The 25-second proposal preserves that duration exactly with 51 blocks.
At 20 seconds, the equivalent count would be 63.75 blocks.

This proposal rounds up to 64 blocks, giving an expected duration of
1,280 seconds. That differs from the existing duration by five seconds,
or approximately 0.39%. A 63-block window would span 1,260 seconds.
Retaining 17 blocks would shorten the duration to 340 seconds.

The longer window approximates the existing smoothing duration. It does
not prevent difficulty from falling during a sustained loss of hash rate
or network split. Recovery time depends on the complete adjustment
algorithm and the sequence of observed blocks.

**TODO: insert difficulty adjustment simulations for the 20-second target
and 64-block window.** Cover activation from 75 seconds, hash rate increases
and decreases, and sustained network splits. Report transient spacing,
recovery criteria, block counts, elapsed time, and effects of timestamp
rules. The earlier 25-second simulations do not establish these results.

## Issuance and height-based schedules

The ratio $75/20 = 15/4$ requires exact rational arithmetic. Scaling the
halving interval to 6,300,000 blocks preserves its expected duration:

$$6{,}300{,}000 \times 20 = 1{,}680{,}000 \times 75 \text{ seconds}.$$

Scaling the subsidy by $4/15$ preserves expected issuance before rounding.
The halving formula accounts for elapsed intervals before activation.

**TODO: reconcile this draft with the final NU7 issuance and funding-stream
ZIPs.** Audit funding periods, lockbox rules, and other height-based schedules
against the chosen activation height. Include subsidy vectors immediately
before and after activation and each affected halving boundary.


# Reference implementation

**TODO: link the implementation of the 20-second target, 64-block averaging
window, subsidy calculation, and action limits.** Include activation-boundary
and mixed-pool budget test vectors. Experiment-specific configurations alone
do not establish an interoperable consensus implementation.


# Deployment

This proposal targets NU7, subject to community agreement and the network
upgrade process. A separate deployment ZIP will specify Mainnet and Testnet
activation heights and consensus branch IDs.

This draft replaces the 25-second target under discussion. It does not
schedule a second transition after a 25-second upgrade.


# References

[^BCP14]: [Information on BCP 14](https://www.rfc-editor.org/info/bcp14)

[^25-second-proposal]: [25-second Block Target Spacing](draft-valargroup-blocktime-reduction.md)

[^protocol]: [Zcash Protocol Specification](protocol/protocol.pdf)

[^protocol-networks]: [Zcash Protocol Specification, § 3.12: Mainnet and Testnet](protocol/protocol.pdf#networks)

[^zip-0200]: [ZIP 200: Network Upgrade Mechanism](zip-0200.rst)

[^zip-0205]: [ZIP 205: Deployment of the Sapling Network Upgrade](zip-0205.rst)

[^zip-0208]: [ZIP 208: Shorter Block Target Spacing](zip-0208.rst)

[^zip-0315]: [ZIP 315: Best Practices for Wallet Implementations](zip-0315.rst)

[^zip-0317]: [ZIP 317: Proportional Transfer Fee Mechanism](zip-0317.rst)
