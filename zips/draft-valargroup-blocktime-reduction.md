
    ZIP: Unassigned
    Title: Shorter Block Target Spacing
    Owners: ValarDragon <dojha@berkeley.edu>
    Status: Draft
    Category: Consensus
    Created: 2026-03-13
    License: MIT
    Discussions-To: <https://forum.zcashcommunity.com/t/proposal-lower-zcash-block-target-spacing-to-25s/54577>


# Terminology

The key words "MUST", "MUST NOT", "SHOULD", and "MAY" in this document
are to be interpreted as described in BCP 14 [^BCP14] when, and only
when, they appear in all capitals.

The terms "block chain", "consensus rule change", "consensus branch",
and "network upgrade" are to be interpreted as defined in ZIP 200.
[^zip-0200]

The term "block target spacing" means the time interval between blocks
targeted by the difficulty adjustment algorithm in a given consensus
branch. It is normally measured in seconds. (This is also sometimes
called the "target block time", but "block target spacing" is the term
used in the Zcash Protocol Specification [^protocol-diffadjustment].)

The character § is used when referring to sections of the Zcash Protocol
Specification. [^protocol]

The terms "Mainnet" and "Testnet" are to be interpreted as described in
§ 3.12 'Mainnet and Testnet'. [^protocol-networks]


# Abstract

This proposal specifies a change in the block target spacing from 75
seconds to 25 seconds in NU7, and introduces per-pool action limits for
the Sapling and Orchard shielded protocols.

This solves three problems. 
- Significantly improves the UX for actors who need 1 or 2 conf's. (Near Intents, small payments) The user-latency goes down 3x.
- Increases consensus bandwidth, which amplifies the scaling impact of a future shielded pool which does not require shielded sync.
- Introduces action limits, which short term more than doubles the Orchard TPS (2.9 → 6.1 TPS), while lowering the impact a DoS attacker can impose on wallets for shielded sync by 42% (270.5 → 156.83 MB/day).

The action limits significantly decrease the number of Sprout and Sapling pool 
outputs available per block, to lower the maximum shielded sync burden under 
attempted DoS.

The emission schedule of mined ZEC will be the same in terms of ZEC/day, 
but this requires the emission per block to be adjusted
to take account of the changed block target spacing.

# Motivation

The motivations for decreasing the block target spacing are:

- **Reduced transaction latency.** Currently, users must wait
  75 seconds on average for even a single confirmation, regardless
  of network utilization. This creates friction for point-of-sale
  payments, exchange deposits, and cross-chain bridge operations. A
  25-second target spacing reduces the expected wait for a first
  confirmation to 25 seconds on average.

- **Greater throughput.** With 3× as many blocks per day and the same
  2 MB block size limit, we will have allocated higher consensus bandwidth 
  capacity. Short term, when paired with the action limits, we will more than 
  double the Orchard TPS for 2-action transactions. Longer term, when we get a 
  shielded pool with no shielded sync burden, we will have 3x higher throughput.

- **Complementary to finality improvements.** This proposal is
  complementary to, and does not compete with, finality mechanisms
  such as Crosslink [^crosslink]. Faster block times improve the
  responsiveness of the base layer regardless of whether an additional finality
  gadget is also deployed.

The throughput goal on its own could be achieved via a block size increase.
However the main goal of this proposal is to foremost improve the transaction
latency.

It is estimated that this reduction in blocktime would increase the stale rate from today's 0.4% to 1.3%. For reference, Ethereum operated at 5.4% stale rate.

There are multiple threat models for rollback attacks. Loosely speaking,
lowering block time while keeping it significantly lower than block propagation 
delay helps improve finality time. This is because more honest
miners quickly build on the block, and the block propagation constraint ensures
stale rates have not significantly increased. See [^slowfastblocks] for 
analysis in various attack models. As this proposal meets the constraint of
keeping stale rates low, this should under the "X% of hashpower is byzantine"
threat model improve user confirmation times by a factor slightly under 3x. 
Under the posts "Economic" threat model, where the user requires the block
rewards built on-top of their payment to exceed the value of the payment, this
significantly improves the variance in confirmation latency. (But makes the 
mean latency a bit higher due to stale rate) As noted there, this attack model
is not applied at sizable transactions. Its only potentially applied for small
value ones, where actually the granularity of block times likely lowers time
until sufficient finality. We do not argue for reducing wall-clock block 
confirmation counts aside from exisitng 1-2 confirmation users in this ZIP.
However, we do expect many classes of users to be able to wall-clock lower 
theirs under consistent threat modelling of what they choose today.

However, Zcash uniquely has a second cost on scaling, the shielded sync. Every 
shielded transaction induces a bandwidth overhead for every wallet
and an extra trial decryption, so we must carefully understand the impact a DOS 
attacker can cause. Today the worst case DOS attack can induce 270.5
MB of wallet sync download to clients per day, and 4.8M trial decrypts per
day. We propose introducing action limits in Orchard (306 actions per block),
and (input+output) limits for Sapling (300 per block). With these limits, the
worst case becomes 156.83 MB bandwidth and 2.1M trial decrypts per day. This 
is a 42% improvement in worst case wallet sync bandwidth despite 3x more blocks.
This yields a 2x in Orchard TPS, and keeps Sapling TPS at a higher level than
today's Orchard TPS.

However, every wallet does have to download every compact block header, which
is 90 bytes. This leads to an extra 200kb of wallet bandwidth per day in
exchange for the improved UX.

The reduced Sapling and Sprout per-block limits are justified by the
current distribution of shielded funds across pools. As of March 2026:

| Pool | Balance | Share of shielded supply |
|------|---------|--------------------------|
| Orchard | 4,511,193 ZEC | 87.5% |
| Sapling | 616,131 ZEC | 12.0% |
| Sprout | 25,480 ZEC | 0.5% |

The vast majority of shielded activity is already in Orchard, and this
trend is expected to continue. The Sapling and Sprout limits are set
generously relative to their current usage while substantially reducing
their potential for DOS abuse.

## Stale block rate

The stale rate is the percentage of blocks that get orphaned, which relates to 
mining centralization risk, block propagation delay, and block verification 
times. Today the stale rate is 0.4%, but this may be lower than what pure block
propagation delay may imply due to hashpower centralization in mining pools.

At 25-second block target spacing, the projected stale (orphan) block
rate is approximately 1.3% using theoretical models, or approximately
3.9% using significantly rounded-up estimates of Zcash network propagation 
delays. Both figures are well below Ethereum's historical stale rate of 5.4%
when it operated under proof-of-work. [^forum-proposal]

(TODO: Refine above numbers and expand on them. The 1.3% is derived from a very straightforward method, of estimating propagation delay using the current uncle
rate and block time as a poisson process. The 3.9% is taken from noticing that current p90 block propagation between EU and US nodes is 700ms, and then 
rounding that up to 1s. This needs to be combined with measuring latencies when the blocks are full, yet it is hard to see how this could risk approaching 2s.)

@evan-forbes is working on experiments to further show the block propagation delay, under different network and hardware configurations.


## Block processing time

A prerequisite for shorter block times is that block validation and
propagation remain small relative to the target spacing. The per-pool
action limits introduced by this proposal ensure that worst-case block
processing time is *lower* per block than today's. The increase in consensus
bandwidth, and Orchard TPS does mean that full node sync will increase in net
time. We accept this trade-off (TODO: be concrete with timing increases, and
remark that more CPU cores fixes this)

**Current worst case:** A full 2 MB block today can contain up to ~617
Orchard actions or ~2,090 Sapling outputs, with no per-pool limits. A fully
packed Orchard block requires verifying all action proofs and spend
authorization signatures for those ~617 actions.

**Proposed worst case:** With the action limits, a block contains at
most 306 Orchard actions or 300 Sapling IOs. This is roughly half the
current Orchard worst case and a fraction of the Sapling worst case.
The per-block verification work is therefore substantially reduced.

**Batch verification.** Orchard transaction verification benefits from
batch validation, where proof and signature verification is amortized
across multiple transactions. In current node implementations, Orchard
transactions are batch-verified in groups of up to 64 transactions
(each worst case being 2 actions). Zebra has performed batch
verification during live network syncing since version 3.0.0. With the
action limits, a worst-case block's Orchard bundle can be fully
batch-verified in a small number of batches.

**Estimated timing.** On a typical 4-core machine, worst-case full
block verification (including proof verification for all shielded
components) is estimated at under 500ms for a block at the
action limits. (TODO: Refine with easily citeable benchmarks)
When transactions have already been pre-verified upon
entering the mempool, which is the typical case for a node that has
been online, block validation reduces to checking signatures and
state updates, which is even cheaper.


# Specification

The changes described in this section are to be made in the Zcash
Protocol Specification [^protocol], relative to the specification as of
the activation of this proposal.

## Consensus changes

### Block target spacing

In § 2 'Notation', add $\mathsf{NU7ActivationHeight}$
and $\mathsf{PostNU7PoWTargetSpacing}$ to the list of
integer constants.

In § 5.3 'Constants', define:

$$\mathsf{PostNU7PoWTargetSpacing} := 25 \text{ seconds}$$

For a given network (production or test), define
$\mathsf{NU7ActivationHeight}$ as the height at which
this network upgrade activates on that network, as specified in a
separate deployment ZIP.

Define:

$$\mathsf{NU7PoWTargetSpacingRatio} := \mathsf{PostBlossomPoWTargetSpacing} \;/\; \mathsf{PostNU7PoWTargetSpacing} = 3$$

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

### Halving interval and block subsidy

Define:

$$\mathsf{PostNU7HalvingInterval} := \lfloor \mathsf{PostBlossomHalvingInterval} \cdot \mathsf{NU7PoWTargetSpacingRatio} \rfloor = 5{,}040{,}000$$

Redefine the $\mathsf{Halving}$ function as:

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
heights:

$$
\mathsf{BlockSubsidy}(\mathsf{height}) :=
  \begin{cases}
    \ldots &\text{(prior cases unchanged)} \\[1ex]
    \left\lfloor \dfrac{\mathsf{MaxBlockSubsidy}}{\mathsf{BlossomPoWTargetSpacingRatio} \cdot \mathsf{NU7PoWTargetSpacingRatio} \cdot 2^{\mathsf{Halving}(\mathsf{height})}} \right\rfloor,
      &\text{if } \mathsf{IsNU7Activated}(\mathsf{height})
  \end{cases}
$$

This divides the per-block subsidy by an additional factor of 3 relative
to the post-Blossom subsidy, so that the total issuance per unit of wall
clock time remains the same.

Note: the current post-Blossom block subsidy of 1.5625 ZEC does not
divide evenly by 3. The post-NU7 subsidy is
$\lfloor 156250000 / 6 \rfloor = 26041666$ zatoshi (0.26041666 ZEC),
losing approximately 0.33 zatoshi per block to rounding. Over a full
halving interval of 5,040,000 blocks this amounts to less than 0.017 ZEC
of total underpaid issuance, a negligible amount. Should any of the NSM ZIP's
be accepted, the difference can be credited to the NSM, else it will just be
under-minted from supply.

### Shielded pool action limits

Define the following constants in § 5.3 'Constants':

$$\mathsf{GlobalShieldedBudget} := 306$$
$$\mathsf{OrchardBlockActionLimit} := 306$$
$$\mathsf{SaplingBlockIOLimit} := 300$$
$$\mathsf{SproutBlockJoinSplitLimit} := 25$$

For each block at height $\mathsf{height}$ where
$\mathsf{IsNU7Activated}(\mathsf{height})$, the following limits MUST
be satisfied:

**Per-pool limits:**

- The total number of Orchard actions across all transactions in the
  block MUST NOT exceed $\mathsf{OrchardBlockActionLimit}$. That is,
  $\sum_{\mathit{tx} \in \mathit{block}} \mathit{nActionsOrchard}(\mathit{tx}) \leq 306$.

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

$$\sum_{\mathit{tx}} \mathit{nActionsOrchard}(\mathit{tx}) \;+\; \sum_{\mathit{tx}} (\mathit{nSpendsSapling}(\mathit{tx}) + \mathit{nOutputsSapling}(\mathit{tx})) \;+\; 2 \times \sum_{\mathit{tx}} \mathit{nJoinSplit}(\mathit{tx}) \;\leq\; 306$$

where the factor of 2 for Sprout JoinSplits reflects that each
JoinSplit produces 2 shielded outputs.

This global budget ensures that the worst-case shielded sync bandwidth
per block is bounded regardless of which combination of pools is used.
If a block's Orchard actions reach the limit of 306, no Sapling or
Sprout shielded outputs may be included. If both pools are used, their
combined cost must stay within the budget.

These limits do not apply to the transparent components of
transactions. The overall 2 MB block size limit continues to apply as
before.

#### Compact sync bandwidth per action

The limits above are chosen to bound the worst-case bandwidth that
lightweight wallets must download for shielded sync. The compact
representation used for syncing has the following per-note costs:

**Orchard:** 148 bytes per action, consisting of:

| Field | Size |
|-------|------|
| cmx (note commitment) | 32 bytes |
| nullifier | 32 bytes |
| ephemeral public key | 32 bytes |
| truncated note plaintext | 52 bytes |
| **Total** | **148 bytes** |

**Sapling:** 32 bytes per spend (input) and 116 bytes per output,
consisting of:

| Field | Size |
|-------|------|
| *Per spend:* nullifier | 32 bytes |
| *Per output:* cmu (note commitment) | 32 bytes |
| *Per output:* ephemeral public key | 32 bytes |
| *Per output:* truncated note plaintext | 52 bytes |
| **Per spend total** | **32 bytes** |
| **Per output total** | **116 bytes** |

With these limits, the worst-case compact sync bandwidth per block is:

- **Orchard:** $306 \times 148 = 45{,}288$ bytes
- **Sapling:** at most $300 \times 116 = 34{,}800$ bytes (all-output
  pathological case)

Due to the global shielded budget, these cannot stack: a block that
uses 306 Orchard actions has zero budget remaining for Sapling or
Sprout. The worst-case compact sync bandwidth per block is therefore
always bounded by the Orchard case at 45,288 bytes.

See the [Rationale](#rationale) section for the full daily bandwidth
analysis.

## Effect on difficulty adjustment

As with the Blossom activation [^zip-0208], the difficulty adjustment
parameters $\mathsf{PoWAveragingWindow}$ and
$\mathsf{PoWMedianBlockSpan}$ refer to numbers of blocks and do *not*
change at activation. The change in the effective value of
$\mathsf{PoWTargetSpacing}$ will cause the block spacing to adjust to
the new target at the normal rate for a difficulty adjustment.

It is likely that the difficulty adjustment for the first few blocks
after activation will be limited by $\mathsf{PoWMaxAdjustDown}$. This
is not anticipated to cause any problem.

## Minimum difficulty blocks on Testnet

On Testnet, the minimum-difficulty block threshold defined in ZIP 205
[^zip-0205] and modified by ZIP 208 [^zip-0208] continues to use
$6 \cdot \mathsf{PoWTargetSpacing}(\mathsf{height})$ seconds.
After activation, this threshold becomes $6 \times 25 = 150$ seconds.

## Non-consensus node behaviour

### Default expiry delta

When not overridden by the `-txexpirydelta` option, node
implementations that create transactions use a default expiry delta.
The current default of 40 blocks (approximately 50 minutes at 75-second
spacing) SHOULD change to
$\mathsf{NU7PoWTargetSpacingRatio} \times 40 = 120$
blocks after activation, to maintain the approximate expiry time of
50 minutes.

If the `-txexpirydelta` option is set, then the set value SHOULD be
used both before and after activation.

### Block-count-based constants

The following constants, measured in number of blocks, were reviewed.
Implementations SHOULD scale these by
$\mathsf{NU7PoWTargetSpacingRatio}$ where they represent
a time duration:

| Constant                                    | Current | Post-activation | Notes |
|---------------------------------------------|---------|-----------------|-------|
| `COINBASE_MATURITY`                         | 100     | 100             | No change; security measured in blocks |
| `MAX_REORG_LENGTH`                          | 99      | 99              | No change; follows `COINBASE_MATURITY` |
| `TX_EXPIRING_SOON_THRESHOLD`                | 3       | 3               | No change; |
| `MAX_BLOCKS_IN_TRANSIT_PER_PEER`            | 16      | 48              | Scale by 3 |
| `BLOCK_DOWNLOAD_WINDOW`                     | 1024    | 3072            | Scale by 3 |
| `MIN_BLOCKS_TO_KEEP`                        | 288     | 864             | Scale by 3; keep 6 hours worth of blocks |
| `NETWORK_UPGRADE_PEER_PREFERENCE_BLOCK_PERIOD` | 1728 | 1728           | No change;  |

### Anchor selection depth

ZIP 213 [^zip-0213] recommends selecting an anchor 10 blocks back from
the chain tip when constructing shielded transactions. The recommended
anchor depth SHOULD remain at 10 blocks after activation, reducing the
wall-clock anchor delay from ~12.5 minutes to ~4.2 minutes. This
follows the same precedent set by the Blossom upgrade (ZIP 208
[^zip-0208]), which halved the anchor delay from ~25 minutes to ~12.5
minutes without changing the 10-block depth.

| Parameter | Current | Post-activation | Notes |
|-----------|---------|-----------------|-------|
| Recommended anchor depth | 10 blocks (~12.5 min) | 10 blocks (~4.2 min) | No change; follows Blossom precedent |


# Rationale

## Shielded sync bandwidth analysis

The per-pool block space limits are chosen so that the worst-case daily
bandwidth for lightweight wallet syncing does not increase relative to
the current protocol. This section presents the analysis.

### Parameters

| Parameter | Value |
|-----------|-------|
| Block size limit | 2,000,000 bytes |
| Block target spacing | 25 seconds |
| Blocks per day | $ 86{,}400 / 25 = 3{,}456$ |
| Compact block header size | ~90 bytes |

**Orchard pool:**

| Parameter | Value |
|-----------|-------|
| $\mathsf{OrchardBlockActionLimit}$ | 306 actions |
| Compact sync bandwidth per action | 148 bytes |
| Compact bandwidth per block | $306 \times 148 = 45{,}288$ bytes |

**Sapling pool:**

| Parameter | Value |
|-----------|-------|
| $\mathsf{SaplingBlockIOLimit}$ | 300 (inputs + outputs) |
| Compact sync bandwidth per spend | 32 bytes |
| Compact sync bandwidth per output | 116 bytes |
| Compact bandwidth per block (worst case, all outputs) | $300 \times 116 = 34{,}800$ bytes |

### Daily bandwidth comparison

| Metric | Current (75s, no pool limits) | Proposed (25s, action limits) |
|--------|-------------------------------|-------------------------------|
| Blocks per day | 1,152 | 3,456 |
| Max Orchard actions/block | ~617 (block-size limited) | 306 |
| Max Sapling IOs/block | ~2,140 (block-size limited) | 300 |
| Orchard compact BW/day | ~105.2 MB | 156.52 MB |
| Sapling compact BW/day | ~270.38 MB | 120.27 MB |
| Compact block headers/day | ~0.10 MB | 0.31 MB |
| **Worst-case total BW/day** | **~270.5 MB** | **156.83 MB** |
| Worst-case trial decrypts/day | ~4.8M | ~2.1M |

The worst-case compact sync bandwidth is **156.83 MB/day**, a reduction
of **42%** from today's worst case of approximately 270.5 MB/day. This
is despite a 3× increase in block frequency and overall throughput
capacity.

The binding constraint is Orchard at 306 actions per block:
$306 \times 148 \times 3{,}456 + 90 \times 3{,}456 = 156.83\text{ MB/day}$.

The trial decryption count also decreases significantly, since the
per-block action limits more than offset the 3× increase in block count.

Note that the trial decrypt count is 2× the number of shielded
outputs/actions, because wallets must attempt decryption with both the
internal and external incoming viewing keys (IVKs). The internal IVK
detects change outputs sent back to the wallet, while the external IVK
detects incoming payments. In principle, wallets could avoid trial decrypts
with their IVK assuming other sync trade-offs are taken, but current Sapling and
Orchard wallets always attempt both.

### Normal transaction throughput

For standard 2-action Orchard transactions, the action limit of 306
allows $\lfloor 306 / 2 \rfloor = 153$ transactions per block, giving:

$$\mathsf{orchard\_tps} = 153 \;/\; 25 = 6.12 \text{ TPS}$$

For comparison, the current protocol (75s blocks, block-size limited)
supports approximately 2.9 TPS for 2-action Orchard transactions. This
is a **2.1× increase** in normal Orchard throughput.

**Sapling throughput.** For standard Sapling transactions (2 spends + 2
outputs = 4 IOs), the limit of 300 IOs allows $\lfloor 300 / 4 \rfloor
= 75$ transactions per block, giving $75 / 25 = 3.0$ TPS. Even with
the reduced Sapling limit, the post-NU7 Sapling TPS (3.0) still
exceeds the current pre-NU7 Orchard TPS (2.9).

### Fee incentives and DoS resistance

A concern with per-pool limits is that a DoS attacker could fill
the Sapling or Sprout budget to crowd out Orchard transactions (or vice
versa). The global shielded budget prevents this from being worse than
filling any single pool, but it is worth examining whether fee
incentives create an asymmetry.

Under ZIP 317 [^zip-0317], the conventional fee is based on *logical
actions*: each Sapling output or spend counts as one logical action, and
each Orchard action counts as one logical action. The marginal fee per
logical action is the same regardless of pool. Therefore, an attacker
gains no fee advantage by spamming Sapling instead of Orchard (or vice
versa). The cost per unit of shielded budget consumed is identical.

Furthermore, because the global shielded budget is shared, filling
the Sapling budget necessarily reduces the Orchard budget by the same
amount. An attacker who spends their entire budget on Sapling spam at
300 IOs leaves only 6 Orchard actions available in that block. But
this attack is no cheaper than filling 306 Orchard actions directly,
since the per-action fee is the same. The global budget ensures that
the total shielded sync cost per block is bounded to 306 units
regardless of the attacker's pool choice.

The Orchard per-pool cap of 306 also guarantees that legitimate Orchard
transactions always have access to the full Orchard budget when Sapling
and Sprout are not used, which is the expected common case going
forward.


# Deployment

This proposal is intended to be deployed as part of NU7, should tokenholder polling and developer consensus agree on it. A separate ZIP will specify the deployment details including
activation heights and consensus branch IDs.


# References

[^BCP14]: [Information on BCP 14 — "RFC 2119: Key words for use in RFCs to Indicate Requirement Levels" and "RFC 8174: Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words"](https://www.rfc-editor.org/info/bcp14)

[^protocol]: [Zcash Protocol Specification, Version 2025.6.3 or later](protocol/protocol.pdf)

[^protocol-networks]: [Zcash Protocol Specification, Version 2025.6.3. Section 3.12: Mainnet and Testnet](protocol/protocol.pdf#networks)

[^protocol-constants]: [Zcash Protocol Specification, Version 2025.6.3. Section 5.3: Constants](protocol/protocol.pdf#constants)

[^protocol-diffadjustment]: [Zcash Protocol Specification, Version 2025.6.3. Section 7.7.3: Difficulty adjustment](protocol/protocol.pdf#diffadjustment)

[^protocol-txnencoding]: [Zcash Protocol Specification, Version 2025.6.3. Section 7.1: Transaction Encoding and Consensus](protocol/protocol.pdf#txnencoding)

[^zip-0200]: [ZIP 200: Network Upgrade Mechanism](zip-0200.rst)

[^zip-0205]: [ZIP 205: Deployment of the Sapling Network Upgrade](zip-0205.rst)

[^zip-0206]: [ZIP 206: Deployment of the Blossom Network Upgrade](zip-0206.rst)

[^zip-0208]: [ZIP 208: Shorter Block Target Spacing](zip-0208.rst)

[^zip-0213]: [ZIP 213: Shielded Coinbase](zip-0213.rst)

[^zip-0315]: [ZIP 315: Best Practices for Wallet Implementations](zip-0315.rst)

[^zip-0317]: [ZIP 317: Proportional Transfer Fee Mechanism](zip-0317.rst)

[^crosslink]: [Crosslink — a Zcash Finality Protocol](https://electric-coin-company.github.io/zcash-crosslink/)

[^slowfastblocks]: [On Slow and Fast Block Times](https://blog.ethereum.org/2015/09/14/on-slow-and-fast-block-times/)

[^forum-proposal]: [Forum: Proposal — Lower Zcash Block Target Spacing to 25s](https://forum.zcashcommunity.com/t/proposal-lower-zcash-block-target-spacing-to-25s/54577)
