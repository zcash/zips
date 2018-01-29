::

  ZIP: ???
  Title: Network Upgrade Mechanism
  Author: Jack Grigg <jack@z.cash>
  Comments-Summary: No comments yet.
  Category: Process
  Created: 2018-01-08
  License: MIT


Terminology
===========

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this document are to be interpreted as
described in RFC 2119.

The following terms are interpreted as follows:

Branch
  A chain of blocks with common consensus rules, where the first block in the chain is not the genesis block,
  but the child of a parent block created under an older set of consensus rules.

Hard fork
  The creation of a new branch by a change in the consensus rules of the network. Nodes that do not recognize
  the new rules will continue to follow the old branch.

Network Upgrade
  An intentional hard fork undertaken by the community in order to improve the network.


Abstract
========

This proposal defines a mechanism for coordinating upgrades of the Zcash network, in order to remove ambiguity
about when network upgrades will activate, provide defined periods in which users should upgrade their local
software, and minimize the risks to both the upgrading network and those users opting out of the changes.


Motivation
==========

Zcash is a *consensual currency*: nobody is ever going to force someone to use a specific software
implementation or a specific branch of Zcash. [#consensual-currency]_ As such, different sub-communities will
always have the freedom to choose different variants or branches which offer different design trade-offs.

The current Zcash software includes an *auto-senescence* feature, causing nodes running a particular version
to automatically shut down 16 weeks after that version was released. This was implemented for several reasons
[#release-lifecycle]_:

- It gives the same systemic advantage of removing old software as auto-upgrade behavior.

- It requires users to individually choose one of the following options:

  - Upgrade to a more recent software release from the main network.

  - Upgrade to an alternative release.

  - Ignore the "deprecation" and keep running the older software.

Developers can rely on this cadence for coordinating network upgrades. Once the last pre-upgrade software
version has been deprecated, they can reasonably assume that all node operators on the network either support
the upgraded rules, or have explicitly chosen not to follow them.

However, this behaviour is not sufficient for performing network upgrades. A globally-understood on-chain
activation mechanism is necessary so that nodes can unambiguously know at what point the changes from an
upgrade come into effect (and can enforce consensus rule changes, for example).


Specification
=============

The following constants are defined for every network upgrade:

BRANCH_ID
  A globally-unique non-zero 32-bit identifier.

  Implementations MAY use a value of zero in branch ID fields to indicate the absence of any upgrade (i.e.
  that the Sprout consensus rules apply).

ACTIVATION_HEIGHT
  The block height at which the network upgrade rules will come into effect, and be enforced as part of the
  blockchain consensus.

  For removal of ambiguity, the block at height ``ACTIVATION_HEIGHT - 1`` is subject to the pre-upgrade
  consensus rules, and would be the last common block in the event of a persistent pre-upgrade branch.

  It MUST be greater than the value of ``DEPRECATION_HEIGHT`` in the last software version that will not
  contain support for the network upgrade. It SHOULD be chosen to be reached approximately three months after
  the first software version containing support for the network upgrade is released, for the following reason:

  - As of the time of writing (the 1.0.15 release), the release cycle is six weeks long, and nodes undergo
    auto-senescence 16 weeks after release. Thus, if version ``X`` contains support for a network upgrade,
    version ``X-1`` will deprecate 10 weeks after the release of version ``X``, which is about 2.3 months. A
    three-month window provides ample time for users to upgrade their nodes after auto-senescence, and
    re-integrate into the network prior to activation of the network upgrade.

Activation mechanism
--------------------

There MUST only be one network upgrade at a time in progress. Concretely, this means that the Zcash blockchain
is broken into "epochs" of block height intervals ``[ACTIVATION_HEIGHT_{N-1}, ACTIVATION_HEIGHT_N)`` (ie.
including ``ACTIVATION_HEIGHT_{N-1}`` and exluding ``ACTIVATION_HEIGHT_N``), on which consensus rule sets are
defined.

Consensus rules themselves (and any network behavior or surrounding code that depends on them) MUST be gated
by block height checks. For example:

.. code:: cpp

  if (chainActive.Tip()->nHeight >= OVERWINTER.ACTIVATION_HEIGHT) {
      // Overwinter-specific logic
  } else {
      // Pre-Overwinter logic
  }

  // ...

  if (pindex->nHeight >= OVERWINTER.ACTIVATION_HEIGHT) {
      // Overwinter consensus rules applied to block
  } else {
      // Pre-Overwinter consensus rules applied to block
  }


Block parsing
`````````````
Incoming blocks known to have a particular height (due to their parent chain being entirely known) MUST be
parsed under the consensus rules corresponding to their height.

Incoming blocks with unknown heights (because at least one block in their parent chain is unknown) MUST NOT be
considered valid, but MAY be cached for future consideration after all their parents have been received.

Chain reorganization
````````````````````
It is possible for a reorganization to occur that rolls back from after the activation height, to before that
height. This can handled in the same way as any regular chain orphaning or reorganization, as long as the new
chain is valid over the same epochs.

Post-activation upgrading
`````````````````````````
If a user does not upgrade their node to a compatible software version before ``ACTIVATION_HEIGHT`` is
reached, their node will follow the pre-upgrade chain and download blocks that are incompatible with the
post-upgrade branch. If the user subsequently upgrades their node to a compatible software version, the node
will consider these blocks to be invalid, and MUST take one of the two following actions:

- Discard all blocks of height ``ACTIVATION_HEIGHT`` and above, and then synchronize with the network.

- Shut down and alert the user of the issue. In this case, the node could offer an option to perform the first
  action.

Memory pool
-----------

While the current chain tip height is below ``ACTIVATION_HEIGHT``, nodes SHOULD NOT accept transactions that
will only be valid on the post-upgrade chain.

When the current chain tip height reaches ``ACTIVATION_HEIGHT``, the node's local transaction memory pool
SHOULD be cleared.

Two-way replay protection
-------------------------

Before the Overwinter network upgrade, two-way replay protection is ensured by enforcing post-upgrade that the
MSB of the transaction version is set to 1. From the perspective of old nodes, the transactions will have a
negative version number, which is invalid under the old consensus rules. Enforcing this rule trivially makes
old transactions invalid on the Overwinter branch.

After the Overwinter network upgrade, two-way replay protection is ensured by transaction signatures
committing to a specific ``BRANCH_ID``. [#zip-0143]_

Wipe-out protection
-------------------

Nodes running upgrade-aware software versions will enforce the upgraded consensus rules from
``ACTIVATION_HEIGHT``. The chain from that height will not reorg to a pre-upgrade branch if any block would
violate the new consensus rules (such as including any old-format transaction).

[TODO: if the non-upgraded chain only had empty blocks, technically that would be valid under new rules, so
could cause a wipe-out. Fixing this would require at least changing the block version, in which case blocks
may as well commit to a ``BRANCH_ID``.]


Example
=======

TBC


Deployment
==========

This proposal will be deployed with the Overwinter network upgrade.


Backward compatibility
======================

This proposal intentionally creates what is known as a "bilateral hard fork". Use of this mechanism requires
that all network participants upgrade their software to a compatible version within the upgrade window. Older
software will treat post-upgrade blocks as invalid, and will follow any pre-upgrade branch that persists.


Reference Implementation
========================

TBC


References
==========

.. [#consensual-currency] https://z.cash/blog/consensual-currency.html
.. [#release-lifecycle]
   - https://z.cash/blog/release-cycle-and-lifetimes.html
   - https://z.cash/blog/release-cycle-update.html
.. [#roadmap-2018] https://z.cash/blog/roadmap-update-2017-12.html
.. [#zip-0143] Transaction Signature Verification for Overwinter
