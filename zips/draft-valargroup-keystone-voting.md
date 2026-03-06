    ZIP: Unassigned
    Title: Keystone Hardware Wallet Voting Delegation
    Owners: Dev Ojha <dojha@berkeley.edu>
            Adam Tucker <adamleetucker@outlook.com>
            Roman Akhtariev <ackhtariev@gmail.com>
            Greg Nagy <greg@dhamma.works>
    Status: Draft
    Category: Informational
    Created: 2026-03-06
    License: MIT
    Pull-Request: <https://github.com/zcash/zips/pull/???>


# Terminology

The key words "MUST", "MUST NOT", "SHOULD", and "MAY" in this document
are to be interpreted as described in BCP 14 [^BCP14] when, and only
when, they appear in all capitals.

The character § is used when referring to sections of the Zcash Protocol
Specification. [^protocol]

The terms "Vote Authority Note (VAN)", "governance nullifier", "voting
round", "governance hotkey", and "ballot" are defined in the Shielded
Voting Protocol ZIP [^voting-protocol].

The terms below are to be interpreted as follows:

Governance PCZT

: A Partially Created Zcash Transaction [^pczt] constructed solely for
  governance delegation. The PCZT contains a single Orchard Action that
  spends a dummy signed note and produces an output to the governance
  hotkey address. It is never broadcast to the Zcash mainchain.

Dummy signed note

: A synthetic Orchard note with value 0 (in the Delegation Proof
  circuit) whose $\text{ρ}$ is deterministically bound to the
  delegation context. The note does not exist in any on-chain note
  commitment tree; it is constructed exclusively to obtain a
  $\mathsf{SpendAuthSig}^{\mathsf{Orchard}}$ via the standard PCZT
  signing flow.

Rho binding

: The constraint that the dummy signed note's
  $\text{ρ}^{\mathsf{signed}}$ equals a Poseidon hash of the delegated
  note commitments, the VAN commitment, and the voting round identifier.
  This makes the spend authorization signature non-replayable and scoped
  to the exact delegation context.


# Abstract

This ZIP specifies how holders of Orchard notes who custody their
spending keys on a Keystone hardware wallet delegate voting authority
to a governance hotkey for participation in the shielded voting
protocol [^voting-protocol].

The mechanism reuses the existing Orchard PCZT signing flow without
requiring Keystone firmware changes. The wallet constructs a governance
PCZT containing a single Orchard Action: a spend of a dummy signed note
(value 0, with $\text{ρ}$ bound to the delegation context) and an
output to the governance hotkey address. The Keystone device interprets
this as a standard Orchard transaction, signs the ZIP 244 [^zip-244]
transaction identifier, and returns the signed PCZT. The wallet extracts
the $\mathsf{SpendAuthSig}^{\mathsf{Orchard}}$ and submits it alongside
the Delegation Proof to the vote chain.

Governance semantics (note ownership, nullifier non-membership, VAN
construction, and rho binding) are enforced entirely by the
zero-knowledge proof and on-chain verification, not by the hardware
wallet. The user confirms the delegation on the Keystone display, which
shows a 1-zatoshi transfer with zero fee and a memo describing the
delegation.


# Motivation

Hardware wallets such as Keystone provide strong custody guarantees by
isolating spending keys from general-purpose computing environments.
However, the shielded voting protocol [^voting-protocol] requires
constructing Halo 2 zero-knowledge proofs over private key material,
operations that hardware wallets cannot perform.

Without a delegation mechanism, hardware wallet users face two
unacceptable choices: export their spending keys to a software
environment (negating the security benefit of hardware custody) or
forgo governance participation entirely.

This ZIP specifies a third option: the hardware wallet signs once per
batch of up to 5 notes during delegation, authorizing a
software-controlled governance hotkey to perform all subsequent voting
operations. The signing reuses the standard Orchard PCZT flow that Keystone
already supports, requiring no firmware changes. The dummy signed note's
rho binding ensures the signature is scoped to the exact delegation context,
even though the device is unaware of governance semantics.


# Privacy Implications

The Keystone device observes the governance PCZT but learns no
information about the holder's real Orchard balance or the delegation
context:

- The PCZT contains a 1-zatoshi dummy note that does not correspond to
  any on-chain note. The holder's actual note commitments, values, and
  nullifiers are never transmitted to the device.
- The VAN commitment, governance nullifiers, and voting round identifier
  are embedded in the rho binding inside the ZKP circuit. They do not
  appear as plaintext fields in the PCZT.
- The output address (governance hotkey) is visible on the device. This
  address is freshly generated per voting round and is not linked to the
  holder's on-chain Orchard addresses.
- The delegation memo (e.g., "I am authorizing this hotkey managed by my
  wallet to vote on {round} with {amount} ZEC") is visible on the
  device. The memo is informational and does not enter the ZKP circuit.

An attacker with physical access to the Keystone device during signing
learns only that the holder is participating in a governance round and
the declared voting weight. The attacker cannot link the delegation to
specific on-chain notes or determine how the holder subsequently votes.


# Requirements

- The delegation signing flow MUST be compatible with existing Keystone
  firmware that supports the Orchard PCZT signing flow [^pczt], without
  requiring firmware changes specific to governance.
- The spend authorization signature MUST be non-replayable: it MUST be
  cryptographically scoped to a specific set of delegated notes, VAN
  commitment, and voting round via the rho binding.
- Real funds MUST NOT be at risk during the delegation signing. The dummy
  signed note has value 0 in the Delegation Proof circuit [^voting-protocol],
  and the governance PCZT is never broadcast to the Zcash mainchain.


# Non-requirements

- Voting-aware Keystone firmware (e.g., a governance network byte that
  allows the device to display delegation context natively) is a future
  extension and is not specified in this ZIP. See [Open issues].
- The software-only signing path (where the wallet holds the spending
  key directly and signs without a hardware wallet) is an alternative
  that does not require the PCZT construction described here. Software
  wallets follow the same Delegation Proof specification
  in [^voting-protocol] but sign the sighash directly.
- The Delegation Proof circuit itself (public inputs, auxiliary inputs,
  conditions) is specified in [^voting-protocol], not in this ZIP.


# Specification

## Overview

The delegation signing flow proceeds in five steps:

1. The wallet generates a governance hotkey on the local device.
2. The wallet constructs a dummy signed note with rho bound to the
   delegation context.
3. The wallet builds a governance PCZT containing the dummy signed note.
4. The Keystone device signs the PCZT and returns the signature.
5. The wallet extracts the signature and assembles the delegation
   submission.

Each interaction with the Keystone device delegates up to 5 Orchard
notes (the per-delegation batch size defined in [^voting-protocol]).
A holder with more than 5 notes repeats the flow for each batch of up
to 5, producing a separate VAN per batch. The holder MAY choose to
delegate fewer batches than their full note set, voting with only the
balance covered by the delegated batches.

## Governance Hotkey Generation

The governance hotkey is a separate Orchard key hierarchy generated on
a general-purpose device (e.g., a mobile phone). It is distinct from
the holder's Orchard spending key, which resides on the Keystone. The
hotkey provides the key material for all voting operations after
delegation.

The hotkey's key components and generation are defined in the Governance
Hotkey section of [^voting-protocol]. This ZIP does not further constrain
the hotkey generation method.

## Dummy Signed Note Construction

The wallet constructs a dummy Orchard note as follows:

1. **Address.** The signed note's address is derived from the holder's
   full viewing key at diversifier index 0 with external scope:
   $\mathsf{addr}^{\mathsf{signed}} = \mathsf{fvk.address\_at}(0, \mathsf{External})$.

2. **Rho binding.** The signed note's $\text{ρ}$ is set to:

$$\text{ρ}^{\mathsf{signed}} = \mathsf{Poseidon}\bigl(\mathsf{cmx}\_\mathsf{1}, \mathsf{cmx}\_\mathsf{2}, \mathsf{cmx}\_\mathsf{3}, \mathsf{cmx}\_\mathsf{4}, \mathsf{cmx}\_\mathsf{5}, \mathsf{van}, \mathsf{voting}\_{\mathsf{round}\_\mathsf{id}}\bigr)$$

   where $\mathsf{cmx}\_\mathsf{1} \ldots \mathsf{cmx}\_\mathsf{5}$ are the
   extracted note commitments of the 5 delegated note slots (real notes
   plus zero-value padding notes), $\mathsf{van}$ is the VAN commitment
   as defined in [^voting-protocol], and
   $\mathsf{voting}\_{\mathsf{round}\_\mathsf{id}}$ is the round identifier.

3. **Value.** The note value MUST be set to 1 zatoshi (0.00000001 ZEC)
   in the PCZT so that the Keystone device renders all transaction
   fields. A value of 0 causes Keystone to suppress field display,
   degrading the user experience. The Delegation Proof circuit treats the
   signed note value as 0 regardless of the PCZT value.

4. **Rseed.** A fresh random $\mathsf{rseed}$ is sampled for the note.

5. **Note construction.** The note is constructed via standard Orchard
   note construction using the address, value (1 zatoshi), rho, and
   rseed above.

For fewer than 5 real notes, the wallet pads the remaining slots with
zero-value dummy notes at diversifier indices $1000 + i$ (external
scope) from the holder's full viewing key. These padding notes enter
the rho binding via their $\mathsf{cmx}$ values but do not correspond
to real on-chain notes.

## Governance PCZT Construction

The wallet constructs a governance PCZT as a single-action Orchard
transaction:

### Spend Side

- The single spend consumes the dummy signed note constructed above.
- A dummy Merkle authentication path (all-zero siblings, position 0)
  is used. The path is not verified on-chain; spend authorization is
  established by the ZKP circuit.
- The Orchard bundle builder generates the spend authorization
  randomizer $\alpha$ and the randomized verification key
  $\mathsf{rk} = \mathsf{ak} + [\alpha]\, G$ internally.

### Output Side

- A single output of 1 zatoshi is addressed to the governance hotkey.
- The output memo SHOULD contain a human-readable delegation description:

  `"I am authorizing this hotkey managed by my wallet to vote on`
  `{round_name} with {amount}.{frac} ZEC."`

  where `{round_name}` is the voting round title and
  `{amount}.{frac}` is the holder's eligible ZEC balance.

### ZIP-32 Derivation

The spend MUST include a ZIP 32 [^zip-32] derivation path so that the
Keystone device can derive the correct spending key:

$$\mathsf{path} = [32', \mathsf{coin\_type}', \mathsf{account}']$$

where $\mathsf{coin\_type}$ is 133 for Zcash mainnet.

### Finalization

The wallet applies the PCZT Creator and IoFinalizer roles. The
IoFinalizer computes the ZIP 244 [^zip-244] transaction identifier
(sighash) that the Keystone device will sign.

## Keystone Signing Flow

The signing flow uses the standard PCZT QR-based air-gapped protocol:

1. **Redaction.** The wallet redacts the PCZT for the Signer role,
   removing fields that are not needed for signing (e.g., proof data,
   witness paths).

2. **QR encoding.** The redacted PCZT is UR-encoded [^ur] and displayed
   as an animated QR code sequence for Keystone to scan.

3. **Device signing.** The Keystone device:
   a. Parses the PCZT and extracts the ZIP-32 derivation path.
   b. Derives the spending key from its stored seed using the path.
   c. Computes the ZIP 244 sighash over the transaction structure.
   d. Produces a $\mathsf{SpendAuthSig}^{\mathsf{Orchard}}$ [^protocol-concretespendauthsig]
      signature on the sighash using the derived spending key and the
      randomizer $\alpha$ from the PCZT.

4. **Return.** The Keystone displays a QR code containing the signed
   PCZT. The wallet scans and parses it.

5. **Extraction.** The wallet extracts the 64-byte
   $\mathsf{spend}\_\mathsf{auth}\_\mathsf{sig}$ and the 32-byte
   sighash from the signed PCZT.

## Keystone Device Display

During signing, the Keystone device displays the governance PCZT as a
standard Orchard transaction. The user sees the following on the device
screen:

    Amount: 0.00000001 ZEC
    Fee: 0 ZEC

    Orchard
    From
    #1 0.00000001 ZEC Mine
    <shielded>

    To
    #1 0.00000001 ZEC
    {governance hotkey address}
    Memo: I am authorizing this hotkey managed by my
          wallet to vote on {round_name} with
          {amount}.{frac} ZEC

The 0.00000001 ZEC amount (1 zatoshi) and 0 ZEC fee confirm that no
real funds are being transferred. The "To" address matches the
governance hotkey address displayed in the wallet application. The memo
provides human-readable context for what the user is authorizing.

The Keystone device has no awareness of governance semantics. It
interprets the governance PCZT identically to any other Orchard
transaction.

## Signature Extraction and Submission

After receiving the signed PCZT from the Keystone device, the wallet:

1. Parses the signed PCZT structurally and reads the
   $\mathsf{spend}\_\mathsf{auth}\_\mathsf{sig}$ field from the relevant action.
   Keystone redacts sensitive fields (e.g., $\alpha$, rseed, ZIP-32 derivation)
   after signing, so the wallet MUST extract the signature by parsing
   the PCZT structure rather than by byte-diffing against the unsigned
   version.

2. Extracts the sighash that the Keystone signed. This is the ZIP 244
   transaction identifier computed over the governance PCZT.

3. Assembles the delegation submission by combining the Keystone
   signature and sighash with the Delegation Proof and other public
   inputs. The full delegation message structure is defined in the
   Delegation Message section of [^voting-protocol].

The delegation submission is sent to the vote chain. The wallet does
not need the Keystone device again for the remainder of the voting
round; all subsequent operations (voting, share submission) use the
governance hotkey.

## On-Chain Verification

The vote chain verifies the delegation submission as specified in the
Out-of-Circuit Verification section of [^voting-protocol]. In
particular, the verifier:

1. Checks that the $\mathsf{SpendAuthSig}^{\mathsf{Orchard}}$ is valid
   under $\mathsf{rk}$ over the submitted sighash.
2. Verifies the Delegation Proof, which establishes (among other
   conditions) that $\mathsf{rk}$ is a valid rerandomization of the
   holder's $\mathsf{ak}$, that the rho binding is correct, and that
   the signed note's address belongs to the holder.

The on-chain verifier does not distinguish between Keystone-signed and
software-signed delegations. Both produce the same delegation message
format and are subject to identical verification.


# Rationale

## Why 1 Zatoshi Instead of 0

The dummy signed note uses a value of 1 zatoshi (0.00000001 ZEC) in the
governance PCZT rather than 0. When an Orchard Action has a 0-value
note, Keystone suppresses the display of transaction fields (amount,
fee, addresses, memo), presenting the user with insufficient information
to make an informed signing decision. Setting the value to 1 zatoshi
causes Keystone to render all fields normally.

The Delegation Proof circuit enforces that the signed note value is 0
regardless of the PCZT value. The 1-zatoshi value exists solely in the
serialized PCZT for the benefit of Keystone's display logic and has no
effect on protocol security or fund safety.

## Why a Dummy Note Instead of a Real Note

A holder's real Orchard notes are not spent or consumed during
delegation. The dummy signed note is constructed specifically for
governance and never appears in any on-chain note commitment tree.
This design has three advantages:

- **No fund risk.** Because the governance PCZT is never broadcast to
  the Zcash mainchain and the signed note has no on-chain existence,
  there is no scenario in which the delegation signing could result in
  loss of funds.
- **Note reusability.** Because real notes are never consumed on
  mainchain, they remain fully spendable and available for other
  applications that use the Orchard Proof-of-Balance [^balance-proof]
  mechanism. Governance nullifiers are domain-separated by
  $\mathsf{voting}\_{\mathsf{round}\_\mathsf{id}}$, so the same notes
  can participate in concurrent voting rounds or other balance-proof
  use cases without conflict.
- **PCZT compatibility.** The dummy note reuses the standard Orchard
  Action structure, allowing the governance PCZT to pass through the
  Keystone's existing PCZT parser and signer without modification.

## Why Rho Binding Provides Non-Replayability

The dummy signed note's $\text{ρ}^{\mathsf{signed}}$ is set to a
Poseidon hash of the delegated note commitments, the VAN, and the
voting round identifier. Because $\text{ρ}$ enters the note commitment
(and therefore the sighash), the Keystone's signature is
cryptographically bound to the exact delegation context. An attacker
cannot replay the signature for a different set of notes, a different
VAN, or a different voting round.

This binding is enforced by the Delegation Proof circuit's rho binding
condition, which the vote chain verifies. The Keystone device does not
need to understand the binding; it is sufficient that the device signs
the sighash derived from the PCZT containing the bound $\text{ρ}$.

## Why ZIP 244 Sighash

The governance PCZT uses the standard ZIP 244 [^zip-244] transaction
identifier as the sighash. This is the only sighash format that
Keystone's existing Orchard signing implementation can produce. Using a
governance-specific sighash would require firmware changes, which this
ZIP explicitly avoids.

The ZIP 244 sighash commits to the full Orchard bundle structure
(including the dummy note's commitment, which embeds the bound
$\text{ρ}$), providing the necessary cryptographic binding without
a custom signature scheme.


# Deployment

The pre-firmware signing flow specified in this ZIP is the current
deployment path. No changes to Keystone firmware or to the Zcash
mainchain consensus rules are required.

When Keystone firmware adds voting-aware signing support (see
[Open issues]), the governance PCZT construction changes but the
overall delegation protocol remains the same: one or more hardware
wallet signatures (one per batch of up to 5 notes) authorize a
governance hotkey for one voting round.


# Reference implementation

The governance PCZT construction and Keystone signature extraction are
implemented in the coinholder voting wallet library.

At the time of writing, some implementation repositories are not
publicly accessible. Public, stable links will be added before
finalization of this ZIP.


# Open issues

- **Voting-aware firmware.** A Keystone firmware update could introduce
  a governance network byte (analogous to the testnet byte) that causes
  the device to display the delegation context (delegated note count,
  total ZEC, voting round name) instead of a generic Orchard
  transaction. The device could then sign a governance-specific sighash
  that binds directly to the delegation parameters. The dummy signed
  note scaffolding (signed note integrity, rho binding, output note
  commitment) could be removed from the Delegation Proof circuit. This
  migration is purely subtractive: the post-firmware circuit is a strict
  subset of the pre-firmware circuit, and only the Delegation Proof
  changes. The Vote Proof and Vote Reveal Proof are unaffected.
- **Memo content standardization.** The delegation memo format is
  currently informational. A future revision could specify a structured
  memo format (e.g., with machine-readable fields) to support
  programmatic verification of delegation intent.


# References

[^BCP14]: [Information on BCP 14 — "RFC 2119: Key words for use in RFCs to Indicate Requirement Levels" and "RFC 8174: Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words"](https://www.rfc-editor.org/info/bcp14)

[^protocol]: [Zcash Protocol Specification, Version 2025.6.3 [NU6.1] or later](protocol/protocol.pdf)

[^protocol-concretespendauthsig]: [Zcash Protocol Specification, Version 2025.6.3 [NU6.1]. Section 5.4.7.1: Spend Authorization Signature (Orchard)](protocol/protocol.pdf#concretespendauthsig)

[^voting-protocol]: [Shielded Voting Protocol](draft-valargroup-shielded-voting)

[^balance-proof]: [Orchard Proof-of-Balance](draft-valargroup-orchard-balance-proof)

[^pczt]: [zcash/zips issue #693: Standardize a protocol for creating shielded transactions offline (PCZT)](https://github.com/zcash/zips/issues/693)

[^zip-244]: [ZIP 244: Transaction Identifier Non-Malleability](zip-0244)

[^zip-32]: [ZIP 32: Shielded Hierarchical Deterministic Wallets](zip-0032)

[^ur]: [BCR-2020-005: Uniform Resources (UR)](https://github.com/BlockchainCommons/Research/blob/master/papers/bcr-2020-005-ur.md)
