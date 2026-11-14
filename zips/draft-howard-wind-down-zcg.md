    ZIP: Unassigned
    Title: Winding Down Zcash Community Grants and Removal of ZCG Funds to the Network Sustainability Mechanism
    Owners: Tom Howard <tom@zcashlabs.org>
    Credits: Maxime Desalle
             Sean Bowe (Tachyon Group)
             Zooko Wilcox (Shielded Labs)
             Jason McGee (Shielded Labs)
    Status: Draft
    Category: Consensus / Process
    Created: 2026-10-28
    License: MIT
    Discussions-To: <https://forum.zcashcommunity.com/t/end-zcg-and-send-its-funds-to-the-nsm/58515>
    Pull-Request: <https://github.com/zcash/zips/pull/1423>


# Terminology

The key words "MUST", "MUST NOT", "SHOULD", and "MAY" in this document are to
be interpreted as described in BCP 14 [^BCP14] when, and only when, they appear
in all capitals.

"Zcash Community Grants" ("ZCG"), "ZCG Committee", and "Financial Privacy
Foundation" ("FPF") have the meanings given in ZIP 1015. [^zip-1015]

"Coinholder-Controlled Fund" ("CCF") has the meaning given in ZIP 1016.
[^zip-1016]

"Future Dev and Legal Defense Fund Lockbox" ("the Lockbox") means the pool
specified in the draft by Sean Bowe, Zooko Wilcox, and Jason McGee.
[^fdldf-lockbox]

"Lockbox administrator" means the entity designated by a future ZIP to
administer Lockbox withdrawals and receive residual ZCG funds for future
Zcash development and legal defense.

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
begin winding down its operations. If ZCG's 8% funding stream is still active,
the upgrade would end it and redirect the same share of the block subsidy to
the Future Dev and Legal Defense Fund Lockbox for the rest of the stream's
scheduled term. If the stream has already expired and the Lockbox has yet to
be deployed, activation would create it with a zero opening balance.

FPF would complete existing commitments under their terms and retain full
reserves for outstanding obligations and permitted wind-down expenses. FPF
would hold the surplus until a future ZIP designates the Lockbox administrator
and that entity establishes a receiving address. Once legally authorized, FPF
would transfer surplus to that address as it becomes available. If a separately
authorized NSM donation is completed before Mainnet activation, the wind-down
would apply to the remaining treasury and subsequent receipts.

ZIPs 1015 and 1016 currently restrict the purposes for which FPF may use ZCG
funds. This ZIP specifies amendments that expressly authorize completing
existing commitments, paying limited closure costs, and transferring the
remainder to the Lockbox administrator. FPF would obtain the legal instruments
and approvals needed to carry out these changes.

The wind-down would begin at Mainnet activation even if the administrator's
receiving address is still pending. Public reporting would account for the
treasury while protecting confidential grantee and financial information.


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
(CDRGP) completed its Q3 2026 round on September 29, 2026, with approximately
2.18 million ZEC of voting power participating on individual proposals.
[^cdrgp-q3-results] [^cdrgp-q3-tallies] The separate NU7 scope vote closed on
September 14, 2026, with approximately 2.40 million ZEC participating on its
issuance-schedule question. [^nu7-poll-results] Circulating supply was
approximately 16.96 million ZEC on September 29 and 16.93 million ZEC on
September 14. Both processes therefore exceeded two million ZEC of
participation, or over 12% of the circulating supply in each case.
[^supply-vote-dates]

The CDRGP has demonstrated that coinholder-directed grants are operational.
Its Q3 2026 results approve funding for core protocol work by ZODL and Valar
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

This ZIP builds on Maxime Desalle's forum proposal, "End ZCG and send its
funds to the NSM", for closing the program and honoring approved grants.
[^maxime-proposal] It uses the Future Dev and Legal Defense Fund Lockbox
proposed by Bowe, Wilcox, and McGee for the remainder of the 8% allocation.
The residual treasury would go to the entity designated to administer
withdrawals from that Lockbox. [^fdldf-lockbox]

The policy proposed here is to honor work already approved, stop creating new
commitments, and reserve the unused balance for future Zcash development and
legal defense. Completing existing commitments gives grantees a defined
transition and avoids treating program closure as a reason to abandon approved
work. The Lockbox administrator would manage the residual funds for the
same purposes under the terms of its designation.

The present fund restrictions need explicit attention. ZIP 1015 requires FPF
to use the ZCG allocation exclusively for grants and related administration,
and to recognize it contractually as a Restricted Fund donation. ZIP 1016
carries those obligations forward. [^zip-1015-zcg] [^zip-1016-admin] Express
amendments are needed to authorize FPF to transfer the residual treasury to
the Lockbox administrator.

FPF is an independent Cayman Islands foundation company. [^fpf] Its actual
authority also depends on applicable law, its constitutional documents, and
the agreements governing the assets. Foundation companies have their own
memorandum and articles of association. [^cayman-foundation] This proposal
provides a community mandate and a process for putting the necessary legal
authority in place; it does not assume those documents have already been
reviewed or amended.


# Privacy Implications

Redirecting the subsidy to the Lockbox creates no payment output. Publishing
the wind-down accounts and evidence of treasury transfers may associate
transactions with FPF or the ZCG treasury. Reports can establish amounts and
completion without publishing grantees' private identities, payment addresses,
KYC records, or privileged legal advice.


# Requirements

* Stop new ZCG grant-making at a clearly defined cutoff.
* If the 8% ZCG stream is still active, end it at activation and direct the
  same share to the Lockbox for the remainder of its scheduled term.
* Establish the Lockbox at activation even if the 8% stream has expired.
* Complete existing commitments under their approved terms, including normal
  milestone verification and remedies for non-performance.
* Provide FPF with an explicit mandate, within the ZIP framework and the
  applicable legal instruments, to close ZCG and transfer residual funds to
  the Lockbox administrator.
* Limit and disclose the costs of administering the wind-down.
* Account for the full ZCG treasury, including later receipts and recoveries,
  without diverting funds belonging to other programs.
* Safeguard commitments and residual funds until their disposition is complete.
* End the committee's operational role when its remaining duties are complete,
  while preserving necessary accounting, custody, and reporting.
* Preserve the CCF stream and governance.


# Specification

## Activation

The wind-down and the amendments to ZIPs 1015 and 1016 MUST take effect at
Mainnet activation of the designated network upgrade, regardless of the
stream's status or the availability of the Lockbox administrator's receiving
address.

The deployment ZIP MUST identify this ZIP and specify the upgrade's activation
height for each network under ZIP 200. [^zip-0200] Existing rules governing ZCG
funds continue to apply until Mainnet activation.

At Mainnet activation, ZCG MUST stop accepting applications and approving new grants.
Pending applications that were not approved before activation MUST be closed
without an award.

## The Future Dev and Legal Defense Fund Lockbox

The Lockbox consensus rules and their activation conditions are specified by
the referenced draft. [^fdldf-activation] [^fdldf-lockbox] The designated
upgrade MUST deploy those rules where they have yet to take effect, subject
to the amendment below. Where they already took effect, the upgrade MUST
carry forward the existing Lockbox and any remaining replacement stream.

**Amendment for activation after stream expiry.** Where the ZCG stream has
already expired at activation and the Lockbox does not yet exist, the Lockbox
recipient and balance rules MUST still take effect at activation. The balance
MUST be initialized to zero before applying the activation block. The
referenced draft's expiry condition continues to govern the funding streams.

## Administration during the wind-down

From Mainnet activation, FPF and the ZCG Committee MUST administer ZCG funds
solely to complete existing commitments, meet the permitted wind-down expenses,
and safeguard and transfer residual funds as specified below.

FPF MUST notify affected applicants and existing grantees of the wind-down
and publish the designated upgrade, its Mainnet activation height, the
Wind-down Date when known, and a contact for outstanding commitments.

This ZIP does not alter ownership of funds already paid to grantees. Any
ZCG funds received after activation MUST be included in the wind-down accounts
and disposed of under this ZIP.

The process MAY be rehearsed on Testnet using test funds. Testnet activation
or rehearsal MUST NOT trigger the Mainnet wind-down or authorize disposal of
Mainnet ZCG funds. Dates and reporting deadlines in this ZIP MUST be
interpreted using UTC.

## Inventory, reserves, and wind-down plan

Within 30 days after the Wind-down Date, FPF, with the ZCG Committee, MUST
publish an initial wind-down plan containing:

* ZCG balances by asset and currency, reconciled to the accounting records,
  with any separately authorized pre-activation NSM donation shown separately;
* each existing commitment, its remaining amount and currency, outstanding
  conditions, and expected completion or lawful termination date, subject to
  the reporting protections below;
* reserves sufficient to meet those commitments and permitted wind-down
  expenses, including a documented allowance for contingent liabilities and
  currency risk;
* an itemized wind-down budget, with a spending cap, responsible parties, and
  an expected timetable for completing the administrative work; and
* the prerequisites for transferring residual funds, identifying
  which have been satisfied and which remain outstanding.

The plan MUST distinguish an approved grant from an unconditional payment
liability. Its reserve MUST provide for unpaid approved milestones without
waiving their conditions. FPF MUST reserve assets needed to satisfy creditors,
existing commitments, and other legal obligations before transferring surplus.
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

FPF MUST account for amounts released by completion, cancellation, refunds,
or a reduction in a required reserve when recalculating residual funds.

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
conclude its operational role. The final budget MUST provide for any remaining
custody, transfers, reporting, and legal record retention. FPF
MUST retain responsibility for those duties. After committee closure, any
increase to the cap for spending from ZCG funds MUST be authorized through an
amendment to this ZIP. FPF MUST disclose any projected shortfall in its
quarterly report.

## Legal authority and implementation

The 50,000 ZEC NSM donation described in the Bowe, Wilcox, and McGee draft
may be completed before Mainnet activation if separately approved and lawful
under the restrictions applicable at the time. [^fdldf-donation] This ZIP
governs the ZCG funds remaining at Mainnet activation and any later receipts
or recoveries.

Before transferring residual funds, FPF MUST obtain advice from qualified
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

## Transfer of residual funds to the Lockbox administrator

FPF MUST hold residual funds in segregated custody pending transfer and
report the balance and custody costs quarterly. Before transferring funds,
FPF MUST obtain the legal authority required above and verify a Mainnet
receiving address established and controlled by the entity designated in an
accepted ZIP.

FPF MUST transfer residual funds to that address in ZEC, retaining sufficient
reserves for all outstanding obligations and permitted wind-down expenses.
FPF MUST convert residual assets other than ZEC on commercially reasonable
terms, with conversion costs included in the approved budget and disclosed in
the accounts. The designated entity MUST account for the received funds
separately from the Lockbox's on-chain balance and administer them for future
Zcash development and legal defense under the terms of the accepted ZIP and
applicable legal instruments.

FPF MUST publish a transfer schedule in the wind-down plan and update it as
reserves are released. Each residual amount MUST be transferred within 90 days
after it becomes available without impairing required reserves and the
designation, address verification, and legal prerequisites above are met.
FPF MAY combine amounts within that period to reduce transaction costs.

For each transfer, FPF MUST verify confirmation on the canonical chain and
publish its amount, transaction identifier, confirmation block, and evidence
of receipt by the designated entity. The same rules apply to later receipts
and recoveries.

## Transparency and final accounting

The existing transparency, security, and responsible disclosure obligations
in ZIPs 1015 and 1016 MUST continue during the wind-down. Reports MUST protect
confidential grantee information, private payment details, and key material;
redactions MUST NOT prevent reconciliation of the aggregate financial amounts.

FPF MUST publish quarterly progress reports reconciling opening balances,
receipts, commitment payments, expenses, conversion proceeds, transfers to
the Lockbox administrator, reserves, and closing balances. FPF MUST explain
any missed timetable or change in reserve or budget.

After existing commitments and wind-down expenses have been settled and all
residual funds then held have been transferred, FPF MUST publish a final
reconciliation and closure report. It MUST identify the custodian and retention
arrangements for legally required records and provide a contact for later
receipts, recoveries, or claims. Public reports and grant records SHOULD remain
available as a historical archive. Any later receipt or recovery MUST be
accounted for and transferred under this ZIP after provision for lawful related
expenses. Custody and quarterly reporting obligations MUST continue for any
such funds pending transfer.

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
> expenses authorized by that ZIP, and transferring all residual funds to the
> entity designated to administer withdrawals from the Future Dev and Legal
> Defense Fund Lockbox. FPF MUST arrange the corresponding amendments to the
> restricted-fund agreements and obtain the legal authority required by that
> ZIP before executing an action that requires it. These
> purposes do not authorize new grants, unrelated FPF expenditure, or diversion
> to another fund.
>
> A transfer mandated by that ZIP is an authorized disposition of the
> Restricted Fund. Compliance with that ZIP satisfies the prescribed-use
> requirement for the purposes of Enforcement.
> Security, separate accounting, and transparency obligations continue until
> their completion under that ZIP, with required record retention continuing
> thereafter.

Add a reference to this ZIP in that subsection and in the References section,
using its assigned identifier when available. The existing funding-stream
tables and historical allocations are unchanged by this amendment.

## Changes to ZIP 1016

In the Abstract, qualify the 8% allocation to ZCG by noting that the ZIP
"Winding Down Zcash Community Grants" redirects the remainder of that stream
at activation if it is still active.

In "Zcash Community Grants", append to the first paragraph:

> At Mainnet activation on the Wind-down Date defined in the ZIP "Winding Down
> Zcash Community Grants", the administration and disposition of ZCG funds are
> governed by that ZIP, including its amendments to ZIP 1015. This applies to both
> accumulated funds and any subsequent receipts for ZCG.

After the paragraph describing the stream's end height, add:

> If the stream is still active at the designated upgrade's activation, it
> ends at that activation height. The same 8% is credited to the Future Dev
> and Legal Defense Fund Lockbox through the remainder of the original term,
> as specified in "Winding Down Zcash Community Grants".

In the first paragraph of "Coinholder-Controlled Fund", replace "for the
same time period as the Zcash Community Grants stream" with "for the period
specified by the start and end heights of `FS_CCF_H3` in ZIP 214". [^zip-0214]

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
using its assigned identifier when available.


# Rationale

## Completing approved work

Staged transfers let FPF move available surplus while keeping a
documented reserve for approved work, potential liabilities, and wind-down
expenses. Existing projects can finish under their milestone conditions.
Closing applications and discretionary renewals provides a definite end to
grant-making. Contractual termination provisions address ongoing arrangements
without assuming that all grants end on the same date.

## Funding future development and legal defense

The Lockbox holds the subsidy allocation for future development and legal
defense. The entity designated to administer its withdrawals would manage the
residual ZCG treasury separately for those same purposes. [^fdldf-lockbox]

## Expressly amending the fund restrictions

Express permission in both ZIPs and the corresponding legal instruments
gives FPF a mandate to transfer the restricted funds to the designated
entity. The CCF exception confines the wind-down to ZCG funds when ZIP 1016
incorporates ZIP 1015's rules.

## Coordinating the wind-down with a network upgrade

Mainnet activation ends new grant-making and, if the ZCG stream is still
active, redirects its remaining subsidy allocation to the Lockbox.

FPF may need to hold the residual treasury after the committee concludes its
operational role while a future ZIP designates the Lockbox administrator and
the entity establishes a receiving address. The wind-down budget accounts
for that custody.

## Community consideration

This is an initial proposal for discussion; it does not claim community
consensus. Review should consider the effect on teams that depend on future
ZCG grants, the availability of other funding channels, the proposed cutoff,
and the costs and risks of retaining funds pending transfer.


# Deployment

This ZIP is not included in NU7 as currently specified by ZIP 259. [^zip-0259]
The target upgrade is after NU7. Its deployment ZIP will specify the
activation height for each network under ZIP 200. [^zip-0200] The upgrade
will establish the Lockbox where needed and redirect any remaining ZCG stream
as specified above. Mainnet activation starts the wind-down even if the
Lockbox administrator has yet to be designated.

# Reference implementation

None yet.

# Open issues

* Obtain FPF's legal review of the restricted-fund arrangements, constitutional
  documents, and required consents; identify any assets with additional
  restrictions that prevent the proposed disposition.
* Designate the target network upgrade and its Mainnet activation height in
  the deployment ZIP.
* Confirm the 30-day initial reporting period and the 90-day transfer period
  after all prerequisites are met.
* Reconcile the outstanding grant and administrative commitments with FPF and
  agree the wind-down budget and reserve methodology before implementation.
* Designate the Lockbox administrator and specify the terms under which it
  will receive and administer residual ZCG funds in a future ZIP.
* Obtain independent review of the treasury custody, transfer verification,
  and privacy arrangements before this ZIP becomes Released under ZIP 0.
  [^zip-0000]
* Record community feedback and any substantiated objections before seeking
  advancement beyond Draft.


# References

[^BCP14]: [Information on BCP 14 — RFC 2119 and RFC 8174](https://www.rfc-editor.org/info/bcp14/)

[^zip-0000]: [ZIP 0: ZIP Process](zip-0000.rst)

[^zip-0200]: [ZIP 200: Network Upgrade Mechanism](zip-0200.rst)

[^zip-0214]: [ZIP 214: Consensus Rules for a Zcash Development Fund](zip-0214.rst)

[^zip-0259]: [ZIP 259: Deployment of the NU7 Network Upgrade](zip-0259.md)

[^zip-1014]: [ZIP 1014: Establishing a Dev Fund for ECC, ZF, and Major Grants](zip-1014.rst)

[^zip-1015]: [ZIP 1015: Block Subsidy Allocation for Non-Direct Development Funding](zip-1015.rst)

[^zip-1015-zcg]: [ZIP 1015: Block Subsidy Allocation for Non-Direct Development Funding — Zcash Community Grants](zip-1015.rst#zcash-community-grants-zcg)

[^zip-1016]: [ZIP 1016: Community and Coinholder Funding Model](zip-1016.md)

[^zip-1016-admin]: [ZIP 1016: Community and Coinholder Funding Model — Administrative obligations and constraints](zip-1016.md#administrativeobligationsandconstraints)

[^fdldf-activation]: [Bowe, Wilcox, and McGee: Activation](https://github.com/aquietinvestor/zips/blob/future-dev-legal-defense-fund/zips/draft-mcgee-future-dev-legal-defense-fund.md#activation)

[^fdldf-lockbox]: [Bowe, Wilcox, and McGee: Future Dev and Legal Defense Fund Lockbox](https://github.com/aquietinvestor/zips/blob/future-dev-legal-defense-fund/zips/draft-mcgee-future-dev-legal-defense-fund.md#the-future-dev-and-legal-defense-fund-lockbox) ([draft PR](https://github.com/zcash/zips/pull/1428))

[^fdldf-donation]: [Bowe, Wilcox, and McGee: The donation](https://github.com/aquietinvestor/zips/blob/future-dev-legal-defense-fund/zips/draft-mcgee-future-dev-legal-defense-fund.md#the-donation)

[^maxime-proposal]: [Maxime Desalle: End ZCG and send its funds to the NSM](https://forum.zcashcommunity.com/t/end-zcg-and-send-its-funds-to-the-nsm/58515)

[^cdrgp-q3-results]: [FPF: Q3 Coinholder-Directed Retroactive Grants Program Results, September 29, 2026](https://forum.zcashcommunity.com/t/q3-coinholder-directed-retroactive-grants-program-results/57909)

[^cdrgp-q3-tallies]: [Q3 2026 Coinholder-Directed Retroactive Grants Program: results and participation, with links to the finalized vote-chain tallies](https://openzcash.org/coinholders/results?round=q3-2026)

[^nu7-poll-results]: [NU7 Coinholder Vote: results published by Sean Bowe, September 14, 2026](https://forum.zcashcommunity.com/t/nu7-coinholder-vote/56912/42)

[^supply-vote-dates]: [ZEC Stats: node-derived daily Zcash supply data](https://zecstats.com/api/daily-stats). The `end_supply_zat` values for 2026-09-14 and 2026-09-29 are 1,693,284,391,554,480 and 1,695,970,641,554,480 zatoshis, respectively: 16,932,843.91554480 and 16,959,706.41554480 ZEC. These are end-of-day UTC figures; the comparison uses total issued ZEC as circulating supply. See the [supply methodology](https://zecstats.com/chart/supply).

[^cdrgp-disbursements]: [FPF: completed Q4 2025 Coinholder-Directed Retroactive Grants Program disbursements, February 4, 2026](https://forum.zcashcommunity.com/t/coinholder-directed-retroactive-grants-program-results-nov-2025/53487/19)

[^coinholder-voting-chain]: [NU7 Coinholder Vote: voting infrastructure and participation](https://forum.zcashcommunity.com/t/nu7-coinholder-vote/56912)

[^fpf]: [Financial Privacy Foundation — About Us](https://www.financialprivacyfoundation.org/)

[^cayman-foundation]: [Cayman Islands General Registry — Foundation Company](https://www.ciregistry.ky/companies-register/types-of-companies/foundation-company/)
