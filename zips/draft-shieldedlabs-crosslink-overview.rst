::

  ZIP: Unassigned {numbers are assigned by ZIP editors}
  Title: Zcash Trailing Finality Layer: Design Overview and Motivation
  Owners: Nate Wilcox <nate@shieldedlabs.com>
  Credits: Daira-Emma Hopwood
           Jack Grigg
           Kris Nuttycombe
  Status: Draft
  Category: Informational
  Created: 2026-04-08
  License: MIT
  Discussions-To: <https://github.com/zcash/zips/issues>


Terminology
===========

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this
document are to be interpreted as described in BCP 14 [#BCP14]_ when, and only
when, they appear in all capitals.

The terms "Mainnet" and "Testnet" in this document are to be interpreted as
defined in the Zcash protocol specification [#protocol-networks]_.

The terms below are to be interpreted as follows:

Trailing Finality Layer (TFL)
  A new Proof-of-Stake subprotocol that provides assured finality for the
  Zcash block chain, ensuring that blocks (and the transactions within them)
  that achieve finality may never be rolled back by the protocol.

PoW+TFL
  The overall complete, integrated hybrid Proof-of-Work / Proof-of-Stake
  consensus protocol described in this and related ZIPs.

Crosslink
  The hybrid construction specifying how the PoW and PoS subprotocols interact
  within PoW+TFL. The specific version described in this series of ZIPs is
  "Crosslink 2".

PoW subprotocol
  The Proof-of-Work consensus subprotocol in PoW+TFL, which is a modification
  of the existing Zcash NU5/NU6 consensus protocol with minimal changes to
  accommodate integration with the TFL.

PoS subprotocol (Π\ :sub:`bft`)
  The Byzantine-Fault-Tolerant Proof-of-Stake consensus subprotocol in
  PoW+TFL, which provides assured finality.

Assured Finality
  A protocol property that assures that transactions cannot be reverted by the
  protocol. Once a transaction achieves finality it retains that property
  indefinitely (so long as protocol requirements are met).

Trailing Finality
  A protocol property wherein transactions become final some time after first
  appearing in PoW blocks.

Best-chain protocol (Π\ :sub:`bc`)
  A longest-chain-rule protocol (such as a PoW protocol) in which the
  "canonical" chain is determined by a fork-choice rule operating on locally
  observed chains.

BFT protocol (Π\ :sub:`bft`)
  A Byzantine Fault Tolerant protocol that provides assured finality for
  blocks it finalizes.

Bounded Availability
  The property that the best-chain ledger does not grow unboundedly ahead of
  the finalized ledger during a finality stall, preventing indefinite
  accumulation of unfinalized transactions.

Finality Gap
  The number of best-chain (PoW) blocks that have not yet been finalized by
  the BFT subprotocol at a given time.

Stalled Mode
  A mode entered when the finality gap exceeds a threshold ``L``, indicating
  an exceptional or emergency condition.


Abstract
========

This ZIP describes the high-level design goals, motivations, and architecture
of the Zcash Trailing Finality Layer (TFL), a proposal to augment the existing
Zcash Proof-of-Work consensus with a new Proof-of-Stake consensus subprotocol
that provides assured, trailing finality.

The TFL design introduces the PoW+TFL hybrid consensus protocol, integrating
the current PoW chain with a new BFT-based PoS layer through a hybrid
construction called Crosslink (specifically Crosslink 2). This document is
intended as a companion to ZIP [#zip-crosslink-construction]_, which provides
the formal protocol specification for the Crosslink 2 construction.

This ZIP does not itself specify consensus rules, but provides the rationale,
goals, and architectural context necessary to evaluate the Crosslink 2
construction specified in the companion ZIP.


Motivation
==========

Probabilistic vs. Assured Finality
-----------------------------------

The current Zcash consensus protocol uses Nakamoto-style Proof-of-Work, which
provides only *probabilistic* finality: a transaction confirmed at depth ``k``
can theoretically be reversed by an adversary with sufficient hash rate.
Although deep reorgs are costly and increasingly unlikely as depth increases,
they are not impossible. This limitation has several practical consequences:

* **Exchange and service delays**: Exchanges and other services must wait for
  many confirmations before crediting deposits, increasing friction for users.

* **Bridge trust assumptions**: Cross-chain bridges and atomic swaps must
  account for reorg risk, often requiring conservative confirmation depths or
  additional trust assumptions.

* **Wallet complexity**: Wallets must communicate uncertainty about
  transaction finality to users, complicating UX.

Assured finality — the property that a finalized transaction *cannot* be
reversed by the protocol — removes these limitations. Any system that can
rely on assured finality can offer faster, safer service with simpler
reasoning about transaction status.

Why Proof-of-Stake for Finality?
---------------------------------

Proof-of-Stake (PoS) consensus protocols using Byzantine Fault Tolerant (BFT)
algorithms are well-established approaches for providing assured finality.
Tendermint, PBFT, Casper, and related protocols all achieve this goal with
strong theoretical foundations. Integrating a BFT PoS layer into Zcash as a
*finality layer* — rather than replacing PoW entirely — allows the ecosystem to:

1. **Retain PoW security**: The PoW chain continues to provide its well-understood
   liveness and censorship-resistance properties.

2. **Add PoS staking rewards**: ZEC holders can participate in network security
   by operating PoS validators or delegating to them, earning protocol rewards.

3. **Minimize disruption**: The transition preserves existing wallets, services,
   and tooling with minimal required changes.

4. **Enable future evolution**: A successful hybrid PoW/PoS transition builds
   confidence and infrastructure for potential future full PoS transitions.

Why Crosslink Rather Than Snap-and-Chat?
-----------------------------------------

An earlier candidate for the hybrid construction was the Snap-and-Chat
protocol from the Ebb-and-Flow paper [#ebb-and-flow]_. However, analysis
revealed several issues with Snap-and-Chat in the Zcash context [#tfl-book]_,
motivating the development of the Crosslink 2 construction:

* Snap-and-Chat's "sanitization" step complicates transaction finality
  semantics in ways that interact poorly with Zcash's shielded transaction
  model.

* Snap-and-Chat does not implement bounded availability, which is a safety
  property important for protecting users during finality stalls.

* The security analysis of Crosslink 2 is more rigorous and complete than
  what is available for Snap-and-Chat.

The Crosslink 2 construction, specified in ZIP [#zip-crosslink-construction]_,
addresses these issues.

The Case for Bounded Availability
-----------------------------------

A key design goal of Crosslink is *bounded availability*: preventing the PoW
chain from growing unboundedly ahead of the finalized chain during a finality
stall. Without this property, a period of BFT protocol failure could allow
unbounded accumulation of unfinalized transactions. When the BFT protocol
recovered, users would face uncertainty about which transactions would
ultimately be finalized and which would be reversed.

Bounded availability addresses this by entering "Stalled Mode" when the
finality gap exceeds a threshold ``L``. In Stalled Mode, PoW block producers
are constrained to produce only "stalled blocks" — blocks that do not include
new user transactions spending into the unfinalized zone. This limits user
exposure during BFT failures.

The arguments for bounded availability and finality overrides are developed in
detail in [#tfl-book]_ and informed the design of Crosslink 2.


Requirements
============

The PoW+TFL design must satisfy the following requirements:

Finality Requirements
---------------------

* The protocol MUST provide assured finality for transactions included in
  finalized blocks.

* The expected time-to-finality SHOULD be below 30 minutes under normal
  network conditions.

* The protocol MUST maintain Local Finalization Linearity: from any single
  node's perspective, the locally-finalized chain can only grow forward, never
  roll back.

Safety Requirements
--------------------

* The cost-of-attack for a 1-hour rollback of the PoW chain MUST NOT be
  reduced compared to the current Zcash consensus protocol, given a reasonably
  rigorous security argument.

* The cost-of-attack to halt the chain MUST be larger than the 24-hour revenue
  of PoW mining rewards, given a reasonably rigorous security argument.

Backward Compatibility Requirements
-------------------------------------

* All currently supported wallet operations (addresses, payment flow, ZEC
  transfers, backup/restore, etc.) MUST continue to function without change
  through the protocol transition, assuming wallets rely on the lightwalletd
  protocol or a full-node API.

* Mining pool operators relying on zcashd-compatible ``GetBlockTemplate``
  MUST NOT be required to make software changes, with the narrow exception of
  software that hardcodes block reward amounts rather than deriving them from
  ``GetBlockTemplate``.

* The ZEC supply cap and issuance schedule MUST be preserved.

* Block explorers that display transaction and block information MUST continue
  to function with the same user experience through the transition.

Bounded Availability Requirements
-----------------------------------

* The protocol MUST implement bounded availability: the PoW best-chain MUST
  NOT grow more than ``L`` blocks ahead of the finalized chain during a
  finality stall, where ``L`` is a protocol parameter.

* ``L`` MUST be set significantly larger than the bc-confirmation-depth ``σ``,
  with a minimum of ``L ≥ 2σ``.

Staking Requirements
--------------------

* ZEC holders MUST be able to earn protocol rewards by operating PoS
  validators or delegating ZEC to validators.

* PoS validators MUST NOT have discretionary control over delegated funds; they
  MUST NOT be able to steal delegated ZEC.

* The protocol MUST allow slashing of validator stake for provable misbehavior.


Non-requirements
================

The following are explicitly out of scope for the initial TFL design:

* Minimizing time-to-finality as a primary goal over other considerations such
  as protocol simplicity or impact on existing use cases.

* In-protocol liquid staking derivatives.

* Maximizing the staked-voter count ceiling. The design may have a relatively
  low ceiling of hundreds to a few thousand staked validators.

* Reducing overall network energy usage (this cannot be achieved for a
  hybrid PoW/PoS design without loss of security).


Specification
=============

Protocol Architecture
---------------------

PoW+TFL is logically an extension of the Zcash consensus rules that introduces
trailing finality. The top-level protocol is divided into two consensus
subprotocols:

1. **PoW Subprotocol** (Π\ :sub:`bc`): Based on the existing Zcash NU5/NU6
   consensus protocol with minimal modifications. This subprotocol remains
   responsible for the majority of consensus rules including transaction
   semantics, shielded transfers, and supply schedule.

2. **PoS Subprotocol** (Π\ :sub:`bft`): A new BFT-based protocol providing
   assured finality for PoW blocks. This is the Trailing Finality Layer itself.

These two subprotocols interact through the **Crosslink 2 hybrid construction**,
which specifies:

* What structural additions are required in each subprotocol's blocks and
  proposals (cross-references between chains).

* How the locally-finalized chain is maintained and updated.

* How the locally-bounded-available chain is determined.

* The Stalled Mode behavior and constraints on PoW block production during
  finality stalls.

The Crosslink 2 construction is formally specified in ZIP
[#zip-crosslink-construction]_.

Modular Design Principles
--------------------------

The TFL is designed to be modular:

* The PoW and PoS subprotocols are conceptually separable components that
  interact through the Crosslink 2 hybrid construction's defined interface.

* Different implementations MAY be provided for each subprotocol component,
  as long as they conform to the interfaces required by Crosslink 2.

* The PoS subprotocol (Π\ :sub:`bft`) is a pluggable component; the Crosslink
  2 construction defines the requirements it must satisfy (Final Agreement and
  related properties) without prescribing a specific BFT algorithm. The
  specific BFT algorithm to be used will be specified in a separate ZIP.

* This separation is also reflected in network and code architecture, enabling
  independent development and validation of each component.

Relationship to the NU5/NU6 Zcash Protocol
--------------------------------------------

The PoW subprotocol within PoW+TFL is not identical to NU5/NU6 but is closely
related. The Crosslink 2 construction requires the following changes to the
PoW subprotocol's block format and validity rules (described in detail in ZIP
[#zip-crosslink-construction]_):

* Each PoW block header MUST include a ``context_bft`` field referencing a BFT
  block, committing the PoW block producer to the current state of the BFT
  chain.

* PoW block validity rules are extended with contextual validity checks based
  on the ``context_bft`` field, including the requirement to enter Stalled Mode
  when the finality gap exceeds ``L``.

The BFT (PoS) subprotocol requires the following changes from its "off-the-shelf"
form:

* Each BFT proposal and block MUST include a ``headers_bc`` field containing
  a sequence of exactly ``σ`` PoW block headers, establishing the PoW chain
  snapshot at the time the BFT proposal was made.

These cross-referencing fields enable both chains to objectively verify
properties of the other chain, which is essential for the security of the
hybrid construction.

Network Upgrade Mechanism
--------------------------

PoW+TFL would be deployed via the existing Zcash network upgrade mechanism
[#zip-0200]_ as a consensus rule change. The precise activation height(s)
will be determined in subsequent process ZIPs once the protocol specification
is finalized.

Reward Distribution
--------------------

Activating PoW+TFL requires adjusting the Zcash block reward to provide
rewards to PoS validators while maintaining the existing ZEC supply schedule.
The specific reward allocation between PoW miners and PoS validators is not
specified in this ZIP; it will be addressed in a separate funding ZIP.

The ZEC supply cap of 21 million ZEC and the overall issuance schedule MUST
be preserved.


Security Considerations
=======================

Hybrid Protocol Security
-------------------------

The security of PoW+TFL depends on the security of both the PoW and PoS
subprotocols as well as the correctness of the Crosslink 2 hybrid construction.
The Crosslink 2 specification (ZIP [#zip-crosslink-construction]_) includes a
security analysis establishing the key properties: Assured Finality, Prefix
Consistency, and Bounded Availability.

BFT Protocol Failure
---------------------

If the BFT subprotocol experiences a safety failure (e.g., due to more than
one-third of stake being controlled by adversarial validators), the Crosslink 2
construction's finalization safety hazard detection will record the event. The
bounded availability property limits the damage from BFT liveness failures by
entering Stalled Mode when the finality gap grows too large.

PoW Protocol Failure
---------------------

If the PoW subprotocol experiences a deep reorg, but the BFT subprotocol has
not yet finalized the affected blocks, the Crosslink 2 construction will simply
not finalize those blocks. If the reorg affects already-finalized blocks, the
finalization safety hazard detection will record the event — but such an event
can only occur if safety assumptions about the BFT protocol (e.g., that fewer
than one-third of stake is adversarial) are also violated.

Staked ZEC Risk
---------------

ZEC delegated to or held by PoS validators may be subject to slashing
penalties for provable misbehavior. The protocol design MUST ensure that
slashing penalties cannot be imposed on honest validators, and that the
slashing conditions and amounts are deterministic and auditable.

Privacy Considerations
-----------------------

The TFL design introduces new on-chain data (BFT blocks, validator votes, and
cross-references between chains). Care must be taken to ensure that this new
data does not leak information about shielded transactions. The privacy
implications of PoS validator identity and staking will be analyzed in the
protocol specification ZIP.


Reference Implementation
========================

A prototype implementation of Crosslink is being developed in the
``zebra-crosslink`` component of [#zebra-crosslink]_. This implementation is
experimental and should not be used in production.


References
==========

.. [#BCP14] `Information on BCP 14 — "RFC 2119: Key words for use in RFCs to Indicate Requirement Levels" and "RFC 8174: Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words" <https://www.rfc-editor.org/info/bcp14>`_
.. [#protocol] `Zcash Protocol Specification, Version 2022.3.8 or later <protocol/protocol.pdf>`_
.. [#protocol-networks] `Zcash Protocol Specification, Version 2022.3.8. Section 3.12: Mainnet and Testnet <protocol/protocol.pdf#networks>`_
.. [#zip-0200] `ZIP 200: Network Upgrade Mechanism <zip-0200.rst>`_
.. [#zip-crosslink-construction] `ZIP [Unassigned]: Crosslink 2: Hybrid PoW/PoS Consensus Construction <draft-shieldedlabs-crosslink-construction.rst>`_
.. [#tfl-book] `Zcash Trailing Finality Layer Design Book <https://electric-coin-company.github.io/tfl-book/>`_
.. [#ebb-and-flow] `Ebb-and-Flow Protocols: A Resolution of the Availability-Finality Dilemma. David Neu, Joachim Neu, Ertem Nusret Tas, David Tse. <https://eprint.iacr.org/2020/1091.pdf>`_
.. [#zebra-crosslink] `ShieldedLabs zebra-crosslink repository <https://github.com/ShieldedLabs/zebra-crosslink>`_
