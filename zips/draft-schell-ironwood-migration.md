    ZIP: Unassigned
    Title: Orchard to Ironwood Migration
    Owners: Schell Carl Scivally <efsubenovex@gmail.com>
    Status: Draft
    Category: Wallet
    Created: 2026-06-16
    License: MIT
    Discussions-To: <https://github.com/zcash/zips/issues/???>


<div class="note"></div>

This document is a pre-proposal working draft produced for discussion with the
librustzcash / Zcash team. It is modeled on ZIP 308 (Sprout to Sapling
Migration) [^zip-0308] and adapts that precedent to an Orchard → Ironwood
migration. It is **not** a ratified ZIP. All numeric parameters are provisional
and require ratification (see [Open issues]).


# Terminology

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this
document are to be interpreted as described in BCP 14 [^BCP14] when, and only
when, they appear in all capitals.

The terms below are to be interpreted as follows:

Orchard pool

: The existing Orchard shielded pool.

Ironwood pool

: A new shielded pool using the Orchard protocol, introduced by the Ironwood
  network upgrade, subject to ongoing formal-verification and auditing efforts.

Migration transaction (or part)

: A single transaction that moves one canonical denomination of value from the
  Orchard pool into the Ironwood pool according to this specification.

Denomination

: A canonical power-of-ten amount (e.g. `100, 10, 1, 0.1, 0.01 ZEC`), bounded
  above by `DENOM_CAP` and below by `DUST_FLOOR`.

Boundary

: A block whose height is $\equiv 0 \pmod{M}$, where $M$ is the batch modulus
  (provisionally 256). Migration parts are broadcast at boundaries.

Cohort

: The set of all migration parts (from all wallets) broadcast at the same
  boundary.

Multiplicity ($k$)

: The number of parts a single wallet broadcasts into one cohort.


# Abstract

This proposal describes a privacy-preserving procedure for migrating funds from
the Orchard shielded pool into a new Ironwood shielded pool. Because consensus
rules require the *net* value crossing a pool boundary to be revealed publicly
(see [Why amounts leak]), a naive migration would expose each wallet's balance
and make migrations linkable. This proposal mitigates that leak by **quantizing**
the balance into canonical power-of-ten denominations so that migrated amounts
collide across wallets, and by broadcasting those denominations at coordinated
block-height boundaries so they mix with other users' parts.

This proposal also defines the procedure such that **no new persistent wallet
state is required**: a wallet's migration progress is fully recoverable from the
chain (using the wallet's viewing keys), and the set of denominations to send is
a deterministic function of the balance. This makes the migration robust to
restart and to restore-from-seed.


# Motivation

A soundness concern has motivated the creation of a new Ironwood pool (using the
Orchard protocol), introduced by the Ironwood network upgrade. Users will need
to migrate funds out of the old Orchard pool and into Ironwood. The
consensus-rule context for the upgrade is summarized in [Consensus context].

Cross-pool transfers are **value-transparent**: the net amount moved across a
pool boundary is a public, cleartext field of the transaction, even though
individual note values, senders, recipients, and memos remain hidden by
encryption and the zero-knowledge proof. Migrating a wallet's entire Orchard
balance in a single cross-pool transfer would therefore publicly reveal that
exact balance and make the migration trivially linkable to any off-chain
information about the wallet.

As with the Sprout → Sapling migration (ZIP 308) [^zip-0308], we wish to perform
the migration in a way that hides individual migration transactions among those
of all users migrating around the same time. The security analysis of migration
strategies is subtle, and the more obvious strategies leak significant
information. This document records the analysis behind the chosen strategy,
including several rejected alternatives (see [Rejected alternatives]).


# Consensus context

This section is non-normative. It summarizes the Ironwood network upgrade
consensus-rule context within which this migration procedure operates.

The relevant orgs and protocol developers have agreed on the consensus-rule
changes for Ironwood. This migration procedure operates within that context:

1. Ironwood introduces a new pool using the Orchard protocol, alongside the
   existing Orchard pool.
2. The Orchard circuit (shared by both pools) gains a flag, toggleable by
   consensus rules, that **disables payments to other users within the pool
   while still permitting change notes**. (This is a privacy/turnstile
   safeguard.)
3. After the upgrade, the **old Orchard pool has this flag enabled**, and
   **payments into the old pool are disabled** by constraining `valueBalance`.
4. Because payments are disabled on the old pool, wallets must send new payments
   to Orchard receivers (inside existing unified addresses) **via the new
   (Ironwood) pool**, and they **should migrate funds away from the old pool**.

Together these enforce a bound on the circulating supply of ZEC via the existing
turnstile mechanism (no one can transact with more ZEC than is supposed to
exist). Migrating funds both protects users from risk and gradually provides
evidence that no counterfeiting took place. Auditing and formal-verification
efforts for the circuit are ongoing.

Consequences for this procedure:

- This document covers **migrating funds out of the old Orchard pool into
  Ironwood**. The separate routing change in (4) - that *new payments* to
  Orchard receivers must go via Ironwood - is a general send-path concern and is
  **out of scope** here (the migration destination is, however, the same
  Ironwood receiver).
- Because the old pool can no longer carry ordinary payments, post-upgrade it
  contains little other than migration-shaped transactions. This reinforces the
  ZIP 308 stance that migration transactions need only be hidden **among
  themselves** (see [Non-requirements]).
- The consensus flag constrains the *structure* of permissible old-pool spends
  (spends + change, no arbitrary payments); the **canonical
  migration-transaction predicate** in this document SHOULD be aligned with the
  consensus-allowed spend shape rather than defined independently. The precise
  interaction (in particular, that a cross-pool migration spend is not itself
  treated as a prohibited "payment to another user") is a dependency on the
  final consensus-rule text.


# Why amounts leak

This section is non-normative.

In an Orchard-style bundle, each action publishes a value commitment (`cv_net`)
that is perfectly hiding, and the bundle as a whole publishes a single cleartext
signed integer `value_balance` equal to (spends − outputs) for that pool. A
binding signature cryptographically forces `value_balance` to equal the true net
of the hidden per-action commitments, so it cannot be falsified.

Consequently, a transaction that moves value **across** a pool boundary
(Orchard → Ironwood) publicly reveals:

- the net amount leaving Orchard (`value_balance` of the Orchard bundle), and
- the net amount entering Ironwood (`value_balance` of the Ironwood bundle),

both in cleartext, linked within the same transaction by the txid. The fee is
publicly computable as the sum of all pools' value balances. The zero-knowledge
proof does **not** and **cannot** hide this; hiding it would require a different
cross-pool construction.

Therefore the only privacy lever available to a wallet is the **shape of the
amounts** it chooses to migrate, and the **timing** with which it broadcasts
them.


# Requirements

- Migration is performed in the background, driven by ordinary wallet usage,
  without significant interference with concurrent usage.
- It is possible to enable or disable migration at any time.
- All Orchard funds at or above the dust floor will eventually be transferred to
  Ironwood, provided the wallet is used.
- The design SHOULD mitigate information leakage via timing information and
  transaction data, including:
  - linkage of particular migration transactions to one another (clustering);
  - information about the distribution of amounts of individual notes;
  - information about a wallet's total balance.
- The design SHOULD require **no new persistent scheduler state**: migration
  progress MUST be recoverable from the chain plus the wallet's key material, so
  that the procedure survives restart and restore-from-seed.
- The procedure SHOULD let a user complete migration with a small number of
  signatures for typical balances (good UX), since adoption drives the size of
  the anonymity set.
- Visibility SHOULD be provided to the user into the progress of the migration.
- The design SHOULD recover from failed/expired transactions.


# Non-requirements

- There is no requirement of network-layer anonymity (e.g. Tor); it MAY be used.
- The procedure does not have to provably leak no information.
- Migration transactions need only be hidden among themselves, not among all
  transactions.
- Individual note values need not be preserved (notes may be consolidated).
- A small amount (below the dust floor) MAY be left unmigrated if this helps
  privacy.
- **Large holders ("whales") are only weakly protected** and this is accepted;
  see [Privacy Implications].


# Specification

There are two main aspects to the strategy:

- the amount sent in each transaction (amount selection);
- how many transactions are sent, and when (the schedule).

## Amount selection: canonical quantization

A wallet's migratable Orchard balance is **quantized into canonical power-of-ten
denominations**, each bounded by `DENOM_CAP` above and `DUST_FLOOR` below:

- Permitted denominations are `DENOM_CAP, …, 1, 0.1, 0.01, …, DUST_FLOOR` ZEC,
  each an exact power of ten. `DENOM_CAP` is provisionally **100 ZEC**.
- The balance is decomposed by **decimal digit expansion** of the integer- and
  fractional-ZEC digits, except that no denomination exceeds `DENOM_CAP`: digits
  in the `≥ DENOM_CAP` place produce multiple `DENOM_CAP` parts. For example,
  with `DENOM_CAP = 100`:

  ```
  123.45  ZEC -> [100, 10, 10, 1, 1, 1, 0.1, 0.1, 0.1, 0.1, 0.01, 0.01, 0.01, 0.01, 0.01]
  540     ZEC -> [100, 100, 100, 100, 100, 10, 10, 10, 10]
  ```

- The quantization is a **pure, deterministic function of the balance** - there
  is no rare, high-entropy "remainder" output. Every emitted denomination is
  canonical and therefore collision-prone across wallets. (This is the key
  property; see [Privacy Implications].)
- Value below `DUST_FLOOR` is left unmigrated.
  TODO(schell): We should discuss this^

The fee for each part is in addition to its denomination (the visible
Orchard-out value of a part is its denomination plus the canonical fee;
equivalently the Ironwood output equals the denomination). The exact fee
accounting is an implementation detail constrained by the canonical-fee
requirement below.

Each migration transaction (part) MUST have:

- exactly one Ironwood output, whose value is a single canonical denomination;
- no transparent inputs or outputs;
- no spends from any pool other than Orchard;
- the canonical fee (provisionally the ZIP 317 minimum fee) [^zip-0317];
- the canonical anchor and expiry described in
  [The schedule: boundaries, cohorts, and multiplicity];
- `lock_time = 0`;
- the outgoing viewing key chosen as for a transfer sent from a transparent
  address;
- **no developer-fee output or any other extra output** (this would partition
  the anonymity set between wallets that add it and those that do not).

This strict, uniform structure is also the **canonical migration-transaction
predicate** used for chain-based recovery (see [State and recovery]).

## The schedule: boundaries, cohorts, and multiplicity

Migration parts are broadcast at **boundaries**: blocks whose height is
$\equiv 0 \pmod{M}$, with $M$ provisionally `256`. At the current target block
spacing of 75 seconds, a boundary occurs roughly every
$256 \times 75\,\text{s} \approx 5.3$ hours.

- Broadcast is **user-driven / opportunistic**: a wallet sends due parts when it
  is next active at or after a boundary. This produces organic dispersion of a
  wallet's parts over time (potentially days or weeks), which is a privacy
  feature.
- A wallet MAY broadcast **multiple parts into the same cohort** (multiplicity
  $k \geq 1$), because all denominations are canonical and therefore not
  attributable to a single wallet by their values (see
  [On multiplicity and cohorts]). This is a deliberate departure from a strict
  one-part-per-boundary rule and is what allows good UX (few signing sessions)
  without sacrificing per-cohort ambiguity.
- A wallet SHOULD choose $k$ to target a small total number of signing sessions
  for typical balances (provisionally a **target of ~6 signing sessions**):
  roughly $k \approx \lceil \text{number\_of\_denominations} / \text{target\_sessions} \rceil$.
- $k$ per cohort MUST be bounded by `K_MAX` (provisional). For balances large
  enough that the target session count would require $k > $ `K_MAX`, the number
  of signing sessions grows instead (the target is a goal for typical wallets,
  not a hard cap); see [Whale handling].
- Each migration part MUST specify, as its Orchard anchor, the tree state as of
  the **previous boundary** (the most recent block height $\equiv 0 \pmod{M}$
  strictly before the part is built). This anchor is deterministic and shared
  across all wallets sending at the same boundary, so the anchor's age carries
  no per-wallet timing information.
- Each migration part MUST use the canonical expiry delta (provisional; chosen
  so the part expires at a deterministic future boundary).

<details>
<summary>

### Rationale for anchor selection
</summary>

TODO(schell): This section is now out of date, since we've planned to move
the anchor to auth data.

A "sign ahead, broadcast later" workflow can leak information through anchor
selection: a transaction's anchor is fixed at signing time, and at broadcast
time the gap between the anchor's age and the broadcast height can reveal when
the transaction was prepared. Under the current transaction-digest rules
[^zip-0244] the anchor is committed by the signature hash, so the anchor cannot
be changed after signing without re-signing.

This specification avoids the leak by (a) building and signing parts **at their
broadcast boundary** (not far ahead), and (b) pinning the anchor to the
**previous boundary**, a value that is identical for every wallet sending at
that boundary. This makes anchor age constant and non-identifying.

**Forward-looking recommendation to the Ironwood pool designers.** Because
Ironwood is a new pool whose transaction format is still malleable, its
transaction-digest definition SHOULD be specified so that the anchor is
**excluded from the signature hash** and is instead only a public input to the
proof. This would allow the prover to choose the anchor *after* signing,
enabling genuinely flexible "sign now, prove/broadcast later" workflows without
any anchor-staleness leak. Doing so for a new pool is essentially free;
retrofitting it onto Orchard/Sapling would be a consensus-level change to the
existing digest.
</details>
<br/>

## State and recovery

This procedure requires **no new persistent scheduler state**. All migration
state is one of:

1. **Chain-recoverable** using the wallet's viewing keys, via the canonical
   migration-transaction predicate; or
2. **A pure, deterministic function of the balance** (the quantization).

### Chain-recoverable state

Using its viewing keys, a wallet can enumerate its own transactions and identify
migration transactions by the strict canonical predicate above. From the
identified migration transactions it can recover, without any stored state:

- which denominations have been broadcast and their confirmation status (by
  decrypting its own Ironwood outputs for their values);
- the value already migrated;
- the remaining migratable Orchard balance.

### Deterministic quantization

The set of denominations still to send is simply the quantization of the
**remaining** migratable balance, recomputed from chain state. Because
quantization is a pure function of the balance (no PRF, no stored partition, no
rare remainder), it recomputes identically on every wallet activation and after
restore-from-seed.

### Rebalancing and termination

Funds that arrive in (or are spent from) the Orchard pool simply change the
remaining balance, and the next recomputed quantization reflects them. To avoid
recomputing a *changing* decomposition mid-cohort in a way that could send
inconsistent amounts, a wallet SHOULD compute the denominations due for a given
cohort from the balance **as of that cohort's boundary** (notes confirmed at or
before the boundary height), and treat funds that arrive later as belonging to a
subsequent boundary.

Migration **terminates** only when the migratable Orchard balance is below
`DUST_FLOOR` **at a boundary**, ensuring that funds arriving late trigger
additional parts rather than being stranded.

### Deduplication and expiry

Because no txids are persisted, a wallet that becomes active after broadcasting
parts (but before they are mined) MUST avoid double-sending. Before
broadcasting, the wallet MUST:

- recompute the quantization of the remaining balance and identify
  already-confirmed parts (predicate + decrypted values);
- determine the set of denominations not yet sent;

A part not mined by its expiry MUST be rebuilt at a subsequent boundary with the
then-current previous-boundary anchor and a fresh expiry; its **denomination is
unchanged**, only the anchor/expiry refresh.


# Privacy Implications

This section analyzes the privacy properties of the procedure specified above.

## Threat model

The adversary observes all on-chain migration transactions: for each, the net
Orchard-out and Ironwood-in amounts and the block (hence time). The adversary
does **not** see addresses. The adversary's goal is **clustering**: partitioning
the global stream of migration transactions into per-wallet sets. Successful
clustering reconstructs a wallet's migration (and hence its balance and
behavior) without any address.

## Why collision provides privacy

Privacy for value-transparent transfers comes from **value collision** (many
wallets emitting the *same* amount) and **ambiguity of grouping** (an observer
cannot tell which amounts belong together), not from unpredictability of the
amount. Randomizing amounts is counterproductive: a high-entropy amount collides
with no other wallet and is a near-unique fingerprint.

Every part in this design is a canonical power-of-ten denomination drawn from a
small shared set (`100, 10, 1, 0.1, ...`). Many wallets emit identical
denominations, so no single part is distinctive by its value.

## On multiplicity and cohorts

A wallet MAY place several parts into the same cohort. This does **not** let the
adversary attribute those parts to one wallet, because:

- **Canonical values are not self-identifying.** Several `100`-ZEC parts in a
  cohort cannot be attributed to one contributor versus several; the adversary
  cannot tell whether three co-located `100`s came from one wallet or three. The
  grouping is ambiguous *by construction*, and there is no rare value to anchor a
  reconstruction (the design has no high-entropy remainder).
- **Parts are not linked by inputs.** Each part is a separate transaction
  spending Orchard notes, which publish only unlinkable nullifiers; shielded
  inputs do not visibly link a wallet's transactions. The mandated absence of
  transparent components, the shared deterministic anchor, the canonical fee, and
  the uniform single-output structure mean nothing on-chain ties one wallet's
  co-located parts together.

This is precisely why multiplicity is safe **only** under canonical amounts.

What a cohort *does* reveal is only the **aggregate throughput** of the entire
migrating population at that boundary (the total of all parts), which is
population-level information, not any individual's magnitude.

## On subset-sum

A worry with canonical decompositions is **targeted** subset-sum (find a subset
summing to a *known* target). This specification accepts the limited residual
exposure on the following grounds:

- Canonical values compose ambiguously: many unrelated parts sum to clean
  totals, so the constraint "this subset sums to a round number" is weak and
  yields exponentially many spurious solutions for an **untargeted** adversary
  (one without a known total).
- If an adversary already knows a wallet's total balance from off-chain data,
  learning that the wallet migrated that balance reveals no *new* information;
  the only further gain would be transaction-level linkage, which remains hard
  due to canonical collision, dispersion, and the lack of intra-cohort linkage.
- Therefore the dominant practical risk is **rarity** (below), which the
  `DENOM_CAP` bounds.

## Accepted residual leaks

- **Rarity bounded by the cap.** No single part exceeds `DENOM_CAP` (100 ZEC),
  so no transfer is extremely large/rare. Larger denominations (e.g. 100 ZEC)
  are rarer than smaller ones, but every value is shared by many wallets in a
  large migrating population.
- **Aggregate cohort throughput.** A cohort reveals the population's total
  migrated value at that boundary (not individual magnitudes).
- **Number of signing sessions / total parts** for very large balances loosely
  indicates *bucketed* magnitude (a whale emits many parts), which is far weaker
  than a unique value.
- **Whale self-selection (deliberate).** Large holders who want fast, clean UX
  may choose to migrate in a single transfer instead of using this procedure.
  This is accepted: forcing whales into a long, manually-driven
  many-transaction process would harm adoption, and lower adoption shrinks the
  anonymity set for *everyone*.

## Whale handling

The target session count (~6) is a goal for typical balances. For large
balances:

- $k$ per cohort is bounded by `K_MAX` to limit the per-cohort count signal;
  consequently the number of cohorts/signing sessions grows with balance rather
  than $k$ growing without bound.
- This trades whale UX (more sessions) against the count-magnitude leak, keeping
  per-cohort multiplicity within a range that the (canonical, ambiguous) cohort
  can absorb.
- Whales remain weakly protected and may self-select to a single transfer, as
  above.

## A note on cohort size vs. per-wallet multiplicity

Two different quantities should not be conflated:

- **Cohort size** (parts from *all* wallets at a boundary): larger is always
  better for privacy (bigger crowd). Coordinated boundaries exist to maximize
  it.
- **Per-wallet multiplicity $k$**: the number of a *single* wallet's parts in
  one cohort. Under canonical-only amounts, $k > 1$ is safe (parts are
  unattributable), but `K_MAX` keeps $k$ modest relative to expected cohort size
  so that per-wallet multiplicity stays well within the crowd.


# Rationale

## Rejected alternatives

| Alternative | Reason rejected |
| --- | --- |
| Migrate the raw balance in one transfer | Publicly reveals exact balance; trivially linkable. |
| Random arbitrary amount per transfer | High-entropy amount is a near-unique fingerprint (crowd ≈ 1). |
| Random partition into high-entropy pieces | Pieces sum to the balance (subset-sum) and are self-fingerprinting. |
| 4-bucket whole-ZEC parts + sub-1-ZEC remainder | The rare remainder is a discriminator that makes co-location dangerous and is itself near-unique. Superseded by canonical-only quantization. |
| Randomized per-wallet multiplicity $k$ | Adds behavioral entropy (a fingerprint) without dispersing co-located parts; dominated by a deterministic, cohort-size-governed $k$. |
| Pre-signing all parts up front | Freezes anchors early, reintroducing the anchor-staleness leak. |
| Persisted migration-plan table | Unnecessary: state is chain-recoverable + a pure function of the balance. |


# Open issues

All of the following are provisional "magic numbers" / design points requiring
ratification, analysis, and ideally simulation (cf. ZIP 308, which left
analogous parameters open):

- The choice of `Category` (provisionally `Wallet`) should be confirmed with the
  ZIP Editors; it may warrant `Standards` or a combined category.
- The batch modulus $M$ (provisionally 256). Tightening $M$ by a factor $c$
  speeds migration ~$c\times$ but divides the per-boundary cohort size by ~$c$
  **unless concurrent migrator volume rises by ~$c$**. $M$ SHOULD be derived
  from a target anonymity-set floor based on expected *concurrent* migrator
  volume, not chosen arbitrarily.
- `DENOM_CAP` (provisionally 100 ZEC) - trades whale UX/adoption against
  per-value rarity.
- `DUST_FLOOR` and the exact fee accounting (canonical fee per part).
- The target number of signing sessions (provisionally ~6) and `K_MAX` (the
  per-cohort multiplicity bound), which SHOULD be set relative to expected
  cohort size.
- The canonical expiry delta and the precise dedup/rebroadcast semantics.
- Reliability of the canonical migration-transaction predicate (cf. ZIP 308's
  note that manually-created transactions might match a structural predicate).
- Throughput simulation at 75 s block spacing for representative balances (e.g.
  1, 10, 100, 1000, 10000 ZEC) under the chosen $M$, `DENOM_CAP`, target
  sessions, and `K_MAX`.
- The interaction with the final Ironwood consensus-rule text, in particular
  that a cross-pool migration spend is not treated as a prohibited "payment to
  another user".


# References

[^BCP14]: [Information on BCP 14 - "RFC 2119: Key words for use in RFCs to Indicate Requirement Levels" and "RFC 8174: Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words"](https://www.rfc-editor.org/info/bcp14)

[^zip-0244]: [ZIP 244: Transaction Identifier Non-Malleability](zip-0244.rst)

[^zip-0308]: [ZIP 308: Sprout to Sapling Migration](zip-0308.rst)

[^zip-0317]: [ZIP 317: Proportional Transfer Fee Mechanism](zip-0317.rst)
