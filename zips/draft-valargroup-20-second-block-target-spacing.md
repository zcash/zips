
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
[^zip-0237]

A "stale block" is a valid mined block that does not remain on the selected
chain. This document reports "stale blocks per accepted block" separately
from the fraction of all mined blocks that become stale.

"Reach 90%" means the time for a block to reach 90% of the specified node
sample. "Effective old-tip mining time" means the accumulated mining work
spent on the old tip, expressed as seconds of the whole network's mining power.

MB means 1,000,000 bytes.


# Abstract

This proposal reduces block target spacing from 25 to 20 seconds in a
network upgrade after NU7. It builds on ZIP 218 without changing its action
limits or block size limit. [^zip-0218] [^zip-0259]

The change reduces the expected wait for a block by 20% and increases
capacity and maximum sustained processing work by 25%. It adjusts the
difficulty averaging window, issuance parameters, and duration-based node
defaults to the new spacing. Shorter inclusion intervals can expose finer
transaction timing information.

# Motivation

A 20-second target reduces the expected wait for a first confirmation by
five seconds. With unchanged per-block limits, it provides 25% more capacity
at the cost of 25% more maximum sustained validation and wallet sync work.
This proposal evaluates that incremental trade-off from ZIP 218's baseline.


# Privacy Implications

ZIP 218 identifies timing and anchor-depth privacy effects. [^zip-0218]
Shorter blocks give observers finer timing information without changing what
individual shielded transactions reveal.

A three-block anchor depth spans an expected 60 seconds instead of 75.
A rollback past the anchor invalidates the transaction. A replacement spending
the same notes exposes the same nullifiers, linking the two transactions.
Ordinary stale-block measurements do not bound rollback depth.

# Requirements

- Reduce target spacing from 25 to 20 seconds after NU7.
- Preserve approximately the difficulty averaging duration and issuance schedule,
  including partial halving intervals, subject to integer rounding.
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

## Action limits

This proposal does not change ZIP 218's action limits, global shielded budget,
or block size limit. Implementations MUST continue to enforce them.

## Minimum difficulty blocks on Testnet

Retain ZIP 218's 450-second elapsed-time threshold after this upgrade.
A block qualifies only if its timestamp is strictly more than 450 seconds
after the preceding block's timestamp. In that case its `nBits` MUST equal
$\mathsf{ToCompact}(\mathsf{PoWLimit})$, following ZIP 218.

At and after $A_{20}$, this fixed threshold replaces the expression
$18\cdot\mathsf{PoWTargetSpacing}(h)$. Thus 450 seconds does not qualify,
while 451 seconds does. This rule does not affect Mainnet.
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
This recommendation does not guarantee protection against reorganizations.


# Rationale

## Capacity and resource costs

With unchanged per-block limits, maximum sustained processing and sync work
increase by 25%. Two-action Orchard capacity rises from 6.6 to 8.25 transactions
per second. ZIP 218's compact-field model rises from approximately 169.10 to
211.38 MB/day; it excludes serialization and transport overhead. [^zip-0218]

**TODO:** add matched 25-second and 20-second verification, propagation, and
wallet sync measurements under sustained near-full-block workloads.

## Stale blocks and effective propagation time

Following ZIP 218's propagation analysis, we estimate stale blocks per
accepted block as the work-weighted time miners remain on the old tip divided
by target spacing: $\phi = \tau_{\mathrm{eff}}/T$. [^zip-0218]
[^propagation-report]

The Zebra-only devnet data accompanying the propagation report contains
621 block hashes at heights of at least 400 with bodies of at least
1,990,000 bytes. This near-full-block sample has a mean reach-90% time of
1.55994 seconds. [^propagation-report]

The mixed-client experiment uses 80 geographically distributed nodes:
40 run Zakura and 40 run Zebra. **TODO:** identify the mixed-run dataset and
report its reach-90% measurement. The 1.56-second input below comes from
the Zebra-only sample and has not been established for the mixed run.

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

ZIP 218 reports a 3.26% propagation-based estimate at 25 seconds.
[^zip-0218] Holding that effective delay fixed gives 4.08% at 20 seconds.
The near-full-block filter gives 4.29% under the same model. The difference
reflects the sample filter, rather than a different scaling rule.

**TODO:** publish the filtered dataset and calculation with node coverage
and timestamp semantics. The 4.29% value is a theoretical estimate, not an
observed 20-second stale rate. The reach proxy does not predict reorganization
depth.

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
[^zip-0207] [^zip-0214] Preserve fractional progress through the active address
period and define integer-boundary rounding. Keep ended streams ended and
ensure recipient lists cover every extended period. The deployment height
and schedule amendments must be settled together; changing NU7 constants
retroactively is invalid.


# Reference implementation

**TODO: link the implementation and activation vectors.** Cover the 25-to-20
transition, 102-to-128 averaging window, exact subsidy rounding, partial
halving intervals, funding schedules, NSM state continuity, and Testnet's
450/451-second boundary. Experiment configurations alone do not establish
an interoperable consensus implementation.


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
