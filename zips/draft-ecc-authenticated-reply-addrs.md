    ZIP: ???
    Title: Authenticated Reply Addresses
    Owners: Jack Grigg <thestr4d@gmail.com>
            Kris Nuttycombe <kris@nutty.land>
            Daira-Emma Hopwood <daira@jacaranda.org>
    Status: Draft
    Category: Standards / Wallet
    Created: 2023-11-12
    License: MIT
    Discussions-To: <https://github.com/zcash/zips/issues/???>
    Pull-Request: <https://github.com/zcash/zips/pull/???>


# Terminology

The key words "MUST" and "SHOULD" in this document is to be interpreted as described in
BCP 14 [#BCP14] when, and only when, they appear in all capitals.


# Abstract

TODO


# Motivation

TODO


# Specification

## Authenticated reply address encoding

- Versioning (which could instead be represented by the ZIP 302 TLV type).
- The reply address.
    - This uses a binary encoding of a ZIP 316 Unified Address.
        - TODO: decide on specifics - https://github.com/zcash/librustzcash/pull/711#issuecomment-1377783264
    - This might be the same address for all inputs, or it might only cover a subset of them
      (in a collaborative multi-sender transaction).
- A non-empty list of tuples:
    - $\mathsf{receiver_type}$: The receiver type for which this proof is made. This receiver
      MUST match one of the receiver types in the reply address.
    - $\mathsf{addr_proof}_\mathsf{pool_type}$: An address proof for that pool type.

## Creating

## Verifying

- Verify that the transaction is valid (in particular, that all proofs and signatures are valid).
- Decrypt the transaction output to obtain the memo field.
- Decode the authenticated reply address.
    - This MUST validate the inner encodings of e.g. ZIP 316 for UAs (as applicable).
- Verify each address proof.

## Sapling address proof

### Encoding

- $\mathsf{index}$: An index into $\mathsf{tx.shieldedSpends}$.
- $\mathsf{nullifier_{addr}}$: A nullifier for a ZIP 304 fake note. [#zip-0304]
- $\mathsf{zkproof_{addr}}$: A Sapling spend proof.

### Creating

Taking as input:
- The Sapling expanded spending key.
- $\alpha$: The randomness used to construct the spend description.
- $\mathsf{index}$: An index into $\mathsf{tx.shieldedSpends}$.

The Sapling address proof is created as follows:

- Extract the Sapling receiver from the reply address.
- Compute $(\mathsf{nf}, zkproof) = Zip304CreateProof(sapling_receiver, expanded_sk, alpha)$.
- Return $(\mathsf{index}, \mathsf{nf}, zkproof)$

### Verifying

- Extract the Sapling receiver from the reply address.
- Look up the spend description at $\mathsf{tx.shieldedSpends}[\mathsf{index}]$.
- Extract $\mathsf{rk}$ from the spend description.
- Call $Zip304VerifyProof(sapling_receiver, \mathsf{nullifier_{addr}}, \mathsf{rk}, \mathsf{zkproof_{addr}})$, and return an error if it fails.

# Rationale

We do not generate and include a full ZIP 304 signature in the Sapling address proof; we
only rely on its proof-of-address helper function. This is for two reasons:
- The ZIP 304 `spendAuthSig` proves knowledge of the spend authorizing key, but we already
  obtain that from the `spendAuthSig` on the Sapling spend description, so there is no
  additional security benefit from including it, and omitting it decreases the encoding
  size.
- We do not need to encode `rk` because it is already present in the transaction.

The individual address proofs commit to the entire reply address. For example, if the
reply address contains a Sapling and Orchard receiver, but the transaction only spends
Sapling notes, the sender is still confirming that the Orchard receiver is also an allowed
reply address receiver.

However, to have proper cross-linking, we need to ensure that all receivers in the UA have
proofs of spend authority, to prevent a sender from including a receiver that they do not
control (as a form of impersonation attack). There are a few ways this could be resolved:
- Always require the transaction to spend notes for all receivers.
    - Pro: This could be done with dummy notes for the pools that the sender doesn't want to
      spend from.
    - Con: This would prevent the sender from pre-emptively adding receivers for upcoming
      shielded pools that are not yet activated.
    - Con: For UAs with transparent receivers, this would be incompatible with shielded-only
      transactions.
- Have an optional proof of spend authority in the address proof.
    - This is omitted when a spent note is present for that receiver type (as the spent note
      serves this purpose).
    - This is pretty much the exact opposite of ZIP 311 (where we require proofs of spend
      authority, and have optional proof-of-address).

In any case, doing this for UAs that include Orchard receivers will result in more data
than can be stored in a single memo field, so this is blocked on some kind of multi-part
memo encoding.


# Security and Privacy Considerations

The verification process for authenticated reply addresses requires that the full
transaction is validated, because it outsources proof-of-spend-authority to the spend
proofs and signatures. As a consequence, wallets that scan transactions via a light client
protocol MUST NOT show the reply address as authenticated until the full transaction has
been downloaded and validated.

# Reference implementation

TBD


# References

[#BCP14]: Information on BCP 14 — "RFC 2119: Key words for use in RFCs to Indicate Requirement Levels" and "RFC 8174: Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words" <https://www.rfc-editor.org/info/bcp14>
