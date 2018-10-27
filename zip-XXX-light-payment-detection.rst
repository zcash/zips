::

  ZIP: XXX
  Title: Light Client Protocol for Payment Detection
  Authors: George Tankersley <gtank@z.cash>
           Jack Grigg <jack@z.cash>
  Credits: Matthew Green <mgreen@z.cash>
  Category: Standards Track
  Created: 2018-09-17
  License: MIT


Terminology
===========

The key words "MUST", "SHOULD", and "MAY" in this document are to be interpreted as
described in RFC 2119. [#RFC2119]_

The terms below are to be interpreted as follows:

Light client
  A client that is not a full participant in the network of Zcash peers. It can send and
  receive payments, but does not store or validate a copy of the blockchain.

Abstract
========

This proposal defines a protocol for a Zcash light client supporting Sapling shielded
transactions.

Motivation
==========

Currently a client that wishes to send or receive shielded payments must be a full node
participanting in the Zcash network. This requires an amount of available bandwidth,
space, and processing power that may be unsuitable for some classes of user. This light
client protocol addresses that need, and is appropriate for low-power,
bandwidth-conscious, or otherwise limited machines (such as mobile phones).

High-Level Design
=================

There are three logical components to a Zcash light client system:

- **Zcash node** that provides chain state and serves as a root of trust for the system.

- **Proxy server** that extracts blockchain data from zcashd to store and serve it in a
  lower-bandwidth format.

- **Light client** that subscribes to the stream from a proxy server and uses that data to
  update its own view of the chain state. The light client MAY be attached to a wallet
  backend that will track particular Sapling notes.

.. figure:: arch.png
    :align: center
    :figclass: align-center

    Outline of the light wallet architecture

Security Model
==============

In this model, we propose **payment detection privacy** as our main security goal. That
is, the proxy should not learn which transactions (received from the blockchain) are
addressed to a given light wallet. If we further assume network privacy (via Tor or
similar), the proxy should not be able to link different connections or queries as
deriving from the the same wallet.

In particular, the underlying Zcash node / proxy combination is assumed to be "honest but
curious" and is trusted to provide a correct view of the current best chain state and to
faithfully transmit queries and responses. Methods for weakening this assumption are
discussed in appendix FOO.

This ZIP does not address how to spend notes privately.

Compact Stream Format
=====================

A key observation in this protocol is that the current zcashd encrypted field is several
hundred bytes long, due to the inclusion of a transaction “memo”. The need to download
this entire field imposes a substantial bandwidth cost on each light wallets, which may be
a limited mobile device on a restricted-bandwidth plan. While more efficient techniques
can be developed in the future, for the moment we propose ignoring the memo field during
payment detection. Futhermore, we can also ignore any information that is not directly
relevant to a Sapling shielded transaction.

A **compact block** is a packaging of ONLY the data from a block needed to:

1. Detect a payment to your shielded Sapling address
2. Detect a spend of your shielded Sapling notes
3. Update your witnesses to generate new Sapling spend proofs.

A compact block and its component compact transactions are encoded on the wire using the
following Protocol Buffers [XXX] format:

.. code:: proto

    message BlockID {
         uint64 blockHeight = 1;
         bytes blockHash = 2;
    }

    message CompactBlock {
        BlockID id = 1;
        repeated CompactTx vtx = 3;
    }

    message CompactTx {
        uint64 txIndex = 1;
        bytes txHash = 2;

        repeated CompactSpend spends = 3;
        repeated CompactOutput outputs = 4;
    }

    message CompactSpend {
        bytes nf = 1;
    }

    message CompactOutput {
        bytes cmu = 1;
        bytes epk = 2;
        bytes ciphertext = 3;
    }

Encoding Details
----------------

``blockHash``, ``txHash``, ``nf``, ``cmu``, and ``epk`` are encoded as
specified in the Zcash Protocol Spec.

The output and spend descriptions are handled differently, as described in the following
sections.

Output Compression
------------------

In the normal Zcash protocol, the output ciphertext consists of the AEAD encrypted form of
a *note plaintext* [Note]:

+------------+----------+----------+-------------+-----------------------------------+
| 8-bit 0x01 | 88-bit d | 64-bit v | 256-bit rcm | memo (512 bytes) + tag (16 bytes) |
+------------+----------+----------+-------------+-----------------------------------+

A recipient detects their transactions by trial-decrypting this ciphertext. On a full node
that has the entire block chain, the primary cost is computational. For light clients
however, there is an additional bandwidth cost: every ciphertext on the block chain must
be received from the server (or network node) the light client is connected to. This
results in a total of 580 bytes per output that must be streamed to the client.

However, we don't need all of that just to detect payments. The first 52 bytes of the
ciphertext contain the contents and opening of the note commitment, which is all of the
data needed to spend the note and to verify that the note is spendable. If we ignore the
memo and the authentication tag, we're left with a 32-byte ephemeral key, the 32-byte note
commitment, and only the first 52 bytes of the ciphertext for each output needed to
decrypt, verify, and spend a note. This totals to 116 bytes per output, for an 80%
reduction in bandwidth use.

However, skipping the full ciphertext means that we can no longer calculate the
authentication tag for the entire ciphertext and will need to do something else to
validate the integrity of the decrypted note plaintext.

Since the note commitment is sent outside the ciphertext and is authenticated by the
binding signature over the entire transaction, it serves as an adequate check on the
validity of the decrypted plaintext (assuming you trust the entity assembling
transactions). We therefore recalculate the note commitment from the decrypted plaintext.
If the recalculated commitment matches the one in the output, we accept the note as valid
and spendable.

Spend Compression
-----------------

Recall that a full Sapling Spend description is 384 bytes long [Spend]:

+-------+--------------+-----------+
| Bytes | Name         | Type      |
+=======+==============+===========+
| 32    | cv           | char[32]  |
+-------+--------------+-----------+
| 32    | anchor       | char[32]  |
+-------+--------------+-----------+
| 32    | nullifier    | char[32]  |
+-------+--------------+-----------+
| 32    | rk           | char[32]  |
+-------+--------------+-----------+
| 192   | zkproof      | char[192] |
+-------+--------------+-----------+
| 64    | spendAuthSig | char[64]  |
+-------+--------------+-----------+

The only part necessary for detection is the nullifier, which allows a light client to
detect when one of its own notes has been spent. This means we only need to take 32 bytes
of each Spend, for a 90% improvement in bandwidth use.

Proxy operation
===============

The proxy's purpose is to provide a scalable and bandwidth-efficient interface between a
Zcash node and any number of light clients. It accomplishes this by parsing a blockwise
stream of transactions from the node and converting them into the compact format described
above.

The proxy offers the following API to clients:

.. code:: proto

    service CompactTxStreamer {
        rpc GetLatestBlock(ChainSpec) returns (BlockID) {}
        rpc GetBlock(BlockID) returns (CompactBlock) {}
        rpc GetBlockRange(RangeFilter) returns (stream CompactBlock) {}
        rpc GetTransaction(TxFilter) returns (FullTransaction) {}
    }

    // Remember that proto3 fields are all optional.

    // Someday we may want to specify e.g. a particular chain fork.
    message ChainSpec {}


    // A BlockID message contains identifiers to select a block: either a
    // height or a hash.
    message BlockID {
        uint64 blockHeight = 1;
        bytes blockHash = 2;
    }


    message RangeFilter {
        BlockID start = 1;
        BlockID end = 2;
    }

    // A TxFilter contains the information needed to identify a particular
    // transaction: either a block and an index, or a direct transaction hash.
    message TxFilter {
        BlockID blockID = 1;
        uint64 txIndex = 2;
        bytes txHash = 3;
    }


Client operation
================

Light clients obtain compact blocks from one or more proxy servers, which they then
process locally to update their view of the block chain. We consider only a single proxy
server here without loss of generality.

Local processing
----------------

Given a ``CompactBlock`` received in height-sequential order from a proxy server, a light
client can process it in three ways:

Scanning for relevant transactions
``````````````````````````````````
For every ``CompactOutput`` in the ``CompactBlock``, the light client can trial-decrypt it
against a set of Sapling incoming viewing keys. The procedure for trial-decrypting a
``CompactOutput`` (*cmu*, *epk*, *ciphertext*) with an incoming viewing key *ivk* is a
slight deviation from the standard decryption process [#sapling-ivk-decryption]_:

- let sharedSecret = KA\ :sup:`Sapling`\ .Agree(*ivk*, *epk*)
- let K\ :sup:`enc` = KDF\ :sup:`Sapling`\ (sharedSecret, *epk*)
- let P\ :sup:`enc` = ChaCha20.Decrypt\ :sub:`K^enc`\ (*ciphertext*)
- extract **np** = (d, v, rcm) from P\ :sup:`enc`
- let rcm = LEOS2IP\ :sub:`256`\ (rcm) and g\ :sub:`d` = DiversifyHash(d)
- if rcm >= r\ :sub:`J` or g\ :sub:`d` = ⊥, return ⊥
- let pk\ :sub:`d` = KASapling.DerivePublic(ivk, g\ :sub:`d`\ )
- let cm\ :sub:`u`\ ' = Extract\ :sub:`J^(r)`\ (NoteCommitSapling\ :sub:`rcm^new`\ (repr\ :sub:`J`\ (g\ :sub:`d`\ ), repr\ :sub:`J`\ (pk\ :sub:`d`\ ), v)).
- if LEBS2OSP\ :sub:`256`\ (cm\ :sub:`u`\ ') != *cmu* , return ⊥, else return **np**.

Creating and updating note witnesses
````````````````````````````````````

As ``CompactBlocks`` are received in-order, the *cmu* values in each ``CompactOutput`` can
be sequentially appended to a Sapling commitment Merkle tree. This can then be used to
create and cache incremental witnesses.

Detecting spends
````````````````

The ``CompactSpend`` entries can be checked against known local nullifiers, to for example
ensure that a transaction has been received by the network and mined.

Client-server interaction
-------------------------

We can divide the typical client-server interaction into four distinct phases:

.. code:: text

    Phase   Client                Server
    =====   ============================
      A     GetLatestBlock ------------>

            <---------------- BlockID(X)

            GetBlock(X) --------------->

            <----------- CompactBlock(X)

                ===

      B     GetLatestBlock ------------>

            <---------------- BlockID(Y)

            GetBlockRange(X, Y) ------->

            <--------- CompactBlock(X)
            <--------- CompactBlock(X+1)
            <--------- CompactBlock(X+2)
                            ...
            <--------- CompactBlock(Y-1)
            <--------- CompactBlock(Y)

                ===

      C     GetTransaction(X+4, 7) ---->

            <--- FullTransaction(X+4, 7)

            GetTransaction(X+9, 2) ---->

            <--- FullTransaction(X+9, 2)

                ===

      D     GetLatestBlock ------------>

            <---------------- BlockID(Z)

            GetBlockRange(Y, Z) ------->

            <--------- CompactBlock(Y)
            <--------- CompactBlock(Y+1)
            <--------- CompactBlock(Y+2)
                            ...
            <--------- CompactBlock(Z-1)
            <--------- CompactBlock(Z)

**Phase A:** The light client starts up for the first time.

- The light client queries the server to fetch the most recent block ``X``.
- The light client queries the commitment tree state for block ``X``.

  - Or, it has to set ``X`` to the block height at which Sapling activated, so as to be
    sent the entire commitment tree. [TODO: Decide which to specify.]

- Shielded addresses created by the light client will not have any relevant transactions
  in this or any prior block.

**Phase B:** The light client updates its local chain view for the first time.

- The light client queries the server to fetch the most recent block ``Y``.
- It then executes a block range query to fetch every block between ``X`` (inclusive) and
  ``Y`` (inclusive).
- The block at height ``X`` is checked to ensure the received ``blockHash`` matches the
  light client's cached copy, and then discards it without further processing.

  - An inconsistency would imply that block ``X`` was orphaned during a chain reorg.

- As each subsequent  ``CompactBlock`` arrives, the light client scans it to find any
  relevant transactions for addresses generated since ``X`` was fetched (likely the first
  transactions involving those addresses). If notes are detected, it:

  - Generates incremental witnesses for the notes, and updates them going forward.
  - Scans for their nullifiers from that block onwards.

**Phase C:** The light client has detected some notes and displayed them. User interaction
has indicated that the corresponding full transactions should be fetched.

- The light client queries the server for each transaction it wishes to fetch.

**Phase D:** The user has spent some notes. The light client updates its local chain view
some time later.

- The light client queries the server to fetch the most recent block ``Z``.
- It then executes a block range query to fetch every block between ``Y`` (inclusive) and
  ``Z`` (inclusive).
- The block at height ``Y`` is checked to ensure the received ``blockHash`` matches the
  light client's cached copy, and then discards it without further processing.

  - An inconsistency would imply that block ``Y`` was orphaned during a chain reorg.

- As each subsequent ``CompactBlock`` arrives, the light client:

  - Updates the incremental witnesses for known notes.
  - Scans for any known nullifiers. The corresponding notes are marked as spent at that
    height, and excluded from further witness updates.
  - Scans for any relevant transactions for addresses generated since ``Y`` was fetched.
    These are handled as in phase B.

Importing a pre-existing seed
`````````````````````````````
Phase A of the interaction assumes that shielded addresses created by the light client
will have never been used before. This is not a valid assumption if the light client is
being initialised with a seed that it did not generate (e.g. a previously backed-up seed).
In this case, phase A is modified as follows:

**Phase A:** The light client starts up for the first time.

- The light client sets ``X`` to the block height at which Sapling activated.

  - Shielded addresses created by any light client cannot have any relevant transactions
    prior to Sapling activation.

Block privacy via bucketing
---------------------------

The above interaction reveals to the server at the start of each synchronisation phase (B
and D) the block height which the light client had previously synchronised to. This is an
information leak under our security model (assuming network privacy). We can reduce the
information leakage by "bucketing" the start point of each synchronisation. Doing so also
enables us to handle most chain reorgs simultaneously.

Let ``⌊X⌋ = X - (X % N)`` be the value of ``X`` rounded down to some multiple of the
bucket size ``N``. The synchronisation phases from the above interaction are modified as
follows:

.. code:: text

    Phase   Client                Server
    =====   ============================
      B     GetLatestBlock ------------>

            <---------------- BlockID(Y)

            GetBlockRange(⌊X⌋, Y) ----->

            <-------- CompactBlock(⌊X⌋)
            <-------- CompactBlock(⌊X⌋+1)
            <-------- CompactBlock(⌊X⌋+2)
                            ...
            <-------- CompactBlock(Y-1)
            <-------- CompactBlock(Y)

                ===

      D     GetLatestBlock ------------>

            <---------------- BlockID(Z)

            GetBlockRange(⌊Y⌋, Z) ----->

            <-------- CompactBlock(⌊Y⌋)
            <-------- CompactBlock(⌊Y⌋+1)
                            ...
            <-------- CompactBlock(Z-1)
            <-------- CompactBlock(Z)

**Phase B:** The light client updates its local chain view for the first time.

- The light client queries the server to fetch the most recent block ``Y``.
- It then executes a block range query to fetch every block between ``⌊X⌋`` (inclusive)
  and ``Y`` (inclusive).
- Blocks between ``⌊X⌋`` and ``X`` are checked to ensure that the received ``blockHash``
  matches the light client's chain view for each height, and are then discarded without
  further processing.

  - If an inconsistency is detected at height ``Q``, the light client sets ``X = Q-1``,
    discards all local blocks with height ``>= Q``, and rolls back the state of all local
    transactions to height ``Q-1`` (un-mining them as necessary).

- Blocks between ``X+1`` and ``Y`` are processed as before.

**Phase D:** The user has spent some notes. The light client updates its local chain view
some time later.

- The light client queries the server to fetch the most recent block ``Z``.
- It then executes a block range query to fetch every block between ``⌊Y⌋`` (inclusive)
  and ``Z`` (inclusive).
- Blocks between ``⌊Y⌋`` and ``Y`` are checked to ensure that the received ``blockHash``
  matches the light client's chain view for each height, and are then discarded without
  further processing.

  - If an inconsistency is detected at height ``R``, the light client sets ``Y = R-1``,
    discards all local blocks with height ``>= R``, and rolls back the following local
    state to height ``R-1``:

    - All local transactions (un-mining them as necessary).
    - All tracked nullifiers (unspending or discarding as necessary).
    - All incremental witnesses (caching strategies are not covered in this ZIP).

- Blocks between ``Y+1`` and ``Z`` are processed as before.

Transaction privacy
-------------------

The synchronisation phases give the light client sufficient information to determine
accurate address balances, show when funds were received or spent, and spend any unspent
notes. As synchronisation happens via a broadcast medium, it leaks no information about
which transactions the light client is interested in.

If, however, the light client needs access to other components of a transaction (such as
the memo fields for received notes, or the outgoing ciphertexts in order to recover spend
information when importing a wallet seed), it will need to download the full transaction.
The light client SHOULD obscure the exact transactions of interest by downloading numerous
uninteresting transactions as well, and SHOULD download all transactions in any block from
which a single full transaction is fetched (interesting or otherwise). It MUST convey to
the user that fetching full transactions will reduce their privacy.

Appendix FOO
============

You can require the proxy to give you all the block headers to validate.

Reference Implementation
========================

This proposal is supported by a set of libraries and reference code made available by the
Zcash Company.

[NOTE: 2018-09-17 WE HAVE NOT YET FINISHED OR RELEASED THESE.]

References
==========

.. [#RFC2119] `Key words for use in RFCs to Indicate Requirement Levels <https://tools.ietf.org/html/rfc2119>`_

[ZEC] Zcash Protocol Spec

[bipXXX] define a light client

[XXX] protobufs

[Note] [ZEC] Section 5.5

[Spend] [ZEC] Section 7.x

[Output] [ZEC] Section 7.x

.. [#sapling-ivk-decryption] `Section 4.17.2: Decryption using an Incoming Viewing Key (Sapling). Zcash Protocol Specification, Version 2018.0-beta-31 or later [Overwinter+Sapling] <https://github.com/zcash/zips/blob/master/protocol/protocol.pdf>`_
