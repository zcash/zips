    ZIP: XXX
    Title: On-chain Accountable Voting
    Owners: Daira-Emma Hopwood <daira@jacaranda.org>
    Status: Draft
    Credits: Josh Swihart
             Kris Nuttycombe
             Jack Grigg
    Category: Consensus / Process
    Created: 2025-02-21
    License: MIT
    Pull-Request: <https://github.com/zcash/zips/pull/???>


# Terminology

The key words "MUST", "REQUIRED", "MUST NOT", "SHOULD", and "MAY" in this document are to be interpreted as described in BCP 14 [^BCP14] when, and only when, they appear in all capitals.

The terms "Mainnet" and "Testnet" in this document are to be interpreted as defined in the Zcash protocol specification [^protocol-networks].

TODO: Consider defining "Proposal", "Decision", "Approval", "Rejection", etc.


# Abstract

This proposal specifies a mechanism for on-chain accountable voting that is available for use by Zcash governance and funding proposals.


# Motivation

Several proposals that have been made for the future of Zcash governance, including the Zcash Governance Bloc [^draft-ecc-zbloc] and Loan-Directed Retroactive Grants [^forum-loan-directed-retroactive-grants], require similar mechanisms. In particular they require some form of on-chain accountable voting.

The details of these mechanisms matter for security and robust oversight. Separating the concerns of governance and funding policy on the one hand, and the mechanisms used to enact this policy on the other, frees initial policy proposals (and proposers) from having to specify unnecessary detail, while ensuring that implementability and security concerns are nonetheless thoroughly considered.

Using a shared vocabulary and repertoire of implementation mechanisms can also facilitate comparison of governance and funding proposals, by focussing attention on their higher-level differences.

It is possible that these mechanisms may also have wider usefulness in the Zcash ecosystem beyond governance and development funding.


# Requirements

* This specification should avoid, as far as possible, over-constraining how decisions about governance and funding are made, if and when they use this mechanism.
* The mechanism is resistant to compromise of some of the parties' keys, up to a given threshold.
* No single party's non-cooperation or loss of keys is able to cause further decisions to be blocked indefinitely.


# Non-requirements

The on-chain accountable voting mechanism does not need to directly support coinholder voting. If that is required, it should be performed via a separate protocol. The results of that protocol might then feed into votes cast in on-chain accountable voting, as suggested by the Zcash Governance Bloc [^draft-ecc-zbloc] proposal, for example.


# Specification

A Proposal to be decided using On-chain Accountable Voting is represented as a Proposal Transaction, which references a human-readable Description of what is to happen on its Approval. The Proposal Transaction MAY also lock up funds that are to be granted on Approval [TODO].

The scope of possible Proposals is left to be specified by the high-level policy that uses this mechanism.

A Decision is represented by spending the Approval Output or Rejection Output of the Proposal, as described in [Decisions]. This can signal either an Approval, recording the fact that the Approval Threshold has been met, or a Rejection, recording the fact that sufficient voting units have been cast against the Proposal that its Approval Threshold *cannot* be met.

More concretely, if there are $V$ voting units overall and $A = \mathsf{ceiling}(V \cdot \mathsf{threshold})$ of them are required for approval, then $V - A + 1$ voting units suffice for Rejection.

A Proposal also has a Deadline Height. It is Implicitly Rejected if no Approval or Rejection occurs on the consensus chain *at or before* the Deadline Height (that is, the Deadline Height is inclusive).

Honestly constructed Proposals SHOULD take into account any planned change in the block target spacing when setting the Deadline Height (see [Block Target Spacing changes]).

## Proposal Transactions

A transaction is considered to be a Proposal Transaction if and only if it includes exactly one Specification Output, exactly one Approval Output, and exactly one Rejection Output, as specified below.

### Description Output

A Proposal Transaction MUST reference a human-readable Description of what is being voted on. This is represented by a Description Output encrypted to the zero $\mathsf{ovk}$, in the same way as for shielded coinbase transactions [^zip-0213]. The plaintext memo of the Description Output MUST use the following format:

* the string $\texttt{“b2-256:”}$
* a hex-encoded BLAKE2b-256 hash of the contents of the file specifying the proposal
* the string $\texttt{“:”}$
* a stable URL to the contents of that file.

The URL MUST be encoded as US-ASCII, but MAY use %-encoding to specify UTF-8 characters as described in [^uri-utf8].

For example, to refer to the contents of ZIP 1015 at time of writing:

    "b2-256:bacb0d5430968e4ce77246523d0e6f29c442f8fce0f3656462fdf5a5c4b8c656:" ||
    "https://raw.githubusercontent.com/zcash/zips/38e4501a2c3bf90f6057872db497295a0a76eb35/zips/zip-1015.rst"

Since a memo field can be a maximum of 512 bytes, this currently allows a maximum of 440 bytes for the URL, which should be enough. If and when memo bundles [^zip-0231] are supported, this will increase the allowed size, and potentially allow the text of the proposal to be encoded directly in the memo.

The contents of the file at the given URL MUST NOT be automatically downloaded unless that is requested by an explicit user action.

## Approval and Rejection Outputs

Let DeadlineHeight be the last block height at which a Decision can be made for this Proposal.

An Approval Output is a P2SH output with a script of the following form:

* TBD

A Rejection Output is a P2SH output with a script of the following form:

* TBD

## Decisions

Approval of a Proposal Transaction is signalled by spending its Approval Output in a transaction mined at or before the Deadline Height.

Rejection of a Proposal Transaction is signalled by spending its Rejection Output in a transaction mined at or before the Deadline Height.

A spend of an Approval or Rejection Output that occurs in a transaction mined strictly after the Proposal's Deadline Height has no effect.

A spend of an Approval or Rejection Output is performative [^wikipedia-performative-utterance] in the sense that, even if it does not directly transfer funds, it records that the decision has been made.

A holder of voting units SHOULD NOT sign transactions that spend both the Approval Output and the Rejection Output of a given Proposal Transaction. However, if this does occur, then it is interpreted as follows:

* If Approval and Rejection occur in the same transaction, then the proposal is rejected.
* Otherwise, the outcome is determined by which of the Approval and Rejection outputs is spent first (i.e. in the earlier transaction).

As stated earlier, a Proposal is Implicitly Rejected if no Approval or Rejection occurs on the consensus chain at or before the Deadline Height.

### Finality of Decisions

Zcash's current consensus layer provides only eventual consistency. A Decision SHOULD be considered "final" when it has 100 confirmations. (In the case where the Decision transaction also directly transfers funds to a recipient, this does not constrain the recipient's ability to spend the funds.)

An Implicit Rejection SHOULD be considered final if a transaction in a block at the Deadline Height would have 100 confirmations.

If and when a mechanism for "assured finality" [^tfl-book-assured-finality] of transactions is adopted by the Zcash network, it is expected to be possible to redefine "finality" of Decisions accordingly.

## Testnet-specific considerations

Proposal Transactions on Testnet MUST only be used to test this mechanism, and have no significance for Zcash governance.


# Rationale

## Block Target Spacing changes

The block target spacing of the Zcash network is currently 75 seconds, but is not necessarily fixed. For example, the current value was established at activation of the Blossom network upgrade, halving the previous value of 150 seconds. This potentially has implications for the use of block heights to specify deadlines, but in practice we believe that block heights will suffice:

* If the block target spacing decreases, then this can only bring a deadline closer. This is not a problem because the Proposal can always be resubmitted if it expires sooner than intended.
* Changes that increase the block target spacing are usually signalled well in advance. It is therefore very unlikely that a deadline will unintentionally be extended. In any case, it is always possible to explicitly Reject any proposal for which the deadline is unintentionally extended.


# Reference implementation

TBD


# Acknowledgements

Thank you to Josh Swihart and Kris Nuttycombe for discussions about [^draft-ecc-zbloc] and [^zip-1016] that led to the idea for this ZIP.


# References

[^BCP14]: [Information on BCP 14 — "RFC 2119: Key words for use in RFCs to Indicate Requirement Levels" and "RFC 8174: Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words"](https://www.rfc-editor.org/info/bcp14)

[^protocol]: [Zcash Protocol Specification, Version 2024.5.1 or later](protocol/protocol.pdf)

[^protocol-networks]: [Zcash Protocol Specification, Version 2024.5.1. Section 3.12: Mainnet and Testnet](protocol/protocol.pdf#networks)

[^zip-0213]: [ZIP 213: Shielded Coinbase](zip-0213.rst)

[^zip-0231]: [ZIP 231: Memo Bundles](zip-0231.rst)

[^draft-ecc-zbloc]: [draft-ecc-zbloc: Zcash Governance Bloc](draft-ecc-zbloc.md)

[^zip-1016]: [ZIP 1016: Community and Coinholder Funding Model](zip-1016.md)

[^forum-loan-directed-retroactive-grants]: [Zcash forum: Loan-Directed Retroactive Grants](https://forum.zcashcommunity.com/t/loan-directed-retroactive-grants/48230)

[^tfl-book-assured-finality]: [Zcash Trailing Finality Layer. Section 2: Terminology — Assured Finality](https://electric-coin-company.github.io/tfl-book/terminology.html#definition-assured-finality)

[^uri-utf8]: [RFC 3986: Uniform Resource Identifier (URI). Section 2.5: Identifying Data](https://www.rfc-editor.org/rfc/rfc3986.html#section-2.5)

[^wikipedia-performative-utterance]: [Wikipedia: Performative utterance](https://en.wikipedia.org/wiki/Performative_utterance)
