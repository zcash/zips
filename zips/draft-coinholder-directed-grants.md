# ZIP XXXX: Coinholder-Directed Retroactive Grants Program

Owners: Jason McGee (<jason@shieldedlabs.net>)  
Credits: Alex Bornstein; Josh Swihart  
Status: Proposed  
Category: Process / Consensus  
Created: 2025-10-14  
License: MIT  
Pull Request: TBD

---

## Terminology

The key words “MUST”, “SHOULD”, and “MAY” are to be interpreted as described in BCP 14 [1] when used in all capitals.

The meanings of Mainnet, Testnet, Electric Coin Company, Zcash Foundation, Bootstrap Project, Deferred Dev Fund Lockbox, Key-Holder Organizations, and Shielded Labs are as defined in ZIP 1016 [2].

“Coinholder Grants Program” refers to the 12% funding stream and multisig-controlled treasury defined in ZIP 1016.

“Retroactive Grants Program” refers to the operational process defined in this ZIP.

“Administrator” refers to an organization to be designated prior to activation of this ZIP, which SHALL administer the Coinholder Grants Program.

“Voting Authorities” are operators of the BFT voting chain used to collect shielded ballots.

“Incoming Viewing Key (IVK)” and “Full Viewing Key (FVK)” have the meanings used in the Orchard protocol. The IVK reveals incoming transaction values and memo data, but does not reveal any information about when outputs are spent.

“ZEC” refers to the Zcash mainnet currency.

---

## Abstract

This ZIP defines how the Coinholder Grants Program established in ZIP 1016 operates. It specifies a retroactive funding model, Administrator responsibilities, shielded and transparent voting procedures, participation thresholds, funding prioritization, partial funding, and payment execution by Key-Holder Organizations.

---

## Motivation

ZIP 1015 [3] introduced a temporary, non-direct funding model that directed 12% of block rewards to a protocol lockbox and 8% to Zcash Community Grants (ZCG).

ZIP 1016 extends this by defining the Community and Coinholder Funding Model, allocating 12% of block rewards to a Coinholder Grants Program and 8% to ZCG through Zcash’s third halving.

While ZIP 1016 establishes a funding stream for coinholder-directed grants, it does not define how proposals are submitted, reviewed, voted, prioritized, or paid. This ZIP provides that missing operational process so that the Coinholder Grants Program can function as intended.

---

## Requirements (design constraints)

The Coinholder Grants Program is intended to fund only retroactive grants for work that is already completed and can be publicly verified.  

The design of this ZIP is constrained to align with the coinholder decision-making mechanisms established in ZIP 1016.  

The process described in this ZIP is intended to provide transparency around proposals, voting outcomes, and disbursements.  

The roles of the Administrator, Key-Holder Organizations, Voting Authorities, and coinholders are expected to be clearly defined and distinguishable.  

This ZIP is written with the intention of describing custody, security, and compliance responsibilities in a clear and understandable manner.  

The design is constrained to remain compatible with ZIP 1016 and with the NU6.1 funding specification that governs key custody.  

The process described in this ZIP is intended to operate on a quarterly cycle, with recurring rounds for proposal submission, review, voting, and disbursement.

---

## Non-Requirements

This ZIP does not modify other Zcash funding programs or governance structures.  
This ZIP does not change consensus parameters or introduce new funding streams.

---

## Specification

### 1. Program Structure and Custody

The Coinholder Grants Program SHALL be administered by an organization to be designated prior to activation, referred to as the Administrator.

Key custody and the n-of-m multisignature scheme controlling the Coinholder-Controlled Fund SHALL follow the NU6.1 funding specification referenced by ZIP 1016. Key-Holder Organizations MUST execute disbursements according to NU6.1 and ZIP 1016’s veto provisions [4].

Only completed and publicly verifiable work is eligible to be funded.

The Administrator MUST maintain publicly accessible resources including program rules, submission formats, timelines, voting instructions, and historical reports.

---

### 2. Administrator Duties

The Administrator MUST operate the proposal submission workflow, perform eligibility screening, and publish qualified proposals.

The Administrator MUST provide written guidance on voting processes, including registration windows, voting mechanics, ballot formats, deadlines, and audit instructions.

The Administrator MUST publish proposal lists, voting parameters, tallies, participation metrics, and disbursement results for each cycle.

The Administrator MUST retain records sufficient to reproduce vote tallies and payment reports.

The Administrator MAY appoint a delegate to assist with executing any part of the quarterly process, including proposal administration, voting logistics, tally verification, and reporting.

---

### 3. KYC and Compliance

The Administrator MUST perform KYC verification for any grant exceeding 50,000 USD (or ZEC equivalent at disbursement) prior to payment.

The Administrator MUST comply with applicable legal, tax, and reporting requirements.

---

## 4. Voting Process

Two voting methods are supported: shielded voting and transparent voting. The Administrator MUST publish cycle parameters and provide sufficient information for independent auditing.

---

### 4.1 Shielded Voting

Shielded voting SHOULD be conducted through the dedicated Coin Voting 2.0 [5] application, which uses Orchard addresses and the Halo2 proof system to verify balances and prevent double spending [6].

The Administrator MUST define a registration window of at least 10 days. Eligibility is determined by Orchard notes created within the defined block range.

The Administrator MUST publish voting guidance to coinholders. This guidance SHOULD include advising participants to move funds out of any wallet used for voting before entering a seed phrase into the Coin Voting 2.0 application, in order to reduce risk if the third-party application is compromised.

Coinholders MAY vote using the shielded voting application.

Votes MUST be submitted to a BFT voting chain operated by at least four independent Voting Authorities. If at least two-thirds of Voting Authorities are honest, vote suppression or manipulation becomes infeasible.

The Administrator MUST collect and publish finalized tallies. Independent auditors MAY verify the results using the published election data.

---

### 4.2 Transparent Voting

Before accepting votes, the Administrator MUST publish the IVK for the Orchard address designated for receiving vote messages and payments. The FVK MUST NOT be published.

Voters MUST create a signed message indicating their vote and transparent address using ECDSA over secp256k1 for the signature.

Voters MUST send the signed message and a payment of at least 1 ZEC to the address associated with the published IVK.

The Administrator MUST ignore submissions with payments below 1 ZEC.

Voters MUST NOT move submitted funds until voting concludes, as specifed in the Quarterly Timeline below.

The Administrator MUST publish IVK-based audit data and all received vote messages to allow verification.

---

## 5. Participation and Voting Thresholds

A proposal MUST have at least 420,000 ZEC participating to be eligible for approval, as specifed in ZIP 1016.

A proposal is approved if a simple majority of participating votes are “Yes.”

Each proposal vote is independent, and coins MAY be reused across proposals in the same cycle.

---

## 6. Proposal Funding and Disbursement

After votes are complete, the Administrator MUST publish final voting results within seven days. The results MUST include total participation, per-proposal tallies, and data necessary for independent auditing.

The Administrator MUST produce a ranked list of approved proposals based on the percentage of “Yes” votes.

Funds MUST be allocated starting from the highest-ranked approved proposal until the treasury is exhausted.

If insufficient funds remain to fully fund the next approved proposal, the Key-Holder Organizations MAY partially fund it up to the remaining balance.

Approved proposals not funded or partially funded MAY be resubmitted in future quarters.

Key-Holder Organizations MUST execute payments using the NU6.1 multisignature scheme and MUST publish transaction identifiers.

The Administrator MUST publish a disbursement report detailing allocated amounts, partial disbursements, and executed transactions.

---

## 7. Quarterly Timeline

| Phase                         | Approximate Duration | Description |
|------------------------------|-----------------------|-------------|
| Public Call for Proposals    | ~ 1 month             | The Administrator or its delegate announces an open call via community channels. Applicants prepare and submit completed-work proposals for consideration. |
| Review and Discussion Period | ≥ 30 days             | Proposals are publicly discussed and evaluated. The Administrator or its delegate reviews submissions for eligibility and publishes a final list of qualified proposals. |
| Registration Period          | ≥ 10 days             | Coinholders register their balances for voting by creating eligible Orchard notes within a defined block range (as described in Section 4.1). |
| Coinholder Vote on Proposals | ~ 2 weeks             | Coinholders vote on eligible proposals using the process defined in Section 4. The Administrator or its delegate verifies and tallies the results. |
| Vote Tallying                | After voting concludes | The Administrator or its delegate tallies all votes. For shielded voting, tallying is performed using the Coin Voting 2.0 Audit Tool [7] to aggregate verified ballots submitted to the voting chain. For transparent voting, tallying is performed by verifying signed messages and corresponding transparent payments received at the published Orchard address using the IVK. Shielded and transparent results are combined into a unified tally prior to publication. |
| Funding Disbursements        | —                     | After final tallies are published, the Administrator or its delegate coordinates with Key-Holder Organizations to execute approved payments from the multisig wallet. |

---

## Security Precautions

Key-Holder Organizations MUST maintain custody according to the NU6.1 funding specification and ZIP 1016.

Any theft or compromise of funds or key material MUST be reported promptly after mitigation.

## References

[1] BCP 14 – Key words for use in RFCs to Indicate Requirement Levels:  
https://www.rfc-editor.org/info/bcp14

[2] ZIP 1016 – Community and Coinholder Funding Model:  
https://zips.z.cash/zip-1016

[3] ZIP 1015 – Block Subsidy Allocation for Non-Direct Development Funding:  
https://zips.z.cash/zip-1015

[4] ZIP 271 – Deferred Dev Fund Lockbox Disbursement:  
https://zips.z.cash/zip-0271

[5] Coin Voting 2.0 Application (zcash-vote-app):  
https://github.com/hhanh00/zcash-vote-app

[6] Coin Voting 2.0 Technical Documentation (Audit Book):  
https://hhanh00.github.io/coin-voting-book/

[7] Coin Voting 2.0 Audit Tool:  
https://github.com/hhanh00/zcash-vote-audit
