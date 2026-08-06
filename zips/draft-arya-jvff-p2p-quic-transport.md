    ZIP: XXX
    Title: Version 2 Zcash P2P Network Protocol
    Owners: Arya <arya@zfnd.org>
            Janito <janito@zfnd.org>
    Status: Draft
    Category: Network
    Created: 2026-07-31
    License: MIT
    Discussions-To: <https://github.com/zcash/zips/issues/352>


# Terminology

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", "MAY", and
"RECOMMENDED" in this document are to be interpreted as described in BCP 14
[^BCP14] when, and only when, they appear in all capitals.

The terms "Mainnet" and "Testnet" are to be interpreted as described in
section 3.12 of the Zcash Protocol Specification. [^protocol-networks]

The term "network upgrade" is to be interpreted as described in ZIP 200.
[^zip-0200]

The term "block chain" in this document is to be interpreted as described in
section 3.3 of the Zcash Protocol Specification. [^protocol-blockchain]

The term "legacy protocol" in this document refers to the Zcash P2P network
protocol specified in ZIP 204 [^zip-0204].

peer
:   A network node that participates in the Zcash P2P protocol by maintaining
    connections to other peers over one or more supported transports and
    exchanging protocol data over streams.

transport
:   A concrete mechanism, such as QUIC [^rfc9000] or Tor onion services
    [^tor-rend-spec], that carries connections between peers and provides the
    stream layer of this protocol (see [Stream Layer](#streamlayer) and
    [Transports](#transports)).

connection
:   A session between two peers over a supported transport, over which P2P
    streams are exchanged.

initiator
:   The peer that initiated a connection (the transport-level client).

responder
:   The peer that accepted a connection (the transport-level server). In the
    context of a single request stream, *responder* instead denotes the peer
    serving the request, irrespective of which peer accepted the connection
    (see [Request Streams](#requeststreams)); which sense is meant is
    indicated by context.

requester
:   The peer that opened a request stream and sends the request on it. Either
    the initiator or the responder of a connection may be the requester on a
    given request stream.

stream
:   An ordered, reliable byte stream within a connection, provided by the
    transport. Streams are typed by their first byte (see
    [Stream Layer](#streamlayer)).

request stream
:   A bidirectional stream carrying a single request and its response.

announcement stream
:   A long-lived unidirectional stream carrying unsolicited announcements
    (blocks, transactions, or peer addresses).

record
:   A length-delimited unit of data on an announcement or handshake stream.

protocol version
:   A 32-bit integer identifying the set of protocol features supported by a
    node. Higher values indicate support for more recent features.


# Abstract

This ZIP specifies version 2 of the Zcash peer-to-peer network protocol, a
successor to the protocol specified in ZIP 204 [^zip-0204]. It specifies the
protocol's transport-neutral stream layer, the QUIC and Tor transports that
realize it, the connection handshake, stream and record types, and relay
behavior, and is intended to be sufficient for an implementor to build a
conformant Zcash network peer.


# Motivation

ZIP 204 [^zip-0204] specifies the current Zcash P2P network protocol, whose
message-passing architecture is inherited from Bitcoin: a single unencrypted TCP
bytestream carrying framed messages with implicit correlation between requests
and responses. This ZIP proposes a successor protocol that replaces that
architecture with multiplexed streams carried over an arbitrary transport that
provides a secure channel between peers and a means of identifying the network
and addressing peers. The protocol is specified against that abstract transport
interface; this ZIP defines two concrete transports, one based on QUIC
[^rfc9000] and one carried over Tor onion services [^tor-rend-spec]. The
motivations for this change are:

- **Transport security.** The legacy transport was unencrypted and
  unauthenticated, exposing all P2P traffic to passive network observers. Every
  transport of this protocol provides an encrypted channel: the QUIC transport
  integrates TLS 1.3 [^rfc8446] [^rfc9001], and the Tor transport inherits the
  encryption of onion service connections. (Bitcoin addressed the same gap with
  a bespoke encrypted transport, BIP 324 [^bip-0324]; this protocol provides
  equivalent protection using standardized protocols.)

- **Multiplexing without head-of-line blocking.** On the legacy transport, a
  single 2 MiB `block` message stalled all other traffic on the connection.
  Streams allow concurrent block downloads, transaction relay, and control
  traffic to proceed independently — on the QUIC transport, at both the
  application and packet-loss level.

- **Explicit request correlation.** Legacy responses (`block`, `tx`, `headers`,
  `notfound`) carried no request identifiers, forcing implementations to
  correlate them heuristically. In this protocol, each request occupies its own
  stream, so correlation, cancellation, and per-request timeouts are
  structural.

- **Simplification.** Transport-level mechanisms that the legacy protocol
  carried in the application layer — payload checksums, network magic,
  keep-alives and latency measurement, flow control — are provided by the
  transport and are deleted from the application protocol.

No backwards compatibility with the legacy protocol is provided; this ZIP
replaces it entirely. See [Deployment](#deployment).

This ZIP does not specify the encoding of transactions and block headers; for
those, refer to the Zcash Protocol Specification [^protocol-txnencoding]
[^protocol-blockheader]. The encoding of a whole block in terms of its header
and transactions is part of the peer-to-peer protocol rather than the
consensus protocol [^protocol-blockheader], and is specified in
[Serialized Blocks](#serializedblocks).


# Changes from the Legacy Protocol

This section is non-normative. Relative to the legacy protocol specified in
ZIP 204 [^zip-0204], this ZIP:

- Replaces network magic bytes with transport-level network identification (for
  the QUIC transport, ALPN protocol identifiers; for the Tor transport, an
  in-band network identifier; see [QUIC Transport](#quictransport) and
  [Tor Transport](#tortransport)).
- Removes per-message headers entirely: the 12-byte command string is replaced
  by a 1-byte stream type, and the length and `SHA-256d` checksum fields are
  subsumed by QUIC framing and authenticated encryption.
- Replaces the `version`/`verack` handshake with a single `init` record
  exchange on a dedicated handshake stream (see
  [Connection Handshake](#connectionhandshake)). The `timestamp`, `addr_recv`,
  and `addr_from` fields are removed.
- Removes `ping` and `pong`; QUIC provides keep-alives and RTT measurement.
- Removes `reject`; QUIC application error codes are used instead (see
  [Application Error Codes](#applicationerrorcodes)).
- Removes `inv`, `getdata`, and `notfound`; announcements are carried on
  dedicated unidirectional streams, and object requests carry per-item results.
- Removes the inventory-walk `getblocks` message; headers-first
  synchronization is the baseline synchronization method, and a new
  `get-hashes` request stream supports checkpoint-based synchronization
  strategies (see [`get-hashes`](#get-hashes) and [^draft-sync]).
- Removes the deprecated `alert` message.
- Removes BIP 37 Bloom filtering (`filterload`, `filteradd`, `filterclear`)
  and the `NODE_BLOOM` service flag.
- Removes the legacy `addr` message and `CAddress`/`CService` encodings; the
  `addrv2` address encoding of ZIP 155 [^zip-0155] is the only address format.
- Retains divided block relay — header-based block announcement and compact
  block relay — recast onto announcement streams and request streams, with a
  block's coinbase transaction and transaction IDs additionally available in
  `get-headers` responses (see [Block Relay](#blockrelay)).


# Specification

## Network Parameters

### Networks

There are three Zcash networks: Mainnet, Testnet, and Regtest. Every connection
is bound to exactly one network, determined during connection establishment as
each transport defines (see [Transports](#transports)); this replaces the
network magic bytes of the legacy protocol.

### DNS Seeds

The DNS seed hostnames used for initial peer discovery on each network are
those listed in ZIP 204 [^zip-0204-dnsseeds]. Regtest does not use DNS seeds
or hardcoded seed nodes.


## Peer Discovery

A node discovers peers through the following mechanisms:

1. **Persisted addresses.** A node SHOULD persist the peer addresses it learns
   (see [Address Relay](#addressrelay)) across restarts, and on startup SHOULD
   attempt connections to previously learned addresses before consulting
   seeds.

2. **DNS seeding.** When the node has no usable persisted addresses — on first
   start, or when too few persisted addresses yield successful connections —
   it queries the DNS seed hostnames listed above for A and AAAA records, and
   attempts connections to the resulting addresses on the default port of the
   QUIC transport.

3. **Hardcoded seed nodes.** If DNS seeding fails or is insufficient, the node
   MAY fall back to a compiled-in list of seed node addresses. DNS seeding is
   preferred over hardcoded seed nodes.

4. **Address relay.** Connected peers exchange address information using
   `get-addr` request streams and address announcement streams (see
   [`get-addr`](#get-addr) and
   [Address Announcements](#addressannouncements)). This mechanism operates
   independently of the above.

DNS seeding yields IP addresses only, and so bootstraps only IP-based
transports such as QUIC. Addresses of peers reachable over overlay transports —
such as the `TORV3` addresses of the Tor transport (see
[Tor Transport](#tortransport)) — are learned through address relay or provided
by local configuration.


## Transports

The protocol semantics in this document are defined against the abstract stream
layer of [Stream Layer](#streamlayer). A *transport* is a concrete mechanism
that carries connections between peers and realizes that stream layer. This ZIP
defines two transports: one based on QUIC (see
[QUIC Transport](#quictransport)), and one carried over Tor onion services (see
[Tor Transport](#tortransport)). Future revisions may define additional
transports — a transport carrying the stream layer over the Nym mixnet is
anticipated (see [Deployment](#deployment)) — and a node MAY support several
transports simultaneously. The protocol semantics on a connection are identical
regardless of its transport.

Every transport MUST provide:

- a secure channel between the two peers: confidentiality and integrity for
  all application data;
- identification of the network (see [Networks](#networks)) during connection
  establishment, such that a connection between peers on different networks
  fails before any application data is exchanged;
- a form of address by which peers reachable over the transport are identified,
  encodable as a network address record (see
  [Network Address Record](#networkaddressrecord));
- the stream operations and guarantees of
  [Transport Requirements](#transportrequirements).

### Connection Management

The transport provides keep-alives and round-trip time measurement; the legacy
`ping`/`pong` messages have no equivalent in this protocol.

- A node SHOULD use an idle timeout of at least 120 seconds, and SHOULD use the
  transport's keep-alive mechanism to keep connections it wishes to retain from
  idling out. The specific values are implementation-defined.
- A node SHOULD close a connection on which the application handshake (see
  [Connection Handshake](#connectionhandshake)) has not completed within a
  reasonable time after the transport connection is established. The specific
  timeout is implementation-defined; values between 3 and 60 seconds were used
  by legacy implementations.
- Per-request timeouts are implementation-defined and are applied per stream
  (see [Request Streams](#requeststreams)).

The specific connection limits are implementation-defined; the legacy
reference values in ZIP 204 [^zip-0204] remain reasonable defaults.

A node SHOULD maintain at most one connection to a given remote address, and
MUST detect connections to itself via the handshake nonce (see
[Init Record](#initrecord)).

### QUIC Transport

The QUIC transport uses QUIC version 1 [^rfc9000] over UDP, secured with
TLS 1.3 [^rfc8446] as specified by RFC 9001 [^rfc9001].

- A node MUST NOT use 0-RTT (early data), and a responder MUST NOT enable the
  acceptance of early data. If a peer nevertheless attempts to use 0-RTT, the
  node MUST close the connection with the `PROTOCOL_ERROR` error code. (0-RTT
  data is replayable by an attacker.)
- QUIC datagrams [^rfc9221] are not used by this protocol. A node MUST ignore
  the peer's `max_datagram_frame_size` transport parameter and MUST NOT send
  DATAGRAM frames.
- A node MAY support connection migration as specified in RFC 9000. Migration
  links the node's traffic across the old and new network paths; a node for
  which that linkage is a privacy concern SHOULD establish a fresh connection
  instead of migrating.
- The address validation and amplification limits of RFC 9000 (including Retry
  packets) apply; a responder under load SHOULD use Retry to validate client
  addresses before committing state.
- QUIC's loss recovery provides round-trip time measurement, and QUIC PING
  frames provide keep-alives. A node using the QUIC transport SHOULD advertise
  a `max_idle_timeout` transport parameter consistent with the idle timeout of
  [Connection Management](#connectionmanagement).

#### Network Identification

The network of a QUIC connection is identified by an Application-Layer Protocol
Negotiation (ALPN) [^rfc7301] protocol identifier, negotiated in the QUIC-TLS
handshake:

| Network | ALPN Identifier |
|---------|-----------------|
| Mainnet | `zcash/main`    |
| Testnet | `zcash/test`    |
| Regtest | `zcash/regtest` |

A node MUST offer exactly the ALPN identifier of the network it operates on,
and MUST NOT complete a connection on which ALPN negotiation did not select
that identifier.

Incompatible future revisions of this transport will be assigned new ALPN
identifiers.

#### Default Ports

The QUIC transport uses the following default UDP port numbers, unchanged from
the legacy protocol:

| Network | Default Port |
|---------|--------------|
| Mainnet | 8233         |
| Testnet | 18233        |
| Regtest | 18344        |

#### Certificates

Connections are encrypted but endpoints are not authenticated: the goal is
protection against passive network observers, not endpoint identity.

- A node presents a self-signed X.509 certificate, or a raw public key
  [^rfc7250], for an Ed25519 or ECDSA P-256 key. The key MAY be ephemeral or
  persistent, at the node's option; a node concerned about cross-connection
  linkability SHOULD use per-connection ephemeral keys.
- A node MUST be prepared to accept both certificate encodings (X.509 and raw
  public key) and both key types from its peer.
- A node MUST NOT require the peer's certificate to chain to any certification
  authority, and MUST NOT reject a connection on the basis of certificate
  contents (subject names, expiry, or extensions).
- Client certificates are not requested: the responder MUST NOT require TLS
  client authentication.

#### Stream Layer Mapping

The abstract stream layer of [Transport Requirements](#transportrequirements)
maps onto QUIC as follows:

| Stream layer concept                             | QUIC realization                                                          |
|--------------------------------------------------|---------------------------------------------------------------------------|
| Bidirectional / unidirectional stream            | QUIC bidirectional / unidirectional streams.                              |
| Finishing a stream direction                     | A STREAM frame with the FIN bit.                                          |
| Resetting a stream with an error code            | `RESET_STREAM` carrying the application error code.                       |
| Cancelling a peer's sending with an error code   | `STOP_SENDING` carrying the application error code.                       |
| Closing the connection with an error code        | `CONNECTION_CLOSE` (application variant) carrying the application error code. |
| Per-stream backpressure                          | QUIC stream and connection flow control.                                  |
| Stream concurrency limits                        | `initial_max_streams_bidi`, `initial_max_streams_uni`, and `MAX_STREAMS` frames. |
| Keep-alive                                       | QUIC PING frames.                                                         |

### Tor Transport

The Tor transport carries connections over the Tor network [^tor] as
connections to version 3 onion services [^tor-rend-spec]. It serves traffic for
which the metadata protection of onion routing outweighs its latency cost (see
[Deployment](#deployment) and
[Security and Privacy Considerations](#securityandprivacyconsiderations)), and
allows a node to participate in the network without exposing an IP address.

- A node that accepts inbound connections over this transport runs a version 3
  onion service and advertises its address as a `TORV3` network address record
  (see [Network Address Record](#networkaddressrecord)); the record's `port`
  field is the onion service virtual port, which SHOULD be the default port of
  the network (see [Default Ports](#defaultports)).
- The initiator connects to the responder's onion service through the Tor
  network. The initiator needs no onion service of its own and is anonymous to
  the responder.
- The secure channel is provided by Tor itself: onion service connections are
  end-to-end encrypted, and the connection is authenticated to the responder's
  onion address (the Ed25519 key that the `TORV3` address encodes). TLS is not
  used inside the connection, and the initiator is deliberately not
  authenticated (cf. [Certificates](#certificates)).
- The transport provides a single ordered bytestream per connection; the
  stream layer is realized on top of it by the framing layer of
  [Stream Framing](#streamframing).

*Note:* The underlying Tor connection is a single TCP-like bytestream, so loss
or congestion on it stalls all streams of the connection; the framing layer
removes head-of-line blocking between streams at the application level only
(see [Deployment](#deployment) for transport selection).

#### Connection Preamble

Immediately after the connection is established, each peer sends a *preamble*,
before any frames:

| Size   | Field                      | Description                                                          |
|--------|----------------------------|----------------------------------------------------------------------|
| varies | `network`                  | Network identifier string (CompactSize-prefixed; see below).         |
| varies | `initial_max_data`         | Initial connection-level flow control credit in bytes (CompactSize). |
| varies | `initial_max_stream_data`  | Initial per-stream flow control credit in bytes (CompactSize).       |
| varies | `initial_max_streams_bidi` | Initial limit on the peer's concurrent bidirectional streams (CompactSize). |
| varies | `initial_max_streams_uni`  | Initial limit on the peer's concurrent unidirectional streams (CompactSize). |

The `network` string is the identifier of the node's network, using the same
values as the QUIC transport's ALPN identifiers (see
[Network Identification](#networkidentification)): `zcash/main`, `zcash/test`,
or `zcash/regtest`. A node MUST close the connection if the peer's `network`
string differs from its own; this replaces ALPN-based network identification,
which is unavailable without TLS.

The flow control fields play the role of the corresponding QUIC transport
parameters: they are the initial credit available to the *peer* for the
corresponding limit (see [Stream Framing](#streamframing)). A node MUST allow
an `initial_max_stream_data` of at least 2,228,224 bytes (the maximum record
payload length plus framing headroom), and SHOULD allow the stream concurrency
minimums of [Transport Requirements](#transportrequirements).

Incompatible future revisions of this transport will be assigned new network
identifier strings.

#### Stream Framing

The stream layer is realized over the connection's ordered bytestream by a
framing layer whose stream semantics — stream states, flow control, and error
signalling — are modeled on those of QUIC [^rfc9000].

Stream IDs are integers. The two least significant bits of a stream ID encode
its kind, as in QUIC: `0x0` initiator-opened bidirectional, `0x1`
responder-opened bidirectional, `0x2` initiator-opened unidirectional, `0x3`
responder-opened unidirectional. Successive streams of each kind are opened
with sequentially increasing stream IDs; a stream is opened implicitly by the
first frame that its opener sends referencing its ID.

Each frame is a 1-byte frame type followed by type-dependent fields. Integer
fields, including stream IDs, are CompactSize-encoded.

| Type   | Frame              | Fields                              | Semantics                                                                     |
|--------|--------------------|-------------------------------------|-------------------------------------------------------------------------------|
| `0x00` | `PING`             | 8-byte opaque value                 | Keep-alive and RTT measurement; the receiver MUST respond with `PONG`.        |
| `0x01` | `PONG`             | 8-byte echoed value                 | Response to `PING`.                                                           |
| `0x02` | `STREAM`           | stream ID, flags (1 byte), length, data | Appends `data` to the stream. Flag bit 0 (`FIN`) finishes the sender's direction of the stream. |
| `0x03` | `RESET_STREAM`     | stream ID, error code               | Resets the sender's direction of the stream (see [Transport Requirements](#transportrequirements)). |
| `0x04` | `STOP_SENDING`     | stream ID, error code               | Requests that the peer stop sending on the stream.                            |
| `0x05` | `MAX_DATA`         | maximum                             | Raises the connection-level flow control limit (cumulative bytes of stream data). |
| `0x06` | `MAX_STREAM_DATA`  | stream ID, maximum                  | Raises the flow control limit of one stream (cumulative bytes).               |
| `0x07` | `MAX_STREAMS_BIDI` | count                               | Raises the limit on the peer's cumulative count of opened bidirectional streams. |
| `0x08` | `MAX_STREAMS_UNI`  | count                               | Raises the limit on the peer's cumulative count of opened unidirectional streams. |
| `0x09` | `CLOSE`            | error code                          | Closes the connection with an application error code; the sender then closes the underlying connection. |

Flow control limits are cumulative, as in QUIC: a limit counts total bytes
sent on a stream (respectively, on all streams; respectively, total streams
opened) since the beginning of the connection, and each `MAX_*` frame
communicates a new absolute limit. Limits never decrease; a `MAX_*` frame with
a lower value than a previously communicated limit is ignored. A node MUST NOT
exceed a limit communicated by its peer; a peer that does so is a connection
error of type `PROTOCOL_ERROR` (equally, a frame that is malformed or has an
unrecognized frame type).

The `length` of a `STREAM` frame MUST NOT exceed 65,536 bytes; larger
application writes are split across multiple `STREAM` frames, allowing frames
of other streams to be interleaved between them.

The abstract stream layer maps onto this framing as follows:

| Stream layer concept                             | Framing realization                                     |
|--------------------------------------------------|---------------------------------------------------------|
| Bidirectional / unidirectional stream            | Stream ID kinds `0x0`/`0x1` and `0x2`/`0x3`.            |
| Finishing a stream direction                     | A `STREAM` frame with the `FIN` flag.                   |
| Resetting a stream with an error code            | `RESET_STREAM` carrying the application error code.     |
| Cancelling a peer's sending with an error code   | `STOP_SENDING` carrying the application error code.     |
| Closing the connection with an error code        | `CLOSE` carrying the application error code.            |
| Per-stream backpressure                          | `MAX_DATA` and `MAX_STREAM_DATA` credit.                |
| Stream concurrency limits                        | Preamble initial limits and `MAX_STREAMS_*` frames.     |
| Keep-alive                                       | `PING` frames.                                          |


## Stream Layer

All application data is carried on streams provided by the transport. The
first byte of every stream is a *stream type* that determines the format and
semantics of the remaining stream data.

### Transport Requirements

The stream layer that every transport provides consists of *bidirectional*
streams (both peers can send) and *unidirectional* streams (only the opener can
send), with the following operations and guarantees:

- Either peer can **open** streams of either kind at any time. The receiver of
  a stream can tell which peer opened it and of which kind it is.
- Data written to a stream is delivered reliably and in order within that
  stream. Streams are mutually independent: delay or loss on one stream MUST
  NOT prevent delivery of data on other streams.
- A sender can **finish** its sending direction of a stream, signalling that no
  more data will be sent on it.
- A peer can **reset** a stream it is sending on, abandoning it with an
  application error code (see
  [Application Error Codes](#applicationerrorcodes)), and can **cancel** the
  peer's sending direction of a stream, requesting with an application error
  code that the peer stop sending.
- Either peer can **close** the connection with an application error code.
- The receiver of a stream can apply per-stream backpressure to bound how much
  data it must buffer.
- Each peer can bound the number of streams of each kind that the other peer
  may have concurrently open. A node SHOULD allow at least 32 concurrent
  bidirectional streams, and SHOULD allow at least 8 concurrent unidirectional
  streams (sufficient for the announcement streams plus headroom for future
  types).

How each transport realizes these operations is specified in the corresponding
transport section (for QUIC, see [Stream Layer Mapping](#streamlayermapping)).

### Stream Types

| Code   | Name                      | Kind                          | Description                                                          |
|--------|---------------------------|-------------------------------|----------------------------------------------------------------------|
| `0x00` | Handshake                 | Bidirectional, initiator only | Connection handshake and control (see [Connection Handshake](#connectionhandshake)). |
| `0x01` | `get-headers`             | Bidirectional                 | Request block headers, optionally with transaction IDs.              |
| `0x02` | `get-blocks`              | Bidirectional                 | Request full blocks.                                                 |
| `0x03` | `get-tx`                  | Bidirectional                 | Request transactions.                                                |
| `0x04` | `get-addr`                | Bidirectional                 | Request peer addresses.                                              |
| `0x05` | `get-mempool`             | Bidirectional                 | Request mempool contents.                                            |
| `0x06` | `get-hashes`              | Bidirectional                 | Request best-chain block hashes at a height stride.                  |
| `0x10` | Block announcements       | Unidirectional                | Announce new blocks (see [Block Announcements](#blockannouncements)). |
| `0x11` | Transaction announcements | Unidirectional                | Announce new transactions (see [Transaction Announcements](#transactionannouncements)). |
| `0x12` | Address announcements     | Unidirectional                | Gossip peer addresses (see [Address Announcements](#addressannouncements)). |

Stream type `0x00` and the ranges `0x01`–`0x0F` and `0x10`–`0x1F` are reserved
for the handshake, request stream types, and announcement stream types
respectively; future revisions are expected to assign new stream types from the
matching range.

To *refuse* a stream opened by its peer, a node cancels the peer's sending
direction of that stream with the applicable error code and, if the stream is
bidirectional, also resets its own sending direction with the same code;
refusing a unidirectional stream involves only the cancellation.

A node receiving a stream whose type byte it does not recognize MUST refuse
that stream with the `UNSUPPORTED_STREAM_TYPE` error code (see
[Application Error Codes](#applicationerrorcodes)) and MUST NOT treat it as a
connection error or assign a misbehavior penalty. This allows future stream
types to be deployed without version gating.

A stream that is finished by its opener before a complete type byte has been
received is a connection error of type `PROTOCOL_ERROR`.

### Request Streams

A request stream is a bidirectional stream carrying exactly one request and its
response:

1. The requester opens a bidirectional stream, writes the stream type byte
   followed by the request in the format defined for that type, and finishes
   its sending direction.
2. The responder writes the response in the format defined for that type and
   finishes its sending direction. (For a stream type that defines an
   open-ended response, the responder instead keeps its sending direction open;
   see [`get-mempool`](#get-mempool).)

Either peer may open request streams; there is no client/server asymmetry
beyond the rules stated for individual stream types.

- A responder MAY begin serving a request as soon as the request is
  syntactically complete, without waiting for the requester to finish its
  sending direction.
- A responder that cannot or will not serve a request MAY reset its sending
  direction of the stream with the `REFUSED` error code instead of sending a
  response.
- A requester that no longer needs a response SHOULD cancel the responder's
  sending direction with the `CANCELLED` error code; the responder SHOULD then
  reset the stream and abandon work on the request.
- A reset or refused request stream is never resumed or reused. A requester
  that retries a request after a reset does so by opening a new stream, and
  the next byte the requesting side sends — the first byte of that new stream
  — MUST be the stream type byte, as for any other stream.
- A node SHOULD apply an implementation-defined timeout to each outstanding
  request, cancelling the stream if the response does not complete in time.
- A node MUST NOT send more than one request on a stream. Unless the stream
  type defines an open-ended response, any data following a complete request
  or response on a stream is a connection error of type `PROTOCOL_ERROR`.
- A request or response that does not conform to the format defined for its
  stream type — including an unrecognized `result` value in a response — is a
  connection error of type `PROTOCOL_ERROR`, unless other handling is
  specified for the stream type.

A node bounds the number of concurrent requests a peer may have outstanding
using the transport's stream concurrency limits (see
[Transport Requirements](#transportrequirements)).

### Announcement Streams

An announcement stream is a long-lived unidirectional stream carrying a
sequence of records for one announcement topic.

- After the connection handshake completes, each peer SHOULD open one
  announcement stream of each type it intends to send announcements on, and
  keep it open for the life of the connection.
- A node MUST NOT open more than one announcement stream of a given type in
  the same direction at a time. A second concurrent stream of the same type is
  a connection error of type `PROTOCOL_ERROR`. If an announcement stream is
  reset or finished, the sender MAY open a replacement.
- Announcements are best-effort: if transport backpressure prevents a record
  from being written promptly, the sender MAY drop the announcement rather
  than queueing it indefinitely.

### Records

Each record on an announcement or handshake stream is encoded as a CompactSize
length prefix followed by that many bytes of payload:

| Size   | Field     | Description                                        |
|--------|-----------|----------------------------------------------------|
| varies | `length`  | Payload length in bytes (CompactSize).             |
| varies | `payload` | Record payload; format depends on the stream type. |

The maximum length of a record payload — and of any individually
length-prefixed element in a request or response, such as a serialized block —
is 2,097,152 bytes (2 MiB). A node MUST treat a length prefix exceeding this
limit as a connection error of type `FLOOD`.

A record MUST NOT be processed until it is complete. A stream that is finished
in the middle of a record is a connection error of type `PROTOCOL_ERROR`.

### Application Error Codes

The following application error codes are used when closing a connection,
resetting a stream, or cancelling a peer's sending direction (see
[Transport Requirements](#transportrequirements)):

| Code   | Constant                  | Usage                                                                                                            |
|--------|---------------------------|------------------------------------------------------------------------------------------------------------------|
| `0x00` | `NO_ERROR`                | Graceful connection close.                                                                                       |
| `0x01` | `PROTOCOL_ERROR`          | The peer violated this specification.                                                                            |
| `0x02` | `UNSUPPORTED_STREAM_TYPE` | Stream refusal: unrecognized stream type.                                                                        |
| `0x03` | `OBSOLETE`                | The peer's protocol version is below the minimum for the current network epoch (see [Network Upgrade Epoch Enforcement](#networkupgradeepochenforcement)). |
| `0x04` | `SELF_CONNECTION`         | The connection is to the node itself (see [Init Record](#initrecord)).                                           |
| `0x05` | `FLOOD`                   | The peer exceeded a size or rate limit.                                                                          |
| `0x06` | `MISBEHAVIOR`             | The peer's misbehavior score reached the ban threshold (see [Misbehavior and Banning](#misbehaviorandbanning)).  |
| `0x07` | `CANCELLED`               | Stop-sending/reset: the request is no longer wanted.                                                             |
| `0x08` | `REFUSED`                 | Stream reset: the responder declines to serve this request.                                                      |
| `0x09` | `INTERNAL_ERROR`          | The sender encountered an internal error.                                                                        |

Where this document states that an event is a *connection error* of a given
type, a node detecting that event MUST close the connection with the
corresponding error code.

A node receiving an error code it does not recognize MUST treat it as
`INTERNAL_ERROR`.


## Data Types and Encoding

All multi-byte integer types are encoded in little-endian byte order unless
otherwise specified. The integer types used in this specification (`uint8`,
`uint16`, `uint32`, `uint64`) have their conventional meanings.

### CompactSize

*Note:* The CompactSize encoding is used in the Zcash Protocol Specification
(section 7) but is not formally defined there. It is defined here for
completeness.

A variable-length unsigned integer encoding used for lengths and counts:

| Value Range                       | Encoding Size | Format                                        |
|-----------------------------------|---------------|-----------------------------------------------|
| 0 to 252                          | 1 byte        | Single byte with the value directly.          |
| 253 to 0xFFFF                     | 3 bytes       | `0xFD` followed by the value as `uint16`.     |
| 0x10000 to 0xFFFFFFFF             | 5 bytes       | `0xFE` followed by the value as `uint32`.     |
| 0x100000000 to 0xFFFFFFFFFFFFFFFF | 9 bytes       | `0xFF` followed by the value as `uint64`.     |

Encodings MUST be canonical: the shortest possible encoding MUST be used for
any given value. A node MUST reject non-canonical CompactSize encodings.

### Strings

Character strings are encoded as a CompactSize length prefix followed by that
many bytes of string data. There is no NUL terminator.

### Serialized Blocks

The Zcash Protocol Specification defines the encodings of block headers and
transactions, but leaves the encoding of a whole block to the peer-to-peer
protocol [^protocol-blockheader]. A serialized block is encoded as follows,
unchanged from the payload of the legacy `block` message:

| Size   | Field      | Description                                                                 |
|--------|------------|-----------------------------------------------------------------------------|
| varies | `header`   | The serialized block header [^protocol-blockheader] (including the Equihash solution). |
| varies | `tx_count` | Number of transactions in the block (CompactSize).                          |
| varies | `txns`     | `tx_count` serialized transactions [^protocol-txnencoding], in block order. |

### Network Address Record

Peer addresses use the `addrv2` address record specified in ZIP 155
[^zip-0155]; it is the only address encoding in this protocol. The record
fields (`time`, `services`, `networkID`, `sizeAddr`, `addr`, `port`), the
network IDs (`IPV4`, `IPV6`, `TORV3`, `I2P`, `CJDNS`), the 512-byte `addr`
limit, the per-network-ID length and encoding rules, and the prohibition on
gossiping addresses with unrecognized network IDs are all as specified in
ZIP 155.

The `port` field is interpreted per transport: for QUIC endpoints it is the
UDP port, and for `TORV3` addresses it is the onion service virtual port (see
[Tor Transport](#tortransport)). It MUST be 0 if not relevant for the
network.

*Note:* Each network ID implies the transport by which the address is
reachable: `IPV4`, `IPV6`, and `CJDNS` addresses identify QUIC endpoints, and
`TORV3` addresses identify onion services of the Tor transport. `I2P`
addresses are not reachable via either transport defined in this ZIP; they
remain defined for gossip so that nodes can learn them ahead of a future
revision that defines an I2P-capable transport.

### Transaction References

Transactions are identified in announcements and requests by *transaction
references*. Per ZIP 239 [^zip-0239], transactions with version ≥ 5 are relayed
by wtxid (the txid followed by the authorizing data commitment `auth_digest`),
and transactions with version ≤ 4 by txid. A transaction reference is encoded
as a 1-byte type followed by a type-dependent identifier:

| Type   | Name      | Total Size | Description                                                                                                     |
|--------|-----------|------------|-----------------------------------------------------------------------------------------------------------------|
| `0x01` | `TXID`    | 33 bytes   | Transaction with version ≤ 4, identified by its 32-byte txid.                                                   |
| `0x02` | `WTXID`   | 65 bytes   | Transaction with version ≥ 5, identified by its 64-byte wtxid (txid followed by `auth_digest`). See ZIP 239 [^zip-0239]. |
| `0x03` | `SHORTID` | 39 bytes   | Transaction within a specific block, identified by a 32-byte block hash followed by a 6-byte short transaction ID (see [Short Transaction IDs](#shorttransactionids)). Only valid in `get-tx` requests. |

A transaction reference with an unrecognized type is a connection error of
type `PROTOCOL_ERROR`. Using the wrong reference type for a transaction's
version is subject to a misbehavior penalty (see
[Misbehavior and Banning](#misbehaviorandbanning)).


## Service Flags

Service flags are advertised in the `services` field of `init` records and
network address records. In the table below, bit $k$ refers to the bit with
numeric weight $2^k$; that is, the `services` field has the corresponding flag
set if and only if `services & (1 << k) != 0`.

| Name           | Bit | Description                                                 |
|----------------|-----|-------------------------------------------------------------|
| `NODE_NETWORK` | 0   | The node is capable of serving the complete block chain.    |

Bits 24–31 are reserved for temporary experiments.

A node MUST ignore service bits that it does not recognize, and SHOULD
preserve them when relaying address records (see
[Address Relay](#addressrelay)).

The legacy `NODE_BLOOM` flag (bit 2) is retired along with BIP 37 Bloom
filtering, and MUST NOT be advertised.


## Connection Handshake

Peers perform an application handshake immediately after the transport
connection is established.

### Handshake Sequence

1. The initiator opens a bidirectional stream with stream type `0x00` (the
   *handshake stream*) and sends an `init` record.
2. The responder sends its own `init` record on the same stream.
3. The handshake is complete for a peer once it has both sent and received an
   `init` record. The negotiated protocol version is
   `min(local_version, remote_version)`.

The two `init` records are independent: the responder MAY send its `init`
record as soon as it observes the handshake stream's type byte, without
waiting for the initiator's `init` record to arrive.

Only the initiator may open the handshake stream, and a connection has exactly
one: a handshake stream opened by the responder, or a second handshake stream,
is a connection error of type `PROTOCOL_ERROR`.

A node MUST NOT open any other stream before it has sent its `init` record,
and MUST NOT send announcement records or requests before the handshake is
complete. A node MAY buffer streams received from a peer before the handshake
completes, or MAY refuse them with `REFUSED` (see
[Stream Types](#streamtypes)); it MUST NOT process them before the handshake
completes.

The handshake stream remains open for the life of the connection. Future
record kinds on the handshake stream may be defined by later revisions; a node
MUST ignore handshake-stream records whose kind it does not recognize.
Finishing or resetting the handshake stream signals intent to disconnect; a
node observing this SHOULD close the connection with `NO_ERROR`.

Records on the handshake stream use the encoding of [Records](#records). The
record payload begins with a 1-byte record kind; kind `0x00` is the `init`
record.

### Init Record

The `init` record payload (following the kind byte) has the following format:

| Size   | Field          | Description                                                                                              |
|--------|----------------|----------------------------------------------------------------------------------------------------------|
| 4      | `version`      | The sender's advertised protocol version (`uint32`).                                                     |
| varies | `services`     | Service flags (CompactSize-encoded `uint64`).                                                            |
| 8      | `nonce`        | Random nonce for self-connection detection (`uint64`).                                                   |
| varies | `user_agent`   | User agent string (CompactSize-prefixed, max 256 bytes).                                                 |
| 4      | `start_height` | Best block height known to the sender (`uint32`).                                                        |
| 1      | `relay`        | Whether the sender wants transaction relay (`uint8`; 0 or 1).                                            |
| 1      | `announce`     | Whether the sender requests high-bandwidth compact block announcements (`uint8`; 0 or 1). See [Compact Block Relay](#compactblockrelay). |
| 1      | `full_ids`     | Whether the sender requests full transaction IDs in compact block announcements (`uint8`; 0 or 1). See [Full Transaction IDs](#fulltransactionids). |

All fields are mandatory. The legacy `timestamp`, `addr_recv`, and `addr_from`
fields are removed.

The `nonce` field is used for self-connection detection. If a node receives an
`init` record containing a nonce it recently sent in its own `init` records,
it MUST close the connection with the `SELF_CONNECTION` error code.

If `relay` is 0, the peer MUST NOT open a transaction announcement stream to
the sender, and SHOULD NOT announce transactions to it by any other means.

There is no mechanism for changing the value of the `relay`, `announce`, or
`full_ids` fields during the life of a connection; a node that wants to
change them disconnects and performs a new handshake.

### Handshake Validation

A receiving node MUST validate the `init` record as follows:

- The `version` field MUST be at least the minimum protocol version of this
  ZIP (see [Protocol Versioning](#protocolversioning)), and at least the
  protocol version associated with the current network epoch (see
  [Network Upgrade Epoch Enforcement](#networkupgradeepochenforcement)). On
  failure, the node MUST close the connection with the `OBSOLETE` error code.
- The `nonce` MUST NOT match the local node's nonce (self-connection
  detection).
- The `user_agent` string MUST NOT exceed 256 bytes.
- The `relay`, `announce`, and `full_ids` fields MUST each be 0 or 1.
- A peer MUST NOT send more than one `init` record per connection.

Except where another error code is specified above, a node MUST close the
connection with the `PROTOCOL_ERROR` error code if any of these checks fail.


## Protocol Versioning

Protocol versions are 32-bit integers, advertised in the `version` field of
the `init` record. The *negotiated protocol version* of a connection is the
minimum of the two peers' advertised versions. The negotiated protocol version
determines whether the peer meets the minimum version requirements for the
current network epoch (see
[Network Upgrade Epoch Enforcement](#networkupgradeepochenforcement)), and
gates any features that later revisions of this protocol introduce under new
protocol versions.

Protocol versions inhabit a single numbering space shared with the legacy
protocol: a protocol version is assigned to a (network, network upgrade) pair,
not to a P2P protocol revision, and denotes the same version whether it is
advertised in a legacy `version` message or in an `init` record. The
association of protocol versions with network upgrades, and the procedure by
which future network upgrades are assigned protocol versions, are specified in
ZIP 204 [^zip-0204-assignment] and are not duplicated here.

At the time of writing, the current protocol version — advertised by nodes
implementing the legacy protocol — is 170160 (`PROTOCOL_VERSION`). The
protocol version from which the protocol specified by this ZIP is deployed has
not yet been assigned; it will be the protocol version that ZIP 204's
assignment procedure [^zip-0204-assignment] assigns to the network upgrade
that deploys this protocol (see [Deployment](#deployment)). That version is
the minimum peer protocol version of this protocol: every node implementing
this ZIP necessarily advertises at least that version, and version-gated
features of the legacy protocol (such as `MSG_WTX` relay and `addrv2` support)
are unconditionally in effect.

### Network Upgrade Epoch Enforcement

Each network upgrade defines a minimum protocol version. When a network
upgrade activates (as defined in ZIP 200 [^zip-0200]), a node MUST disconnect
any peer whose negotiated protocol version is less than the protocol version
associated with the current epoch, using the `OBSOLETE` error code.

The protocol versions associated with network upgrades on each network are
tabulated in ZIP 204 [^zip-0204-epochs].

In the preference window before an upgrade's activation, a node SHOULD
preferentially connect to peers advertising the upcoming epoch's protocol
version, as specified in ZIP 201 [^zip-0201].


## Request Stream Types

This section defines each request stream type. For each type, the request and
response formats and their semantics are specified. All requests and responses
follow the lifecycle of [Request Streams](#requeststreams).

### `get-headers`

Stream type: `0x01`

**Request:**

| Size   | Field            | Description                                                          |
|--------|------------------|----------------------------------------------------------------------|
| varies | `locator_count`  | Number of block locator hashes (CompactSize).                        |
| varies | `locator_hashes` | Block locator hashes (each 32 bytes), from highest to lowest height. |
| 32     | `hash_stop`      | Hash of the last desired header, or all zeros to request as many as possible. |
| 1      | `tx_ids`         | Whether each returned header should be accompanied by the block's coinbase transaction and transaction IDs (`uint8`; 0 or 1). |

**Response:**

| Size   | Field     | Description                                       |
|--------|-----------|---------------------------------------------------|
| varies | `count`   | Number of entries (CompactSize).                  |
| varies | `entries` | `count` entries, each encoded as follows.         |

Each entry:

| Size   | Field      | Description                                                                                        |
|--------|------------|----------------------------------------------------------------------------------------------------|
| varies | `header`   | The block header, encoded as a CompactSize length prefix followed by the serialized header [^protocol-blockheader] (including the Equihash solution). |
| 1      | `has_txs`  | Present only if the request had `tx_ids = 1`. `0x01`: the coinbase transaction and transaction IDs follow. `0x00`: nothing further follows for this entry. |
| varies | `coinbase` | Present only if `has_txs` is `0x01`: the block's coinbase transaction, encoded as a CompactSize length prefix followed by the serialized transaction [^protocol-txnencoding]. |
| varies | `ids_count`| Present only if `has_txs` is `0x01`: the number of transaction IDs (CompactSize).                  |
| varies | `ids`      | Present only if `has_txs` is `0x01`: the full transaction IDs (64 bytes each; see [Full Transaction IDs](#fulltransactionids)) of the block's transactions other than the coinbase transaction, in block order. |

Requests block headers starting after the first block locator hash found in
the responder's best chain, up to and including `hash_stop` or 160 headers
(`MAX_HEADERS_RESULTS`), whichever comes first. The `locator_count` MUST NOT
exceed 101, and `tx_ids` MUST be 0 or 1.

If none of the locator hashes are found in the responder's best chain, headers
start at height 1 (the block after the genesis block). If `locator_count` is
0, the response consists solely of the entry for the header whose hash is
`hash_stop`, if the responder has it. A response with `count = 0` is valid and
indicates that the responder has no headers to return.

If `tx_ids` is 1, each entry additionally identifies the block's transactions:
the coinbase transaction in full (it is never otherwise relayed), and every
other transaction by its full transaction ID, letting the requester fetch only
the transactions it is missing via `get-tx` (see
[Relay Protocol](#relayprotocol)). A responder that cannot supply a returned
header's transactions sets `has_txs` to `0x00` for that entry, and the
requester falls back to `get-blocks`.

A node performing bulk synchronization SHOULD set `tx_ids` to 0: the
transaction-ID form pays off only near the chain tip, where the requester
already holds most of a block's transactions.

The response `count` MUST NOT exceed 160. The headers MUST form a contiguous
chain (each header's `hashPrevBlock` must match the hash of the preceding
header). A node receiving non-contiguous headers SHOULD assign a misbehavior
penalty of 20 points.

The legacy always-zero transaction count that followed each header in
`headers` messages is removed.

### `get-blocks`

Stream type: `0x02`

**Request:**

| Size   | Field    | Description                              |
|--------|----------|------------------------------------------|
| varies | `count`  | Number of block hashes (CompactSize).    |
| varies | `hashes` | `count` block hashes (each 32 bytes).    |

**Response:** For each requested hash, in request order:

| Size   | Field    | Description                                                                                                      |
|--------|----------|------------------------------------------------------------------------------------------------------------------|
| 1      | `result` | `0x00`: a full block follows. `0x02`: not found (nothing follows for this entry).                                |
| varies | `object` | If `result` is `0x00`: a CompactSize length prefix followed by the serialized block (see [Serialized Blocks](#serializedblocks)). |

Requests full blocks by hash; the hashes to request are learned from headers,
announcements, or `get-hashes` responses. The `count` MUST NOT exceed 128.
Compact blocks cannot be requested — they occur only as announcements (see
[Compact Block Relay](#compactblockrelay)).

### `get-tx`

Stream type: `0x03`

**Request:**

| Size   | Field    | Description                                                                                                   |
|--------|----------|---------------------------------------------------------------------------------------------------------------|
| varies | `count`  | Number of transaction references (CompactSize).                                                               |
| varies | `txrefs` | `count` transaction references (see [Transaction References](#transactionreferences)). All three reference types are permitted. |

**Response:** For each requested reference, in request order:

| Size   | Field    | Description                                                                                 |
|--------|----------|---------------------------------------------------------------------------------------------|
| 1      | `result` | `0x00`: a transaction follows. `0x02`: not found (nothing follows for this entry).          |
| varies | `tx`     | If `result` is `0x00`: a CompactSize length prefix followed by the serialized transaction [^protocol-txnencoding]. |

Requests transactions by reference. The `count` MUST NOT exceed 50,000.

`SHORTID` references identify a transaction within a block relayed by a
compact block; their handling is specified in
[Requesting Missing Transactions](#requestingmissingtransactions).

### `get-addr`

Stream type: `0x04`

**Request:** Empty (the stream is finished immediately after the stream type
byte).

**Response:**

| Size   | Field       | Description                                                              |
|--------|-------------|--------------------------------------------------------------------------|
| varies | `count`     | Number of address records (CompactSize).                                 |
| varies | `addresses` | `count` network address records (see [Network Address Record](#networkaddressrecord)). |

Requests peer addresses from the remote node. The response `count` MUST NOT
exceed 1000; a node receiving a larger response SHOULD assign a misbehavior
penalty of 20 points.

To impede address-based fingerprinting attacks, a node SHOULD send `get-addr`
only on outbound connections, at most once per connection, and SHOULD only
answer `get-addr` requests on inbound connections (resetting its sending
direction of the stream with `REFUSED` otherwise).

### `get-mempool`

Stream type: `0x05`

**Request:** Empty (the stream is finished immediately after the stream type
byte).

**Response:** Open-ended. The response is a sequence of records (see
[Records](#records)), each with the following payload:

| Size   | Field    | Description                                                                                              |
|--------|----------|----------------------------------------------------------------------------------------------------------|
| varies | `count`  | Number of transaction references (CompactSize).                                                          |
| varies | `txrefs` | `count` transaction references (see [Transaction References](#transactionreferences)). `SHORTID` references MUST NOT be used. |

Subscribes to the contents of the peer's transaction memory pool. The
responder first sends one or more records that together reference every
transaction currently in its mempool (the snapshot; a single record with
`count = 0` is valid and indicates an empty mempool). It then keeps its
sending direction open, and sends further records referencing transactions as
they are accepted into its mempool, until the stream or connection ends. The
requester fetches transactions of interest with `get-tx`.

This is the one stream type whose response is open-ended (see
[Request Streams](#requeststreams)): the responder finishing its sending
direction ends the subscription (for example, on shutdown), and a requester
that no longer wants the subscription cancels the responder's sending
direction with `CANCELLED`. A node MUST NOT open more than one concurrent
`get-mempool` stream to the same peer; a second concurrent subscription is a
connection error of type `PROTOCOL_ERROR`.

Records after the snapshot SHOULD be subject to the same trickling delay as
transaction announcements (see [Trickling](#trickling)). The responder MAY
omit references it has already sent to the same peer — in the snapshot, in an
earlier record, or on a transaction announcement stream — and the requester
MUST tolerate duplicate references. A node MAY decline to serve `get-mempool`
by resetting its sending direction of the stream with `REFUSED`.

### `get-hashes`

Stream type: `0x06`

**Request:**

| Size   | Field          | Description                                                          |
|--------|----------------|----------------------------------------------------------------------|
| 4      | `start_height` | Height of the first requested block hash (`uint32`, little-endian).  |
| 4      | `stride`       | Spacing between requested heights (`uint32`, little-endian). MUST be ≥ 1. |
| varies | `count`        | Maximum number of block hashes requested (CompactSize).              |

**Response:**

| Size   | Field    | Description                                                                                                    |
|--------|----------|----------------------------------------------------------------------------------------------------------------|
| varies | `count`  | Number of block hashes returned (CompactSize).                                                                 |
| varies | `hashes` | Block hashes, 32 bytes each: the hash of the block at height `start_height + k × stride` in the responder's best chain, for `k` from 0 to `count − 1`. |

Requests the hashes of the blocks at heights `start_height + k × stride` of
the responder's best chain, for `k` from 0 to `count − 1`. Setting `stride`
to 1 requests the hashes of consecutive blocks; a larger `stride` requests
hashes at a regular spacing (for example, the spacing of the requester's
checkpoints; see [^draft-sync]). Responders serve `get-hashes` purely from
the height-to-hash index of their best chain.

The requested `count` MUST NOT exceed 50,000, `stride` MUST NOT be 0, and
the greatest requested height (`start_height + (count − 1) × stride`) MUST
NOT exceed `0xFFFFFFFF`.

The response `count` MAY be less than the requested count, and MAY be 0: a
node omits requested heights above its chain tip, and SHOULD NOT include the
hashes of blocks fewer than 100 blocks below its chain tip (which could
still be affected by a chain reorganization). Truncation MUST be a prefix:
if fewer hashes are returned than were requested, the returned hashes MUST
correspond to the lowest requested heights, so that the requester can
re-request the missing tail.

Responses are not self-authenticating: the returned hashes are only as
trustworthy as the peer that sent them. A node MUST NOT rely on them for any
security-relevant purpose without verifying them against trusted data (such
as the trusted commitments of
[Checkpointed Synchronization](#checkpointedsynchronization)) or fully
validating the corresponding blocks.


## Announcement Stream Types

### Block Announcements

Stream type: `0x10`

Each record payload on a block announcement stream has the following format:

| Size   | Field     | Description                                                                                             |
|--------|-----------|---------------------------------------------------------------------------------------------------------|
| 1      | `kind`    | `0x00`: header announcement. `0x01`: compact block announcement.                                        |
| varies | `payload` | For `kind = 0x00`: a serialized block header [^protocol-blockheader]. For `kind = 0x01`: a compact block (see [Compact Block Encoding](#compactblockencoding)). |

Blocks are announced immediately; they are not subject to the trickling delay
applied to transactions.

A node announces a new block to a given peer in one of two ways:

1. If the peer requested high-bandwidth compact block announcements (the
   `announce` field of its `init` record was 1), by sending a compact block
   announcement (`kind = 0x01`).
2. Otherwise, by sending header announcements (`kind = 0x00`) for the new
   block and for any intermediate blocks the peer has not yet been sent, up to
   a small implementation-defined limit. This follows the design of BIP 130
   [^bip-0130].

A node MUST NOT send compact block announcements to a peer whose `init`
record had `announce = 0`. Header announcements MAY be sent to any peer,
regardless of its `announce` preference; in particular, if a block's compact
block encoding would exceed the maximum record payload length (see
[Records](#records)), the sender announces that block with a header
announcement instead.

An announcing node SHOULD only announce a block if it expects the peer to be
able to connect the announced header to the peer's known chain (for example,
because the parent block was previously announced to or by that peer). A node
receiving an announcement whose header does not connect to its known chain
SHOULD recover by sending a `get-headers` request, and MUST NOT assign a
misbehavior penalty solely because a header does not connect.

### Transaction Announcements

Stream type: `0x11`

Each record payload on a transaction announcement stream is a single
transaction reference (see [Transaction References](#transactionreferences))
of type `TXID` or `WTXID`. `SHORTID` references MUST NOT be used in
announcements.

A node MUST NOT open a transaction announcement stream to a peer whose `init`
record had `relay = 0`.

Announcements are subject to the trickling delay of [Trickling](#trickling).
Interested peers fetch announced transactions with `get-tx` requests.

### Address Announcements

Stream type: `0x12`

Each record payload on an address announcement stream is a single network
address record (see [Network Address Record](#networkaddressrecord)).

Address announcements are subject to the rate limits and address book
management practices of [Address Relay](#addressrelay).


## Block Relay

### Divided Block Relay

This protocol divides block headers and block transactions, rather than
transferring monolithic `block` messages as the legacy protocol did:

- Block headers are gossiped directly on block announcement streams, as in
  BIP 130 [^bip-0130].
- Block transactions are relayed separately from headers using compact block
  relay (adapted from BIP 152 [^bip-0152]): a block is transferred as its
  header plus identifiers of its transactions, and only the transactions the
  receiver is missing are requested and transferred, using `get-tx` requests.

Both mechanisms are unconditional; the per-connection preferences are carried
in the `announce` and `full_ids` fields of the `init` record (see
[Init Record](#initrecord)).

### Headers-First Synchronization

Nodes synchronize the block chain using a headers-first approach; it is the
baseline synchronization method of this protocol, which every node supports.
It is the *full-validation* method: it assumes no trusted data beyond the
consensus rules and the genesis block. (An alternative method for nodes
with trusted checkpoint data is specified in
[Checkpointed Synchronization](#checkpointedsynchronization); recommended
concrete synchronization strategies are specified in [^draft-sync].)

1. The synchronizing node sends a `get-headers` request with a block locator
   (typically with `tx_ids = 0`; see [`get-headers`](#get-headers)).
2. The remote peer responds with up to 160 headers.
3. The synchronizing node validates the headers and requests full blocks via
   `get-blocks` requests.
4. Steps 1–3 repeat until the node is synchronized with the network.

The following rules apply to headers-first synchronization:

- A node MUST validate each received header — including its proof of work
  and its difficulty adjustment — before requesting the corresponding block
  and before extending its header chain with it.
- Received headers, even with valid proof of work, establish only that work
  was expended: a node MUST NOT treat a block as part of its best chain
  until the block itself has been validated under the consensus rules.
  Until then, headers serve to select and schedule block downloads.
- A node MUST NOT assign a misbehavior penalty solely because a peer's
  headers do not connect to its known chain or reflect a different best
  chain (see [Block Announcements](#blockannouncements)); penalties apply
  to provably invalid headers and blocks, per
  [Misbehavior and Banning](#misbehaviorandbanning).

### Checkpointed Synchronization

A node MAY synchronize spans of the historical chain against *trusted
commitments*: checkpoint data — bindings of block heights to block hashes —
obtained through a channel the node already trusts, such as its own binary
or local configuration. A recommended concrete strategy using `get-hashes`
is specified in [^draft-sync]; any checkpoint-based synchronization
procedure MUST obey the following rules.

- **Validated advancement.** A node MUST NOT advance its validated chain
  except through blocks that it has either validated under the consensus
  rules, or authenticated by an unbroken hash chain terminating in a
  checkpoint bound by a trusted commitment. The extent to which consensus
  checks may be abbreviated for checkpoint-authenticated blocks is a matter
  of local policy.
- **Untrusted inputs.** Peer-supplied data — hashes, headers, blocks — MUST
  NOT be relied upon for any security-relevant purpose until verified under
  the previous rule; until then it MAY be used only to select and schedule
  downloads. Data received from peers MUST NOT be incorporated into a
  node's trusted commitments.
- **Tolerance of divergent views.** A node MUST NOT assign a misbehavior
  penalty to a peer solely because the peer's `get-hashes` responses fail
  verification against the node's commitments, or reflect a different best
  chain; such responses are discarded and MAY be retried with other peers.
- **Reorganization margin.** Commitment-based authentication SHOULD NOT be
  applied within 100 blocks of the node's view of the network chain tip
  (matching the responder-side margin of [`get-hashes`](#get-hashes)); the
  chain near the tip is synchronized headers-first.
- **Headers-first fallback.** A node MUST be capable of completing
  synchronization using headers-first synchronization alone, and MUST fall
  back to it where its commitments end or where too few peers serve
  `get-hashes`.

The commitment scheme itself — checkpoint spacing, any chunking, and the
hash or signature scheme binding it — is local to the node and out of scope
for this protocol.

### Block Download Parameters

The block download parameters of ZIP 204 [^zip-0204-blockdownload] — the
download window, the per-peer in-transit limit, and the stalling timeout —
apply unchanged. On a stall, the node MAY re-request the block from an
alternative peer, cancelling the original request stream with `CANCELLED`.

### Compact Block Relay

Compact block relay is adapted from BIP 152 [^bip-0152]. This section
specifies the protocol flows and the Zcash-specific differences from BIP 152;
BIP 152 provides the design rationale.

The differences from BIP 152 are:

- There is no `sendcmpct` message. Compact block relay is unconditional, and
  the high-bandwidth announcement preference is carried in the `announce`
  field of the `init` record (see [Init Record](#initrecord)), and cannot be
  changed during the life of a connection. (A future change to the compact
  block encoding would be deployed under a new protocol version.)
- A compact block cannot be requested: BIP 152's `getdata` with
  `MSG_CMPCT_BLOCK` has no equivalent, and compact blocks occur only as
  high-bandwidth announcements. A peer announced to in low-bandwidth mode
  instead requests the block's coinbase transaction and transaction IDs via
  `get-headers` with `tx_ids = 1` (see [Relay Protocol](#relayprotocol)).
- A compact block can identify the block's transactions either by short
  transaction IDs or by full transaction IDs, at the receiver's option (the
  `full_ids` field of the `init` record; see
  [Full Transaction IDs](#fulltransactionids)). BIP 152 supports only short
  transaction IDs.
- There are no `getblocktxn` and `blocktxn` messages. Missing transactions are
  requested with `get-tx` requests (using `SHORTID`, `TXID`, or `WTXID`
  references) and delivered in the corresponding responses; see
  [Requesting Missing Transactions](#requestingmissingtransactions).
- The `header` field of a compact block uses the Zcash block header encoding
  [^protocol-blockheader], including the Equihash solution, rather than the
  80-byte Bitcoin header.
- The input to the short transaction ID computation is based on the wtxid as
  defined in ZIP 239 [^zip-0239] for version 5 transactions, rather than on
  either the txid (BIP 152 version 1) or the BIP 141 wtxid (BIP 152
  version 2); see [Short Transaction IDs](#shorttransactionids).

#### Compact Block Encoding

A compact block relays a block as its header plus a compact representation of
its transactions:

| Size   | Field             | Description                                                                                        |
|--------|-------------------|----------------------------------------------------------------------------------------------------|
| varies | `header`          | The block header, encoded as a CompactSize length prefix followed by the serialized header [^protocol-blockheader] (including the Equihash solution). |
| 8      | `nonce`           | Nonce for short transaction ID computation (`uint64`, little-endian). If `ids_kind` is 1, this field SHOULD be 0 and MUST be ignored. |
| 1      | `ids_kind`        | 0 if `ids` contains short transaction IDs; 1 if it contains full transaction IDs (`uint8`).        |
| varies | `ids_count`       | Number of transaction IDs (CompactSize).                                                           |
| varies | `ids`             | If `ids_kind` is 0: short transaction IDs, 6 bytes each, little-endian (see [Short Transaction IDs](#shorttransactionids)). If `ids_kind` is 1: full transaction IDs, 64 bytes each (see [Full Transaction IDs](#fulltransactionids)). |
| varies | `prefilled_count` | Number of prefilled transactions (CompactSize).                                                    |
| varies | `prefilled_txns`  | Prefilled transactions (see below).                                                                |

Each transaction in the block, in block order, is represented either by a
transaction ID in `ids` (short or full, according to `ids_kind`) or by a full
serialized transaction in `prefilled_txns`; the total number of transactions
in the block is `ids_count + prefilled_count`. A compact block in which
`ids_count + prefilled_count` exceeds 65,536 is a connection error of type
`FLOOD`.

A node MUST set `ids_kind` to 1 in compact blocks sent to a peer that set
`full_ids = 1` in its `init` record, and SHOULD set `ids_kind` to 0 otherwise.
A node MUST reject a compact block with an `ids_kind` value other than 0 or 1.

Each entry of `prefilled_txns` has the following format:

| Size   | Field   | Description                                                                                     |
|--------|---------|-------------------------------------------------------------------------------------------------|
| varies | `index` | Differentially encoded index of this transaction within the block (CompactSize; see below).     |
| varies | `tx`    | A full serialized transaction, encoded as a CompactSize length prefix followed by the serialized transaction [^protocol-txnencoding]. |

Prefilled transaction indexes are differentially encoded: the first `index`
is the absolute index of the first prefilled transaction within the block, and
each subsequent `index` is the difference between the absolute index of that
prefilled transaction and the absolute index of the previous prefilled
transaction, minus one. A node MUST reject a compact block in which any
absolute index would exceed 65535, or in which indexes overflow or are not
strictly increasing.

The coinbase transaction MUST be prefilled. A sender SHOULD additionally
prefill any transaction that it predicts the receiver does not have.

#### Short Transaction IDs

The short transaction ID of a transaction, relative to a given compact block,
is computed as follows:

1. Let `input` be the transaction identifier used for relay of the
   transaction: for a transaction with version ≥ 5, its 64-byte wtxid as
   defined in ZIP 239 [^zip-0239] (the txid followed by the `auth_digest`);
   for a transaction with version ≤ 4, its 32-byte txid.
2. Compute the single SHA-256 hash of the serialized block header (as it
   appears in the `header` field, without the length prefix) followed by the
   8-byte little-endian encoding of the `nonce` field.
3. Let `k0` and `k1` be the `uint64` values obtained by interpreting the first
   and second 8 bytes, respectively, of that hash in little-endian byte order.
4. The short transaction ID is the least significant 6 bytes, in little-endian
   byte order, of `SipHash-2-4(k0, k1, input)`, where SipHash-2-4 is as used
   in BIP 152 [^bip-0152].

The `nonce` SHOULD be chosen uniformly at random by the sender of a compact
block, so that short ID collisions between blocks and senders are independent.

#### Full Transaction IDs

The full transaction ID of a transaction is the 64-byte value consisting of
the transaction's txid followed by its `auth_digest`. For a transaction with
version ≥ 5, this is the wtxid used for relay, as defined in ZIP 239
[^zip-0239]. For a transaction with version ≤ 4, the `auth_digest` is the
placeholder value consisting of 32 bytes of `0xFF` defined in ZIP 244
[^zip-0244].

Matching against full transaction IDs is exact — they are not subject to
collisions and involve no `nonce`. A node unable to do short-ID matching (for
example, a pruned node) requests full transaction IDs by setting
`full_ids = 1` in its `init` record, at the cost of larger compact blocks.

#### Requesting Missing Transactions

Transactions that could not be matched while reconstructing a block from a
compact block are requested with `get-tx` requests, rather than with dedicated
messages as in BIP 152 (`getblocktxn` and `blocktxn`, which identify
transactions by index within the block):

- If the compact block had `ids_kind = 0`, each unmatched short transaction ID
  is requested as a `SHORTID` transaction reference containing the block hash
  and the short transaction ID copied from the compact block. Because short
  transaction IDs depend on the `nonce` of the compact block they appeared in,
  the responding node interprets them using the `nonce` of the compact block
  it most recently sent to the requesting peer for the identified block. A
  node receiving a `SHORTID` reference for a block for which it has not
  recently sent that peer a compact block, or whose short transaction ID
  matches no transaction — or more than one transaction — in the identified
  block, SHOULD answer that reference with a not-found result.
- If the compact block had `ids_kind = 1` — and likewise for each unmatched
  full transaction ID from a `get-headers` response with `tx_ids = 1` (see
  [`get-headers`](#get-headers)) — each unmatched full transaction ID is
  requested as an ordinary transaction reference: a `TXID` reference
  containing the txid if the `auth_digest` half of the full transaction ID is
  the 32-byte `0xFF` placeholder (indicating a pre-v5 transaction), or a
  `WTXID` reference containing the full transaction ID otherwise.

A node that has sent a peer a compact block, or a `get-headers` entry carrying
transaction IDs, MUST be able, for a reasonable implementation-defined time
thereafter, to serve that block's transactions to the same peer via `get-tx` —
including by `SHORTID` references in the compact block case, and irrespective
of whether those transactions remain in its mempool.

#### Relay Protocol

A node follows the BIP 152 [^bip-0152] protocol flows:

- **High-bandwidth mode** (the receiver's `init` record had `announce = 1`):
  the sender announces a new block by sending a compact block announcement
  directly. To minimize propagation latency, the sender MAY do so as soon as
  it has validated the block header (checking proof of work and difficulty),
  before fully validating the block. Because a high-bandwidth announcement may
  legitimately precede full validation by the announcing peer, a node MUST NOT
  assign a misbehavior penalty for a compact block announcement of a block
  that fails full validation, provided the block's header is valid (including
  its proof of work). A node SHOULD request high-bandwidth
  announcements from at most 3 peers, preferring the peers that most recently
  announced blocks to it first; to change its selection, it disconnects and
  reconnects with a new `init` record.
- **Low-bandwidth mode** (the receiver's `init` record had `announce = 0`):
  blocks are announced to the receiver with header announcements (see
  [Block Announcements](#blockannouncements)). The receiver MAY then request
  the block's coinbase transaction and transaction IDs — a `get-headers`
  request with `tx_ids = 1` whose `hash_stop` is the announced block hash —
  and reconstruct the block, fetching the transactions it is missing with
  `get-tx`; or it MAY request the full block via `get-blocks`. The receiver
  SHOULD use the transaction-ID form only for blocks close to its chain tip
  (BIP 152 [^bip-0152] recommends within 5 blocks), and request full blocks
  otherwise.

Upon receiving a compact block — or the equivalent header, coinbase
transaction, and transaction IDs from a `get-headers` response with
`tx_ids = 1` — a node attempts to reconstruct the block by matching each
transaction ID against the transactions it already holds (in its mempool or
otherwise) — computing short transaction IDs for the held transactions if the
IDs are short (`ids_kind = 0`), or comparing full transaction IDs directly
otherwise:

- If all transactions are available, the node reconstructs and validates the
  block as if it had been received as a full block.
- If one or more transactions are missing, or (for short transaction IDs) if
  two or more held transactions collide on the same short ID, the node
  requests the unresolved transactions with a `get-tx` request (see
  [Requesting Missing Transactions](#requestingmissingtransactions)), and
  completes reconstruction as the response arrives.
- If any requested transaction is answered with a not-found result, or if
  reconstruction fails after the responses arrive (for example, because a
  short ID collision caused a wrong match and the reconstructed block is
  invalid), the node SHOULD fall back to requesting the full block via
  `get-blocks`, and MUST NOT assign a misbehavior penalty solely because
  reconstruction failed.

An incorrectly reconstructed block fails validation of the block's merkle
root and authorizing data commitment, so short ID matching does not weaken
consensus enforcement.


## Transaction Relay

### Announcement-Based Relay

Transaction relay follows an announcement-based protocol:

1. A node with a new transaction sends a transaction reference on its
   transaction announcement stream to each peer (subject to trickling).
2. Peers that want the transaction request it with a `get-tx` request.
3. The originating node serves the transaction in the `get-tx` response.

Announcements use `TXID` and `WTXID` references according to transaction
version, as specified in
[Transaction References](#transactionreferences).

### Trickling

To impede network topology inference, transaction announcements SHOULD NOT be
sent immediately but SHOULD instead be "trickled" at random intervals. The
specific parameters are implementation-defined; for the reference values used
by legacy implementations, see ZIP 204 [^zip-0204-txrelay].

### Transaction Expiry

A node SHOULD NOT relay a transaction that will expire within 3 blocks of its
view of the current chain tip (`TX_EXPIRING_SOON_THRESHOLD`).

### Mempool Policy

Orphan transaction handling and the minimum relay fee are local mempool
policy, unchanged from the legacy protocol; see ZIP 204 [^zip-0204-txrelay].


## Address Relay

Address relay allows nodes to discover peers by propagating network address
records through the network, via address announcement streams and `get-addr`
requests.

### Rate Limiting

Address records SHOULD be subject to rate limiting to prevent address
flooding. The specific mechanism is implementation-defined; for the
token-bucket reference values used by zcashd, see ZIP 204
[^zip-0204-addressrelay].

A node MAY additionally apply backpressure on the peer's address announcement
stream to bound the rate at which it receives address records.

### Address Book Management

Relayed addresses are unauthenticated, attacker-suppliable data; an address
book that one source can fill leads to eclipse [^eclipse]. A node SHOULD
segment its address book by IP range, in the manner of the Bitcoin Core
address manager design:

- Define an address's *group* as an IP-range prefix of its address — for
  reference, Bitcoin Core and zcashd use the /16 prefix for IPv4 and the /32
  prefix for IPv6 — and, for a relayed address, its *source group* as the
  group of the peer that relayed it.
- Partition the address book into a bounded number of bounded-size buckets,
  and assign each address to a bucket determined by its group and its source
  group (keyed with a node-local secret), so that addresses from any one
  source group can occupy only a bounded fraction of the buckets. When a
  bucket is full, evict within the bucket; do not let insertions grow the
  book or displace addresses in other buckets.
- Keep addresses learned from independently trusted mechanisms (DNS seeding,
  local configuration) distinguishable from relayed addresses, and do not let
  relayed addresses evict them.

A node SHOULD also diversify its outbound connections across groups: for
reference, Bitcoin Core and zcashd make at most one outbound connection per
group. Outbound peer selection SHOULD NOT be biased toward the addresses most
recently received, since those are the easiest for an attacker to have
planted.

Addresses of overlay networks (`TORV3`, `I2P`) have no IP-range structure and
are free to generate, so bucketing cannot bound an attacker's share of them.
A node SHOULD treat each overlay network as a separate bounded segment of its
address book, and a node supporting both IP-based and overlay transports
SHOULD retain a minimum number of outbound connections on IP-based
transports.

### Address Broadcasting

The specific broadcast intervals are implementation-defined; for the
reference values used by zcashd, see ZIP 204 [^zip-0204-addressrelay].

How a node determines its own externally reachable addresses is out of scope
for this ZIP; the legacy `addr_recv`-based self-discovery is removed (see
[Init Record](#initrecord)).


## Misbehavior and Banning

Peer misbehavior is handled by two mechanisms, split by severity. Unambiguous
violations of "MUST"-level requirements — malformed records, invalid stream
usage, exceeded hard limits — are *connection errors*: the node closes the
connection immediately with the indicated error code (`PROTOCOL_ERROR` or
`FLOOD` unless otherwise specified), with no score kept. Violations for which
immediate disconnection would be disproportionate, or which an
honest-but-buggy peer or a peer on a different chain could commit, instead
accumulate a per-peer *misbehavior score* that leads to disconnection and
banning only when it crosses a threshold.

The misbehavior score works as follows:

- A node SHOULD maintain a misbehavior score for each connected peer,
  initialized to zero when the connection is established.
- When the node detects one of the violations listed below, it adds the
  listed number of points to the peer's score:

| Points | Violation                                                                                                          |
|--------|--------------------------------------------------------------------------------------------------------------------|
| 20     | `get-headers` response with more than 160 headers.                                                                 |
| 20     | Non-contiguous headers in a `get-headers` response.                                                                |
| 20     | `get-addr` response with more than 1000 address records.                                                           |
| 100    | Using a `TXID` reference to announce a v5 transaction, or a `WTXID` reference to announce a v4-or-earlier transaction (see ZIP 239 [^zip-0239]). |
| varies | Transaction, block, or header validation failure. The penalty is determined by the severity of the validation error. (See [Relay Protocol](#relayprotocol) for an exemption covering compact blocks relayed before full validation.) |

- When a peer's score reaches or exceeds the node's ban threshold, the node
  SHOULD close the connection with the `MISBEHAVIOR` error code and ban the
  peer's network address.
- While an address is banned, the node SHOULD NOT initiate connections to it,
  SHOULD refuse inbound connections from it, and SHOULD NOT include it in
  `get-addr` responses or address announcements.
- The ban threshold and ban duration are implementation-defined; for the
  reference values used by legacy implementations, see ZIP 204
  [^zip-0204-misbehavior].
- Whitelisted peers accumulate misbehavior scores but are exempt from
  banning.

Bans are keyed by network address, and are only as strong as the cost of
acquiring a new address. Banning is a meaningful deterrent for IP-based
transports; for overlay networks whose addresses are free to generate (such
as Tor onion services), it excludes only the banned address, and inbound
connection limits — not ban lists — bound the node's exposure (see
[Address Book Management](#addressbookmanagement)).


# Security and Privacy Considerations

**Scope of transport encryption.** Transport encryption protects the
confidentiality and integrity of each connection against passive network
observers. Peers are deliberately not authenticated (see
[Certificates](#certificates)), so an active attacker in a position to
intercept a connection can terminate the encryption with its own certificate
and read or modify that connection's traffic. The structural defense against
an active attacker seeking to control a node's view of the network is
redundancy: connections to multiple, independently discovered peers.

**Denial of service.** QUIC's address validation and amplification limits,
including Retry packets, bound the cost that spoofed-source floods can impose
(see [QUIC Transport](#quictransport)). At the application layer, resource
consumption is bounded by the record payload limit (see [Records](#records)),
the stream concurrency limits (see
[Transport Requirements](#transportrequirements)), the per-request count
limits of each request stream type, and address rate limiting (see
[Address Relay](#addressrelay)); exceeding a hard size or rate limit is a
connection error of type `FLOOD`.

**Fingerprinting and linkability.** A persistent TLS key would allow a node
to be recognized across connections and network locations; a node concerned
about this uses per-connection ephemeral keys (see
[Certificates](#certificates)). Connection migration links a node's traffic
across network paths (see [QUIC Transport](#quictransport)). The `user_agent`
field of the `init` record is a fingerprinting vector; a node MAY advertise a
generic user agent string. The `get-addr` policy (see [`get-addr`](#get-addr))
impedes fingerprinting of a node's address book, and trickling (see
[Trickling](#trickling)) impedes inference of the network topology and of the
origin of a transaction from announcement timing.

**Traffic analysis.** QUIC encrypts payloads but conceals neither packet
timing and volume nor the IP addresses of the communicating peers. In
particular, an adversary observing a node's traffic may still be able to
identify it as the originator of a transaction. The Tor transport (see
[Tor Transport](#tortransport)) defends against this adversary when it is
local — an observer of the node's network, or the remote peer itself, learns
neither the node's IP address nor which peers it communicates with — but not
against a global adversary correlating traffic timing across the Tor network.
The anticipated Nym mixnet transport (see [Deployment](#deployment)) is
directed at that stronger adversary.

**Tor.** On a Tor transport connection the initiator is anonymous — it
reveals no network address to the responder or to network observers — so a
node SHOULD prefer the Tor transport (where available) for the traffic most
sensitive to linkage, above all announcing transactions it originated. The
responder's onion address is a stable, linkable identifier, and onion
addresses are free to generate, which weakens address-based banning and
address book protections for `TORV3` addresses (see
[Misbehavior and Banning](#misbehaviorandbanning) and
[Address Book Management](#addressbookmanagement)).

**Synchronization.** Headers-first synchronization trusts proof of work:
forging a history requires outspending the honest chain's accumulated work
over the forged span, which an eclipsing attacker with sufficient hash power
can in principle do. Checkpointed synchronization trusts the node's
commitment, which shares a trust base with its binary: below its
checkpoints, an attacker who cannot break the block hash function cannot
cause acceptance of a false history. Under either method, an attacker
controlling a node's connections can withhold data and stall
synchronization; the mitigations are redundancy and re-requesting from
alternative peers (see
[Block Download Parameters](#blockdownloadparameters)).

**Eclipse attacks.** An attacker that controls all of a node's connections
controls its view of the block chain and mempool. The structural defenses are
segmentation of the address book by IP range and diversity in outbound peer
selection (see [Address Book Management](#addressbookmanagement) and
[^eclipse]), persisted addresses (see [Peer Discovery](#peerdiscovery)), and
rate-limited, validated address relay (see [Address Relay](#addressrelay)).
Overlay addresses such as onion services deserve particular caution here,
since an attacker can generate them without limit (see
[Address Book Management](#addressbookmanagement)).


# Deployment

This ZIP replaces the legacy protocol without a compatibility bridge: nodes
implementing this protocol do not interoperate with nodes implementing the
legacy protocol. Deployment is coordinated through the network upgrade
mechanism [^zip-0200]: the protocol version from which this protocol is in
effect will be assigned to a network upgrade, and the epoch enforcement of
ZIP 201 [^zip-0201] retires legacy-protocol peers at activation, as with any
other network upgrade.

Because there is no compatibility bridge, an implementation deploying this
protocol is expected to also implement the legacy protocol during the
transition: before activation, a node participates in the network over the
legacy protocol while also listening on the QUIC transport, so that DNS
seeders and upgraded peers can discover and exercise QUIC endpoints ahead of
activation. The QUIC transport uses UDP where the legacy transport uses TCP,
so both can be served concurrently on the same port number and address. At
activation, epoch enforcement retires legacy-protocol connections, and the
node continues on this protocol alone.

DNS seeders are expected to probe and serve the QUIC endpoints of nodes
implementing this ZIP.

The protocol semantics are specified against the abstract stream layer of
[Stream Layer](#streamlayer); QUIC and Tor are the transports defined by this
ZIP. Future revisions are expected to define additional transports to be used
simultaneously with them; in particular, a transport carrying the stream layer
over the Nym mixnet [^nym] is anticipated, providing network-level metadata
protection (resistance to traffic analysis of which peers are communicating)
stronger than onion routing provides.

*Note:* The transports are complementary rather than alternatives: a node is
expected to use QUIC for latency-critical bulk relay and synchronization, and
Tor (eventually Nym) where anonymity matters more than latency, selected per
connection according to the traffic it will carry.


# Formal Model

A TLA+ formal specification of the legacy protocol's connection lifecycle is
available at [^formal-model]; it has not yet been updated for the protocol
specified here.


# References

[^BCP14]: [Information on BCP 14 — "RFC 2119: Key words for use in RFCs to Indicate Requirement Levels" and "RFC 8174: Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words"](https://www.rfc-editor.org/info/bcp14)

[^protocol-networks]: [Zcash Protocol Specification, Version 2026.8.0 [NU6.3]. Section 3.12: Mainnet and Testnet](protocol/protocol.pdf#networks)

[^protocol-blockchain]: [Zcash Protocol Specification, Version 2026.8.0 [NU6.3]. Section 3.3: The Block Chain](protocol/protocol.pdf#blockchain)

[^protocol-txnencoding]: [Zcash Protocol Specification, Version 2026.8.0 [NU6.3]. Section 7.1: Transaction Encoding and Consensus](protocol/protocol.pdf#txnencoding)

[^protocol-blockheader]: [Zcash Protocol Specification, Version 2026.8.0 [NU6.3]. Section 7.6: Block Header Encoding and Consensus](protocol/protocol.pdf#blockheader)

[^zip-0155]: [ZIP 155: addrv2 message](zip-0155.rst)

[^zip-0200]: [ZIP 200: Network Upgrade Mechanism](zip-0200.rst)

[^zip-0201]: [ZIP 201: Network Peer Management for Overwinter](zip-0201.rst)

[^zip-0204]: [ZIP 204: Zcash P2P Network Protocol](zip-0204.rst)

[^zip-0204-epochs]: [ZIP 204: Zcash P2P Network Protocol — Network Upgrade Epoch Enforcement](https://zips.z.cash/zip-0204#network-upgrade-epoch-enforcement)

[^zip-0204-dnsseeds]: [ZIP 204: Zcash P2P Network Protocol — DNS Seeds](https://zips.z.cash/zip-0204#dns-seeds)

[^zip-0204-blockdownload]: [ZIP 204: Zcash P2P Network Protocol — Block Download Parameters](https://zips.z.cash/zip-0204#block-download-parameters)

[^zip-0204-txrelay]: [ZIP 204: Zcash P2P Network Protocol — Transaction Relay](https://zips.z.cash/zip-0204#transaction-relay)

[^zip-0204-addressrelay]: [ZIP 204: Zcash P2P Network Protocol — Address Relay](https://zips.z.cash/zip-0204#address-relay)

[^zip-0204-misbehavior]: [ZIP 204: Zcash P2P Network Protocol — Misbehavior and Banning](https://zips.z.cash/zip-0204#misbehavior-and-banning)

[^zip-0204-assignment]: [ZIP 204: Zcash P2P Network Protocol — Assigning Protocol Versions to Network Upgrades](https://zips.z.cash/zip-0204#assigning-protocol-versions-to-network-upgrades)

[^zip-0239]: [ZIP 239: Relay of Version 5 Transactions](zip-0239.rst)

[^draft-sync]: [Draft ZIP: Block Chain Synchronization](draft-arya-block-chain-sync.md)

[^zip-0244]: [ZIP 244: Transaction Identifier Non-Malleability](zip-0244.rst)

[^bip-0130]: [BIP 130: sendheaders message](https://github.com/bitcoin/bips/blob/master/bip-0130.mediawiki)

[^bip-0152]: [BIP 152: Compact Block Relay](https://github.com/bitcoin/bips/blob/master/bip-0152.mediawiki)

[^bip-0324]: [BIP 324: Version 2 P2P Encrypted Transport Protocol](https://github.com/bitcoin/bips/blob/master/bip-0324.mediawiki)

[^rfc7250]: [RFC 7250: Using Raw Public Keys in Transport Layer Security (TLS) and Datagram Transport Layer Security (DTLS)](https://www.rfc-editor.org/rfc/rfc7250.html)

[^rfc7301]: [RFC 7301: Transport Layer Security (TLS) Application-Layer Protocol Negotiation Extension](https://www.rfc-editor.org/rfc/rfc7301.html)

[^rfc8446]: [RFC 8446: The Transport Layer Security (TLS) Protocol Version 1.3](https://www.rfc-editor.org/rfc/rfc8446.html)

[^rfc9000]: [RFC 9000: QUIC: A UDP-Based Multiplexed and Secure Transport](https://www.rfc-editor.org/rfc/rfc9000.html)

[^rfc9001]: [RFC 9001: Using TLS to Secure QUIC](https://www.rfc-editor.org/rfc/rfc9001.html)

[^rfc9221]: [RFC 9221: An Unreliable Datagram Extension to QUIC](https://www.rfc-editor.org/rfc/rfc9221.html)

[^tor]: [The Tor Project](https://www.torproject.org/)

[^tor-rend-spec]: [Tor Rendezvous Specification — Version 3 Onion Services](https://spec.torproject.org/rend-spec/index.html)

[^nym]: [The Nym Mixnet](https://nymtech.net/)

[^eclipse]: [Ethan Heilman, Alison Kendler, Aviv Zohar, Sharon Goldberg. Eclipse Attacks on Bitcoin's Peer-to-Peer Network. 24th USENIX Security Symposium, 2015.](https://eprint.iacr.org/2015/263)

[^formal-model]: [Zcash P2P Protocol TLA+ Specification](https://github.com/oxarbitrage/zcash-p2p-spec)
