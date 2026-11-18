    ZIP: Unassigned
    Title: 10-second Block Target Spacing
    Owners: Marek <marek@zfnd.org>
    Status: Draft
    Category: Consensus
    Created: 2026-10-31
    License: MIT


# Terminology

The key words "MUST", "SHALL", "SHOULD", and "SHOULD NOT" in this document are
to be interpreted as described in BCP 14 [^BCP14] when, and only when, they
appear in all capitals.

The term "network upgrade" is to be interpreted as defined in ZIP 200.
[^zip-0200]

The term "block target spacing" is to be interpreted as defined in ZIP 218.
[^zip-0218]

The character § is used when referring to sections of the Zcash Protocol
Specification. [^protocol]

The terms "Mainnet" and "Testnet" are to be interpreted as described in
§ 3.12 'Mainnet and Testnet'. [^protocol-networks]

"NU8" is the code name of the network upgrade that deploys this proposal.


# Abstract

This proposal changes the block target spacing from 25 seconds to 10 seconds
in NU8. The block subsidy, the block size limit, and the shielded action limits
of each block are scaled by the same factor, so that issuance, block space, and
shielded capacity per unit of time are unchanged.


# Motivation

ZIP 218 reduces the block target spacing from 75 seconds to 25 seconds in NU7
in order to reduce transaction latency. [^zip-0218] This proposal reduces it to
10 seconds, which reduces the expected time to a first confirmation from 25
seconds to 10 seconds.

The proposal changes latency only. Each quantity that NU7 specifies per unit of
time is preserved: issuance, funding stream address periods, reissuance by the
Network Sustainability Mechanism, the duration of the difficulty averaging
window, and the resource limits of the block chain.


# Specification

The changes below are made to the Zcash Protocol Specification [^protocol] and
to ZIPs 207, 214, and 237 [^zip-0207] [^zip-0214] [^zip-0237], as amended for
NU7 by ZIP 218 [^zip-0218] and ZIP 259 [^zip-0259].

## Block target spacing

In § 5.3 'Constants' [^protocol-constants], define:

$$\mathsf{NU8ActivationHeight} : \mathbb{N}$$
$$\mathsf{PostNU8PoWTargetSpacing} : \mathbb{N} := 10 \textsf{ seconds}$$

In § 7.7.3 'Difficulty adjustment' [^protocol-diffadjustment], define:

$$\mathsf{NU8PoWTargetSpacingRatio} : \mathbb{Q} := \mathsf{PostNU7PoWTargetSpacing} \;/\; \mathsf{PostNU8PoWTargetSpacing} = 5/2$$

$$\mathsf{IsNU8Activated} : \mathbb{N} \to \{\mathsf{false}, \mathsf{true}\}$$
$$\mathsf{IsNU8Activated}(\mathsf{height}) := (\mathsf{height} \geq \mathsf{NU8ActivationHeight})$$

On each network, $\mathsf{NU8ActivationHeight}$ SHALL be even.

In the definition of $\mathsf{PoWTargetSpacing}$ in ZIP 218, replace the case
"otherwise" with "if $\mathsf{IsNU7Activated}(\mathsf{height})$ and not
$\mathsf{IsNU8Activated}(\mathsf{height})$", and add the case
$\mathsf{PostNU8PoWTargetSpacing}$ "otherwise".

## Difficulty averaging window

In § 5.3 'Constants', define:

$$\mathsf{PostNU8PoWAveragingWindow} : \mathbb{N} := 255$$

In the definition of $\mathsf{PoWAveragingWindow}$ in ZIP 218, replace the case
"otherwise" with "if $\mathsf{IsNU7Activated}(\mathsf{height})$ and not
$\mathsf{IsNU8Activated}(\mathsf{height})$", and add the case
$\mathsf{PostNU8PoWAveragingWindow}$ "otherwise".

The averaging window timespan therefore remains 2,550 seconds.

## Halving interval and block subsidy

Define:

$$\mathsf{PostNU8HalvingInterval} : \mathbb{N} := \mathsf{PostNU7HalvingInterval} \cdot \mathsf{NU8PoWTargetSpacingRatio} = 12{,}600{,}000$$

In the definition of $\mathsf{Halving}$ in ZIP 218, replace the case
"otherwise" with "if $\mathsf{IsNU7Activated}(\mathsf{height})$ and not
$\mathsf{IsNU8Activated}(\mathsf{height})$", and add the case:

$$
\left\lfloor \dfrac{\mathsf{BlossomActivationHeight} - \mathsf{SlowStartShift}}{\mathsf{PreBlossomHalvingInterval}}
  + \dfrac{\mathsf{NU7ActivationHeight} - \mathsf{BlossomActivationHeight}}{\mathsf{PostBlossomHalvingInterval}}
  + \dfrac{\mathsf{NU8ActivationHeight} - \mathsf{NU7ActivationHeight}}{\mathsf{PostNU7HalvingInterval}}
  + \dfrac{\mathsf{height} - \mathsf{NU8ActivationHeight}}{\mathsf{PostNU8HalvingInterval}} \right\rfloor,
  \quad \textsf{otherwise}
$$

In the definition of $\mathsf{ScheduledBlockSubsidy}$ in ZIP 237, replace the
condition "if $\mathsf{IsNU7Activated}(\mathsf{height})$" of the case added by
ZIP 218 with "if $\mathsf{IsNU7Activated}(\mathsf{height})$ and not
$\mathsf{IsNU8Activated}(\mathsf{height})$", and add the case:

$$
\mathsf{floor}\left(\dfrac{\mathsf{MaxBlockSubsidy}}{\mathsf{BlossomPoWTargetSpacingRatio} \cdot \mathsf{NU7PoWTargetSpacingRatio} \cdot \mathsf{NU8PoWTargetSpacingRatio} \cdot 2^{\mathsf{Halving}(\mathsf{height})}}\right),
  \quad \textsf{if } \mathsf{IsNU8Activated}(\mathsf{height})
$$

The denominator is $15 \cdot 2^{\mathsf{Halving}(\mathsf{height})}$.

## Block size and shielded action limits

For a block at a height for which $\mathsf{IsNU8Activated}(\mathsf{height})$,
the size of the block MUST be less than or equal to 800,000 bytes, in place of
the limit of 2,000,000 bytes in § 7.6 'Block Header Encoding and Consensus'.
[^protocol-blockheader]

For such a block, the shielded action limits of ZIP 218 apply with
$\mathsf{GlobalShieldedBudget} = 132$,
$\mathsf{OrchardProtocolBlockActionLimit} = 132$, and
$\mathsf{SaplingBlockIOLimit} = 120$. $\mathsf{SproutBlockJoinSplitLimit}$
remains 0.

## Funding streams

Let $A$, $R$, $C$, $I$, and $H_1$ be as in the definition of
$\mathsf{AddressPeriod}$ in Revision 2 of ZIP 207, and let
$B = \mathsf{NU8ActivationHeight}$. In that definition, replace the case
"otherwise" with "if $\mathsf{IsNU7Activated}(\mathsf{height})$ and not
$\mathsf{IsNU8Activated}(\mathsf{height})$", and add the case:

$$
\mathsf{floor}\left(\dfrac{5\left(R(A + I - H_1) + B - A\right) + 2(\mathsf{height} - B)}{5RC}\right),
  \quad \textsf{otherwise}
$$

This preserves the address index at NU8 activation. Each later address period
lasts $5RC/2 = 262{,}500$ blocks.

For each funding stream that is active at $B$ and whose end height is
$\mathsf{HeightForHalving}(3)$ by Revision 3 of ZIP 214, the end height SHALL
be $\mathsf{HeightForHalving}(3)$ calculated using the $\mathsf{Halving}$
function of this proposal. If $H_3$ is the third-halving height under ZIP 218
(6,132,390 on Mainnet and 4,497,948 on Testnet), this end height is
$B + 5(H_3 - B)/2$. The number of addresses that ZIP 207 requires
for each such stream is unchanged.

## Network Sustainability Mechanism

In ZIP 237, $\mathsf{HalvingInterval}(\mathsf{height})$ is
$\mathsf{PostNU8HalvingInterval}$ if $\mathsf{IsNU8Activated}(\mathsf{height})$.
From NU8 activation, $\mathsf{BLOCK\_SUBSIDY\_FRACTION}$ is therefore
$550 / 10^{10}$.

If $B$ is less than the $\mathsf{DEPLOYMENT\_BLOCK\_HEIGHT}$ that ZIP 237
specifies for a network, then $\mathsf{DEPLOYMENT\_BLOCK\_HEIGHT}$ for that
network SHALL instead be calculated as in ZIP 237, with $B$ in place of $A$,
with $\mathsf{ScheduledBlockSubsidy}$, $H_3$, and $H_4$ as specified by this
proposal, and with 550 in place of 1375. NU8 activation heights SHALL be chosen
so that this height exists before $H_4$. The NU8 deployment ZIP specifies the
resulting height for each network.

## Minimum-difficulty blocks on Testnet

On Testnet, from NU8 activation, the minimum-difficulty threshold specified by
ZIP 218 is $45 \cdot \mathsf{PoWTargetSpacing}(\mathsf{height})$ seconds, which
remains 450 seconds.

## Unchanged consensus rules

Consensus rules that are expressed in blocks and not changed above, including
the coinbase maturity of 100 blocks and $\mathsf{PoWMedianBlockSpan}$, are
unchanged.

## Non-consensus changes

From NU8 activation:

- Wallets SHOULD use a default expiry delta of 300 blocks, in place of the 120
  blocks recommended by ZIP 218.
- Nodes SHOULD support rolling back at least 1,500 blocks, in place of the 600
  blocks recommended by ZIP 218.
- Implementations SHOULD multiply the block-count constants that ZIP 218
  multiplies by 3 by $\mathsf{NU8PoWTargetSpacingRatio}$, rounding up.
- Nodes SHOULD NOT admit to their mempools or relay, and wallets SHOULD NOT
  create, a transaction that alone exceeds the block size or shielded action
  limits above.


# Rationale

A target spacing of 10 seconds makes each scaled quantity an integer: the
averaging window of 255 blocks, the halving interval of 12,600,000 blocks, the
address period of 262,500 blocks, and the limits of 800,000 bytes, 132
actions, and 120 Sapling inputs and outputs.

Every post-NU7 halving height is even on both networks. An even activation
height $B$ therefore maps each such height $H$ to the integer height
$B + 5(H - B)/2$, so that no halving boundary falls within a 25-second block.

Scaling the per-block limits by 2/5 keeps the worst-case validation work,
compact sync bandwidth, and chain growth per unit of time at their NU7 values.
ZIP 218 bounds worst-case compact sync bandwidth at 169.10 MB per day.
[^zip-0218] Without the scaling, each of these would increase by a factor of
5/2.

The post-NU8 block subsidy differs from 2/5 of the post-NU7 block subsidy by
less than one zatoshi, due to rounding. If NU8 activates before the third
halving, this reduces total scheduled issuance, relative to ZIP 218, by
$(H_3 - B)/2$ zatoshi before the third halving and by 1.134 ZEC after it.


# Security and Privacy Considerations

The stale block rate increases with the ratio of block propagation time to the
block target spacing. ZIP 218 reports a stale block rate of 4.86% for 2 MB
blocks at 25-second spacing on a 99-node devnet. [^zip-0218] The rate at
10-second spacing has not been measured; it needs to be measured before
deployment. Smaller blocks and compact block relay [^draft-compact-block-relay]
reduce propagation time.

A given number of confirmations corresponds to 2.5 times less time. Where
propagation time is significant relative to the target spacing, it also
provides less security against an attacker with a given fraction of the hash
power.

Wallets that select an anchor three blocks behind the chain tip, as
recommended by ZIP 315 [^zip-0315], select one about 30 seconds old. A rollback
past the anchor invalidates the transaction, and links its revealed nullifiers
to any later transaction that spends the same notes. More frequent blocks also
give observers finer timing information.


# Deployment

This proposal is intended to be deployed in NU8. The NU8 deployment ZIP will
specify $\mathsf{NU8ActivationHeight}$ for each network.


# References

[^BCP14]: [Information on BCP 14 — "RFC 2119: Key words for use in RFCs to Indicate Requirement Levels" and "RFC 8174: Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words"](https://www.rfc-editor.org/info/bcp14)

[^protocol]: [Zcash Protocol Specification, Version 2026.8.0 or later](protocol/protocol.pdf)

[^protocol-networks]: [Zcash Protocol Specification, Version 2026.8.0. Section 3.12: Mainnet and Testnet](protocol/protocol.pdf#networks)

[^protocol-constants]: [Zcash Protocol Specification, Version 2026.8.0. Section 5.3: Constants](protocol/protocol.pdf#constants)

[^protocol-blockheader]: [Zcash Protocol Specification, Version 2026.8.0. Section 7.6: Block Header Encoding and Consensus](protocol/protocol.pdf#blockheader)

[^protocol-diffadjustment]: [Zcash Protocol Specification, Version 2026.8.0. Section 7.7.3: Difficulty adjustment](protocol/protocol.pdf#diffadjustment)

[^zip-0200]: [ZIP 200: Network Upgrade Mechanism](zip-0200.rst)

[^zip-0207]: [ZIP 207: Funding Streams](zip-0207.rst)

[^zip-0214]: [ZIP 214: Consensus rules for a Zcash Development Fund](zip-0214.rst)

[^zip-0218]: [ZIP 218: 25-second Block Target Spacing](zip-0218.md)

[^zip-0237]: [ZIP 237: Network Sustainability Mechanism: Halving-Preserving Issuance](zip-0237.md)

[^zip-0259]: [ZIP 259: Deployment of the NU7 Network Upgrade](zip-0259.md)

[^zip-0315]: [ZIP 315: Best Practices for Wallet Implementations](zip-0315.rst)

[^draft-compact-block-relay]: [Draft ZIP: Compact Block Relay](https://github.com/zcash/zips/pull/1429)
