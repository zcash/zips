    ZIP: Unassigned
    Title: Winding Down Zcash Community Grants
    Owners: Tom Howard <tom@zcashlabs.org>
    Credits: Maxime Desalle
    Status: Draft
    Category: Consensus Process
    Created: 2026-10-28
    License: MIT
    Updates: 1015, 1016


# Terminology

The key words "MUST", "MUST NOT", "SHOULD", and "MAY" in this document are to
be interpreted as described in BCP 14 [^BCP14] when, and only when, they appear
in all capitals.

"Zcash Community Grants" ("ZCG"), "ZCG Committee", and "Financial Privacy
Foundation" ("FPF") have the meanings given in ZIP 1015. [^zip-1015]

"Coinholder-Controlled Fund" ("CCF") has the meaning given in ZIP 1016.
[^zip-1016]

"Network Sustainability Mechanism" ("NSM") and "NSM Value Balance" refer to
the mechanism and balance specified in ZIP 237. [^zip-0237] A contribution to
the NSM removes ZEC from circulation for subsequent reissuance under the
protocol; it is not a payment to an organization or a treasury address.

"Wind-down Date" means the UTC calendar day of Mainnet activation of the
network upgrade that deploys this ZIP.

"ZCG funds" means assets held or administered by FPF for the ZCG program,
including its grant and Discretionary Budget balances, assets subsequently
received for that program, grant refunds, and proceeds attributable to those
assets. This includes any remaining assets transferred from ZCG's previous
administrator. It excludes the CCF and assets administered by FPF for other
programs.

"Existing commitments" means grants approved by the ZCG Committee before
activation of the designated upgrade on the Wind-down Date, including their
approved but unpaid milestones, and legally binding ZCG administrative
obligations entered into before that activation. An application, request for
proposals, or expression of intent that has not resulted in an approved grant
or binding obligation is not a commitment.

"Residual funds" means ZCG funds remaining after provision for existing
commitments and the wind-down expenses permitted by this ZIP.


# Abstract

This ZIP proposes an orderly wind-down of Zcash Community Grants. At activation
of the designated Mainnet network upgrade, ZCG would stop making new grants and
begin winding down its operations. Existing commitments would be completed
under their existing terms. FPF would retain sufficient assets to meet those
commitments and reasonable wind-down expenses, then contribute all residual
funds to the Network Sustainability Mechanism.

ZIPs 1015 and 1016 currently restrict the purposes for which FPF may use ZCG
funds. This ZIP specifies amendments that expressly authorize completing
existing commitments, paying limited closure costs, and contributing the
remainder to the NSM. It also calls for corresponding legal instruments and
approvals so that the change can be executed consistently with FPF's legal
obligations, rather than assuming a ZIP alone changes existing agreements.

This proposal complements the separate proposal to end ZCG's future funding
stream. That proposal changes future block subsidy allocations; this proposal
addresses the existing treasury, commitments, and program governance. It does
not itself change consensus rules or the CCF.

The wind-down can begin before a voluntary NSM contribution mechanism is
deployed. Until such a mechanism is available, FPF would safeguard the residual
funds solely for that purpose. Public reporting would establish the disposition
of the treasury while protecting confidential grantee and financial information.


# Motivation

ZCG has carried the torch through the evolution of Zcash's development reward
program. From the Major Grants structure established by ZIP 1014 to the
community grants program administered by FPF under ZIP 1015, it has provided
continuity for independent teams and a way to direct protocol-funded resources
toward work that benefits the Zcash ecosystem. [^zip-1014] [^zip-1015] That
contribution provides the foundation for the next stage of the funding model.

Coinholder-directed funding has been part of that model since ZIP 1016,
"Community and Coinholder Funding Model", was created on 2025-02-19.
[^zip-1016] The voting technology developed to support it has since matured
into an operational system. The Coinholder-Directed Retroactive Grants Program
(CDRGP) completed its latest round on September 29, 2026, with approximately
2.18 million ZEC of voting power participating on individual proposals.
[^cdrgp-q3-results] [^cdrgp-q3-tallies] The separate NU7 scope vote closed on
September 14, 2026, with approximately 2.40 million ZEC participating on its
issuance-schedule question. [^nu7-poll-results] Circulating supply was
approximately 16.96 million ZEC on September 29 and 16.93 million ZEC on
September 14. Both processes therefore exceeded two million ZEC of
participation, or over 12% of the circulating supply in each case.
[^supply-vote-dates]

The CDRGP has demonstrated that coinholder-directed grants are operational.
Its latest results approve funding for core protocol work by ZODL and Valar
Group, Zec.rocks wallet infrastructure, Ironwood external audits and formal
verification, and critical vulnerability bounties for Orchard and Zebra.
[^cdrgp-q3-results] Earlier rounds have also progressed from approval to
completed disbursements, including payments for Unstoppable Wallet, BitcoinVN,
and ZcashCommunity website hosting. [^cdrgp-disbursements] These are concrete
examples of a functioning funding channel for core development, infrastructure,
and security.

ZIP 1016 provides for open proposal submission and permissionless participation
by eligible coinholders in grant approval, rather than requiring an award from
the ZCG Committee. [^zip-1016] The program retains published eligibility
conditions, legal vetoes, and administration and disbursement by FPF and the
Key-Holder Organizations. Its operation demonstrates that a separate ZCG
grant-selection committee is no longer needed to provide that funding channel.

This proposal therefore treats ZCG's off-chain committee and legal arrangements
as a transitional bridge that has served its purpose. The development-funding
system now has an operational coinholder-directed approval process, supported
by on-chain voting infrastructure. [^coinholder-voting-chain] Continuing a
parallel ZCG grant-making body is no longer necessary in the proposed model.
Winding it down recognizes its contribution and completes that transition,
while preserving the legal administration still needed to execute grants.

Ending ZCG's automatic funding stream and winding down its grant-making
program are distinct decisions. The proposal "Ending the ZCG Funding Stream in
Favor of the NSM" leaves ZCG's existing assets and the rules governing them
unchanged, including its authority to make further grants. [^end-zcg-stream]
An additional decision is therefore needed to close the program and determine
the disposition of its remaining treasury.

This ZIP builds on Maxime Desalle's forum proposal, "End ZCG and send its
funds to the NSM". [^maxime-proposal]

The policy proposed here is to honor work already approved, stop creating new
commitments, and direct the unused balance toward the long-term sustainability
of the Zcash network. Completing existing commitments gives grantees a defined
transition and avoids treating program closure as a reason to abandon approved
work. Returning the remainder through the NSM avoids creating another
discretionary grant-making body to receive it.

The present fund restrictions need explicit attention. ZIP 1015 requires FPF
to use the ZCG allocation exclusively for grants and related administration,
and to recognize it contractually as a Restricted Fund donation. ZIP 1016
carries those obligations forward. [^zip-1015-zcg] [^zip-1016-admin] An NSM
contribution is neither a grant to an external party nor ordinary grant
administration. Express amendments are needed to authorize it within the ZIP
framework.

FPF is an independent Cayman Islands foundation company. [^fpf] Its actual
authority also depends on applicable law, its constitutional documents, and
the agreements governing the assets. Foundation companies have their own
memorandum and articles of association. [^cayman-foundation] This proposal
provides a community mandate and a process for putting the necessary legal
authority in place; it does not assume those documents have already been
reviewed or amended.


# Privacy Implications

This proposal introduces no changes to transaction privacy or wallet behavior.
Publishing the wind-down accounts and NSM contribution evidence may associate
transactions with FPF or the ZCG treasury. Reports can establish amounts and
completion without publishing grantees' private identities, payment addresses,
KYC records, or privileged legal advice. A future voluntary NSM contribution
mechanism may have additional privacy implications, as discussed in ZIP 233.
[^zip-0233]


# Requirements

* Stop new ZCG grant-making at a clearly defined cutoff.
* Complete existing commitments under their approved terms, including normal
  milestone verification and remedies for non-performance.
* Provide FPF with an explicit mandate, within the ZIP framework and the
  applicable legal instruments, to close ZCG and contribute residual funds to
  the NSM.
* Limit and disclose the costs of administering the wind-down.
* Account for the full ZCG treasury, including later receipts and recoveries,
  without diverting funds belonging to other programs.
* Safeguard commitments and residual funds until their disposition is complete.
* End the committee's operational role when its remaining duties are complete,
  while preserving necessary accounting, custody, and reporting.
* Keep the decision about existing assets separate from changes to future
  subsidy allocations and CCF governance.


# Specification

## Activation

The wind-down and the amendments to ZIPs 1015 and 1016 MUST take effect at the
designated Mainnet network upgrade activation, regardless of NSM contribution
mechanism availability or ZCG funding-stream status. This ZIP MUST already
be Active under ZIP 0. [^zip-0000]

The deployment ZIP MUST identify this ZIP and specify the upgrade's Mainnet
activation height under ZIP 200. [^zip-0200] Existing rules governing ZCG funds
continue to apply until that activation.

At activation, ZCG MUST stop accepting applications and approving new grants.
Pending applications that were not approved before activation MUST be closed
without an award.

## Administration during the wind-down

From activation, FPF and the ZCG Committee MUST administer ZCG funds solely to
complete existing commitments, meet the permitted wind-down expenses, and
contribute residual funds to the NSM as specified below.

FPF MUST notify affected applicants and existing grantees of the wind-down
and publish the designated upgrade, its Mainnet activation height, the
Wind-down Date when known, and a contact for outstanding commitments.

This ZIP does not alter block validity, funding-stream amounts or end heights,
or ownership of funds already paid to grantees. Any ZCG funding-stream receipts
that continue under the consensus rules MUST be included in the wind-down
accounts and disposed of under this ZIP. Ending those receipts requires a
separate consensus change, such as the complementary proposal.
[^end-zcg-stream]

The process MAY be rehearsed on Testnet using test funds. Testnet activation
or rehearsal MUST NOT trigger the Mainnet wind-down or authorize disposal of
Mainnet ZCG funds. Dates and reporting deadlines in this ZIP MUST be
interpreted using UTC.

## Inventory, reserves, and wind-down plan

Within 30 days after the Wind-down Date, FPF, with the ZCG Committee, MUST
publish an initial wind-down plan containing:

* ZCG balances by asset and currency, reconciled to the accounting records;
* each existing commitment, its remaining amount and currency, outstanding
  conditions, and expected completion or lawful termination date;
* a reserve sufficient to meet those commitments, including a documented
  allowance for contingent liabilities and currency risk;
* an itemized wind-down budget, with a spending cap, responsible parties, and
  an expected timetable for completing the administrative work; and
* the legal and technical prerequisites for the NSM contribution, identifying
  which have been satisfied and which remain outstanding.

The plan MUST distinguish an approved grant from an unconditional payment
liability. Its reserve MUST provide for unpaid approved milestones without
waiving their conditions. FPF MUST NOT contribute assets needed to satisfy
creditors, existing commitments, or other legal obligations to the NSM.
If assets are insufficient to meet these obligations, FPF MUST report the
shortfall and address it under the applicable agreements and law before
determining that any residual funds are available.

FPF MUST keep ZCG funds separately accounted for and MUST NOT use them for the
CCF, other FPF programs, or general FPF operations unrelated to the wind-down.

## Completion of existing commitments

FPF and the ZCG Committee MUST continue to administer existing commitments
under their approved terms, including milestone review, reporting, and any
applicable suspension, termination, or refund provisions. This ZIP does not
make conditional milestones payable in advance or excuse non-performance.

An existing commitment MAY be amended to enable completion or lawful closure,
but an amendment MUST NOT increase its approved funding amount or add a new
project or new scope of work. Any change requiring a grantee's consent MUST
obtain that consent. An unexercised option for additional funding or a
discretionary renewal MUST NOT be exercised.

For an indefinite or automatically renewing commitment, FPF MUST use the
earliest lawful non-renewal or termination opportunity consistent with its
existing obligations. The plan MUST identify the resulting final service and
payment dates. Disputed or contingent liabilities MUST remain reserved until
resolved or lawfully discharged.

Amounts released by completion, cancellation, refunds, or a reduction in a
required reserve MUST become residual funds; they MUST NOT be reassigned to
new grants.

## Wind-down expenses and committee closure

ZCG funds MAY cover reasonable, documented expenses necessary to complete the
wind-down, including grant administration, legal and accounting work, asset
conversion, custody, transaction fees, final reporting, and required record
retention. FPF MUST limit charges to work attributable to ZCG's wind-down and
MUST NOT charge unrelated programs' costs to ZCG.

The ZCG Committee MUST approve the initial wind-down budget and any increase
in its spending cap, subject to FPF's existing legal veto. Existing conflict
of interest and compensation rules MUST continue to apply. Committee and FPF
compensation MUST reflect the reduced duties and actual work required.

Until its remaining decisions are complete, the committee MUST retain the
membership and decision-making arrangements required by ZIP 1015. A vacancy
or expiring term MUST be addressed under the existing selection process if
needed to perform those duties. The wind-down does not authorize FPF to take
over discretionary grant decisions.

Once existing commitments have been completed or lawfully discharged and the
committee has approved the final administrative budget, the committee MUST
conclude its operational role. No further ZCG elections are required after
that point. FPF MUST retain responsibility for any remaining custody, NSM
contributions, reporting, and legal record retention. An expense above the
final approved cap MUST NOT be paid from ZCG funds without further community
authorization under an amendment to this ZIP.

## Legal authority and implementation

Before making an NSM contribution, FPF MUST obtain advice from qualified
Cayman Islands counsel concerning its authority to execute this wind-down,
including the restricted-fund terms, its constitutional documents, existing
contracts, and any required consents or approvals.

FPF MUST arrange for the commitments required by ZIPs 1015 and 1016 to be
amended, in suitable legal language, to authorize the uses specified here.
It MUST obtain any additional consent, corporate approval, or court order
that is necessary before taking an action that requires it. A ZIP amendment
MUST NOT be treated as automatically amending an agreement, extinguishing a
third party's rights, or overriding applicable law.

FPF MUST publish confirmation of the authority and approvals on which it
relies, without disclosing privileged advice or confidential information. If
a required authorization cannot be obtained, FPF MUST report the obstacle,
safeguard the affected funds, and seek a further community decision. Such an
obstacle MUST NOT authorize new grants or an alternative recipient.

## Contribution of residual funds to the NSM

Subject to the reserve and legal requirements above, FPF MUST contribute all
residual funds to the NSM. Residual assets held in currencies or assets other
than ZEC MUST be converted to ZEC on commercially reasonable terms, with
conversion costs included in the approved budget and disclosed in the accounts.

The contribution MUST use a deployed consensus mechanism that removes the
contributed ZEC from circulation and credits the corresponding amount to the
NSM Value Balance under ZIP 237. [^zip-0237] That mechanism MUST be active on
Mainnet when the contribution is made; publication of a ZIP, implementation
in software, or activation on Testnet alone is insufficient.

ZIP 237 defines the NSM balance and reissuance rules, but does not by itself
provide a transaction mechanism for contributing existing treasury ZEC.
ZIP 233 proposes such a voluntary mechanism, but is not deployed by NU7 as
specified in ZIP 259. [^zip-0233] [^zip-0259] A different deployed Mainnet
mechanism meeting the contribution requirements above MAY be used. This ZIP
neither deploys ZIP 233 nor supplies a new consensus mechanism.

If a suitable mechanism is not yet available, FPF MUST hold the residual
funds in segregated custody solely for a future NSM contribution and report
their balance and custody costs quarterly. FPF MUST NOT represent a payment
to an unspendable address, an excessive transaction fee, or a transfer to
another organization as fulfilling this obligation.

FPF MUST publish a contribution schedule in the wind-down plan and update it
as reserves are released. Each residual amount MUST be contributed within
90 days after all three conditions are satisfied for that amount: it is
available without impairing the required reserves, the necessary legal
authority has been obtained, and the technical mechanism is deployed.
FPF MAY combine amounts within that period to reduce transaction costs,
provided the full remaining balance is accounted for and ultimately
contributed.

For each contribution, FPF MUST publish its amount, transaction identifier,
confirmation block, and evidence that the amount was credited under the
deployed NSM mechanism. It MUST verify confirmation on the canonical chain
before recording the contribution as complete. The same rules apply to
later receipts and recoveries, including funding-stream payments received
after the initial treasury has been contributed.

## Transparency and final accounting

The existing transparency, security, and responsible disclosure obligations
in ZIPs 1015 and 1016 MUST continue during the wind-down. Reports MUST protect
confidential grantee information, private payment details, and key material;
redactions MUST NOT prevent reconciliation of the aggregate financial amounts.

FPF MUST publish quarterly progress reports reconciling opening balances,
receipts, commitment payments, expenses, conversion proceeds, NSM
contributions, reserves, and closing balances. Any missed timetable or
change in reserve or budget MUST be explained.

After existing commitments and wind-down expenses have been settled and all
residual funds then held have been contributed, FPF MUST publish a final
reconciliation and closure report. It MUST identify the custodian and retention
arrangements for legally required records and provide a contact for later
receipts, recoveries, or claims. Public reports and grant records SHOULD remain
available as a historical archive. Any later receipt or recovery, including
funding-stream receipts, MUST be accounted for and contributed under this ZIP
after provision for lawful related expenses. Custody and quarterly reporting
obligations MUST continue for any such funds pending contribution.

## Changes to ZIP 1015

In the Specification, under "Zcash Community Grants (ZCG)", insert a new
subsection "Wind-down of Zcash Community Grants" immediately before
"Furthering Decentralization", with the following text:

> At Mainnet activation on the Wind-down Date defined in the ZIP "Winding Down
> Zcash Community Grants", FPF and the ZCG Committee MUST begin winding down
> the ZCG program in accordance with that ZIP. For this limited purpose, its
> provisions take precedence over conflicting provisions of this ZIP, including
> the exclusive grant-use restriction, committee and election requirements,
> Discretionary Budget provisions, and obligations to explore an independent
> ZCG entity.
>
> The permitted purposes of the ZCG Restricted Fund donation expressly include
> completing existing commitments, paying the reasonable and limited wind-down
> expenses authorized by that ZIP, and contributing all residual funds to the
> NSM. FPF MUST arrange the corresponding amendments to the restricted-fund
> agreements and obtain the legal authority required by that ZIP before
> executing an action that requires it. These purposes do not authorize new
> grants, unrelated FPF expenditure, or diversion to another fund.
>
> An NSM contribution mandated by that ZIP is an authorized disposition of the
> Restricted Fund, rather than a grant requiring a new grant award. Compliance
> with that ZIP does not constitute a breach for the purposes of Enforcement.
> Security, separate accounting, and transparency obligations continue until
> their completion under that ZIP, with required record retention continuing
> thereafter.

Add a reference to this ZIP in that subsection and in the References section,
using its assigned identifier when available. The existing funding-stream
tables and historical allocations are unchanged by this amendment.

## Changes to ZIP 1016

In "Zcash Community Grants", append to the first paragraph:

> At Mainnet activation on the Wind-down Date defined in the ZIP "Winding Down
> Zcash Community Grants", the administration and disposition of ZCG funds are
> governed by that ZIP, including its amendments to ZIP 1015. This applies to both
> accumulated funds and any subsequent receipts for ZCG.

In "Administrative obligations and constraints", append to the first paragraph:

> These provisions are subject to the ZCG wind-down amendments specified in
> the ZIP "Winding Down Zcash Community Grants". FPF MUST arrange the
> corresponding amendments to its contractual commitments governing ZCG funds.

After the third paragraph of that section, insert:

> The ZCG wind-down amendments to ZIP 1015 and the ZIP "Winding Down Zcash
> Community Grants" apply only to ZCG funds. They are not incorporated into
> the requirements governing the Coinholder-Controlled Fund or its Key-Holder
> Organizations. For that Fund, the otherwise applicable ZIP 1015 obligations
> continue without those amendments. Neither FPF nor the ZCG Committee is
> authorized by the wind-down to dispose of Coinholder-Controlled Fund assets.

Add references to this ZIP at those insertions and in the References section,
using its assigned identifier when available. If the complementary
funding-stream proposal is also adopted, its changes to the duration and
destination of future allocations apply independently of these amendments.


# Rationale

## Completing approved work

Paying the entire treasury into the NSM immediately would leave approved work
and potential liabilities unfunded. Keeping a documented reserve permits
existing projects to finish while preserving their milestone conditions.
Closing applications and discretionary renewals provides a definite end to
grant-making. Contractual termination provisions address ongoing arrangements
without assuming that all grants end on the same date.

## Choosing the NSM for the remainder

The proposal directs the remainder toward protocol-defined network
sustainability. Transferring it to another discretionary organization or
creating a replacement grants committee would preserve the allocation role
that this proposal seeks to close. The NSM's subsequent reissuance remains
governed by its own consensus specification.

## Expressly amending the fund restrictions

Relying on an interpretation that an NSM contribution is an ordinary ZCG grant
would leave FPF's mandate unclear. Express permission in both ZIPs, together
with corresponding legal instruments, addresses the restricted-fund purpose
and the incorporation of ZIP 1015's rules by ZIP 1016. The CCF exception avoids
accidentally authorizing its wind-down through that incorporation.

## Coordinating the wind-down with a network upgrade

Mainnet activation provides a shared cutoff for ending new grant-making and,
if the complementary proposal is adopted for the same upgrade, ending future
funding-stream receipts. The proposals remain separate decisions about future
allocations and existing assets. This ZIP uses the upgrade's activation as its
process trigger without introducing its own block-validation changes.

If a voluntary NSM contribution mechanism is not available when the wind-down
begins, safe custody bridges the interval until it is deployed. Custody may
continue after the committee concludes its operational role. It introduces
continuing costs and dependence on a future deployment, which the community
should weigh when considering this ZIP.

## Community consideration

This is an initial proposal for discussion; it does not claim community
consensus. Review should consider the effect on teams that depend on future
ZCG grants, the availability of other funding channels, the proposed cutoff,
and the costs and risks of retaining funds pending an NSM contribution.


# Deployment

This ZIP is not included in NU7 as currently specified by ZIP 259. [^zip-0259]
The target upgrade and its Mainnet activation height are unassigned. A
deployment ZIP will specify them under ZIP 200. [^zip-0200]

# Reference implementation

None yet.

# Open issues

* Obtain FPF's legal review of the restricted-fund arrangements, constitutional
  documents, and required consents; identify any assets with additional
  restrictions that prevent the proposed disposition.
* Designate the target network upgrade and its Mainnet activation height in
  the deployment ZIP.
* Confirm the 30-day initial reporting period and the 90-day contribution
  period after legal and technical readiness.
* Reconcile the outstanding grant and administrative commitments with FPF and
  agree the wind-down budget and reserve methodology before implementation.
* Identify the network upgrade and operational tooling for voluntary NSM
  contributions. Decide whether to retain the proposed custody arrangement if
  deployment is substantially delayed.
* Obtain independent review of the treasury custody, contribution verification,
  and privacy arrangements before this ZIP becomes Released under ZIP 0.
* Record community feedback and any substantiated objections before seeking
  advancement beyond Draft.


# References

[^BCP14]: [Information on BCP 14 — RFC 2119 and RFC 8174](https://www.rfc-editor.org/info/bcp14/)

[^zip-0000]: [ZIP 0: ZIP Process](zip-0000.rst)

[^zip-0200]: [ZIP 200: Network Upgrade Mechanism](zip-0200.rst)

[^zip-0233]: [ZIP 233: Network Sustainability Mechanism: Removing Funds From Circulation](zip-0233.md)

[^zip-0237]: [ZIP 237: Network Sustainability Mechanism: Halving-Preserving Issuance](zip-0237.md)

[^zip-0259]: [ZIP 259: Deployment of the NU7 Network Upgrade](zip-0259.md)

[^zip-1014]: [ZIP 1014: Establishing a Dev Fund for ECC, ZF, and Major Grants](zip-1014.rst)

[^zip-1015]: [ZIP 1015: Block Subsidy Allocation for Non-Direct Development Funding](zip-1015.rst)

[^zip-1015-zcg]: [ZIP 1015: Block Subsidy Allocation for Non-Direct Development Funding — Zcash Community Grants](zip-1015.rst#zcash-community-grants-zcg)

[^zip-1016]: [ZIP 1016: Community and Coinholder Funding Model](zip-1016.md)

[^zip-1016-admin]: [ZIP 1016: Community and Coinholder Funding Model — Administrative obligations and constraints](zip-1016.md#administrativeobligationsandconstraints)

[^end-zcg-stream]: [Draft: Ending the ZCG Funding Stream in Favor of the NSM](https://github.com/zcash/zips/blob/end-zcg-stream/zips/draft-bowe-end-zcg-stream.md)

[^maxime-proposal]: [Maxime Desalle: End ZCG and send its funds to the NSM](https://forum.zcashcommunity.com/t/end-zcg-and-send-its-funds-to-the-nsm/58515)

[^cdrgp-q3-results]: [FPF: Q3 Coinholder-Directed Retroactive Grants Program Results, September 29, 2026](https://forum.zcashcommunity.com/t/q3-coinholder-directed-retroactive-grants-program-results/57909)

[^cdrgp-q3-tallies]: [Q3 2026 Coinholder-Directed Retroactive Grants Program: results and participation, with links to the finalized vote-chain tallies](https://openzcash.org/coinholders/results?round=q3-2026)

[^nu7-poll-results]: [NU7 Coinholder Vote: results published by Sean Bowe, September 14, 2026](https://forum.zcashcommunity.com/t/nu7-coinholder-vote/56912/42)

[^supply-vote-dates]: [ZEC Stats: node-derived daily Zcash supply data](https://zecstats.com/api/daily-stats). The `end_supply_zat` values for 2026-09-14 and 2026-09-29 are 1,693,284,391,554,480 and 1,695,970,641,554,480 zatoshis, respectively: 16,932,843.91554480 and 16,959,706.41554480 ZEC. These are end-of-day UTC figures; the comparison uses total issued ZEC as circulating supply. See the [supply methodology](https://zecstats.com/chart/supply).

[^cdrgp-disbursements]: [FPF: completed Q4 2025 Coinholder-Directed Retroactive Grants Program disbursements, February 4, 2026](https://forum.zcashcommunity.com/t/coinholder-directed-retroactive-grants-program-results-nov-2025/53487/19)

[^coinholder-voting-chain]: [NU7 Coinholder Vote: voting infrastructure and participation](https://forum.zcashcommunity.com/t/nu7-coinholder-vote/56912)

[^fpf]: [Financial Privacy Foundation — About Us](https://www.financialprivacyfoundation.org/)

[^cayman-foundation]: [Cayman Islands General Registry — Foundation Company](https://www.ciregistry.ky/companies-register/types-of-companies/foundation-company/)
