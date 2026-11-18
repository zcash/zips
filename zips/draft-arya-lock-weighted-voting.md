    ZIP: Unassigned
    Title: Lock-weighted Coinholder Polling
    Owners: Arya <arya@zfnd.org>
    Status: Draft
    Category: Process
    Created: 2026-11-03
    License: MIT
    Discussions-To: <URL TBD>


# Terminology

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this
document are to be interpreted as described in BCP 14 [^BCP14] when, and only
when, they appear in all capitals.

The terms "Mainnet" and "Testnet" in this document are to be interpreted as
defined in the Zcash protocol specification [^protocol-networks].

The term "*Ironwood pool*" is to be interpreted as described in ZIP 229
[^zip-0229].

The terms "Coinholder-Controlled Fund" and "Key-Holder Organizations" are to be
interpreted as described in ZIP 1016 [^zip-1016]. The term "Deferred Dev Fund
Lockbox" is to be interpreted as described in ZIP 1015 [^zip-1015].

Poll

: A vote in which each ballot carries a ZEC amount.

Poll operator

: Whoever announces a poll, verifies ballots, and publishes results.

Snapshot height

: The block height $S$ at which holdings are measured.

Close height

: The height $C$ of the last block in which a ballot can be accepted.

Lock record

: A triple $(v, u, c)$: a value $v$ in zatoshi, an unlock height $u$ at or
  before which consensus forbids spending it ($u = 0$ if unlocked), and an
  evidence class $c$. Its lock length is $\ell = \max(0, u - S)$ blocks.


# Abstract

Coinholder polls count one ZEC as one vote at a snapshot height, and coins may
be moved right after the snapshot. This ZIP changes only the weighting: a
ballot's weight rises linearly with how long its coins stay locked past the
snapshot, up to a cap of one halving interval; unlocked coins keep a small
floor weight. One evidence class works today: transparent outputs locked
with `OP_CHECKLOCKTIMEVERIFY`. A second class for shielded locks is reserved
for a consensus ZIP. Quorum and the ZIP 1016 participation threshold stay in
unweighted ZEC. The transparent class reveals the voter's output, amount, and
unlock height on chain, which the current shielded polling path does not; the
shielded class is the intended end state.


# Motivation

Coinholder polling gives holders a voice alongside developers, users, and
miners. ZIP 1016 [^zip-1016] makes it the deciding input for the
Coinholder-Controlled Fund, and about 2.4 million of 3.6 million eligible ZEC
voted in the NU7 scope poll of September 2026 [^coindesk-nu7].

The status quo is one ZEC, one vote, at a snapshot, with coins movable the
moment the snapshot passes [^forum-nu7-vote]. Someone who buys the week of
the vote and sells the week after is not a holder; they are renting a vote.
This ZIP favours people credibly in it for the long haul. Someone willing to
lock ZEC for years should have a big say, not the only say. A whale who locks
for years still gets a big vote; they have put their coins where their vote
is. The change removes the cheap vote, not the big one.

## Scope decision

There is no timelock for shielded notes. Transparent outputs can be locked
with `OP_CHECKLOCKTIMEVERIFY` [^bip-0065], which Zebra enforces on every
transparent input [^zebra-script] `[VERIFY: enforced by zcashd since
genesis]`. Sapling, Orchard, and Ironwood notes have no script and no lock
field, and a transaction's `lock_time` is ignored when no transparent input
has a non-final sequence number [^zebra-locktime], so it cannot lock a
shielded-only spend. Three options were considered:

1. A process-only ZIP using transparent locks. It works at the protocol
   level, not the tooling level: the live mechanism accepts only notes in the
   *Ironwood pool* [^zcashlabs-voting]. It asks holders to unshield for full
   weight, which is at odds with the point of Zcash. Not acceptable as the
   only option.
2. A consensus ZIP adding a lock to shielded notes. The smallest version is a
   lock-height field in the Ironwood note commitment, one circuit constraint,
   and one consensus rule (see [Class S]). That is a new circuit version for a
   pool created, with formal verification, after the Orchard soundness
   vulnerability [^zip-0229]. It is not small and needs a network upgrade.
3. Two ZIPs: this process ZIP, defining weighting over any lock the protocol
   can prove, with the transparent class as an interim, plus a later consensus
   ZIP for shielded locks.

Option 3 is chosen. Everything below is defined over lock records, so the
shielded class can be added without rewriting this ZIP.


# Privacy Implications

Under the live mechanism, validators learn neither who voted nor how much ZEC
a ballot carried; amounts are encrypted and only totals are decrypted
[^zcashlabs-voting]. A ballot under [Class T] reveals an output, its value,
and its unlock height on chain to everyone, and links the ballot to that
output unless the operator encrypts ballot contents. A voter who unshields to
lock also reveals the unshielding transaction. That cost is why Class S is the
intended end state.

The shielded class is required to reveal no more than the current shielded
path: the lock length stays a private witness, the multiplier is applied
inside the proof, and locked notes are indistinguishable from unlocked notes
on chain, including when spent.


# Requirements

* A ballot's weight depends on both the amount of ZEC and how long it is
  locked past the snapshot.
* Borrowing, hedging, or splitting to gain weight costs more than under
  amount-only weighting.
* Weighting is defined over an abstract lock record, so shielded locks can be
  added without changing the rules.
* The shielded class reveals no more than the current shielded polling path.
* Coins with no holder, such as protocol-level lockboxes, cannot be voted.


# Non-requirements

* This ZIP does not change who is eligible to vote, what polls are held, or
  what polls decide. It changes weighting only.
* It does not propose on-chain binding governance. Polls remain what ZIP 1016
  says they are.
* It does not change mining, block subsidy, or funding streams.
* It does not verify custody.


# Specification

## Parameters

$S$ and $C$ are chosen by the poll operator per poll. The floor is
$f = 1/10$. The cap $L$ is the halving interval in effect at height $S$:
$\mathsf{PostBlossomHalvingInterval} = 1{,}680{,}000$ blocks before NU7
activation and $\mathsf{PostNU7HalvingInterval} = 5{,}040{,}000$ blocks from
NU7 activation [^zip-0218]. Both are about four years.

## Weight function

For a lock record $(v, u, c)$ with lock length $\ell = \max(0, u - S)$:

$$m(\ell) = f + (1 - f) \cdot \frac{\min(\ell, L)}{L}, \qquad w = v \cdot m(\ell)$$

If $u \leq C$, the record MUST be counted as unlocked ($\ell = 0$). A ballot's
weight is the sum of $w$ over its lock records.

| $\ell / L$ | $m(\ell)$ | at the four-year cap |
|-----------:|----------:|----------------------|
| 0          | 0.100     | unlocked             |
| 1/16       | 0.156     | 3 months             |
| 1/8        | 0.213     | 6 months             |
| 1/4        | 0.325     | 1 year               |
| 1/2        | 0.550     | 2 years              |
| 1 or more  | 1.000     | 4 years or more      |

## Lock records

An operator MUST accept Class H and at least one lock class, and MUST reject
any ballot whose evidence fails verification; a failed record MUST NOT be
counted under Class H.

### Class H

Class H evidence is whatever proof of holding at $S$ the operator already
accepts, such as a proof of unspent Ironwood notes. It yields $(v, 0,
\mathrm{H})$ and counts at the floor.

### Class T

Class T evidence is a transparent output whose `scriptPubKey` is a
pay-to-script-hash of the redeem script

    <u> OP_CHECKLOCKTIMEVERIFY OP_DROP <pubkey> OP_CHECKSIG

where `<u>` is a minimally encoded script number with
$1 \leq u < 500{,}000{,}000$ (a block height, not a Unix time) [^bip-0065].
The ballot carries the outpoint, the redeem script, and an ECDSA signature
over secp256k1 by `pubkey`, as for `OP_CHECKSIG`, over a message $M$ defined
by the operator. $M$ MUST include a poll identifier and MUST bind the ballot
contents or a commitment to them.

The operator MUST check that:

1. the output exists and is unspent in the chain state at height $S$;
2. the `scriptPubKey` equals the P2SH encoding of the supplied redeem script;
3. the redeem script matches the template and $u$ is in height form;
4. the signature is valid for `pubkey` over $M$;
5. the outpoint has not been used in another ballot of this poll.

The lock record is $(v, u, \mathrm{T})$ with $v$ the output's value.
Operators MAY also accept an `OP_CHECKMULTISIG` variant of the template with
$m$ valid signatures.

### Class S

Class S, shielded locks, is reserved for a consensus ZIP. That ZIP MUST
provide: a way to fix an unlock height at note creation that consensus
enforces on spends; a proof usable within the operator's shielded path that
yields a lock record for notes unspent at $S$, with the multiplier applied
inside the proof; and locked notes indistinguishable from unlocked notes on
chain, including when spent.

The smallest design known: a lock-height field inside the
Ironwood note commitment (zero for none); a circuit constraint that the field
is at most a per-bundle minimum height; a consensus rule that a transaction
with a non-zero minimum height is invalid in any block below it; and wallets
that set that value on every transaction so locked spends do not stand out.
`[VERIFY: fit with ZIP 229 and the Ironwood circuit]`

## Counting

For each option the operator MUST compute the weighted total $W$, the sum of
ballot weights, and the unweighted total $V$, the sum of $v$ over the same
ballots. The outcome among options MUST be decided on $W$. Any quorum, and the
420,000 ZEC participation threshold of ZIP 1016 [^zip-1016], MUST be measured
on $V$.

## Excluded coins

Value in the Deferred Dev Fund Lockbox [^zip-2001] and the NSM value balance
[^zip-0237] are chain value pool balances, not outputs or notes. They cannot
produce lock records and MUST NOT be counted.

## Poll operator obligations

Before height $S$ the operator MUST publish $S$, $C$, $L$, $f$, the accepted
evidence classes, and the format of $M$. The operator SHOULD NOT verify
Class T evidence until the block at height $S$ has at least 100
confirmations. After the poll the operator MUST publish $W$ and $V$ for every
option and SHOULD publish only totals. Operators MAY rehearse on Testnet,
where Mainnet thresholds do not apply.


# Security Considerations

**Borrow-to-vote.** Borrow ZEC, lock it, vote, repay after unlock. At an
annual borrowing cost $r$, a one-week unlocked borrow costs about $r/52$ of
$v$ for weight $0.1\,v$; a lock of $L$ costs about $4r$ of $v$ for weight $v$,
roughly twenty times more per unit of weight, and the loan must run until
$u$.

**Lock-and-hedge.** Lock $v$ and short $v$ elsewhere, voting with no net
exposure. This costs funding and margin over $\ell$ and remains possible; the
design raises cost, it does not make this impossible.

**Splitting.** Because $m$ is linear below the cap, weight per ZEC-block is
constant, so no partition of a holding across lock lengths changes its total
weight.

**Last-minute locks.** A lock placed the day before $S$ that reaches past $L$
counts in full. The forward commitment is the same whenever the lock was
placed; what such a voter lacks is past holding, which this ZIP does not
weigh. See [Open questions].

**Vote buying** is unchanged in kind. A seller must lock to sell full weight,
so the price rises, but the trade exists.

**Custodians.** A custodian that owes coins on demand cannot lock them without
a liquidity mismatch, so voting customer coins at full weight gets harder.
That is intended. The limits: a custodian can lock its own float or accept
the mismatch, and this ZIP does not verify custody.


# Rationale

## Alternatives considered

*Amount only (status quo).* One ZEC, one vote, movable right after the
snapshot [^forum-nu7-vote]. The vote can be rented for a week's exposure.

*One person, one vote.* Zcash has no sybil-resistant identity. The Zcash
Community Advisory Panel already gives a per-person signal alongside
coinholder polls [^zfnd-nu7-results].

*Square root or logarithm of amount.* Without identity, any concave function
of amount is defeated by splitting a holding across ballots.

*Conviction tiers* [^polkadot-opengov]. Multipliers that step with lock
length let a holder pick the best point on the curve by splitting. Linear with
a cap, as in Curve's vote-escrow [^curve-vecrv], does not.

*Age weighting.* Weight by how long coins have already been held. For
shielded notes this is provable today without a consensus change: the note
commitment tree is append-only, so a note's position bounds its creation
height, and the proof-of-balance draft [^draft-str4d-balance-proof] already
proves holding at a snapshot. In the *Ironwood pool*, age is bounded by the
pool's activation in July 2026 [^zip-0258] and reset by migration
[^zip-0318]. It is backward-looking, so it does not express willingness to
stay, but it defeats buy-vote-sell and last-minute locks directly. Not
adopted here; see [Open questions].

*Time-averaged balance.* Several snapshots, several proofs per ballot, still
passive. A forward lock supplies its own window.

## Rationale for the cap and floor

The cap is one halving interval: the longest horizon over which the protocol
itself plans issuance, and the four-year maximum of vote-escrow systems
[^curve-vecrv]. The floor is non-zero so that this ZIP does not change who
can vote; zero would exclude every shielded holder until Class S exists. One
tenth is the weight of an unlocked vote in Polkadot's conviction voting
[^polkadot-opengov].

## Rationale for measuring in blocks

`OP_CHECKLOCKTIMEVERIFY` heights are blocks, and NU7 cuts the target spacing
from 75 to 25 seconds [^zip-0218], so a lock expressed in time would change
meaning at activation. Measuring $\ell$ and $L$ in blocks at height $S$ keeps
the weight well defined.


# Open questions

* Will any poll operator add a Class T path to a shielded-only mechanism, and
  what is $M$ there?
* Should past holding (age) count toward $\ell$, generally or as the shielded
  interim before Class S?
* Are $f = 1/10$ and $L$ = one halving interval right? Should $f$ drop to
  zero once Class S exists?
* Should a lock have to reach past a fixed horizon rather than only past $C$?
* Should Coinholder-Controlled Fund coins held by the Key-Holder
  Organizations [^zip-0271] be excluded? ZIP 1016 restricts no one.
* Should Class T accept time-form or `OP_CHECKSEQUENCEVERIFY` locks
  (ZIP 112 [^zip-0112])?
* ZIP 1016 decides on ZEC cast in favour and, between competing grants, on
  ZEC committed in support. Deciding on $W$ changes that; applying this ZIP
  to ZIP 1016 votes needs its Owners and an Updates header.
* Which network upgrade could carry Class S? `[VERIFY: NU8 planning]`


# Deployment

This ZIP applies to a poll when the operator announces, before $S$, that the
poll follows it. Class T is usable once an operator implements its
verification. Class S is usable only after its consensus ZIP activates on
Mainnet; until then, shielded coins vote under Class H at the floor weight.


# References

[^BCP14]: [Information on BCP 14 — "RFC 2119: Key words for use in RFCs to Indicate Requirement Levels" and "RFC 8174: Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words"](https://www.rfc-editor.org/info/bcp14)

[^protocol-networks]: [Zcash Protocol Specification, Version 2026.8.0 [NU6.3]. Section 3.12: Mainnet and Testnet](protocol/protocol.pdf#networks)

[^zip-0112]: [ZIP 112: CHECKSEQUENCEVERIFY](zip-0112.rst)

[^zip-0218]: [ZIP 218: 25-second Block Target Spacing](zip-0218.md)

[^zip-0229]: [ZIP 229: Version 6 Transaction Format](zip-0229.md)

[^zip-0237]: [ZIP 237: Network Sustainability Mechanism](zip-0237.md)

[^zip-0258]: [ZIP 258: Deployment of the NU6.3 Network Upgrade](zip-0258.md)

[^zip-0271]: [ZIP 271: Deferred Dev Fund Lockbox Disbursement](zip-0271.md)

[^zip-0318]: [ZIP 318: Orchard to Ironwood Migration](zip-0318.md)

[^zip-1015]: [ZIP 1015: Block Subsidy Allocation for Non-Direct Development Funding](zip-1015.rst)

[^zip-1016]: [ZIP 1016: Community and Coinholder Funding Model](zip-1016.md)

[^zip-2001]: [ZIP 2001: Lockbox Funding Streams](zip-2001.rst)

[^draft-str4d-balance-proof]: [draft-str4d-orchard-balance-proof: Air drops, Proof-of-Balance, and Stake-weighted Polling](draft-str4d-orchard-balance-proof.md)

[^bip-0065]: [BIP 65: OP_CHECKLOCKTIMEVERIFY](https://github.com/bitcoin/bips/blob/master/bip-0065.mediawiki)

[^zebra-script]: [Zebra: zebra-script/src/lib.rs, script verification flags P2SH and CHECKLOCKTIMEVERIFY](https://github.com/ZcashFoundation/zebra/blob/main/zebra-script/src/lib.rs)

[^zebra-locktime]: [Zebra: zebra-chain/src/transaction.rs, `Transaction::lock_time`](https://github.com/ZcashFoundation/zebra/blob/main/zebra-chain/src/transaction.rs)

[^forum-nu7-vote]: [Zcash Community Forum: NU7 Coinholder Vote](https://forum.zcashcommunity.com/t/nu7-coinholder-vote/56912)

[^zcashlabs-voting]: [Zcash Labs: NU7 coinholder vote](https://zcashlabs.org/voting)

[^coindesk-nu7]: [CoinDesk: Zcash holders overwhelmingly back faster transactions and bitcoin-style halvings, 2026-09-16](https://www.coindesk.com/tech/2026/09/16/zcash-holders-overwhelmingly-back-faster-transactions-and-bitcoin-style-halvings)

[^zfnd-nu7-results]: [Zcash Foundation: NU7 Polling Results: What We Heard and Where We Go From Here](https://zfnd.org/nu7-polling-results-what-we-heard-and-where-we-go-from-here/)

[^curve-vecrv]: [Curve DAO: Vote-Escrowed CRV (veCRV)](https://resources.curve.finance/vecrv/overview)

[^polkadot-opengov]: [Polkadot Wiki: Polkadot OpenGov — Voluntary Locking (Conviction Voting)](https://wiki.polkadot.com/learn/learn-polkadot-opengov/)
