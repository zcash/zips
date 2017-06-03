**Title:** Cross-chain Atomic Transaction Standards

**Author:** Jay Graber

**Status:** Active

**Category:** Informational

**Created:** 2017-03-08

Abstract
===========

This is an Informational ZIP describing a proposed specification for a standardized protocol for performing cross-chain atomic transactions (XCAT) between Zcash and Bitcoin, or other Bitcoin-derived cryptocurrencies.

Motivation
===========

A well-defined standard for performing cross-chain transactions would improve the liquidity of cryptocurrencies and be useful for third-party services, such as decentralized exchanges.

Specification
===============

The proposed protocol for XCAT is a set of hash time-locked contracts across both chains, created by two parties who wish to do a cross-chain exchange.

The party that wishes to initiate an atomic swap will post a transaction to the counterparty with the amount they wish to exchange. This transaction can only be redeemed with the pre-image of a hash that's provided, and expires after a certain period of time (suggested duration is 48 hrs). We will call this step the "offerer challenge", because it is as though they have publicly posted a challenge that can only be redeemed with hidden information.

The other party in the exchange then creates a transaction with a 1 day time-lock, which can be redeemed by the first party if they provide the hash pre-image. This transaction expires after a shorter period of time (suggested duration is 24 hrs). We will call this step the "bidder challenge", because it is a response to the first that can only be redeemed if the party who initially offered to do the exchange accepts this price and completes the transaction.

The first party then redeems the bidder challenge by revealing the hash pre-image and spending the transaction. We will call this step the "offerer redemption", because the party who initially offered to do the exchange gets to redeem the funds they requested in this step.

The second party then redeems the offerer challenge by using the revealed hash pre-image to spend the first transaction. We will call this step the "bidder redemption", because the party who created a bid to fulfill the exchange gets the funds they requested in this step.

An example of this protocol is described below.

1. Alice sends 1 BTC to a p2sh transaction to Bob's address, with a 2 day time-lock, and with the hash of a random number R. This transaction will either time out, in which case the 1 BTC is never sent, or can be redeemed by Bob providing R
2. Bob sends 10 ZEC to a p2sh transaction to Alice's address, with a 1 day time-lock, and includes the hash of R. This transaction will either time out and never send, or will be redeemed Alice providing R, which should be a value only Alice knows and can redeem.
3. Alice spends the 10 ZEC from Bob's p2sh transaction to one of her addresses, revealing R in the process (her input's redeem script includes R)
4. Bob then spends the 1 BTC to one of his addresses, using the R revealed by Alice.

**Note:** The time-lock on Bob's transaction must be significantly shorter than the time-lock on Alice's, so that he can have enough time to use R to redeem his BTC from Alice's p2sh transaction. The redemptions can take place at any point within the timeout periods, so the transaction can happen quickly if both parties are immediately responsive and provide the correct information. The full duration of the timeout period for each transaction will only be applied in the fail case, where either Alice or Bob defaults on their agreement to exchange.


Rationale
===========

Users are free to come up with their own protocols for atomic swaps, but having a well-defined protocol would aid adoption and support third-party services wishing to provide such functionality.
