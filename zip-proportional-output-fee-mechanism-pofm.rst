::

  ZIP: 317
  Title: Proportional Transfer Fee Mechanism
  Owners: Aditya Bharadwaj <nighthawk24@gmail.com>
  Credits: Madars Virza
           Kris Nuttycombe
           Daira Hopwood
           Jack Grigg
           Francisco Gindre
  Status: Draft
  Category: Standards / Wallet
  Obsoletes: ZIP 313
  Created: 2022-08-15
  License: MIT
  Discussions-To: <https://forum.zcashcommunity.com/t/zip-proportional-output-fee-mechanism-pofm/42808>
  Pull-Request: <https://github.com/zcash/zips/pull/631>


Terminology
===========

The key word "SHOULD" in this document is to be interpreted as described in
RFC 2119. [#RFC2119]_

The term "conventional transaction fee" in this document is in reference
to the value of a transaction fee that is conventionally used by wallets,
and that a user can reasonably expect miners on the Zcash network to accept
for including a transaction in a block.

The terms "Mainnet, "Testnet", and "zatoshi" in this document are defined
as in [#protocol-networks]_.


Abstract
========

The goal of this ZIP is to change the conventional fees for transactions
and get buy-in from wallet developers, miners and Zcash users.


Motivation
==========

In light of recent network activity, it is time to review and update the
standard 1,000 zatoshi transaction fee set in ZIP 313 [#zip-0313]_.

The conventional transaction fee presently is 0.00001 ZEC or 1,000 zatoshis, as
specified in ZIP 313. This allowed exploration of novel use cases of the Zcash
blockchain. The Zcash network has operated for almost 2 years at a conventional
transaction fee of 1,000 zatoshis, without consideration for the total number
of inputs and outputs in each transaction. Under this conventional fee, some
usage of the chain has been characterized by high-output transactions with
1,100 outputs paying the same conventional fee as a transaction with 2 outputs.

The objective of the new fee policy, once it is enforced, is for fees paid by
transactions to fairly reflect the processing costs that they impose on various
participants in the network. This will tend to discourage usage patterns that
cause either intentional or unintentional denial of service, while still
allowing low fees for regular transaction use cases.


Requirements
============

* The conventional fee formula should not favour or discriminate against any
  of the Orchard, Sapling, or transparent protocols.
* The fee for a transaction should scale linearly with the number of inputs
  and/or outputs.
* Users should not be penalised for sending transactions constructed
  with padding of inputs and outputs to reduce information leakage.
  (The default policy employed by zcashd and the mobile SDKs pads to
  two inputs and outputs for each shielded pool used by the transaction).
* Users should be able to spend a small number of UTXOs or notes with value
  below the marginal fee per input.


Specification
=============

This specification defines three parameters that are used to calculate the
conventional fee:

=================== ============================
Parameter           Units
=================== ============================
`marginal_fee`      zatoshis per input or output
`grace_window_size` inputs or outputs
=================== ============================

Wallets implementing this specification SHOULD use a conventional fee
calculated in zatoshis per the following formula::

    logical_actions = max(transparent_inputs, transparent_outputs) +
                      2*sprout_joinsplits +
                      max(sapling_inputs, sapling_outputs) +
                      orchard_actions

    conventional_fee = marginal_fee * max(grace_actions, logical_actions)

The parameters are set to the following values:
* `marginal_fee = 5000`;
* `grace_window_size = 2`.

It is not a consensus requirement that fees follow this formula; however,
wallets SHOULD create transactions that pay this fee, in order to reduce
information leakage, unless overridden by the user.

Transaction relaying
--------------------

zcashd, zebrad, and potentially other node implementations, implement
fee-based restrictions on relaying of mempool transactions. Nodes that
normally relay transactions are expected to do so for transactions that pay
at least the conventional fee as specified in this ZIP, unless there are
other reasons not to do so for robustness or denial-of-service mitigation.

Mempool size limiting
---------------------

zcashd and zebrad limit the size of the mempool as described in [#zip-0401]_.
This specifies a *low\_fee\_penalty* that is added to the "eviction weight"
if the transaction pays a fee less than the conventional transaction fee.
This threshold is modified to use the new conventional fee formula.

Block production
----------------

Miners, mining pools, and other block producers, select transactions for
inclusion in blocks using a variety of criteria. Where the criteria
previously used the conventional transaction fee defined in ZIP 313 to
decide on transaction inclusion, it is expected to instead use the formula
specified in this ZIP.

Open Issues
-----------

> TODO: Remove this section once a decision is made.

Possible alternatives for the parameters:

* marginal_fee = 250 in @nuttycom's proposal.
* marginal_fee = 1000 adapted from @madars' proposal.
* marginal_fee = 2500 in @daira's proposal.
* marginal_fee = 1000 for Shielded, Shielding and De-shielding
  transactions, and marginal_fee = 10000 for Transparent transactions
  adapted from @nighthawk24's proposal.

(In @madars' and @nighthawk24's original proposals, there was an additional
`base_fee` parameter that caused the relationship between fee and number
of inputs/outputs to be non-proportional above the `grace_window_size`. This
is no longer expressible with the formula specified above.)

Rationale for logical actions
'''''''''''''''''''''''''''''

A previous proposal used `inputs + outputs` instead of logical actions.
This would have disadvantages Orchard transactions, as a result of an
Orchard Action combining an input and an output. The effect of this
combining is that Orchard requires padding of either inputs or outputs
to ensure that the number of inputs and outputs are the same. Usage of
Sapling and transparent protocols does not require this padding, and
so this could have effectively discriminated against Orchard.


Security and Privacy considerations
===================================

Non-standard transaction fees may reveal specific users or wallets or wallet
versions, which would reduce privacy for those specific users and the rest
of the network. However, the advantage of faster deployment argued against
synchronizing the change in wallet behaviour at a specific block height.

Long term, the issue of fees needs to be re-visited in separate future
proposals as the blocks start getting consistently full. New ZIPs with
scaling solutions, will need to be evaluated and applied.

Denial of Service Vulnerability
-------------------------------

A transaction-rate-based denial of service attack occurs when an attacker
generates enough transactions over a window of time to prevent legitimate
transactions from being mined, or to hinder syncing blocks for full nodes
or miners.

There are two primary protections to this kind of attack in Zcash: the
block size limit, and transaction fees. The block size limit ensures that
full nodes and miners can keep up with the blockchain even if blocks are
completely full. However, users sending legitimate transactions may not
have their transactions confirmed in a timely manner.

Variable fees could mitigate this kind of denial of service: if there are
more transactions available than can fit into a single block, then a miner
will typically choose the transactions that pay the highest fees. If
legitimate wallets were to increase their fees during this condition, the
attacker would also increase the fees of their transactions. It is
sometimes argued that this would impose a cost to the attacker that would
limit the time window for which they can continue the attack. However, there
is little evidence that the actual costs involved would be a sufficient
disincentive.

This proposal does not alter how fees are paid from transactions to miners.

Wallet developers and operators should monitor the Zcash network for rapid
growth in transaction rates.


Deployment
==========

Wallets SHOULD deploy these changes immediately. Nodes SHOULD deploy the
change to the *low\_fee\_penalty* threshold described in `Mempool size limiting`_
immediately.

Nodes can deploy restrictions to their policies for relaying, mempool
acceptance, and/or mining once a sufficient proportion of wallets in the
ecosystem are observed to be paying at least the updated conventional
transaction fee. Node developers SHOULD coordinate on deployment
schedule.


Endorsements
============

The following entities/groups/individuals expressed their support for the
updated fee mechanism:

*Developer Groups or Sole OSS contributors*

* Zecwallet Suite (Zecwallet Lite for Desktop/iOS/Android & Zecwallet FullNode)
* Nighthawk Wallet for Android & iOS

To express and request your support to be added to this ZIP please comment
below indicating:

* (group) name/pseudonym
* affiliation
* contact

or, conversely e-mail the same details to the Owner of the ZIP.

> TODO: Endorsements may depend on specific parameter choices. The ZIP
> Editors should ensure that the endorsements are accurate before merging
> this ZIP.


Acknowledgements
================

Thanks to Madars Virza for initially proposing a fee mechanism similar to that
proposed in this ZIP [#madars-1]_, and to Kris Nuttycombe, Jack Grigg, Daira Hopwood,
Francisco Gindre, Greg Pfeil, and Teor for suggested improvements.


References
==========

.. [#RFC2119] `RFC 2119: Key words for use in RFCs to Indicate Requirement Levels <https://www.rfc-editor.org/rfc/rfc2119.html>`_
.. [#protocol-networks] `Zcash Protocol Specification, Version 2022.3.8. Section 3.12: Mainnet and Testnet <protocol/protocol.pdf#networks>`_
.. [#madars-1] `Madars concrete soft-fork proposal <https://forum.zcashcommunity.com/t/zip-reduce-default-shielded-transaction-fee-to-1000-zats/37566/89>`_
.. [#zip-0313] `ZIP 313: Reduce Conventional Transaction Fee to 1000 zatoshis <zip-0313.rst>`_
.. [#zip-0401] `ZIP 401: Addressing Mempool Denial-of-Service <zip-0401.rst>`_
