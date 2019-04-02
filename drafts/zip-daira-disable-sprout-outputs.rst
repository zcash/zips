::

  ZIP: 211
  Title: Disabling Sprout Outputs
  Owners: Daira Hopwood <daira@z.cash>
  Credits: Sean Bowe <sean@z.cash>
  Status: Draft
  Category: Consensus
  Created: 2019-03-29
  License: MIT


Terminology
===========

The key words "MUST" and "MAY" in this document are to be interpreted as described in
RFC 2119. [#RFC2119]_

The term "network upgrade" in this document is to be interpreted as described in ZIP 200
[#zip-0200]_.

The term "Sapling" in this document is to be interpreted as described in ZIP 205
[#zip-0205]_.

The terms "commitment tree", "treestate", and "dummy note" are to be interpreted as
described in [#protocol]_.


Abstract
========

This proposal defines a modification to the transaction format to disable outputs to
Sprout addresses. This takes a step toward being able to remove the Sprout protocol,
thus reducing the overall complexity and attack surface of Zcash.


Motivation
==========

The first iteration of the Zcash network, called Sprout, provided a shielded payment
protocol that was relatively closely based on the original Zerocash proposal. [#zerocash]_

The Sapling network upgrade [#zip-0205]_ introduced significant efficiency and
functionality improvements for shielded transactions. It is expected that over time,
the use of Sapling shielded transactions will replace the use of Sprout.

The Sapling and Sprout shielded protocols employ different cryptographic designs.
Since an adversary could potentially exploit any vulnerability in either design,
supporting both presents additional risk over supporting only the newer Sapling protocol.

For example, a vulnerability was discovered in the zero-knowledge proving system
originally used by Zcash that could have allowed counterfeiting [#counterfeiting]_.
While this particular vulnerability was addressed (also for Sprout shielded transactions)
by the Sapling upgrade, and we are not aware of others at the time of writing, the
possibility of other cryptographic weaknesses cannot be entirely ruled out.

In addition, the Zcash specification and implementation incurs complexity and
"technical debt" from the requirement to support both shielded transaction protocols.

Removing the ability to send to Sprout outputs is a first step toward reducing this
complexity and potential risk. This does not prevent extracting value held in Sprout
addresses and sending it to transparent addresses, or to Sapling addresses via the
migration tool [#migration]_.


Specification
=============

A new v5 transaction format is defined, with the following changes relative to the
Sapling v4 transaction format [#v4-tx]_:

- In JoinSplit descriptions, the ``ephemeralKey``, and ``encCiphertexts`` fields are
  removed.

- When creating JoinSplit descriptions, the Sprout output notes MUST be either
  internal change (i.e. spent in a subsequent JoinSplit of the same transaction),
  or dummy notes as described in [#protocol]_ section 4.7.1.

- The output commitments of a JoinSplit description in a v5 transaction MUST NOT
  be added to the output Sprout commitment tree. That is, the root of the Sprout note
  commitment tree in the output treestate of a v5 transaction is the same as that in
  its input treestate. This does not affect the use of interstitial Sprout treestates
  in v5 transactions.

The removal of ``ephemeralKey`` and ``encCiphertexts`` fields means that for JoinSplit
descriptions in v5 transactions, it is not necessary for a wallet to perform trial
decryption of those fields to detect incoming payments as described in [#protocol]_
sections 4.18 and 4.16.2. The processing of nullifiers in the algorithm of section 4.18
is unaffected.

Note that the consensus protocol does not prevent a wallet from incorrectly creating
a Sprout output note that is neither internal change nor a dummy note. In this case
the value associated with the note cannot be spent and is therefore "burnt".

When this proposal is activated, nodes and wallets MUST disable any facilities to
send to Sprout addresses, and this SHOULD be made clear in user interfaces.


Rationale
=========

This design does not require any change to the JoinSplit circuit, thus minimizing
the risk of security regressions, and avoiding the need for a new ceremony to generate
circuit parameters.

The code changes needed are relatively small and simple, and their security is easy
to analyse.

Removing the ``ephemeralKey`` and ``encCiphertexts`` fields reduces the size of a
JoinSplit description in a v5 transaction from 1698 bytes to 464 bytes, and avoids
the need to scan those fields for incoming payments.

During the development of this proposal, an alternative design was considered that
would also have removed the ``commitment`` field from v5 JoinSplit descriptions,
instead computing the commitments in a way that ensured at the consensus level that
they had zero value. This alternative was not adopted because it would have prevented
the use of internal change between JoinSplits, and that would have resulted in an
unavoidable information leak of the total value of the two Sprout inputs to each
JoinSplit. As it is, there is an unavoidable leak of the total value of Sprout inputs
to each v5 *transaction*, but not for individual JoinSplits.


Security and Privacy Considerations
===================================

The security motivations for making this change are described in the Motivation section.

Since all clients change their behaviour at the same time when this proposal activates,
there is no additional client distinguisher.


Deployment
==========

At the time of writing it has not been decided which network upgrade (if any) will
implement this proposal. The changes described in the Specification section must be
merged with any other transaction format changes made in the same upgrade.


Reference Implementation
========================

TBD


References
==========

.. [#RFC2119] `Key words for use in RFCs to Indicate Requirement Levels <https://tools.ietf.org/html/rfc2119>`_
.. [#zip-0200] `ZIP 200: Network Upgrade Activation Mechanism <https://github.com/zcash/zips/blob/master/zip-0200.rst>`_
.. [#zip-0205] `ZIP 205: Deployment of the Sapling Network Upgrade <https://github.com/zcash/zips/blob/master/zip-0205.rst>`_
.. [#protocol] `Zcash Protocol Specification, Version 2019.0-beta-37 [Overwinter+Sapling] <https://github.com/zcash/zips/blob/master/protocol/protocol.pdf>`_
.. [#v4-tx] `Section 7.1: Encoding of Transactions. Zcash Protocol Specification, Version 2019.0-beta-37 [Overwinter+Sapling] <https://github.com/zcash/zips/blob/master/protocol/protocol.pdf>`_
.. [#zerocash] `Zerocash: Decentralized Anonymous Payments from Bitcoin (extended version) <http://zerocash-project.org/media/pdf/zerocash-extended-20140518.pdf>`_
.. [#counterfeiting] `Zcash Counterfeiting Vulnerability Successfully Remediated <https://z.cash/blog/zcash-counterfeiting-vulnerability-successfully-remediated/>`_
.. [#migration] `Draft ZIP 308: Sprout to Sapling Migration <https://github.com/zcash/zips/pull/197>`_
