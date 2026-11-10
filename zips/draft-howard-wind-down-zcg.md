    ZIP: Unassigned
    Title: Winding Down Zcash Community Grants
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
    Updates: 207, 209, 214, 1015, 1016


# Terminology

The key words "MUST", "MUST NOT", "SHOULD", and "MAY" in this document are to
be interpreted as described in BCP 14 [^BCP14] when, and only when, they appear
in all capitals.

"Zcash Community Grants" ("ZCG"), "ZCG Committee", and "Financial Privacy
Foundation" ("FPF") have the meanings given in ZIP 1015. [^zip-1015]

"Coinholder-Controlled Fund" ("CCF") has the meaning given in ZIP 1016.
[^zip-1016]

"Future Dev and Legal Defense Fund Lockbox" ("the Lockbox") means the
in-protocol pool identified by `FDLDF_POOL` and tracked by `FDLDFBalance` in
the draft by Sean Bowe, Zooko Wilcox, and Jason McGee. [^fdldf-lockbox]

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
reserves for outstanding obligations and permitted wind-down expenses. Once
legally authorized and technically able to deposit, FPF would contribute
surplus to the Lockbox as it becomes available. If a separately authorized
NSM donation is completed before Mainnet activation, the wind-down would
apply to the remaining treasury and subsequent receipts.

ZIPs 1015 and 1016 currently restrict the purposes for which FPF may use ZCG
funds. This ZIP specifies amendments that expressly authorize completing
existing commitments, paying limited closure costs, and contributing the
remainder to the Lockbox. It also calls for corresponding legal instruments and
approvals so that the change can be executed consistently with FPF's legal
obligations, rather than assuming a ZIP alone changes existing agreements.

The 12% CCF stream is unchanged. The wind-down can begin before a mechanism
for depositing existing ZEC into the Lockbox is deployed. Until such a
mechanism is available, FPF would safeguard the residual funds solely for
that purpose. Public reporting would establish the disposition of the treasury
while protecting confidential grantee and financial information.


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
proposed by Bowe, Wilcox, and McGee for both the remaining term of the 8%
allocation and the residual treasury. [^fdldf-lockbox]

The policy proposed here is to honor work already approved, stop creating new
commitments, and reserve the unused balance for future Zcash development and
legal defense. Completing existing commitments gives grantees a defined
transition and avoids treating program closure as a reason to abandon approved
work. Crediting the remainder to the Lockbox avoids creating another
discretionary grant-making body to receive it.

The present fund restrictions need explicit attention. ZIP 1015 requires FPF
to use the ZCG allocation exclusively for grants and related administration,
and to recognize it contractually as a Restricted Fund donation. ZIP 1016
carries those obligations forward. [^zip-1015-zcg] [^zip-1016-admin] A Lockbox
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

Redirecting the subsidy to the Lockbox creates no payment output. A future
deposit mechanism may have its own privacy implications. Publishing the
wind-down accounts and Lockbox contribution evidence may associate
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
  applicable legal instruments, to close ZCG and contribute residual funds to
  the same Lockbox.
* Limit and disclose the costs of administering the wind-down.
* Account for the full ZCG treasury, including later receipts and recoveries,
  without diverting funds belonging to other programs.
* Safeguard commitments and residual funds until their disposition is complete.
* End the committee's operational role when its remaining duties are complete,
  while preserving necessary accounting, custody, and reporting.
* Preserve the CCF stream and governance.


# Specification

## Activation

Let $A$ be this ZIP's activation height on a network, and $N$ that network's
NU7 activation height. $A$ MUST be greater than $N$. Let $E$ be the end height
of `FS_FPF_ZCG_H3` under Revision 3 of ZIP 214 [^zip-0214], at the third halving
under ZIP 218's 25-second blocks [^zip-0218]. Then $E = N + 3 \cdot (H_3 - N)$,
where $H_3$ is the pre-NU7 third-halving height (4406400 on Mainnet, 4476000 on
Testnet). With $N = 3543405$ on Mainnet and $N = 4465026$ on Testnet [^zip-0259],
$E = 6132390$ on Mainnet and $E = 4497948$ on Testnet. End heights are exclusive,
as specified in ZIP 207. [^zip-0207]

The stream redirection below applies only on a network where $A < E$. Where
$A \geq E$, the ZCG stream has already ended and this ZIP does not restart it.

The wind-down and the amendments to ZIPs 1015 and 1016 MUST take effect at the
Mainnet activation height $A$, regardless of the stream's status or whether
the Lockbox accepts deposits of existing ZEC.

The deployment ZIP MUST identify this ZIP and specify the upgrade's activation
height for each network under ZIP 200. [^zip-0200] Existing rules governing ZCG
funds continue to apply until Mainnet activation.

At Mainnet activation, ZCG MUST stop accepting applications and approving new grants.
Pending applications that were not approved before activation MUST be closed
without an award.

## The Future Dev and Legal Defense Fund Lockbox

The Lockbox reserves funds for future Zcash development and legal defense.
Spending from it requires a future consensus change. [^fdldf-lockbox]

**Funding streams.** On each network where $A < E$ and `FS_FPF_ZCG_H3` would
otherwise remain active at $A$, a new revision of ZIP 214 [^zip-0214] makes
the following changes at activation:

* Set the exclusive end height of `FS_FPF_ZCG_H3` to $A$. Preserve its recipient
  at each height where the stream was active before $A$, using the existing
  address-period calculations and ZIP 2008's address list update where
  applicable. [^zip-0207] [^zip-2008]
* Add `FS_FDLDF_H3` with numerator 8, denominator 100, inclusive start height
  $A$, and exclusive end height $E$. Every recipient entry is `FDLDF_POOL`.
  ZIP 207's funding-stream calculation gives its value in whole zatoshis.

If the same redirection already took effect, the existing `FS_FDLDF_H3`
schedule carries forward. `FS_CCF_H3` and the Deferred Dev Fund Lockbox
continue under their existing rules.

**Recipient and coinbase accounting.** A new revision of ZIP 207 adds
`FDLDF_POOL` as a funding-stream recipient, using the same form of accounting
as `DEFERRED_POOL` under ZIP 2001. [^zip-2001] In the protocol specification's
funding-stream payment rules, add `FDLDF_POOL` to the allowed recipient
identifiers and exclude it from the rule requiring a coinbase output to pay
an address. Credit its value to the Lockbox balance. [^protocol]

For a block height $h \in \mathbb{N}$, define
$\mathsf{totalFDLDFOutput}(h)$ in § 7.8 as the sum of $\mathsf{fs.Value}(h)$,
in zatoshis, over the active funding streams whose recipient at $h$ is
`FDLDF_POOL`. The sum is zero when there are no such streams. In § 7.1.2,
add $\mathsf{totalFDLDFOutput}(h)$ to the coinbase transaction's total output
value alongside $\mathsf{totalDeferredOutput}(h)$.

**Chain value pool balance.** On each network, if the Lockbox is being
deployed for the first time, initialize its balance to zero before applying
the block at height $A$. This initialization also applies where $A \geq E$.
An existing Lockbox carries forward its accumulated balance. In § 4.17,
define the Lockbox balance in zatoshis through height $h$ as

$$\mathsf{FDLDFBalance}(h) := \sum_{i=0}^{h} \mathsf{totalFDLDFOutput}(i).$$

Include this balance in $\mathsf{IssuedSupply}(h)$ and in the set of pools
subject to ZIP 209. [^zip-0209] Nodes MUST reject a block that would make any
of those pool balances negative or make their sum, computed without overflow,
exceed $\mathsf{MAX\_MONEY}$ zatoshis.

## Administration during the wind-down

From Mainnet activation, FPF and the ZCG Committee MUST administer ZCG funds
solely to complete existing commitments, meet the permitted wind-down expenses,
and contribute residual funds to the Lockbox as specified below.

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
* the legal and technical prerequisites for Lockbox contributions, identifying
  which have been satisfied and which remain outstanding.

The plan MUST distinguish an approved grant from an unconditional payment
liability. Its reserve MUST provide for unpaid approved milestones without
waiving their conditions. FPF MUST NOT contribute to the Lockbox any assets
needed to satisfy creditors, existing commitments, or other legal obligations.
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
custody, Lockbox contributions, reporting, and legal record retention. FPF
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

Before making a Lockbox contribution, FPF MUST obtain advice from qualified
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

## Contribution of residual funds to the Lockbox

FPF MUST contribute each residual amount to the Lockbox as it becomes
available under the conditions below, retaining sufficient reserves for all
outstanding obligations and permitted wind-down expenses. Residual assets held
in currencies or assets other than ZEC MUST be converted to ZEC on commercially
reasonable terms, with conversion costs included in the approved budget and
disclosed in the accounts.

The contribution MUST use a consensus mechanism active on Mainnet that
debits the contributed ZEC from its source pool and credits the same amount
to `FDLDFBalance` without new issuance. A separate consensus specification
MUST extend the balance calculation above to include those deposits.

If a suitable mechanism is not yet available, FPF MUST hold the residual
funds in segregated custody solely for a future Lockbox contribution and report
their balance and custody costs quarterly. FPF MUST NOT represent a payment
to an unspendable address, an excessive transaction fee, or a transfer to
another organization as fulfilling this obligation.

FPF MUST publish a contribution schedule in the wind-down plan and update it
as reserves are released. Each residual amount MUST be contributed within
90 days after all three conditions are satisfied for that amount: it is
available without impairing the required reserves, the necessary legal
authority has been obtained, and the deposit mechanism is active on Mainnet.
FPF MAY combine amounts within that period to reduce transaction costs,
provided the full remaining balance is accounted for and ultimately
contributed.

For each contribution, FPF MUST publish its amount, transaction identifier,
confirmation block, and evidence that the amount was credited under the
deployed Lockbox deposit mechanism. It MUST verify confirmation on the canonical
chain before recording the contribution as complete. The same rules apply to
later receipts and recoveries after the initial treasury has been contributed.

## Transparency and final accounting

The existing transparency, security, and responsible disclosure obligations
in ZIPs 1015 and 1016 MUST continue during the wind-down. Reports MUST protect
confidential grantee information, private payment details, and key material;
redactions MUST NOT prevent reconciliation of the aggregate financial amounts.

FPF MUST publish quarterly progress reports reconciling opening balances,
receipts, commitment payments, expenses, conversion proceeds, Lockbox
contributions, reserves, and closing balances. Any missed timetable or
change in reserve or budget MUST be explained.

After existing commitments and wind-down expenses have been settled and all
residual funds then held have been contributed, FPF MUST publish a final
reconciliation and closure report. It MUST identify the custodian and retention
arrangements for legally required records and provide a contact for later
receipts, recoveries, or claims. Public reports and grant records SHOULD remain
available as a historical archive. Any later receipt or recovery MUST be
accounted for and contributed under this ZIP after provision for lawful related
expenses. Custody and quarterly reporting obligations MUST continue for any
such funds pending contribution.

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
> Future Dev and Legal Defense Fund Lockbox. FPF MUST arrange the corresponding
> amendments to the restricted-fund agreements and obtain the legal authority
> required by that ZIP before executing an action that requires it. These
> purposes do not authorize new grants, unrelated FPF expenditure, or diversion
> to another fund.
>
> A Lockbox contribution mandated by that ZIP is an authorized disposition of the
> Restricted Fund, rather than a grant requiring a new grant award. Compliance
> with that ZIP does not constitute a breach for the purposes of Enforcement.
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

Staged contributions let FPF deposit available surplus while keeping a
documented reserve for approved work, potential liabilities, and wind-down
expenses. Existing projects can finish under their milestone conditions.
Closing applications and discretionary renewals provides a definite end to
grant-making. Contractual termination provisions address ongoing arrangements
without assuming that all grants end on the same date.

## Choosing the Lockbox for both allocations

Both sources are reserved in the same protocol pool for future Zcash
development and legal defense. A future ZIP would specify how the Lockbox
can be spent. [^fdldf-lockbox]

## Expressly amending the fund restrictions

Relying on an interpretation that a Lockbox contribution is an ordinary ZCG grant
would leave FPF's mandate unclear. Express permission in both ZIPs, together
with corresponding legal instruments, addresses the restricted-fund purpose
and the incorporation of ZIP 1015's rules by ZIP 1016. The CCF exception avoids
accidentally authorizing its wind-down through that incorporation.

## Coordinating the wind-down with a network upgrade

Mainnet activation ends new grant-making and, if the ZCG stream is still
active, redirects its remaining subsidy allocation to the Lockbox.

If a Lockbox deposit mechanism is not available when the wind-down
begins, safe custody bridges the interval until it is deployed. Custody may
continue after the committee concludes its operational role. It introduces
continuing costs and dependence on a future deployment, which the community
should weigh when considering this ZIP.

## Community consideration

This is an initial proposal for discussion; it does not claim community
consensus. Review should consider the effect on teams that depend on future
ZCG grants, the availability of other funding channels, the proposed cutoff,
and the costs and risks of retaining funds pending a Lockbox contribution.


# Deployment

This ZIP is not included in NU7 as currently specified by ZIP 259. [^zip-0259]
The target upgrade is after NU7. Its deployment ZIP will specify the
activation height for each network under ZIP 200. [^zip-0200] The upgrade
will establish the Lockbox where needed and redirect any remaining ZCG stream
as specified above. Mainnet activation starts the wind-down even if deposits
of existing ZEC into the Lockbox are not yet supported.

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
* Specify and deploy a consensus mechanism for deposits of existing ZEC into
  the Lockbox.
* Obtain independent review of the treasury custody, contribution verification,
  and privacy arrangements before this ZIP becomes Released under ZIP 0.
  [^zip-0000]
* Record community feedback and any substantiated objections before seeking
  advancement beyond Draft.


# References

[^BCP14]: [Information on BCP 14 — RFC 2119 and RFC 8174](https://www.rfc-editor.org/info/bcp14/)

[^protocol]: [Zcash Protocol Specification](protocol/protocol.pdf)

[^zip-0000]: [ZIP 0: ZIP Process](zip-0000.rst)

[^zip-0200]: [ZIP 200: Network Upgrade Mechanism](zip-0200.rst)

[^zip-0207]: [ZIP 207: Funding Streams](zip-0207.rst)

[^zip-0209]: [ZIP 209: Prohibit Out-of-Range Chain Value Pool Balances](zip-0209.rst)

[^zip-0214]: [ZIP 214: Consensus Rules for a Zcash Development Fund](zip-0214.rst)

[^zip-0218]: [ZIP 218: 25-second Block Target Spacing](zip-0218.md)

[^zip-0259]: [ZIP 259: Deployment of the NU7 Network Upgrade](zip-0259.md)

[^zip-1014]: [ZIP 1014: Establishing a Dev Fund for ECC, ZF, and Major Grants](zip-1014.rst)

[^zip-1015]: [ZIP 1015: Block Subsidy Allocation for Non-Direct Development Funding](zip-1015.rst)

[^zip-1015-zcg]: [ZIP 1015: Block Subsidy Allocation for Non-Direct Development Funding — Zcash Community Grants](zip-1015.rst#zcash-community-grants-zcg)

[^zip-1016]: [ZIP 1016: Community and Coinholder Funding Model](zip-1016.md)

[^zip-1016-admin]: [ZIP 1016: Community and Coinholder Funding Model — Administrative obligations and constraints](zip-1016.md#administrativeobligationsandconstraints)

[^zip-2001]: [ZIP 2001: Lockbox Funding Streams](zip-2001.rst)

[^zip-2008]: [ZIP 2008: Update to FS_FPF_ZCG_H3 address list](zip-2008.md)

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
