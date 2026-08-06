# Security review: draft P2P v2 protocol and Block Chain Synchronization ZIPs

Reviewed at commit `a8672747` (branch `agent/checkpointed-sync-zip`), covering the
two documents added by that branch:

- `zips/draft-arya-jvff-p2p-quic-transport.md` (v2 P2P protocol)
- `zips/draft-arya-block-chain-sync.md` (block chain synchronization)

Ten independent finder passes were run and each candidate finding was
adversarially cross-checked against the document text and against the consensus
ZIPs it depends on (ZIP 221, ZIP 244, ZIP 209). Numeric constants, anchor
rendering, and the `get-block-range` fork-substitution argument were checked and
produced no findings.

Fourteen findings survived verification. Line numbers are as of `a8672747`.

Status column: **fixed** means addressed in the follow-up commit on this branch.

| # | File | Line | Issue | Status |
|---|------|------|-------|--------|
| 1 | sync | 233 | Sapling-root check wrong for Heartwood..NU5 | fixed |
| 2 | sync | 234 | Boundary tree roots adopted unverified | fixed |
| 3 | sync | 349 | Backfill does not discharge snapshot trust | fixed |
| 4 | sync | 260 | Spentness-hint crypto unspecified | fixed |
| 5 | sync | 305 | Any-order verification drops per-block rules | fixed |
| 6 | p2p | 1251 | get-block-range does not bind v5 auth data | fixed |
| 7 | p2p | 1339 | Unbounded get-object offset underflows clamp | fixed |
| 8 | p2p | 1526 | Prefilled index bound wrong; count sum wraps | fixed |
| 9 | p2p | 990 | get-headers `ids_count` unbounded | fixed |
| 10 | p2p | 1065 | get-tx / get-blocks bound counts but not bytes | fixed |
| 11 | p2p | 1207 | `span_size` mismatch penalizes honest hint peer | fixed |
| 12 | p2p | 1039 | Bulk responses need not match the request | fixed |
| 13 | p2p | 438 | Tor preamble fields unbounded, parsed before limits | fixed |
| 14 | p2p | 1839 | addrv2 `time` is an unvalidated freshness signal | fixed |

---

## 1. Sapling-root verification is wrong for the Heartwood..NU5 span

**Where:** sync ZIP, "Verified Tree Roots" step 2; mirrored normatively in the
p2p ZIP's `get-tree-roots` section.

The text said to check the supplied Sapling root against the header's
`hashFinalSaplingRoot` "between Sapling and NU5". But ZIP 221 repurposes that
header field from **Heartwood** activation, not NU5: from Heartwood it carries
`hashChainHistoryRoot`, and from NU5 `hashBlockCommitments`. The direct check is
therefore wrong for every block in Heartwood..NU5 — roughly 784,000 mainnet
blocks (903,000 to 1,687,104).

**Impact.** A conforming verifier compares honest Sapling roots against the
chain-history root, always mismatches, and applies the 100-point instant ban to
every honest `NODE_TREE_ROOTS` server — mass-banning honest peers and narrowing
the node's peer set toward eclipse. An implementer who instead notices the check
is unsatisfiable and skips it adopts attacker-supplied roots; above the final
checkpoint under full validation, an attacker can then spend a self-minted note
against a forged Sapling anchor with a valid proof.

**Fix.** Split the procedure by what the header actually commits to: direct
`hashFinalSaplingRoot` check between Sapling and Heartwood, chain-history-tree
reconstruction from Heartwood onward.

## 2. Boundary tree-root entries are adopted with no working verification

**Where:** sync ZIP, "Verified Tree Roots" steps 2-3.

Four classes of entry passed every stated check while being verified by nothing:

- **Pre-activation entries.** The sync ZIP required "the empty tree root" (a
  nonzero constant) while the p2p ZIP mandates 32 zero bytes. An honest
  responder following the p2p ZIP is instant-banned by a verifier following the
  sync ZIP.
- **Ironwood roots.** The ZIP 221 leaf defines no Ironwood fields, so no header
  commits to them; there was no verification path at all, yet they were adopted.
- **The topmost entry of every response.** Verification "runs one block behind",
  so the highest entry of each ≤4,000-entry response is checked against nothing.
- **Out-of-order ranges**, for the same reason.

**Impact.** A peer returns 4,000 entries whose last entry (or any Ironwood root)
carries an attacker-chosen root that passes every stated check. Step 3 installs
it into the historical anchor index, enabling a later forged-anchor spend. The
document's claim that "every adopted root is authenticated by a header" was
false at these boundaries.

**Fix.** Align the pre-activation sentinel with the p2p ZIP (32 zero bytes);
state that a root no header commits to MUST NOT be adopted and is recomputed;
require that an entry is adopted only after its own check passes, and note
explicitly that the highest entry of a response stays unadopted until the
following block's entry verifies it.

## 3. Hint-verified backfill does not discharge snapshot trust

**Where:** sync ZIP, "Snapshot Synchronization" step 5 and the Security
Considerations paragraph that repeats the claim.

The claim was that when the backfill aggregates check out at `H`, the snapshot's
transparent UTXO set and nullifier sets have been *verified against the chain*,
discharging the only trusted components. Three gaps:

- The transparent aggregate hashed **outpoints only** — never amounts or
  scriptPubKeys, and never phantom UTXOs that were never created on-chain. Every
  real span output cancels, so a fabricated entry contributes no term and is
  never reconciled against the constructed set.
- The **Sprout note commitment tree** is verified by no described procedure.
- The **chain value pool balances** are verified by no described procedure.

**Impact.** A wrong-but-correctly-committed snapshot (buggy generator or
malicious mirror) containing a fabricated outpoint worth 21e6 ZEC, a fabricated
Sprout frontier, and inflated pool balances aggregates to exactly zero at `H`.
The node reports the snapshot verified, advertises `NODE_NETWORK`, spends the
unbacked coin, and accepts JoinSplits anchored to a Sprout root that never
existed — defeating the ZIP 209 turnstile permanently.

**Fix.** Make the reconciliation cover full UTXO entries rather than outpoints
(an aggregate over `outpoint ‖ value ‖ scriptPubKey ‖ height ‖ coinbase flag`,
constructible on both sides without lookups); require the Sprout tree to be
recomputed from the span's JoinSplit commitments and the value pool balances to
be recomputed and compared; and scope the discharge claim to exactly what those
checks cover.

## 4. Spentness-hint cryptographic parameters are unspecified

**Where:** sync ZIP, "Spentness Hints" introduction.

"Salted hash (`H(salt ‖ item)`), summed with wrapping addition" leaves the hash
function, output width, truncation, accumulator width, salt entropy, and domain
separation all unspecified — so the security-critical property that a wrong hint
causes *failure, not fraud* is not actually guaranteed.

**Impact.** "Wrapping addition" reads as a 32- or 64-bit machine accumulator,
giving ~2^-32 false-accept per attempt, and a nonzero aggregate only triggers a
silent retry rather than a ban, so trials are cheap. Worse, "salted hash" does
not require a PRF: an affine hash (keyed multiply-shift, polynomial) is linear
over Z_2^n, so cancellation relations hold for *every* salt and the salt-secrecy
argument provides zero protection — an artifact author can deterministically
forge a zero aggregate. Prefix-keying `H(salt ‖ item)` with SHA-256 is also
length-extendable, and one salt keyed all pool aggregates with no domain
separation.

**Fix.** Specify keyed BLAKE2b-256 with a 32-byte CSPRNG salt as the key,
per-aggregate personalization for domain separation, and 256-bit modular
addition for the accumulator.

## 5. Any-order verification silently drops per-block consensus rules

**Where:** sync ZIP, end of "Spentness Hints".

"Because no step reads state written by an earlier block, blocks and ranges MAY
be verified and committed in any order" is true of the aggregates but not of
every rule it was applied to.

**Impact.** ZIP 209 requires rejecting a block if any chain value pool balance
would become negative *at that block*; summing `valueBalance` fields in arbitrary
order and inspecting only the terminal total accepts a span whose running
Sprout/Sapling balance dips negative at an interior height and recovers by the
terminal height. Coinbase maturity and the pre-NU5 shielded-coinbase rule need
the spent output's creation height and coinbase flag, which the no-lookup rule
makes unavailable. And no overflow discipline is stated while the adjacent text
endorses wrapping arithmetic, so a reused idiom silently wraps an i64 pool
balance.

**Fix.** Scope the order-independence claim to the state construction and
aggregates; list the rules that remain height-ordered or are covered by the
trusted commitment below the final checkpoint; carry the per-output metadata the
maturity rules need in the hint artifact; and require checked (non-wrapping)
arithmetic for value sums, distinguishing them from the deliberately modular
aggregates.

## 6. get-block-range does not bind a v5 transaction's authorizing data

**Where:** p2p ZIP, `get-block-range` arrival checks.

The three MUST-checks are the hash chain plus "transactions match the header's
transaction merkle root". Per ZIP 244 the txid — and therefore the block merkle
root — commits prevouts, sequence, outputs and note data, but **not** scriptSigs
or shielded proofs and signatures, which live in the auth digest committed
separately via `hashBlockCommitments`. So the claim that a requester with a
trusted anchor "accepts no unverified bytes" is false for every NU5-onward block.

**Impact.** A malicious responder delivers the genuine header chain while
replacing every scriptSig with junk padded up to the 2 MiB element limit and
garbling all proofs and signatures. All three checks pass, and under checkpointed
sync abbreviated validation applies, so the node commits and stores non-canonical
blocks. It then serves them to full-validating peers (earning itself penalties),
cannot regenerate chunk artifacts or snapshot pieces byte-identically, and has
its own download inflated by orders of magnitude — with no rule violated by the
attacker.

**Fix.** Correct the overclaim; bound each delivered block by the consensus
maximum block size; require the authorizing-data commitment to be checked before
a block is stored, served, or used to regenerate artifacts; and add an
attributable misbehavior penalty for the failure.

## 7. Unbounded get-object offset underflows the natural length clamp

**Where:** p2p ZIP, `get-object` request format and response prose.

`offset` is a CompactSize with no stated maximum, and the "offsets at or beyond
the object's size are answered with no data" rule is declarative prose rather
than a MUST evaluated *before* computing `offset + length`.

**Impact.** A 41-byte request with `offset = 0xFFFFFFFFFFFFFFF0` and
`length = 33554432` defeats the obvious implementation
`end = min(offset + length, size); data = object[offset..end]`: the sum wraps to
33554416, `size` exceeds that, so `end < offset` and `end - offset` underflows to
~1.8e19 — a giant memcpy, i.e. an out-of-bounds read and heap disclosure in C++
or a slice-index panic in Rust, from one small request. The mirror hazard is a
responder that under-reports `size`, underflowing the requester's shortfall
computation `size - received` into an unbounded re-request loop.

**Fix.** Cap `offset`, make the ordering normative (`offset >= size` is
evaluated first and returns no data; otherwise exactly `min(length, size -
offset)` bytes), and require the requester to reject a `size` smaller than what
it has already received.

## 8. Compact-block prefilled indexes and count sum are mis-bounded

**Where:** p2p ZIP, "Compact Block Encoding".

Two distinct problems. Prefilled absolute indexes are bounded only by the
constant 65535, never by the block's actual transaction count — BIP 152 required
indexes to lie within the block, and that requirement was dropped. Separately,
`ids_count + prefilled_count` is a sum of two individually unbounded CompactSizes
that can wrap uint64 past the 65,536 FLOOD guard.

**Impact.** A compact block with `ids_count = 1`, `prefilled_count = 2` and
differential indexes `[0, 65534]` yields absolute index 65535 in a
three-transaction block. It is ≤ 65535, strictly increasing and non-overflowing,
so every check passes, and a reconstructor sized to the true transaction count
performs an out-of-bounds write at `txns[65535]`. Separately,
`ids_count = 0xFFFFFFFFFFFFFFFF` with `prefilled_count = 2` wraps the sum to 1,
bypassing the FLOOD check, so `Vec::with_capacity(ids_count)` aborts the process
— from a request costing the attacker a few bytes.

**Fix.** Bound each count individually before summing, and require every absolute
index to be strictly less than the total transaction count.

## 9. get-headers `ids_count` has no upper bound

**Where:** p2p ZIP, `get-headers` response entry format.

`ids_count` and its 64-byte-per-element `ids` array are the only count in the
protocol with no maximum. The 2 MiB element limit does not save it: that limit
applies to individually length-prefixed elements, and `ids` is a fixed-width
array.

**Impact.** A malicious responder answers a ~66-byte `tx_ids = 1` request with an
entry declaring `ids_count = 2^40`; a requester that preallocates from the
declared count attempts a 64 TiB allocation and is OOM-killed, and a streaming
requester has no specified stopping rule and no misbehavior attribution.
Conversely, an honest `tx_ids = 1` request aimed at large historical blocks
compels the responder to emit ~100 MB of transaction IDs (and compute
`auth_digest`s) from 66 bytes; only requester-side SHOULDs discouraged it, with
no responder-side byte bound.

**Fix.** Bound `ids_count` by the maximum transactions in a block, with FLOOD on
violation, and give the responder an explicit byte bound plus permission to
answer `has_txs = 0`.

## 10. get-tx and get-blocks bound item counts but not response bytes

**Where:** p2p ZIP, `get-tx` and `get-blocks`; and the Security Considerations
claim that per-request count limits bound resource consumption.

`get-tx` caps references at 50,000 and `get-blocks` caps hashes at 128, but
neither has a `max_bytes` — unlike `get-block-range` (64 MiB) and `get-object`
(32 MiB). The Security Considerations claim is therefore false wherever per-item
size is large.

**Impact.** An attacker learns mempool txids via `get-mempool`, then sends one
`get-tx` with 50,000 WTXID references — a 3.25 MB request compelling on the order
of 100 GB of serialized transactions. A 128-hash `get-blocks` similarly yields
~244 MiB of random block-store reads. Sustained over the 32 concurrent streams a
node SHOULD allow, that is roughly 30,000:1 bandwidth amplification and unbounded
disk-read amplification from one cheap connection. `SHORTID` retention compounds
it by forcing service of transactions no longer in the mempool.

**Fix.** Give the responder an explicit byte budget and permission to finish
early after any complete entry (mirroring `get-block-range`), with the requester
re-requesting the remainder; and correct the Security Considerations claim.

## 11. A `span_size` mismatch penalizes the honest hint peer

**Where:** p2p ZIP, `get-hashes` after-the-fact hint verification.

The 20-point penalty is justified by "the `hash` identifies the blocks uniquely,
so a mismatch is not attributable to a different chain view". That reasoning
holds for `span_txs` and `span_notes`, but **not** for `span_size`: a v5 block's
serialized size is not fixed by its hash, because scriptSig length is not
txid-committed (the same malleability as finding 6).

**Impact.** A victim fetches span hints from honest peer A and the corresponding
blocks from malicious peer B, which pads scriptSigs. The blocks hash correctly,
but their serialized size differs from A's honest `span_size`, so the penalty is
charged to **A**, not B. Five such spans reach the ban threshold: A is banned and
dropped from the address book. An attacker serving blocks can thus evict honest
hint-serving peers one by one, narrowing the victim toward eclipse while
committing no attributable misbehavior of its own.

**Fix.** Restrict the penalty to the genuinely hash-determined fields unless the
span's blocks have passed authorizing-data verification.

## 12. Nothing requires a bulk response to match the request

**Where:** p2p ZIP, `get-blocks`, `get-tx`, `get-object`, and the misbehavior
table.

Unlike `get-block-range`, which has explicit hash MUSTs, neither `get-blocks` nor
`get-tx` requires the delivered object to be the one requested, and no
misbehavior entry covers a mismatched or hash-failing bulk response. The sync
ZIP's claim that every verification failure is "detected, attributed, penalized,
and routed around" points at rules that do not exist.

**Impact.** A peer answers every `get-blocks` entry with a valid-but-unrequested
block (a stale sibling, letting it choose which competing block the victim
adopts), every `get-tx` with an unrelated transaction, and every `get-object`
piece with 32 MiB of garbage. Each response is syntactically conformant, so it is
not a `PROTOCOL_ERROR` and the misbehavior table has no matching row. The peer
keeps a zero score, is never deselected or banned, and can be reselected for the
same work forever — stalling synchronization indefinitely at near-zero cost while
remaining in good standing. This is asymmetric with the 100- and 20-point
penalties levied for `get-tree-roots` and `get-hashes`.

**Fix.** Require delivered blocks and transactions to match the corresponding
request entry (checkable by hashing, hence `PROTOCOL_ERROR`), and add a
misbehavior row for artifact data that fails its object hash.

## 13. Tor preamble fields are unbounded and parsed before every limit

**Where:** p2p ZIP, Tor transport "Connection Preamble".

The preamble's `network` string and its four flow-control fields are
CompactSize-prefixed with no maximum, and are parsed *before* any frame, record,
handshake, or size limit applies — so both the 2 MiB FLOOD rule and the
malformed-frame `PROTOCOL_ERROR` rule miss them entirely.

**Impact.** An attacker connects to a node's onion service and sends nine bytes —
`0xFF` followed by 2^64-1, a canonical CompactSize — as the `network` length,
then stalls. A node that reserves the declared length aborts on a 16 EB
allocation; one that reads incrementally holds a connection slot and buffer
indefinitely, because the handshake-completion timeout is scoped to the init
record on stream `0x00`, which the preamble precedes. Onion identities are free
to generate and explicitly acknowledged as unbannable. That `user_agent` is
capped at 256 bytes shows the omission is not deliberate; QUIC caps the
analogues of the four flow-control fields at 2^62-1.

**Fix.** Bound `network` to 16 bytes and the flow-control fields to 2^62-1, make
a violation an immediate close, and scope the handshake timeout to connection
establishment so it covers the preamble.

## 14. addrv2 `time` is an unvalidated freshness signal

**Where:** p2p ZIP, "Network Address Record" and "Address Book Management".

v2 makes the attacker-suppliable addrv2 `time` field the freshness signal that
address-book selection ranks on, but states no validation, clamping, or staleness
rule. The legacy protections — clamp to `now - 5 days` / `now + 10 minutes`, drop
entries older than 30 days — lived only in implementation code and were not
carried into the specification.

**Impact.** The careful Address Book Management rules govern source-group
bucketing and order of receipt, not the field an address manager actually ranks
on. An attacker relays its own addresses with `time` set far in the future; they
are never aged out as stale, always rank as the freshest entries in whatever
buckets they land in, and win outbound peer selection on every refresh —
reintroducing, from *inside* the buckets where bucketing gives no protection,
exactly the eclipse primitive [Heilman et al.] that the surrounding rules were
written to close.

**Fix.** Specify the clamping and staleness rules normatively and state that
`time` is unauthenticated and must not be the primary ranking key.

---

## Lower-severity items also noted

These were verified as real but ranked below the fourteen above.

- **Reorganization margin.** Only SHOULD on both sides, and the two documents
  disagree at depth exactly 100 (p2p synchronization rules vs. the `get-hashes`
  responder margin), letting near-tip commitment authority wedge a node on an
  orphaned branch. *(Wording aligned in the fix commit.)*
- **Snapshot frontier verification is vacuous** unless the trusted commitment
  reaches `H+1`, which nothing requires — `hashBlockCommitments` of the
  *following* block is what commits the chain history tree at `H`.
  *(Requirement added.)*
- **No required handshake timeout, inbound-connection bound, or
  application-level liveness check**, so a silent peer squats inbound slots while
  QUIC's stack-answered keepalive reports the link healthy.
- **`get-mempool` has no rate limit**; a re-open loop forces full mempool
  re-serialization per 1-byte request. It is also not gated by `relay`, and its
  live first-seen feed undoes trickling's topology protection.
- **Response `count` is never bounded to the requested count** for `get-hashes`
  and `get-tree-roots`.
- **The Tor framing layer omits QUIC's stream state machine** and stream-ID
  implicit-open semantics.
- **Artifact and spentness-hint byte layouts are unspecified** despite a
  "byte-identical regeneration" requirement.
- **Conventions:** duplicate "Example (non-normative)" headings produce colliding
  anchors *(fixed)*; absolute `zips.z.cash` URLs; missing Requirements section;
  `ZIP: XXX` placeholder.
