    ZIP: Unassigned
    Title: Wallet-to-Wallet Messaging
    Owners: Arya <arya@zfnd.org>
    Status: Draft
    Category: Standards / Wallet
    Created: 2026-11-03
    License: MIT
    Pull-Request: <https://github.com/zcash/zips/pull/1435>


# Terminology

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this
document are to be interpreted as described in BCP 14 [^BCP14] when, and only
when, they appear in all capitals.

The terms "Unified Address" and "Receiver" are to be interpreted as defined
in ZIP 316. [^zip-0316]

Envelope

: An encrypted message, padded to one of three sizes.

Mailbox

: A queue of Envelopes held by a Mailbox Server under a Mailbox ID.

Conversation

: The state two wallets share after a first Envelope: a secret from which
  they derive Envelope keys and Mailbox IDs.

Contact Mailbox, Pairwise Mailbox

: The Mailbox derived from an Orchard Receiver, and one derived from a
  Conversation, a direction, and a week-long epoch.

Routing Binding

: A specification of how wallets reach Mailbox Servers, and optionally each
  other, over one anonymity network.


# Abstract

This ZIP specifies an off-chain channel between Zcash wallets. A wallet that
holds another wallet's Unified Address deposits an encrypted Envelope in a
Mailbox, reaching the Mailbox Server over an anonymity network, and the
recipient fetches it later. Neither wallet reveals its network identity to
the other or to the server.

Nothing is added to the Unified Address. The Mailbox ID and Mailbox Server
are derived from the address's Orchard Receiver, the Envelope is encrypted to
that Receiver using the Orchard key agreement, and fetching requires the
incoming viewing key. Every first Envelope also starts a Conversation, whose
mailboxes rotate each epoch, so that an ongoing exchange does not accumulate
metadata under one identifier. Routing is separate from storage: mailboxes
are reached over any supported anonymity network, and prompt replies can also
go directly between the wallets. Payload types are defined for
acknowledgements, text, ZIP 321 payment requests, and PCZTs.

Anyone who holds the recipient's Orchard incoming viewing key can read and
fetch its Envelopes, and a Mailbox Server sees the volume and timing of what
each Mailbox ID receives. Appendix A sketches Routing Bindings for the Nym
mixnet [^nym] and for Tor. [^tor-rend]


# Motivation

Several wallet protocols need a direct channel between wallets, and each
wallet that wants one currently builds its own:

- Multisig and hardware-signer flows pass PCZTs [^pczt] between parties.
- FROST signing (ZIP 312 [^zip-0312]) needs a confidential, authenticated
  channel that ZIP 312 leaves out of scope. This ZIP supplies confidentiality
  and anonymity; a FROST payload would carry its own authentication.
- Payment requests (ZIP 321 [^zip-0321]) have no wallet-to-wallet transport.
- Project Tachyon [^tachyon] [^tachyon-post] proposes removing in-band secret
  distribution from transactions, which makes an off-chain delivery channel a
  requirement.

On-chain memos are the only standard channel today. Even without their size
cap (ZIP 231 [^zip-0231]) they cost fees, are stored forever, and need a
block confirmation per round. ZIP 324 [^zip-0324] covers the case where the
sender has no address for the recipient; this ZIP covers the case where it
does.

Out-of-band delivery over a mixnet, with a mailbox for offline recipients,
has been proposed before. [^hornby-2020] [^zips-629] The Nym × Zcash
integration [^nym-zcash] routes chain-sync and transaction submission through
the mixnet, not wallet-to-wallet messages.


# Privacy Implications

**Incoming viewing key holders.** Whoever holds an account's Orchard incoming
viewing key can read and fetch every Envelope ever sent to its addresses, and
by fetching can cause the server to delete them. It can also derive the
secret of every Conversation started with those addresses, and so read,
fetch, and send Envelopes in them, in both directions. There is no forward
secrecy. Envelopes can reveal more than notes do: a PCZT shows a transaction
before it is signed. The viewing keys of the wallet that starts a
Conversation give no access to it.

All diversified addresses of an account share one incoming viewing key, so
using a different address does not help. Viewing keys of different accounts
are unrelated: a user who shares an account's viewing key, for example with
an auditor or a watch-only service, keeps messages from its holder only by
receiving them at addresses of another account.

**Mailbox Servers.** A server never learns a network identity. It sees each
Mailbox ID it holds and the number, size, and timing of the Envelopes
deposited in and fetched from it. A Contact Mailbox lives as long as its
address, and anyone who knows the address can compute its ID and server, so
that server holds a long-lived traffic record for the address. Pairwise
Mailbox IDs change every epoch and can be computed only by the two wallets
and the responder's viewing key holders.

**Linking addresses.** Diversified addresses of one wallet have unrelated
Contact Mailboxes. A server can still link them if the wallet fetches them
together, which is why fetches use separate sessions and schedules.

**No opt-in signal.** Every address with an Orchard Receiver has a Contact
Mailbox whether or not its wallet implements this ZIP, so a sender cannot
tell whether its Envelope will be read.

**The other wallet.** Envelopes do not authenticate their sender. An answer
shows the sender that the recipient was online. Both wallets can fetch from
the Pairwise Mailboxes of both directions, so each can see when the other's
fetches cause its Envelopes to be deleted, and a wallet in Conversations with
two addresses can compare them.

**Network observers.** Privacy is bounded by the anonymity set of the Routing
Binding. A wallet's entry point to the network sees its IP address but no
Mailbox ID, server, or Zcash address.

**Denial of service.** Anyone can deposit under any Mailbox ID, at the
expense of the server's storage and the recipient's bandwidth.


# Requirements

- A sender holding only a recipient's Unified Address can deliver a message
  with no prior contact, while the recipient is offline.
- Unified Addresses and ZIP 316 are unchanged, and first contact needs no key
  material beyond the recipient's existing Orchard keys.
- A wallet can use many diversified addresses without a Mailbox Server, a
  network observer, or a sender being able to link them.
- No Mailbox Server or network observer learns the network identity of a
  sender or recipient, and neither wallet learns the other's.
- No party that sees a wallet's IP address is bound to that wallet's
  addresses or mailboxes.
- Two wallets can keep exchanging messages without a Mailbox Server
  accumulating metadata under a long-lived identifier.
- An Envelope reveals nothing about its content beyond its size.
- The protocol does not depend on any one network or token.


# Non-requirements

- Sender authentication, guaranteed delivery, forward secrecy, and group
  messaging.
- Backup and recovery. Contact Mailboxes can be recomputed from the wallet's
  addresses and viewing keys; Conversations cannot.


# Specification

## Notation

$\mathsf{BLAKE2b\text{-}256}$ and $\mathsf{BLAKE2b\text{-}512}$
[^protocol-blake2], $\mathsf{DiversifyHash^{Orchard}}$
[^protocol-diversifyhash], $\mathsf{ToScalar^{Orchard}}$ [^protocol-orchardkeycomponents], $\mathsf{Sym}$ [^protocol-sym],
$\mathsf{GroupHash}^{\mathbb{P}}$ [^protocol-grouphash],
$\mathsf{repr}_{\mathbb{P}}$ and $\mathcal{O}_{\mathbb{P}}$
[^protocol-pallasandvesta], and $\mathsf{I2LEOSP}$ and $\mathsf{LEBS2OSP}$
[^protocol-endian] are as defined in the Zcash Protocol Specification.

- $\mathsf{PointBytes}(Q) = \mathsf{LEBS2OSP}_{256}(\mathsf{repr}_{\mathbb{P}}(Q))$.
- $\mathsf{Scalar}(p, x) = \mathsf{ToScalar^{Orchard}}(\mathsf{BLAKE2b\text{-}512}(p, x))$.
- $[b]$ is the one-byte string with value $b$.

Integers are encoded little-endian. Times are in hours since the Unix epoch,
rounded down.

Throughout, $(\mathsf{d}, \mathsf{pk_d})$ is an Orchard Receiver with raw
encoding $\mathsf{rcv}$, [^protocol-orchardaddrencoding] incoming viewing key
$\mathsf{ivk}$, and
$\mathsf{g_d} = \mathsf{DiversifyHash^{Orchard}}(\mathsf{d})$.

## Envelopes

| Field          | Type           | Description                         |
|----------------|----------------|-------------------------------------|
| `version`      | `byte`         | $1$                                 |
| `ephemeralKey` | `byte[32]`     | $\mathsf{PointBytes}(\mathsf{epk})$ |
| `ciphertext`   | `byte[N + 16]` | $N$ is 2048, 32768, or 262144       |

The plaintext is:

| Field          | Type                | Description                                   |
|----------------|---------------------|-----------------------------------------------|
| `seed`         | `byte[32]`          | Uniformly random                              |
| `payload_type` | `u16`               | See [Payloads](#payloads)                     |
| `flags`        | `byte`              | Bit 0: `ack_requested`                        |
| `expiry_time`  | `u32`               | Time from which the Envelope is dropped       |
| `fast_len`     | `byte`              | Length of `fast_reply`                        |
| `fast_reply`   | `byte[fast_len]`    | See [Fast mode](#fast-mode); may be empty     |
| `payload_len`  | `u32`               | Length of `payload`                           |
| `payload`      | `byte[payload_len]` |                                               |
| padding        | `byte[]`            | Zero bytes up to the smallest $N$ that fits   |

Every Envelope belongs to a Conversation with secret $\kappa$, and is sent by
its *initiator* ($\delta = 0$) or its *responder* ($\delta = 1$).
$\mathsf{g_d}$, $\mathsf{pk_d}$, and $\mathsf{ivk}$ below are those of the
responder's Receiver. With

$\hspace{2em}\mathsf{esk} = \mathsf{Scalar}(\texttt{"Zcash\_WMsgEsk\_\_\_"}, \mathtt{seed}), \quad \mathsf{epk} = [\mathsf{esk}]\,\mathsf{g_d}$

$\hspace{2em}\mathsf{K} = \mathsf{BLAKE2b\text{-}256}(\texttt{"Zcash\_WMsgPairK\_"}, \kappa \,||\, [\delta] \,||\, \mathtt{ephemeralKey})$

the ciphertext is $\mathsf{Sym.Encrypt_K}$ of the plaintext.

A *first Envelope* starts a Conversation. Its sender is the initiator, and

$\hspace{2em}\kappa = \mathsf{BLAKE2b\text{-}256}(\texttt{"Zcash\_WMsgPairS\_"}, \mathsf{PointBytes}([\mathsf{esk}]\,\mathsf{pk_d}) \,||\, \mathtt{ephemeralKey})$

which the responder computes from
$[\mathsf{esk}]\,\mathsf{pk_d} = [\mathsf{ivk}]\,\mathsf{epk}$, as in Orchard
note decryption.

The recipient processes an Envelope only as a first Envelope to the Receiver
whose Contact Mailbox it was fetched from, or in the Conversation and
direction of the Pairwise Mailbox it was fetched from or of the `fast_reply`
address it arrived at. It MUST drop the Envelope, with no behaviour that
depends on which check failed, if:

- `version` or the length is unknown;
- decryption fails, the plaintext does not parse, or the padding is not zero;
- $\mathtt{ephemeralKey} \neq \mathsf{PointBytes}([\mathsf{esk}]\,\mathsf{g_d})$;
- `expiry_time` has been reached; or
- it has already processed an Envelope with this `ephemeralKey`.

It ignores the payload of an unknown `payload_type` and unknown bits of
`flags`, which senders set to zero.

## Payloads [payloads]

| `payload_type` | Name            | `payload`                                     |
|----------------|-----------------|-----------------------------------------------|
| $1$            | Ack             | `ephemeralKey` of the acknowledged Envelope   |
| $2$            | Text            | UTF-8 text for display to the user            |
| $3$            | Payment request | UTF-8 ZIP 321 URI [^zip-0321]                 |
| $4$            | PCZT            | Serialized PCZT [^pczt]; format reference TBD |

An Ack MUST NOT set `ack_requested`. Payloads MUST NOT carry spend authority,
such as spending keys or ZIP 324 URIs. [^zip-0324]

## Mailboxes

A Mailbox ID is $\mathsf{PointBytes}(G) \,||\, \mathsf{PointBytes}(P)$, where
$P = [a]\,G$ for a scalar $a$ that authorizes fetching. A derivation below
that yields $\mathcal{O}_{\mathbb{P}}$ for $G$ or $P$ defines no mailbox.

The **Contact Mailbox** of a Receiver has

$\hspace{2em}r = \mathsf{Scalar}(\texttt{"Zcash\_WMsgMbxOrc"}, \mathsf{rcv}), \quad G = [r]\,\mathsf{g_d}, \quad P = [r]\,\mathsf{pk_d}$

so $a = \mathsf{ivk}$.

The **Pairwise Mailbox** of a Conversation for direction $\delta$ and epoch
$e$ has, with $m = \kappa \,||\, [\delta] \,||\, \mathsf{I2LEOSP}_{32}(e)$,

$\hspace{2em}G = \mathsf{GroupHash}^{\mathbb{P}}(\texttt{"z.cash:WalletMsg-pair"}, m), \quad a = \mathsf{Scalar}(\texttt{"Zcash\_WMsgPairX\_"}, m), \quad P = [a]\,G$

The epoch at time $t$ is $\mathsf{floor}(t / 168)$.

A Server List entry is a 32-byte `server_id` and, for each network the server
is on, an address in the format of that network's Routing Binding. The
Mailbox Server of a Mailbox ID $\mathsf{id}$ is the entry with the smallest
$\mathsf{BLAKE2b\text{-}256}(\texttt{"Zcash\_WMsgSrvSel"}, \mathtt{server\_id} \,||\, \mathsf{id})$,
compared as a byte string. The Server List itself is not yet specified; see
[Open issues](#open-issues).

## Conversations

A first Envelope is deposited in the Contact Mailbox of the Receiver it is
encrypted to. In the Conversation it starts:

- An Envelope is deposited in the Pairwise Mailbox of its sender's direction
  and of the epoch in which it is deposited.
- The responder fetches the Pairwise Mailboxes for $\delta = 0$ from the
  moment it first sends an Envelope.
- The initiator fetches the Pairwise Mailboxes for $\delta = 1$ for as long
  as it wants an answer. It MUST NOT send another Envelope in the
  Conversation until it has received one; until then, anything further it
  sends is another first Envelope.
- A wallet fetches the mailbox of the current epoch, and that of an ended
  epoch until it has fetched it at least 24 hours after the epoch ended.

Each Conversation costs the responder a fetch schedule, so a wallet SHOULD
NOT answer a first Envelope, even with an Ack, without the user's approval.
Either wallet MAY forget a Conversation at any time; the other is not told.

## Mailbox Servers

| Request | Fields                                                                  | Response                        |
|---------|-------------------------------------------------------------------------|---------------------------------|
| Deposit | $[1]$, `mailbox_id`, an Envelope                                        | None                            |
| Fetch   | $[2]$, `mailbox_id`, `after` (`u64`), `time` (`u32`), `sig` (`byte[64]`) | (`seq` (`u64`), `len` (`u32`), Envelope) triples |

The server gives each deposited Envelope a nonzero `seq` greater than any it
has ever given under that Mailbox ID. Fetch returns, in order, the Envelopes with
`seq` greater than `after`, up to a size of the server's choosing, and allows
the server to delete those with `seq` up to `after`. The server MAY also
discard Envelopes after a retention period of its choosing.

`sig` is a RedPallas signature [^protocol-reddsa] with generator $G$ in place
of the fixed one, signing key $a$, and validating key $P$, over `server_id`
followed by the request without `sig`. The wallet SHOULD make the signature's
random input $T$ depend on $a$ as well as on fresh randomness, since a
repeated or predictable $T$ reveals $a$.

The server MUST drop a request, without responding, if it is malformed, including
when either half of `mailbox_id` is not the encoding of a Pallas point other
than $\mathcal{O}_{\mathbb{P}}$, or, for Fetch, if `time` is not within an hour of the server's clock or `sig`
does not validate. It MUST NOT distinguish a mailbox it holds nothing for
from an empty one.

## Routing

A Routing Binding carries requests to Mailbox Servers and responses back. It
MUST:

- hide the wallet's network identity from the server and from everyone but
  the wallet's own entry point to the network;
- keep requests and responses confidential and authentic between the wallet
  and the server;
- provide *sessions* such that neither the server nor a network observer can
  tell whether two requests in different sessions come from one wallet.

Its specification states the server address format, the framing of requests,
responses, and Envelopes sent in fast mode, what a session is, and what each
party can observe.

A wallet MUST use a new session for each Deposit, and MUST NOT use one
session for two Mailbox IDs. It MUST NOT bypass the anonymity network when it
is unavailable.

### Fast mode [fast-mode]

A Routing Binding MAY define addresses at which a wallet can receive
Envelopes directly for a limited time without revealing its network identity
to the sender. `fast_reply`, if not empty, is:

| Field         | Type     | Description                               |
|---------------|----------|-------------------------------------------|
| `network_id`  | `byte`   | Identifies the Routing Binding            |
| `valid_until` | `u32`    | Time from which the address is not used   |
| `address`     | `byte[]` | As specified by the Routing Binding       |

A wallet MUST create a new address for each `fast_reply` and use it for
nothing else, so that neither its host nor the other wallet can tie it to a
Zcash address or to another `fast_reply`.

A wallet that answers an Envelope with a `fast_reply` MAY, before
`valid_until` and as well as depositing its answer, send the same Envelope to
`address` from a session used for nothing else.

## Wallet behaviour

- Wallets SHOULD fetch each mailbox on its own randomized schedule,
  independent of user actions and of their other mailboxes, and SHOULD set
  `after` to the last `seq` they received, or to $0$.
- Wallets SHOULD delay Acks, and deposits that are not part of an interactive
  exchange, by a random amount, in particular relative to a related on-chain
  broadcast. They SHOULD send an Ack only when `ack_requested` is set.
- Wallets MUST NOT present a message as coming from a named party.
- Wallets SHOULD NOT fetch the Contact Mailboxes of an account whose incoming
  viewing key they have exported, and SHOULD give out addresses of another
  account for messaging instead. If they do fetch them, they SHOULD tell the
  user that the holder of the key can read and delete the account's messages
  and send messages in its Conversations.


# Rationale

**Why reuse the Orchard keys?** Any address with an Orchard Receiver is
already a public encryption key, so first contact needs nothing new. The cost
is the power it gives incoming viewing key holders.

**Why derive the mailbox instead of advertising it?** Advertising it would
need a ZIP 316 Metadata Item, lengthen addresses, and allow one mailbox to be
put in two addresses, linking them. Derivation gives every diversified
address its own mailbox. In exchange, senders cannot tell whether a recipient
reads messages, wallets have to agree on a Server List, and fetching has to
be authorized by a key the wallet already has.

**Why is a Mailbox ID a pair of points?** It lets a server verify knowledge
of $\mathsf{ivk}$ without having been told anything by the recipient, and
without the fetcher revealing its Receiver. Under the Decisional
Diffie–Hellman assumption the pair cannot be linked to the Receiver or to
the mailbox of another address with the same $\mathsf{ivk}$; neither can the
signatures.

**Why is $\mathsf{epk}$ checked?** For the reason given in ZIP 212:
[^zip-0212] an Envelope encrypted to one address also decrypts under any
other address with the same $\mathsf{ivk}$, so without the check a sender
could deposit an Envelope made for one address in the mailbox of another and
learn from a reaction that they belong to one wallet. The check also ties
$\kappa$ to a single Receiver.

**Why Conversations?** A Contact Mailbox gives its server a record of
everything sent to an address. Pairwise Mailboxes move an ongoing exchange to
identifiers that change weekly, and they give the recipient a way to answer
without the sender disclosing an address. Shorter epochs would leak less but
cost a returning wallet one fetch per missed epoch and Conversation.

**Why is there no Delete request?** Deleting on the next fetch puts a random
delay between reading an Envelope and its disappearance, which the sender in
a Conversation can observe.

**Why separate routing from mailboxes?** A party that stores messages for a
wallet's address and also sees the wallet's IP address, as a Nym gateway
named in an address would, can link the two. Here the server that stores
Envelopes never sees an IP address, and the entry point that sees one never
learns a Mailbox ID. It also means wallets on different networks can exchange
messages, and the protocol outlives any one network.

**Why fixed sizes?** Exact lengths would leak payload types.

**Why no ZIP 324 payload?** A sender on this channel already holds the
recipient's address and can pay it, and a ZIP 324 URI carries spend authority
that every incoming viewing key holder could use.


# Reference implementation

None yet.


# Open issues [open-issues]

- The Server List: encoding, maintenance, distribution, authentication,
  handling of changes, and whether one network is mandatory to implement.
- Who runs Mailbox Servers and what pays for them; quotas, retention, and
  whether Deposit should carry a payment or proof of work.
- Whether an opt-in signal is needed after all.
- Whether Conversations should add an ephemeral key exchange in their first
  two Envelopes. That would give forward secrecy and shut out a viewing key
  holder who only reads, though not one who answers a first Envelope before
  the wallet does. First Envelopes cannot be protected without publishing a
  separate messaging key, for which an address has no place.
- Whether Fetch needs a way to skip large Envelopes.
- Sapling-only recipients.
- Payload types for FROST round messages, with their authentication, and for
  off-chain note delivery.


# Appendix A: Routing Bindings (non-normative)

These sketches exist so that the protocol can be evaluated against real
networks. Items marked TBD have to be resolved before either is normative.

## Nym mixnet

`network_id` $1$.

- **Server address.** The 96-byte Nym client address [^nym-addressing] of a
  client run by the server.
- **Sessions.** A Nym client with fresh keys. Each has to register with an
  entry gateway and hold bandwidth credentials; the cost and latency per
  request, and who pays, are TBD.
- **Framing.** A request is one Nym message. Fetch attaches reply SURBs
  [^nym-surbs] for the response; how many, and how the server asks for more,
  is TBD.
- **Fast mode.** `address` is the 96-byte address of a client created for
  the purpose, with an independently chosen gateway; an Envelope is one Nym
  message. Its gateway holds messages while the client is offline, for
  24 hours by default, [^nym-gateway-retention] which bounds `valid_until`.
- **Observability.** A wallet's entry gateway sees its IP address and traffic
  volume but not the destination. Mixing delays and
  cover traffic hinder a global passive adversary. Larger Envelopes take more
  packets.

## Tor

`network_id` $2$.

- **Server address.** The 32-byte public key of a version 3 onion service.
  [^tor-rend] The port is TBD.
- **Sessions.** A connection over a circuit shared with no other session.
- **Framing.** One request per connection, with request and response each
  preceded by a `u32` length (TBD).
- **Observability.** A wallet's guard sees its IP address and traffic timing.
  Tor adds no delays or cover traffic, so a global passive adversary can
  correlate a wallet's traffic with requests arriving at a server.


# References

[^BCP14]: [Information on BCP 14 — "RFC 2119: Key words for use in RFCs to Indicate Requirement Levels" and "RFC 8174: Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words"](https://www.rfc-editor.org/info/bcp14)

[^protocol-orchardkeycomponents]: [Zcash Protocol Specification, Version 2026.8.0 [NU6.3]. Section 4.2.3: Orchard Key Components](protocol/protocol.pdf#orchardkeycomponents)

[^protocol-endian]: [Zcash Protocol Specification, Version 2026.8.0 [NU6.3]. Section 5.1: Integers, Bit Sequences, and Endianness](protocol/protocol.pdf#endian)

[^protocol-blake2]: [Zcash Protocol Specification, Version 2026.8.0 [NU6.3]. Section 5.4.1.2: BLAKE2 Hash Functions](protocol/protocol.pdf#concreteblake2)

[^protocol-diversifyhash]: [Zcash Protocol Specification, Version 2026.8.0 [NU6.3]. Section 5.4.1.6: DiversifyHash^Sapling and DiversifyHash^Orchard Hash Functions](protocol/protocol.pdf#concretediversifyhash)

[^protocol-sym]: [Zcash Protocol Specification, Version 2026.8.0 [NU6.3]. Section 5.4.3: Symmetric Encryption](protocol/protocol.pdf#concretesym)

[^protocol-reddsa]: [Zcash Protocol Specification, Version 2026.8.0 [NU6.3]. Section 5.4.7: RedDSA, RedJubjub, and RedPallas](protocol/protocol.pdf#concretereddsa)

[^protocol-pallasandvesta]: [Zcash Protocol Specification, Version 2026.8.0 [NU6.3]. Section 5.4.9.6: Pallas and Vesta](protocol/protocol.pdf#pallasandvesta)

[^protocol-grouphash]: [Zcash Protocol Specification, Version 2026.8.0 [NU6.3]. Section 5.4.9.8: Group Hash into Pallas and Vesta](protocol/protocol.pdf#concretegrouphashpallasandvesta)

[^protocol-orchardaddrencoding]: [Zcash Protocol Specification, Version 2026.8.0 [NU6.3]. Section 5.6.4.2: Orchard Raw Payment Addresses](protocol/protocol.pdf#orchardpaymentaddrencoding)

[^zip-0212]: [ZIP 212: Allow Recipient to Derive Ephemeral Secret from Note Plaintext](zip-0212.rst)

[^zip-0231]: [ZIP 231: Memo Bundles](zip-0231.md)

[^zip-0312]: [ZIP 312: FROST for Spend Authorization Multisignatures](zip-0312.rst)

[^zip-0316]: [ZIP 316: Unified Addresses and Unified Viewing Keys](zip-0316.rst)

[^zip-0321]: [ZIP 321: Payment Request URIs](zip-0321.rst)

[^zip-0324]: [ZIP 324: URI-Encapsulated Payments](zip-0324.rst)

[^pczt]: [Partially Created Zcash Transactions (librustzcash `pczt` crate)](https://github.com/zcash/librustzcash/tree/main/pczt)

[^zips-629]: [zips#629: Scalability Design Explorations around changing Payment Flows](https://github.com/zcash/zips/issues/629)

[^hornby-2020]: [Taylor Hornby, "Fixing Privacy Problems in the Zcash Light Wallet Protocol" (2020)](https://defuse.ca/downloads/Fixing%20Privacy%20Problems%20in%20the%20Zcash%20Light%20Wallet%20Protocol.pdf)

[^tachyon]: [Sean Bowe and Ian Miers, "A Note on Notes: Towards Scalable Anonymous Payments via Evolving Nullifiers and Oblivious Synchronization", IACR ePrint 2025/2031](https://eprint.iacr.org/2025/2031)

[^tachyon-post]: [Sean Bowe, "Tachyon: Scaling Zcash with Oblivious Synchronization" (Zcash Community Forum thread)](https://forum.zcashcommunity.com/t/scaling-zcash-tachyon-ragu/50789)

[^nym]: [Nym documentation](https://nym.com/docs)

[^nym-addressing]: [Nym documentation: Addressing System](https://nym.com/docs/network/reference/addressing)

[^nym-surbs]: [Nym documentation: Anonymous Replies (SURBs)](https://nym.com/docs/network/mixnet-mode/anonymous-replies)

[^nym-gateway-retention]: [`nym-node` source: `StaleMessageDebug::DEFAULT_STALE_MESSAGES_MAX_AGE` in `config/gateway_tasks.rs`](https://github.com/nymtech/nym/blob/develop/nym-node/src/config/gateway_tasks.rs)

[^nym-zcash]: [Nym × Zcash Integration Guide](https://zcash-sdk.nym.com/)

[^tor-rend]: [Tor Rendezvous Specification - Version 3](https://spec.torproject.org/rend-spec/)
