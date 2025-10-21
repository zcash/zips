# ZIP XXXX: Coinholder-Directed Retroactive Grants Program

**Owners:** Jason McGee <jason@shieldedlabs.net>  
**Credits:** Alex Bornstein  
            Josh Swihart  
**Status:** Proposed  
**Category:** Process  
**Created:** 2025-10-14  
**License:** MIT  
**Pull-Request:** *TBD*  

---

## Terminology

The key words “MUST”, “SHOULD”, and “MAY” in this document are to be interpreted as described in BCP 14 when, and only when, they appear in all capitals.  

The terms “Mainnet”, “Testnet”, “Electric Coin Company (ECC)”, “Zcash Foundation (ZF)”, “Bootstrap Project (BP)”, “Financial Privacy Foundation (FPF)”, “Deferred Dev Fund Lockbox”, “Key-Holder Organizations”, and “Shielded Labs” are as defined in [ZIP 1016](https://zips.z.cash/zip-1016).  

**“Coinholder Grants Program”** refers to the 12% funding stream and associated multisig-controlled treasury defined in ZIP 1016.  
**“Retroactive Grants Program”** refers to the operational process described by this ZIP for disbursing coinholder-directed funding.  
**“The Administrator”** refers to an organization that administers the Coinholder Grants Program and manages proposal submission, verification, and reporting processes.  

“ZEC” refers to the native currency of Zcash on Mainnet.  

---

## Abstract

This ZIP defines the **process** for the Coinholder Grants Program established in ZIP 1016.  
It specifies that the program SHALL operate as a **retroactive grants program**, awarding funds only for work that has been completed and verified.  

The program:  
* empowers coinholders to directly approve or reject funding proposals;  
* minimizes administrative overhead by paying only for finished work; and  
* ensures transparency, accountability, and legal compliance through limited oversight by the Administrator or its delegate and Key-Holder Organizations.  

---

## Motivation

[ZIP 1015](https://zips.z.cash/zip-1015) introduced a temporary, non-direct funding model that redirected 12% of block rewards to a protocol lockbox and 8% to Zcash Community Grants (ZCG).  

[ZIP 1016](https://zips.z.cash/zip-1016) extends this by defining the **Community and Coinholder Funding Model**, allocating 12% of block rewards to a Coinholder Grants Program and 8% to ZCG through Zcash’s third halving.  

While ZIP 1016 defines the funding structure and governance boundaries, it does not prescribe an implementation process for coinholder-directed grants. This ZIP provides that missing specification.  

A **retroactive grants** model aligns with Zcash’s principles of accountability and decentralization by:  
* rewarding completed, verifiable work rather than speculative milestones;  
* reducing administrative complexity for Key-Holder Organizations;  
* enabling direct, transparent coinholder participation; and  
* ensuring that funds are only disbursed for measurable contributions that advance Zcash.  

---

## Requirements

1. **Retroactive Funding Model** — Grants MUST be awarded solely for work that is demonstrably complete and publicly verifiable.  
2. **Coinholder Voting Process** — All grants MUST be approved by a coinholder vote meeting the participation threshold defined in ZIP 1016 (≥ 420,000 ZEC voted).  
3. **Transparency and Reporting** — Proposal information, vote outcomes, and disbursements MUST be published publicly by the Administrator or its delegate.  
4. **Administrative Safeguards** — The Administrator or its delegate SHALL manage proposal submission, eligibility screening, compliance checks, and quarterly reporting, including KYC for grants > 50,000 USD equivalent.  
5. **Keyholder Oversight** — Key-Holder Organizations MUST execute approved disbursements unless vetoed under the conditions defined in ZIP 1016 (Veto Process).  
6. **Legal Compliance** — All parties MUST comply with applicable legal, tax, and reporting obligations.  
7. **Security and Custody** — Multisig keys MUST be secured per the standards in ZIP 1016.  

---

## Non-Requirements

* Changes to governance or funding mechanisms of other programs are **outside scope**.  
* This ZIP does not modify consensus parameters or introduce new Funding Streams beyond those defined in ZIP 1016.  

---

## Specification

### 1. Program Structure

The Coinholder Grants Program SHALL operate as a **retroactive funding mechanism** for the 12% Funding Stream defined in ZIP 1016.  

Funds are held in the Coinholder-Controlled Fund multisig wallet and distributed per approved proposals.  

The Administrator or its delegate is responsible for managing proposal intake, eligibility review, publication, and transparency reporting.  

Key-Holder Organizations (ECC, ZF, Shielded Labs) execute multisig disbursements upon coinholder approval, subject to veto provisions.  

---

### 2. KYC and Compliance

Grants > 50,000 USD require KYC verification of the recipient by the Administrator or its delegate prior to payment.  

The Administrator or its delegate MAY charge a reasonable administrative fee to cover these duties, subject to coinholder approval.  

---

### 3. Participation and Voting Thresholds

* Participation threshold: ≥ 420,000 ZEC voted (≈ 2% of total supply).  
* Approval criterion: simple majority of “Yes” votes.  
* Each proposal vote is independent; coins used in one vote MAY be reused in another.  

---

### 4. Voting Process

The Coinholder Grants Program supports two voting methods: **Shielded Voting** and **Transparent Voting**.  

Both MUST produce verifiable and auditable results administered by the Administrator or its delegate.  

#### 4.1 Shielded Voting Process

Shielded voting is conducted through the dedicated Coin Voting 2.0 application that uses Orchard addresses and the Halo2 proof system to verify balances and prevent double voting.  

1. **Registration Period** – The Administrator or its delegate MUST define a registration window not shorter than 10 days, specified by block heights. Only Orchard notes created or refreshed within this window are eligible for voting.  
2. **Pre-Vote Safeguards** – Participants SHOULD move funds out of the wallet used for voting *before* entering their seed phrase into the Coin Voting application to reduce risk if the third-party app is compromised.  
3. **Voting Phase** – After registration closes, eligible coinholders vote using their Orchard funds via the Coin Voting application. Each ZEC held corresponds to 1,000 vote units.  
4. **Vote Submission** – Votes are submitted to a dedicated voting blockchain operated by independent Voting Authorities running a Byzantine Fault Tolerant (BFT) consensus network (e.g., CometBFT).  
5. **Tally and Audit** – At the end of the voting period, the Administrator or its delegate collects finalized results from the Voting Authorities. Auditors MAY independently verify the tally using the public viewing key and revealed election seed.  
6. **Security Assumptions** – The system MUST include ≥ 4 Voting Authorities to ensure liveness and integrity; so long as ≥ ⅔ are honest, the vote cannot be manipulated.  

#### 4.2 Transparent Voting Process

Transparent voting MAY be used alongside shielded voting to expand participation and maintain verifiability.  

1. Voters create a signed message containing their vote choice and transparent address.  
2. The signed message and a payment of ≥ 1 ZEC MUST be sent to a designated Orchard address controlled by the Administrator or its delegate.  
3. The Administrator or its delegate publishes the corresponding viewing key so anyone can verify vote contents and tally independently.  
4. Votes with payments < 1 ZEC MUST be ignored to mitigate Sybil attacks.  
5. Funds MUST remain immobile until the voting period concludes to prevent vote tampering.  

Both methods MUST produce publicly auditable vote records and a final summary published by the Administrator or its delegate within 7 days of vote conclusion.  

---

### 5. Proposal Funding and Disbursement

Following the publication of voting results, approved proposals SHALL be funded in order of their relative voting support.  

1. **Prioritization by Vote Share** — Approved grants are ranked from highest to lowest based on the percentage of “Yes” votes received. Funding is distributed sequentially from the top of this ranking until available treasury funds for the quarter are fully allocated.  
2. **Partial Funding** — If the Coinholder Grants Program treasury cannot fully fund all approved grants within the same quarter, the remaining balance MAY be used to partially fund the next-ranked proposal. Partial funding MUST be proportional to the remaining available balance.  
3. **Deferral to Next Quarter** — Proposals that are approved but not funded in full MAY be resubmitted in the following quarter for coinholder re-approval. Partial funding in one quarter does not guarantee automatic completion in the next.  
4. **Execution by Key-Holder Organizations** — Once funding amounts are determined, the Key-Holder Organizations SHALL jointly execute payments from the Coinholder-Controlled Fund using their k-of-n multisignature scheme (as defined in ZIP 1016). All transactions MUST be approved by the required threshold of signatures and published for community transparency.  
5. **Transparency Reporting** — The Administrator or its delegate MUST publish a summary report after each cycle detailing the funds available, amounts disbursed per proposal, any partial allocations or deferrals, and the hashes of executed transactions.  

This approach ensures that coinholder preferences are respected while maintaining a clear, deterministic process for allocating limited treasury resources and executing disbursements securely through the Key-Holder Organizations.  

---

### 6. Quarterly Timeline (Example)

| Phase | Approximate Duration | Description |
|:--|:--|:--|
| **Public Call for Proposals** | ~ 1 month | The Administrator or its delegate announces an open call via community channels. Applicants prepare and submit completed-work proposals for consideration. |
| **Review and Discussion Period** | ≥ 30 days | Proposals are publicly discussed and evaluated. The Administrator or its delegate reviews submissions for eligibility and publishes a final list of qualified proposals. |
| **Registration Period** | ≥ 10 days | Coinholders register their balances for voting by creating or refreshing eligible Orchard notes within a defined block range (as described in Section 4.1). |
| **Coinholder Vote on Proposals** | ~ 2 weeks | Coinholders vote on eligible proposals using the process defined in Section 4. Results are verified and tallied by the Administrator or its delegate. |
| **Funding Disbursements** | — | After votes are verified, the Administrator or its delegate coordinates with the Key-Holder Organizations to execute approved payments from the multisig wallet per Section 5. |

This quarterly cycle repeats for the duration of the Coinholder Grants Program.  

---

### 7. Security Precautions

All multisig custodians MUST follow the same security standards and reporting requirements outlined in ZIP 1016.  

Any loss or compromise MUST be disclosed to the community immediately after mitigation.  

---

## Process

This ZIP SHALL be activated concurrently with ZIP 1016 upon the next Network Upgrade following community ratification.  

Implementation of the Coinholder Voting Mechanism is a prerequisite for operational deployment.  


---

## References

1. [ZIP 1014 – Establishing a Dev Fund for ECC, ZF, and Major Grants](https://zips.z.cash/zip-1014)  
2. [ZIP 1015 – Block Subsidy Allocation for Non-Direct Development Funding](https://zips.z.cash/zip-1015)  
3. [ZIP 1016 – Community and Coinholder Funding Model](https://zips.z.cash/zip-1016)  
4. [ZIP 207 – Funding Streams](https://zips.z.cash/zip-0207)  
5. [ZIP 2001 – Lockbox Funding Streams](https://zips.z.cash/zip-2001)  
6. [ZIP 271 – Deferred Dev Fund Lockbox Disbursement](https://zips.z.cash/zip-0271)  

---

**This ZIP defines the operational framework for the Coinholder Grants Program and may be revised through future ZIPs as the voting system matures.**
