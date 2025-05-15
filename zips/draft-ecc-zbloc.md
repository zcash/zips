    ZIP: XXX
    Title: Zcash Governance Bloc
    Owners: Josh Swihart <josh@electriccoin.co>
            Daira-Emma Hopwood <daira-emma@electriccoin.co>
    Credits: Kris Nuttycombe
             Jack Grigg
             Tatyana Peacemonger
             Chris Tomeo
    Status: Obsolete
    Category: Consensus / Process
    Created: 2025-01-28
    License: MIT
    Pull-Request: <https://github.com/zcash/zips/pull/???>


# Terminology

The key words "MUST", "REQUIRED", "SHALL", "SHOULD", "SHOULD NOT", and "MAY" in this document are to be interpreted as described in BCP 14 [^BCP14] when, and only when, they appear in all capitals.

The terms "Mainnet" and "Testnet" in this document are to be interpreted as defined in the Zcash protocol specification [^protocol-networks].

The terms "Electric Coin Company" (or "ECC") and "Zcash Foundation" (or "ZF") in this document are to be interpreted as described in ZIP 1014 [^zip-1014].

The terms "Zcash Community Grants" (or "ZCG"), "Financial Privacy Foundation" (or "FPF"), and "Deferred Dev Fund Lockbox" in this document are to be interpreted as defined in ZIP 1015 [^zip-1015].

"Shielded Labs" refers to the Assocation of that name registered in the Swiss canton of Zug under the Unique Identifier CHE-243.302.798.

"Zcash Core Engineers" refers to the current set of engineers whose primary job is to make changes to consensus node software and libraries.

TODO: define "Zechub".

"Zcash Governance" refers to the social consensus of the Zcash community on specifications, procedures, agreements (legal or otherwise), and decision-making processes for operation and use of the Zcash Protocol on the Zcash Mainnet and (as applicable) Testnet networks.

"Protocol-defined Ecosystem Funding" is funding from sources defined by the Zcash Protocol for development of the Zcash ecosystem. At the time of writing, these sources are a portion of block rewards defined by Funding Streams [^zip-0207] and Lockbox Funding Streams [^zip-2001].

A "Proposal" is either a proposed change in Zcash Governance ("Governance Proposal") or a proposed disbursement of Protocol-defined Ecosystem Funding ("Funding Proposal") to be approved or rejected by a vote of the [zBloc Constituencies](#zbloc-membership).

A "Decision" is the approval or rejection of a Proposal.


# Abstract

In recent polls about the future of Zcash development funding, the community signaled a strong preference for a non-direct funding model. It also decided on a temporary one-year continuation of a development fund, starting at the second halving in November 2024, where ZCG would continue to be funded and the remainder would be temporarily placed in a Deferred Dev Fund Lockbox, while the community determines next steps.

This ZIP outlines a more detailed proposal for non-direct funding, based on voting among a group of Constituencies with a stake in Zcash and its protocol. It has 80% of the block rewards given to miners and 20% to a Zcash Community Fund, in perpetuity. The current balance of the Deferred Dev Fund Lockbox is used to seed the Zcash Community Fund. This fund is initially split into two Funding Pools, with different rules for each: the Large Grant Fund and the Minor Grant Fund. Other specialized pools could be added over time.

This model allows for the community to guide its evolution and possible replacement via Governance Decisions, and so would be activated indefinitely.


# Motivation

Zcash governance must represent voices from all over the world, who need digital cash for their security and for their dignity. It must not be dependent on individuals who, despite their best intentions, are flawed and prone to temptations to control and coerce. It must be durable and withstand attempted capture of all forms.

zBloc is a governance model that is designed for decentralization and accountability, to include more voices and ensure results from those who receive Protocol-defined Ecosystem Funding.

It is built to allow new innovative and positive voices to rise up and carry the flag of the Zcash community forward, in recognition of the risk that any one group may become captured or ineffective.


# Requirements

* This ZIP covers how to decide on Proposals for potential changes to Zcash Governance and/or disbursement of Protocol-defined Ecosystem Funding.
* There is a well-defined, publically agreed, process for evaluation and community feedback on both Governance Proposals and Grant Proposals.
* Funds are held in a multisig resistant to compromise of some of the parties' keys, up to a given threshold.
* The voting mechanism used for decision-making is similarly resistant to compromise of some of the parties' keys, up to a given threshold.
* No single party's non-cooperation or loss of keys is able to cause any Protocol-defined Ecosystem Funding to be locked up unrecoverably.
* 80% of the block rewards are given to miners, and 20% to a Zcash Community Fund seeded from the Deferred Dev Fund Lockbox.
* The funds from the 20% funding stream will be usable immediately.
* The funds in the Deferred Dev Fund Lockbox will be usable once a mechanism is available for disbursing them.
* Any use of Deferred Dev Fund Lockbox funds is consistent with the purpose specified in [^zip-1015-lockbox] of "funding grants to ecosystem participants".


# Non-requirements

Any changes to the ZCG or its governance, such as its expansion to include more members, may be desired but are specifically outside this proposal’s scope.

# Specification

## zBloc Membership

The zBloc would distribute decision-making authority for both Zcash governance and funding decisions, potentially to any number of Constituencies.

A zBloc Constituency is a group representing a trusted subsection of the Zcash community.

The [Initial Structure] section below proposes a set of initial Constituencies, but the model allows for changes over time, enabling the zBloc to evolve. New zBloc Constituencies may be added as they gain trust and removed if they are no longer operating or trust is eroded. The means for this is described in the [Governance Decisions] section below.

zBloc Constituencies may be granted different levels of authority, receiving less or more say over time. This is done by allocating or removing "Voting Units" to reflect the amount of voting power allocated to each Constituency. For example, if the community wishes to increase the weight of coinholder voice over time, it could increase the number of Voting Units allocated to coinholder representatives, which would dilute the relative power of other Constituencies.

### Decision-making policies

To be considered a Constituency, each must pre-commit to an internal policy for decision-making that all other Constituencies approve of (i.e. greater than one decision maker, means of assessing community sentiment, etc.). This could be by polling, majority vote within the Constituency, coinholder signaling, technical feasibility, mission alignment, etc.

In order for a Constituency to change its decision-making policy, the change MUST be expressed as a [Governance Proposal] and Approved before it comes into effect. The Constituency that is proposing to change its policy is eligible to vote, but it MUST make its decision according to its *pre-existing* policy (if it does not abstain).

## Initial Structure

The initial group of Constituencies will be (if they are willing and approved by the others and by the Zcash community):

* Coinholders
* Electric Coin Company
* Zcash Foundation
* Shielded Labs
* Zcash Community Grants
* Zcash Core Engineers
* ZecHub

Each Constituency initially receives three Voting Units. This MAY be changed by a Governance Proposal.

Constituencies other than the Coinholder Constituency above are called Organizational Constituencies. The Organizational Constituencies will together elect a representative responsible for establishing a clear process and mechanism for gathering coinholder sentiment, which will then be used as the decision-making process of the Coinholder Constituency.

TODO: as Organizational Constituencies make commitments about their decision-making policies, link to those commitments here.

Initial zBloc members MUST take on the responsibility to encourage, nurture, and welcome potential new Constituencies.

**Rationale:** Relentless decentralization is zBloc’s core value and mission. It is the unifying ethos that will keep zBloc’s doors open to new contributors. This continuous expansion is in the best interests of the growing Zcash community. 

## Voting

A suitable voting mechanism is needed that —among other design requirements— makes the votes cast by each Constituency (i.e. the number of Voting Units cast for Approval and for Rejection) publically visible. A possible design that meets this requirement is suggested in [^draft-ecc-onchain-accountable-voting] ("On-chain Accountable Voting"). In addition, the chosen voting mechanism MUST support the situation where voting entities must choose among multiple competing proposals to select a single grant recipient. The voting system selected MUST avoid vote-splitting scenarios that can result in an option being selected that achieves only a plurality (not a majority) of Consituencies supporting it.

Each independent zBloc Constituency decides how to cast its Voting Units for each Governance or Funding Proposal, provided it is eligible to vote on that proposal (see the next section). If its decision-making policy permits, it MAY cast fewer than its total number of Voting Units, and MAY cast some Voting Units for Approval and some for Rejection. This might be used to publically acknowledge internal dispute over a decision, for example.

### Conflicts of interest

If a Constituency has a conflict of interest for a given decision, such as potentially being the recipient of funds or additional authority, then its Voting Units are not eligible to be cast for that vote. This affects the [Approval Threshold] discussed below, which is calculated as a proportion of the remaining Eligible Voting Units.

A Constituency is not automatically considered to have a conflict of interest merely because the decision affects it — for example, when changing its decision-making policy, or because it would need to make changes to software if the Proposal were Approved.

### Approval Thresholds

The Approval Threshold is the absolute majority, as a proportion of the total number of Eligible Voting Units, required for a Proposal to be Approved. As stated earlier, Eligible Voting Units do not include those of Constituencies that have a conflict of interest for this Proposal. However, they do include the Voting Units of Constituencies that have no conflict of interest but choose to abstain.

By default, a [Governance Proposal](#governanceproposals) requires a three-fifths Approval Threshold, and MUST have a Deadline at least two weeks from when the Proposal is published on-chain.

All Consituencies MUST be consulted in order to determine whether they consider a draft Proposal to be "controversial", before it is published on-chain. If *any* Constituency decides that a Proposal should be treated as controversial, it is then subject to a higher Approval Threshold of three quarters, and a Deadline at least four weeks from when the Proposal is published on-chain. (In the case of the Coinholder constituency, a coinholder vote is not necessarily required to establish this; it is likely sufficient to decide based on forum discussions for example.)

The following categories of [Governance Proposal](#governanceproposals) are automatically subject to the three-quarters Approval Threshold and 4-week Deadline:

* Increasing or decreasing the voting power of zBloc Constituencies by adjusting how many Voting Units they hold.
* Increasing or decreasing the number of Funding Pools, the rules that govern them, and the amounts allocated.

In the case of [Governance Proposals] that affect consensus, final ratification occurs when node operators adopt the software implementing the changes.

Note: Nothing forces developers of Zcash consensus node software to implement any particular proposal. The aim of a process specification like this one is only to establish a social consensus. It fundamentally cannot affect the autonomy of developers of Zcash consensus node software to publish (or not) the software they want to publish, or the autonomy of node operators to run (or not) the software they want to run.

## Proposals

As stated in [Terminology], there are two categories of Proposal that can be put to a vote of the [zBloc Constituencies](#zbloc-membership):

* a "Governance Proposal", expressing a proposed change in Zcash Governance;
* a "Funding Proposal", expressing a proposed disbursement of Protocol-defined Ecosystem Funding.

Proposals have a Deadline (expressed as a Deadline Height if [^draft-ecc-onchain-accountable-voting] is used). If the Deadline is reached, they are implicitly Rejected. This does not necessarily preclude reintroducing the same or a similar Proposal.

### Governance Proposals

At least the following changes to Zcash Governance MUST be proposed and approved by a Governance Proposal before they can take effect:

* Changes to Zcash consensus rules. In this case Approval is REQUIRED in order for an activation height to be set.
* Substantive changes to the ZIP Process defined in ZIP 0 [^zip-0000].
* Substantive changes to this ZIP defining the zBloc.
* Changes to the set of zBloc Constituencies and/or the distribution of Voting Units among those Constituencies.
* Changes to the policy a Constituency uses for its decision-making.

The ZIP Editors will modify ZIP 0 to define other categories of change to Zcash Governance that MUST or SHOULD require Approval of a Governance Proposal.

Unrelated changes SHOULD NOT be bundled into a single Governance Proposal. This does not prevent a single Governance Proposal from being used to decide whether to adopt a proposed Network Upgrade involving multiple consensus and/or process changes, since those are considered related. During the process of drafting Governance Proposals, the ZIP Editors MAY request that proposals be split in order to satisfy this rule, or merged if they are sufficiently interdependent.

### Disputes

If any zBloc Constituency, or the ZIP Editors, have concerns relating to the conduct of any vote, they MAY raise a dispute. Possible reasons to raise a dispute include believing that:

* A Constituency or any holders of keys for its Voting Units were unduly pressured or coerced.
* A Constituency voted contrary to its intended position (due to key compromise or error, for instance), or contrary to its stated decision-making policy.
* A Constituency failed to disclose a relevant conflict of interest.
* There were technical irregularities in the use of the voting mechanism.

If a dispute is raised, the Constituencies SHALL first resolve any technical issues as far as possible (e.g. by rotating keys), and then make one or more Governance Proposals intended to resolve the situation to the satisfaction of the community.

### Exceptional decisions to remediate security vulnerabilities

The governance processes specified in this ZIP are not intended to prevent consensus node implementors from making consensus changes that they reasonably believe are critical to maintain the security of the Zcash Mainnet network and/or Zcash users. Such changes might need to be developed and released according to a controlled disclosure process that precludes public voting.

In cases where the zBloc governance processes could not be used for this reason, the consensus node implementors MUST, once the risk of exploitation has passed, publish a thorough post-mortem analysis that explains why this was the case.

## Funding

### Zcash Community Fund

A pool of multisig-controlled funds, seeded from the existing contents of the ZIP 1015 Deferred Dev Fund Lockbox [^zip-1015-lockbox] and supplemented with a funding stream consising of 20% of the block subsidy starting at block 3146400 that will continue until modified by a future ZIP, forms a new Zcash Community Fund. The mechanisms for the creation and management of this fund are described by the Deferred Dev Fund Lockbox Disbursement proposal [^draft-ecc-lockbox-disbursement], with the $\mathsf{stream\_value}$ parameter set to 20%, and the $\mathsf{stream\_end\_height}$ parameter set to the height at which the Zcash block subsidy diminishes to zero.

The Zcash Community Fund will be controlled by a multisig with keys held by the Zcash Foundation and the Electric Coin Company, along with three other entities yet to be determined ("Key-Holder Organisations").

If Option 1 of the Deferred Dev Fund Lockbox Disbursement proposal is selected, the community SHOULD prioritize the development of a mechanism for disbursement of funds from the Deferred Dev Fund Lockbox. It is assumed here that lockbox funds would be controlled via a similar multisig with keys held by the same Key-Holder Organisations.

The Key-Holder Organisations would be bound by a legal agreement to only use funds held in the Zcash Community Fund according to the specifications in this ZIP, expressed in suitable legal language.

The Zcash Community Fund will be subject to rules similar to those currently in effect for ZCG and specified in ZIP 1015, as described under [Administrative obligations and constraints].

### Funding Pools

This proposal initially sets up two Funding Pools, with different rules for each. These are the Large Grant Fund and Minor Grant Fund. Over time, it is worthwhile to consider other specialized pools. This might include novel ideas, such as Loan-Directed Retroactive Grants [^forum-loan-directed-retroactive-grants] suggested by @nuttycom, or other retroactive or speculative grant pools.

Who may apply for grants is not restricted. It is highly encouraged for all participating organizations to seek outside funding and not solely rely on the Zcash Community Fund.

The Large Grant Fund will include 80% of the Zcash Community Fund.

* The Large Grant Fund is used for grants at or above USD 100,000 (or equivalent in another currency). An Approved Governance Proposal can change this threshold.
* The zBloc makes funding decisions and disbursements via Funding Proposals with an Approval Threshold of one half (i.e. an absolute majority of Eligible Voting Units is sufficient for Approval). The Deadline SHOULD be at least two weeks from when a Proposal is published on-chain.
* Proposals are submitted to a dedicated section of the Zcash forum. Each zBloc Constituency SHOULD monitor the forum and engage with participants. If a Constituency does not cast their vote for Approval, they SHOULD explain why they are not supporting the grant.
* If the grant is Approved, disbursements are made when the recipient successfully demonstrates completion of a milestone to the satisfaction of Constituencies holding a simple majority of Eligible Voting Units.

The Small Grant Fund will include 20% of the Zcash Community Fund.

* The Small Grant Fund is used for grants under USD 100,000 (or equivalent in another currency). An Approved Governance Proposal can change this threshold.
* A designated organization, or perhaps different organizations with areas of specialization (engineering, marketing, etc.) will administer decisions and disbursements in exchange for an annual fee.
* The organization(s) will be elected by the zBloc, and can be changed or removed by Approving a Governance Proposal.
* The fee will be proposed by the organization and approved by the zBloc.
* The organization will self-govern and manage the process for grant submissions, approvals, and disbursements.
* ZCG could be a candidate for this role initially.
* The role is open to competition. For example, rather than ZCG splitting off as an independent organization, perhaps this function could be rolled under the Financial Privacy Foundation or third parties that may be interested in managing the fund in exchange for a fee.

## Administrative obligations and constraints

Provisions of ZIP 1015 imposing obligations and constraints on the Financial Privacy Foundation, Electric Coin Company, the Zcash Foundation, and grant recipients relating to the previous ``FS_FPF_ZCG`` funding stream, SHALL continue in effect for the Zcash Community Fund. In particular this includes the following:

* A decision to disburse funds is subject to veto if any Key-Holder Organization judges it to violate applicable law or reporting requirements.
* The Key-Holder Organizations SHALL be contractually required to recognize the Zcash Community Fund as a Restricted Fund donation or equivalent [TBD], and keep separate accounting of its balance and usage under its Transparency and Accountability obligations defined in ZIP 1015 [^zip-1015-transparency-and-accountability].

TODO: use the same veto process as [^draft-ecc-community-and-coinholder].

## Security precautions

The Key-Holder Organizations and the Organizational Consituencies MUST take appropriate precautions to safeguard funds from theft or accidental loss. Any theft or loss of funds, or any loss or compromise of key material MUST be reported to the Zcash community as promptly as possible after applying necessary mitigations.

# Acknowledgements

Thank you to Tatyana Peacemonger, Kris Nuttycombe, and Chris Tomeo for the reviews, feedback, questions, and suggestions needed to make this a strong proposal.

# References

[^BCP14]: [Information on BCP 14 — "RFC 2119: Key words for use in RFCs to Indicate Requirement Levels" and "RFC 8174: Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words"](https://www.rfc-editor.org/info/bcp14)

[^protocol]: [Zcash Protocol Specification, Version 2024.5.1 or later](protocol/protocol.pdf)

[^protocol-networks]: [Zcash Protocol Specification, Version 2024.5.1. Section 3.12: Mainnet and Testnet](protocol/protocol.pdf#networks)

[^zip-0000]: [ZIP 0: ZIP Process](zip-0000.rst)

[^zip-0207]: [ZIP 207: Funding Streams](zip-0207.rst)

[^zip-1014]: [ZIP 1014: Establishing a Dev Fund for ECC, ZF, and Major Grants](zip-1014.rst)

[^zip-1015]: [ZIP 1015: Block Subsidy Allocation for Non-Direct Development Funding](zip-1015.rst)

[^zip-1015-lockbox]: [ZIP 1015: Block Subsidy Allocation for Non-Direct Development Funding — Lockbox](zip-1015#lockbox)

[^zip-1015-transparency-and-accountability]: [ZIP 1015: Block Subsidy Allocation for Non-Direct Development Funding — Transparency and Accountability](zip-1015#transparency-and-accountability)

[^zip-2001]: [ZIP 2001: Lockbox Funding Streams](zip-2001.rst)

[^draft-ecc-lockbox-disbursement]: [draft-ecc-lockbox-disbursement: Deferred Dev Fund Lockbox Disbursement](draft-ecc-zbloc.md)

[^draft-ecc-community-and-coinholder]: [draft-ecc-community-and-coinholder: Community and Coinholder Funding Model](draft-ecc-community-and-coinholder.md)

[^draft-ecc-onchain-accountable-voting]: [draft-ecc-onchain-accountable-voting: On-chain Accountable Voting](draft-ecc-onchain-accountable-voting.md)

[^forum-loan-directed-retroactive-grants]: [Zcash Forum: Loan-Directed Retroactive Grants](https://forum.zcashcommunity.com/t/loan-directed-retroactive-grants/48230)
