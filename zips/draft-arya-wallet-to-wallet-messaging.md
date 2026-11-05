    ZIP: Unassigned
    Title: Wallet-to-Wallet Messaging
    Owners: Arya <arya@zfnd.org>
    Status: Draft
    Category: Standards / Wallet
    Created: 2026-11-03
    License: MIT
    Pull-Request: <https://github.com/zcash/zips/pull/???>


# Terminology

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this
document are to be interpreted as described in BCP 14 [^BCP14] when, and only
when, they appear in all capitals.

The terms "Unified Address", "Unified Viewing Key", "Receiver", "Metadata
Item", "Typecode", "Producer", and "Consumer" are to be interpreted as defined
in ZIP 316. [^zip-0316] An "Orchard Receiver" is a Receiver with Typecode
$\mathtt{0x03}$.

compactSize

: A variable-length integer as used in the Bitcoin protocol,
  [^Bitcoin-CompactSize] in minimal encoding, with a value of at most
  $\mathtt{0x02000000}$.

Sender wallet

: The wallet that creates and deposits an Envelope.

Recipient wallet

: The wallet an Envelope is encrypted to.

Envelope

: An encrypted message, padded to a size class, as deposited in a Mailbox.

Mailbox

: A service that holds Envelopes for a Recipient wallet until it fetches them.

Mailbox Descriptor

: The data a Sender wallet needs to deposit an Envelope in a Mailbox.

Transport Binding

: A specification of the Mailbox operations over one anonymity network,
  identified by a `binding_id`.

Payload

: The typed content carried inside an Envelope.


# Abstract

This ZIP specifies an off-chain channel between Zcash wallets. A Sender wallet
that holds a Recipient wallet's Unified Address deposits an encrypted Envelope
in a Mailbox over an anonymity network, and the Recipient wallet fetches it
later. Neither wallet reveals its network identity to the other, and the
Mailbox operator does not learn who sent an Envelope.

Envelopes are encrypted to the Orchard Receiver of the Unified Address, using
the Orchard key agreement with a domain-separated key derivation, so no new
keys have to be exchanged. A new ZIP 316 Metadata Item carries the Mailbox
Descriptor in the Unified Address. Payload types are defined for
acknowledgements, text, ZIP 321 payment requests, and PCZTs, with codes
reserved for FROST signing rounds and off-chain note delivery. Mailbox
credentials are derived from the wallet seed with ZIP 32 registered key
derivation.

Anyone who holds the recipient's Orchard incoming viewing key can read its
Envelopes, and a Mailbox Descriptor links every Unified Address that carries
it. Transport Bindings are specified separately; Appendix A sketches one for
the Nym mixnet. [^nym]


# Motivation

Several wallet protocols need a direct channel between wallets. Each wallet
that wants one currently builds its own, so wallets from different vendors
cannot talk to each other:

- Multisig and hardware-signer flows pass PCZTs [^pczt] between parties.
- FROST signing (ZIP 312 [^zip-0312]) runs over a confidential, authenticated
  channel between the Coordinator and the signers whose mechanism ZIP 312
  leaves out of scope. This ZIP supplies the confidential, anonymous
  transport; a FROST payload would have to carry its own authentication.
- Payment requests (ZIP 321 [^zip-0321]) and acknowledgements have no
  wallet-to-wallet transport.
- Project Tachyon [^tachyon] [^tachyon-post] proposes removing in-band secret
  distribution from transactions, which makes an off-chain delivery channel a
  requirement rather than an add-on.

On-chain memos are the only standard channel today. ZIP 231 [^zip-0231]
proposes to lift their 512-byte size cap, but memos would still cost fees, be
stored by every full validator forever, and need a block confirmation per
round, which rules out interactive protocols such as PCZT and FROST
exchanges.

ZIP 324 [^zip-0324] delegates delivery to a channel the parties already
share, such as a secure messenger or a QR code, for the case where the sender
has no address for the recipient. It does not help when the sender does hold
a Unified Address, which is the case this ZIP covers.

The idea is not new. Hornby's 2020 light wallet privacy review [^hornby-2020]
lists out-of-band transaction delivery over a mixnet as an option and notes
that scalable Zcash will need a mixnet or similar technology anyway. zips#629
[^zips-629] suggests a mixnet plus a "private mailbox" to keep offline
reception. The Nym × Zcash integration guide [^nym-zcash] covers routing a
wallet's chain-sync and transaction-submission traffic through the mixnet,
not wallet-to-wallet delivery. This ZIP fills that gap.


# Privacy Implications

**Who can read Envelopes.** Envelopes are encrypted to an Orchard Receiver, so
anyone holding the account's Orchard incoming viewing key can decrypt them.
That is the trust model of incoming notes, but Envelopes can carry more: a
PCZT reveals a transaction the recipient is about to sign, including its
outputs. Users who share incoming viewing keys with auditors or watch-only
services should not expect Envelopes to be private from them.

**Linkability.** A Mailbox Descriptor is a stable identifier. Two Unified
Addresses that carry the same descriptor are linked to one recipient by anyone
who sees both, which defeats diversified addresses. Unlinkable addresses
therefore need separate mailboxes, at the cost of more credentials to derive
and more mailboxes to fetch from. A `reply_to` address inside an Envelope has
the same property for the sender.

**Network observers and the Mailbox operator.** The anonymity network hides
the sender's network identity from the operator and the recipient, and the
recipient's from the sender. The operator still sees how many Envelopes a
mailbox receives, their size classes, and when they are deposited and
fetched. In bindings where the recipient connects to its own mailbox
directly, as in the Nym sketch of Appendix A, the operator also learns the
recipient's network identity unless the connection is tunnelled, for example
over Tor. Network privacy is only as good as the anonymity set: while few
wallets use a binding, cover traffic carries most of the weight.

**Timing.** A deposit made at the same moment as a related on-chain
broadcast, a fetch triggered by opening the app, or an immediate
acknowledgement each leak timing that an observer can correlate with chain
activity. The wallet behaviour rules in the specification reduce but do not
remove this.

**No sender authentication and no forward secrecy.** Envelopes do not
authenticate their sender, so a Text payload can impersonate anyone; the
specification forbids presenting it as coming from a named party. Envelope
keys derive from long-lived keys, so compromise of an incoming viewing key
exposes every Envelope the adversary has recorded, as for on-chain notes.

**Denial of service.** Anyone holding a Unified Address can fill its mailbox.
The cost falls on the mailbox's storage and the recipient's bandwidth; trial
decryption itself is cheap. Bindings are expected to document quotas, and the
unencrypted Envelope header lets a wallet see size classes before fetching
bodies where a binding allows that.


# Requirements

- A sender holding only a recipient's Unified Address can deliver a message
  with no prior contact.
- The recipient need not be online when the message is sent.
- No long-term key material is needed beyond what the wallet derives from its
  seed, and a wallet restored from seed can recover its mailboxes on a
  best-effort basis.
- Neither the Mailbox operator nor a network observer learns the sender's
  network identity or links a sender to a recipient. The sender does not learn
  the recipient's network identity.
- An Envelope reveals nothing about its content beyond its size class.
- Wallets that implement ZIP 316 but not this ZIP can still parse and pay a
  Unified Address that carries a Mailbox Descriptor, provided the Typecode
  registration requested in the Specification is granted.
- The core protocol does not depend on any one network or token.


# Non-requirements

- Sender authentication at the Envelope layer. Payload types that need it
  carry their own.
- Guaranteed delivery. Delivery is best-effort; protocols built on top have to
  handle loss.
- Forward secrecy.
- Group messaging.
- Hiding the recipient's network identity from its own Mailbox operator. A
  binding may provide this, and a wallet can add Tor, but the core does not
  require it.


# Specification

## Overview

    Sender wallet                                        Recipient wallet
         |                                                      ^
         | 1. read Orchard Receiver and Mailbox                 |
         |    Descriptor from the recipient's UA                |
         | 2. build and encrypt the Envelope                    | 5. trial-decrypt
         | 3. Deposit over the anonymity network                |    with ivk
         v                                                      |
      [ Mailbox ] -------------- 4. Fetch over the anonymity network

## Mailbox Descriptors [mailbox-descriptors]

A Mailbox Descriptor is encoded as:

| Field            | Type                   | Description                      |
|------------------|------------------------|----------------------------------|
| `binding_id`     | `u16` (LE)             | Identifies the Transport Binding |
| `descriptor_len` | `compactSize`          | Length of `descriptor`           |
| `descriptor`     | `byte[descriptor_len]` | Binding-specific bytes           |

Registered `binding_id` values:

| `binding_id`                        | Binding                                      |
|-------------------------------------|----------------------------------------------|
| $\mathtt{0x0000}$                   | Reserved                                     |
| $\mathtt{0x0001}$                   | Nym mixnet (Appendix A, non-normative)       |
| $\mathtt{0xFF00}$–$\mathtt{0xFFFF}$ | Experimental; MUST NOT be used in production |

## Unified Address Metadata Item [metadata-item]

This ZIP defines a ZIP 316 Metadata Item, **Mailbox Descriptors**, with a
Typecode in the Non-MUST-understand Metadata range $\mathtt{0xC0}$ to
$\mathtt{0xDF}$, to be assigned by the ZIP Editors. [^zip-0316-metadata]

The Item's value MUST parse as one or more Mailbox Descriptors, concatenated
with no trailing bytes, in the recipient's order of preference. Descriptors
with an unrecognised `binding_id` MUST be skipped, not rejected. A Sender
wallet SHOULD use the first descriptor whose binding it supports.

A Unified Address that carries this Item MUST also carry an Orchard Receiver;
Envelopes are encrypted to that Receiver. The Item MUST NOT appear in a
Unified Viewing Key.

A Mailbox Descriptor is a stable identifier. A wallet MUST NOT put the same
descriptor into two Unified Addresses that the user expects to be unlinkable.
Wallets SHOULD include the Item only in addresses generated for a purpose
that calls for messaging, and SHOULD NOT include it by default.

If a binding's descriptors can go stale (for example in Appendix A, when the
recipient changes gateway), the wallet SHOULD also set an Address Expiry Time
Metadata Item [^zip-0316-expiry] on the address. Address Expiry Typecodes are
MUST-understand, so such an address can only be paid by Consumers that
implement ZIP 316 Revision 2; see [Open issues](#open-issues).

### Typecode registration [typecode-registration]

The ZIP 316 Typecode Registry [^zip-0316-registry] does not currently permit
Producers to include Non-MUST-understand Metadata in any address type, and
additions to the registry are made by 2xxx-series ZIPs. This ZIP requests the
following row, to be applied when it reaches Proposed status:

| Typecode | Description         | R0 | R2 `zu` | R2 `tu` |
|----------|---------------------|----|---------|---------|
| TBD      | Mailbox Descriptors | ✅ | ✅      | ✅      |

The Item has no effect on transaction construction, so it meets ZIP 316's
condition for `zu` addresses. Permitting it in Revision 0 addresses is what
lets wallets that predate this ZIP pay the address, because Consumers ignore
Items with Typecodes they do not recognise. If the ZIP Editors permit it only
in Revision 2 addresses, the compatibility requirement holds only for
Consumers that implement ZIP 316 Revision 2.

## Envelope encryption [envelope-encryption]

Let $(\mathsf{d}, \mathsf{pk_d})$ be the recipient's Orchard Receiver. Let
$\mathsf{KA^{Orchard}}$ [^protocol-orchardkeyagreement],
$\mathsf{DiversifyHash^{Orchard}}$ [^protocol-diversifyhash],
$\mathsf{repr}_{\mathbb{P}}$ and $\mathsf{abst}_{\mathbb{P}}$
[^protocol-pallasandvesta], and $\mathsf{ivk}$
[^protocol-orchardkeycomponents] be as defined in the Zcash Protocol
Specification, and let $\mathsf{LEBS2OSP}_{256}$ be used to encode Pallas
points as 32-byte strings as in $\mathsf{KDF^{Orchard}}$.
[^protocol-orchardkdf]

The sender:

1. Computes $\mathsf{g_d} = \mathsf{DiversifyHash^{Orchard}}(\mathsf{d})$.
2. Chooses $\mathsf{esk}$ uniformly at random from
   $\mathsf{KA^{Orchard}.Private}$. $\mathsf{esk}$ MUST NOT be reused across
   Envelopes.
3. Computes $\mathsf{epk} = \mathsf{KA^{Orchard}.DerivePublic}(\mathsf{esk}, \mathsf{g_d})$,
   $\mathsf{sharedSecret} = \mathsf{KA^{Orchard}.Agree}(\mathsf{esk}, \mathsf{pk_d})$,
   and $\mathsf{ephemeralKey} = \mathsf{LEBS2OSP}_{256}(\mathsf{repr}_{\mathbb{P}}(\mathsf{epk}))$.
4. Derives the 32-byte key

   $\hspace{2em}\mathsf{K} = \mathsf{BLAKE2b\text{-}256}(\texttt{"Zcash\_WalletMsg\_"}, \mathsf{LEBS2OSP}_{256}(\mathsf{repr}_{\mathbb{P}}(\mathsf{sharedSecret})) \,||\, \mathsf{ephemeralKey})$

   This is $\mathsf{KDF^{Orchard}}$ with a different personalization, so
   Envelope keys are domain-separated from note encryption keys even though
   they share the key agreement.
5. Chooses the smallest size class (see [Envelope format](#envelope-format))
   whose padded size $N$ fits the plaintext, and pads the plaintext with zero
   bytes to exactly $N$ bytes.
6. Computes

   $\hspace{2em}\mathsf{C} = \mathsf{IETF\_AEAD\_CHACHA20\_POLY1305.Encrypt}(\mathsf{K}, \mathsf{nonce}, \mathsf{aad}, \mathsf{plaintext})$
   [^RFC8439]

   with $\mathsf{nonce} = [\mathtt{0x00}]^{12}$ and
   $\mathsf{aad} = \mathtt{version} \,||\, \mathtt{size\_class} \,||\, \mathsf{ephemeralKey}$.
   The zero nonce is safe because $\mathsf{K}$ is unique to each
   $\mathsf{esk}$.

The recipient, for each Orchard incoming viewing key $\mathsf{ivk}$ it holds:

1. Computes $\mathsf{epk} = \mathsf{abst}_{\mathbb{P}}(\mathsf{ephemeralKey})$
   and rejects the Envelope if the result is $\bot$ or the identity
   $\mathcal{O}_{\mathbb{P}}$.
2. Computes $\mathsf{sharedSecret} = \mathsf{KA^{Orchard}.Agree}(\mathsf{ivk}, \mathsf{epk})$.
   Since $\mathsf{pk_d} = \mathsf{KA^{Orchard}.DerivePublic}(\mathsf{ivk}, \mathsf{g_d})$,
   this equals the sender's value.
3. Derives $\mathsf{K}$ as above and attempts decryption with the same
   $\mathsf{aad}$. On failure, the Envelope is not for this key.
4. Rejects the plaintext if it does not parse as described in
   [Plaintext format](#plaintext-format), or if any padding byte is nonzero.
5. Rejects the Envelope unless the plaintext's $\mathsf{d}$ is the
   diversifier of an address of this account that this wallet issued either
   with a Mailbox Descriptors Item or as a `reply_to`.

A wallet processes an Envelope under the first $\mathsf{ivk}$ for which
decryption succeeds. Steps 1 and 2 cost one point decompression and one
scalar multiplication per Envelope and account.

## Envelope format [envelope-format]

| Field          | Type           | Description                                                             |
|----------------|----------------|-------------------------------------------------------------------------|
| `version`      | `byte`         | $\mathtt{0x01}$                                                         |
| `size_class`   | `byte`         | See table below                                                         |
| `ephemeralKey` | `byte[32]`     | $\mathsf{LEBS2OSP}_{256}(\mathsf{repr}_{\mathbb{P}}(\mathsf{epk}))$     |
| `ciphertext`   | `byte[N + 16]` | AEAD output; $N$ is set by `size_class`                                 |

| `size_class`    | Padded plaintext size $N$ | Intended use              |
|-----------------|---------------------------|---------------------------|
| $\mathtt{0x00}$ | 2048 bytes                | Acks, URIs, short text    |
| $\mathtt{0x01}$ | 32768 bytes               | Small PCZTs, FROST rounds |
| $\mathtt{0x02}$ | 262144 bytes              | Large PCZTs               |

Other values are reserved. Recipients MUST reject Envelopes with an unknown
`version` or `size_class`, or whose length does not match `size_class`.

## Plaintext format [plaintext-format]

| Field          | Type                | Description                                                   |
|----------------|---------------------|---------------------------------------------------------------|
| `payload_type` | `u16` (LE)          | See [Payload types](#payload-types)                           |
| `flags`        | `byte`              | Bit 0: `ack_requested`; see below                             |
| `d`            | `byte[11]`          | Diversifier of the Orchard Receiver the Envelope was sent to  |
| `message_id`   | `byte[32]`          | Uniformly random                                              |
| `in_reply_to`  | `byte[32]`          | `message_id` of the Envelope this one answers, or all zero    |
| `expiry_time`  | `u64` (LE)          | Unix seconds; $0$ means no expiry                             |
| `reply_len`    | `compactSize`       | Length of `reply_to`                                          |
| `reply_to`     | `byte[reply_len]`   | A Unified Address, or empty                                   |
| `payload_len`  | `compactSize`       | Length of `payload`                                           |
| `payload`      | `byte[payload_len]` | Type-specific                                                 |
| `padding`      | `byte[]`            | Zero bytes up to $N$                                          |

Senders MUST set bits of `flags` other than bit 0 to $0$; recipients MUST
ignore bits they do not recognise.

`d` lets the recipient attribute the Envelope to one of its addresses without
trusting `reply_to`, and `in_reply_to` lets protocols with several rounds
match answers to requests.

`reply_to`, if present, is the UTF-8 string encoding of a Unified Address
[^zip-0316-encoding] whose Human-Readable Part matches the network of the
Envelope's recipient. It MUST carry an Orchard Receiver and MAY carry a
Mailbox Descriptors Item. A reply is encrypted to
that Receiver. It is deposited in the mailbox named by the Item if there is
one, or sent by a transport-level anonymous reply if the binding provides one
(see [Mailbox operations](#mailbox-operations)); if neither is available, no
reply is possible. A sender that wants replies without linking them to its
other addresses SHOULD use a Unified Address and mailbox dedicated to replies.

Senders SHOULD round `expiry_time` to the hour, to avoid leaking clock skew.

Recipients:

- MUST drop Envelopes whose `expiry_time` is nonzero and in the past.
- MUST drop Envelopes whose `message_id` they have already processed, and
  SHOULD remember processed `message_id`s at least until their expiry, or for
  a wallet-chosen period when `expiry_time` is $0$.
- MUST ignore the payload of an Envelope with an unknown `payload_type`, but
  still record its `message_id`.

## Payload types [payload-types]

| `payload_type`                      | Name            | Payload                                                |
|-------------------------------------|-----------------|--------------------------------------------------------|
| $\mathtt{0x0000}$                   | Reserved        | —                                                      |
| $\mathtt{0x0001}$                   | Ack             | Empty; `in_reply_to` names the acknowledged Envelope   |
| $\mathtt{0x0002}$                   | Text            | UTF-8 text for display to the user                     |
| $\mathtt{0x0003}$                   | Payment request | UTF-8 ZIP 321 URI [^zip-0321]                          |
| $\mathtt{0x0004}$                   | PCZT            | Serialized PCZT [^pczt]; format reference TBD          |
| $\mathtt{0x0005}$                   | Reserved        | FROST round messages (ZIP 312 [^zip-0312]); format TBD |
| $\mathtt{0x0006}$                   | Reserved        | Off-chain note delivery [^tachyon]; format TBD         |
| $\mathtt{0xF000}$–$\mathtt{0xFFFF}$ | Experimental    | MUST NOT be used in production                         |

An Ack MUST NOT set `ack_requested`.

Payloads MUST NOT carry spend authority, such as spending keys or ZIP 324 URIs
[^zip-0324], because every holder of the recipient's incoming viewing key can
read them.

Payload types that cause side effects SHOULD carry their own replay
protection; `message_id` deduplication and `expiry_time` only bound replay.

## Mailbox operations [mailbox-operations]

A Transport Binding MUST provide these operations:

- **Deposit**(descriptor, envelope): deliver an Envelope to the Mailbox named
  by the descriptor.
- **Fetch**(credential) → envelopes: retrieve held Envelopes.
- **Delete**(credential, handles): remove fetched Envelopes, unless the
  binding documents that Fetch removes them implicitly.

A Transport Binding MUST hide the sender's network identity from the Mailbox
operator and from the recipient, and MUST hide the recipient's network
identity from the sender. It SHOULD hide the recipient's network identity from
the Mailbox operator, and SHOULD resist timing correlation by a global
passive adversary. Bindings SHOULD rate-limit Deposit and SHOULD bound the
storage a mailbox can consume.

A Transport Binding specification MUST state:

- the descriptor encoding;
- how the 64-byte mailbox key from
  [Mailbox key derivation](#mailbox-key-derivation) is turned into the
  binding's credentials;
- the retention period, or how a wallet learns it;
- per-mailbox storage quotas, if any;
- which size classes it supports;
- how replies work: by depositing to a `reply_to` mailbox, by a
  transport-level anonymous reply, or both, and how long each path stays
  usable;
- rate limiting and cost, if any;
- what network identity, timing, and size information each party can
  observe.

## Mailbox key derivation [mailbox-key-derivation]

Mailbox credentials are derived from the wallet seed $S$ with ZIP 32
registered key derivation [^zip-0032-registered], using
$\mathsf{ContextString} = \texttt{"Zcash\_WalletMessaging"}$ and
$\mathsf{ZipNumber}$ equal to the number assigned to this ZIP:

- $(\mathsf{sk}_{subtree}, \mathsf{c}_{subtree}) = \mathsf{RegKD}(\mathsf{ContextString}, S, \mathsf{ZipNumber})$
- $(\mathsf{sk}_{n}, \mathsf{c}_{n}) = \mathsf{CKDreg}((\mathsf{sk}_{subtree}, \mathsf{c}_{subtree}), \mathsf{coin\_type} + 2^{31}, [\,])$
- $(\mathsf{sk}_{b}, \mathsf{c}_{b}) = \mathsf{CKDreg}((\mathsf{sk}_{n}, \mathsf{c}_{n}), \mathtt{binding\_id} + 2^{31}, [\,])$
- $(\mathsf{sk}_{a}, \mathsf{c}_{a}) = \mathsf{CKDreg}((\mathsf{sk}_{b}, \mathsf{c}_{b}), \mathsf{account} + 2^{31}, [\,])$
- $\mathsf{K}_{i} = \mathsf{derive\_child\_cryptovalue}((\mathsf{sk}_{a}, \mathsf{c}_{a}), i + 2^{31}, [\,])$

where $\mathsf{coin\_type}$ is the ZIP 32 coin type of the network
[^zip-0032-paths], so that Mainnet and Testnet mailboxes are unlinkable;
$\mathsf{account}$ is the ZIP 32 account index of the Orchard key whose
addresses carry the descriptor; and $i$ is a per-binding, per-account counter
that the wallet increments for each new mailbox. $\mathsf{K}_{i}$ is 64
bytes; each binding states how it is split into credentials.

A wallet restored from seed can rebuild its credentials by scanning $i$ from
$0$ with a gap limit, subject to the binding's own limits (for example,
knowing which gateway each mailbox used).

## Wallet behaviour [wallet-behaviour]

Sending:

- Wallets SHOULD NOT deposit an Envelope at the same moment as a related
  on-chain broadcast, and SHOULD add a random delay when the use is not
  interactive.
- Wallets MUST NOT fall back to a direct connection to a Mailbox when the
  binding's anonymity network is unavailable.

Fetching:

- Wallets SHOULD fetch on a randomized schedule that does not depend on user
  actions, including when no message is expected.
- Wallets SHOULD cap the bytes they fetch and trial-decrypt per Fetch.

Acknowledgements:

- Wallets SHOULD send an Ack only when `ack_requested` is set, and SHOULD
  delay it by a random amount.

Display:

- Envelopes are not authenticated. Wallets MUST NOT present a message as
  coming from a named party unless the payload type itself authenticates the
  sender, and SHOULD NOT open links in Text payloads without user
  confirmation.

Viewing keys:

- Wallets that export an account's incoming viewing key to a third party
  SHOULD NOT advertise mailboxes on that account's addresses.


# Rationale

**Why reuse Orchard key agreement?** It needs no new keys and no prior
contact: any Unified Address with an Orchard Receiver is already a public
encryption key. The cost is that incoming viewing key holders can read
Envelopes; a dedicated messaging key in the descriptor would avoid that at
the cost of a larger Item.

**Why fixed size classes?** Exact lengths would leak payload types and
content. Three classes keep the anonymity set per class large while still
allowing PCZTs.

**Why no ZIP 324 payload?** A sender that can use this channel already holds
the recipient's Unified Address and can pay it on chain, and a ZIP 324 URI
carries spend authority that every incoming viewing key holder could use.

**Why a transport-agnostic core?** Tying a standard to one network and its
token is a long-term risk. Nym is sketched first because it is live,
packet-based, uses cover traffic, stores messages for offline clients, and
offers sender-anonymous replies.


# Reference implementation

None yet.


# Open issues [open-issues]

- Assignment of the Metadata Item Typecode, whether it is permitted in
  Revision 0 addresses, and this ZIP's number, which the key derivation
  depends on.
- Whether to encrypt to a dedicated messaging key carried in the descriptor
  instead of to the Orchard Receiver, so that incoming viewing key holders
  cannot read Envelopes.
- Address Expiry Items make an address unpayable by ZIP 316 Revision 0
  Consumers, while the compatibility requirement assumes they can pay it.
  Whether to recommend expiry, shorter-lived descriptors, or neither.
- The cost of running one mailbox per unlinkable address, and whether wallets
  should offer a deliberately linkable "contact" mode.
- A stable reference for the PCZT serialization.
- The FROST round message format and its authentication layer.
- The off-chain note delivery format, to be aligned with Tachyon.
- Support for Sapling-only recipients.
- A Tor onion-service binding.
- Whether the Nym binding in Appendix A becomes normative in this ZIP or in a
  separate one, once its TBDs are resolved.


# Appendix A: Nym transport binding (non-normative) [nym-binding]

This appendix sketches a binding for the Nym mixnet so that the core protocol
can be evaluated against a real network. It is not a complete Transport
Binding specification: the items marked TBD have to be resolved before it can
be made normative. `binding_id` $\mathtt{0x0001}$ is reserved for it.

**Descriptor.** The 96-byte binary form of a Nym client address,
[^nym-addressing] [^nym-recipient] laid out as follows:

| Field                 | Type       | Description                       |
|-----------------------|------------|-----------------------------------|
| client identity key   | `byte[32]` | Ed25519 public key                |
| client encryption key | `byte[32]` | X25519 public key                 |
| gateway identity key  | `byte[32]` | Ed25519 public key of the gateway |

**Credentials.** The first 32 bytes of $\mathsf{K}_{i}$ would be the Ed25519
seed of the client identity key, and the last 32 bytes the X25519 secret key
[^RFC7748] of the client encryption key. The Nym Rust SDK accepts externally
supplied client keys through a custom key store. [^nym-sdk-keys]

**Deposit.** The sender sends the Envelope as a Nym message to the
descriptor's address through the mixnet, from an ephemeral Nym client with
fresh keys rather than from its own mailbox client, attaching reply SURBs
[^nym-surbs] if it expects a prompt reply. Each ephemeral client has to
register with an entry gateway and hold bandwidth credentials; the cost and
latency of doing so per message are unverified (TBD).

**Fetch.** The recipient runs a Nym client with the derived keys, connected to
the gateway named in the descriptor, with cover traffic on. The gateway stores
messages while the client is offline and delivers them when it connects.
[^nym-addressing]

**Delete.** Implicit on delivery by the gateway (TBD: confirm).

**Retention.** Not documented by Nym (TBD).

**Size classes.** All. Nym splits a message into fixed-size Sphinx packets,
so larger classes take more packets and leave a larger timing footprint.

**Replies.** SURB reply keys expire after 24 hours, [^nym-surbs] so SURBs
serve interactive exchanges only. A recipient that fetches later can reply
only to a `reply_to` address that carries a Nym descriptor.

**Rate limiting and cost.** Sending through Nym consumes bandwidth
credentials. Who pays, and whether they can be bought with shielded ZEC, is
TBD.

**Gateway changes.** The gateway is part of the descriptor. If the recipient
moves gateway, old descriptors stop working and a new Unified Address has to
be issued. How a wallet restored from seed learns which gateway each mailbox
index used is TBD.

**Observability.** The recipient's gateway, which is the Mailbox operator,
sees the recipient's connection, including its IP address unless the
connection is tunnelled over Tor, and the count and size of stored messages.
The sender's entry gateway sees the sender's IP address but not the
destination. Mix nodes see packets only. A global passive adversary faces
Nym's mixing delays and cover traffic.


# References

[^BCP14]: [Information on BCP 14 — "RFC 2119: Key words for use in RFCs to Indicate Requirement Levels" and "RFC 8174: Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words"](https://www.rfc-editor.org/info/bcp14)

[^protocol-orchardkeycomponents]: [Zcash Protocol Specification, Version 2026.8.0 [NU6.3]. Section 4.2.3: Orchard Key Components](protocol/protocol.pdf#orchardkeycomponents)

[^protocol-diversifyhash]: [Zcash Protocol Specification, Version 2026.8.0 [NU6.3]. Section 5.4.1.6: DiversifyHash^Sapling and DiversifyHash^Orchard Hash Functions](protocol/protocol.pdf#concretediversifyhash)

[^protocol-orchardkeyagreement]: [Zcash Protocol Specification, Version 2026.8.0 [NU6.3]. Section 5.4.5.5: Orchard Key Agreement](protocol/protocol.pdf#concreteorchardkeyagreement)

[^protocol-orchardkdf]: [Zcash Protocol Specification, Version 2026.8.0 [NU6.3]. Section 5.4.5.6: Orchard Key Derivation](protocol/protocol.pdf#concreteorchardkdf)

[^protocol-pallasandvesta]: [Zcash Protocol Specification, Version 2026.8.0 [NU6.3]. Section 5.4.9.6: Pallas and Vesta](protocol/protocol.pdf#pallasandvesta)

[^RFC7748]: [RFC 7748: Elliptic Curves for Security](https://www.rfc-editor.org/rfc/rfc7748.html)

[^RFC8439]: [RFC 8439: ChaCha20 and Poly1305 for IETF Protocols](https://www.rfc-editor.org/rfc/rfc8439.html)

[^Bitcoin-CompactSize]: [Variable length integer. Bitcoin Wiki](https://en.bitcoin.it/wiki/Protocol_documentation#Variable_length_integer)

[^zip-0032-registered]: [ZIP 32: Shielded Hierarchical Deterministic Wallets — Specification: Registered key derivation](zip-0032.rst#specification-registered-key-derivation)

[^zip-0032-paths]: [ZIP 32: Shielded Hierarchical Deterministic Wallets — Key path levels](zip-0032.rst#key-path-levels)

[^zip-0231]: [ZIP 231: Memo Bundles](zip-0231.md)

[^zip-0312]: [ZIP 312: FROST for Spend Authorization Multisignatures](zip-0312.rst)

[^zip-0316]: [ZIP 316: Unified Addresses and Unified Viewing Keys](zip-0316.rst)

[^zip-0316-encoding]: [ZIP 316: Unified Addresses and Unified Viewing Keys — Encoding of Unified Addresses](zip-0316.rst#encoding-of-unified-addresses)

[^zip-0316-metadata]: [ZIP 316: Unified Addresses and Unified Viewing Keys — Metadata Items](zip-0316.rst#metadata-items)

[^zip-0316-expiry]: [ZIP 316: Unified Addresses and Unified Viewing Keys — Address Expiration Metadata](zip-0316.rst#address-expiration-metadata)

[^zip-0316-registry]: [ZIP 316: Unified Addresses and Unified Viewing Keys — Typecode Registry](zip-0316.rst#typecode-registry)

[^zip-0321]: [ZIP 321: Payment Request URIs](zip-0321.rst)

[^zip-0324]: [ZIP 324: URI-Encapsulated Payments](zip-0324.rst)

[^pczt]: [Partially Created Zcash Transactions (librustzcash `pczt` crate)](https://github.com/zcash/librustzcash/tree/main/pczt)

[^zips-629]: [zips#629: Scalability Design Explorations around changing Payment Flows](https://github.com/zcash/zips/issues/629)

[^hornby-2020]: [Taylor Hornby, "Fixing Privacy Problems in the Zcash Light Wallet Protocol" (2020)](https://defuse.ca/downloads/Fixing%20Privacy%20Problems%20in%20the%20Zcash%20Light%20Wallet%20Protocol.pdf)

[^tachyon]: [Sean Bowe and Ian Miers, "A Note on Notes: Towards Scalable Anonymous Payments via Evolving Nullifiers and Oblivious Synchronization", IACR ePrint 2025/2031](https://eprint.iacr.org/2025/2031)

[^tachyon-post]: [Sean Bowe, "Tachyon: Scaling Zcash with Oblivious Synchronization" (Zcash Community Forum thread)](https://forum.zcashcommunity.com/t/scaling-zcash-tachyon-ragu/50789)

[^nym]: [Nym documentation](https://nym.com/docs)

[^nym-addressing]: [Nym documentation: Addressing System](https://nym.com/docs/network/reference/addressing)

[^nym-recipient]: [`nym-sphinx-addressing` crate: `Recipient` (source)](https://docs.rs/nym-sphinx-addressing/latest/src/nym_sphinx_addressing/clients.rs.html)

[^nym-surbs]: [Nym documentation: Anonymous Replies (SURBs)](https://nym.com/docs/network/mixnet-mode/anonymous-replies)

[^nym-sdk-keys]: [`nym-sdk` crate: `shared_identity.rs` example](https://docs.rs/crate/nym-sdk/latest/source/examples/shared_identity.rs)

[^nym-zcash]: [Nym × Zcash Integration Guide](https://zcash-sdk.nym.com/)
