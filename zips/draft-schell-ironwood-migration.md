    ZIP: Unassigned
    Title: Orchard to Ironwood Migration
    Owners: Schell Carl Scivally <efsubenovex@gmail.com>
            Pacu Gindre <pacu@zecdev.org>
    Credits: Kris Nuttycombe <kris@nutty.land>
    Status: Draft
    Category: Wallet
    Created: 2026-06-16
    License: MIT
    Discussions-To: <https://github.com/zcash/zips/issues/1315>


<div class="note"></div>

This document is a pre-proposal working draft produced for discussion with the
librustzcash / Zcash team. It unifies two earlier drafts: a stateful,
background-scheduled wallet flow (issue #1315, "Path A") and a stateless,
chain-recoverable quantization proposal (PR #1299). It is modeled in part on
ZIP 308 (Sprout to Sapling Migration) [^zip-0308] and adapts that precedent to an
*Orchard*-to-*Ironwood* migration. It is **not** a ratified ZIP. All numeric
parameters are provisional and require ratification (see [Open issues](#openissues)).


# Terminology

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", "MAY", and "RECOMMENDED"
in this document are to be interpreted as described in BCP 14 [^BCP14] when, and
only when, they appear in all capitals.

The terms "*Orchard pool*" and "*Ironwood pool*" are to be interpreted as
described in ZIP 229 [^zip-0229]. Following the convention in the protocol
specification [^protocol], we use *slanted text* to refer to pool names, in order
to more clearly distinguish them from shielded protocols.

The term "network upgrade" is to be interpreted as described in ZIP 200.
[^zip-0200]

The terms "Mainnet" and "Testnet" are to be interpreted as defined in the Zcash
protocol specification. [^protocol-networks]

The terms "trusted TXO", "untrusted TXO", "known-spendable", and
"confirmed-spendable" are to be interpreted as defined in ZIP 315. [^zip-0315]

The terms below are to be interpreted as follows:

Migration
:   The process by which a wallet transfers a user's funds from the *Orchard pool*
    to the *Ironwood pool*.

Pool-crossing transfer
:   A transaction that moves value from one shielded pool to another. The net
    amount crossing between the pools is revealed on-chain. [^zip-0209]

Note splitting
:   A wallet-internal send-to-self transaction whose purpose is to divide a small
    number of larger notes into a larger number of smaller notes, so that
    subsequent migration transactions can be created without waiting for change
    from earlier ones to confirm.

Migration transaction (or part)
:   A single pool-crossing transfer that moves part of the user's *Orchard-pool*
    balance to the *Ironwood pool* as part of a migration. In the recommended
    amount-selection scheme each migration transaction moves exactly one
    denomination.

Denomination
:   A canonical power-of-ten amount (for example `100, 10, 1, 0.1, 0.01` ZEC),
    bounded above by `DENOM_CAP` and below by `DUST_FLOOR`.

Anchor-height bucket (boundary)
:   A shared, network-wide interval of block heights delimited by *boundaries*:
    blocks whose height is $\equiv 0 \pmod{M}$ for a network-wide modulus $M$
    (provisionally 256). The anchor height of a migration transaction is drawn
    from a bucket rather than from the wallet's own chain tip, so that the anchor
    does not reveal when a particular wallet last synchronized.

Cohort
:   The set of all migration transactions, from all wallets, assigned to the same
    anchor-height bucket.

Multiplicity ($k$)
:   The number of migration transactions a single wallet contributes to one
    cohort.

Migration schedule
:   The ordered set of migration transactions, together with their assigned
    anchor-height buckets and broadcast windows, that a wallet plans in order to
    complete a migration.

Background scheduling
:   The use of platform mechanisms (for example, *BGTaskScheduler* on iOS or
    *WorkManager* on Android) to broadcast a migration transaction at an
    approximate future time without requiring the user to have the application in
    the foreground.


# Abstract

The *Ironwood pool* is a new shielded pool introduced by the NU6.3 network
upgrade [^zip-0258]. It uses the same Orchard shielded protocol as the
*Orchard pool* [^zip-0229], and exists for two reasons. First, its notes use a
quantum-recoverable construction [^zip-2005], so that funds held in it could be
recovered after a future post-quantum transition, whereas funds left in the
*Sprout*, *Sapling*, or *Orchard pools* would be lost if those protocols had to
be disabled to defend against a discrete-log-breaking (for example, quantum)
adversary. Second, as part of NU6.3 the shared Orchard Action circuit gains a
flag that disables ordinary payments within the old *Orchard pool* while still
permitting change [^zip-2006] [^draft-zodl-valargroup-action-circuit-update];
this turnstile both protects users and provides ongoing evidence that no
counterfeiting has taken place. Because ordinary transfers within the old *Orchard pool* become restricted once
NU6.3 activates, migrating to the *Ironwood pool* is effectively necessary rather
than optional, and wallets should treat it as such.

This ZIP specifies best practices for wallets performing this migration. It is
written with light client wallets in mind, because their reliance on a light
wallet server and on mobile background scheduling makes these privacy and
reliability concerns most acute, but the same practices apply to desktop and
full-node wallets. Because a pool-crossing transfer reveals the migrated amount on-chain,
a naive migration risks linking transfers to a single wallet and to the user's
activity. To mitigate this, the wallet decomposes the balance into several
smaller transfers spread over time. The transfer amounts are RECOMMENDED to be
canonical power-of-ten denominations: because many wallets emit the same canonical
values, individual transfers collide across the migrating population and so resist
fingerprinting, whereas high-entropy random amounts would each be near-unique. A
wallet MAY instead use any amount-splitting strategy that achieves the same broad
value collision. Each transfer is broadcast at an anchor height drawn from a
shared network-wide bucket, forming cohorts that mix many wallets and
de-correlate transfers from when the user opens the application.

The migration runs as a two-phase process: a note-splitting phase followed by a
scheduled transaction-creation phase. Migration transactions are pre-signed,
persisted, and broadcast by best-effort background tasks, with a fallback that
prompts the user on the next application open when a scheduled window is missed.
Synchronization is kept decoupled in time from broadcast. This ZIP also specifies
user-consent, network-privacy, progress-reporting, and error-handling
requirements.


# Motivation

The *Ironwood pool* changes the construction of Orchard-protocol notes so that
funds held in it can be recovered after a future post-quantum transition, whereas
funds in the *Sprout*, *Sapling*, and *Orchard pools* could not be. [^zip-2005]
A soundness concern motivating the new pool is summarized in
[Consensus context](#consensuscontext). For these reasons users are expected to
migrate *Orchard-pool* funds to the *Ironwood pool* well in advance of any need
to disable the older protocols.

Migrating funds between shielded pools is fundamentally different from spending
within a single pool. Within a pool, both balances and the relationships between
transactions remain private. A pool-crossing transfer, however, reveals the net
amount crossing between the pools on-chain. [^zip-0209] (Why this leak is
unavoidable is explained in [Why amounts leak](#whyamountsleak).) If a wallet
migrates a user's entire balance in a single transaction, that amount, its
timing, and (via network-layer metadata) potentially the user's IP address are
all exposed at once, and the transfer can be correlated with the wallet's other
activity.

ZIP 315 [^zip-0315] already establishes that the user's consent is needed to
reveal amounts publicly, and that wallets should minimize pool crossing. A mass
migration event is a case where many users perform pool-crossing transfers in a
relatively short window. This both creates an opportunity (many simultaneous
migrations form an anonymity set) and a risk, because an observer who can
distinguish one user's transfers from the crowd learns a great deal.

A precedent exists in ZIP 308 [^zip-0308], which defined a privacy-preserving
procedure for the Sprout-to-Sapling migration by sending a bounded amount per
period and hiding individual migration transactions among those of all migrating
users. This ZIP adapts that idea to the light-client setting, where the wallet
does not run a full validator, scheduling is constrained by mobile operating
systems, and synchronization happens against a light wallet server whose operator
is a potential observer. The security analysis of migration strategies is subtle,
and the more obvious strategies leak significant information; this document
records the analysis behind the chosen strategy, including several rejected
alternatives (see [Rejected alternatives](#rejectedalternatives)).

The goal of this ZIP is therefore to document how a light client wallet SHOULD
perform the Orchard-to-Ironwood migration so that, by default, individual
transfers are as hard as practical to correlate to a specific wallet or to the
user's behaviour, while still completing the migration reliably and giving the
user enough information to consent to any residual information leakage.


# Consensus context

This section is non-normative. It summarizes the *Ironwood* network upgrade
consensus-rule context within which this migration procedure operates.

## The Ironwood pool

The *Ironwood pool* is defined by the NU6.3 consensus changes, whose primary
sources are the Zcash Protocol Specification [^protocol], the version 6
transaction format [^zip-0229], the Orchard Action circuit update
[^draft-zodl-valargroup-action-circuit-update], ZIP 2005 [^zip-2005], and
ZIP 2006 [^zip-2006], with the NU6.3 activation parameters fixed by ZIP 258
[^zip-0258]. Its properties that matter for this procedure are:

* The *Ironwood pool* uses the **same Orchard shielded protocol** (the same
  Action circuit) as the *Orchard pool*. It is nonetheless a distinct value
  pool, with its own chain value pool balance ($\mathsf{valueBalanceIronwood}$),
  its own note commitment tree and anchor, and its own nullifier set.
  [^zip-0229]
* *Ironwood* notes use the **quantum-recoverable note plaintext** construction
  (an *Ironwood-pool* note plaintext has a lead byte of $\mathtt{0x03}$ or
  greater). [^zip-2005] This is the change that makes *Ironwood* funds
  recoverable after a future post-quantum transition, and is why migrating ahead
  of any such transition is worthwhile.
* *Ironwood* addresses are identical to the user's existing *Orchard* address;
  what differs is the pool in which a note is created, not the address. A wallet
  treats the *Ironwood pool* as a distinct pool with its own identifier (see
  [Destination](#destination)).
* The *Ironwood chain value pool* balance cannot become negative [^zip-0209],
  the same turnstile constraint applied to the other shielded pools.

## Turnstile and disabled Orchard payments

This migration procedure operates within the following consensus context:

1. *Ironwood* introduces a new pool using the Orchard protocol, alongside the
   existing *Orchard pool*.
2. The Orchard circuit (shared by both pools) gains a flag, toggleable by
   consensus rules, that **disables payments to other users within the pool while
   still permitting change notes**. (This is a privacy/turnstile safeguard.)
3. After the upgrade, the **old *Orchard pool* has this flag enabled**, and
   **payments into the old pool are disabled** by constraining `valueBalance`.
4. Because payments are disabled on the old pool, wallets must send new payments
   to Orchard receivers (inside existing unified addresses) **via the new
   (*Ironwood*) pool**, and they **should migrate funds away from the old pool**.

Together these enforce a bound on the circulating supply of ZEC via the existing
turnstile mechanism (no one can transact with more ZEC than is supposed to
exist). Migrating funds both protects users from risk and gradually provides
evidence that no counterfeiting took place. Auditing and formal-verification
efforts for the circuit are ongoing.

Consequences for this procedure:

- This document covers **migrating funds out of the old *Orchard pool* into
  *Ironwood***. The separate routing change in (4), that *new payments* to
  Orchard receivers must go via *Ironwood*, is a general send-path concern and is
  **out of scope** here (the migration destination is, however, the same
  *Ironwood* receiver).
- Because the old pool can no longer carry ordinary payments, post-upgrade it
  contains little other than migration-shaped transactions. This reinforces the
  ZIP 308 stance that migration transactions need only be hidden **among
  themselves** (see [Non-requirements](#non-requirements)).
- The consensus flag constrains the *structure* of permissible old-pool spends
  (spends + change, no arbitrary payments); the canonical
  migration-transaction predicate in this document SHOULD be aligned with the
  consensus-allowed spend shape rather than defined independently. The precise
  interaction (in particular, that a cross-pool migration spend is not itself
  treated as a prohibited "payment to another user") is a dependency on the final
  consensus-rule text.


# Why amounts leak

This section is non-normative.

In an Orchard-style bundle, each action publishes a value commitment (`cv_net`)
that is perfectly hiding, and the bundle as a whole publishes a single cleartext
signed integer `value_balance` equal to (spends − outputs) for that pool. A
binding signature cryptographically forces `value_balance` to equal the true net
of the hidden per-action commitments, so it cannot be falsified.

Consequently, a transaction that moves value **across** a pool boundary
(*Orchard* → *Ironwood*) publicly reveals:

- the net amount leaving *Orchard* (`value_balance` of the Orchard bundle), and
- the net amount entering *Ironwood* (`value_balance` of the Ironwood bundle),

both in cleartext, linked within the same transaction by the txid. The fee is
publicly computable as the sum of all pools' value balances. The zero-knowledge
proof does **not** and **cannot** hide this; hiding it would require a different
cross-pool construction.

Therefore the only privacy levers available to a wallet are the **shape of the
amounts** it chooses to migrate, and the **timing** with which it broadcasts
them. Both levers are exercised by the specification below.


# Requirements

The migration flow MUST satisfy the following high-level goals. The Specification
section defines how they are met; this section does not itself impose conformance
requirements beyond those.

* The user MUST be able to migrate *Orchard-pool* funds to the *Ironwood pool*,
  and MUST be informed that doing so is necessary to retain access to those funds.

* The wallet MUST obtain the user's consent, before any funds leave the
  *Orchard pool*, to the public revelation of pool-crossing amounts, consistent
  with ZIP 315. [^zip-0315]

* All *Orchard-pool* funds at or above the dust floor SHOULD eventually be
  transferred to the *Ironwood pool*.

* By default the migration SHOULD de-correlate individual transfers from each
  other and from the user's interaction with the application, to the extent
  practical on the target platform. In particular it SHOULD mitigate leakage of:
  the linkage of particular migration transactions to one another (clustering);
  information about the distribution of individual note values; and information
  about a wallet's total balance.

* The migration SHOULD let a user complete migration with a small number of
  signing sessions for typical balances, because adoption drives the size of the
  anonymity set on which everyone's privacy depends.

* The migration SHOULD complete reliably even when best-effort background
  scheduling does not run, without requiring the user to keep the application in
  the foreground.

* The user MUST be given an informed choice about network-layer privacy (Tor or
  VPN) before the migration begins.

* The wallet MUST report migration progress and MUST NOT present the fallback
  (prompting on the next application open) as an error.

* The migration MUST adapt safely when the user spends *Orchard-pool* funds
  outside the migration, when scheduled transactions expire, or when the
  application is reinstalled.


# Non-requirements

The following are explicitly **not** requirements of this flow:

* **Statelessness.** The migration is permitted to rely on locally persisted
  state (the migration schedule and pre-signed transactions). It is not required
  to be reconstructible from on-chain data alone. (The tradeoff against a
  stateless, chain-recoverable design is discussed in
  [Rationale for the stateful design](#rationaleforthestatefuldesign).)

* **Multi-device and recovery continuity.** A migration in progress is not
  required to be resumable on another device, nor after restoring from seed on a
  new device. A wallet that detects unspent *Orchard-pool* funds after such a
  restore MAY treat the situation as a fresh migration.

* **Guaranteed background execution.** Background scheduling is best-effort.
  Wallets are not required to guarantee that any transfer is broadcast without the
  user ever opening the application.

* **Network-layer anonymity.** Network-layer anonymity (for example, Tor) is
  offered as an opt-in but is not mandated; the user MAY proceed without it.

* **Provably leak-free migration.** The procedure does not have to provably leak
  no information; migration transactions need only be hidden among themselves
  (see [Consensus context](#consensuscontext)), and a small amount below the dust
  floor MAY be left unmigrated where this helps privacy or economy.

* **Strong protection for very large holders.** Large holders ("whales") are only
  weakly protected, and this is accepted; see
  [Whale handling](#whalehandling).


# Specification

## Overview, two-phase architecture

A wallet performing a privacy-preserving migration SHOULD implement it as two
phases:

1. **Note splitting** (see [Phase 1, Note splitting](#phase1notesplitting)): a
   wallet-internal send-to-self that divides the *Orchard-pool* balance into
   appropriately sized notes.

2. **Scheduled migration transactions** (see
   [Phase 2, Scheduled migration transactions](#phase2scheduledmigrationtransactions)):
   pre-signed pool-crossing transfers, each transferring a canonical denomination
   and assigned to an anchor-height bucket, broadcast by best-effort background
   tasks.

A wallet MAY offer an immediate single-transfer migration in addition to the
privacy-preserving flow (see
[Migration entry point and user consent](#migrationentrypointanduserconsent)),
but it MUST present the privacy trade-off of doing so.

## Migration entry point and user consent

When a wallet detects a non-zero confirmed-spendable *Orchard-pool* balance after
the *Ironwood pool* has activated, it SHOULD surface a dedicated migration entry
point.

* The entry point MUST display the *Orchard-pool*-specific balance at risk, and
  MUST NOT present only a unified total that hides how much is in the
  *Orchard pool*.

* The wallet SHOULD offer the user a choice between:

  * **Migrate immediately**: a single pool-crossing transfer with no delay and
    minimal privacy; and
  * **Migrate with privacy**: the scheduled, quantized approach specified below.

* Before any funds leave the *Orchard pool*, the wallet MUST present the full
  proposed migration schedule and obtain the user's confirmation. This
  confirmation constitutes the user's consent, required by ZIP 315 [^zip-0315], to
  the public revelation of the pool-crossing amounts.

* Once the schedule is confirmed, individual transfers within it SHOULD be
  broadcast automatically when their window arrives, and SHOULD NOT require
  separate per-transfer confirmation.

To keep the choice tractable for users who may not know what is best, the wallet
SHOULD minimize the number of privacy-tuning options exposed.

## Phase 1, Note splitting

The purpose of note splitting is to ensure that migration transactions can be
created without waiting for change from earlier ones to confirm.

* Note splitting MUST be implemented as a wallet-internal send-to-self
  transaction with no external receiver.

* It is RECOMMENDED that a wallet require a successful note split before beginning
  Phase 2 of a privacy-preserving migration, unless the *Orchard-pool* balance
  already consists of suitably sized notes (for example, a single small note), in
  which case note splitting MAY be skipped.

* Note splitting MAY be performed at any time after the user initiates the
  migration, including before the network upgrade that activates the
  *Ironwood pool* has finalized. Performing it early MUST NOT degrade the user's
  normal transacting experience.

* If the user does not split notes before the *Ironwood pool* activates, the
  wallet MUST either perform the split afterwards or accept longer waits between
  migration transactions while change confirms.

* The wallet MUST wait for the note-splitting transaction to confirm before
  treating the resulting notes as available for migration, consistent with the
  confirmation requirements for trusted TXOs in ZIP 315. [^zip-0315]

### Open questions for Phase 1

* The maximum note size produced by note splitting, and whether a single
  note-splitting transaction can accommodate very large balances (for example, on
  the order of $10^6$ ZEC), is an open point.

* The exact splitting heuristic (number of notes and their sizes) is an open
  point for the Zcash core team. Sizing notes so that the canonical denominations
  of [Amount selection, canonical quantization](#amountselectioncanonicalquantization)
  can each be funded without waiting on change is a natural target.

## Phase 2, Scheduled migration transactions

### Amount selection, canonical quantization

The migratable *Orchard-pool* balance MUST be decomposed into a set of migration
transactions, each transferring a single denomination. It is RECOMMENDED that the
denominations be selected by **canonical power-of-ten quantization** rather than
by random or arbitrary sizing, because canonical denominations collide across
wallets and therefore resist fingerprinting (see
[Why value collision provides privacy](#whyvaluecollisionprovidesprivacy)).
A wallet MAY use a different amount-selection strategy provided it achieves the
same effect, namely that migrated amounts collide across the migrating population
rather than fingerprinting the wallet. Random arbitrary amounts do not achieve
this and are a rejected alternative (see
[Rejected alternatives](#rejectedalternatives)).

* Permitted denominations are `DENOM_CAP, …, 1, 0.1, 0.01, …, DUST_FLOOR` ZEC,
  each an exact power of ten. `DENOM_CAP` is provisionally **100 ZEC**.

* The balance is decomposed by **decimal digit expansion** of the integer- and
  fractional-ZEC digits, except that no denomination exceeds `DENOM_CAP`: digits
  in the `≥ DENOM_CAP` place produce multiple `DENOM_CAP` parts. For example, with
  `DENOM_CAP = 100`:

  ```
  123.45  ZEC -> [100, 10, 10, 1, 1, 1, 0.1, 0.1, 0.1, 0.1, 0.01, 0.01, 0.01, 0.01, 0.01]
  540     ZEC -> [100, 100, 100, 100, 100, 10, 10, 10, 10]
  ```

* The quantization is a **pure, deterministic function of the balance**: there is
  no rare, high-entropy "remainder" output. Every emitted denomination is
  canonical and therefore collision-prone across wallets. This is the key privacy
  property (see [Privacy Implications](#privacyimplications)).

* Value below `DUST_FLOOR` MAY be left unmigrated.

The fee for each part is in addition to its denomination (the visible
Orchard-out value of a part is its denomination plus the canonical fee;
equivalently the *Ironwood* output equals the denomination). Each migration
transaction SHOULD have:

* exactly one *Ironwood* output, whose value is a single canonical denomination;
* no transparent inputs or outputs;
* no spends from any pool other than *Orchard*;
* the canonical fee (provisionally the ZIP 317 minimum fee) [^zip-0317];
* the canonical anchor described in
  [Anchor-height bucketing and cohorts](#anchor-heightbucketingandcohorts) and a
  canonical expiry;
* `lock_time = 0`;
* no developer-fee output or any other extra output (this would partition the
  anonymity set between wallets that add it and those that do not).

This strict, uniform structure also serves as a canonical migration-transaction
predicate, useful both for chain-based status recovery and for keeping all
wallets' migration transactions structurally indistinguishable.

### Anchor-height bucketing and cohorts

* The anchor height of each migration transaction MUST be selected from a shared,
  network-wide anchor-height bucket, rather than from the wallet's own chain tip,
  so that the anchor does not reveal when this wallet last synchronized.

* Buckets are delimited by **boundaries**: blocks whose height is
  $\equiv 0 \pmod{M}$, with $M$ provisionally `256`. At the current target block
  spacing of 75 seconds, a boundary occurs roughly every
  $256 \times 75\,\text{s} \approx 5.3$ hours (on the order of a quarter day). A
  longer interval increases privacy; a shorter interval speeds up the migration.

* Each migration transaction MUST take, as its *Orchard* anchor, the tree state as
  of the **previous boundary** of its assigned bucket (the most recent block
  height $\equiv 0 \pmod{M}$ before the transaction is broadcast). Because this
  anchor is identical for every wallet sending into the same bucket, it carries no
  per-wallet timing information, and sharing it does **not** link a wallet's
  transactions to one another.

* The set of all migration transactions assigned to one bucket forms a **cohort**.
  A wallet MAY contribute several migration transactions to the same cohort
  (multiplicity $k \geq 1$), because all denominations are canonical and therefore
  not attributable to a single wallet by their values (see
  [On multiplicity and cohorts](#onmultiplicityandcohorts)).

* A wallet SHOULD choose $k$ to target a small total number of signing sessions
  for typical balances (provisionally a target of about **6 signing sessions**):
  roughly $k \approx \lceil \text{number of denominations} / \text{target sessions} \rceil$.
  $k$ per cohort MUST be bounded by `K_MAX`. For balances large enough that the
  target session count would require $k >$ `K_MAX`, the number of signing sessions
  grows instead (see [Whale handling](#whalehandling)).

### Transfer scheduling

* Each migration transaction MUST be assigned to a future anchor-height bucket,
  and the wallet MUST propose the complete schedule to the user before any
  transfer is sent, obtaining confirmation of the whole schedule (see
  [Migration entry point and user consent](#migrationentrypointanduserconsent)).

* Spreading a wallet's transfers across several buckets, together with
  de-correlated broadcast times, is the primary means by which the wallet's own
  transfers are kept from being linked to one another; distinct per-wallet anchor
  heights are **not** required, because the shared boundary anchor already carries
  no per-wallet information.

* The split count, the target number of signing sessions, and the bucket interval
  $M$ are open points for the Zcash core team; see [Open issues](#openissues).

### Pre-signed transaction storage

* Once the schedule is committed, migration transactions SHOULD be pre-signed and
  persisted, reusing the wallet's existing transaction-resubmission storage
  mechanism where one exists.

* Pre-signing freezes the anchor at signing time under the current
  transaction-digest rules [^zip-0244]. To avoid the resulting anchor-staleness
  leak, a wallet MUST either build and sign each transaction at (or close to) its
  broadcast boundary, or rely on the forward-looking digest change recommended in
  [Rationale for anchor selection](#rationaleforanchorselection), under which the
  anchor can be chosen at broadcast time without re-signing.

* If a stored transaction becomes invalid (for example, because its input notes
  were spent outside the migration, or it expired), the wallet MUST detect this
  and prompt the user to re-initiate the affected step (see
  [Error handling](#errorhandling)).

### Background scheduling

* Background scheduling MUST be treated as best-effort. The operating system
  chooses the exact execution time within the requested window.

* A background task MUST broadcast only; it MUST NOT trigger a wallet
  synchronization (see
  [Decoupling synchronization from broadcast](#decouplingsynchronizationfrombroadcast)).

* If a scheduled window is missed, the wallet MUST fall back to prompting the user
  on the next application open (see
  [Fallback on application open](#fallbackonapplicationopen)).

Platform-specific guidance is given in
[Platform considerations](#platformconsiderations).

### Decoupling synchronization from broadcast

* The wallet MUST NOT perform a wallet synchronization in the same background
  session as a migration broadcast, because doing so would let an observer
  correlate the synchronization with the broadcast.

* Where a synchronization is needed, it MUST be separated in time from any
  broadcast. In particular, a migration transaction that outputs change back to
  the *Orchard pool* requires the wallet to synchronize before that change can be
  spent; the wallet MUST schedule that synchronization decoupled in time from the
  broadcast of the next migration transaction.

The minimum synchronization required before the first scheduled send (for example,
to spend pre-upgrade *Orchard-pool* change), and how a wallet determines when a
synchronization is needed, are open points.

### Fallback on application open

* On every application launch, the wallet MUST reconcile the scheduled broadcast
  times against the transfers actually completed, and MUST surface any overdue
  transfers. This on-launch reconciliation is the primary catch-up mechanism and
  MUST NOT rely on notification delivery.

* When the user is prompted to send overdue transfers, the wallet MUST disclose
  that sending them at application-open time correlates the broadcasts with the
  user's activity, weakening the privacy of those transfers.

* When the user chooses to send overdue transfers immediately, the wallet SHOULD
  broadcast them in sequence rather than simultaneously, to avoid bundling them in
  the same block.

* When a window is missed and the remaining transfers are rescheduled, the wallet
  SHOULD shift the remaining schedule by the offset (or re-assign overdue
  transfers to the next available anchor-height buckets).

* A slip of up to approximately two hours in which the background task eventually
  runs SHOULD be treated as normal operation and SHOULD NOT be surfaced as an
  error.

## Destination

* The destination of a migration MUST be the *Ironwood pool* only. Migration to
  the *Sapling pool* MUST NOT be offered or recommended as part of this flow.

* *Ironwood* addresses are identical to the user's existing *Orchard* address; the
  wallet treats the *Ironwood pool* as a distinct pool with its own identifier. No
  special address handling or memo-based tagging is required, and self-send
  detection is handled by the wallet's existing account logic.

## Network-layer privacy

Before the schedule is committed, the wallet MUST present a network-privacy step.

* No network-privacy option MAY be pre-selected or defaulted.

* The wallet SHOULD offer a Tor toggle. When enabled, all migration transaction
  broadcasts MUST be routed through Tor. [^tor]

* If Tor is unavailable on the user's network or region, the wallet SHOULD suggest
  using a trusted VPN before proceeding.

* The user MAY proceed without Tor or a VPN; the choice is the user's.

* The wallet MUST display a disclaimer explaining the IP-correlation risk: because
  pool-crossing transfers are visible on-chain, without network-level privacy a
  server or network operator can correlate the broadcasting IP address with the
  on-chain event.

* Broadcasting migration transactions to a different server than the one used for
  synchronization MAY further reduce correlation, and a wallet MAY do so.

## Platform considerations

This section is non-normative except where it restates requirements from
[Background scheduling](#backgroundscheduling) and
[Decoupling synchronization from broadcast](#decouplingsynchronizationfrombroadcast).
The flow applies to both iOS and Android; differences are noted where they affect
implementation.

### iOS

* Background scheduling SHOULD use *BGTaskScheduler* with a background-processing
  task type suitable for longer work.
* The task MUST broadcast only and MUST NOT trigger synchronization.
* If the task does not run, the next application open MUST surface the fallback
  prompt.

### Android

* Background scheduling SHOULD use *WorkManager* with a flex interval aligned to
  the anchor bucket.
* The Worker MUST broadcast only and MUST NOT trigger synchronization.
* OEM battery-optimization behaviour (for example on MIUI or One UI) may suppress
  tasks even when permissions are granted; this is acknowledged as a known
  limitation. During onboarding the wallet SHOULD request a battery-optimization
  exemption to improve reliability, and MUST continue to function (relying on the
  on-launch fallback) if the exemption is denied.
* On every application launch, the wallet MUST reconcile whether a pending
  transfer is overdue and surface the fallback prompt if needed.
* WorkManager task persistence across reboots SHOULD be verified by the
  implementation; if a boot receiver is used to re-enqueue tasks, the relevant
  platform permission must be declared.

## Status notifications

* On a successful transfer, the wallet MAY show a notification.

* On a failed transfer, the wallet MUST surface the failure with the ability to
  retry. The retry affordance SHOULD lead to a self-contained screen that does not
  start a synchronization.

* Notification delivery MUST NOT be relied upon as the primary status mechanism;
  on-launch reconciliation is primary (see
  [Fallback on application open](#fallbackonapplicationopen)).

* On platforms where notifications can be cleared by a reboot or suppressed by the
  OS or OEM managers (notably Android), the wallet MUST disclose that notification
  delivery is not guaranteed and MUST direct the user to return to the application
  to check progress.

## Progress visibility

The wallet SHOULD report migration progress.

## User-facing copy requirements

Because background scheduling is best-effort, product copy MUST NOT describe the
migration as automatic or guaranteed. The fallback of prompting on the next
application open MUST be presented as a normal part of the flow, not as an error
state.

## Error handling

The wallet MUST handle at least the following conditions.

* **Transient broadcast failure (network unavailable).** The stored pre-signed
  transaction MUST NOT be discarded. The task SHOULD retry within its window and
  rely on background backoff for the next window. If broadcast continues to fail,
  the on-launch fallback MUST offer the user the choice to send now or retry in
  the background.

* **Invalid transaction (input note already spent).** If the user spends
  *Orchard-pool* funds outside the migration, a queued migration transaction may
  become invalid. The wallet MUST detect this (the detection condition is that
  the confirmed-spendable *Orchard-pool* balance is greater than zero while the
  next scheduled migration transaction is missing or invalid), MUST notify the
  user of the failure, and MUST construct a revised schedule for the remaining
  unspent balance using a fresh anchor. The screen that does so MUST be
  self-contained and MUST NOT trigger a synchronization.

* **Expired transaction.** A pre-signed transaction that reaches its expiry height
  [^zip-0203] before being broadcast MUST be detected on the next application open
  and handled in the same way as an invalid transaction: a new transaction with a
  fresh anchor and expiry is constructed for the remaining balance, with its
  denomination unchanged.

* **Negligible remaining balance.** If, after the last scheduled transfer, only an
  amount below a significance threshold remains (for example, due to fee
  rounding), the wallet MAY treat the migration as complete and inform the user
  that a negligible amount remains. If the remaining amount is above the
  threshold, the wallet SHOULD add a final transfer. Wallets SHOULD apply the
  ZIP 317 marginal-fee considerations [^zip-0317] when deciding whether a residual
  note is economic to migrate.

* **Note-split transaction unconfirmed or failed.** If the application is closed
  before the note-splitting transaction confirms, on re-open the wallet MUST
  report that it is waiting for confirmation and MUST proceed to scheduling once
  the split confirms. If the split transaction expired, the wallet MUST offer to
  retry it.

* **Application reinstall or restore on a new device.** On detecting unspent
  *Orchard-pool* funds with no local migration state, the wallet MAY treat the
  situation as a fresh migration (already-confirmed transfers remain on-chain;
  only the remaining balance is rescheduled). See
  [Non-requirements](#non-requirements).


# Rationale

## Rationale for the scheduled background approach

The chosen approach broadcasts migration transactions from best-effort background
tasks at pre-determined, anchor-bucketed times that are de-correlated from the
user's interaction with the application. An alternative considered was a guided
"on-open" approach (referred to in the source material as "Path B"), in which each
transfer is created at the moment the user opens the application.

The on-open approach was dismissed primarily because user-triggered sends leak too
much information: the scan ranges a wallet requests from a light wallet server
already link its notes to one user, and if each pool-crossing send also coincides
with an application open, an observer can monitor the wallet across the entire
migration. It also provides no temporal de-correlation, because every transfer is
anchored to the moment of user interaction.

The scheduled approach achieves temporal de-correlation in the common case. Its
worst case (when no background task ever runs and the user sends everything on a
single application open) is no worse than the on-open approach, while its best
case is significantly better. Pre-signed transactions can be stored using existing
transaction-resubmission infrastructure.

## Rationale for the stateful design

An attractive alternative, explored in an earlier draft of this proposal, is a
**stateless, chain-recoverable** design: persist no scheduler state at all, and
instead recover migration progress from the chain using the wallet's viewing keys
(identifying migration transactions by the canonical predicate) plus a
deterministic re-computation of the quantization of the remaining balance. Because
the quantization is a pure function of the balance, it recomputes identically on
every activation and after restore-from-seed, which makes that design robust to
restart and to multi-device restore.

This unified proposal nonetheless adopts a **stateful** design (a persisted
schedule plus pre-signed transactions) and treats statelessness and
multi-device/recovery continuity as non-requirements (see
[Non-requirements](#non-requirements)). The reasons are:

* Persisted, pre-signed transactions make best-effort background broadcast
  practical, and make temporal de-correlation of broadcast from synchronization
  and from application opens straightforward to implement.
* Statelessness was judged to make the desired temporal de-correlation harder, not
  easier, while the robustness it buys (restart and restore continuity) is not
  required for this flow.

The chain-recoverability property is not wasted: the canonical
migration-transaction predicate of
[Amount selection, canonical quantization](#amountselectioncanonicalquantization)
still lets a wallet reconstruct which denominations have confirmed, which is how
the reinstall/restore case is handled as a fresh migration. The full stateless
design is recorded as a rejected alternative (see
[Rejected alternatives](#rejectedalternatives)).

## Rationale for canonical amount selection

Privacy for value-transparent transfers comes from **value collision** (many
wallets emitting the same amount) and **ambiguity of grouping** (an observer
cannot tell which amounts belong together), not from unpredictability of the
amount. A high-entropy random amount collides with no other wallet and is a
near-unique fingerprint; a random partition into high-entropy pieces additionally
exposes the balance to subset-sum reconstruction. Canonical power-of-ten
denominations are therefore preferred precisely because they are *not* distinctive:
many wallets emit identical denominations, so no single transfer is identifiable by
its value, and a wallet MAY safely place several transfers in one cohort. The
detailed privacy argument is in
[Why value collision provides privacy](#whyvaluecollisionprovidesprivacy) and the
sections that follow it; the discarded random-amount strategies are listed in
[Rejected alternatives](#rejectedalternatives).

## Rationale for decoupling synchronization from broadcast

Linking synchronization and broadcast in the same background session would let an
observer correlate the two events and thereby link the broadcast to the wallet.
Keeping them separated in time preserves the de-correlation that the scheduling is
designed to provide. The principal place a synchronization is unavoidable is when
a migration transaction outputs change back to the *Orchard pool*, since spending
that change requires the wallet to witness it; this is handled by scheduling the
synchronization at a different time from the next broadcast.

## Rationale for anchor-height bucketing

Drawing anchors from shared, network-wide buckets means a transaction's anchor
reveals only which bucket the creator had reached, not the wallet's precise sync
height, and allows many users' transactions to share anchors. This mirrors the
goal of ZIP 308 [^zip-0308] (hiding individual migration transactions among those
of all migrating users), adapted to anchor selection in the light-client setting,
and complements the anchor-selection guidance of ZIP 315. [^zip-0315] The earlier
Path A notion of an "anchor-height bucket (~6 hours)" and the earlier
quantization-draft notion of a boundary at height $\equiv 0 \pmod{M}$ with a
shared previous-boundary anchor (~5.3 hours) are the same idea, unified here as a
single network-wide bucket/boundary scheme forming cohorts that mix wallets.

## Rationale for anchor selection

This subsection is non-normative.

A "sign ahead, broadcast later" workflow can leak information through anchor
selection: a transaction's anchor is fixed at signing time, and at broadcast time
the gap between the anchor's age and the broadcast height can reveal when the
transaction was prepared. Under the current transaction-digest rules [^zip-0244]
the anchor is committed by the signature hash, so the anchor cannot be changed
after signing without re-signing.

This specification avoids the leak by (a) building and signing parts at their
broadcast boundary (not far ahead), and (b) pinning the anchor to the previous
boundary, a value that is identical for every wallet sending at that boundary.
This makes anchor age constant and non-identifying.

**Forward-looking recommendation to the *Ironwood* pool designers.** Because
*Ironwood* is a new pool whose transaction format is still malleable, its
transaction-digest definition SHOULD be specified so that the anchor is **excluded
from the signature hash** and is instead only a public input to the proof. This
would allow the prover to choose the anchor *after* signing, enabling genuinely
flexible "sign now, prove/broadcast later" workflows, and thus the pre-signed
storage of [Pre-signed transaction storage](#pre-signedtransactionstorage),
without any anchor-staleness leak. Doing so for a new pool is essentially free;
retrofitting it onto Orchard/Sapling would be a consensus-level change to the
existing digest.

## Rejected alternatives

| Alternative | Reason rejected |
| --- | --- |
| Migrate the raw balance in one transfer | Publicly reveals exact balance; trivially linkable. |
| Random arbitrary amount per transfer | High-entropy amount is a near-unique fingerprint (crowd ≈ 1). |
| Random partition into high-entropy pieces | Pieces sum to the balance (subset-sum) and are self-fingerprinting. |
| 4-bucket whole-ZEC parts + sub-1-ZEC remainder | The rare remainder is a discriminator that makes co-location dangerous and is itself near-unique. Superseded by canonical-only quantization. |
| Randomized per-wallet multiplicity $k$ | Adds behavioral entropy (a fingerprint) without dispersing co-located parts; dominated by a deterministic, cohort-size-governed $k$. |
| Guided on-open sending ("Path B") | User-triggered sends coincide with app opens and light-wallet-server scan-range requests, letting an observer track the wallet across the whole migration; provides no temporal de-correlation. |
| Stateless, chain-recoverable migration (no persisted schedule) | Robust to restart and restore-from-seed, but statelessness is a non-requirement here, and persisted state makes temporal de-correlation and pre-signed background scheduling simpler. See [Rationale for the stateful design](#rationaleforthestatefuldesign). |
| Privacy/speed slider exposed to the user | The decision and the UI are too complex for typical users; the wallet picks sensible defaults instead. |


# Privacy Implications

The migration necessarily reveals information; the requirements in this ZIP are
intended to minimize it and to ensure the user consents to what remains. The
principal sources of leakage are:

* **Migrated amounts.** Each migration transaction reveals on-chain the value it
  moves from the *Orchard pool* to the *Ironwood pool*. [^zip-0209] Quantizing the
  balance into canonical denominations means no single transaction reveals the
  user's whole *Orchard-pool* balance, and each amount collides with those of many
  other wallets.

* **Linkage between a wallet's own transfers.** If multiple migration transactions
  could be grouped by a shared distinctive value, anchor, expiry, or broadcast
  time, an observer might cluster them as belonging to one wallet. Canonical
  amounts, the network-wide shared boundary anchor, and de-correlated broadcast
  times are intended to defeat this clustering.

* **Synchronization timing.** The anchor height of a transaction reveals the block
  height to which its creator had synchronized. Drawing anchors from shared,
  network-wide buckets prevents an observer from inferring when a specific wallet
  last synced. Triggering a wallet synchronization in the same background session
  as a broadcast would let an observer correlate the two; synchronization is
  therefore kept decoupled in time from broadcast.

* **Correlation with user behaviour.** If transfers are broadcast at the moment the
  user opens the application, an observer (in particular a light wallet server that
  also sees the user's scan-range requests) can monitor the wallet across the whole
  migration. De-correlating broadcasts from application opens is the primary
  privacy goal of the chosen approach.

* **Network-layer metadata.** Without network-level privacy, the server or network
  operator that receives a broadcast can correlate the broadcasting IP address with
  the on-chain pool-crossing event. This ZIP requires offering Tor as an opt-in and
  disclosing the residual IP-correlation risk.

* **Change back to the Orchard pool.** A migration transaction that produces change
  in the *Orchard pool* requires the wallet to synchronize before that change can
  be spent, creating a point where synchronization and migration interact and must
  be carefully separated in time.

The remaining subsections of this section are non-normative; they analyze the
privacy properties of the procedure specified above.

## Threat model

This subsection is non-normative.

The adversary observes all on-chain migration transactions: for each, the net
Orchard-out and Ironwood-in amounts and the block (hence time). The adversary does
**not** see addresses. The adversary's goal is **clustering**: partitioning the
global stream of migration transactions into per-wallet sets. Successful clustering
reconstructs a wallet's migration (and hence its balance and behavior) without any
address.

## Why value collision provides privacy

This subsection is non-normative.

Privacy for value-transparent transfers comes from **value collision** (many
wallets emitting the *same* amount) and **ambiguity of grouping** (an observer
cannot tell which amounts belong together), not from unpredictability of the
amount. Randomizing amounts is counterproductive: a high-entropy amount collides
with no other wallet and is a near-unique fingerprint.

Every part in this design is a canonical power-of-ten denomination drawn from a
small shared set (`100, 10, 1, 0.1, ...`). Many wallets emit identical
denominations, so no single part is distinctive by its value.

## On multiplicity and cohorts

This subsection is non-normative.

A wallet MAY place several parts into the same cohort. This does **not** let the
adversary attribute those parts to one wallet, because:

- **Canonical values are not self-identifying.** Several `100`-ZEC parts in a
  cohort cannot be attributed to one contributor versus several; the adversary
  cannot tell whether three co-located `100`s came from one wallet or three. The
  grouping is ambiguous *by construction*, and there is no rare value to anchor a
  reconstruction (the design has no high-entropy remainder).
- **Parts are not linked by inputs.** Each part is a separate transaction spending
  Orchard notes, which publish only unlinkable nullifiers; shielded inputs do not
  visibly link a wallet's transactions. The mandated absence of transparent
  components, the shared deterministic anchor, the canonical fee, and the uniform
  single-output structure mean nothing on-chain ties one wallet's co-located parts
  together.

This is precisely why multiplicity is safe **only** under canonical amounts.

What a cohort *does* reveal is only the **aggregate throughput** of the entire
migrating population at that boundary (the total of all parts), which is
population-level information, not any individual's magnitude.

## On subset-sum

This subsection is non-normative.

A worry with canonical decompositions is **targeted** subset-sum (find a subset
summing to a *known* target). This specification accepts the limited residual
exposure on the following grounds:

- Canonical values compose ambiguously: many unrelated parts sum to clean totals,
  so the constraint "this subset sums to a round number" is weak and yields
  exponentially many spurious solutions for an **untargeted** adversary (one
  without a known total).
- If an adversary already knows a wallet's total balance from off-chain data,
  learning that the wallet migrated that balance reveals no *new* information; the
  only further gain would be transaction-level linkage, which remains hard due to
  canonical collision, dispersion, and the lack of intra-cohort linkage.
- Therefore the dominant practical risk is **rarity** (below), which the
  `DENOM_CAP` bounds.

## Accepted residual leaks

This subsection is non-normative.

- **Rarity bounded by the cap.** No single part exceeds `DENOM_CAP` (100 ZEC), so
  no transfer is extremely large/rare. Larger denominations (e.g. 100 ZEC) are
  rarer than smaller ones, but every value is shared by many wallets in a large
  migrating population.
- **Aggregate cohort throughput.** A cohort reveals the population's total migrated
  value at that boundary (not individual magnitudes).
- **Number of signing sessions / total parts** for very large balances loosely
  indicates *bucketed* magnitude (a whale emits many parts), which is far weaker
  than a unique value.
- **Whale self-selection (deliberate).** Large holders who want fast, clean UX may
  choose to migrate in a single transfer instead of using this procedure. This is
  accepted: forcing whales into a long, manually-driven many-transaction process
  would harm adoption, and lower adoption shrinks the anonymity set for *everyone*.

## Whale handling

This subsection is non-normative.

The target session count (~6) is a goal for typical balances. For large balances:

- $k$ per cohort is bounded by `K_MAX` to limit the per-cohort count signal;
  consequently the number of cohorts/signing sessions grows with balance rather
  than $k$ growing without bound.
- This trades whale UX (more sessions) against the count-magnitude leak, keeping
  per-cohort multiplicity within a range that the (canonical, ambiguous) cohort can
  absorb.
- Whales remain weakly protected and may self-select to a single transfer, as
  above.

## A note on cohort size vs. per-wallet multiplicity

This subsection is non-normative.

Two different quantities should not be conflated:

- **Cohort size** (parts from *all* wallets at a boundary): larger is always better
  for privacy (bigger crowd). Coordinated boundaries exist to maximize it.
- **Per-wallet multiplicity $k$**: the number of a *single* wallet's parts in one
  cohort. Under canonical-only amounts, $k > 1$ is safe (parts are unattributable),
  but `K_MAX` keeps $k$ modest relative to expected cohort size so that per-wallet
  multiplicity stays well within the crowd.


# Deployment

This is a Wallet-category ZIP and does not itself introduce consensus rules. It
applies to wallets once the *Ironwood pool* is activated by its network upgrade
[^zip-0258] and the migration becomes relevant. The note-splitting phase MAY be
performed before that activation (see
[Phase 1, Note splitting](#phase1notesplitting)).


# Reference implementation

TODO: link to the SDK and wallet pull requests implementing this flow. Phase 2 is
intended to be implemented in a Rust backend exposed through a public SDK
interface, so that wallets can integrate against a stable interface (initially with
mocked data) and later switch to the production implementation.


# Open issues

The following points are open for the Zcash core team. Several are provisional
"magic numbers" that require ratification, analysis, and ideally simulation (cf.
ZIP 308, which left analogous parameters open):

* **Choice of `Category`**: provisionally `Wallet`; to be confirmed with the ZIP
  Editors (it may warrant `Standards` or a combined category).
* **Amount-selection / split heuristic**: canonical power-of-ten quantization is
  the recommended baseline; the exact decomposition, `DENOM_CAP`, `DUST_FLOOR`, and
  fee accounting (canonical fee per part) remain to be ratified.
* **Anchor bucket modulus $M$**: provisionally 256 blocks (≈ 5.3 hours, about a
  quarter day). Tightening $M$ by a factor $c$ speeds migration ~$c\times$ but
  divides the per-boundary cohort size by ~$c$ unless concurrent migrator volume
  rises by ~$c$. $M$ SHOULD be derived from a target anonymity-set floor based on
  expected *concurrent* migrator volume, not chosen arbitrarily.
* **Target signing sessions and `K_MAX`**: provisionally ~6 sessions; the
  per-cohort multiplicity bound `K_MAX` SHOULD be set relative to expected cohort
  size. The meaning of a "typical balance" also needs definition.
* **Canonical expiry delta and dedup/rebroadcast semantics**: to be specified.
* **Minimum synchronization before the first scheduled send**: define the minimum
  requirement for spending pre-upgrade *Orchard-pool* change, and how a wallet
  detects when a synchronization is needed.
* **Fallback de-correlation**: define behaviour for users whose background tasks
  never run, so broadcast remains de-correlated from synchronization.
* **Note-split maximum size**: whether a single note-split transaction can handle
  very large balances.
* **Reliability of the canonical migration-transaction predicate**: cf. ZIP 308's
  note that manually-created transactions might match a structural predicate.
* **Throughput simulation** at 75 s block spacing for representative balances (e.g.
  1, 10, 100, 1000, 10000 ZEC) under the chosen $M$, `DENOM_CAP`, target sessions,
  and `K_MAX`.
* **Interaction with the final *Ironwood* consensus-rule text**: in particular,
  that a cross-pool migration spend is not treated as a prohibited "payment to
  another user".

The following points are considered closed:

* **Multi-server (community light wallet server) submission**: broadcasting to a
  different server than the one used for synchronization is permitted but is not
  required.
* **Statelessness / multi-device recovery**: non-requirements for this flow; a
  stateful, persisted schedule is adopted (see
  [Rationale for the stateful design](#rationaleforthestatefuldesign)).


# References

[^BCP14]: [Information on BCP 14, "RFC 2119: Key words for use in RFCs to Indicate Requirement Levels" and "RFC 8174: Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words"](https://www.rfc-editor.org/info/bcp14)

[^protocol]: [Zcash Protocol Specification, Version 2025.6.3 [NU6.1] or later](protocol/protocol.pdf)

[^protocol-networks]: [Zcash Protocol Specification, Version 2025.6.3 [NU6.1]. Section 3.12: Mainnet and Testnet](protocol/protocol.pdf#networks)

[^zip-0200]: [ZIP 200: Network Upgrade Mechanism](zip-0200.rst)

[^zip-0203]: [ZIP 203: Transaction Expiry](zip-0203.rst)

[^zip-0209]: [ZIP 209: Prohibit Negative Shielded Chain Value Pool Balances](zip-0209.rst)

[^zip-0229]: [ZIP 229: Version 6 Transaction Format](zip-0229.md)

[^zip-0244]: [ZIP 244: Transaction Identifier Non-Malleability](zip-0244.rst)

[^zip-0258]: [ZIP 258: Deployment of the NU6.3 Network Upgrade](zip-0258.md)

[^zip-0308]: [ZIP 308: Sprout to Sapling Migration](zip-0308.rst)

[^zip-0315]: [ZIP 315: Best Practices for Wallet Implementations](zip-0315.rst)

[^zip-0317]: [ZIP 317: Proportional Transfer Fee Mechanism](zip-0317.rst)

[^zip-2005]: [ZIP 2005: Ironwood Quantum Recoverability](zip-2005.md)

[^zip-2006]: [ZIP 2006: Orchard Consensus Changes for NU6.3 (Ironwood)](zip-2006.md)

[^draft-zodl-valargroup-action-circuit-update]: [NU6.2 and NU6.3 updates to the Orchard Circuit (draft)](draft-zodl-valargroup-action-circuit-update.md)

[^tor]: [Tor Project](https://www.torproject.org/)
