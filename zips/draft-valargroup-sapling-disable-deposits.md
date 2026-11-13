    ZIP: Unassigned
    Title: Disabling Sapling Pool Deposits
    Owners: Dev Ojha <dev@valargroup.dev>
    Status: Draft
    Category: Consensus / Wallet
    Created: 2026-10-27
    License: MIT
    Discussions-To: <https://forum.zcashcommunity.com/t/sapling-withdraw-only-discussion-kickoff/55223>
    Pull-Request: <https://github.com/zcash/zips/pull/???>


# Terminology

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this
document are to be interpreted as described in BCP 14 [^BCP14] when, and only
when, they appear in all capitals.

The term "network upgrade" in this document is to be interpreted as described
in ZIP 200. [^zip-0200]

The character § is used when referring to sections of the Zcash Protocol
Specification. [^protocol]

The terms "Mainnet" and "Testnet" are to be interpreted as described in
§ 3.12 ‘Mainnet and Testnet’. [^protocol-networks]

The term "Sapling shielded protocol" refers to the shielded payment protocol
introduced in the Sapling network upgrade. [^zip-0205] Following the
convention of ZIP 229 [^zip-0229], *Sapling pool*, *Orchard pool* and
*Ironwood pool* refer to chain value pools, as distinct from the protocols that
operate on them.

The term "Sapling chain value pool balance" is to be interpreted as described
in ZIP 209 [^zip-0209] and § 4.17 ‘Chain Value Pool Balances’.
[^protocol-chainvaluepoolbalances]

The term "quantum recoverable" is to be interpreted as described in
ZIP 2005. [^zip-2005]

NU8 refers to the network upgrade following NU7.


# Abstract

This proposal disables the ability to add new value to the Sapling chain value
pool balance. From NU8 activation, every transaction's Sapling value balance
must be nonnegative: value may leave the *Sapling pool*, or move between
Sapling notes, but no new value may enter it. Coinbase transactions may no
longer contain Sapling outputs.

This starts the migration of the remaining *Sapling pool* funds into
quantum-recoverable shielded pools (the *Ironwood pool* today). It is the
Sapling counterpart of what ZIP 211 [^zip-0211] did for Sprout at Canopy and
what ZIP 2006 [^zip-2006] did for the *Orchard pool* at NU6.3.


# Motivation

The Sapling shielded protocol is not quantum recoverable: an adversary able to
compute discrete logarithms, for example with a quantum computer, could steal
funds held in the *Sapling pool*. ZIP 2005 expects Sapling funds to be
migrated to the *Ironwood pool* instead [^zip-2005]. Ironwood notes are quantum
recoverable, and formal verification shows that undetectable counterfeiting
bugs do not exist in Ironwood. [^Ironwood-book] [^ironwood-verification]
Ironwood and later Tachyon [^tachyon] are steps toward a fully post-quantum
shielded pool soon after.

Nothing currently stops new value from entering the *Sapling pool*, and every
deposit adds to what must later be migrated. Pool migrations take years: about
22,000 ZEC remains in Sprout six years after ZIP 211 disabled additions to it
[^zip-0211]. The *Sapling pool* holds about 419,900 ZEC, or 8.5% of shielded
ZEC [^cipherscan-supply]. Disabling deposits now, while all funds remain fully
spendable, gives custodians and wallets a firm deadline and makes the
remaining balance only decline.

The cost of doing so is low. Excluding mining pool coinbase shielding and the
Zcash Community Grants funding stream, which can move to Ironwood (see Open
issues), only 1.2% of non-coinbase transactions in the last 30 days touched
the *Sapling pool*, and they withdrew 101,216 ZEC more than they deposited.
Coinbase outputs to Sapling are essentially unused. [^sapling-activity]

As with Sprout [^zip-0211], disabling additions also limits the impact of any
undiscovered soundness bug in Sapling, and is a precondition for eventually
removing the Sapling shielded protocol.


# Privacy Implications

Withdrawals from the *Sapling pool* reveal the amount that leaves it, through
the Sapling value balance. This is unchanged by this ZIP. However, the ZIP will
cause most remaining Sapling value to cross a turnstile over time. Wallets
should therefore migrate Sapling funds in a way that limits linkability of the
amounts moved; see [Changes to ZIP 318](#changestozip318).

The *Sapling pool* anonymity set is its note commitment set, which this ZIP
does not reduce. As fewer transactions use the pool, individual Sapling
transactions may become easier to distinguish by timing and amount, as is true
of any shielded pool with low usage, but the unlinkability of spent notes from
the transactions that created them is unaffected.

Full nodes change behaviour at the NU8 activation height, and from that height
consensus prevents all wallets from adding value to the *Sapling pool*, so
wallets also change behaviour at that height in this respect. When a wallet
chooses to migrate its users' Sapling funds is not constrained to a single
height; using a common migration procedure (ZIP 318 [^zip-0318]) limits how much
that choice distinguishes wallets.


# Requirements

* No new value can enter the *Sapling pool* after activation, from any
  transaction version, including coinbase.
* Holders keep full access to their Sapling funds. They can spend to any
  other pool (in practice Ironwood or transparent), and can keep making
  Sapling-to-Sapling transfers, including to other people.
* No change to the Sapling circuits or parameters, and no new trusted setup.
* The consensus change is small and easy to analyse.


# Non-requirements

* This ZIP does not set a date after which Sapling notes can no longer be
  spent. That is left to a future proposal. So is what happens to any value
  left in the pool at that point.
* This ZIP does not make Sapling quantum recoverable.
* This ZIP does not restrict the *Sprout pool* or the transparent pool.


# Specification

## Consensus rules

The following rules apply to every transaction in a block at a height greater
than or equal to the NU8 activation height, regardless of transaction version:

* $\mathsf{v}^{\textit{SaplingPoolBalance}}$ MUST be nonnegative, where
  $\mathsf{v}^{\textit{SaplingPoolBalance}}$ is the transaction's Sapling
  balancing value as defined in § 4.13 ‘Balance and Binding Signature
  (Sapling)’. [^protocol-saplingbalance]

* A coinbase transaction MUST NOT contain any Sapling Output descriptions;
  that is, `nOutputsSapling` MUST be zero. Coinbase transactions are already
  required to have `nSpendsSapling` equal to zero.

Non-normative notes:

* $\mathsf{v}^{\textit{SaplingPoolBalance}}$ is the value of Sapling Spends
  minus Outputs. It is encoded as the `valueBalanceSapling` field of version 4,
  5 and 6 transactions (implicitly zero when absent), so for those versions the
  rule is equivalent to requiring that encoded field to be nonnegative. For a
  transaction format that expresses value balances as value pool deltas
  [^zip-0248], it corresponds to the delta for the Sapling bundle and the ZEC
  asset. When it is nonnegative, value can only move out of the *Sapling pool* or stay inside
  it. Together with the ZIP 209 [^zip-0209] rule that the Sapling chain value
  pool balance never goes negative, the balance can only stay the same or fall
  from activation onward.

* Sapling Output descriptions remain valid in non-coinbase transactions. A
  transaction may pay Sapling notes to any Sapling address, including a third
  party's, if Sapling spends in the same transaction fund those outputs.

* The coinbase rule is partly implied by the balance rule, because a coinbase
  transaction has no Sapling spends. It is stated explicitly so that
  zero-valued Sapling coinbase outputs are excluded too, and to mirror the
  ZIP 2006 rule for the *Orchard pool* [^zip-2006].

## Changes to ZIP 213

In the Specification section of ZIP 213 [^zip-0213], after the NU6.3 rules,
add:

> Once the NU8 network upgrade activates:
>
> - Coinbase transactions MAY contain *Ironwood-pool* outputs.
> - Coinbase transactions MUST NOT contain Sapling outputs.

## Changes to the Protocol Specification

§ 7.1.2 ‘Transaction Consensus Rules’ [^protocol-txnconsensus] gains the two
consensus rules above, gated on NU8 activation, alongside the existing NU6.3
rule that $\mathsf{v}^{\textit{OrchardPoolBalance}}$ is nonnegative.

## Changes to ZIP 318

ZIP 318 [^zip-0318] is extended so that its migration procedure can take either
the *Orchard pool* or the *Sapling pool* as its source pool, with the
*Ironwood pool* as the destination in both cases:

* A migration MUST draw on a single source pool. A wallet with funds in both
  the *Sapling pool* and the *Orchard pool* runs a separate migration for
  each, and no note preparation or migration transaction spends from both.
* For a Sapling-source migration, each canonical migration transaction has
  exactly one Sapling spend in place of the single Orchard spend, with the
  Sapling bundle padded so that the presence or absence of a Sapling change
  output is not observable, and no spends from any other pool. All other
  properties of the canonical migration transaction are unchanged.
* Note preparation for a Sapling-source migration is performed within the
  *Sapling pool*.

Mixing source pools within one transaction or one migration schedule would
link a user's Sapling and Orchard holdings, so each migration is restricted to
one source pool.

## Requirements for wallets and node software

From NU8 activation:

* Wallets MUST NOT create transactions that contain one or more Sapling
  outputs together with one or more inputs from outside the *Sapling pool*
  (transparent inputs, or spends from any other shielded pool). As with
  ZIP 211 [^zip-0211], this is stricter than consensus, for usability
  reasons. Consensus would accept a mixed transaction whose Sapling spends
  cover its Sapling outputs.

* Wallets SHOULD NOT create new Unified Addresses that include a Sapling
  receiver. They MAY keep producing Sapling receivers before activation for
  compatibility.

* Wallets that hold Sapling funds SHOULD offer to migrate them to the
  *Ironwood pool*. Wallets SHOULD use the migration procedure of ZIP 318
  [^zip-0318], as extended below.

* Block template software SHOULD reject Sapling-only miner addresses with a
  clear error.

Transactions signed for an earlier consensus branch become invalid at NU8
activation under ZIP 200 [^zip-0200] and ZIP 244 [^zip-0244], so no
mempool-specific rule is needed.


# Rationale

## Why a balance rule, not a circuit change

The rule mirrors ZIP 211 for Sprout and ZIP 2006 for Orchard. It only
needs a check on a field validators already parse. It does not touch the
Sapling Spend or Output circuits. That avoids a new parameter generation
ceremony, any risk of a soundness regression in Groth16 circuits, and any new
transaction version. The implementation is a few lines in each full validator,
and its security is easy to analyse.

## Why internal transfers stay allowed

ZIP 2006 also disabled cross-address transfers within the *Orchard pool*. That
was possible because the new Orchard Action circuit had an `enableCrossAddress`
flag [^zip-2006]. Doing the same for Sapling would need a new Sapling circuit
and trusted setup, which this ZIP sets out to avoid.

Allowing Sapling outputs also lets wallets keep using Sapling change when
withdrawing, so a withdrawal reveals only the amount leaving the pool rather
than the total value of the notes spent.

## Why the coinbase prohibition is explicit

ZIP 213 has allowed coinbase outputs to Sapling addresses since Heartwood
[^zip-0213], but miners have not adopted it: only one Mainnet block has ever
paid its coinbase to a Sapling output. {TODO: cite the block height and txid.}
Shielded coinbase has instead moved to the Orchard protocol, which since NU6.3
pays into the *Ironwood pool*. In the 30 days to height 3,532,124, 4.6% of
blocks paid their coinbase directly to the *Ironwood pool*, and none contained
a Sapling output. [^sapling-activity] Leaving Sapling coinbase outputs
available invites zero-value or misconfigured outputs that add commitments
with no purpose. The explicit rule matches the ZIP 2006 Orchard rule.

# Deployment

This ZIP is proposed for deployment in the NU8 network upgrade.


# Open issues

* **Mining pool coinbase shielding.** 58.8% of all Sapling transactions in
  the 30 days to height 3,532,124 (3,737 of 6,352) are attributable to mining
  pools shielding transparent coinbase rewards into Sapling: 2,705 deposits
  carrying 31,228 ZEC, and at least 1,032 withdrawals carrying 16,432 ZEC that
  return those funds to transparent addresses. Most of these pools send the
  funds back to their own coinbase payout address shortly afterwards (F2Pool,
  Luxor, Kryptex, Mining Dutch), or on to a transparent payout transaction
  (2Miners), so the shielding is a round trip rather than a shielded payout to
  miners. ViaBTC and ViaBTC-Solo deposited a further 14,633 ZEC whose
  withdrawals could not be attributed. Together, pools that shield their
  coinbase into Sapling mined about 72% of blocks in that window.
  [^sapling-activity] These pools need to shield into the *Ironwood pool*
  instead, and should be contacted before activation.

* **Zcash Community Grants funding stream.** The ZCG funding stream address
  [^zip-0214] sweeps its coinbase outputs into Sapling. In the same window
  this was 32 transactions, 0.5% of all Sapling transactions, but 4,000 ZEC,
  or 9.5% of all ZEC deposited into Sapling. [^sapling-activity] These sweeps
  should move to the *Ironwood pool* before activation.


# References

[^BCP14]: [Information on BCP 14 — "RFC 2119: Key words for use in RFCs to Indicate Requirement Levels" and "RFC 8174: Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words"](https://www.rfc-editor.org/info/bcp14)

[^protocol]: [Zcash Protocol Specification, Version 2026.6.4 or later](protocol/protocol.pdf)

[^protocol-networks]: [Zcash Protocol Specification. Section 3.12: Mainnet and Testnet](protocol/protocol.pdf#networks)

[^protocol-chainvaluepoolbalances]: [Zcash Protocol Specification. Section 4.17: Chain Value Pool Balances](protocol/protocol.pdf#chainvaluepoolbalances)

[^protocol-saplingbalance]: [Zcash Protocol Specification. Section 4.13: Balance and Binding Signature (Sapling)](protocol/protocol.pdf#saplingbalance)

[^protocol-txnconsensus]: [Zcash Protocol Specification. Section 7.1.2: Transaction Consensus Rules](protocol/protocol.pdf#txnconsensus)

[^zip-0200]: [ZIP 200: Network Upgrade Mechanism](zip-0200.rst)

[^zip-0205]: [ZIP 205: Deployment of the Sapling Network Upgrade](zip-0205.rst)

[^zip-0209]: [ZIP 209: Prohibit Negative Shielded Chain Value Pool Balances](zip-0209.rst)

[^zip-0211]: [ZIP 211: Disabling Addition of New Value to the Sprout Chain Value Pool](zip-0211.rst)

[^zip-0213]: [ZIP 213: Shielded Coinbase](zip-0213.rst)

[^zip-0214]: [ZIP 214: Consensus rules for a Zcash Development Fund](zip-0214.rst)

[^zip-0229]: [ZIP 229: Version 6 Transaction Format](zip-0229.md)

[^zip-0244]: [ZIP 244: Transaction Identifier Non-Malleability](zip-0244.rst)

[^zip-0248]: [ZIP 248: Extensible Transaction Format](zip-0248.rst)



[^zip-0318]: [ZIP 318: Orchard to Ironwood Migration](zip-0318.md)

[^zip-2005]: [ZIP 2005: Ironwood Quantum Recoverability](zip-2005.md)

[^zip-2006]: [ZIP 2006: Restricting Transfers into the Orchard Pool](zip-2006.md)

[^Ironwood-book]: [The Ironwood Book](https://zcash.github.io/ironwood/)

[^ironwood-verification]: [Formal Verification of Zcash Ironwood Completed](https://tachyon.z.cash/blog/ironwood-verification-complete/)

[^sapling-activity]: Analysis of all 34,560 Mainnet blocks at heights 3,497,565 to 3,532,124 (2026-09-27 to 2026-10-27), using per-transaction data from the [CipherScan API](https://api.mainnet.cipherscan.app/api/block/3532124). Transactions were classified by the sign of `valueBalanceSapling`: deposits (negative), withdrawals (positive beyond the fee, or with transparent or other shielded outputs), and internal transfers (otherwise). A deposit is attributed to a mining pool or to the ZCG funding stream when that party's coinbase payout address supplied most of its transparent input value. A withdrawal is attributed to a pool when it pays that pool's coinbase payout address, or when the value leaving Sapling exactly equals the sum of up to its number of Sapling spends of that pool's deposits made in the preceding 4,032 blocks. Pool names are from CipherScan's labels for the coinbase payout address. Hashpower share is estimated by share of blocks mined. Each block is assigned to the *Ironwood pool* if its coinbase transaction has Ironwood outputs; otherwise to the pool into which most of the in-window coinbase value of its miner payout address (excluding the funding stream address `t3cFfPt1Bcvgez9ZbMBFWeZsskxTkPzGCow`) was subsequently shielded. This gives Sapling 71.6% of blocks and Ironwood 28.4% (23.8% by later sweep and 4.6% by shielded coinbase).

[^tachyon]: [Tachyon: Scaling Zcash with Oblivious Synchronization](https://seanbowe.com/blog/tachyon-scaling-zcash-oblivious-synchronization/)

[^cipherscan-supply]: [CipherScan Mainnet chain value pool balances](https://api.mainnet.cipherscan.app/api/supply), retrieved 2026-10-27 at height 3,532,124.
