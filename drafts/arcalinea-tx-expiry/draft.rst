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

Transactions that are too large or have insufficient fees are often not mined. This indeterminism is a source of confusion for users and wallets. Allowing transactions to set a block height or timestamp after which it expires from the mempool would provide certainty around how long a transaction has to confirm before it is rejected by the network and must be re-sent.

Advantages include improving performance by removing transactions unlikely to be mined, and potentially simplifying bidirectional payment channels by reducing the need to store and compress revocations for past states, since transactions not committed to the chain could expire and become invalid after a period of time.

Specification
===============

Transactions will have a new field, nExpiryTime, which will set the block height or UNIX timestamp after which transactions will be removed from the mempool if they have not been mined.

The data type for nExpiryTime will be uint32_t, conforming to the structure of nLockTime. If used in combination with nLockTime, both nLockTime and nExpiryTime must be the same unit (either block height or timestamp).

For the example below, the last block that the transaction below could possibly be included in is 3539. After that, it will be removed from the mempool.

````
"txid": "17561b98cc77cd5a984bb959203e073b5f33cf14cbce90eb32b95ae2c796723f",
"version": 3,
"locktime": 2089,
"blockexpiry": 3539,
```

Default: nExpiryTime defaults to 0, which means transaction does not expire, preserving current behavior.
Minimum: When nExpiryTime is set, it must be at least 60 blocks greater than the current blockheight, or 2 hrs greater than LOCKTIME_MEDIAN_TIME_PAST. This is because of the safety thresholds specified below.
Maximum: No maximum specified, although based on the highest timestamp available for uint32 numbers, nExpiryTime becomes meaningless after the year 2106.

Timeline of expiration safety thresholds
-----------------------------------------

2 hours before a transaction is set to expire, other nodes stop relaying it.
1 hour before expiring, CreateNewBlock does not include the tx anymore. This is in case mining software changes the timestamp afterwards, resulting in the mining of an invalid block that contains expired transactions.
1 hour after expiring, wallet marks the transaction as expired and frees the coins.

Another reason to set a minimum expiration period is to mitigate the use of this feature as a spam mechanism.

Upon block reorganization
--------------------------

Transactions that are confirmed close to the end of their expiry period may be dropped from the mempool upon a block reorg, which could leave dependent transactions stranded in the mempool. Therefore, each time an expired transaction is removed from the mempool, a check must be added to remove its dependent transactions as well.

Wallet behavior and UI
-----------------------

With the addition of this feature, zero-confirmation transactions with an expiration block height set will have even less guarantee of inclusion. This means that UIs and services must never rely on zero-confirmation transactions in Zcash.

Wallet should notify user of expired transactions that must be re-sent.

Wallet should notify user and reject the creation of a transaction that builds on a transaction with zero confirmations and an expiry blockheight set.

RPC
-----
listtransactions has a new filter attribute, showing expired transactions only:
    listtransactions "*" 10 0 "expired"

WalletTxToJSON shows a boolean expired true/false

Notify
--------

-expirenotify= can notify an external script when a wallet transaction expires
