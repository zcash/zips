::

  ZIP: XXXX
  Title: URI-Encapsulated Payments
  Owners: Ian Miers <imichaelmiers@gmail.com>
          Eran Tromer <eran@tromer.org>
  Credits: Sean Bowe
           Deirdre Connolly
           Kevin Gorham
           Jack Grigg
           Daira Hopwood
           Linda Naeun Lee
           George Tankersley
           Henry de Valence
  Status: Draft
  Category: Standards Track
  Created: 2019-07-17
  License: MIT

Terminology
===========

The key words "MUST", "MUST NOT", "SHOULD", and "MAY" in this document are to be 
interpreted as described in RFC 2119. [#RFC2119]_

Zcash protocol terms are as defined in the Zcash Protocol Specification. [#protocol]_

.. _applink:
By “applink” we mean a platform mechanism for triggering local applications using HTTP links, such as `App Links`_ on Android, `Universal Links`_ on iOS, or `App URI handlers`_ on Windows.


Abstract
========

This proposal defines a mechanism for sending a Zcash payment encapsulated in a URI string. This enables sending Zcash funds over any secure channel, such as via a messaging app, even if the recipient does not yet have Zcash software installed and does not have a Zcash payment address. This is implemented by having the URI convey the secret spending key of an ephemeral Zcash “wallet address”, to which the funds have been transferred. Anyone who learns the URI can accept this payment, by a “finalization” process which uses the key given in the URI to transfer the encapsulated funds to their own wallet. After the payment is finalized, via a suitable on-chain transaction by the recipient, it becomes irrevocable.

The proposal specifies the syntax and semantics of Payment-Encapsulating URIs, the workflow of generating and handling them, and requisite infrastructure.

At its core, a URI encapsulated payment communicates the existence of a transaction (specifically a note committing to an amount of funds) to a receiving client.  The URI encode contains the amount of the payment and a key used to derive all necessary randomness for note construction including the address and secret key needed to spend it.

Usage Story
-----------

Alice wants to send a 1.23 ZEC payment to Bob. She generates a fresh ephemeral spending key and sends 1.2301 ZEC to it. This transaction is submitted to the network and mined. Meanwhile, Alice constructs a URI containing the ephemeral spending key and appropriate metadata, and sends it to Bob over an end-to-end encrypted channel such as Signal or WhatsApp.

Bob receives a message, which looks as follows:

    This message contains a Zcash payment.
    Click the following link to view it and receive the funds using your Zcash wallet app: 
    
https://pay.withzcash.com:65536/v1#amount=1.23&desc=Payment+for+foo&key=...
    If you do not yet have a Zcash wallet app, see: https://z.cash/wallets

Bob clicks the link. His Zcash mobile wallet app (which is already installed and has configured itself as a handler for URLs of that form) shows up, and tells Bob that a payment of 1.23 ZEC awaits him. The wallet app confirms the existence of the pertinent transactions on the blockchain, and then offers to finalize the payment. Bob clicks the “Finalize” button, and his wallet app generates a transaction moving the money to his own address (using the extra 0.0001 ZEC he has received to pay the transaction fee). When this transaction is confirmed on-chain, Alice’s and Bob’s wallets both indicate that the payment is finalized, and thus Bob can send the funds to other parties.


Motivation
==========

This proposal enables sending of funds without exposing users to the notion of payment addresses and their secure distribution. Instead, funds can be sent using any pre-existing communication channel, by a single message sent unidirectionally from the sender to the recipient. This message conveys all the information needed to obtain control of the funds, compactly expressed as a textual URI.

Consequently, all functionality related to contact discovery and secure-channel establishment can be delegated to the message app(s) with which the user is already familiar, and in which the user has already established communication channels to many of their contacts.

Moreover, funds can be sent to users who have not yet installed wallet software and who do not yet have a payment address. The recipient can collect the funds at any later time by installing suitable software.

The proposal is complementary to ZIP 321 [#zip321]_, which will standardize *Payment Request URIs* using which the payment *recipient* can convey their persistent payment address to the *sender*, for subsequent fund transfers (to be done using the normal on-chain mechanism rather than the encapsulated payments described in the current proposal).


Requirements
============

This proposal’s specification of Payment-Encapsulating URIs, and the intended protocols for using them, is meant to fulfill the following requirements:

* The protocol must not require the sender of a payment to stay online until the recipient receives the URI (let alone finalizes the payment).

* The URIs should be short, for convenient rendering and to maximize compatibility with length-limited messaging platforms.

* It must not be feasible for someone who has not seen the URI (or has compromised a party who has) to collect the funds.

* The URIs and protocol should minimize the likelihood of inadvertent misuse, and in particular the risks discussed in “Security Considerations” below.

* The protocol must not leak any information (sender identity, recipient identity, amount, description) to third parties, other than inevitable metadata about the existence of a transaction, the inevitable network communication around sending/receipts of transactions, whatever leakage is induced by the communication channel used to transmit the URI, and whatever is voluntarily shared by the parties.

* The URIs should allow for future modifications and expansion of the format, without risk of ambiguous parsing.

* The on-chain footprint of payments that use this mechanism should be indistinguishable from normal fully-shielded transactions (except, possibly, for the statistics of the number of shielded inputs and outputs).

* Don’t lose funds, even if wallets crash.

Non-requirements
================

* It is outside the scope of this proposal to establish a secure communication channel for transmission of Payment-Encapsulating URIs, or to protect the parties’ devices from security compromise.

* Finalizing the payment may involve significant wait times, on the scale of minutes, as the requisite on-chain transactions are generated, mined and confirmed. This proposal does not try to solve this (though it does try to avoid imposing significant additional delays, and it does address how the intermediate state is conveyed to the user).


Specification
=============

A Payment-Encapsulating URI represents the capability to claim the Zcash funds from specific on-chain transactions, as long as they’re unspent. See `Usage Story`_ for an example.

Syntax
------

A Payment-Encapsulating URI is a Universal Resource Locator (URL), as defined in RFC 3986 [#RFC3986]_, of the following form.

Scheme: ``https``

Host: ``pay.withzcash.com``

Port: ``65536`` (this is intentionally not a valid TCP/IP port number)

Path: ``payment/v1``

Fragment parameters: these attribute-value pairs, in this order, separated by ``&``, and with all values percent-encoded where necessary:

* ``amount=...`` where the attribute is a decimal number representing the amount of ZEC included in the payment. MUST be present.
   If a decimal fraction is present then a period (.) MUST be used as the separating character to separate the whole number from the decimal fraction, and both the whole number and the decimal fraction MUST be nonempty. No other separators (such as commas for grouping or thousands) are permitted. Leading zeros in the whole number or trailing zeros in the decimal fraction are ignored. There MUST NOT be more than 8 digits in the decimal fraction.
* ``desc=...`` where the attribute is a human-readable string associated with the payment. MAY be present.
   If present, it MUST be encoded as “textual data consisting of characters from the Universal Character Set” as specified in RFC 3986 section 2.5. 
* ``key=``is a 128 bit random number encoded with Bech32 as specified in Section 5.6.9 of the Zcash Protocol Specification [#protocol]_). MUST be present.


Semantics
---------

The values of ``key’’ and ``amount`` deterministically imply a unique *payment note* corresponding to this URI, which is a Zcash Sapling note that carries the given amount and is spendable by a Sapling spending key derived from ``key`. The derivation of this note is done by the following procedure:
*DerivePaymentNote(key,amount)*:
    Derive the master extended spending key *(ask, nsk, ovk, dk, c)* according to ZIP 32 [#zip32]_ `Sapling master key generation`_, with *key* as *sk_m*.
    Fix the diversified d = XXX.
    Derive *rcm = PRF^expand(sk_m || [0x11])* as specified in [#protocol]_ Section 5.4.2.
    Derive *pk_d* from *ask* and *nsk* as specified in [#protocol]_ Section 4.2.2.
    Define the corresponding *payment note* as *n = (d, pk_d, amount, rcm)*  (see [#protocol]_ Section 3.2).
    Define the corresponding a *payment note commitment* as *cm = NoteCommit^Sapling_rcm (repr_J (dk),repr_J (pk_d ), value)* as specified in [#protocol]_ Section 5.4.7.2.

Construct a shielded zcash transaction containing that note as an output.

The payment note SHOULD be unspent at the time it is intended to be received by the recipient. 

Clients MAY generate and send the URI before the transaction is built, sent, or confirmed.

The ``amount`` parameter MUST match the total amount of ZEC in the payment note plus the standard transaction fee for fully-shielded transactions (currently 0.0001 ZEC).

There MUST NOT exist any other notes on the blockchain, beyond the payment note derived from the Payment URI, that are addressed to a payment address derived from ``key``. Such notes MAY be generated within an implementation (e.g., as speculative pre-generation) but MUST NOT be broadcast for mining. 

The ``desc`` parameter MAY convey a human-readable description of the payment, entered manually by the user or generated by the application in any reasonable manner.

The encrypted memo fields in the output description containing the payment note commitment MUST be either empty (all-zero), or identical to the ``desc`` parameter (padded with zeros). 

When conveying payment to users, the sender’s and recipient’s wallet software MAY convey the description encoded in the ``desc`` parameter.

The recipient’s wallet software SHOULD convey to the user that the ``amount`` and ``desc`` values are merely a claim made by the party who sent the URI, and may be tentative, inaccurate or malicious.

In particular, the recipient’s wallet software SHOULD convey to the user that the amount of ZEC they can successfully transfer to their wallet may be different than that given by the ``amount`` parameter, and may change (possibly to zero), until the finalization process has been completed.


Centralized Deployment
----------------------

The owner of the ``withzcash.com`` domain name MUST NOT create a DNS record for the ``pay.withzcash.com`` domain name, nor a TLS certificate for it. All feasible means SHOULD be taken to ensure this, and to prevent unintended transfer of ownership or control over the ``withzcash.com`` domain name. (See `Rationale for URI Format`_ and `Security Considerations`_ below for discussion.)

Applink_ mechanisms let domain name owners provide a whitelist, specifying which apps are authorized to handle URLs with that domain name. This is implemented by serving suitable files at well-known paths on the web server of that domain or, in the case of a subdomain, its parent domain. Thus, the owner of the ``withzcash.com`` domain effectively controls the whitelist of apps that may be launched by users’ platform to handle URI-Encapsulated Payments (see `Security Implications`_). This whitelist should protect users from installing rogue apps that intercept incoming payments. Thus, the domain owner MUST do the following:
* Maintain such a whitelist and serve it as needed for the applink_ mechanisms of major platforms.
* Publish a policy for inclusion of apps in this whitelist.
* Use all feasible means to whitelist only apps that comply with the published policy.
* Publish the whitelist’s content in human-readable form.
* Provide clear and effective means for rapid removal of apps from the whitelist when required as security response.
* Use all feasible means to protect the whitelist’s integrity (in particular, this includes protecting the web server that serves the whitelist, the domain’s TLS certificate, and the means by which the whitelist is modified).
* Use effective means for keeping a precise, irrevocable and public history of the whitelist (e.g., using a timestamped Git repository, or an accountability mechanism akin to Certificate Transparency).

They also SHOULD:
* Strive for the whitelist to include all apps that would not place the user at any greater security risk than reputable state-of-the-art wallet apps.


Testing
-------

For testing purposes, all of the above specification is duplicated for the Zcash testnet network, substituting ``TAZ`` (Zcash testnet coins) for ``ZEC`` and ``testzcash.com`` for ``withzcash.com``.

A separate “testnet whitelist” MUST be maintained by the owner of the ``testzcash.com`` domain name, with a separate policy that SHOULD allow any legitimate third-party developer to add their work-in-progress wallet for testing purposes. Integrity and availability MAY be looser.

Wallets apps MAY support just one type of payments (ZEC or TAZ), and if they support both then they MUST keep separate accounting and must clearly distinguish the type when payments or balances are conveyed to users.


Rationale for URI Format
------------------------

The URI format ``https://pay.withzcash.com:65536/v1#...``  was chosen to allow automatic triggering of wallet software on mobile devices, using the platform’s applink_ mechanism, while minimizing the risk of payment information being intercepted by third parties. The latter is prevented by a defense in depth, where any of the following suffices to prevent the payment information from being exposed over the network:
* The ``pay.withzcash.com`` domain should not resolve.
* A valid TLS certificate for ``pay.withzcash.com`` should not exist..
* The port number ``65536`` is not valid for the TCPv4, TCPv6 or UDP protocols. Empirically, the common behavior in browsers and messaging apps, when following HTTPS links with port number port number 65536, is to render an empty or `about:blank` page rather than a DNS error; a network fetch is not triggered. (This may change if a network proxy protocol is used, but SOCKS5 also cannot represent port 65536.)
* The contents of the fragment identifier are specified by HTTP as being resolved locally, rather than sent over the network (but see the caveat about active JavaScript attacks below).

The downside is that if the user follows the link prior to installing a suitable wallet app, they get a weird-looking DNS error or a blank page. Also, the URL looks weird due to the port number.

Several alternatives were considered, but found to have inferior usability and/or security ramifications:

1.  ``https://pay.withzcash.com/v1#...``: similar to above, but without the port number, and backed by a DNS record, TLS certificate and web server for ``pay.withzcash.com`` that serves an informative HTML page (e.g., “Please install a wallet to receive this payment”). This still allows handling by wallet apps using an applink_ mechanism, and provides a friendlier fallback in case the user follows the link prior to installing a suitable app. However, it creates a security risk. If the web server serving that web page is compromised, or impersonated using an DNS+TLS attack, then the attacker can capture they payment parameters and steal the funds. (Note that the sensitive information is in the fragment following the ``#``, which is not sent in an HTTP GET request; but the malicious server can serve JavaScript code which retrieves the fragment.)

2. ``zcash-data:payment/v1?amount=1.23&desc=Payment+for+foo&key=...&seedcmu=...``: a custom URI scheme, such as ``zcash-data``. This still allows for triggering application action (e.g., using Mobile Deep Links). However, on most platorms, *any* app installed on the device is able to register to handle links from (almost) any custom URI scheme. If the request is received by a rogue party, then the funds could be stolen. Even if received by an honest operator, funds could be stolen if they are compromised. Also, custom URI schemes are not linkified when displayed in some messaging apps.

   Note the use of the ``zcash-data`` URI scheme, rather than the more elegant ``zcash``, because URIs of the form ``zcash:address?...`` are already used to specify Zcash addresses and payment requests in ZIP 321 [#zip321]_, by analogy to the ``bitcoin`` URIs of BIP 21. An alternative is to use ``zcash:v1/payment?...``; legacy software may parse this as a payment request to the address ``v1``, which is invalid. Another alternative is to use ``zcash-payment:v1?...``, which is appealing in terms of length and readability, but may be gratuitous pollution of the URI scheme namespace.

Another option, which can be added to any of the above, is to add a confirmation code outside the URI that needs to be manually entered by the user into the wallet app, so that merely intercepting the URI link would not suffice. This does not seem to significantly reduce risk in the scenarios considered, and so deemed to not justify the reduced usability.


Lifecycle Specification
=======================

The lifecycle of a Payment-Encapsulating URI consists of several stages, which in the usual case culminate in the funds being irrevocably deposited into the recipient’s personal wallet irrevocably:

Generating the notes and URI
----------------------------
The sender’s Zcash wallet app creates an ephemeral spending key, sends ZEC funds to the payment addressed derived from that key, and creates a Payment-Encapsulating URI that contains this ephemeral spending key and the newly-generated note commitments.

URI Transmission
----------------
The sender conveys the Payment-Encapsulating URI to the intended recipient, over some secure channel (e.g., an end-to-end encrypted messaging platform such as Signal, WhatsApp or Magic Wormhole; or a QR code scanned in person).

If transmitted via a human-readable medium, such as a messaging app, the Payment-Encapsulating URI MAY be accompanied by a contextual explanation that the URI encapsulates a payment, and a suggested action by the recipient to complete the process (see Usage Story above for an example).

When sent via a human-readable medium that consists of discrete messages, the message that contains the URI SHOULD NOT contain any payment-specific or manually-entered information outside the URI itself, since this information may not be visible to the recipient (see “Message Rendering” below).

From this point, and until finalization or cancellation (see below), from the sender’s perspective the payment is “in progress”; it SHOULD be conveyed as such to the sender; and MUST NOT be conveyed as “finalized” or other phrasing that conveys successful completion.

Message Rendering
-----------------
The recipient’s device renders the Payment-Encapsulating URI, or an indication of its arrival, along with the aforementioned contextual explanation (if any). The user has the option of “opening” the URI (i.e., by clicking it), which results in the device opening a Zcash wallet app, using the local platforms app link mechanism.

A messaging app MAY recognize Payment-Encapsulating URIs, and render them in a way that conveys their nature more clearly than raw URI strings. If the messaging medium consists of discrete messages, and a message contains one or more Payment-Encapsulating URIs, then the messaging app MAY assume that all other content in that message is automatically generated and contains no payment-specific or manually-generated information, and thus may be discarded during rendering.


Payment Rendering and Blockchain Lookup
---------------------------------------
The recipient’s Zcash wallet app SHOULD present the payment amount and MAY present the description, as conveyed in the URI, along with an indication of the tentative nature of this information.

In parallel, the wallet app SHOULD retrieve the relevant transactions from the Zcash blockchain, by looking up the transactionnote commitments given by the ``seedcmu`` parameter (this MAY use an efficient index, perhaps assisted by a server), and check whether:
* such transactions are indeed present on the blockchain
* the notes are unspent
* the notes can be spent using an ephemeral spending keys given by the ``key`` parameter.

The wallet conveys to the user one of the following states:

* *Ready-to-finalize*: The tests all verify, and the payment is ready to be finalized. The wallet SHOULD present the user with an option to finalize the payment (e.g., a “Finalize” button).
* *Invalid*: The tests fail irreversibly (e.g., some of the notes are already spent, or the amounts to not add up). The wallet MAY convey the reason to the user, but in any case MUST convey that the funds cannot be received.
* *Pending*: The tests fail in a way that may be remedied in the future, namely, some of the notes are not yet present on the blockchain (and no other tests are violated).

Within the *Pending* state, the wallet app MAY also consider “0 confirmations” transactions (i.e., transactions that have been broadcast on the node network but are neither mined nor expired), and convey their existence to the user. These do not suffice for entering the *Ready-to-finalize* state (since unmined notes cannot be immediately spent.)

The aforementioned conditions may change over time (e.g., the transactions may be spent by someone else in the interim), so the status SHOULD be updated periodically.

Finalization
------------
When the recipient chooses to finalize the payment, the wallet app generates transactions that spends the aforementioned notes (using the ephemeral spending key) and send these Zcash funds to the user’s own persistent payment address. These transactions carry the default expiry time (currently 100 blocks).

The recipient’s wallet app SHOULD convey the payment status as “Finalizing…” starting at the time that the uses initiates the finalization process. It MAY in addition convey the specific action done or event waited.

The sender’s wallet SHOULD convey the payment status as “Finalizing…” as soon as it detects that relevant transactions have been broadcast on the peer-to-peer network, or mined to the blockchain.

Once these transactions are confirmed (to an extent considered satisfactory by the local wallet app; currently 10 confirmations is common practice), their status SHOULD be conveyed as “Finalized”, by both the sender’s wallet app and the recipient’s wallet app. Both wallets MUST NOT convey the payment as “finalized”, or other phrasing that conveys irrevocability, until this point.

If these transactions expire unmined, or are otherwise rendered irrevocably invalidated (e.g., by a rollback), then both wallets’ status SHOULD convey this, and the recipient’s wallet SHOULD revert to the “Payment Rendering and Blockchain Lookup” stage above.

Payment Cancellation
--------------------
At any time prior to the payment being finalized, the sender is capable of cancelling the payment, by themselves finalizing the payment into their own wallet (thereby “clawing back” the funds). If the wallet has not yet sent, for inclusion in the blockchain, any of the transactions associated with the ephemeral spending key, then cancellation can also be done by discarding these transactions or aborting their generation. The sender’s wallet app SHOULD offer this feature, and in this case, MUST appropriately handle the race condition where the recipient initiated finalization concurrently.


Status View
------------

Wallet apps SHOULD let the user view the status of all payments they have generated, as well as all inbound payment (i.e., Payment-Encapsulating URIs that have been sent to the app, e.g., by invocation from messaging apps). The status includes the available metadata, and the payment’s current state. When pertinent, the wallet app SHOULD offer the ability to finalize any *Pending* inbound payment, and MAY offer the ability to cancel any outbound payment.

Wallet apps SHOULD actively alert the user (e.g., via status notifications) if a payment that they sent has not been finalized within a reasonable time period (e.g., 1 week), and offer to cancel the payment.


Security Considerations
=======================

* Anyone who intercepts the Payment-Encapsulating URIs may steal the encapsulated funds. Therefore, Payment-Encapsulating URIs should be sent over a secure channel, and should be kept secret from anyone but the intended recipient.
   The Payment-Encapsulating URI is like a magic spell that will teleport the money to the first person that clicks it and then does "finalize".

* Payment-Encapsulating URIs may be captured by malicious local apps on the sender or receiver’s platform, e.g., by screen capturing or clipboard eavesdropping. Wallet apps should use the platform’s interaction and communication facilities in a way that minimizes these risks (e.g., use the “Share” API rather than a clipboard that is visible to all apps).

* Likewise, if the URI is transferred by presenting and optically scanning a QR code, anyone who observes this QR code may be able to finalize the payment and thus take ownership of the funds before the intended recipient. For example, an attacker may use a telephoto lens aimed at a point-of-sale terminal to steal QR-encoded payments sent to that terminal.

* Users may have casually-established communication channels (e.g., they have entered the phone number of a new contact without bothering to double-check it), but may later mistakenly consider these to be adequately-authenticated secure channels for the purpose of sending Payment-Encapsulating URI. Wallet apps should mitigate this where feasible, e.g., by indicating that the chosen messaging channel is previously-unused and thus should be more carefully checked.

* Users may incorrectly believe that the payment has been irrevocably received even though they have not invoked the finalization procedure, or even though the finalization procedure has failed. Wallet software should correctly convey the status and set expectations, as discussed above.

* Payment recipients may not notice the incoming payment notification and act on it (i.e., invoke finalization) in a timely fashion. By the time they see it, the payment may have been cancelled by the sender.

* Users may not understand that Payment-Encapsulating URIs are for one-time use, and attempt to use the same URI for multiple people or payments, resulting in race conditions on who receives the funds.

* Users may confuse Payment-Encapsulating URIs (as specified in the current ZIP) with Payment Request URIs of the form ``zcash:payment-address?amount=...``. (The latter are a de facto standard, and will be specified in the forthcoming ZIP 321 [#zip321issue]_). Normally these serve different workflows, and work in opposing directions (send vs. receive of funds), and thus ought to not arise in ambiguous context. Wallet apps should take care to not create or send a Payment-Encapsulating URI (which is for *sending* funds) in a context where the user may be intending to *receive* funds.

* Users may attempt to use a Payment-Encapsulating URI as a “cold wallet”, e.g., by writing the URI on paper and putting it in a safe. This is dangerous. The spending key is known to the sending wallet at the time when the URI is produced, and possibly also at other times (e.g., if there are storage remnants, or if deterministic derivation is used; see “Ephemeral key derivation” below). Thus, an adversary who compromises the sending wallet may drain the cold wallet. 

* The act and timing of finalizing a payment is visible to the sender, which may be a privacy leak. Likewise, if the on-chain transactions are sent in advance, their timing can be linked to the later payment, which may be a privacy leak.

* The payment amount is readily visible to anyone who observes the Payment-Encapsulating URI, even in retrospect after payment has already been finalized (e.g., if their device or chat log backups are later compromised). This may be a privacy concern, and in particular may put recipients of large payments at risk of undesired attention.

* Users attempting to follow Payment-Encapsulating URIs as a regular HTTPS hyperlink may inadvertently leak the payment information to a remote attacker, if all layers of defense listed in `Rationale for URI Format`_ are somehow breached.

* The owner of the ``withzcash.com`` domain effectively controls the whitelist of apps that may be launched by users’ platform to handle URI-Encapsulated Payments using the applink_ mechanism. If the whitelist is too *permissive* and includes a malicious or vulnerable app, and a user installs that app (which itself may be subject to the platform vendor’s app review mechanism), then the user is placed at risk of having their payments intercepted by an attacker. Conversely, if the whitelist is too *restrictive*, or altogether unavailable, then users would not be able to trigger desirable wallet apps by simply following links, and would need to instead ”share” the message containing the URI into their wallet app (note that, as discussed above, clipboard copy-and-paste is insecure).

* Usage of Payment-Encapsulating URIs may train users to, generally, click on other types of URI/URL links sent in other messaging contexts. Malicious links sent via unauthenticated messaging channels (e.g., emails and SMS texts) are a common attack vector, used for exploiting vulnerabilities in the apps triggered to handle these links. Even though the fault for vulnerabilities lies with those other apps, and even though this ZIP uses deep link URIs in the way intended, there are none the less these negative externalities to encouraging such use.

* 

Design Decisions and Rationale
==============================

See `Rationale for URI Format`_ above. Moreover:

1. The metadata (amount and description) is provided within the URI. An alternative would be to encode the description in the encrypted memo fields of the associated shielded transactions, and compute the amount from those transactions. However, in that case the metadata would not be available for presentation to the user until the transactions have been retrieved from the blockchain.

2. We support multiple spending keys and multiple notes in one URI, because these payments may be speculatively generated and mined before the payment amount is determined (to allow payments with no latency). For example, the sending wallets may pre-generate transactions for powers-of-2 amounts, and then include only a subset of them in the URI, totalling to the desired amount.

3. We do not include the sender or receiver’s identity in the URI, because the sending wallet many not know the name of who it is sending to (or even from). Moreover there is the risk that fraudulent sender/recipient information could be used. If necessitated by circumstances (e.g., the `Travel Rule`_), claimed sender and recipient identity can be included in ``desc`` parameter.


Open Questions
==============

Ephemeral Key Derivation
------------------------
Specify how the ephemeral spending keys can be derived from a seed a la ZIP 32, so that if a wallet is recovered from backup, sent-but-unfinalized payments can be reclaimed.
This requires a deterministic key-derivation mechanism, and means to find payments that can be recovered given just the wallet seed and the blockchain ledger.

Sketch:
Use a ZIP 32 derivation pathway to obtain a child extended spending key from path m_Sapling/zip_number'/coin_type'/payment_index'
Implementations need to remember which payment_index values they have used (in range 0..2^31), and not reuse them.
Convert the child ExtSK into a “URI seed” (e.g. hash the entire key), and provide that to the recipient.
The intent of this step is to shorten the value that goes into the URI, while keeping it linked to the sender’s backed-up wallet seed for recovery purposes.
The length of this URI seed can be “short” (e.g. 128 bits instead of 256) given that funds are not intended to be stored long-term underneath this secret (one of the sender or recipient is expected to scrape funds back into a long-term address)
Use PRF^expand on the URI seed with to-be-defined domain separation to obtain 64 bytes. Split this into two 32-byte values.
First 32-byte value is sk_m; derive spending key from this as in the spec / ZIP 32.
Second 32-byte value is the root for deriving randomness following ZIP 212.


URI Usability
-------------
The URI could  be changed in several ways due to usability concerns:

1. It may be desirable to prevent the ``amount`` and ``desc`` parameters from being human readable. This is to discourage people from just looking at the URI, seeing the numbers and text, and mistakenly thinking this is already a confirmation of successful receipt (without going through the finalization process). 

2. Perhaps the URI should be contain the phrase “password” early on (e.g., ``zcash-data:/payment/v1/password=``, as a cue that this string must be kept secret. (Note that technically nothing here is a password in the usual sense of the term.)

3. Perhaps we should actually use BIP 39 words as an actual password. So you could memorize it or read it over the phone. The BIP 39 words can be embedded in the URI itself (which is highly unusual):
   ``zcash-data:payment/v1/password=witch+collapse+practice+feed+shame+open+despair+creek+road+again+ice+least``
   or
   ``zcash-data:payment/v1/password=WitchCollapsePracticeFeedShameOpenDespairCreekRoadAgainIceLeast``
   This provides an additional cue that the URI contains a sensitive password (for users who are accustomed to BIP 39 style word lists; to others the Base 64 encoding may be more evocative of a password). Moreover, users may discover the fact that they can manually send these words to recipients, in writing or verbally, as a way to send money without a textual messaging service.   
   Alternatively, the BIP 39 words can be used as an alternative syntax for the encapsulation, without the confusing-to-humans URI syntax (but generating this alternative syntax this may complicate the UI).


Identifying Notes
-----------------
The recipient’s wallet needs to identify the notes related to the payment (and the on-chain transactions that contain them), in order to verify their validity and then (during the finalization process) spend them. 

In the above description, we explicitly list the notes involved in the payment (which are easily mapped to the transactions containing them, using a suitable index). This results in long URIs when multiple notes are involved (e.g., when using the aforementioned “powers-of-2 amounts” technique).

Instead, we can have the nodes be implicitly identified by the spending key (or similar) included in the URI. This can make URI shorter, thus less scary and less likely to run into length limits (consider SMS). The following alternatives are feasible:

0. Explicitly list the note commitments within the URI.

1. Include only the spending key(s) in the URI, and have the recipient scan the blockchain using the existing mechanism (trial decryption of the encrypted memo field). This is very slow, and risks denial-of-service attacks. Would be faster in the nominal case if the scanning is done backwards (newest block first), or if told by the sender when the transactions were mined; but scanning the whole chain for nonexistent transactions (perhaps induced by a DoS) would still take very long.

2. Derive a tag from a seed included in the URI, and put this tag within the encrypted memo field of the output descriptors in the associated transactions. Put the tag plaintext within the space reserved for the memo field ciphertext (breaking the AEAD abstraction). The recipient’s wallet (or the service assisting it) would maintain an index of such tags, and efficiently look up the tags derived from the URI.
   The tags are publicly-visible and thus may leak information on the payment amount (e.g., when using the powers-of-2 pre-generation technique).

3. Similarly to the above, but place the tag in an additional zero-value output descriptor added to each pertinent transaction. The recipient can recompute this note commitment and use that as the identifier, to be looked up in an index in order to locate the transaction.
   Here too, the tags are publicly-visible and thus may leak information on the payment amount (e.g., when using the powers-of-2 pre-generation technique).

4. Have the URI include a seed and the amount of the (single) output note. Let the seed determine not only the spending key, but also all randomness involved in the generation of the note. Thus, the recipient can deterministically derive the note commitment from the seed and amount, and look it up to find the relevant transaction. This requires the recipient (or the server assisting them) to maintain an index mapping note commitments (of output descriptors that are the first in their transaction) to the transaction that contains them. Additional notes can be included in the same transaction.




Other Questions
---------------
Should senders delay admitting a generated transaction by a random amount to prevent traffic analysis (i.e., so the messaging service operator cannot correlate messages with on-chain transactions)?

Consider the behavior in case a chain reorgs invalidates a sent payment. Should we specify a Merkle root or block hash to help detect this reason for payment failure? Or have some servers that maintain a cache of payments that were invalidated by reorgs?


References
==========

.. [#RFC2119] `Key words for use in RFCs to Indicate Requirement Levels <https://tools.ietf.org/html/rfc2119>`_
.. [#RFC3986] `Uniform Resource Identifier (URI): Generic Syntax <https://tools.ietf.org/html/rfc3986>`_
.. [#protocol] `Zcash Protocol Specification, Version 2019.0.3 or later [Overwinter+Sapling] <https://github.com/zcash/zips/blob/master/protocol/protocol.pdf>`_
.. [#zip321] `ZIP 321: Payment Request URIs
 <https://zips.z.cash/zip-0321>`_

.. _Sapling master key generation: https://zips.z.cash/zip-0032#sapling-master-key-generation
.. _App Links: https://developer.android.com/training/app-links
.. _Universal Links: _https://developer.apple.com/documentation/uikit/inter-process_communication/allowing_apps_and_websites_to_link_to_your_content
.. _App URI handlers: https://docs.microsoft.com/en-us/windows/uwp/launch-resume/web-to-app-linking 
.. _Travel Rule: https://www.fincen.gov/sites/default/files/2019-05/FinCEN%20Guidance%20CVC%20FINAL%20508.pdf


Publication Blockers
====================
* Register all domains mentioned in this draft (``withzcash.com``, ``testzcash.com``).
* Clean up semantics.


