::

  ZIP: 143
  Title: Transaction Signature Verification for Overwinter
  Author: Jack Grigg <jack@z.cash>
          Daira Hopwood <daira@z.cash>
  Credits: Johnson Lau <jl2012@xbt.hk>
           Pieter Wuille <pieter.wuille@gmail.com>
  Comments-Summary: No comments yet.
  Category: Process
  Created: 2017-12-27
  License: MIT


Terminology
===========

The key words "MUST" and "MUST NOT" in this document are to be interpreted as described in RFC 2119.


Abstract
========

This proposal defines a new transaction digest algorithm for signature verification from the Overwinter
network upgrade, in order to minimize redundant data hashing in verification, and to cover the input value by
the signature.


Motivation
==========

There are 4 ECDSA signature verification codes in the original Zcash script system: ``CHECKSIG``,
``CHECKSIGVERIFY``, ``CHECKMULTISIG``, ``CHECKMULTISIGVERIFY`` ("sigops"). According to the sighash type
(``ALL``, ``NONE``, or ``SINGLE``, possibly modified by ``ANYONECANPAY``), a transaction digest is generated
with a double SHA256 of a serialized subset of the transaction, and the signature is verified against this
digest with a given public key. The detailed procedure is described in a Bitcoin Wiki article. [#wiki-checksig]_

Unfortunately, there are at least 2 weaknesses in the original SignatureHash transaction digest algorithm:

* For the verification of each signature, the amount of data hashing is proportional to the size of the
  transaction. Therefore, data hashing grows in O(n\ :sup:`2`) as the number of sigops in a transaction
  increases. While a 1 MB block would normally take 2 seconds to verify with an average computer in 2015, a
  1MB transaction with 5569 sigops may take 25 seconds to verify. This could be fixed by optimizing the digest
  algorithm by introducing some reusable “midstate”, so the time complexity becomes O(n). [#quadratic]_

* The algorithm does not involve the value being spent by the input. This is usually not a problem for online
  network nodes as they could request for the specified transaction to acquire the output value. For an
  offline transaction signing device ("cold wallet"), however, the lack of knowledge of input amount makes it
  impossible to calculate the exact amount being spent and the transaction fee. To cope with this problem a
  cold wallet must also acquire the full transaction being spent, which could be a big obstacle in the
  implementation of a lightweight, air-gapped wallet. By including the input value of part of the transaction
  digest, a cold wallet may safely sign a transaction by learning the value from an untrusted source. In the
  case that a wrong value is provided and signed, the signature would be invalid and no funds would be lost.
  [#offline-wallets]_

Deploying the aforementioned fixes in the original script system is not a simple task.


Specification
=============

A new transaction digest algorithm is defined, but only applicable from the Overwinter upgrade block height
[#ZIP0000]_::
  BLAKE2b-256 of the serialization of:
    1. nVersion of the transaction (4-byte little endian)
    2. hashPrevouts (32-byte hash)
    3. hashSequence (32-byte hash)
    4. hashOutputs (32-byte hash)
    5. hashJoinSplits (32-byte hash)
    6. nLocktime of the transaction (8-byte little endian)
    7. sighash type of the signature (4-byte little endian)
    8. If we are serializing an input (ie. this is not a JoinSplit signature hash):
       a. outpoint (32-byte hash + 4-byte little endian) 
       b. scriptCode of the input (serialized as scripts inside CTxOuts) [TODO]
       c. value of the output spent by this input (8-byte little endian)
       d. nSequence of the input (4-byte little endian)

The BLAKE2b-256 personalization field will be set to::

  "ZcashSigHash" || BRANCH_ID

Semantics of the original sighash types remain unchanged, except the followings:

#. The way of serialization is changed;

#. All sighash types commit to the amount being spent by the signed input;

#. ``SINGLE`` does not commit to the input index. When ``ANYONECANPAY`` is not set, the semantics are
   unchanged since ``hashPrevouts`` and ``outpoint`` together implictly commit to the input index. When
   ``SINGLE`` is used with ``ANYONECANPAY``, omission of the index commitment allows permutation of the
   input-output pairs, as long as each pair is located at an equivalent index.

Field definitions
-----------------

The items 1, 6, 7, 8a, 8d have the same meaning as the original algorithm. [#wiki-checksig]_

2: ``hashPrevouts``
```````````````````
* If the ``ANYONECANPAY`` flag is not set, ``hashPrevouts`` is the double SHA256 of the serialization of all
  input outpoints;

* Otherwise, ``hashPrevouts`` is a ``uint256`` of ``0x0000......0000``.

3: ``hashSequence``
```````````````````
* If none of the ``ANYONECANPAY``, ``SINGLE``, ``NONE`` sighash type is set, ``hashSequence`` is the double
  SHA256 of the serialization of ``nSequence`` of all inputs;

* Otherwise, ``hashSequence`` is a ``uint256`` of ``0x0000......0000``.

4: ``hashOutputs``
``````````````````
* If the sighash type is neither ``SINGLE`` nor ``NONE``, ``hashOutputs`` is the double SHA256 of the
  serialization of all output amount (8-byte little endian) with ``scriptPubKey`` (serialized as scripts
  inside CTxOuts);

* If sighash type is ``SINGLE`` and the input index is smaller than the number of outputs, ``hashOutputs`` is
  the double SHA256 of the output amount with ``scriptPubKey`` of the same index as the input;

* Otherwise, ``hashOutputs`` is a ``uint256`` of ``0x0000......0000``. [#01-change]_

5: ``hashJoinSplits``
`````````````````````
* If ``vjoinsplits`` is non-empty, ``hashJoinSplits`` is the double SHA256 of the serialization of all
  JoinSplits concatenated with the joinSplitPubKey;

* Otherwise, ``hashJoinSplits`` is a ``uint256`` of ``0x0000......0000``.

8b: ``scriptCode``
``````````````````
[TODO: TBC]

* For ``P2PKH``, the ``scriptCode`` is ``0x1976a914{20-byte-pubkey-hash}88ac``.

* For ``P2SH``, the ``scriptCode`` is the ``script`` serialized as scripts inside ``CTxOut``.

8c: value
`````````
An 8-byte value of the amount of ZEC spent in this input.

Notes
-----

The ``hashPrevouts``, ``hashSequence``, ``hashOutputs``, and ``hashJoinSplits`` calculated in an earlier
verification may be reused in other inputs of the same transaction, so that the time complexity of the whole
hashing process reduces from O(n\ :sup:`2`) to O(n).

Refer to the reference implementation, reproduced below, for the precise algorithm:

.. code:: cpp

  uint256 hashPrevouts;
  uint256 hashSequence;
  uint256 hashOutputs;
  uint256 hashJoinSplits;

  if (!(nHashType & SIGHASH_ANYONECANPAY)) {
      CHashWriter ss(SER_GETHASH, 0);
      for (unsigned int n = 0; n < txTo.vin.size(); n++) {
          ss << txTo.vin[n].prevout;
      }
      hashPrevouts = ss.GetHash();
  }

  if (!(nHashType & SIGHASH_ANYONECANPAY) && (nHashType & 0x1f) != SIGHASH_SINGLE && (nHashType & 0x1f) != SIGHASH_NONE) {
      CHashWriter ss(SER_GETHASH, 0);
      for (unsigned int n = 0; n < txTo.vin.size(); n++) {
          ss << txTo.vin[n].nSequence;
      }
      hashSequence = ss.GetHash();
  }

  if ((nHashType & 0x1f) != SIGHASH_SINGLE && (nHashType & 0x1f) != SIGHASH_NONE) {
      CHashWriter ss(SER_GETHASH, 0);
      for (unsigned int n = 0; n < txTo.vout.size(); n++) {
          ss << txTo.vout[n];
      }
      hashOutputs = ss.GetHash();
  } else if ((nHashType & 0x1f) == SIGHASH_SINGLE && nIn < txTo.vout.size()) {
      CHashWriter ss(SER_GETHASH, 0);
      ss << txTo.vout[nIn];
      hashOutputs = ss.GetHash();
  }

  if (!txTo.vjoinsplit.empty()) {
      CHashWriter ss(SER_GETHASH, 0);
      for (unsigned int n = 0; n < txTo.vjoinsplit.size(); n++) {
          ss << txTo.vjoinsplit[n];
      }
      ss << txTo.joinSplitPubKey;
      hashJoinSplits = ss.GetHash();
  }

  unsigned char personalization[16] = {};
  memcpy(personalization, "ZcashSigHash", 12);
  memcpy(personalization+12, branchId, 4);

  CBlake2HashWriter ss(SER_GETHASH, 0, personalization);
  // Version
  ss << txTo.nVersion;
  // Input prevouts/nSequence (none/all, depending on flags)
  ss << hashPrevouts;
  ss << hashSequence;
  // Outputs (none/one/all, depending on flags)
  ss << hashOutputs;
  // JoinSplits
  ss << hashJoinSplits;
  // Locktime
  ss << txTo.nLockTime;
  // Sighash type
  ss << nHashType;

  if (nIn != NOT_AN_INPUT) {
      // The input being signed (replacing the scriptSig with scriptCode + amount)
      // The prevout may already be contained in hashPrevout, and the nSequence
      // may already be contain in hashSequence.
      ss << txTo.vin[nIn].prevout;
      ss << static_cast<const CScriptBase&>(scriptCode);
      ss << amount;
      ss << txTo.vin[nIn].nSequence;
  }

  return ss.GetHash();


Restrictions on public key type
===============================

[TODO: decide whether we want to implement this policy]

As a default policy, only compressed public keys are accepted in ``P2PKH`` and ``P2SH``. Each public key
passed to a sigop must be a compressed key: the first byte MUST be either ``0x02`` or ``0x03``, and the size
MUST be 33 bytes. Transactions that break this rule will not be relayed or mined by default.

Since this policy is preparation for a future softfork proposal, to avoid potential future funds loss, users
MUST NOT use uncompressed keys.


Example
=======

TBC


Deployment
==========

This proposal is deployed with the Overwinter network upgrade.


Backward compatibility
======================

This proposal is backwards-compatible with old UTXOs. It is **not** backwards-compatible with older software.
All transactions will be required to use this transaction digest algorithm for signatures, and so transactions
created by older software will be rejected by the network.


Reference Implementation
========================

TBC


References
==========

.. [#wiki-checksig] https://en.bitcoin.it/wiki/OP_CHECKSIG
.. [#quadratic]
   * `CVE-2013-2292 <https://web.nvd.nist.gov/view/vuln/detail?vulnId=CVE-2013-2292>`_
   * `New Bitcoin vulnerability: A transaction that takes at least 3 minutes to verify <https://bitcointalk.org/?topic=140078>`_
   * `The Megatransaction: Why Does It Take 25 Seconds? <http://rusty.ozlabs.org/?p=522>`_
.. [#offline-wallets] `SIGHASH_WITHINPUTVALUE: Super-lightweight HW wallets and offline data <https://bitcointalk.org/index.php?topic=181734.0>`_
.. [#ZIP0000] ZIP???: Overwinter Network Upgrade
.. [#01-change] In the original algorithm, a ``uint256`` of ``0x0000......0001`` is committed if the input
   index for a ``SINGLE`` signature is greater than or equal to the number of outputs. In this ZIP a
   ``0x0000......0000`` is commited, without changing the semantics.
