
    ZIP: Unassigned
    Title: Zcash Adoption Pool (ZAP)
    Owners: Daira-Emma Hopwood <daira@jacaranda.org>
            Violet Rollergirl
    Credits: Blake Benthall (emersonian)
             Mylo Bennett
             Alison Stevenson
    Status: Draft
    Category: Consensus Process
    Created: 2026-10-30
    License: MIT
    Discussions-To: <https://forum.zcashcommunity.com/t/zcash-adoption-pool-zap/58656>
    Pull-Request: <https://github.com/zcash/zips/pull/1431>


# Terminology

The key words "MUST", "SHALL", "SHOULD", and "SHOULD NOT" in this document are
to be interpreted as described in BCP 14 [^BCP14] when, and only when, they
appear in all capitals.

The terms "Mainnet" and "Testnet" in this document are to be interpreted as
defined in the Zcash protocol specification [^protocol-networks].

The terms "Zcash Community Grants" (or "ZCG"), "ZCG Committee", and "Deferred
Dev Fund Lockbox" are to be interpreted as defined in ZIP 1015 [^zip-1015].

The terms "Protocol-defined Ecosystem Funding" and "Coinholder-Controlled Fund"
are to be interpreted as defined in ZIP 1016 [^zip-1016].

“ZEC” refers to the native currency of Zcash on Mainnet.

"Adoption" means an increase in the number of natural persons who hold ZEC
directly or transact directly in ZEC on the Zcash network.

A "stakeholder" is a party whose routine economic activity depends on the
continued operation of the Zcash network.

A "disbursement chain" is the sequence of ZEC transfers from a ZAP grant first
to its "grant recipient", then through zero or more "intermediary recipients",
to one or more "end recipients" (who are natural persons).

A "computational attack" is a costly effort denominated in hashrate, hardware,
or energy that targets the consensus network of Zcash networks (usually Mainnet).

A "political attack" is a costly effort denominated in legislative, regulatory, legal,
reputational, or market-access capital that targets the Zcash network's ability
to be used by any natural person. Examples of political attacks include delisting ZEC
from popular currency exchanges, deplatforming of developers or infrastructure,
hostile legislation, and smear campaigns.


# Abstract

The portion of Protocol-defined Ecosystem Funding allocated to Zcash Community Grants
(ZCG) is reaffirmed and bound to its stated objective in ZIP 1015 [^zip-1015-zcg],
consistent with increasing adoption as broadly as possible.

The store of funds for this purpose is renamed to "Zcash Adoption Pool".

Adoption is defined in a manner that recognizes its inherent value as
protection from political attacks, and thus clarified as comprising a critical
property of Zcash operation that must be increased, and accelerated.

A viable assessment criterion is specified for grants disbursed from the ZAP.


# Motivation

As specified in ZIP 1015:

> The stream allocated to Zcash Community Grants (ZCG) is intended to fund
> independent teams entering the Zcash ecosystem, to perform major ongoing
> development (or other work) for the public good of the Zcash ecosystem, to the
> extent that such teams are available and effective. The ZCG Committee is given
> the discretion to allocate funds not only to major grants, but also to a
> diverse range of projects that advance the usability, security, privacy, and
> adoption of Zcash, including community programs, dedicated resources, and other
> projects of varying sizes.

Many projects that fulfil these criteria are in need of funding.

## Threat model

As a privacy-preserving payment network, Zcash faces both computational and political attacks.
The historical record of privacy technologies writ large shows political attacks to be the more
frequent and often the more effective. Of the Zcash block subsidy, 80% is allocated against
computational attack via the miner reward. In contrast, The `FS_FPF_ZCG_H3` stream, only 8%, is
the native allocation that most directly addresses political attack. This ZIP doesn't resize the
stream. It records the gap and defines the stream's purpose to guide future ZIPs addressing it.

Political adversaries do not need to be intentionally hostile to meaningfully cause Zcash harm.
Regulators act to retain control over settlement; payment incumbents to preserve margin;
competing networks to acquire market share; and legislators on their interpretation of the
preferences of their most visible or vocal constituencies. Each will act against Zcash whenever
doing so is cheap relative to what they see as the benefit of doing so. The network's objective
is therefore not persuasion of any one actor, or unanimity within the set of actors with
investments in the network, but increasing the costs that political adversaries must expend to
rationally launch political attacks.

## Defense strategy

An adversary is deterred when the cost of its aim exceeds the benefit. The cost for political
attackers, for a given attack, is bounded by stakeholder concentrations. Attacks are cheap when
stakeholders are concentrated in one exchange, jurisdiction, developer organization, or sector:
a single point at which effort can be applied, and at bounded cost. Attacks become expensive as
the count of jurisdictions, sectors, and political alignments across which stakeholders are
distributed grows, because no single stakeholder's removal then suffices to constitute a successful
attack on the availability or access to the network as a whole. In other words, Zcash survives.

The most costly political attacks are those against stakeholders for whom shielded settlement is an
operational requirement rather than merely a preference, and who are also outside the adversary's
reach. Such stakeholders contest their own removal with their own resources, rather than with any
portion of the block subsidy. In contrast, that same cost is near zero for parties who currently
have no economic dependency on the Zcash network, whatever their stated preferences.

Adoption converts the party with no economic dependency on Zcash into a stakeholder of it.
Moreover, adoption does this most cheaply, before the adversary has chosen their attack.

Increased and accelerated adoption therefore directly secures Zcash against political attack.

## Background

Throughout the history of the Zcash project, there have been periodic calls to
abandon support for independent teams entering the Zcash ecosystem. This has
presented itself in a variety of forms with numerous arguments. At no point in
Zcash's history, however, has there ever been a lack of use cases for programmes
and initiatives that utilize shielded ZEC.

The most recent of such calls rest on a reading of "development" restricted to
protocol engineering, which is inconsistent with the text of ZIP 1015 quoted in
[Motivation] above and with its documented intent, which ZIP 1016 did not alter.
Notably, these calls have not stipulated any change to the Coinholder-Controlled
Fund. In practice this would result in a substantial shift of power toward large
holders.

Such a shift only increases the vulnerability of Zcash to political attack: as
outlined by the model above, concentrating allocation authority in any single
class of participant narrows the dependency graph and reduces the number of
dependencies an adversary must remove to capture Zcash. This holds for large
holders and for the grant committee alike — we do not argue that the latter is
a perfect mechanism to disburse funds for the purpose of accelerating adoption,
but only that it likely does so *differently* to the preferences of large
coinholders. That is its strength: the breadth of allocations is actually a
security property of Zcash, not a distributional preference.

Another such argument is that development work can be funded via other means,
such as private equity, and therefore "should" be funded solely that way. This
argument fails to consider that capital from an external principal carries an
external exit condition ("kicking away the ladder"). ZAP provides a source of
funding that is less vulnerable to that problem. This ZIP addresses the
programmes that private capital has *not* funded, and holds that the two
funding sources (Protocol-defined Ecosystem Funding streams and external
private capital) are complementary.

In particular, the retrospective nature of the grants currently provided by
the Coinholder-Controlled Fund biases them toward parties that have the capital
to perform work speculatively. Insurance does not solve this: parties that have
less capital to start with, and/or that come from groups subject to prejudice
or social disfavour, are much less likely to be able to find others to take on
the risk of not getting paid.

Finally, note that ZEC holders are also the principal beneficiaries of adoption:
velocity and breadth of distribution are the inputs to liquidity, and liquidity
is what holders are exposed to. The authors advise that future ZIPs that treat
holder and adoption interests as opposed should be evaluated skeptically against
the threat and cost models defined above.


# Privacy Implications

Measuring adoption for a privacy-preserving payment network can easily suppress
realized adoption, and actively slows the speed of adoption. The [Assessing adoption]
section discusses the consequences for assessment of grant evidence and for the
collection of information to assess grant effectiveness.


# Requirements

All requirements of ZIP 1015 continue to apply; in particular:

* There is a well-defined, publicly agreed, process for evaluation and
  community feedback on grant proposals.
* Any use of Deferred Dev Fund Lockbox funds is consistent with the purpose
  specified in [^zip-1015-lockbox] of "funding grants to ecosystem participants".

In addition, funds disbursed through the Zcash Adoption Pool are intended to
be used for the explicit purpose of accelerating Zcash and ZEC adoption as
defined above — either by further disbursement or by the funding of development,
in a broad sense, that directly increases adoption.


# Non-requirements

* Unanimity among stakeholders.
* Any change to the amount or duration of the `FS_FPF_ZCG_H3` stream.
* Categorization of grant recipients. (The criterion is defined by its
  mechanism, not by the identity of the recipient.)


# Specification

For avoidance of doubt, the `FS_FPF_ZCG_H3` funding stream SHALL continue at its
existing value and for the duration specified in ZIP 214 Revision 3 [^zip-0214].
This applies to Mainnet and Testnet.

The pool of funds associated with this stream SHALL be renamed to
"Zcash Adoption Pool" ("ZAP"), the grant programme by which it is disbursed renamed
to "Zcash Adoption Pool Grants" ("ZAP Grants"), and the ZCG Committee renamed to
"Zcash Adoption Pool Committee" ("ZAP Committee"). Assets associated with Zcash
Community Grants (past, present, or future) therefore become assets of the
Zcash Adoption Pool and the requirements on their administration specified in
ZIPs 1015 and 1016 [^zip-1015] [^zip-1016] are unchanged.

Before approving a ZAP Grant, the ZAP Committee MUST obtain reasonable confidence,
on the evidence in the application, that funds disbursed through that ZAP Grant
will be used for the explicit purpose of accelerating adoption as defined above.
That is, they will be further disbursed or used to fund development that, in either case,
directly increases adoption. Here "development" is supposed to be interpreted as
broadly as possible, in order to extend the scope of adoption programmes beyond
what is otherwise likely to be funded from other sources. Direct disbursement,
educational initiatives, legal defence, and technical development are all
possibilities.

As stated earlier, existing constraints defined by ZIP 1015 and 1016 continue to
apply, including constraints on grants of indefinite duration. This specifically
means that the ZAP Committee SHOULD periodically review grants that have been
previously approved for indefinite funding in order to continue receiving
disbursements from the Zcash Adoption Pool. Such reviews for indefinite grants
SHOULD occur on a schedule that the ZAP Committee considers appropriate.

The ZAP Committee SHOULD publish non-normative assessment guidance, including on
recipient categories expected to contribute most to adoption. Such guidance is
not part of this ZIP.

## Assessing adoption

A grant whose proceeds stop at the grant recipient adds at most one stakeholder;
proceeds transferred onward in ZEC add one at each hop:

    ZAP -> grant recipient -> [intermediary recipient(s)] -> end recipient(s)

A grant's expected contribution is therefore proportional to the expected number of
distinct parties in its disbursement chain. Assessment SHOULD weight the expected fan-out
of the chain and the proportion of recipients for whom shielded ZEC is an
operational requirement, on the evidence in the application.

The metric to assess adoption is distinct shielded receives, not transaction count.
Outflows, for example ZEC-to-BTC swaps, inflate transaction count while terminating
the chain (the ZEC goes to a market maker, which does not count as new adoption).
Assessment SHOULD therefore rank receipt metrics (external-asset-to-shielded-ZEC,
and preferably shielded-ZEC-to-shielded-ZEC) above spend metrics, balance held, or
undifferentiated transaction count. The point here is not that off-ramps are not
useful, but that their use does not by itself contribute to accelerating Zcash or
ZEC adoption.

Measuring adoption for a privacy-preserving payment network can easily suppress
realized adoption, and actively slows the speed of adoption. Therefore, this criterion
SHOULD NOT be interpreted to require evidence that is not realistically obtainable,
whose collection would reduce adoption or compromise grant, intermediary, or end
recipient privacy, or could interfere with the effectiveness of other adoption
efforts.

Collection of information on intermediary or end recipients MUST be limited to
what is necessary to reasonably assess grant effectiveness, MUST be aggregated or
otherwise anonymized, and MUST be performed only with the informed consent of the
parties concerned.


# Rationale

Since no consensus changes are needed to achieve the goals of this proposal, none
are made. Despite potential redundancy, the authors believe it is necessary to
explicitly reaffirm some of the current rules of ZIPs 1015, 1016, and 214. The
purposes of that are to distinguish it from other concurrent proposals, and to
dispel potential misconceptions that have arisen about this proposal in discussions
on the Zcash Community Forum.

## Other proposals

`draft-mcgee-future-dev-legal-defense-fund` [^draft-mcgee-future-dev-legal-defense-fund]
would end the `FS_FPF_ZCG_H3` funding stream and requires ZCG to send 50,000 ZEC
—about 55% of ZCG's current treasury— to the Network Sustainability Mechanism.
Its argument for doing so apparently hinges primarily on ZCG having approximately
91,453 ZEC of unspent funds (as of October 26, 2026).

It is unclear to us why unspent funds in ZCG's treasury are a problem relative
to the much larger amount of unspent funds in the Coinholder-Controlled Fund,
or relative to the initially unspendable funds in the NSM. Funds in the NSM are
unspendable at least until they are diverted to new issuance in 2031. After that
the increase in miner rewards due to the 50,000 ZEC is intially 0.006875 ZEC per
block, or 2.64% of the 0.26041666 ZEC scheduled block subsidy after the third halving,
decreasing over time. The primary effect of `draft-mcgee-future-dev-legal-defense-fund`
is therefore simply to deprive the ZCG treasury, and the projects that could be
funded by it, of 50,000 ZEC. Another proposal, `draft-howard-wind-down-zcg`
(zips#1423) [^draft-howard-wind-down-zcg], would go further and shut down the
ZCG entirely for new grants, stripping it of all of its treasury after current
grant obligations.

Our proposal would continue to make that money available, as needed, to
projects consistent with accelerating the adoption of Zcash and ZEC. As
stated earlier, "direct disbursement, educational initiatives, legal defence,
and technical development are all possibilities." It is neither anticipated
nor necessary for this money to be spent immediately. The authors of this
proposal believe that prudent management of the funds in the Zcash Adoption
Pool is a matter for the ZAP Committee and not something to be dictated by
a ZIP, since it depends heavily on market conditions and on what grant
applications are actually submitted.

## Inclusivity is essential to Zcash governance

Sometimes it is necessary to speak plainly and on the record. During this
governance debate, the Owners of this ZIP have faced considerable hostility
and antipathy to who we are. We are both trans women, and one of us is a sex
worker. Other participants in the debate have at times insisted that it be
conducted primarily on X, or have assumed participation on X as table stakes.
But X is not a safe platform for trans women, and especially not for trans
sex workers. It is literally impossible for either of us to participate there
without the replies being swamped by hate speech.

We therefore support `draft-emersonian-zcash-town-square` [^draft-emersonian-zcash-town-square],
which would affirm the Zcash Community Forum as the official venue for
discussion of Zcash governance, funding, and protocol direction. It would
also require certain announcements by funded organizations' Executives and
Official Accounts on other platforms to be cross-posted, within 24 hours,
to that Forum. This would make it practical for participants in Zcash
governance discussions who face an inordinate level of hate on other platforms
(especially but not limited to X) to keep up with all turns in the debate.

A stronger stance against hate speech in future Zcash governance debates will
be critical to the integrity and inclusivity of that governance, and therefore
of the Zcash community and network. We are profoundly disappointed with how
many others in the Zcash community this is apparently not obvious to. You did
not have our backs.


# Acknowledgements

The authors would like to thank the attendees of the Zcon7 conference for
discussions leading to this proposal, and the organizers of the conference
for the space to discuss it in person.


# References

[^BCP14]: [Information on BCP 14 — "RFC 2119: Key words for use in RFCs to Indicate Requirement Levels" and "RFC 8174: Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words"](https://www.rfc-editor.org/info/bcp14)

[^protocol-networks]: [Zcash Protocol Specification, Version 2026.8.0 [NU6.3]. Section 3.12: Mainnet and Testnet](protocol/protocol.pdf#networks)

[^zip-0214]: [ZIP 214: Consensus rules for a Zcash Development Fund](zip-0214.rst)

[^zip-1015]: [ZIP 1015: Block Subsidy Allocation for Non-Direct Development Funding](zip-1015.rst)

[^zip-1015-zcg]: [ZIP 1015: Block Subsidy Allocation for Non-Direct Development Funding — Zcash Community Grants](zip-1015#zcash-community-grants-zcg)

[^zip-1015-lockbox]: [ZIP 1015: Block Subsidy Allocation for Non-Direct Development Funding — Lockbox](zip-1015#lockbox)

[^zip-1016]: [ZIP 1016: Community and Coinholder Funding Model](zip-1016.md)

[^draft-emersonian-zcash-town-square]: [draft-emersonian-zcash-town-square: The Zcash Town Square: Official Discussion and Announcement Cross-Posting](draft-emersonian-zcash-town-square.md)
