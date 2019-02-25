::

  ZIP: ???
  Title: Prohibit Negative Shielded Value Pool
  Author: Sean Bowe <sean@z.cash>
  Category: Consensus
  Created: 2019-02-25
  License: MIT

Terminology
===========

The key words "MUST", "SHOULD", "SHOULD NOT", and "MAY" in this document are to be interpreted as described in
RFC 2119. [#RFC2119]_

The "Sprout value pool", as described by section 4.11 of the Zcash Protocol Specification [#protocol]_, is the sum of all previous transactions' ``vpub_old`` fields subtracted by the sum of all previous transactions ``vpub_new`` fields.

The "Sapling value pool", as described by section 4.12 of Zcash Protocol Specification [#protocol]_, is the negation of the sum of all previous transactions' ``valueBalance`` fields.

Abstract
========

This proposal defines how the consensus rules are altered such that blocks which produce negative shielded value pools are prohibited.

Motivation
==========

It is possible for nodes to monitor the total amount of coins that are shielded or unshielded in each of the Sprout or Sapling shielded transaction protocols. If the amount of coins that are unshielded exceed the amount that are shielded, a balance violation has occurred in the corresponding shielded transaction protocol.

It would be preferable for the network to reject blocks that result in the aforementioned balance violation. However, nodes do not currently react to such an event. Remediation may therefore require chain rollbacks and other disruption.

Specification
=============

If the "Sprout value pool" or "Sapling value pool" were to become negative as a result of accepting a block, then all nodes MUST reject the block as invalid.

Deployment
==========

This consensus rule is not deployed as part of a network upgrade as defined in ZIP-200 [#zip-0200]_ and there is no mechanism by which the network will synchronize to enforce this rule. Rather, all nodes should begin enforcing this consensus rule upon acceptance of this proposal.

There is a risk that before all nodes on the network begin enforcing this consensus rule that block(s) will be produced that violate it, potentially leading to network fragmentation. This is considered sufficiently unlikely that the benefits of enforcing this consensus rule sooner are overwhelming.

.. [#RFC2119] `Key words for use in RFCs to Indicate Requirement Levels <https://tools.ietf.org/html/rfc2119>`_
.. [#protocol] `Zcash Protocol Specification, Version 2019.0-beta-37 [Overwinter+Sapling] <https://github.com/zcash/zips/blob/master/protocol/protocol.pdf>`_
.. [#zip-0200] `ZIP 200: Network Upgrade Mechanism <https://github.com/zcash/zips/blob/master/zip-0200.rst>`_
