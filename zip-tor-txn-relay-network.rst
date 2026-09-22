::

  ZIP: ??? <TTRN>
  Title: The Zcash Tor Transaction Relay Network
  Owners: Nathan Wilcox <nathan@electriccoin.co>
  Credits: 
  Status: Proposed
  Category: Application Standard
  Created: 2020-08-12
  License: MIT


Terminology
===========

The key words "MUST", "SHOULD", and "OPTIONAL" in this document are to be interpreted
as described in RFC 2119. [#RFC2119]_

The term "network upgrade" in this document is to be interpreted as described in ZIP 200
[#zip-0200]_.

The term "Sapling" in this document is to be interpreted as described in ZIP 205
[#zip-0205]_.

The term "Sprout value pool balance" in this document is to be interpreted as described
in ZIP 209 [#zip-0209]_.


Abstract
========

The Zcash `Tor Transaction Relay Network` (`TTRN`) is an auxillary Zcash protocol to improve network privacy of wallets which issue transactions. TTRN `Service Providers` publish a `Service Descriptor` to a well-known Wishing Well (see [FIXME link to zip-wishing-well]), which includes a `registration fee` paid into the well (ie burned). TTRN-enabled wallets subscribe to that Wishing Well to discover Providers. When sending a shielded transaction the wallet selects a random provider, connects to it over Tor, and delivers the transaction via a TTRN-specific `Delivery Protocol`. These transactions pay `TTRN service fees` to providers.

As an auxillary protocol, it is transparent and backwards compatible with the Zcash P2P protocol and consensus layer, and it is also opt-in for wallet usage. Light wallets, as well as full-node wallets, may be able to protect an important aspect of their privacy from hosted service providers with this protocol.

Motivation
==========

When wallets generate transactions they must transmit them to the Zcash network, and this initial transmission is a weak point for Zcash network privacy: it is possible for network peers to determine which node originated a transaction, even when the P2P protocol is routed over Tor [#]. By associating two different fully shielded transactions with the same originating peer, those transactions are linked by this network metadata, thereby violating a key privacy property that Zeroknowledge proofs protect against on-chain analysis. When a peer does not route its P2P traffic over Tor, this association can also include an IP address, which can reveal some information about the physical location of the wallet.

.. [#] This assertion is an educated bet by the author. FIXME: find published research or supporting evidence to back up this claim.

For mobile light wallets, the originating peer analysis above typically identifies the mobile wallet service provider's peer. Mobile wallets are even more directly vulnerable to their hosting provider in typical deployment architectures, because those hosting providers relay all of a wallet's transactions, and the hosting provider can trivially link those transactions and furthermore typically have more information about the mobile wallet and its user.

This protocol aims to protect the association of which transactions originate with which peers, because each transaction arrives to a random TTRN provider via a new fresh Tor circuit with no history. This may potentially also protect the association of which transactions originate with which mobile light wallets against analysis by mobile wallet service providers.

Design Goals
============

TODO: refine this section to be more precise/complete.

- Protect linkage between wallets and the transactions they originate.
- Providers don't learn anything about the recipient addresses, amounts, memos, or change in a relayed transaction except for the single output amount & memo used to pay for the service.
- Opt-in for wallets.
- Feasible for mobile light clients.
- Auxillary protocol requiring no changes to the Zcash P2P protocol or consensus rules.
- Incentivize providers via revenue stream.
- Disincentivize attacker control of a large proportion of the provider network via registration fees.

Non-Goals
---------

- Protecting the network topological location of providers. (Anyone may determine a transaction first reaches the P2P network from a provider.)
- Protecting providers from "service identification": anyone may determine a node is a TTRN provider based on its txn emission patterns.
- Protecting against network attacks which Tor is vulnerable against.
- Varied / self-set provider fees; service fee and registration fee are the same for all participants.
- Dynamic fee adjustments; the fee schedules are manually set for simplicity, even though that may lead to suboptimal resource deployment.

Specification
=============

- `Address Pairs` are a pair of the Provider's `Sapling Address` and `Tor Hidden Service`.
- The Tor Hidden Service connects to the Provider's `TTRN Relay Protocol` server.
- A Provider periodically `registers` their Address Pair by sending a memo to the `TTRN Wishing Well` which pays at least `Registration Fee` into the well. This is called a `Registration`.
- A `Registration` is `active` when it pays at least `Registration Fee` into the well, and it is in a block with at least `REGISTRATION_MIN_CONF` confirmations up until `REGISTRATION_MAX_CONF`.
- A Wallet observes all registrations with the `Wishing Well Viewing Key` and maintains them into a list.
- The wallet `deduplicates` the list as follows:
    - Remove any registration that's not `active`.
    - Where the same `Sapling Address` appears multiple times, remove all but the earliest entry (with the lowest block height).
    - Where the same `Tor Hidden Service` appears multiple times, remove all but the earliest entry.
- When a Wallet intends to send a shielded transfer, it:
    - Selects a uniformly random entry in the `deduplicated list`. Wallets must use uniform random selection and not rely on local information such as how reliable a provider is.
    - Includes a Sapling Shielded Output to the given Sapling Address transferring at least `Relay Fee` ZEC. The memo field must be empty and is reserved.
    - Generates necessary proofs and signs the complete transaction.
    - Connects to the hidden service and executes the `TTRN Relay Protocol` as a client.
- When a provider receives a transaction via the Hidden Service TTRN Relay Protocol service, it decodes the transfer to its Sapling Address.
    - If the fee paid is at least `Relay Fee`, it submits the transaction to the Zcash network vai the P2P protocol.
    - If the fee paid is less, it drops the transaction.

Security Considerations
=======================

TODO

- unfinished thoughts:
    - what is different in privacy protections for wallets between there being 1 provider versus k providers who do not share information? Or maybe a better framing: p providers are malicious and 1-p are not.
    - malicious providers can passively surveil, but what else can they do? Drop selected transactions?
    - All of my thinking so far has assumed fully shielded transactions. What about partially shielded transactions?

Economic Considerations
=======================

TODO: refine/harden/analyze these:

- We call the total number of transactions routed through TTRN in a given time period times the relay fee is `aggregate revenue`.
- Since active providers are chosen uniformly randomly, the `expected revenue per provider` (aka `ERPP`) in the time period is `aggregate revenue` / `number of registrations`.
- Over time, given stable conditions like a stable transaction rate, we expect the number of providers will increase or decrease such that `ERPP` + `non-financial incentive` + `out-of-band financial incentives` = `Total Cost for Service` + `epsilon` for providers.
    -  We include `non-financial incentive` to capture the notion that some providers may have other incentives to overcome excessive costs, such as the altruism of improving privacy for users or to execute an attack on privacy. However, we posit that over long enough time frames the non-financial incentives will tend towards 0 or else the providers become bankrupt and cannot continue.
    - We include `out-of-band financial incentives` to capture cases where providers earn other revenue in connection to their service that isn't in the scope of this protocol. For example, as long as a charity pays providers for their service separately from txn fees, this can tip the balance financially for those providers.
- The system is economically sustainable when:
    - for a given transaction, the `relay fee` is worth less than the additional privacy for a user, and
    - that implies that the number of independent providers is large enough to meet the user's privacy threshold, and
    - the aggregate rate of such transactions is large enough to fund enough independent providers.
- If any of those three do not hold, the system is not sustainable:
    - If the additional privacy isn't worth at least `relay fee` for enough transactions, possibly because:
    - there aren't enough independent providers to 

Deployment
==========

TODO


Reference Implementation
========================

TODO


References
==========

TODO
