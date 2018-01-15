::

  ZIP: ???
  Title: Network Upgrade Zero ("OverWinter") Transaction Format
  Author: Simon Liu <simon@z.cash>
  Comments-Summary: No comments yet.
  Category: Process
  Created: 2018-01-10
  License: MIT

Terminology
===========

The key words "MUST", "MUST NOT", "SHOULD", and "MAY" in this document are to be interpreted as described in RFC 2119.

"Legacy" - pre-NU0

"NU0" - Network upgade zero

"Overwinter" - Code-name for NU0

Abstract
========

This proposal defines a new transaction format required for Network Upgrade Activation Mechanism [#zip-0???]_
and Transaction Expiry [#zip-0???]_.

Related to [#zip-0143]_

Motivation
==========

A new transaction format is required to:

* support safe network upgrades as specified in Network Upgrade Activation Mechanism [#zip-0???]_.
* provide replay protection between Legacy and Overwinter network upgrade.
* provide replay protection between different branches post-Overwinter e.g. Overwinter and Sapling upgrade.
* enable soft forks of transactions within a branch i.e. forwards compatibility, where a node will accept a newer transaction version format.
* enable a branch to support multiple transaction version formats
* support transaction expiry as specified in the Transaction Expiry [#zip-0???]_

Specification
=============

Zcash launched with support for upstream Bitcoin version 1 transactions and a custom version 2 transaction format which added fields required for shielded transactions.

======== =============== =========================== =======
Version  Field           Description                 Type
======== =============== =========================== =======
1        version         positive value              int32
1        in_count        varint                      1-9 bytes
1        tx_inputs       list of inputs              vector
1        out_count       varint                      1-9 bytes
1        tx_outputs      list of outputs             vector
1        lock_time       block height or timestamp   uint32
2        nJoinSplit      varint                      1-9 bytes
2        vJoinSplit      list of joinsplits          vector
2        joinSplitPubKey joinSplitSig public key     32 bytes
2        joinSplitSig    signature                   64 bytes
======== =============== =========================== =======

Version 1 and 2 transaction formats are legacy formats.

Version 3 transaction format will be introduced for Overwinter.

The version field must have its most significant bit set.

There will be new fields for:

* branch id
* expiry height
* list of extra fields for future soft forks

======== =============== =========================== =======
Version  Field           Description                 Type
======== =============== =========================== =======
3        version         bit 31 (msb) must be set    int32
3        branch_id       branch/fork identifier      uint32
3        expiry_height   block height                uint32
3        extra_count     number of extra fields      uint8
3        vExtraFields    list of uint32 extra fields vector
1        in_count        varint                      1-9 bytes
1        tx_inputs       list of inputs              vector
1        out_count       varint                      1-9 bytes
1        tx_outputs      list of outputs             vector
1        lock_time       block height or timestamp   uint32
2        nJoinSplit      varint                      1-9 bytes
2        vJoinSplit      list of joinsplits          vector
2        joinSplitPubKey joinSplitSig public key     32 bytes
2        joinSplitSig    signature                   64 bytes
======== =============== =========================== =======


Transaction Version
-------------------

With Overwinter, the most significant bit of the version field must be set, meaning that legacy parsers will interpret the version, the first four bytes of a serialized transaction, as a negative value.  Since legacy parsers expect version to be a positive value, such as 1 or 2, legacy parsers will reject Overwinter transactions as invalid.

Existing code typically checks the tx version using greater than comparison operators::

    if (tx.nVersion >= 2) {
      for (int js = 0; js < joinsplits; js++) {

Existing tests typically set tx.nVersion to zero as an error condition::

    mtx.nVersion = 0;
    // https://github.com/zcash/zcash/blob/59de56eeca6f9f6f7dc1841630d53676075242a5/src/gtest/test_mempool.cpp#L99
    
    EXPECT_CALL(state, DoS(100, false, REJECT_INVALID, "bad-txns-version-too-low", false)).Times(1);
    // https://github.com/zcash/zcash/blob/30d3d2dfd438a20167ddbe5ed2027d465cbec2f0/src/gtest/test_checktransaction.cpp#L99

By using a negative value for the version field, we ensure there is replay protection between Legacy and Overwinter compatible software.

Consider an example where the raw version field of an Overwinter transaction is 0xFFFFFFFD ( binary 11111111 11111111 11111111 11111101 )

Legacy parsers will deserialize the raw version field as a 32-bit signed integer.  With a negative version value of -3, legacy parsers will reject the transaction.

Overwinter parsers will deserialize the raw version field as a 32-bit signed integer.  With a negative raw value of -3, the Overwinter parser knows the most significant bit has been set; the parser could also choose to speficially test the bit has been set.

Overwinter parsers can retrieve the transaction format version of 3 by getting the absolute value of the raw version field e.g. using standard library call std::abs()

Currently, the nVersion field is a public member variable which can be accessed directly.  As part of implementing Overwinter, the nVersion field will be made private with access restricted to using getters, e.g.::

    bool isLegacyFormat()         // return true if the msb of nVersion is not set
    unsigned int32 getVersion()   // return absolute value of raw version field which is compatible with Legacy and Overwinter

Alternate Transaction Version
-----------------------------

Another option considered is that transaction version 3 could be represented as:

0x80000003 = 10000000 00000000 00000000 00000011

The value of the raw version field is -2147483646, so a Legacy parser would reject this transaction.

To retrieve the transaction version value of 3, an Overwinter parser would need to mask off the most significant byte.

0x7FFFFFFF & 0x80000003 = 00000000 00000000 00000000 00000011

This alternate method however implies that the transaction format should be changed to look like this:

======== =============== =========================== =======
Version  Field           Description                 Type
======== =============== =========================== =======
3        overwinter_flag must be set to 1            1 bit
3        version         positive value              31 bits
...      ...             ...                         ...
======== =============== =========================== =======



Soft forking with extra fields
------------------------------

Transaction version 3 will have no extra fields.

* extra_count must be 0
* vExtraFields must be empty

The extra fields are to be used by new transaction formats to maintain forwards compatibility.  For example, an Overwinter node should still be able to process transaction format version 4 if it introduces additional data fields which can be ignored by the node.

An Overwinter parser which can only process version 3 transactions should ignore the extra fields::

  if (tx.getVersion() >= 3) {
    // parse transaction, ignoring extra_count and vExtraFields
    // optionally assert that extra_count == 0 and vExtraFields.length == 0
  }

If the parser is aware of transaction version 4, code might look like this::

    if (tx.getVersion() == 3) {
      ...
    } else if (tx.getVersion() >= 4 ) {
      // verify extra_count should be 1
      // verify vExtraFields.length matches extra_count
      // retrieve the extra field
      // verify the extra field
      // take some action based on the extra field
    }
      
Multiple branches
-----------------

A branch may support many transaction version formats.  For example:

* Zcash reference implementation, branch "Zcash", versions 3, 4.
* Fork of Zcash, branch "Clone", versions 3, 4*

4* is transaction format version 4 for the "Clone" branch and might be substantially different from the expected transaction format version 4 for the "Zcash" branch.

Given forward compatibility, we want the "Zcash" branch nodes to reject version 4* transactions which are intended only for the "Clone" branch.

To achieve this, Overwinter requires a transaction to include a branch ID, to explicitly state which branch (i.e. network) this transaction is intended for.

Overwinter introduces a new signature hashing scheme which includes the branch ID, but by including the branch ID into the transaction format, clients can quickly reject transactions during deserialization without having to check signatures.

A simple way to filter transactions might look like this::

    if (tx.branchID != CLIENT_BRANCH_ID) { ... }
    
However given that a branch may support a set of transaction version formats, we should implement such that we can write code like::

    if (isBranchSupported(tx.getBranchID())) { ... }

    if (tx.isSupportedBranch()) { ... }
    
Overwinter will introduce a method for developers to easily specify and update a map of supported branch IDs and transaction versions which can be easily accessed throughout the system.

Deployment
==========

This proposal will be deployed with the Overwinter network upgrade.

Testnet:

Mainnet:

Backward compatibility
======================

This proposal intentionally creates what is known as a "bilateral hard fork" between Legacy software and Overwinter compatible software. Use of this new transaction format requires that all network participants upgrade their software to a compatible version within the upgrade window. Legacy software will treat Overwinter transactions as invalid.  Overwinter compatible software will reject legacy transactions.  Once Overwinter has activated, nodes will only accept transactions based upon supported branch ID and transaction versions.


Reference Implementation
========================

TBC


References
==========

Design hard fork activation mechanism https://github.com/zcash/zcash/issues/2286

.. [#zip-0???] Network Upgrade Activation Mechanism

.. [#zip-0???] Transaction Expiry

.. [#zip-0143] Transaction Signature Verification for Overwinter



