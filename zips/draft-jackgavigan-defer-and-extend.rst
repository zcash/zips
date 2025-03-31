::

    ZIP: XXX
    Title: Defer Lockbox Distribution and Extend the Current Dev Fund
    Owners: Jack Gavigan <jackgaviganzip@gmail.com>
    Status: Draft
    Category: Consensus / Process
    Created: 2025-03-31
    License: MIT
    Pull-Request: <https://github.com/zcash/zips/pull/???>


Terminology
===========

The key words "SHALL NOT", and "SHOULD" in this document are to be interpreted as 
described in BCP 14 [#BCP14]_ when, and only when, they appear in all 
capitals.

"Zcash Community Advisory Panel", also called "ZCAP", refers to the panel of
community members assembled by the Zcash Foundation and described at [#zcap]_.

"Zcash Shielded Assets", also called "ZSAs", refers to the protocol changes
described in draft ZIP 226 [#zip-0226]_ and draft ZIP 227. [#zip-0227]_ 

The character § is used when referring to sections of the Zcash Protocol
Specification. [#protocol]_

The term "Mainnet" is to be interpreted as described in § 3.12 ‘Mainnet and 
Testnet’. [#protocol-networks]_

"Lockbox" refers to the in-protocol lockbox described in ZIP 1015, [#zip-1015]_ 
and specified in ZIP 2001. [#zip-2001]_

"Current Dev Fund" refers to the block subsidy allocation described in ZIP 1015, 
[#zip-1015]_ and specified in ZIP 2001. [#zip-2001]_

"Zcash Community Grants", also called "ZCG", refers to the committee described 
in [#zip-1015]_.

"Bootstrap Project", also called "BP", refers to the 501(c)(3) nonprofit 
corporation of that name.

"Zcash Foundation", also called "ZF", refers to the 501(c)(3) nonprofit 
corporation of that name.

"Electric Coin Company", also called "ECC", refers to the Zerocoin Electric 
Coin Company, LLC.


Abstract
========
This ZIP proposes expressly prohibiting any disbursement of funds from the 
Lockbox until after Zcash Shielded Assets is active on Mainnet, and extending 
the Current Dev Fund for one year. 


Motivation
==========

Zcash Shielded Assets (ZSAs) is arguably the single most impactful change to the 
Zcash protocol since the launch of Zcash in late 2016. There is clear consensus
support for ZSAs across the Zcash community, and a ZCAP poll carried out in 
August 2021 indicated that the Zcash community believed that ZSAs should be 
first priority for Zcash following the activation of NU5. [#priorities]_

In January 2022, ZCG provided funding for QEDIT to research and implement ZSAs 
[#zsagrant]_, and the functionality was demonstrated using a fork of zcashd 
during Zcon4 in August 2023. [#zsademo]

Due to ECC's decision to no longer support new protocol features in the zcashd 
node implementation, zcashd must be deprecated before ZSAs can activate on 
Mainnet. Zcashd deprecation was expected to be complete by April 2025. However, 
the necessary work was not prioritized. [#nu7-timeline]_ As a result, as of March 
2025, there is no confirmed schedule for zcashd deprecation (and, therefore, no 
schedule for the activation of ZSAs on Mainnet). 

The activation of ZSAs on Mainnet is also dependent on the merging of necessary 
code changes into the core Zcash cryptographic libraries and the new Zcash stack 
(Zebra, Zaino and Zallet) that will replace zcashd. With limited resources, 
anything that distracts the engineers who are working on the new stack is likely 
to delay ZSA activation further. 

In addition, any changes to the core Zcash cryptographic libraries or Zebra -- 
including the definition and implementation of a Lockbox distribution mechanism 
-- would require that QEDIT rebase their code changes, incurring further cost 
and delay. 

This ZIP therefore proposes expressly prohibiting any disbursement of funds from 
the Lockbox until after Zcash Shielded Assets is active on Mainnet. 

It is anticipated that the majority of teams currently working on the development 
or outreach required to deprecate zcashd, and activate ZSAs, will require funding 
in order to see this effort through to a successful conclusion. Following the end 
of direct funding of BP and ZF, ZCG is the sole source of funding in the Zcash 
ecosystem. 

Under the existing consensus rules, after block height 3146400, 100% of the 
block subsidies would be allocated to miners, and no further funds would be 
automatically allocated to the Lockbox or to ZCG. Consequently, unless the 
community takes action to approve new block-subsidy-based funding, existing 
teams dedicated to development or outreach or furthering charitable, 
educational, or scientific purposes would likely need to seek other sources of 
funding; failure to obtain such funding would likely impair their ability to 
continue serving the Zcash ecosystem.

This ZIP therefore proposes extending the Current Dev Fund by one year, to 
ensure that ZCG receives sufficient funding to enable it to fund teams that are 
carrying out the work required to deprecate zcashd, and activate ZSAs. 


Requirements
============

This ZIP is dependent on ZIP 1015, [#zip-1015]_ and ZIP 2001. [#zip-2001]_ 
Amendments to these ZIPs are specified below. 


Non-requirements
================



Specification
=============


Changes to ZIP 1015 [#zip-1015]_
-------------------------------

In the section **Funding streams** [#zip-1015-funding-streams]_, the **End height** for Mainnet will be modified from 3146400 to 3566400, and the **End height** for Testnet will be modified from 3396000 to 3816000. 

In the section **Zcash Community Grants (ZCG)** [#zip-1015-zcg]_, a new constraint will be inserted: 

    11. Priority SHOULD be given to major grants that directly further the goal of deprecating zcashd, and activating ZSAs on Mainnet (until the latter objective is achieved). 


In the section **Requirements** [#zip-1015-requirements]_, a new paragraph will be inserted: 

    3. **Lockbox Distribution Prerequisite**: A mechanism for disbursing the 
       accumulated funds from the lockbox SHALL NOT be implemented until Zcash
       Shielded Assets functionality has activated on Mainnet. 


Changes to ZIP 2001 [#zip-2001]_
-------------------------------

*To be confirmed*


References
==========

.. [#BCP14] `Information on BCP 14 — "RFC 2119: Key words for use in RFCs to
    Indicate Requirement Levels" and "RFC 8174: Ambiguity of Uppercase vs
    Lowercase in RFC 2119 Key Words" <https://www.rfc-editor.org/info/bcp14>`_
.. [#zcap] `Zcash Community Advisory Panel <https://zfnd.org/zcap/>`_
.. [#zip-0226] `ZIP 226: Transfer and Burn of Zcash Shielded Assets 
    <zip-0226.rst>`_
.. [#zip-0227] `ZIP 227: Issuance of Zcash Shielded Assets <zip-0227.rst>`_
.. [#protocol] `Zcash Protocol Specification, Version 2024.5.1 [NU6] or later 
    <protocol/protocol.pdf>`_
.. [#protocol-networks] `Zcash Protocol Specification, Version 2024.5.1 [NU6]. 
    Section 3.12: Mainnet and Testnet <protocol/protocol.pdf#networks>`_
.. [#zip-1015] `ZIP 1015: Block Subsidy Allocation for Non-Direct Development 
    Funding <zip-1015.rst>`_
.. [#zip-2001] `ZIP 2001: Lockbox Funding Streams <zip-2001.rst>`_
.. [#priorities] `Zcash Foundation ZCAP August 2021 Consultation 
    <https://vote.heliosvoting.org/helios/elections/5dd57b92-01ed-11ec-a0a8-ae3066fac55d/view>`_
.. [#zsagrant] `A Proposal for Shielded Assets (ZSA/UDA) for DeFi on Zcash 
    <https://forum.zcashcommunity.com/t/40520/53>`_
.. [#zsademo] `ZSA Demo during Zcon4 
    <https://www.youtube.com/watch?v=bRdNvepJVXM&t=793s>`_
.. [#20240419arboristcall] `Dedicated Zcash Arborist Call (ZSAs, NU6, & NU7), 
    19th April 2024 <https://youtu.be/C_S5e2WNIe8?si=32xanF7jV3KlFqxo&t=2640>`_
.. [#nu7-timeline] `NU7 Timeline and the Dev Fund Expiration 
    <https://forum.zcashcommunity.com/t/50134/3>`_
.. [#zip-1015-funding-streams] `ZIP 1015: Block Subsidy Allocation for Non-Direct 
    Development Funding. Section: Funding Streams 
    <zip-1015.rst#funding-streams>`_
.. [#zip-1015-zcg] `ZIP 1015: Block Subsidy Allocation for Non-Direct Development 
    Funding. Section: Zcash Community Grants (ZCG) 
    <zip-1015.rst#zcash-community-grants-zcg>`_
.. [#zip-1015-requirements] `ZIP 1015: Block Subsidy Allocation for Non-Direct Development 
    Funding. Section: Requirements 
    <zip-1015.rst#requirements>`_
