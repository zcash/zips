**Title:** Transaction Expiry

**Author:** Jay Graber

**Status:** Active

**Category:** Standards

**Created:** 2018-01-09

Abstract
===========

This is an Standards ZIP describing a new consensus rule to expire transactions that are not mined from the mempool.

Motivation
===========

Transactions that are too large or have insufficient fees are often not mined. This indeterminism is a source of confusion for users and wallets. Giving users the ability to specify the number of blocks a transaction should sit in the mempool before it expires, and otherwise setting a default, would provide certainty around how long a transaction has to confirm.

Advantages include improving performance by removing transactions unlikely to be mined, and simplifying bidirectional payment channels by reducing the need to store and compress revocations for past states since transactions are allowed to expire.

Specification
===============

Transactions will have a new field, nBlockExpiry, which will set the blockheight after which transactions will be removed from the mempool if they have not been mined. The last block that the transaction below could possibly be included in is 3539. After that, it will be removed from the mempool.

````
"txid": "17561b98cc77cd5a984bb959203e073b5f33cf14cbce90eb32b95ae2c796723f",
"version": 3,
"locktime": 2089,
"blockexpiry": 3539,
```

With the addition of this feature, zero-confirmation transactions with an expiration blockheight set will have even less guarantee of inclusion. This means that UIs and services must never rely on zero-confirmation transactions in Zcash.

Default behavior
-----------------

Default behavior does not change -- transactions do not expire. (Alternative proposal is to set a default expiry period of 2 days, ~1440 blocks.) When nBlockExpiry is set to 0, the transaction will not expire from the mempool.

If used in combination with nLockTime, nLockTime must be a blockheight, and nBlockExpiry must be higher. To simplify this feature, we could disallow its use in conjunction with nLockTime.

Upon block reorg
-----------------

Transactions that are confirmed close to the end of their expiry period may be dropped from the mempool upon a block reorg, which could leave dependent transactions stranded in the mempool. Therefore, each time an expired transaction is removed from the mempool, a check must be added to remove its dependent transactions as well.

Wallet behavior and UI
-----------------------

Wallet should notify user of expired transactions that must be re-sent.

Wallet should notify user and reject the creation of a transaction that builds on a transaction with zero confirmations and an expiry blockheight set.

RPC interface
--------------

sendtoaddress will allow the user to easily set a blockheight for the transaction to expire.

sendtoaddress "zcashaddress" amount ( blockexpiry "comment" "comment-to" subtractfeefromamount )
