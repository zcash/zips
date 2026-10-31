
    ZIP: Unassigned
    Title: Zcash Adoption Pool (ZAP)
    Owners: Daira-Emma Hopwood <daira@jacaranda.org>
    Credits: Violet Rollergirl
             Blake Benthall (emersonian)
             Mylo Bennett
             Alison Stevenson
    Status: Draft
    Category: Consensus Process
    Created: 2026-10-30
    License: MIT
    Discussions-To: <https://forum.zcashcommunity.com/???>
    Pull-Request: <https://github.com/zcash/zips/pull/1431>


# Terminology

The key words "MUST" and "SHALL" in this document are to be interpreted as
described in BCP 14 [^BCP14] when, and only when, they appear in all capitals.

The terms "Mainnet" and "Testnet" in this document are to be interpreted as
defined in the Zcash protocol specification [^protocol-networks].

The terms "Zcash Community Grants" (or "ZCG"), "ZCG Committee", and "Deferred
Dev Fund Lockbox" are to be interpreted as defined in ZIP 1015 [^zip-1015].

The terms "Protocol-defined Ecosystem Funding" and "Coinholder-Controlled Fund"
are to be interpreted as defined in ZIP 1016 [^zip-1016].

“ZEC” refers to the native currency of Zcash on Mainnet.


# Abstract

Reaffirm the portion of Protocol-defined Ecosystem Funding allocated to
Zcash Community Grants (ZCG), and focus on its original goal described in
ZIP 1015 [^zip-1015-zcg] — to accelerate Zcash adoption as broadly as
possible. To better reflect that focus and to clarify the original intent
of ZIP 1015, this portion of funds will be called the "Zcash Adoption Pool".


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

There is no shortage of projects that fulfil these criteria and that are in
desperate need of funding.

## Background

Throughout the history of the Zcash project, there have been periodic calls to
abandon support for independent teams entering the Zcash ecosystem. This has
presented itself in a variety of forms with numerous arguments. At no point in
Zcash's history, however, has there ever been a lack of use cases for programmes
and initiatives that utilize shielded ZEC.

Most recently, calls for the abolition of the ZCG have made absurd arguments,
including that there is more money in the Zcash Community Grants portion of the
"dev" fund than is required for "development". This argument presupposes that
"development" should be limited to technical protocol development, which is a
clear misinterpretation of both the letter of ZIP 1015 (as quoted above), and
its original intent. That intent was not changed by ZIP 1016. Notably, these
proposals have not stipulated any change to the Coinholder-Controlled Fund —
which in practice would result in a substantial shift of power toward large
holders.

Another such argument is that development work can be funded via other means,
such as private equity, and therefore "should" be funded by private equity. The
authors of this ZIP do not object to funding from private equity. Rather, this
ZIP reaffirms the utility of funding programmes that private equity has
evidently *not* funded, and for which no other reliable source of funding
currently exists.

There are many programmes that may apply for ZCG grants whose source for funds
is at risk, but for whom support will undeniably increase the adoption rate of
Zcash. That is precisely what the "dev" fund was designed to fund.

To clarify this in literal terms, this ZIP therefore renames the pool of funds
and the grant programme funded via the `FS_FPF_ZCG_H3` slice of Protocol-defined
Ecosystem Funding to explicitly include the word "adoption", in order to avoid
further misinterpretation or the possibility of future misappropriation of the
funds previously allocated for purposes of broader Zcash and ZEC adoption.


# Requirements

All requirements of ZIP 1015 continue to apply; in particular:

* There is a well-defined, publically agreed, process for evaluation and
  community feedback on grant proposals.
* Any use of Deferred Dev Fund Lockbox funds is consistent with the purpose
  specified in [^zip-1015-lockbox] of "funding grants to ecosystem participants".

In addition:

* Funds disbursed through the Zcash Adoption Pool are to be further disbursed for
  the explicit purpose of increasing the number of human individuals who have
  direct holdings in ZEC or who directly transact in ZEC on the Zcash network.
  The purpose of this is to further broaden the holding of ZEC and increase the
  velocity of its use as a currency. This is what *adoption* means.


# Non-requirements

* Pleasing everyone.


# Specification

For avoidance of doubt, the `FS_FPF_ZCG_H3` funding stream SHALL continue at its
existing value and for the duration specified in ZIP 214 Revision 3 [^zip-0214].
This applies to Mainnet and Testnet.

The pool of funds associated with this stream SHALL be renamed to
"Zcash Adoption Pool" ("ZAP"), and the grant programme by which it is disbursed
to "Zcash Adoption Pool Grants" ("ZAP Grants"). Assets associated with Zcash
Community Grants (past, present, or future) therefore become assets associated
with the Zcash Adoption Pool; requirements on their administration specified in
ZIPs 1015 and 1016 [^zip-1015] [^zip-1016] are unchanged. The ZCG Committee SHALL
be referred to as the ZAP Committee.

The ZAP Grant assessment process MUST obtain reasonable confidence, on the evidence
in the application, that funds disbursed through Zcash Adoption Pool Grants will
be further disbursed for the explicit purpose of increasing the number of human
individuals who have direct holdings in ZEC or who directly transact in ZEC on the
Zcash network. The purpose of this is to further broaden the holding of ZEC and
increase the velocity of its use as a currency.

## Examples

Examples of end-recipients who might receive ZEC as a result of grants approved
under this programme include:

* sex workers who are debanked or require electronic payment means otherwise
  unavailable to them, and their clients that require payment discretion;
* civil society organizations who struggle to maintain funding;
* privacy projects and contributors in need of legal defence;
* technical development projects that would similarly struggle to
  receive funding from private investments (a past example would be Arti, an
  implementation of Tor in Rust);
* people protesting surveillance or restrictions on their speech, movement, and
  freedom of association;
* abortion funds;
* people in need of humanitarian aid and disaster relief, e.g. across borders;
* communities threatened by genocide or forced displacement;
* debanked individuals;
* remittance recipients;
* victims of abuse;
* homeless people;
* trans people attempting to access hormones;
* refugees;
* people unable to obtain food or medical care due to discrimination;
* people in need of education in underfunded nations;
* publishers catering to underserved groups or to political views opposing
  discrimination;
* projects developing accessibility features, or localization to minority
  languages;
* small businesses choked by excessive payment processing fees;
* people and businesses unable to access the financial system due to payment
  processor discrimination and censorship.

Some of these examples are intentionally provocative. All can be funded
entirely legally in most jurisdictions. They are presented here to highlight
the requirement that Zcash remain **for everyone**.


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
