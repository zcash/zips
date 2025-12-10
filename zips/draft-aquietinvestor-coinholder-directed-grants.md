    ZIP: Unassigned
    Title: Coinholder-Directed Retroactive Grants Program
    Owners: Jason McGee <jason@shieldedlabs.net>
            Mark Henderson <mark@shieldedlabs.net>
    Credits: Alex Bornstein
             Josh Swihart
             outgoing.doze
             Jack Grigg
             Daira-Emma Hopwood
             Kris Nuttycombe
    Status: Draft
    Category: Process / Standards
    Created: 2025-10-14
    License: MIT
    Pull Request: <https://github.com/zcash/zips/pull/1112>


# Terminology

The key words "MUST", "SHALL", "MUST NOT", "SHOULD", and "MAY" in this document
are to be interpreted as described in BCP 14 [^BCP14] when, and only when, they
appear in all capitals.

The character § is used when referring to sections of the Zcash Protocol
Specification. [^protocol]

The terms “Mainnet” and “Testnet” are to be interpreted as described in
§ 3.12 ‘Mainnet and Testnet’. [^protocol-networks]

The terms “Electric Coin Company”, “Bootstrap Project”, and “Zcash Foundation”
in this document are to be interpreted as described in ZIP 1014 [^zip-1014].

The terms “Zcash Community Grants” and “Deferred Dev Fund Lockbox” in this
document are to be interpreted as defined in ZIP 1015 [^zip-1015].

The terms “Key-Holder Organizations” and “Shielded Labs” in this document are to
be interpreted as defined in ZIP 1016 [^zip-1016].

“Coinholder Grants Program” refers to the 12% funding stream and multisig-controlled treasury defined in ZIP 1016.

“Retroactive Grants Program” refers to the operational process defined in this ZIP.

“Administrator” refers to an organization to be designated prior to activation of this ZIP, which SHALL administer the Coinholder Grants Program.

“Voting Authorities” are operators of the BFT voting chain used to collect shielded ballots.

“Incoming Viewing Key (IVK)” and “Full Viewing Key (FVK)” have the meanings used in the Orchard protocol. The IVK reveals incoming transaction values and memo data, but does not reveal any information about when outputs are spent.

“ZEC” refers to the native currency of Zcash on Mainnet.

“Cycle” refers to a single iteration of the quarterly process of grant submission,
voting, and grant disbursement.


# Abstract

This ZIP defines how the Coinholder Grants Program established in ZIP 1016 [^zip-1016] operates. It specifies a retroactive funding model, Administrator responsibilities, shielded and transparent voting procedures, participation thresholds, funding prioritization, partial funding, and payment execution by Key-Holder Organizations.


# Motivation

ZIP 1015 [^zip-1015] introduced a temporary, non-direct funding model that directed 12% of block rewards to a protocol lockbox and 8% to Zcash Community Grants.

ZIP 1016 extends this by defining the Community and Coinholder Funding Model, allocating 12% of block rewards to a Coinholder Grants Program and 8% to Zcash Community Grants through Zcash’s third halving.

While ZIP 1016 establishes a funding stream for coinholder-directed grants, it does not define how proposals are submitted, reviewed, voted, prioritized, or paid. This ZIP provides that missing operational process so that the Coinholder Grants Program can function as intended.


# Privacy Implications

TBD


# Requirements

The design of this ZIP is constrained to align with the coinholder decision-making mechanisms established in ZIP 1016.

The process described in this ZIP should describe how proposals are submitted, how voting is performed, how voting outcomes are determined, and how disbursements are made.

The roles of the Administrator, Key-Holder Organizations, Voting Authorities, and coinholders are expected to be clearly defined and distinguishable.

This ZIP should describe Key-Holder responsibilities for custody, security, and legal compliance in a clear and understandable manner.

The design is constrained to remain compatible with ZIP 1016 and with the NU 6.1 funding specification that governs key custody.

The process described in this ZIP is intended to operate on a quarterly cycle, with recurring rounds for proposal submission, review, voting, and disbursement.

This ZIP should not modify other Zcash funding programs or governance structures.

This ZIP must not require any changes to Zcash consensus.


# Specification

## Program Structure and Custody

The Coinholder Grants Program SHALL be administered by an organization to be designated prior to activation, referred to as the Administrator.

Key-Holder Organizations MUST execute disbursements according to ZIP 1016’s disbursment process [^zip-1016-disbursement-process] when grant proposals are approved by the process described in this ZIP.

The Coinholder Grants Program MUST fund only grants for work that is already completed and has been publicly verified. Such a grant for completed work is referred to as a "retroactive grant".

The Administrator MUST maintain publicly accessible resources including program rules, submission formats, timelines, voting instructions, and historical reports.

## Administrator Duties

The Administrator MUST operate the proposal submission workflow, perform eligibility screening, and publish qualified proposals.

The Administrator MUST provide written guidance on voting processes, including registration windows, voting mechanics, ballot formats, deadlines, and audit instructions.

The Administrator MUST publish proposal lists, voting parameters, tallies, participation metrics, and disbursement results for each cycle.

The Administrator MUST retain records sufficient to reproduce vote tallies and payment reports.

The Administrator MAY appoint a delegate to assist with executing any part of the quarterly process, including proposal administration, voting logistics, tally verification, and reporting.

## KYC and Compliance

The Administrator MUST perform KYC verification for any grant exceeding 50,000 USD (or ZEC equivalent at disbursement) prior to payment.

The Administrator MUST comply with applicable legal, tax, and reporting requirements.

## Voting Methods

Two voting methods are supported: shielded voting and transparent voting.

### Shielded Voting

Coinholders should vote using the dedicated Coin Voting 2.0 [^zcash-vote-app] application, which uses Orchard addresses and the Halo2 proof system to verify balances and prevent double voting [^zcash-vote-doc]. In the future, the coin voting process should be rigorously specified, at which point any application that correctly implements that specification may be used to vote.

#### Collecting Votes

The shielded voting protocol has a registration window corresponding to a defined block range. Eligibility is determined by Orchard notes created within this block range.

The Administrator MUST choose a registration window of at least 10 days.

The Administrator MUST publish voting guidance to coinholders. This guidance SHOULD include advising participants to move funds out of any wallet used for voting before entering a seed phrase into the Coin Voting 2.0 application, in order to reduce risk if the third-party application is compromised.

Votes MUST be submitted to a BFT voting chain operated by at least four independent Voting Authorities. The rationale for this threshold is that if at least two thirds of Voting Authorities are honest, vote suppression or manipulation becomes infeasible.

#### Counting Votes

The Administrator MUST collect and publish finalized tallies.

TBD: specify how shielded voting is counted.

#### Vote Auditing

Independent auditors MAY verify the results using the published election data.

TBD: specify how shielded voting is audited.

### Transparent Voting


#### Signing protocol

The signing protocol used for transparent voting is the "legacy address signatures" signature scheme implemented by Satoshi in Bitcoin Core. We specify it here in the absence of a formal specification anywhere else.

Let $\mathsf{SerializeString}(s) = \mathsf{WriteCompactSize}(\mathsf{length}(s)) \,||\, s$

Let $\mathsf{MessageHash}(\mathsf{msg}) = \textsf{SHA-256}(\textsf{SHA-256}(\mathsf{SerializeString}(\texttt{“Zcash Signed Message:”} \,||\, [\mathtt{0x0A}]) \,||\, \mathsf{SerializeString}(\mathsf{msg})))$

Let $\mathsf{Base64Encode}$ denote Base 64 Encoding as specified in [^base64], i.e. with the standard alphabet and '=' padding.

$\mathsf{LegacySignMessage}(\mathsf{msg}, \mathsf{addr})$ is the following algorithm:
- Let $\mathsf{msg}$ be the message to be signed, encoded as US-ASCII.
- Let $\mathsf{addr}$ be a transparent P2PKH address.
- Fetch the secp256k1 public key $\mathsf{pk}$ corresponding to $\mathsf{addr}$. (The wallet controlling $\mathsf{addr}$ should be tracking sufficient information to trivially derive it.)
- Fetch the secp256k1 private key $\mathsf{sk}$ corresponding to $\mathsf{pk}$.
- Let $\mathsf{msg\_hash} = \mathsf{MessageHash}(\mathsf{msg})$
- Let $\mathsf{sig} = \mathsf{secp256k1\_ecdsa\_sign\_recoverable}(\mathsf{msg\_hash}, \mathsf{sk}, \mathsf{secp256k1\_nonce\_function\_rfc6979})$
- Let $(\mathsf{recid}, \mathsf{sig\_bytes}) = \mathsf{secp256k1\_ecdsa\_recoverable\_signature\_serialize\_compact}(\mathsf{sig})$
- Verify that $\mathsf{recid}$ is set appropriately (TODO: be more precise).
- Return $\mathsf{Base64Encode}([27 + \mathsf{recid} + (\mathsf{pk.is\_compressed} \;?\; 4 : 0)] \,||\, \mathsf{sig\_bytes})$
   - (TODO: try and find where this encoding comes from, and reference it. SEC-1 perhaps? IEEE Std 1363-2000? This is a 3-bit flag added to $27 = \mathtt{0b11011}$)

$\mathsf{LegacyVerifyMessage}(\mathsf{msg}, \mathsf{addr}, \mathsf{signature})$ is the following algorithm:
- Let $\mathsf{msg}$ be the message to be verified, encoded as US-ASCII.
- Let $\mathsf{addr}$ be a transparent P2PKH address.
- If the signature is not a strictly valid Base 64 Encoding, fail verification; otherwise let $\mathsf{sig\_bytes} = \mathsf{Base64Decode}(\mathsf{signature})$.
- Check that $\mathsf{length}(\mathsf{sig\_bytes}) = 65$, otherwise fail verification.
- Let $\mathsf{msg\_hash} = \mathsf{MessageHash}(\mathsf{msg})$
- Let $\mathsf{recid} = (\mathsf{sig\_bytes}[0] - 27) \;\&\; \mathtt{0b011}$
- Let $\mathsf{pk\_is\_compressed} = ((\mathsf{sig\_bytes}[0] - 27) \;\&\; \mathtt{0b100}) \neq 0$
- Let $\mathsf{sig} = \mathsf{secp256k1\_ecdsa\_recoverable\_signature\_parse\_compact}(\mathsf{sig\_bytes}[1..], \mathsf{recid})$, and fail verification if this errors.
- Let $\mathsf{raw\_pk} = \mathsf{secp256k1\_ecdsa\_recover}(\mathsf{msg\_hash}, \mathsf{sig})$, and fail verification if this errors.
- Let $\mathsf{pk} = \mathsf{secp256k1\_ec\_pubkey\_serialize}(\mathsf{raw\_pk}, \mathsf{pk\_is\_compressed})$
- Pass verification if $\mathsf{addr}$ is the transparent P2PKH address encoding of $\textsf{RIPEMD-160}(\textsf{SHA-256}(\mathsf{pk}))$ as defined in [^protocol-transparentaddrencoding], otherwise fail verification.

#### Collecting Votes

Before accepting votes, the Administrator MUST publish an Orchard-only IVK designated for receiving vote messages and payments. The corresponding FVK MUST NOT be published.

To create a transparent vote, Voters do the following:

- Select a transparent P2PKH address $\mathsf{addr}$ to use for voting.
- Ensure that $\mathsf{addr}$ contains the intended balance of funds as of the end of the registration window.
- Construct a US-ASCII-encoded voting message $\mathsf{msg}$, using the template provided by the Administrator. It MUST NOT be longer than $387$ bytes.
- Let $\mathsf{sig} = \mathsf{LegacySignMessage}(\mathsf{msg}, \mathsf{addr})$. This can be produced via the `zcashd` `signmessage` RPC call, or using a Trezor device following the procedure described in [^trezor-sign-and-verify].
- Construct a vote-casting text $\mathsf{memo} = \mathsf{msg} \,||\, [\mathtt{0x0A}] \,||\, \mathsf{addr} \,||\, [\mathtt{0x0A}] || \mathsf{sig}$
   - Previously this was ambiguous as to how many LF characters (or other whitespace) separated the fields, or whether additional LF characters were allowed.
- Send $\mathsf{memo}$ along with a payment of at least 1 ZEC to the address associated with the published IVK.

TBD: finish the specification, including but not limited to:
- The address derivation to be used.
- The structure of transaction to be created (what kinds of outputs, how many, to what recipients, with what values).

#### Counting Votes

TBD: specify how transparent votes are counted.

The Administrator MUST ignore submissions:

- with a payment threshold chosen by the Administrator.
- where the Voter moves the submitted funds before voting concludes, as specified in the Quarterly Timeline below.

TBD: clarify specification of "voting concludes"; if you mean "at the end of the Coinholder Vote on Proposals phase" then say this instead of relying on the indirect definition.

#### Vote Auditing

The Administrator MUST publish IVK-based audit data and all received vote messages in order to allow verification.

TBD: specify how transparent votes are verified.

## Voting Process

The Administrator MUST publish relevant parameters for each voting method for each cycle, and provide sufficient information for independent auditing.

TBD: specify the rest of the overall voting process.

## Participation and Voting Thresholds

A proposal MUST have at least 420,000 ZEC participating to be eligible for approval, as specifed in ZIP 1016. [^zip-1016]

A proposal is approved if a simple majority of participating votes are “Yes”.

Each proposal vote is independent, and coins MAY be reused across proposals in the same cycle.

## Proposal Funding and Disbursement

After votes are complete, the Administrator MUST publish final voting results within seven days. The results MUST include total participation, per-proposal tallies, and data necessary for independent auditing.

The Administrator MUST produce a ranked list of approved proposals based on the percentage of “Yes” votes.

Funds MUST be allocated starting from the highest-ranked approved proposal until the treasury is exhausted.

If insufficient funds remain to fully fund the next approved proposal, the Key-Holder Organizations MAY partially fund it up to the remaining balance.

Approved proposals not funded or partially funded MAY be resubmitted in future quarters.

Key-Holder Organizations MUST execute payments using the NU 6.1 multisignature scheme and MUST publish transaction identifiers.

The Administrator MUST publish a disbursement report detailing allocated amounts, partial disbursements, and executed transactions.

## Quarterly Timeline

| Phase                        | Approximate Duration  | Description |
|------------------------------|-----------------------|-------------|
| Public Call for Proposals    | ~ 1 month             | The Administrator or its delegate announces an open call via community channels. Applicants prepare and submit completed-work proposals for consideration. |
| Review and Discussion Period | ≥ 30 days             | Proposals are publicly discussed and evaluated. The Administrator or its delegate reviews submissions for eligibility and publishes a final list of qualified proposals. |
| Registration Period          | ≥ 10 days             | Coinholders register their balances for voting by creating eligible Orchard notes within a defined block range (as described in Section 4.1). |
| Coinholder Vote on Proposals | ~ 2 weeks             | Coinholders vote on eligible proposals using the process defined in Section 4. The Administrator or its delegate verifies and tallies the results. |
| Vote Tallying                | After voting concludes | The Administrator or its delegate tallies all votes. For shielded voting, tallying is performed using the Coin Voting 2.0 Audit Tool [^zcash-vote-audit] to aggregate verified ballots submitted to the voting chain. For transparent voting, tallying is performed by verifying signed messages and corresponding transparent payments received at the published Orchard address using the IVK. Shielded and transparent results are combined into a unified tally prior to publication. |
| Funding Disbursements        | —                     | After final tallies are published, the Administrator or its delegate coordinates with Key-Holder Organizations to execute approved payments from the multisig wallet. |

## Security Precautions

Key-Holder Organizations MUST maintain custody according to the ZIP 271 funding specification and ZIP 1016.

Any theft or compromise of funds or key material MUST be reported promptly after mitigation.


# Rationale

TBD: add missing rationale for:
- Why the transparent voting FVK must not be published.
- The requirement for, and bound on, the payment amount for transparent voting.
- The requirement that transparent voters not move their funds until voting concludes.


# Historic Context: How the transparent voting process was run in the last vote

Every election, Jason posts something like this:

>Transparent ZEC
>
> If you want to vote ZEC held in a transparent address, follow the instructions and example outlined by @outgoing.doze:
>
>> To protect the anonymity of wallet holders, I suggest votes (signed messages) are sent to a shielded wallet where the viewing key is shared with the community so anyone can review the votes. The character limit being 512 if not mistaken, should be plenty. The format could be as simple as this:
>>
>>     $voteDetails
>>
>>     $address
>>
>>     $signature
>>
>> The extra line in between will make it easier easier to review visually.
>>
>> Example (ignore invalid signature):
>>
>>     1A; 2E Let’s make more Zcash Swag; 3Y
>>
>>     t1VydNnkjBzfL1iAMyUbwGKJAF7PgvuCfMY
>>
>>     ICrKSQjLORZP/aUTluyf2sZXXK+HuKtxdBLt2RRCn2j5CxgZlccNmiMC2K104JuhHnvHd5cXgSzdZtGh9vgWAYA=
>>
>> To protect from a Sybil attack, I suggest a payment of 0.1 ZEC is sent along with the vote. Anything less than 0.1 ZEC would therefore be ignored.
>>
>> The wallet would be generated and controlled by a trusted member of the community, same person that would share the viewing key with the community.
>
> Orchard Address:
>     ADDRESS
>
> View Key:
>     VK
>
> Birthday Height:
>     HEIGHT
>
> Note: Funds cannot be moved during the voting period, which runs until Tuesday, November 25, at 11:59 PM UTC.

Jason then pulled up the transparent address received in each voting message on a block explorer (Blockchair) and looked at when the last activity was. If there was no activity since the defined registration window ended, then the vote was accepted, and he trusted that the balance in the address (as reported by the block explorer) was the voting amount corresponding to the received message.

dismad verified signatures in zcashd with:

> zcash-cli verifymessage "t1VydNnkjBzfL1iAMyUbwGKJAF7PgvuCfMY" "IGobRVUtwsL92th70UFj0bGztv701evq/uHVuoTTceWsRjWeasSdvMkNUR43gSpMo393yixoFMiTQqnYh3y0b5U=" "Q1:N; Q2:N; Q3:Y (20250903)" true

and in Trezor following the instructions in [^trezor-sign-and-verify].

# References

[^BCP14]: [Information on BCP 14 — "RFC 2119: Key words for use in RFCs to Indicate Requirement Levels" and "RFC 8174: Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words"](https://www.rfc-editor.org/info/bcp14)

[^base64]: [RFC 4658: The Base16, Base32, and Base64 Data Encodings. Section 4: Base 64 Encoding](https://www.rfc-editor.org/rfc/rfc4648.html#section-4)

[^protocol]: [Zcash Protocol Specification, Version 2025.6.1 [NU 6.1] or later](protocol/protocol.pdf)

[^protocol-networks]: [Zcash Protocol Specification, Version 2025.6.1 [NU 6.1]. Section 3.12: Mainnet and Testnet](protocol/protocol.pdf#networks)

[^protocol-transparentaddrencoding]: [Zcash Protocol Specification, Version 2025.6.1 [NU 6.1]. Section 5.6.1.1: Transparent Addresses](protocol/protocol.pdf#transparentaddrencoding)

[^zip-0271]: [ZIP 271: Deferred Dev Fund Lockbox Disbursement](zip-0271.md)

[^zip-1014]: [ZIP 1014: Establishing a Dev Fund for ECC, ZF, and Major Grants](zip-1014.rst)

[^zip-1015]: [ZIP 1015: Block Subsidy Allocation for Non-Direct Development Funding](zip-1015.rst)

[^zip-1016]: [ZIP 1016: Community and Coinholder Funding Model](zip-1016.md)

[^zip-1016-disbursement-process]: [ZIP 1016: Community and Coinholder Funding Model — Disbursement Process](zip-1016.md#disbursementprocess)

[^zcash-vote-app]: [Coin Voting 2.0 Application (zcash-vote-app)](https://github.com/hhanh00/zcash-vote-app)

[^zcash-vote-doc]: [Coin Voting 2.0 Technical Documentation (Audit Book)](https://hhanh00.github.io/coin-voting-book/)

[^zcash-vote-audit]: [Coin Voting 2.0 Audit Tool](https://github.com/hhanh00/zcash-vote-audit)

[^trezor-sign-and-verify]: [Trezor documentation: Sign & Verify messages in Trezor Suite](https://trezor.io/learn/supported-assets/bitcoin/sign-and-verify-messages-trezor-suite)
