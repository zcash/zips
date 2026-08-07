::

  ZIP: ??? <Wishing Well>
  Title: The Wishing Well Protocol
  Owners: Nathan Wilcox <nathan@electriccoin.co>
  Credits: 
  Status: Proposed
  Category: Application Standard
  Created: 2020-08-10
  License: MIT


Terminology
===========

The key words "MUST", "SHOULD", and "OPTIONAL" in this document are to be interpreted
as described in RFC 2119. [#RFC2119]_

The term "network upgrade" in this document is to be interpreted as described in ZIP 200
[#zip-0200]_.

The term "Sapling" in this document is to be interpreted as described in ZIP 205
[#zip-0205]_.

The term "Sprout value pool balance" in this document is to be interpreted as described
in ZIP 209 [#zip-0209]_.


Abstract
========

A `Wishing Well` is a Zcash Sapling Z-Address for which no Spending Key exists. The Viewing Key is derived from a `Wishing Well Seed` by the `Wishing Well Derivation Scheme` introduced here. This ensures there is no corresponding `Spending Key`. Participants with the Viewing Key can thus be certain that any ZEC sent to that address is unrecoverable by anyone, which enables certain use cases.

Motivation
==========

The technique of "burning" crypto assets has wide applicability across the cryptocurrency design space for both base protocols as well as applications built atop existing base consensus protocols. While base protocols may rely on burning to achieve broad systemic properties of the supply, the use in higher level applications is typically to ensure participants incur some cost while also preventing any party from accruing the associated funds. This often helps ensure fairness while leveraging the crypto asset's scarcity within an application.

For example, a broadcast system may require funds to be burnt in order to prevent spam, while also ensuring the funds don't accrue to a centralized party who may unduly influence the broadcast system.

Specification
=============

Concepts and Terminology
------------------------

The protocol is used to create and interact with `Wishing Well` instances. Each instance has four associated components: a `Well Seed`, a `Sapling incoming viewing key` (aka `SIVK`), a `Sapling address`, and all associated `blockchain transactions` which send ZEC irretrievably to the given address along with an optional `encrypted memo`.

Wishing-Well-aware tools can `generate` and `verify` well seeds. A Wishing-Well-aware tool can `derive` a Well's SIVK from a seed.

Applications and/or their users manage the creation of instances, the distribution of the SIVK to a specific set of participants, the transfer of ZEC and memos to the address, and detecting/responding to other participants doing the same.

Note: a SIVK or Sapling address that is derived from a Sapling Spending Key (or any intermediate prerequisite) is distinguished in this document as a `typical SIVK` or `typical address`.

Design Goals
------------

#. Enable applications wherein a group may privately broadcast memos and provably burn funds.
#. Work with transparent backwards compatibility of existing Zcash Sapling protocol and tools.
#. Preserve the `Security Properties` below.

Security Properties
-------------------

#. Wishing-Well-aware applications or users can `verify` a seed to reasonably convince themselves that the ZEC sent into the Well is not recoverable. By implication: it is not possible for anyone to create any typical SIVK prerequisite and also a Well seed for the same SIVK [#].
#. Any Sapling-enabled wallets or other products can interact with an instance's SIVK and/or address with no awareness of, or specialized features for, the Wishing Well protocol.
#. It is not possible, without knowledge of either a Well seed or one typical Sapling address prerequisites, to determine whether or not a Sapling address is a Well address, a typical address, or perhaps derived from some other protocol.
#. It is not possible for a sender to a Well instance to determine whether or not their transfer to a Sapling address is into a Well instance versus a typical address or other case without knowledge of the Well seed.
#. All privacy properties of Sapling hold against all adversary models and capabilities that apply to typical Sapling usage.
#. It is not possible for an adversary observing the blockchain to distinguish Wishing Well transactions from other Sapling transactions. Caveats:
  - Different applications may have different usage patterns, especially timing, which may leave a signature on-chain. If a particular application which relies on the Wishing Well Protocol has a unique detectable usage pattern, this does not impact the on-chain privacy of different applications which rely on the Wishing Well Protocol.
#. It is not possible for a privacy adversary with knowledge of the Viewing Key to distinguish if that Viewing Key and associated Address is a Well instance versus a typical Sapling address. Caveats:
  - An adversary who can observe the lack of outgoing transactions may deduce that the associated address is a well instance.

.. [#] This follows from collision resistance of `BLAKE2s-256`. See [FIXME protocol reference].

Specification
=============

Well Seed Generation
--------------------

A `Well Seed` is an arbitrary application specific value. However, application designers should be aware of the security properties of their choice. For many applications, a seed should be generated as a 256-bit-entropy value. This ensures the seed is unguessable and will not collide with any other application instances.

An application may want a "globally public" Wishing Well, in which case it may use a well-known constant value.

In particular it is recommended against allowing users to select bare seeds.

Wishing Well Derivation Scheme
------------------------------

A Sapling incoming viewing key is derived from a `Well Seed` by using `blake2b` with the personalization ASCII string ``zcash-wishing-well-derivation-v1-u8eQd6IG7wsxlr+PC2UFa1GxttqAA159m+tdV3Tl3XI=``. [#]

.. [#] The suffix is random 32 bytes from the author's system encoded as base64, designed to reduce the possibility of an unrelated protocol or application using the same personalization string. While the source randomness is not verifiable, we posit this has no tangible impact.

Rationale
=========

TODO


Security and Privacy Considerations
===================================

TODO


Deployment
==========

TODO


Reference Implementation
========================

TODO


References
==========

TODO
