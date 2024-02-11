::

  ZIP: Unassigned {numbers are assigned by ZIP editors}
  Title: Zcash Wallet Application End of Life / End Of Service Best practices
  and recommendations
  Owners: Francisco Gindre <codebuffet@proton.me>
          
  Credits: Kris Nuttycombe
           ...
  Status: Draft
  Category: Wallet
  Created: 2024-02-03
  License: MIT
  Pull-Request: TBD

Terminology
===========

The key words "MUST", "REQUIRED", "MUST NOT", "SHOULD", and "MAY" in this
document are to be interpreted as described in BCP 14 [#BCP14]_ when, and
only when, they appear in all capitals.

Maintainer: the individual, group or organization responsible for the 
operation, maintenance, development or support of a Zcash wallet software
application.

End-user: the final user of the wallet. An individual, group or organization 
that makes use of the wallet application. Maintainers MUST NOT assume that end-users
have any other technical knowledge than the information or education their application
provides with its intended use. 

End of Life / End of Service: refers to a point in time where the wallet
software will no longer be actively maintained or developed, therefore its
operation cannot be guaranteed anymore or terminated indefinitely.

Self-custody wallets: Wallet applications that require end-users to maintain a 
sovereign custody of their private keys and/or the input they originate from (E.g: 
entropy bytes or BIP-39 style mnemonic seed phrases)


Abstract
========

Zcash Wallet Applications might no longer be maintained, supported or serviced by
their maintainter from a point in time onwards. This ZIP defines a set of best practices
and recommendations to minimize the impact of the End of Service of a Zcash wallet 
application onto its current or potential users.


Motivation
==========

Cryptocurrency peer-to-peer networks are designed to be long-lived decentralized systems
that should tolerate the pass of time. While it is considered that the network implementing 
these decentralized protocols would live indefinitely, wallet applications might be subject to
shorter lifecycles. There are many reasons for them to reach a point in time where they will
longer able to keep functioning. Whatever the reason might be, this document considers that 
the result for end-users is indistinct: they will not be able to carry on their usual activities
on the application once the EOL/EOS day comes. To that end, this ZIP will discuss the topic of
sunsetting end-user applications gracefully by anticipating the moment as an invariant of any
product's lifecycle. 


Requirements
============

This document aims to ensure the ability for user to exercise complete sovereign self-
custody of their keys and funds related to them. Although it will refer specifically to 
non-custodian wallets (or similar applications that handle Zcash keys), it can also apply to
custodian applications reaching EOS/EOL. The goal of this ZIP is to ensure that the user is in 
control of its funds (or access to them) at all times, and that they can be provided ways to
keep that access beyond a specific product EOS/EOL in a "hassle-free" and user-friendly way.
Maintainers SHOULD always be eagerly looking to provide well-tested, dependable and mission
critical use cases that produce an application feature that can be made available to users in 
the case of an EOS/EOL scenario.


Non-requirements
================

Wallets that are considered to be "in testing", "alpha", "beta" or "developer preview"
programs and openly adversiting that to their users, therefore, not considered to be deployed 
to an open audience as a finished product that is intended for end-users MAY opt not to follow 
this practices. Althought, they SHOULD consider implementing them as part of their process to 
delivering the application into production.


Specification
=============

What is an EOS/EOL event?
-------------------------
End of Life / End of Service: refers to a point in time where the wallet
software will no longer be actively maintained or developed, therefore its
operation cannot be guaranteed anymore or terminated indefinitely.


Scope of an EOS/EOL event
-------------------------

The breath of an application userbase and ecosystem may vary depending of the number of Operating
Systems, Platforms and/or architectures it supports. 

Complete EOS/EOL for 100% of the userbase
'''''''''''''''''''''''''''''''''''''''''
It might be the case that the whole product ceases to exist for all application versions on all target
Operating Systems or Platforms. This would be the more  drastic scenario for an end-user application. 
After EOL/EOS no user will be able to use the application as normally.

Partial EOS/EOL for a portion of the userbase
'''''''''''''''''''''''''''''''''''''''''''''
A subset of the userbase becomes unsupported. For example, a range of versions for a given target OS
will become unsupported at a given date (regardless the reason). Maintainers MUST scope and assess 
the impact on their userbase to determine if there is a portion of which that will not be able to 
continue to use their application with their current host device. If it is the case that 1 to N users 
would eventually be unable to continue operating the application as usual after the EOS/EOL date, 
Maintainers MUST treat those users as if they were going through "Complete EOS/EOL for 100% of the
userbase". 

The subsections below illustrate some of the scenarios that were taken into consideration when
creating this ZIP. We grouped them into two broad categories: "Initiated by Maintainers" or 
"caused by Contigency or third party". 


EOL / EOS initiated by Maintainer(s)
------------------------------------

Unilateral End of Support
'''''''''''''''''''''''''
Maintainers will no longer continue to provide support to all or some of the aplications versions.
Casting a complete or a partial EOS/EOL event onto their userbase. 


EOL / EOS caused by continency or a third party
-----------------------------------------------

Programmed obsolescense
'''''''''''''''''''''''

Programmed Obsolescense is imposed by hardware and software manufacturers. They may 
unilaterally force users of otherwise perfectly operational products to cease to use them 
by limiting or entirely disabling their capabilities, leaving the users with no other choice than
acquiring a newer version or migrating to a different product. 

Example: 
After 19 Sep 2017, iOS 10 users won't be able to get any updates for their OS. Maintainers 
might be not able to provide updates to their applications either. They decide to end support
for iOS 10. Users whose devices can't upgrade will have to be treated as EOS/EOL'd users. 


Sanctions, Embargo, Ban, Closure or Prosecution
'''''''''''''''''''''''''''''''''''''''''''''''

Wallet Maintainers might be based in jurisdictions subject to geopolitical Sanctions, Embargos
and be threatened or forced to cease their operations. Maintainers might also be legally bound
to cease and desist of their operations because of regulations on their jurisdictions, as well
as ceasing to provide support to certain subset of their whole userbase. Maintainers SHOULD
be aware of their jurisdictional risks and act accordingly to provided support over possible
imposed EOS/EOL scenario.

Example: 

Country A forbids the use of cryptocurrency. "SomeWallet" is a very popular mobile crypto wallet
in country A. Developers of "SomeWallet" are informed that their application won't be available
on official distribution platforms (like App Store or Google Play) for the region of Country A
from date YYYY-mm-dd onwards. Developers of "SomeWallet" have to follow this ZIP's practices to
treat this event as a Partial EOS/EOL event. 


Best Practices for handling EOS/EOL events on wallet applications
-----------------------------------------------------------------

Anticipating to the event
`````````````````````````
"Unhappy" paths are better than absense of a path. Wallet developers SHOULD consider that eventually,
users will have to move out from their application. Either by their own choice or by force, users of
a Zcash wallet will have to go through the process of ceasing to use this application in favor of 
another one. It could also be the case that users stay within the same application but switch to a 
different device. **Building these use cases** into the Business as Usual (BAU) use cases, will give
developers a better understanding of what will eventually be needed in the case of having to enforce an
EOS/EOL event. 

Maintain an cccurate inventory or mind-map of the User Data that the application handles
`````````````````````````````````````````````````````````````````````````````````````````

Wallet maintainters SHOULD account for the kind of information that is locally stored on the user's device. 
Although a great amount of information could be restored and/or derived from the blockchain with the 
help of the user's private and public keys, maintainters SHOULD keep a record of which information
can be restored from the blockchain and which one is product of regular use and interaction and would
still be relevant for the user when an EOS/EOL event forces users to move to another version or wallet
application. 

Example of recoverable information:

- On-chain information that can be recreated with user's viewing keys.

Example of potentially non-recoverable information:
- A local address book that the wallet maintained for the user.
- local user-preferences of the user like, default currency conversion, locale, account pet-names, 
- imported viewing keys not related to the user's seed phrase.
- internal datastructures that the wallet application uses to enhance the User Experience

Educate the user on the information that can or can't be backed up or exported from the wallet
`````````````````````````````````````````````````````````````````````````````````````````````
TODO

Use familiar building blocks
````````````````````````````
Wallet maintainers SHOULD reuse the same UI and UX components that the user is familiar with from 
everyday usage to handle EOS/EOL events. Additional UI elements MAY be used to convey a sense of 
urgency, call user's attention or stress out critical aspects that cannot be ignored by the user.

Example: 
If the maintainers determine that to handle an EOS/EOL event, the user should backup its keys and 
later restore it into another application or a subsequent version of the current application, the
application should reuse an existing backup flow (if available) that the user is already familiar
with or that it could remembrance from when it first signed into the application. 


Support Offline / disconnected types of use modes
`````````````````````````````````````````````````
TODO

Tombstone Releases
``````````````````
TODO



Open questions and TODOs
========================

- Shall the ZIP recommend that EOS/EOL features be bundled in and hidden from the public
regardless?
- [TODO] EOS/EOL type flow chart 
- [TODO] Add References
- [TODO] Provide offline modes
- [TODO] Tombstone Releases
- [TODO] User education on restorable or ephemeral information

Reference implementation
========================

{This section is entirely optional; if present, it usually gives links to zcashd or
zebrad PRs.}


References
==========

.. [#BCP14] `Information on BCP 14 — "RFC 2119: Key words for use in RFCs to Indicate Requirement Levels" and "RFC 8174: Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words" <https://www.rfc-editor.org/info/bcp14>`_
.. [#protocol] `Zcash Protocol Specification, Version 2022.3.8 or later <protocol/protocol.pdf>`_
.. [#protocol-introduction] `Zcash Protocol Specification, Version 2022.3.8. Section 1: Introduction <protocol/protocol.pdf#introduction>`_
.. [#protocol-blockchain] `Zcash Protocol Specification, Version 2022.3.8. Section 3.3: The Block Chain <protocol/protocol.pdf#blockchain>`_
.. [#protocol-networks] `Zcash Protocol Specification, Version 2022.3.8. Section 3.12: Mainnet and Testnet <protocol/protocol.pdf#networks>`_
.. [#katex] `KaTeX - The fastest math typesetting library for the web <https://katex.org/>`_
.. [#zip-0000] `ZIP 0: ZIP Process <zip-0000.rst>`_
