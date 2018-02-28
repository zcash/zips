::

  ZIP: 202
  Title: Version 3 Transaction Format for Overwinter
  Author: Simon Liu <simon@z.cash>
  Category: Consensus
  Created: 2018-01-10
  License: MIT

Terminology
===========

The key words "MUST", "MUST NOT", "SHOULD", and "MAY" in this document are to be interpreted as described in RFC 2119. [#RFC2119]_

Branch
  A chain of blocks with common consensus rules, where the first block in the chain is either the genesis
  block, or the child of a parent block created under an older set of consensus rules (i.e. the parent block
  is a member of a different branch). By definition, every block belongs to at most one branch.

Hard fork
  The creation of a new branch by a change in the consensus rules of the network. Nodes that do not recognize
  the new rules will continue to follow the old branch.

Network upgrade
  An intentional hard fork undertaken by the community in order to improve the network.

Overwinter
  Code-name for the first ZCash network upgrade, also known as Network Upgrade 0.

Abstract
========

This proposal defines a new transaction format required for Network Upgrade Activation Mechanism [#zip-0200]_ and Transaction Expiry [#zip-0203]_.

Motivation
==========

Zcash launched with support for upstream Bitcoin version 1 transactions and defined a new version 2 transaction format which added fields required for shielded transactions.

======== ================== =========================== ==========
Version  Field              Description                 Type
======== ================== =========================== ==========
>= 1     version            positive value              int32
>= 1     tx_in_count        variable length integer     compactSize
>= 1     tx_in              list of inputs              vector
>= 1     tx_out_count       variable length integer     compactSize
>= 1     tx_out             list of outputs             vector
>= 1     lock_time          block height or timestamp   uint32
>= 2     nJoinSplit         variable length integer     compactSize
>= 2     vJoinSplit         list of joinsplits          vector
>= 2     joinSplitPubKey    joinsplit_sig public key    32 bytes
>= 2     joinSplitSig       signature                   64 bytes
======== ================== =========================== ==========


A new transaction format is required to:

* support safe network upgrades as specified in Network Upgrade Activation Mechanism [#zip-0200]_;
* provide replay protection between pre-Overwinter and Overwinter branches during upgrades;
* provide replay protection between different branches post-Overwinter;
* enable a branch to support multiple transaction version formats;
* ensure transaction formats are parsed uniquely across parallel branches;
* support transaction expiry [#zip-0203]_.

Specification
=============

Transaction format version 3
----------------------------

A new version 3 transaction format will be introduced for Overwinter.

The version 3 format differs from the version 2 format in the following ways:

* header (first four bytes, little endian encoded)

  * fOverwintered flag : bit 31, must be set
  * nVersion : bits 30-0, positive integer
* nVersionGroupId
* nExpiryHeight

======== ================== =========================== =========
Version  Field              Description                 Type
======== ================== =========================== =========
>= 3     header             contains:                   uint32

                            - fOverwintered flag
                              (bit 31, always set)
                            - nVersion (bits 30-0)
>= 3     nVersionGroupId    version group id (not zero) uint32
>= 1     tx_in_count        variable length integer     compactSize
>= 1     tx_in              list of inputs              vector
>= 1     tx_out_count       variable length integer     compactSize
>= 1     tx_out             list of outputs             vector
>= 1     lock_time          block height or timestamp   uint32
>= 3     expiryHeight       block height                uint32
>= 2     nJoinSplit         variable length integer     compactSize
>= 2     vJoinSplit         list of joinsplits          vector
>= 2     joinSplitPubKey    joinsplit_sig public key    32 bytes
>= 2     joinSplitS ig      signature                   64 bytes
======== ================== =========================== =========


Header Field
------------

The first four bytes of pre-Overwinter and Overwinter transactions are little-endian encoded.

Version 1 transaction (txid 5c6ba844e1ca1c8083cd53e29971bd82f1f9eea1f86c1763a22dd4ca183ae061 https://zcash.blockexplorer.com/tx/5c6ba844e1ca1c8083cd53e29971bd82f1f9eea1f86c1763a22dd4ca183ae061)

* begins with little-endian byte sequence [0x01, 0x00, 0x00, 0x00]
* deserialized as 32-bit signed integer with decimal value of 1

Version 2 transaction (txid 4435bf8064e74f01262cb1725fd9b53e600fa285950163fd961bed3a64260d8b https://zcash.blockexplorer.com/tx/4435bf8064e74f01262cb1725fd9b53e600fa285950163fd961bed3a64260d8b)

* begins with little-endian byte sequence [0x02, 0x00, 0x00, 0x00]
* deserialized as 32-bit signed integer with decimal value of 2

Transaction parsers for versions of Zcash prior to Overwinter, and for most other Bitcoin forks, require the transaction version number to be positive.

With the version 3 transaction format, the first four bytes of a serialized transaction, the 32-bit header, are made up of two fields as shown in the table above:

* 1 bit Overwinter flag, must be set
* 31 bit unsigned int for the Version

Pre-Overwinter parsers will deserialize these four bytes as a 32-bit signed integer.  With two's complement integers, the most significant bit indicates whether an integer is positive or negative.  With the Overwinter flag set, the transaction version will be negative, resulting in pre-Overwinter parsers rejecting the transaction as invalid.  This provides transaction replay protection between per-Overwinter and Overwinter software.

Consider the following example of a serialized version 3 transaction.

Pre-Overwinter parser:

* data begins with little-endian byte sequence: [0x03, 0x00, 0x00, 0x80]
* deserialized as 32-bit signed integer

  * with hexadecimal value of 0x80000003 (most significant bit is set)
  * decimal value of -2147483645

Legacy parsers will expect the version to be a positive value, such as 1 or 2, and will thus reject the Overwinter transaction as invalid.

Overwinter parser:

- data begins with little-endian byte sequence: [0x03, 0x00, 0x00, 0x80]
- deserialized as 32-bit unsigned integer

  - with binary value of 0b10000000000000000000000000000011
- the 32-bits are decomposed into two fields

  - overwinter flag (bit 31) as a boolean, expected to be set
  - version (bits 30 - bit 0) as an unsigned integer, expected to have a decimal value of 3

Overwinter parsers will accept the transaction as valid as the most significant bit of the header has been set.  By masking off (unsetting) the most significant bit, the parser can retrieve the transaction version number::

    0x80000003 & 0x7FFFFFFFF = 0x00000003 = 3

Version Group Id
----------------

The version group id is a non-zero, random and unique identifier, of type uint32_t, assigned to a transaction format version, or a group of soft-forking transaction format versions.  The version group id helps nodes disambiguate between branches using the same version number.

That is, it prevents a client on one branch of the network from attempting to parse transactions intended for another branch, in the situation where the transactions share the same format version number but are actually specified differently.  For example, Zcash and a clone of Zcash might both define their own custom v3 transaction formats, but each will have its own unique version group id, so that they can reject v3 transactions with unknown version group ids.

The combination of transaction version and version group id, `nVersion || nVersionGroupId`, uniquely defines the transaction format, thus enabling parsers to reject transactions from outside the client's chain which cannot be parsed.

By convention, it is expected that when introducing a new transaction version requiring a network upgrade, a new unique version group id will be assigned to that transaction version.

However, if new transaction versions are soft-fork compatible with older transaction versions, the same version group id can be re-used.

Expiry Height
-------------

The expiry height field, as defined in the Transaction Expiry ZIP [#zip-0203]_, stores the block height after which a transaction can no longer be mined.

Transaction Validation
======================

A valid Overwinter transaction intended for Zcash MUST have:

- version number 3
- version group id 0x03C48270 [#versiongroupid]_
- fOverwintered flag set

Overwinter transaction parsers should reject transactions for violating consensus rules if:

- the fOverwintered flag is not set
- the version group id is unknown
- the version number is unknown

Implementation
==============

The comments and code samples in this section apply to the reference C++ implementation of Zcash.  Other implementations may vary.

Transaction Version
-------------------

Transaction version remains a positive value.  The main Zcash chain will follow convention and continue to order transaction versions in an ascending order.

Tests can continue to check for the existence of forwards-compatible transaction fields by checking the transaction version using comparison operators::

    if (tx.nVersion >= 2) {
        for (int js = 0; js < joinsplits; js++) {
            ...
        }
    }

When (de)serializing v3 transactions, the version group id should also be checked in case the transaction is intended for a branch which has a different format for its version 3 transaction::

    if (tx.nVersion == 3 && tx.nVersionGroupId == OVERWINTER_VERSION_GROUP_ID) {
        auto expiryHeight = tx.nExpiryHeight;
    }

Tests can continue to set the version to zero as an error condition::

    mtx.nVersion = 0


Overwinter Validation
---------------------

To test if the format of an Overwinter transaction is v3 or not::

    if (tx.fOverwintered && tx.nVersion == 3) {
        // Valid v3 format transaction
    }

This only tests that the format of the transaction matches the v3 specification described above.

To test if the format of an Overwinter transaction is both v3 and the transaction itself is intended for the client's chain::

    if (tx.fOverwintered &&
        tx.nVersionGroupId == OVERWINTER_VERSION_GROUP_ID) &&
        tx.nVersion == 3) {
        // Valid v3 format transaction intended for this client's chain
    }

It is expected that this test involving ``nVersionGroupId`` is only required when a transaction is being constructed or deserialized e.g. when an external transaction enters the system.

However, it's possible that a clone of Zcash is using the same version group id and passes the conditional.

Ultimately, a client can determine if a transaction is truly intended for the client's chain or not by following the signature verification process detailed in the Transaction Signature Verification for Overwinter ZIP [#zip-0143]_.

Deployment
==========

This proposal will be deployed with the Overwinter network upgrade.

Backwards compatibility
=======================

This proposal intentionally creates what is known as a "bilateral hard fork" between pre-Overwinter software and Overwinter-compatible software. Use of this new transaction format requires that all network participants upgrade their software to a compatible version within the upgrade window. Pre-Overwinter software will treat Overwinter transactions as invalid.  

Once Overwinter has activated, Overwinter-compatible software will reject version 1 and version 2 transactions, and will only accept transactions based upon supported transaction version numbers and recognized version group ids.


Reference Implementation
========================

https://github.com/zcash/zcash/pull/2925

References
==========

.. [#RFC2119] https://tools.ietf.org/html/rfc2119
.. [#zip-0143] `Transaction Signature Verification for Overwinter <https://github.com/zcash/zips/pull/129>`_
.. [#zip-0200] `Network Upgrade Activation Mechanism <https://github.com/zcash/zips/pull/128/>`_
.. [#zip-0201] `Network Handshaking for Overwinter <https://github.com/zcash/zips/pull/134/>`_
.. [#zip-0203] `Transaction Expiry <https://github.com/zcash/zips/pull/131>`_
.. [#versiongroupid] `OVERWINTER_VERSION_GROUP_ID <https://github.com/zcash/zcash/pull/2925/files#diff-5cb8d9decaa15620a8f98b0c6c44da9bR311>`_





