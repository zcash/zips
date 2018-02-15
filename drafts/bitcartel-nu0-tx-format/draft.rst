::

  ZIP: ???
  Title: Network Upgrade Zero ("OverWinter") Transaction Format
  Author: Simon Liu <simon@z.cash>
  Comments-Summary: No comments yet.
  Category: Consensus
  Created: 2018-01-10
  License: MIT

Terminology
===========

The key words "MUST", "MUST NOT", "SHOULD", and "MAY" in this document are to be interpreted as described in RFC 2119.

"Branch" - The key words "branch" and "network upgrade" in this document are to be interpreted as described in [#zip-0200]_.

"Network Upgrade" - An intentional hard fork undertaken by the community in order to improve the network.

"Overwinter" - Code name for network upgrade zero.

Abstract
========

This proposal defines a new transaction format required for Network Upgrade Activation Mechanism [#zip-0200]_ and Transaction Expiry [#zip-0???]_.

Related to [#zip-0143]_

Motivation
==========

Zcash launched with support for upstream Bitcoin version 1 transactions and defined a new version 2 transaction format which added fields required for shielded transactions.

======== ================== =========================== ==========
Version  Field              Description                 Type
======== ================== =========================== ==========
>= 1     version            positive value              int32
>= 1     in_count           varint                      1-9 bytes
>= 1     tx_inputs          list of inputs              vector
>= 1     out_count          varint                      1-9 bytes
>= 1     tx_outputs         list of outputs             vector
>= 1     lock_time          block height or timestamp   uint32
>= 2     joinsplit_count    varint                      1-9 bytes
>= 2     tx_joinsplits      list of joinsplits          vector
>= 2     joinsplit_pubkey   joinsplit_sig public key    32 bytes
>= 2     joinsplit_sig      signature                   64 bytes
======== ================== =========================== ==========


A new transaction format is required to:

* support safe network upgrades as specified in Network Upgrade Activation Mechanism [#zip-0200]_;
* provide replay protection between pre-Overwinter and Overwinter branches during upgrades;
* provide replay protection between different branches post-Overwinter;
* enable a branch to support multiple transaction version formats;
* ensure transaction formats are parsed uniquely across parallel branches;
* support transaction expiry [#zip-0???]_.

Specification
=============

Transaction format version 3
----------------------------

A new version 3 transaction format will be introduced for Overwinter.

The version 3 format differs from the version 2 format in the following ways:

* header (first four bytes, little endian encoded)

  * overwintered flag : bit 31, must be set
  * version : bits 30-0, positive integer
* version group id
* expiry height

======== ================== =========================== =========
Version  Field              Description                 Type
======== ================== =========================== =========
>= 3     header             - flag (bit 31 must be set) uint32
                            - version (bits 30-0)
>= 3     vers_group_id      version group id (not zero) uint32
>= 1     in_count           varint                      1-9 bytes
>= 1     tx_inputs          list of inputs              vector
>= 1     out_count          varint                      1-9 bytes
>= 1     tx_outputs         list of outputs             vector
>= 1     lock_time          block height or timestamp   uint32
>= 3     expiry_height      block height                uint32
>= 2     joinsplit_count    varint                      1-9 bytes
>= 2     tx_joinsplits      list of joinsplits          vector
>= 2     joinsplit_pubkey   joinsplit_sig public key    32 bytes
>= 2     joinsplit_sig      signature                   64 bytes
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

The version group id is a non-zero, random and unique identifier assigned to a transaction format version, or a group of soft-forking transaction format versions.  The version group id helps nodes disambiguate between branches using the same version number.

That is, it prevents a client on one branch of the network from attempting to parse transactions intended for another branch, in the situation where the transactions share the same format version number but are actually specified differently.  For example, Zcash and Zclone might both define their own custom v3 transaction formats, but each will have its own unique version group id, so that they can reject v3 transactions with unknown version group ids.

The combination of transaction version and version group id, ``nVersion || nVersionGroupId``, uniquely defines the transaction format, thus enabling parsers to reject transactions from outside the client's chain which cannot be parsed.

By convention, it is expected that when introducing a new transaction version requiring a network upgrade, a new unique version group id will be assigned to that transaction version.

However, if new transaction versions are soft-fork compatible with older transaction versions, the same version group id can be re-used.

Expiry Height
-------------

The expiry height field, as defined in the Transaction Expiry ZIP [#zip-???]_, stores the block height after which a transaction will be removed from the mempool if it has not been mined.

Transaction Validation
======================

A valid Overwinter transaction intended for Zcash must have:

- version number 3
- version group id as specified in Zcash source code
- overwintered flag set

Overwinter transaction parsers should reject transactions for violating consensus rules if:

- the overwintered flag is not set
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

    if (tx.nVersion == 3 && tx.nVersionGroupID == OVERWINTER_VERSION_GROUP_ID) {
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

To test if the format of an Overwinter transaction is bothv3 and the transaction itself is intended for the client's chain::

    if (tx.fOverwintered &&
        tx.nVersionGroupID == OVERWINTER_VERSION_GROUP_ID) &&
        tx.nVersion == 3) {
        // Valid v3 format transaction intended for this client's chain
    }

However, it's possible that a ZClone is using the same version group id and passes the conditional.

Ultimately, a client can determine if a transaction is truly intended for the client's chain or not by following the signature verification process detailed in the Transaction Signature Verification for Overwinter ZIP [#zip-???]_.

Deployment
==========

This proposal will be deployed with the Overwinter network upgrade.

Testnet is set to activate Overwinter at block XXX.

- This means that starting from block XXX of testnet, new Overwinter consensus rules take effect and transactions must be using v3 to be accepted as valid.

Mainnet is set to activate Overwinter at block XXX.

- This means that starting from block XXX of mainnet, new Overwinter consensus rules take effect and transactions must be using v3 to be accepted as valid.


Backwards compatibility
=======================

This proposal intentionally creates what is known as a "bilateral hard fork" between pre-Overwinter software and Overwinter compatible software. Use of this new transaction format requires that all network participants upgrade their software to a compatible version within the upgrade window. Pre-Overwinter software will treat Overwinter transactions as invalid.  Overwinter compatible software will reject legacy transactions.  Once Overwinter has activated, nodes will only accept transactions based upon supported transaction version numbers and recognized version group ids.


Reference Implementation
========================

https://github.com/zcash/zcash/pull/2925

References
==========

Design hard fork activation mechanism https://github.com/zcash/zcash/issues/2286

.. [#zip-0200] Network Upgrade Activation Mechanism

.. [#zip-0???] Transaction Expiry

.. [#zip-0143] Transaction Signature Verification for Overwinter




