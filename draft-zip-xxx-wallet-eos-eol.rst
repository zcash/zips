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
that should tolerate the pass of time. While it is expected that the network implementing 
these decentralized protocols live indefinitely, wallet applications might be subject to
shorter lifecycles. There are many reasons for them to reach a point in time where they will
longer able to keep functioning. Whatever the reason might be, this document considers that 
the result for end-users is indistinct: they will not be able to carry on their usual activities
on the application once the EOL/EOS day comes. To that end, this ZIP will discuss the topic of
sunsetting end-user applications gracefully by anticipating the moment as an invariant of any
product's lifecycle. 

Scope of an EOS/EOL event
-------------------------

The breath of an application userbase and ecosystem may vary depending of the number of Operating
Systems, Platforms and/or architectures it supports. 

Complete EOS/EOL for 100% of the userbase
'''''''''''''''''''''''''''''''''''''''''
It might be the case that the whole product ceases to exist for all cases, which would be the more 
drastic scenario for an end-user application. After EOL/EOS no user will be able to use the application
as normally.

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
"Caused by Contigency or third party". 


EOL / EOS initiated by Maintainer(s)
------------------------------------

Programmed obsolescense
'''''''''''''''''''''''

Programmed Obsolescense is imposed by hardware and software manufacturers may unilaterally 
force users of otherwise perfectly operational products to cease to use them by crippling, 
limiting or entirely disabling their capabilities, leaving the users with no choice than
acquiring a newer version or migrating to a different product.

Sanctions, Embargo, Ban, Closure or Prosecution
'''''''''''''''''''''''''''''''''''''''''''''''

Wallet Maintainers might be based in jurisdictions subject to geopolitical Sanctions, Embargos
and be threatened or forced to cease their operations. Maintainers might also be legally bound
to cease and desist of their operations because of regulations on their jurisdictions, as well
as ceasing to provide support to certain subset of their whole userbase. 



Requirements
============

{Describe design constraints on, or goals for the solution -- typically one
paragraph for each constraint or goal. Again, don't actually specify anything
here; this section is primarily for use as a consistency check that what is
specified meets the requirements.}


Non-requirements
================

Wallets that are considered to be "in testing", "alpha", "beta" or "developer preview"
programs and openly adversiting that to their users, therefore, not considered to be deployed 
to an open audience as a finished product that is intended for end-users MAY opt not to follow 
this practices. Althought, they SHOULD consider implementing them as part of their process to 
delivering the application into production.


Specification
=============

{Replace this entire section.}

The Specification section describes what should change, using precise language and
conformance key words. Anything that is *required in order to implement the ZIP*
(or follow its process, in the case of a Process ZIP) should be in this section.

Avoid overspecification! Also avoid underspecification. Specification is hard.
Don't be afraid to ask for help.

Feel free to copy from other ZIPs doing similar things, e.g. defining RPC calls,
consensus rules, etc.

ZIPs MUST take into account differences between the Zcash Mainnet and Testnet
[#protocol-networks]_ where applicable. A consensus ZIP MUST be able to be deployed
on both Mainnet and Testnet.

Unless the specification is particularly simple, you will need to organise it under
subheadings.

Example subheading
------------------

At least while the ZIP is in Draft, we encourage writing open questions and TODOs.

Open questions
''''''''''''''

* What happens if a full validator can't parse the fandangle as a doohicky?

TODO: define byte encoding for the Jabberwock.

Comparison of ZIPs to RFCs
--------------------------

Like RFCs, ZIPs are precise technical documents that SHOULD give enough
implementation information to implement part of a Zcash-related protocol or follow a
Zcash-related process.

ZIPs are different from RFCs in the following ways:

* Many (but not all) ZIPs are "living documents"; they are updated in-place as
  the relevant areas of the protocol or process change. Unlike in the RFC process,
  making a change in an area described by a published ZIP does not *necessarily*
  require creating a new ZIP, although that is an option if the change is extensive
  enough to warrant it.
* The expected structure of a ZIP is more constrained than an RFC. For example,
  the Specification section is REQUIRED, and all of the conformance requirements
  MUST go in that section. The ZIP editors will help you to ensure that things
  go in the right sections.
* Security considerations SHOULD be spread throughout the text, in the places
  where they are most relevant.

Using mathematical notation
---------------------------

Embedded :math:`\LaTeX` is allowed and encouraged in ZIPs. The syntax for inline
math is "``:math:`latex code```" in reStructuredText or "``$latex code$``" in
Markdown. The rendered HTML will use KaTeX [#katex]_, which only supports a subset
of :math:`\LaTeX\!`, so you will need to double-check that the rendering is as
intended.

In general the conventions in the Zcash protocol specification SHOULD be followed.
If you find this difficult, don't worry too much about it in initial drafts; the
ZIP editors will catch any inconsistencies in review.

Notes and warnings
------------------

.. note::
    "``.. note::``" in reStructuredText, or "``:::info``" (terminated by
    "``:::``") in Markdown, can be used for an aside from the main text.

    The rendering of notes is colourful and may be distracting, so they should
    only be used for important points.

.. warning::
    "``.. warning::``" in reStructuredText, or "``:::warning``" (terminated by
    "``:::``") in Markdown, can be used for warnings.

    Warnings should be used very sparingly — for example to signal that a
    entire specification, or part of it, may be inapplicable or could cause
    significant interoperability or security problems. In most cases, a "MUST"
    or "SHOULD" conformance requirement is more appropriate.

Valid reStructuredText
----------------------

This is optional before publishing a PR, but to check whether a document is valid
reStructuredText, first install ``rst2html5``. E.g. on Debian-based distros::

  sudo apt install python3-pip pandoc perl sed
  pip3 install docutils==0.19 rst2html5

Then, with ``zip-xxxx.rst`` in the root directory of a clone of this repo, run::

  make zip-xxxx.html

(or just ``make``) and view ``zip-xxxx.html`` in a web browser.

Conventions for references
--------------------------

For references to the Zcash protocol specification, prefer to link to a section
anchor, and name the reference as ``[#protocol-<anchor>]``. This makes it more likely
that the link will remain valid if sections are renumbered or if content is moved.
The anchors in the protocol specification can be displayed by clicking on a section
heading in most PDF viewers. References to particular sections should be versioned,
even though the link will point to the most recent stable version.

Do not include the "``https://zips.z.cash/``" part of URLs to ZIPs or the protocol spec.


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
