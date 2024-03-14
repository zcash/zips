::

  ZIP: ???
  Title: Regular Periodic Turnstiles
  Owner: Nathan Wilcox <nathan@electriccoin.co>
  Original-Authors: Nathan Wilcox
  Status: Draft
  Category: Protocol Design Policy
  Created: 2020-01-20
  License: MIT


Terminology
===========

The key words "MUST", "MUST NOT", "SHOULD", and "MAY" in this document are to
be interpreted as described in RFC 2119. [#RFC2119]_

The terms below are to be interpreted as follows:

Sprout protocol
  Code-name for the Zcash shielded protocol at launch.
Sapling protocol
  Code-name for the Zcash shielded protocol added by the second Zcash network
  upgrade, also known as Network Upgrade 1.
Blossom protocol
  Code-name for the Zcash shielded protocol added by the third Zcash network
  upgrade, also known as Network Upgrade 2.


Abstract
========

This ZIP establishes a protocol design policy to make Zcash `shielded pool turnstiles` a regular process on a predictable schedule. The schedule introduces a new shielded pool once per year, as well as an established `retirement process` for older pools.

Motivation
==========

…

Requirements
============

Transaction Semantics
---------------------

This specification requires the following transaction semantics remain in place in future upgrades. These semantics are already present since the Network Upgrade 1 Sapling upgrade:

#. A transaction's interactions with any given pool are publicly verifiable in the consensus representation. For example, if a transaction involves the Sprout (original) pool and the Sapling NU1 pool, then separate Sprout and Sapling fields are present. Note that if this ZIP is standardized, some pools may have identical field layouts and semantics, and MUST never-the-less be distinguishable in the transaction representation.
#. ZEC may not enter or leave a pool except through an unencrypted, unobfuscated value encoding in the transaction field representing interactions with that pool. Note that this value representation does not require interacting with Transparent addresses, and these semantics can remain in place even should Transparent Addresses be retired from the protocol.

Schedule
--------

Once per year, during a network upgrade, a new `shielded pool` is established in the consensus protocol. Such network upgrades are referred to as `major network upgrades`. Other upgrades are referred to as `minor network upgrades`.

These shielded pools are referred to by the major network upgrade that introduces them, as in `shielded pool NU5` would be the shielded pool introduced in `Network Upgrade 5` which implies NU5 is a major upgrade.

Only a subset of network upgrades, the major upgrades, introduce shielded pools, since more than one network upgrade may occur in one year. Also note that this policy requires *at least one* network upgrade per year.

Shielded Pool Lifecycles
------------------------

Shielded pools are retired through a well-known `retirement process` on a predictable schedule so that they adhere to the following `shielded pool lifecycle` which is a sequence of `stages`. Shielded pools transition to subsequent stages only via the activation of a major network upgrade. At the activation of each major network upgrade, a shielded pool always transitions to the subsequent stage, unless it is in the frozen stage in which it remains permanently.

The stages are:

#. `Current Shielded Pool Stage`
#. `Previous Shielded Pool Stage`
#. `Restricted Shielded Pool Stage`
#. `Retired Shielded Pool Stage`
#. `Frozen Shielded Pool Stage`

Protocol Lifecycle States
~~~~~~~~~~~~~~~~~~~~~~~~~

Each lifecycle `stage` has an associated `protocol lifecycle state` (or `protocol state` for short) which determines a standard set of consensus rule semantics for interacting with that shielded pool.

#. Both the `current` and `previous` stages are in the `active protocol state`. In this state the full functionality of the associated pool is available, including transfering funds into the pool from any other active pool or transparent address, transfering funds within the pool, and transfering funds out of the active pool either to a Transparent Address or any other active pool.
#. The `restricted` stage is in the `restricted protocol state`, which prevents any transfers of funds *into* the pool. Funds may still be transferred out of the pool, and between accounts in the pool. [#]_
#. The `retired` stage is in the `retired protocol state`, which disallows any transfer of funds *except* out of the pool. This explicitly prohibits transfers of funds between addresses within the pool. [#]_
#. The `frozen` stage is the `frozen protocol state`, in which no transactions may interact with the pool.

.. [#] Implementation note: Because of the transaction semantic requirements, this rule can generally be enforced without circuit changes by merely requiring the transparent funds input to the pool to equal 0.


Protocol States and Future Compatibility
++++++++++++++++++++++++++++++++++++++++

Zcash is likely to extend shielded functionality in the future in a manner of ways, potentially including even general purpose stateful extensions. If this ZIP is standardized, all such new functionality specifications MUST define appropriate semantics for the four `protocol lifecycle states` above.

User Interface Interactions
---------------------------

This ZIP standardizes several user interface requirements:

Addresses
~~~~~~~~~

Some major upgrades will require address format changes, and some will not. It is also possible a future pool may support multiple distinct address types due to different kinds of functionality. Therefore, user interfaces must account for managing funds across multiple pools for a single address.

Migration
~~~~~~~~~

Because fund amounts must be transparently publicly revealed in transfers between pools by design, this can negatively impact user privacy. User interfaces should provide tools to help users migrate funds between pools as safely as possible.

This ZIP requires that user interfaces support the [#zip-0308]_ migration design from any non-frozen pool to the active pool only. If the [#zip-0308]_ migration design is superceded, user interfaces MUST adopt the newer migration design upon the next major activation.

.. admonition:: TODO

   Introduce an improvement ZIP based on [#zip-0308]_ that is general between pools and thus compatible with this ZIP.

Non-requirements
================

…

Specification
=============

…

Related ZIPs
------------

…

Open questions
--------------

…

Consensus Node Support
======================

…

References
==========

.. [#zip-0308] `ZIP 308: Sprout to Sapling Migration <zip-0308.rst>`_
