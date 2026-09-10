```
ZIP: unassigned
Title: Network Sustainability Mechanism: Halving-Preserving Issuance
Owners: Judah Caruso <judah@shieldedlabs.net>
Original-Authors: Nathan Wilcox
                  Jason McGee
                  Zooko Wilcox
                  Mark Henderson
                  Tomek Piotrowski
                  Mariusz Pilarek
                  Paul Dann
Credits: Conrado Gouvea
Status: Draft
Category: Consensus
Created: 2026-08-19
License: BSD-2-Clause
Discussions-To: <https://github.com/zcash/zips/issues/1353>
```


# Terminology

The key words "MUST" and "MUST NOT" in this document are to be interpreted as
described in BCP 14 [^BCP14] when, and only when, they appear in all capitals.

The term "network upgrade" in this document is to be interpreted as described
in ZIP 200. [^zip-0200]

The character § is used when referring to sections of the Zcash Protocol
Specification. [^protocol]

The terms "Mainnet" and "Testnet" are to be interpreted as described in
§ 3.12 ‘Mainnet and Testnet’. [^protocol-networks]

The symbol "$\,\cdot\,$" means multiplication, as described in § 2 ‘Notation’.
[^protocol-notation]

"ZEC/TAZ" refers to the native currency of Zcash on a given network, i.e.
ZEC on Mainnet and TAZ on Testnet.

The terms "Block Subsidy" and "Issuance" are to be interpreted as described in
ZIP 233. [^zip-0233]

Let $\mathsf{PostBlossomHalvingInterval}$ be as defined in [^protocol-diffadjustment].

$\mathsf{MAX\_MONEY}$, as defined in § 5.3 ‘Constants’ [^protocol-constants],
is the total ZEC/TAZ supply cap measured in zatoshi, corresponding to
21,000,000 ZEC. This is slightly larger than the supply cap for the current
issuance mechanism, but is the value used in existing critical consensus
checks.

"Issued Supply" - The Issued Supply at a given height of a block chain is
the total ZEC/TAZ value in all chain value pool balances at that height, as
calculated by $\mathsf{IssuedSupply}(\mathsf{height})$ defined in
§ 4.17 ‘Chain Value Pool Balances’. [^protocol-chainvaluepoolbalances]

"Money Reserve" - The Money Reserve at a given height of a block chain is
the total ZEC/TAZ value remaining to be issued, as calculated by
$\mathsf{MAX\_MONEY} - \mathsf{IssuedSupply}(\mathsf{height})$.

"Scheduled Block Subsidy" - The block subsidy given by the existing halving
schedule, i.e. $\mathsf{BlockSubsidy}(\mathsf{height})$ as defined in § 7.8
‘Calculating Block Subsidy, Funding Streams, Lockbox Disbursement, and Founders'
Reward’ [^protocol-subsidies] prior to this ZIP, renamed
$\mathsf{ScheduledBlockSubsidy}(\mathsf{height})$ in the Specification below.

"Expected Issued Supply" - The Issued Supply that the existing halving schedule
would have produced at a given height had every block subsidy and fee been
claimed in full and no ZEC/TAZ been removed from circulation;
$\mathsf{ExpectedIssuedSupply}(\mathsf{height})$ is defined in the Specification
below.

"Issuance Deficit" - The amount by which the Issued Supply at a given height
falls below the Expected Issued Supply, i.e. the total ZEC/TAZ that the
existing halving schedule would have issued by that height but that is not in
any chain value pool: funds removed from circulation via ZIP 233
[^zip-0233], plus block subsidy and fees left unclaimed by coinbase
transactions prior to NU6 [^zip-0236].
$\mathsf{IssuanceDeficit}(\mathsf{height})$ is defined in the Specification
below.


# Abstract

This ZIP proposes a change to how nodes calculate the block subsidy.

The step function around the 4-year halving intervals inherited from Bitcoin
is retained unchanged. In addition, each block issues a fixed portion of the
current Issuance Deficit (the ZEC/TAZ that the existing schedule would already
have issued but which has been removed from circulation or left unclaimed), so
that such funds are reissued along a smooth curve on top of the existing
schedule.

The new issuance scheme is identical to the existing schedule whenever no
ZEC/TAZ has been removed from circulation or left unclaimed, and retains the
existing supply cap (which is below $\mathsf{MAX\_MONEY}$). It is proposed as
an alternative to ZIP 234 [^zip-0234], from which its structure and much of
its text are adapted.


# Motivation

The current block reward halving schedule is fixed and does not provide a way
to “recycle” funds removed from circulation via ZIP 233 into future issuance.
Once scheduled issuance ends, the network becomes reliant on transaction fees
for the security budget.

Key Objectives:

1. We want to introduce an automated mechanism that allows users of the network
   to contribute to the long-term sustainability of the network.
2. We want to enable ZEC that has been removed from circulation to be reissued
   in the future to benefit network sustainability.
3. We want to retain the existing ZEC supply cap of 21 million.
4. We want the issuance rate to remain identical to the historical rate for
   Zcash (and before that, Bitcoin), including the 4-year halving structure,
   whenever no ZEC/TAZ has been removed from circulation or left unclaimed.
5. We want issuance to be easy for all network users to understand and predict.
6. We want to preserve Zcash's existing 4-year halving schedule.

This ZIP is a variation of ZIP 234 [^zip-0234] that differs only in Key
Objective 6. ZIP 234 replaces the halving schedule with a smooth curve in order
to reissue funds removed from circulation; this ZIP shows that reissuance does
not require that change. The halving schedule is a long-standing, widely
understood property of Zcash on which block subsidy recipients and the wider
community rely, and this ZIP allows the question of whether to change it to be
decided on its own merits.

This NSM-based issuance scheme preserves the core aspects of Zcash's issuance
policy, the halving schedule, and the 21-million-coin cap. Critically,
it establishes the intended path for ZEC that has been voluntarily removed from
circulation, as well as transaction fees that are deliberately redirected into
the reserve: these funds are automatically and algorithmically reissued over
future block subsidies, ensuring they benefit the network's long-term security.

# Requirements

Reissuing funds removed from circulation while preserving halvings is possible
using an exponential decay formula applied to the Issuance Deficit that
satisfies the following requirements:

1. The issuance can be summarized into a reasonably simple explanation.
2. If no ZEC/TAZ is removed from circulation (and every subsidy is claimed in
   full), block subsidies are identical to the existing halving schedule.
3. If the Issuance Deficit is greater than 0, then the additional block
   subsidy must be non-zero, so that funds removed from circulation are
   eventually fully reissued.
4. For any 4-year period, the additional block subsidies paid out are
   approximately equal to half of the Issuance Deficit at the beginning of
   that 4-year period, if no ZEC/TAZ is removed from circulation during those
   4 years.
5. Decrease the short-term impact of the deployment of this ZIP on block subsidy
   recipients, and minimize the potential reputation risk to Zcash of changing
   the block subsidy amount.

# Specification

## Parameters

$\mathsf{BLOCK\_SUBSIDY\_FRACTION} = 4126 / 10\_000\_000\_000 = 0.0000004126$

$\mathsf{DEPLOYMENT\_BLOCK\_HEIGHT} =$ the NU7 activation height on the
relevant network. It MUST be no earlier than the NU7 activation height, and
MUST be at least 1.

## Changes to the Zcash Protocol Specification

In § 7.8 ‘Calculating Block Subsidy, Funding Streams, Lockbox Disbursement, and
Founders' Reward’ [^protocol-subsidies]:

Rename the existing function $\mathsf{BlockSubsidy}(\mathsf{height})$ to
$\mathsf{ScheduledBlockSubsidy}(\mathsf{height})$, leaving its definition
unchanged.

Add the following definitions, where $\mathsf{IssuedSupply}$ is as defined in
§ 4.17 ‘Chain Value Pool Balances’ [^protocol-chainvaluepoolbalances]:

$\mathsf{ExpectedIssuedSupply}(\mathsf{height}) := \sum_{\mathsf{h}=0}^{\mathsf{height}} \mathsf{ScheduledBlockSubsidy}(\mathsf{h})$

$\mathsf{IssuanceDeficit}(\mathsf{height}) := \mathsf{ExpectedIssuedSupply}(\mathsf{height}) - \mathsf{IssuedSupply}(\mathsf{height})$

Define $\mathsf{BlockSubsidy}(\mathsf{height})$ as:

$$\mathsf{BlockSubsidy}(\mathsf{height}) := \begin{cases}
\mathsf{ScheduledBlockSubsidy}(\mathsf{height}), & \text{if } \mathsf{height} < \mathsf{DEPLOYMENT\_BLOCK\_HEIGHT} \\
\mathsf{ScheduledBlockSubsidy}(\mathsf{height}) + \mathsf{ceiling}(\mathsf{BLOCK\_SUBSIDY\_FRACTION} \cdot \mathsf{IssuanceDeficit}(\mathsf{height} - 1)), & \text{otherwise}
\end{cases}$$

Add $\mathsf{BLOCK\_SUBSIDY\_FRACTION}$, with the value given under
Parameters above, to § 5.3 ‘Constants’ [^protocol-constants].

All other uses of $\mathsf{BlockSubsidy}(\mathsf{height})$ in the protocol
specification ($\mathsf{FoundersReward}$, $\mathsf{fsValue}$ and hence
$\mathsf{totalDeferredOutput}$, $\mathsf{MinerSubsidy}$, and the total input
value of a coinbase transaction in § 7.1.2 [^protocol-txnconsensus]) are
unchanged and refer to the redefined function; in particular, funding streams
receive their fixed percentage of the total (scheduled plus additional) block
subsidy. Note that $\mathsf{BlockSubsidy}(\mathsf{height})$ now depends on the
chain value pool balances after block $\mathsf{height} - 1$, and not only on
$\mathsf{height}$.

In § 4.17 ‘Chain Value Pool Balances’ [^protocol-chainvaluepoolbalances], add
the consensus rule:

> [NU7 onward] If $\mathsf{IssuanceDeficit}(\mathsf{height})$ would become
> negative in the block chain created as a result of accepting a block at
> $\mathsf{height}$, then all nodes MUST reject the block as invalid.

## Applicability

All of these changes apply identically to Mainnet and Testnet.


# Rationale

* Leaving the existing schedule in place and applying an exponential decay
  function only to the Issuance Deficit satisfies **Requirements 1**, **2**
  and **4** above.
* We round up to the next zatoshi to satisfy **Requirement 3** above. Since
  $\mathsf{BLOCK\_SUBSIDY\_FRACTION} < 1$ and the Issuance Deficit is a
  non-negative integer number of zatoshi, the additional subsidy never exceeds
  the Issuance Deficit, so the Issued Supply never exceeds the Expected Issued
  Supply and the supply cap is preserved.
* By § 7.1.2 [^protocol-txnconsensus], the net increase in the Issued Supply
  from a block is at most $\mathsf{BlockSubsidy}(\mathsf{height})$ (fees and
  lockbox disbursements are transfers between pools), so the Issuance Deficit
  can never become negative unless an implementation is in error. The
  consensus rule above makes such an error a block-validity failure rather than
  silently clamping the value.
* This ZIP makes the exact value of the Issued Supply at every height
  consensus-critical, since a one-zatoshi disagreement about the chain value
  pool balances would produce different block subsidies. Implementations MUST
  compute the chain value pool balances in § 4.17 identically from genesis.
  (The same applies to ZIP 234.)
* The issuance formula depends only on `IssuanceDeficit(height - 1)` (derived
  from the Issued Supply and the height) and a single constant fraction, making
  it simple to implement, explain, and verify.

## Rationale for Parameters

Because the formula reduces to the existing schedule whenever the Issuance
Deficit is zero, activation can occur at any height and no special activation
height is needed. The only change at activation is the reissuance of the
Issuance Deficit existing at that point, at
$\mathsf{BLOCK\_SUBSIDY\_FRACTION}$ per block. For example, if a total of
100,000 ZEC were removed from circulation prior to activation, then at
activation the issuance would be larger than the Scheduled Block Subsidy by
$100\_000\textsf{ ZEC} \cdot \mathsf{BLOCK\_SUBSIDY\_FRACTION}$, which we
calculate equals $0.04126$ ZEC. This example is chosen to demonstrate that a
very large amount removed from circulation (much larger than expected) would
elevate issuance by a relatively small amount, satisfying **Requirement 5**.

Since NU6, coinbase transactions are required to claim the full miner subsidy
and fees [^zip-0236], so the part of the Issuance Deficit not attributable to
funds removed from circulation is a fixed historical amount: on Mainnet
approximately 365 ZEC (estimated from the NSM Simulator's predicted supply at
that height; TODO for ZIP owner: confirm $\mathsf{IssuanceDeficit}$ at height
2,726,399 from a full node), which is reissued from activation at an initial
rate of about 0.00015 ZEC per block.

## BLOCK_SUBSIDY_FRACTION

Let $\mathsf{IntendedIssuanceDeficitFractionRemainingAfterFourYears} = 0.5$.

The value $4126 / 10\_000\_000\_000$ satisfies the approximation within $\pm 0.003\%$:

$(1 - \mathsf{BLOCK\_SUBSIDY\_FRACTION})^\mathsf{PostBlossomHalvingInterval} \approx \mathsf{IntendedIssuanceDeficitFractionRemainingAfterFourYears}$

This implies that after a period of 4 years around half of the Issuance
Deficit will have been issued as additional block subsidies, thus satisfying
**Requirement 4**.

The largest possible value of the Issuance Deficit is less than
$\mathsf{MAX\_MONEY}$, in the theoretically possible case that all issued funds
are removed from circulation. If this happened, the largest interim sum in the
block subsidy calculation would be less than
$\mathsf{MAX\_MONEY} \cdot 4126 / 10\_000\_000\_000$.

This uses at most 62.91 bits, which is just under the 63-bit limit for signed
two's complement 64-bit integer amount types.

The numerator could be brought closer to the limit by using a larger
denominator, but the difference in the amount issued would be very small. So we
chose a power-of-10 denominator for simplicity.

## Visualization of the Halving-Preserving Curve

The following graph compares issuance for the current halving-based step
function vs this ZIP, assuming 100 ZEC per day is removed from circulation
from activation (assumed at height 3,687,123 for illustration). With no
removals (and every subsidy claimed in full) the two lines coincide.

![A graph showing a comparison of the current halving-based step function vs the halving-preserving NSM issuance](../rendered/assets/images/draft-judah-nsm-halving-preserving-issuance-block_subsidy.png)

The graph below shows the balance of the Money Reserve assuming this ZIP is
implemented, under the same removal schedule.

![A graph showing the balance of the Money Reserve assuming halving-preserving issuance is implemented](../rendered/assets/images/draft-judah-nsm-halving-preserving-issuance-balance.png)


# Appendix: Simulation

A [fork](https://github.com/ShieldedLabs/zsf-simulator/tree/halving-preserving-issuance)
of the [NSM Simulator](https://github.com/eigerco/zsf-simulator) allows us to
simulate the effects of this ZIP on the Money Reserve and the block subsidy, as
well as generate plots like the ones above. Assuming that 100 ZEC per day is
removed from circulation from activation, this fragment of its output:

```
Halving  3 at block  4406400:
  NSM subsidies:    138028653049305 (~ 1380286.530 ZEC, 0.80365268 to 0.83585478 ZEC per block)
  legacy subsidies: 131250000000000 (~ 1312500.000 ZEC, 0.78125000 ZEC per block)
  difference:         6778653049305 (~   67786.530 ZEC),         NSM/legacy: 1.0516
  removed in period: 14583333333333 (~  145833.333 ZEC)
```

shows that the difference between this and the existing halving schedule during
the first full halving period after activation consists almost entirely of the
reissuance of funds removed from circulation (the remainder being reissuance of
the pre-NU6 shortfall); with no ZEC removed (and every subsidy claimed in full)
the difference is exactly 0 at every height.


# Appendix: Considerations for the Future

Future protocol changes may not increase the payout rate of the Issuance
Deficit to a reasonable approximation beyond the four year half-life
constraint.


# Deployment

This ZIP is proposed to activate with Network Upgrade 7. [^draft-arya-deploy-nu7]
It MUST be deployed at the same time or after ZIP 233 ("NSM: Removing Funds From
Circulation" [^zip-0233]), and MUST NOT be deployed together with ZIP 234.
[^zip-0234]


# References

[^BCP14]: [Information on BCP 14 — "RFC 2119: Key words for use in RFCs to Indicate Requirement Levels" and "RFC 8174: Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words"](https://www.rfc-editor.org/info/bcp14)

[^protocol]: [Zcash Protocol Specification, Version 2025.6.2 [NU6.1] or later](protocol/protocol.pdf)

[^protocol-notation]: [Zcash Protocol Specification, Version 2025.6.2 [NU6.1]. Section 2: Notation](protocol/protocol.pdf#notation)

[^protocol-networks]: [Zcash Protocol Specification, Version 2025.6.2 [NU6.1]. Section 3.12: Mainnet and Testnet](protocol/protocol.pdf#networks)

[^protocol-chainvaluepoolbalances]: [Zcash Protocol Specification, Version 2025.6.2 [NU6.1]. Section 4.17: Chain Value Pool Balances](protocol/protocol.pdf#chainvaluepoolbalances)

[^protocol-constants]: [Zcash Protocol Specification, Version 2025.6.2 [NU6.1]. Section 5.3: Constants](protocol/protocol.pdf#constants)

[^protocol-diffadjustment]: [Zcash Protocol Specification, Version 2025.6.2 [NU6.1]. Section 7.7.3: Difficulty Adjustment](protocol/protocol.pdf#diffadjustment)

[^protocol-txnconsensus]: [Zcash Protocol Specification, Version 2025.6.2 [NU6.1]. Section 7.1.2: Transaction Consensus Rules](protocol/protocol.pdf#txnconsensus)

[^protocol-subsidies]: [Zcash Protocol Specification, Version 2025.6.2 [NU6.1]. Section 7.8: Calculating Block Subsidy, Funding Streams, Lockbox Disbursement, and Founders' Reward](protocol/protocol.pdf#subsidies)

[^zip-0200]: [ZIP 200: Network Upgrade Mechanism](zip-0200.rst)

[^zip-0233]: [ZIP 233: Network Sustainability Mechanism: Removing Funds From Circulation](zip-0233.md)

[^zip-0234]: [ZIP 234: Network Sustainability Mechanism: Issuance Smoothing](zip-0234.md)

[^zip-0236]: [ZIP 236: Blocks should balance exactly](zip-0236.rst)

[^draft-arya-deploy-nu7]: [draft-arya-deploy-nu7: Deployment of the NU7 Network Upgrade](draft-arya-deploy-nu7.md)
