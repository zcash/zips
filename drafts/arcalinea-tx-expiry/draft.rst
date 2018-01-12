**Title:** Transaction Expiry

**Author:** Jay Graber

**Status:** Active

**Category:** Standards

**Created:** 2018-01-09

Abstract
===========

This is an Standards ZIP describing a new consensus rule to set an expiration time for transactions that are not mined to be removed from the mempool.

Motivation
===========

Transactions that are too large or have insufficient fees are often not mined. This indeterminism is a source of confusion for users and wallets. Allowing transactions to set a block height after which it expires from the mempool would provide certainty around how long a transaction has to confirm before it is rejected by the network and must be re-sent.

Advantages include improving performance by removing transactions unlikely to be mined, and potentially simplifying bidirectional payment channels by reducing the need to store and compress revocations for past states, since transactions not committed to the chain could expire and become invalid after a period of time.

Specification
===============

Transactions will have a new field, nBlockExpiry, which will set the block height after which transactions will be removed from the mempool if they have not been mined.

The data type for nBlockExpiry will be uint32_t, conforming to the structure of nLockTime. If used in combination with nLockTime, both nLockTime and nBlockExpiry must be block heights.

For the example below, the last block that the transaction below could possibly be included in is 3539. After that, it will be removed from the mempool.

````
"txid": "17561b98cc77cd5a984bb959203e073b5f33cf14cbce90eb32b95ae2c796723f",
"version": 3,
"locktime": 2089,
"blockexpiry": 3539,
```

Default: TBD. One suggestion is 576 blocks, or about 1 day assuming 2.5 minute block times. Can add a config option to set user's default.
Minimum: No minimum
Maximum: 500000000, about 380 years
No limit: To set no limit on transactions (so that they do not expire), nBlockExpiry should be set to UINT_MAX.  


Upon block reorganization
--------------------------

Transactions that are confirmed close to the end of their expiry period may be dropped from the mempool upon a block reorg, which could leave dependent transactions stranded in the mempool. Therefore, each time an expired transaction is removed from the mempool, a check must be added to remove its dependent transactions as well.

Wallet behavior and UI
-----------------------

With the addition of this feature, zero-confirmation transactions with an expiration block height set will have even less guarantee of inclusion. This means that UIs and services must never rely on zero-confirmation transactions in Zcash.

Wallet should notify user of expired transactions that must be re-sent. See "Notify" section below.

Wallet should notify user and reject the creation of a transaction that builds on a transaction with zero confirmations and an expiry blockheight set.

RPC
-----
To use:
To make changes to the sendtoaddress and z_sendmany commands backwards compatible for future changes, keyword arguments should be accepted by the RPC interface. Since this is not consensus critical behavior, it can be added in a future release. For Overwinter, tx expiry will be set to a default that can be overridden by a flag `txexpirydefault` set in the config file.

-txexpirydefault= set default for tx expiry

To view:
listtransactions has a new filter attribute, showing expired transactions only:
    listtransactions "*" 10 0 "expired"

WalletTxToJSON shows a boolean expired true/false

Notify
-------

-expirenotify= can notify an external script when a wallet transaction expires
