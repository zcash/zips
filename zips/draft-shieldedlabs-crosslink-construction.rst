::

  ZIP: Unassigned {numbers are assigned by ZIP editors}
  Title: CCC-SL: Crosslink Consensus Construction from Shielded Labs
  Owners: Nate Wilcox <nate@shieldedlabs.com>
  Credits: Daira-Emma Hopwood
           Jack Grigg
           Kris Nuttycombe
  Status: Draft
  Category: Consensus
  Created: 2026-04-08
  License: MIT
  Discussions-To: TBD (no specific discussion thread yet)


Terminology
===========

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this
document are to be interpreted as described in BCP 14 [#BCP14]_ when, and only
when, they appear in all capitals.

The terms "Mainnet" and "Testnet" in this document are to be interpreted as
defined in the Zcash protocol specification [#protocol-networks]_.

The terms below are to be interpreted as follows:

CCC-SL (Crosslink Consensus Construction from Shielded Labs)
  The hybrid consensus construction specified by this ZIP, integrating the
  Zcash PoW best-chain protocol with ``CFP-SL`` to produce a protocol with
  both availability and Crosslink Finality. CCC-SL is the core of Shielded
  Labs Crosslink v1 and is closely based on CCC-TFLv2 from the TFL book
  [#tfl-book]_.

CCC-TFLv2 (Crosslink Consensus Construction from the TFL Book, version 2)
  The abstract hybrid consensus construction documented in the Zcash TFL book
  [#tfl-book]_. CCC-SL is the Shielded Labs adaptation and extension of this
  construction for the Zcash PoW+TFL deployment.

CFP-SL (Crosslink Finalization Protocol from Shielded Labs)
  The BFT Proof-of-Stake finalization protocol used as the BFT subprotocol
  within CCC-SL. CFP-SL satisfies the interface requirements (``Final
  Agreement`` and related properties) defined in this ZIP.

Best-chain subprotocol (Π\ :sub:`bc`)
  The Zcash Proof-of-Work best-chain protocol, modified by CCC-SL to
  participate in the hybrid construction. Blocks in this protocol are called
  "bc-blocks" and chains are "bc-chains".

Original best-chain subprotocol (Π\ :sub:`origbc`)
  The "off-the-shelf" PoW best-chain protocol before CCC-SL modifications.
  For the Zcash deployment, this corresponds to the Zcash NU5/NU6 consensus
  protocol.

BFT subprotocol (Π\ :sub:`bft`)
  The BFT protocol (instantiated by ``CFP-SL``) modified to participate in
  CCC-SL. Blocks in this protocol are called "bft-blocks" and finality is
  called "bft-finality".

Original BFT subprotocol (Π\ :sub:`origbft`)
  The "off-the-shelf" BFT protocol before CCC-SL adaptation modifications.
  CFP-SL is a specific instance of this with Zcash-specific adaptations.

bc-confirmation-depth (σ)
  A protocol parameter specifying the number of bc-block confirmations required
  before a bc-block may be included in the snapshot referenced by a bft-block.
  This is also the default depth used by nodes when computing the locally
  finalized chain.

Finalization gap bound (L)
  A protocol parameter specifying the maximum number of unfinalized bc-blocks
  permitted before CCC-SL enforces Stalled Mode. MUST satisfy ``L ≥ 2σ``.

Bounded-availability depth (μ)
  A per-node choice of confirmation depth for the locally bounded-available
  chain, where ``0 < μ ≤ σ``.

Locally finalized chain (``localfin``)
  Each node's monotonically advancing view of the bc-chain that has been
  finalized by ``CFP-SL``. Once a bc-block is in a node's locally finalized
  chain, it will never be removed from it.

Locally bounded-available chain (``localba``)
  Each node's view of the confirmed (but not necessarily finalized) bc-chain,
  computed using confirmation depth μ.

Finality gap
  At a given time, the number of bc-blocks in the bc-best-chain that have not
  yet been finalized by ``CFP-SL``.

Stalled Mode
  A mode enforced by CCC-SL when the finality gap exceeds ``L``, during which
  bc-block producers are constrained to produce only stalled blocks.

Stalled block
  A bc-block produced during Stalled Mode, constrained by the ``isStalledBlock``
  predicate (e.g., not including new user transactions that spend into the
  unfinalized zone).

Final Agreement
  The property of the BFT subprotocol (``CFP-SL``) that all bft-valid blocks
  in honest view are consistent: for any two such blocks, one must be an
  ancestor of the other.

Prefix Consistency
  The property of the best-chain subprotocol (Zcash PoW) that any two honest
  nodes' confirmed best-chains are consistent up to their confirmed depths.

Crosslink Finality
  The finality property provided by CCC-SL, as defined in the zebra-crosslink
  design documentation [#zebra-crosslink-terminology]_. Formally: for any two
  honest nodes ``i`` and ``j`` at any times ``t`` and ``u``, if both
  ``localfin_i(t)`` and ``localfin_j(u)`` are non-genesis then one is a
  prefix of the other (``localfin_i(t) ≼_bc localfin_j(u)`` or
  ``localfin_j(u) ≼_bc localfin_i(t)``). See the Security Analysis section.

``≼_bc`` (bc-prefix relation)
  ``A ≼_bc B`` holds iff the bc-chain with tip ``A`` is a prefix of the
  bc-chain with tip ``B``; equivalently, ``A`` is an ancestor of ``B`` or
  ``A = B``. The notation ``≼`` (without subscript) is used as a shorthand
  for ``≼_bc`` when the context is unambiguous.

``C.truncate_bc(k)``
  For a bc-chain ``C`` and natural number ``k``: the bc-chain obtained by
  removing the last ``k`` blocks from ``C``. The tip of ``C.truncate_bc(k)``
  is the block at depth ``k`` in ``C``. If ``len(C) ≤ k``, the result is the
  genesis block ``Origin_bc``. When applied to a block ``H`` (shorthand for
  the chain ending at ``H``), ``H.truncate_bc(k)`` denotes the block at
  depth ``k`` from ``H``.

``lastCommonAncestor(A, B)``
  For two bc-blocks ``A`` and ``B``: the most recent (deepest) bc-block that
  is an ancestor of both ``A`` and ``B``. Equivalently, the tip of the longest
  common prefix of the bc-chains ending at ``A`` and ``B``. If one block is an
  ancestor of the other, ``lastCommonAncestor(A, B) = min(A, B)`` by depth.

``bftLastFinal(B)``
  For a bft-block ``B``, the function returning the last bft-block that is
  considered final in the context of ``B`` (including ``B`` itself, if
  applicable). This function is defined by ``CFP-SL``.

``snapshot(B)``
  For a bft-block or bft-proposal ``B``, the bc-block at the base of the
  bc-chain snapshot committed to by ``B``. Formally: if ``B.headers_bc`` is
  null (genesis), ``snapshot(B) = Origin_bc``; otherwise
  ``snapshot(B) = B.headers_bc[0].truncate_bc(1)``.

``LF(H)``
  For a bc-block ``H``, the last final bft-block in the context of ``H``:
  ``LF(H) = bftLastFinal(H.context_bft)``.

``candidate(H)``
  For a bc-block ``H``, the candidate finalization point:
  ``candidate(H) = lastCommonAncestor(snapshot(LF(H)), H.truncate_bc(σ))``.


Abstract
========

This ZIP specifies **CCC-SL** (the Crosslink Consensus Construction from
Shielded Labs), the hybrid consensus protocol at the core of Shielded Labs
Crosslink v1 [#zip-crosslink-overview]_. CCC-SL integrates the Zcash
Proof-of-Work best-chain protocol with the ``CFP-SL`` BFT finalization
protocol to provide both the availability properties of the PoW chain and the
Crosslink Finality of a BFT protocol.

CCC-SL is closely based on the ``CCC-TFLv2`` construction from the Zcash TFL
book [#tfl-book]_. The key features of CCC-SL are:

1. Cross-referencing fields in both bc-blocks and bft-blocks/proposals that
   allow each chain to objectively verify properties of the other.

2. A locally finalized chain (``localfin``) maintained by each node that
   advances monotonically and never rolls back.

3. A locally bounded-available chain (``localba``) providing a
   confirmed-but-not-necessarily-finalized view of the PoW chain.

4. A Stalled Mode mechanism implementing bounded availability when the
   finality gap exceeds the threshold ``L``.

This ZIP is accompanied by ZIP [#zip-crosslink-overview]_, which provides the
design motivation and architecture overview for the full Shielded Labs
Crosslink v1 protocol suite.


Motivation
==========

See ZIP [#zip-crosslink-overview]_ for the full motivation. In brief:

* Zcash's current PoW-only consensus provides only probabilistic finality,
  creating friction for exchanges, bridges, and other services.

* Integrating ``CFP-SL`` as a finality layer via CCC-SL preserves PoW
  availability and security while adding Crosslink Finality.

* CCC-SL (following CCC-TFLv2) improves on the Snap-and-Chat construction
  [#ebb-and-flow]_ by eliminating the need for transaction-log sanitization
  and by implementing bounded availability.

* The cross-referencing design of CCC-SL enables each chain to provide
  objective validity checks on the other, strengthening the security of the
  hybrid construction.


Requirements
============

CCC-SL MUST satisfy:

* **Crosslink Finality**: If both subprotocols satisfy their safety assumptions,
  the locally finalized chain of any two honest nodes must be consistent —
  neither node's locally finalized chain can conflict with the other's.

* **Local Finalization Linearity**: For each honest node, the locally finalized
  chain is monotonically non-decreasing: it only ever advances forward, never
  rolls back.

* **Prefix Consistency** (inherited from Π\ :sub:`bc`): Two honest nodes'
  confirmed best-chains must be consistent.

* **Bounded Availability**: The finality depth of any non-stalled bc-block
  MUST NOT exceed ``L`` while honest bc-block producers follow the protocol.
  (Stalled blocks may exist at finality depth greater than ``L``; the bound
  applies to transaction-carrying blocks only.) When the finality depth at the
  chain tip exceeds ``L``, bc-block producers MUST enter Stalled Mode.

* **Objective Validity**: The validity of any bc-block MUST be determinable
  from the block itself and its ancestors in both chains, with no external
  context beyond the two chains.

* **Minimal Subprotocol Modification**: The modifications to the PoW and
  ``CFP-SL`` subprotocols SHOULD be as minimal as possible while satisfying
  the above requirements.


Non-requirements
================

The following are out of scope for this ZIP:

* The specific BFT algorithm used internally by ``CFP-SL``. This ZIP specifies
  only the interface requirements (Final Agreement, etc.) that
  Π\ :sub:`origbft` must satisfy. The CFP-SL specification is a separate ZIP.

* The staking mechanics, Finalizer registration, delegation, and slashing
  rules (specified in the RSM-SL-v1 ZIP).

* Reward distribution between PoW miners and Finalizers (a separate funding
  ZIP).

* The specific activation height(s) for the network upgrade.


Specification
=============

Parameters
----------

CCC-SL is parameterized by:

* **bc-confirmation-depth** ``σ ∈ ℕ⁺``: the number of bc-block headers
  included in each bft-block's ``headers_bc`` field, representing the depth
  at which a bc-block is considered confirmed for snapshotting purposes. This
  is also the default confirmation depth for the locally finalized chain.

* **Finalization gap bound** ``L ∈ ℕ⁺``, where ``L`` is significantly greater
  than ``σ`` (the minimum is ``L ≥ 2σ``): the maximum finality gap before
  Stalled Mode is enforced.

The precise values of ``σ`` and ``L`` for Mainnet and Testnet deployment are
to be determined through a network upgrade process ZIP, taking into account
measured CFP-SL latency and desired time-to-finality targets.

Subprotocol Interface Requirements
------------------------------------

CCC-SL places the following requirements on Π\ :sub:`origbft` (which is
instantiated as ``CFP-SL`` in Shielded Labs Crosslink v1):

* Π\ :sub:`origbft` MUST be a protocol with an identified set of blocks
  forming a DAG with a defined genesis block ``Origin_bft``.

* Π\ :sub:`origbft` MUST define a function
  ``bftValid(B) → Boolean`` determining whether a bft-block ``B`` is valid
  in the context of the bft-chain.

* Π\ :sub:`origbft` MUST define a function
  ``bftLastFinal(B) → BftBlock`` returning the last bft-block that is
  "final" in the context of bft-block ``B``, where ``bftLastFinal(Origin_bft)
  = Origin_bft``.

* Π\ :sub:`origbft` MUST satisfy **Final Agreement**: in any execution where
  safety assumptions hold, for all bft-valid blocks ``C`` in honest view and
  all times ``t``, ``bftLastFinal(C)`` must be an ancestor of every other
  bft-valid block that honest nodes have finalized.

CCC-SL places the following requirements on Π\ :sub:`origbc` (the Zcash PoW
protocol):

* Π\ :sub:`origbc` MUST be a best-chain protocol with bc-blocks forming a tree
  rooted at ``Origin_bc``.

* Π\ :sub:`origbc` MUST define a fork-choice function selecting the "best
  chain" among all bc-valid chains known to a node.

* Π\ :sub:`origbc` MUST satisfy **Prefix Consistency** (Common Prefix): in any
  execution where assumptions hold, for any two honest nodes' confirmed chains
  ``C1`` and ``C2``, one is a prefix of the other.

Structural Additions
--------------------

CCC-SL extends the block formats of both subprotocols with cross-referencing
fields:

bc-block structural additions
  Each bc-block header MUST include, in addition to all
  Π\ :sub:`origbc`-block fields:

  * ``context_bft``: a hash identifying a bft-block. This commits the
    bc-block producer to their view of the ``CFP-SL`` chain at the time the
    block was produced. The referenced bft-block MUST be a bft-valid block in
    the bc-block producer's view at the time of production.

bft-proposal structural additions
  Each non-genesis bft-proposal MUST include, in addition to all
  Π\ :sub:`origbft`-proposal fields:

  * ``headers_bc``: a sequence of exactly ``σ`` bc-block headers (zero-indexed,
    deepest first, i.e., ``headers_bc[0]`` is deepest and
    ``headers_bc[σ-1]`` is the most recent). These headers MUST form a valid
    chain in Π\ :sub:`bc` (each header's parent hash must match the previous
    header's hash). The genesis bft-block has ``headers_bc = null``.

bft-block structural additions
  Each non-genesis bft-block MUST include, in addition to all
  Π\ :sub:`origbft`-block fields:

  * ``headers_bc``: the same sequence of ``σ`` bc-block headers as in the
    corresponding bft-proposal. The genesis bft-block has ``headers_bc = null``.

Derived Functions
-----------------

Based on the structural additions above, define:

``snapshot(B)``
  For a bft-block or bft-proposal ``B``::

    snapshot(B) :=
      if B.headers_bc == null:
        Origin_bc
      else:
        B.headers_bc[0].truncate_bc(1)

  That is, the bc-block one step before the deepest header in the snapshot,
  i.e., the bc-block at depth ``σ+1`` relative to the tip of the snapshot
  chain. [#note-snapshot]_

``LF(H)``
  For a bc-block ``H``::

    LF(H) := bftLastFinal(H.context_bft)

``candidate(H)``
  For a bc-block ``H``::

    candidate(H) := lastCommonAncestor(snapshot(LF(H)), H.truncate_bc(σ))

  When ``H`` is the tip of a node's bc-best-chain, ``candidate(H)`` gives the
  candidate finalization point (subject to the local finalization update rule
  below). It represents the deepest bc-block that both (a) has been snapshotted
  by the last final bft-block in context, and (b) is at least ``σ`` deep in
  the bc-best-chain.

Locally Finalized Chain
-----------------------

Each node ``i`` maintains a locally finalized bc-chain ``localfin_i``,
initialized at ``Origin_bc``. The chain state MUST NOT be exposed to external
clients of the node until the node has synced (see `Syncing and Checkpoints`_).

When node ``i``'s bc-best-chain view is updated from ``ch_i(s)`` to
``ch_i(t)``::

  UpdateLocalFin(localfin_i, ch_i(t), s):
    let N = candidate(ch_i(t))
    if N is a descendant of localfin_i(s) (i.e., localfin_i(s) ≼ N):
      localfin_i(t) ← N
    else:
      localfin_i(t) ← localfin_i(s)
      if N conflicts with localfin_i(s) (i.e., neither is a prefix of the other):
        record a finalization safety hazard

A finalization safety hazard record SHOULD include ``ch_i(t)`` and the history
of ``localfin_i`` updates including and since the last update that was an
ancestor of ``N``.

**Lemma (Local Finalization Linearity)**: The time series of bc-blocks
``localfin_i(t)`` for any honest node ``i`` is bc-linear: for all times
``s ≤ t``, ``localfin_i(s) ≼_bc localfin_i(t)``.

*Proof*: By the update rule, ``localfin_i(t)`` is either ``localfin_i(s)`` or
a descendant of it, never a conflicting chain or an ancestor.

**Lemma (Local Fin-Depth)**: For any honest node ``i`` at time ``t``, there
exists a time ``r ≤ t`` such that
``localfin_i(t) ≼_bc ch_i(r).truncate_bc(σ)``.

*Proof*: By definition of ``candidate``, ``candidate(H) ≼ H.truncate_bc(σ)``
for all bc-blocks ``H``. Let ``r ≤ t`` be the last time ``localfin_i(t)``
changed, or genesis time ``0`` if it has never changed.

Locally Bounded-Available Chain
---------------------------------

Each node ``i`` chooses a bounded-availability depth ``μ`` where
``0 < μ ≤ σ``. The locally bounded-available chain is::

  localba(μ)_i(t) := ch_i(t).truncate_bc(μ)

.. warning::
   Choosing ``μ < σ`` is at the node's own risk and may increase susceptibility
   to rollback attacks. The default SHOULD be ``μ = σ``.

Syncing and Checkpoints
------------------------

When a node first syncs or re-syncs, the locally finalized chain state MUST
NOT be exposed to external clients until the node has processed the full bc-chain
and bft-chain up to a recent point. The node MAY use checkpoints embedded in
the software (committing to a known bc-block and bft-block at a given height)
to accelerate syncing.

Checkpoints MUST be chosen conservatively to avoid committing to blocks that
could be reorganized or that have not been finalized by ``CFP-SL``. A
checkpoint at bc-height ``h`` SHOULD only be used if ``CFP-SL`` has finalized
bc-blocks up to height ``h - σ`` or deeper.

Π\ :sub:`bft` (CFP-SL) Changes from Π\ :sub:`origbft`
--------------------------------------------------------

BFT block and proposal validity
  In addition to Π\ :sub:`origbft` validity rules, a bft-proposal ``P`` is
  bft-valid only if:

  1. ``P.headers_bc`` is a sequence of exactly ``σ`` bc-block headers forming
     a valid bc-chain (headers are correctly linked by parent hashes and each
     satisfies the bc-block header validity rules, including proof-of-work and
     difficulty adjustment).

  2. For each header ``h`` in ``P.headers_bc``, the proof-of-work MUST be
     valid (checking this requires only the headers, enabling DoS mitigation).

  3. ``P.headers_bc[σ-1]`` (the most recent header) MUST be at block height
     at least as great as the snapshot committed to in the bft-parent of
     ``P``, to prevent proposers from referencing stale bc-chain snapshots.

  4. The bc-chain committed to by ``P.headers_bc`` MUST be consistent with
     (i.e., a descendant of) the snapshot committed to in the bft-parent of
     ``P``.

BFT honest proposal rule (CFP-SL)
  An honest CFP-SL Finalizer proposing a bft-block at time ``t`` MUST set
  ``headers_bc`` to the sequence of the most recent ``σ`` bc-block headers
  in the node's bc-best-chain at time ``t``. The Finalizer MUST only propose
  if they have a bc-best-chain that is at least ``σ`` blocks deep.

BFT honest voting rule (CFP-SL)
  An honest CFP-SL Finalizer voting on a bft-proposal ``P`` MUST verify that
  ``P.headers_bc`` satisfies the proposal validity rules above. In particular,
  it MUST verify proof-of-work for all headers in ``P.headers_bc`` before
  accepting the proposal.

  If ``P.headers_bc`` connects to the Finalizer's known bc-chain, the
  Finalizer SHOULD download and fully validate any bc-blocks it has not yet
  seen before voting. If the headers do not connect to any known bc-chain, the
  Finalizer SHOULD assign lower priority to validating the proposal (to limit
  DoS exposure) and MAY drop it.

Π\ :sub:`bc` (Zcash PoW) Changes from Π\ :sub:`origbc`
---------------------------------------------------------

BC block validity (structural)
  In addition to Π\ :sub:`origbc` validity rules, a bc-block ``H`` is
  bc-valid only if:

  1. ``H.context_bft`` is a hash identifying a bft-valid block in
     Π\ :sub:`bft`.

  2. ``H.context_bft`` refers to a bft-block that is an ancestor of, or
     equal to, the bft-block referred to by ``H``'s bc-parent's
     ``context_bft`` field. (Context can only move forward in the bft-chain.)

BC contextual validity (finality gap)
  A bc-block ``H`` is contextually valid only if the finality gap constraint
  is satisfied. Let ``fin_height(H)`` be the bc-height of ``candidate(H)``
  and ``tip_height(H)`` be the bc-height of ``H``. The finality gap is
  ``tip_height(H) - fin_height(H)``.

  If the finality gap at ``H`` exceeds ``L``, then ``H`` MUST be a stalled
  block (i.e., ``isStalledBlock(H)`` MUST return ``true``).

BC honest block production
  An honest bc-block producer creating bc-block ``H`` at time ``t`` MUST:

  1. Set ``H.context_bft`` to the hash of the most recent bft-valid block
     in the producer's CFP-SL node view at time ``t``.

  2. Check the finality gap: if the finality gap would exceed ``L`` for the
     new block, the producer MUST apply the stalled-block policy.

  3. Not include ``H.context_bft`` referencing a bft-block whose
     ``headers_bc[σ-1]`` refers to a bc-block that is not a prefix of
     ``H``'s bc-ancestor chain (consistency check).

Stalled Mode Policy
--------------------

The stalled-block predicate ``isStalledBlock(H) → Boolean`` determines whether
a bc-block is a stalled block. The specific definition of ``isStalledBlock``
for the Zcash deployment is deferred to a subsequent consensus ZIP, but MUST
satisfy:

1. A stalled block MUST NOT include transactions that spend outputs created in
   bc-blocks that are not in the locally finalized chain (i.e., unfinalized
   outputs). This prevents users from having their funds locked in a deep
   unfinalized zone.

2. A stalled block MAY include coinbase transactions for miner rewards.

3. The validity of ``isStalledBlock(H)`` MUST be objectively determinable from
   ``H`` and its bc-ancestors (it requires no external state beyond the chain).

4. Nodes MUST enforce the stalled block policy: a non-stalled block with a
   finality gap exceeding ``L`` MUST be rejected as bc-invalid.

Open questions
''''''''''''''

* Should stalled blocks be permitted to include transactions spending finalized
  outputs only, or should they be entirely empty of user transactions? The
  tradeoff is between some throughput during a stall versus specification
  simplicity.

* What is the correct definition of "unfinalized outputs" in the context of
  Zcash shielded transactions, where output ownership is not publicly visible?

TODO: Define the specific encoding of ``context_bft`` in Zcash block headers,
including the exact byte representation of the bft-block hash reference.

TODO: Define the specific encoding of ``headers_bc`` in bft-proposals and
bft-blocks, including the exact byte layout.

TODO: Specify the precise values of ``σ`` and ``L`` for Mainnet and Testnet.

Security Analysis
-----------------

The following properties are claimed for CCC-SL under the stated assumptions.

Crosslink Finality
''''''''''''''''''

**Property**: If ``CFP-SL`` satisfies Final Agreement and the Zcash PoW
protocol satisfies Prefix Consistency, then for any two honest nodes ``i`` and
``j`` at any times ``t`` and ``u``, their locally finalized chains are
consistent: either ``localfin_i(t) ≼_bc localfin_j(u)`` or
``localfin_j(u) ≼_bc localfin_i(t)``.

*Proof sketch*: By the ``UpdateLocalFin`` rule, ``localfin_i(t)`` is always
equal to ``candidate(ch_i(r))`` for some time ``r ≤ t``. By the definition of
``candidate``, this is the last common ancestor of ``snapshot(LF(ch_i(r)))``
and ``ch_i(r).truncate_bc(σ)``.

By Final Agreement of ``CFP-SL``, ``LF(ch_i(r))`` and ``LF(ch_j(s))`` (for
any two honest nodes and times) must be consistent: one is an ancestor of the
other in the bft-chain. By the monotonic inclusion of snapshots in bft-ancestor
chains and Prefix Consistency of the PoW protocol, ``candidate(ch_i(r))`` and
``candidate(ch_j(s))`` are consistent bc-blocks. Since both
``localfin_i(t)`` and ``localfin_j(u)`` are derived from ``candidate`` values
of consistent finalization points and consistent bc-chains, they must be
consistent.

Bounded Availability
''''''''''''''''''''

**Property**: If all honest bc-block producers follow the stalled-block policy,
then every non-stalled bc-block accepted by honest full nodes has finality depth
at most ``L``. (Stalled blocks may have finality depth greater than ``L``; the
bound applies only to transaction-carrying, non-stalled blocks.)

*Proof sketch*: By the BC contextual validity rule, a bc-block whose finality
gap exceeds ``L`` that is not a stalled block is rejected as bc-invalid. Since
honest bc-block producers only produce stalled blocks when the gap would exceed
``L``, and honest full nodes reject non-stalled blocks with
``tip_height(H) - fin_height(H) > L``, all non-stalled blocks in any honest
full node's view of the bc-chain satisfy ``tip_height(H) - fin_height(H) ≤ L``.
Stalled blocks may accumulate arbitrarily, but they do not carry new
unfinalized-output-spending transactions, so the set of pending unfinalized
user transactions is bounded.

Resilience of Finality to PoW Reorgs
''''''''''''''''''''''''''''''''''''''

**Property**: A rollback of the bc-best-chain shorter than ``σ`` blocks does
not cause the locally finalized chain to roll back.

*Proof sketch*: The candidate finalization point ``candidate(H)`` for a chain
tip ``H`` is at depth ``σ`` or deeper in the bc-chain (by the Local Fin-Depth
lemma). A reorg of fewer than ``σ`` blocks cannot affect the bc-block at depth
``σ``. Furthermore, the ``UpdateLocalFin`` rule only advances the locally
finalized chain, never rolling it back.


Reference Implementation
========================

A prototype implementation of CCC-SL is being developed in the
``zebra-crosslink`` component of [#zebra-crosslink]_ and integrated in the
``crosslink_monolith`` repository [#crosslink-monolith]_. These implementations
are experimental and should not be used in production.

Reference documentation for CCC-SL's theoretical foundations is available in
the Zcash TFL design book [#tfl-book]_, specifically the "Crosslink 2
Construction" chapter (which corresponds to CCC-TFLv2, the basis for CCC-SL).


References
==========

.. [#BCP14] `Information on BCP 14 — "RFC 2119: Key words for use in RFCs to Indicate Requirement Levels" and "RFC 8174: Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words" <https://www.rfc-editor.org/info/bcp14>`_
.. [#protocol] `Zcash Protocol Specification, Version 2022.3.8 or later <protocol/protocol.pdf>`_
.. [#protocol-networks] `Zcash Protocol Specification, Version 2022.3.8. Section 3.12: Mainnet and Testnet <protocol/protocol.pdf#networks>`_
.. [#zip-0200] `ZIP 200: Network Upgrade Mechanism <zip-0200.rst>`_
.. [#zip-crosslink-overview] `ZIP [Unassigned]: Shielded Labs Crosslink v1: Protocol Overview and Architecture <draft-shieldedlabs-crosslink-overview.rst>`_
.. [#tfl-book] `Zcash Trailing Finality Layer Design Book — The Crosslink 2 Construction <https://electric-coin-company.github.io/tfl-book/design/crosslink/construction.html>`_
.. [#ebb-and-flow] `Ebb-and-Flow Protocols: A Resolution of the Availability-Finality Dilemma. David Neu, Joachim Neu, Ertem Nusret Tas, David Tse. <https://eprint.iacr.org/2020/1091.pdf>`_
.. [#zebra-crosslink] `ShieldedLabs zebra-crosslink repository <https://github.com/ShieldedLabs/zebra-crosslink>`_
.. [#crosslink-monolith] `ShieldedLabs crosslink_monolith repository <https://github.com/ShieldedLabs/crosslink_monolith>`_
.. [#zebra-crosslink-terminology] `Shielded Labs zebra-crosslink design book: Terminology <https://github.com/ShieldedLabs/zebra-crosslink/blob/main/book/src/design/terminology.md>`_

.. [#note-snapshot] The snapshot function returns the bc-block at depth 1 from the deepest header, i.e., the parent of ``headers_bc[0]``. This means the snapshot is a bc-block at depth ``σ+1`` relative to the tip of the snapshotted chain. This ensures that a bft-block referring to a snapshot provides evidence (via the ``σ`` headers) that the snapshot was confirmed at the time of the proposal.
