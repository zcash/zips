::

  ZIP: Unassigned
  Title: Addressing mempool denial-of-service
  Owners: Daira Hopwood <daira@electriccoin.co>
  Status: Draft
  Category: Network
  Created: 2019-09-09
  License: MIT


Terminology
===========

The key words "MUST", "SHOULD", and "MAY" in this document are to be interpreted
as described in RFC 2119. [#RFC2119]_


Abstract
========

This proposal specifies a change to the behaviour of zcashd nodes intended to
mitigate denial-of-service from transaction flooding.


Motivation
==========

Adoption of this proposal would increase robustness of Zcash nodes against
denial-of-service attack, in particular attacks that attempt to exhaust node
memory.

Bitcoin Core added size limitation for the mempool in version 0.12
[#BitcoinCore-PR6722]_, defaulting to 300 MB. This was after Zcash forked from
Bitcoin Core.


Requirements
============

The memory usage of a node’s mempool should be bounded.

The eviction policy should as far as possible not be “gameable” by an adversary,
i.e. an adversary should not be able to cause legitimate transactions (that do not
themselves present any denial-of-service problem) to be preferentially evicted
relative to its own transactions.

Any configuration options should have reasonable defaults, i.e. without changing
relevant configuration, a node should be adequately protected from denial-of-service
via mempool memory exhaustion.


Non-requirements
================

The current architecture of Zcash imposes fundamental limits on scaling of
transaction throughput. This proposal does not increase the aggregate transaction
capacity of the network. (The Blossom upgrade does increase transaction capacity,
by a factor of two [#zip-0208]_.)

Denial-of-service issues in the messaging layer of the peer-to-peer protocol are
out of scope for this proposal.

This proposal is focused primarily on memory exhaustion attacks. It does not
attempt to use fees to make denial-of-service economically prohibitive, since that
is unlikely to be feasible while maintaining low fees for legitimate users. It
does not preclude changes in fee policy.


Specification
=============

This specification describes the intended behaviour of zcashd nodes. Other node
implementations MAY implement the same or similar behaviour, but this is not a
requirement of the network protocol. Thus, RFC 2119 conformance keywords below are
to be interpreted only as placing requirements on the zcashd implementation (and
potentially other implementations that have adopted this specification in full).

The mempool of a node holds a set of transactions. Each transaction has a cost,
which is an integer defined as:

  max(serialized transaction size in bytes, 4000) + fee_penalty

where ``fee_penalty`` is 16000 if the transaction pays a fee less than
10000 zatoshi, otherwise 0.

Each node also MUST hold a FIFO queue RecentlyEvicted of pairs (txid, time), where
the time indicates when the given txid was evicted. This SHOULD be empty on node
startup. The size of RecentlyEvicted MUST never exceed 10000 entries.

There MUST be a configuration option ``mempool.tx_cost_limit``, which SHOULD default
to 80000000.

There MUST be a configuration option ``mempool.eviction_memory_minutes``, which
SHOULD default to 60.

On receiving a transaction:

* If it is in RecentlyEvicted, the transaction MUST be dropped.
* Calculate its cost. If the total cost of transactions in the mempool including
  this one would exceed ``mempool.tx_cost_limit``, then the node MUST repeatedly
  call EvictTransaction (with the new transaction included as a candidate to evict)
  until the total cost does not exceed ``mempool.tx_cost_limit``.

EvictTransaction MUST do the following:

* Select a random transaction to evict, weighted by cost.
* Add the txid and the current time to RecentlyEvicted, dropping the oldest entry
  in RecentlyEvicted if necessary to keep it to at most 10000 entries.
* Remove it from the mempool.

Nodes SHOULD remove transactions from RecentlyEvicted that were evicted more than
``mempool.eviction_memory_minutes`` minutes ago. This MAY be done periodically,
and/or just before RecentlyEvicted is accessed when receiving a transaction.


Rationale
=========

The accounting for transaction size should include some overhead per transaction,
to reflect the cost to the network of processing them (proof and signature
verification; networking overheads; size of in-memory data structures). The
implication of not including overhead is that a denial-of-service attacker would
be likely to use minimum-size transactions so that more of them would fit in a
block, increasing the unaccounted-for overhead. A possible counterargument would
be that the complexity of accounting for this overhead is unwarranted given that
the format of a transaction already imposes a minimum size. However, the proposed
cost function is almost as simple as using transaction size directly.

The threshold 4000 for the cost function is chosen so that the size in bytes of a
typical fully shielded Sapling transaction (with, say, 2 shielded outputs and up
to 5 shielded inputs) will fall below the threshold. This has the effect of
ensuring that such transactions are not evicted preferentially to typical
transparent transactions because of their size.

The proposed eviction policy differs significantly from that of Bitcoin Core
[#BitcoinCore-PR6722]_, which is primarily fee-based. This reflects differing
philosophies about the motivation for fees and the level of fee that legitimate
users can reasonably be expected to pay. The proposed cost function does involve
a penalty for transactions with a fee lower than the standard (0.0001 ZEC) value,
but since there is no further benefit to increasing the fee above the standard
value, it creates no pressure toward escalating fees. For transactions up to
4000 bytes, this penalty makes a transaction that pays less than the standard fee
value five times as likely to be chosen for eviction.

The default value of 80000000 for ``mempool.tx_cost_limit`` represents no more
than 40 blocks’ worth of transactions in the worst case, which is the default
expiration height after Blossom network upgrade [#zip-0208]_. It would serve no
purpose to make it larger.

The ``mempool.tx_cost_limit`` is a per-node configurable parameter in order to
provide flexibility for node operators to change it either in response to
attempted denial-of-service attacks, or if needed to handle spikes in transaction
demand. It may also be useful for nodes running in memory-constrained environments
to reduce this parameter.

The limit of 100000 entries in RecentlyEvicted bounds the memory needed for this
data structure. Since a txid is 32 bytes and a timestamp 8 bytes, 100000 entries
can be stored in ~4 MB, which is small compared to other node memory usage (in
particular, small compared to the maximum memory usage of the mempool itself under
the default ``mempool.tx_cost_limit``). 100000 entries should be sufficient to
mitigate any performance loss caused by re-accepting transactions that were 
previously evicted. In particular, since a transaction has a minimum cost of 1000,
and the default ``mempool.tx_cost_limit`` is 80000000, at most 80000 transactions
can be in the mempool of a node using the default parameters. While the number of
transactions “in flight” or across the mempools of all nodes in the network could
exceed this number, we believe that is unlikely to be a problem in practice.

The default expiry of 40 blocks after Blossom activation represents an expected
time of 50 minutes. Therefore (even if some blocks are slow), most legitimate
transactions are expected to expire within 60 minutes. Note however that an
attacker’s transactions cannot be relied on to expire.


Deployment
==========

This specification is proposed to be implemented in zcashd v2.1.0.


Reference implementation
========================

TBD


References
==========

.. [#RFC2119] `Key words for use in RFCs to Indicate Requirement Levels <https://tools.ietf.org/html/rfc2119>`_
.. [#zip-0208] `Shorter Block Target Spacing <https://zips.z.cash/zip-0208>`_
.. [#BitcoinCore-PR6722] `Bitcoin Core PR 6722: Limit mempool by throwing away the cheapest txn and setting min relay fee to it <https://github.com/bitcoin/bitcoin/pull/6722>`_
