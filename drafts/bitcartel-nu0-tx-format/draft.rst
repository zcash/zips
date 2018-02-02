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

"Branch" - A chain of blocks with common consensus rules, where the first block in the chain is not the genesis block, but the child of a parent block created under an older set of consensus rules.

"Network Upgrade" - An intentional hard fork undertaken by the community in order to improve the network.

"Overwinter" - Code name for network upgrade zero.

Abstract
========

This proposal defines a new transaction format required for Network Upgrade Mechanism [#zip-0???]_ and Transaction Expiry [#zip-0???]_.

Related to [#zip-0143]_

Motivation
==========

A new transaction format is required to:

* support safe network upgrades as specified in Network Upgrade Activation Mechanism [#zip-0???]_;
* provide replay protection between pre-Overwinter and Overwinter network upgrades;
* provide replay protection between different branches post-Overwinter;
* enable a branch to support multiple transaction version formats;
* ensure transaction formats are parsed uniquely across parallel branches;
* support transaction expiry [#zip-0???]_.

Specification
=============

Transaction format version 1 and 2
----------------------------------

Zcash launched with support for upstream Bitcoin version 1 transactions and defined a new version 2 transaction format which added fields required for shielded transactions.

======== =============== =========================== =======
Version  Field           Description                 Type
======== =============== =========================== =======
>= 1     version         positive value              int32
>= 1     in_count        varint                      1-9 bytes
>= 1     tx_inputs       list of inputs              vector
>= 1     out_count       varint                      1-9 bytes
>= 1     tx_outputs      list of outputs             vector
>= 1     lock_time       block height or timestamp   uint32
>= 2     nJoinSplit      varint                      1-9 bytes
>= 2     vJoinSplit      list of joinsplits          vector
>= 2     joinSplitPubKey joinSplitSig public key     32 bytes
>= 2     joinSplitSig    signature                   64 bytes
======== =============== =========================== =======

Transaction format version 3
----------------------------

A new version 3 transaction format will be introduced for Overwinter.

The version 3 format differs from the version 2 format in the following ways:

* header (first four bytes, little endian encoded)
  * overwinter flag : bit 31, must be set
  * version : bits 30-0, positive integer
* branch id
* expiry height

======== =============== =========================== =======
Version  Field           Description                 Type
======== =============== =========================== =======
>= 3     header          flag: bit 31 must be set    uint32
                         version: bits 30-0 positive
>= 3     branch_id       format branch id            uint32
>= 1     in_count        varint                      1-9 bytes
>= 1     tx_inputs       list of inputs              vector
>= 1     out_count       varint                      1-9 bytes
>= 1     tx_outputs      list of outputs             vector
>= 1     lock_time       block height or timestamp   uint32
>= 3     expiry_height   block height                uint32
>= 2     nJoinSplit      varint                      1-9 bytes
>= 2     vJoinSplit      list of joinsplits          vector
>= 2     joinSplitPubKey joinSplitSig public key     32 bytes
>= 2     joinSplitSig    signature                   64 bytes
======== =============== =========================== =======


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

With the version 3 transaction format, the first four bytes of a serialized transaction, the 32-bit header, are made up of two fields as shown in the able above:

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

* data begins with little-endian byte sequence: [0x03, 0x00, 0x00, 0x80]
* deserialized as 32-bit unsigned integer
  * with binary value of 10000000000000000000000000000011
* decomposed into two fields  
  * overwinter flag (bit 31) is set
  * version (bits 30 - bit 0) have a decimal value of 3

Overwinter parsers will accept the transaction as valid as the most significant bit of the header has been set.  By masking off (unsetting) the most significant bit, the parser can retrieve the transaction version number::

    0x80000003 & 0x7FFFFFFFF = 0x00000003 = 3

Existing code can continue to check the transaction version using greater than comparison operators::

    if (tx.nVersion >= 3) {
      for (int js = 0; js < joinsplits; js++) {

Existing tests can continue to set tx.nVersion to zero as an error condition::

    mtx.nVersion = 0;
    // https://github.com/zcash/zcash/blob/59de56eeca6f9f6f7dc1841630d53676075242a5/src/gtest/test_mempool.cpp#L99

    EXPECT_CALL(state, DoS(100, false, REJECT_INVALID, "bad-txns-version-too-low", false)).Times(1);
    // https://github.com/zcash/zcash/blob/30d3d2dfd438a20167ddbe5ed2027d465cbec2f0/src/gtest/test_checktransaction.cpp#L99

Format Branch Id
----------------

As defined in Network Upgrade Mechanism [#zip-0???]_ every network upgrade can be identified by a branch id, a globally-unique non-zero 32-bit identifier.

A format branch id is the branch id when a new transaction format version was introduced on the main chain of a client implementation.  Overwinter requires a transaction to include the format branch id.

Including a format branch id prevents a client on one branch of the network from attempting to parse transactions intended for another branch, in the situation where the transactions share the same format version number but are specified differently.

The combination of transaction version and format branch id, `nVersion || nFormatBranchId` uniquely defines the transaction format, thus enabling parsers to reject transactions from outside the client's chain which cannot be parsed, providing users with replay protection. 

For example, at a block height H the reference implementation of Zcash introduces a new transaction version 3 format as part of the Overwinter network upgrade and assigns a branch id of 0x11111111.  Meanwhile, Zclone at that same block height decides to fork the network upgrade, creating a parallel branch with branch id 0xCCCCCCCC and modifying transaction version 3 format with new fields.  The Zcash parser will reject the Zclone transactions and vice versa, ensuring replay protection, even though both clients create transactions with the version number of 3.

Expiry Height
-------------

The expiry height field specifies the last block height at which a transaction must be mined into a block, after which the transaction is deemed to have expired and should be removed from the mempool.  A block is invalid if it contains an expired transaction.  More information can be found in the Transaction Expiry ZIP [#zip-???]_

Transaction Validation
======================

A client which supports the consensus rules identified by the format branch id should accept the transaction for further validation.  If the value of the branch id is zero, this indicates the absence of any network upgrade and that Sprout consensus rules apply.

Overwinter parsers should reject transactions from further processing and validation if the:

- version number is unknown
- overwinter flag is not set
- format branch id is not set

Overwinter clients should reject transactions for violating consensus rules if:

- version number is invalid according to current set of active consensus rules
- format branch id is different from the branch id corresponding to the current set of active consensus rules
- mis-matched format branch id causes signatures to fail verification under the new Overwinter signature hashing scheme which includes a branch id

Reference Implementation
========================

Coming soon.

Deployment
==========

This proposal will be deployed with the Overwinter network upgrade.

Testnet: block ???

Mainnet: block ???

Backwards compatibility
=======================

This proposal intentionally creates what is known as a "bilateral hard fork" between pre-Overwinter software and Overwinter compatible software. Use of this new transaction format requires that all network participants upgrade their software to a compatible version within the upgrade window. Pre-Overwinter software will treat Overwinter transactions as invalid.  Overwinter compatible software will reject legacy transactions.  Once Overwinter has activated, nodes will only accept transactions based upon supported branch id and transaction versions.


Reference Implementation
========================

TBC


References
==========

Design hard fork activation mechanism https://github.com/zcash/zcash/issues/2286

.. [#zip-0???] Network Upgrade Activation Mechanism

.. [#zip-0???] Transaction Expiry

.. [#zip-0143] Transaction Signature Verification for Overwinter



