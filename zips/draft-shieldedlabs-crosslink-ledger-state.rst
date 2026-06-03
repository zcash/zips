::

  ZIP: Unassigned {numbers are assigned by ZIP editors}
  Title: RSM-SL-v1: Crosslink Ledger State and Ledger Mutations
  Owners: Nate Wilcox <nate@shieldedlabs.com>
  Credits: Daira-Emma Hopwood
           Jack Grigg
           Kris Nuttycombe
  Status: Draft
  Category: Consensus
  Created: 2026-06-03
  License: MIT
  Discussions-To: TBD (no specific discussion thread yet)


Terminology
===========

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this
text are to be interpreted as described in BCP 14 [#BCP14]_ when, and only
when, they appear in all capitals.

The terms "Mainnet" and "Testnet" in this document are to be interpreted as
defined in the Zcash protocol specification [#protocol-networks]_.

The terms below are to be interpreted as follows:

RSM-SL-v1
  The Shielded Labs v1 instantiation of the roster state module referenced by
  the Crosslink Overview ZIP [#zip-crosslink-overview]_.

Idealized ledger state
  A point-in-time abstract data structure used for specification and consensus
  reasoning. Implementations MAY use equivalent internal layouts, but MUST
  produce exactly the same externally verifiable state transitions as if they
  had updated this idealized structure directly.

Bond
  A delegated ZEC amount associated with a Finalizer identifier and tracked by
  this specification's ledger state rules.

Candidate Roster
  A deterministic mapping from Finalizer identifiers to voting weights,
  computed by summing all currently effective bonds for each Finalizer.

Active Finalizer set
  The top ``K`` Finalizers by voting weight in the Candidate Roster, where
  ``K = 100``.

Most-recent-final ancestor
  For any PoW tip block, the unique most recent ancestor on that tip's chain
  that is finalized under CCC-SL [#zip-ccc-sl]_.


Abstract
========

This ZIP specifies the Crosslink ledger-state changes required by RSM-SL-v1.
It defines the idealized point-in-time ledger state extension, and the ledger
mutation rules that update this state, including issuance distribution and
roster mutations.

The specification is layered:

* abstract Proof-of-Stake actions over ledger state, and
* concrete consensus extensions to Zcash transaction fields and semantics.


Motivation
==========

The Crosslink Overview ZIP defines RSM-SL-v1 conceptually but leaves the
consensus state and mutation details to a companion specification. Nodes need a
single, deterministic definition of:

* how Finalizer voting weights are derived from on-chain bonds,
* how the active BFT roster is selected, and
* how roster-related state evolves as blocks are applied and reverted.

Without this ZIP, implementations may diverge on ledger state interpretation,
producing incompatible active rosters and finality inputs.


Requirements
============

This ZIP MUST specify the following:

* An idealized ledger state extension over the existing Zcash ledger state,
  including bonds, Finalizer identifiers, and cryptographic material needed for
  self-authenticating roster membership.
* Candidate Roster construction by summing currently effective bonds per
  Finalizer, and Active Finalizer set selection as the top ``K = 100`` by
  voting weight.
* Dual-state interpretation in which ledger processing distinguishes finalized
  state from tip state, with each tip having an objectively verifiable
  most-recent-final ancestor.
* Ledger mutation rules for issuance distribution and roster mutations.
* A two-layer mutation definition:

  1. abstract PoS actions, and
  2. concrete Zcash transaction-field and transaction-semantic extensions.


Non-requirements
================

The following are out of scope for this ZIP:

* Pre-existing Zcash ledger state, except where it is extended or requires new
  considerations due to Crosslink.
* The Crosslink mechanism itself (including chain selection and finality-status
  verification), specified in CCC-SL [#zip-ccc-sl]_.
* Internal BFT protocol design, except that the Active Finalizer set is an
  input provided by this ZIP.
* Networking behavior outside transaction format and transaction semantics.
* Topics designated as separate ZIPs in the Crosslink overview
  [#zip-crosslink-overview]_.


Specification
=============

Idealized Ledger State Extension
--------------------------------

Let ``S_zec`` denote the existing Zcash ledger state. This ZIP defines an
extended idealized state ``S_xl`` that behaves as:

* ``S_xl = (S_zec, S_roster, S_finality_views, S_issuance)``.
* ``S_roster`` includes at minimum:

  * bond records keyed by bond identifier,
  * Finalizer identity records,
  * cryptographic verification keys and status metadata,
  * deterministic activation/deactivation metadata needed for roster
    computation.

* ``S_finality_views`` tracks finalized and tip-relative views so that, for each
  accepted tip, the corresponding most-recent-final ancestor is objectively
  derivable from block data and finalized commitments.
* ``S_issuance`` tracks distribution state required to apply issuance rules that
  involve Finalizers.

Consensus behavior MUST be equivalent to transitions over ``S_xl`` even when an
implementation does not materialize ``S_xl`` as one in-memory object.

Candidate Roster and Active Finalizers
--------------------------------------

For each state ``S_xl`` at a given chain point:

* Candidate voting weight for Finalizer ``f`` is the sum of all currently
  effective bond amounts targeting ``f``.
* Candidate Roster computation MUST be deterministic for every honest node given
  the same chain history.
* The Active Finalizer set is the top ``K = 100`` Finalizers by candidate voting
  weight.
* Tie-breaking for equal weights MUST be deterministic and based only on
  consensus-visible data.
* The active roster output MUST be suitable as an input to CFP-SL voting-weight
  selection.

Finalized and Tip State Relationship
------------------------------------

Ledger processing MUST expose both:

* a finalized state view anchored at finalized history, and
* a tip state view for each accepted PoW tip.

For every accepted tip, nodes MUST be able to derive an objectively verifiable
most-recent-final ancestor from consensus data. Reorganizations MUST preserve
this invariant and recompute dependent tip state deterministically.

Ledger Mutations: Abstract Action Layer
---------------------------------------

This ZIP defines abstract actions that mutate ``S_xl``:

* ``BondCreate``: create a bond linking stake to a Finalizer identifier.
* ``BondAdjust``: increase or decrease an existing bond according to consensus
  constraints.
* ``BondDeactivate``: transition stake out of active weighting, including
  unbonding behavior.
* ``FinalizerRegister`` and ``FinalizerUpdate``: manage Finalizer identity and
  associated cryptographic keys.
* ``FinalizerDeactivate``: remove a Finalizer from future roster eligibility.
* ``Slash``: apply deterministic penalties for provable misbehavior.
* ``DistributeIssuance``: apply issuance distribution updates affecting miner
  and Finalizer-related allocation state.

Each action MUST define preconditions, state transition effects, and reversion
behavior under chain rollback.

Ledger Mutations: Concrete Zcash Transaction Semantics
------------------------------------------------------

Consensus transaction rules are extended so that specific transaction patterns
encode the abstract actions above. This layer MUST define:

* the concrete transaction fields and encodings used for roster-related actions,
* validity checks for signatures, authorization, and amount constraints,
* ordering and interaction rules when multiple roster actions appear in one
  block,
* rejection behavior for malformed, unauthorized, or semantically conflicting
  actions.

Applying a valid block MUST induce exactly the same abstract action sequence on
``S_xl`` at all honest nodes.

Issuance Distribution and Roster Interaction
--------------------------------------------

Issuance distribution rules covered by this ZIP MUST specify:

* which issuance components are affected by roster/finalizer state,
* when issuance state updates occur relative to other per-block mutations, and
* deterministic accounting behavior under normal progression and reorgs.

Detailed policy values (for example, exact allocation percentages) MAY be set by
separate process or funding ZIPs, but this ZIP defines the consensus state
transition hooks that enforce whichever policy is activated.


Rationale
=========

Separating this specification from CCC-SL keeps concerns modular:

* CCC-SL specifies the hybrid-consensus construction and finality properties.
* This ZIP specifies the ledger-state machine that supplies active roster input
  and applies roster-related mutations inside Zcash consensus processing.

This split keeps each ZIP auditable while preserving deterministic integration.


Deployment
==========

This ZIP is intended to activate through the Zcash network-upgrade mechanism
[#zip-0200]_ alongside the other required Crosslink ZIPs.


Reference Implementation
========================

A prototype implementation is under development in the Shielded Labs
``zebra-crosslink`` and ``crosslink_monolith`` repositories, referenced from
ZIP [#zip-crosslink-overview]_.


References
==========

.. [#BCP14] `Information on BCP 14 — "RFC 2119: Key words for use in RFCs to Indicate Requirement Levels" and "RFC 8174: Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words" <https://www.rfc-editor.org/info/bcp14>`_
.. [#protocol] `Zcash Protocol Specification, Version 2022.3.8 or later <protocol/protocol.pdf>`_
.. [#protocol-networks] `Zcash Protocol Specification, Version 2022.3.8. Section 3.12: Mainnet and Testnet <protocol/protocol.pdf#networks>`_
.. [#zip-0200] `ZIP 200: Network Upgrade Mechanism <zip-0200.rst>`_
.. [#zip-ccc-sl] `ZIP [Unassigned]: CCC-SL: Crosslink Consensus Construction from Shielded Labs <draft-shieldedlabs-crosslink-construction.rst>`_
.. [#zip-crosslink-overview] `ZIP [Unassigned]: Shielded Labs Crosslink v1: Protocol Overview and Architecture <draft-shieldedlabs-crosslink-overview.rst>`_
