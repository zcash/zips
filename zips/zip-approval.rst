::

  ZIP: TO BE ASSIGNED
  Title: Transaction User Controls
  Owners: Pablo Kogan <pablo@qed-it.com>
          Antoine Rondelet <antoine@qed-it.com>
  Status: Draft
  Category: Consensus
  Created: 2024-12-22
  License: MIT
  Discussions-To: <https://forum.zcashcommunity.com/t/introducing-transaction-controls-in-zcash/49640>
  Pull-Request: <TODO: ADD>


Terminology
===========

The key word "MUST" in this document is to be interpreted as described in BCP 14 [#BCP14]_ when, and only when, it appears in all capitals.

The term "network upgrade" in this document is to be interpreted as described in ZIP 200 [#zip-0200]_.

The terms "Orchard" and "Action" in this document are to be interpreted as described in ZIP 224 [#zip-0224]_.

The terms "Asset" and "ZSA" in this document are to be interpreted as described in ZIP 227 [#zip-0227]_.

Abstract
========

This ZIP proposes transaction user controls - a mechanism allowing recipients of shielded funds to actively participate in the transfer of assets by approving or rejecting incoming transactions.

Motivation
==========

In the current version of Zcash, fund transfers occur without explicit recipient consent.
While this simplicity offers convenience, it creates significant challenges for users of the network (e.g. individuals or businesses).
The goal of this ZIP is to design a mechanism where the recipient of shielded funds on Zcash (for any type of ZSA) can confirm (or ‘approve’) the receipt of the funds on chain.
This enhancement addresses crucial needs in the Zcash ecosystem, particularly at a time when privacy-preserving assets face increased scrutiny from major exchanges.
The proposed controls offer robust safeguarding solutions while maintaining Zcash’s core privacy features.

Overview
========

Existing Zcash users rely on the notion of "address" to identify each other.
Each Zcash user has one or more address.
When 2 users (a sender and a recipient) want to transact, they first need to "discover each other".
More particularly, the sender of the funds, must get the address of the recipient in order to transfer funds to the counterparty.
This "address discovery" is usually done via off-chain communications (e.g. emails, forum).
By sharing (or not sharing) their payment address, recipients can decide (i.e. 'authorize' or 'not authorize') which other network participants can send them funds on the network.

In some contexts, individuals and/or organizations may want to publish one of their addresses in order to allow everyone to issue a payment to them (e.g. charities like Turing Trust).
In other cases, Zcash users may want to selectively disclose their payment addresses to only allow incoming payments from a restricted set of users.

But, relying exclusively on "address discovery" to authorize / not authorize incoming payments has the following limitations:
    
- Lack of revocation: Sharing one's payment address only allows the recipient to "grant" the "authority to be paid by a user", but it doesn't allow the recipient to "revoke" this "authority to be paid". This could be an issue if recipients want to authorize the sender to pay them only once. (Generating new addresses is not a clean way to revoke the authorization to pay because the sender can still send funds to the old address, potentially leading to lost funds. More on that below.)
- Loose authorization. Sharing one's address with a sender only allows the recipient to "grant" the "authority to be paid by a user" but it does not constrain the terms of the payment. The recipient might want to only authorize payments for specific amounts - or at specific times (e.g. for tax reasons) -, instead of authorizing "every kind of payments, any time" from the sender they shared their payment address with.
- Payment authorization is transitive (undesired property). A malicious sender could disclose the payment address of the recipient to other network participants which will - in turn - "grant them authorization to send funds to the recipient", against the recipient's will. Say, e.g. Alice gives her address to Bob to authorize him to pay her. If Bob leaks Alice's address to Charlie, then, now Charlie knows Alice's address - as if Alice gave her address to Charlie (to authorize him to pay her). In other words, recipients can control who they share their address with, but once shared they can't control who else will get their address. (Obviously, not all senders will be malicious in reality, but every sender can be compromised. This is why, we must assume all senders to be malicious in the analysis.)

Nowadays, any sender who has the address of another Zcash user can - unilaterally - send funds to this user.

In doing so, the sender can:

- Create a link between the recipient and a specific asset.
- Create a link between a recipient and unlawfully acquired/tainted funds (e.g. to blackmail, cause reputational damages) etc.
- Associate the recipient with a group of users or a set of on-chain transactions

The fact that senders can - unaliterally - transfer funds to a recipient, without their consent creates a set of practical issues.
Custodians like centralized exchanges (CEX), for instance, have no way to reject fraudulent deposits. As a consequence, several CEX have started to delist privacy preserving crypto assets like Zcash [#zcash-delist]_. Such delistings impact the Zcash community, making the asset harder to buy and sell across the ecosystem.
Likewise, given that recipients are not actively involved in the transfer of funds, the sender is the sole responsible to make sure that the asset transfer occurs as expected.
Unfortunately, mistakes are made regularly (e.g. typos in the address of the recipient), which regularly leads funds being lost.
Established payment systems (e.g. CHAPS or Faster Payments in the UK) have developped solutions to mitigate errors in transfers (e.g. Confirmation of Payee (CoP) [#confirmation-of-payee]_), but, to date, crypto transfers lack such safeguarding functionality.

This ZIP introduces an interactive protocol for the sender of funds to seek approval from the recipient during an asset transfer.
This approval is generated by the recipient of funds who generates an approval signature on the raw transaction and sends it back to the sender.
Upon receipt of the approval signature, the sender can then submit the transaction to the chain for execution.
The Zcash network can verify the validity of the approval by verifying that the approval signature has been generated by the recipient of the funds transfered in the transaction.

This interactive user control protocol offers a double-opt in on fund transfers, which:

1. acts as a loss-prevention mechanism, and
2. allows the recipients of funds to control (accept/reject) the funds being sent to their wallet.

Specification
=============

Most of the protocol is kept the same as the Orchard protocol released with NU5, except for the following.

Approval Signature
------------------

Given the Orchard address (in the form: $d | pk_d$, see [#protocol-raw-address]_) of the recipient of the output note of an Orchard Action and given that $g_d$ is a Pallas curve point, derived from $d$ (see [#protocol-diversify-hash]_) - the approval signature derivation goes as follows:

1. The sender sends the OrchardAction (the preimage of the message to be signed) for the recipient to sign.
2. The recipient executes the following steps:
    - $m \gets H(OrchardActionDescription)$, where $OrchardActionDescription$ is the Orchard Action description as per [#protocol-actions]_.
    - Takes $r \overset{{\scriptscriptstyle\$}}{\leftarrow} \mathbb{Z}_{r_{\mathbb{P}}}$, where $\mathbb{Z}_{r_{\mathbb{P}}}$ is the scalar field of Pallas [#protocol-pallas-vesta]_, and where $\overset{{\scriptscriptstyle\$}}{\leftarrow}$ denotes a variable assignment uniformly at random from a given set.
    - $u \gets [r]g_d$, a Pallas point
    - $C \gets H(g_d, pk_d, u, m) \mod r_{\mathbb{P}}$, an element of Pallas' scalar field, and where $H$ is a secure hash function (e.g. SHA256 or Blake2)
    - $s \gets r + C * ivk \mod r_{\mathbb{P}}$, an element of Pallas' scalar field
    - $\sigma_{approval} \gets (u, s)$

, and sends $\sigma_{approval}$ to the sender (off-chain).

$\sigma_{approval}$ is a tuple made of one Pallas point and one element of Pallas' scalar field.
Hence, the size, in bytes of $\sigma_{approval}$ is: 96 bytes.

Rationale for Approval Signature
````````````````````````````````

To prove that the correct recipient of the output notes of an Orchard Action approves (the transfer of funds represented by) the Action, we want to show that the approval signature has been generated with a signing key that is derived from the spending key of the recipient of the output notes of the Action.
In other words, we want to prove that the approval signature is generated by the network user who "knows" the spending key of the output notes of the Action.
Doing so means that only the recipient of the note created in the Orchard Action can approve the payment.

To achieve this, we look into the key structure of Zcash Orchard.
We know that the Orchard address is of the form: $d | pk_d$.
These 2 fields, the diversifier and the diversified address, are used by the sender when sending notes.

Looking at the Orchard key components derivations, we know that $pk_d$ is derived as:
$pk_d := KAOrchard.DerivePublic(ivk, g_d) = [ivk]g_d$, see [#protocol-orchard-keys]_ and [#protocol-key-agreement]_

Given that $ivk$ is derived from the spending key of the recipient of the funds, we can prove that the recipient of the funds in an Orchard Action is approving the receipt of the funds, by using a proof of knowledge of $ivk$.
Such proof of knowledge of $ivk$ can be obtained by using the Non-Interactive Schnorr Protocol. 

In fact, such proof of knowledge of ivk can be obtained by using a Schnorr Signature on the Action (the message) with ivk as signing/secret key and $g_d$ as group generator.

Modifications to the Orchard Statement/Circuit
----------------------------------------------

The following steps are added to the Orchard Action statement:

Instance:

- $\sigma_{approval}$
- $OrchardActionDescription$

Witness:

- $g_d$
- $pk_d$

Circuit:

- $C’ \gets H(g_d, pk_d, \sigma_{approval}.u, H(OrchardActionDescription))$
- $LHS \gets [\sigma_{approval}.s]g_d$
- $RHS \gets \sigma_{approval}.u + [C']pk_d$
- $LHS - RHS = 0$

Rationale for the modifications to the Orchard Statement/Circuit
````````````````````````````````````````````````````````````````

Upon receipt of the approval signature by the recipient of the funds, the sender could include $\sigma_{approval}$ along with $g_d$ and $pk_d$ in the transaction to be sent on chain.
Indeed, both $g_d$ and $pk_d$ of the recipient are needed by the Zcash validators/miners to verify the approval Schnorr signature on chain.

In this case, the Zcash miners could verify the recipient's approval by doing (for each Action in the transaction):

1. $C’ \gets H(g_d, pk_d, \sigma_{approval}.u, H(OrchardActionDescription))$
2. $LHS \gets [\sigma_{approval}.sigma]g_d$
3. $RHS \gets \sigma_{approval}.u + [C']pk_d$
4. $LHS \stackrel{?}{=} RHS$. If not, reject transaction.

If the signature was generated correctly, $LHS = [r + C * ivk]g_d$ and $RHS =[r]g_d + [C]pk_d$, since a well derived $pk_d$ equals $[ivk]g_d$ we get $RHS = [r]g_d + [C][ivk]g_d \implies RHS = [r + C * ivk]g_d$.
So if all steps are followed properly, $LHS = RHS$ and the signature verification succeeds.

However, to verify the signature, Zcash miners need to know which $g_d$ and $pk_d$ to use to verify the approval signatures on each Actions.
Disclosing these values leaks "which Orchard address" is the recipient of the output notes of an Action.
So, unlinkability is affected.

Here, the sender needs to include the Orchard address of the recipient for the miners to check approval from the recipient.
To fix this, we included the Schnorr signature verification in the Orchard Action circuit directly. This keeps the recipient's $g_d$ and $pk_d$ privy to the transacting parties (i.e. the values remain part of the witness - as currently done in the NU5 protocol).
The Zcash miners, just need to verify the Orchard Action proof to make sure the approval signature was:

- Properly generated by the recipient of the notes in the Orchard Actions
- Properly verified by the sender of the funds

Modifications to the Transaction Format
---------------------------------------

In order to support this ZIP, the transaction format, as specified in [#protocol-tx-encoding]_, must be extended to add the appoval signatures, as follows:

======================= ================ ============================ ================================================================
Bytes                   Name             Data Type                    Description
======================= ================ ============================ ================================================================
96 * nActionsOrchard    vApprovalSigs    byte[96][nActionsOrchard]    Approval signatures for each Orchard Action
======================= ================ ============================ ================================================================ 

Other Considerations
====================

Transaction Fees
----------------

Given the modification of the transaction structure (and the additional bytes), it might be necessary to slightly increase the default transaction fees on Zcash if this ZIP gets implemented.

References
==========

.. [#BCP14] `Information on BCP 14 — "RFC 2119: Key words for use in RFCs to Indicate Requirement Levels" and "RFC 8174: Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words" <https://www.rfc-editor.org/info/bcp14>`_
.. [#zip-0200] `ZIP 200: Network Upgrade Mechanism <zip-0200.html>`_
.. [#zip-0209] `ZIP 209: Prohibit Negative Shielded Chain Value Pool Balances <zip-0209.html>`_
.. [#zip-0224] `ZIP 224: Orchard <zip-0224.html>`_
.. [#zip-0227] `ZIP 227: Issuance of Zcash Shielded Assets <zip-0227.html>`_
.. [#confirmation-of-payee] `Confirmation of Payee` <https://www.wearepay.uk/what-we-do/overlay-services/confirmation-of-payee/>
.. [#zcash-delist] `Important: Potential Binance Delisting` <https://forum.zcashcommunity.com/t/important-potential-binance-delisting/45954>
.. [#protocol-actions] `Zcash Protocol Specification, Version 2024.5.1 [NU6]. Section 7.5: Action Description Encoding and Consensus` <https://zips.z.cash/protocol/protocol.pdf#actionencodingandconsensus>
.. [#protocol-raw-address] `Zcash Protocol Specification, Version 2024.5.1 [NU6]. 5.6.4.2 Orchard Raw Payment Addresses` <https://zips.z.cash/protocol/protocol.pdf#orchardpaymentaddrencoding>
.. [#protocol-diversify-hash] `Zcash Protocol Specification, Version 2024.5.1 [NU6]. 5.4.1.6 DiversifyHashSapling and DiversifyHashOrchard Hash Functions` <https://zips.z.cash/protocol/protocol.pdf#concretediversifyhash>
.. [#protocol-pallas-vesta] `Zcash Protocol Specification, Version 2024.5.1 [NU6]. 5.4.9.6 Pallas and Vesta` <https://zips.z.cash/protocol/protocol.pdf#pallasandvesta>
.. [#protocol-orchard-keys] `Zcash Protocol Specification, Version 2024.5.1 [NU6]. 4.2.3 Orchard Key Components` <https://zips.z.cash/protocol/protocol.pdf#orchardkeycomponents>
.. [#protocol-key-agreement] `Zcash Protocol Specification, Version 2024.5.1 [NU6]. 5.4.5.5 Orchard Key Agreement` <https://zips.z.cash/protocol/protocol.pdf#concreteorchardkeyagreement>
.. [#protocol-tx-encoding] `Zcash Protocol Specification, Version 2024.5.1 [NU6]. 7.1 Transaction Encoding and Consensus` <https://zips.z.cash/protocol/protocol.pdf#txnencoding>