<pre>
ZIP: XXX
Title: ZeWIF: Zcash Wallet Interchange Format
Owners: Kris Nuttycombe &lt;kris@nutty.land&gt;
Status: Draft
Category: Standards / Wallet
Created: 2026-07-02
License: MIT
Discussions-To: &lt;https://github.com/zcash/zewif/issues&gt;
</pre>

# Terminology

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", "MAY", and
"RECOMMENDED" in this document are to be interpreted as described in BCP 14
[^BCP14] when, and only when, they appear in all capitals.

"ZeWIF document" means a byte sequence conforming to the container format
defined in this specification. "Exporter" means software producing a ZeWIF
document from wallet state; "importer" means software consuming one.

# Abstract

This proposal defines ZeWIF, a file format for migrating wallet data between
Zcash wallet implementations. A ZeWIF document is a single-snapshot archive of
the state a wallet cannot recover from the block chain alone — key material,
account structure, address metadata, user annotations — together with optional
chain-derived data that lets an importing wallet avoid expensive rescanning.
The format is a deterministic CBOR encoding [^RFC8949] under a normative CDDL
schema [^RFC8610], with spending-key material segregated into a section that
can be independently encrypted.

# Motivation

Zcash wallet implementations persist their state in mutually incompatible
formats. When a wallet reaches end of service (as zcashd has) or a user wishes
to change wallets, the absence of an interchange format forces ad-hoc pairwise
migration tools, and data that only the source wallet knows — spending keys
for legacy addresses, address books, memos and annotations on transactions,
address-exposure state needed for gap-limit-correct restores — is routinely
lost.

An interchange format for this purpose has unusual durability requirements: a
ZeWIF file may be written to offline storage and read decades later, possibly
after its producing software has disappeared. This motivates the central
design choices:

- **A widely deployed, standardized encoding.** CBOR is an IETF Internet
  Standard (STD 94) with independent implementations in every mainstream
  language, and is self-describing at the data-model level: any generic CBOR
  tool can decode the structure of a ZeWIF file without this specification in
  hand. A ZeWIF document begins with the self-described-CBOR tag (RFC 8949
  §3.4.6), so its leading bytes are a magic number that identifies the file as
  CBOR to content-sniffing tools, and it carries a registered CBOR tag that
  identifies it specifically as ZeWIF.
- **A normative machine-readable schema.** The CDDL schema in this document is
  the authoritative definition of the format; the Rust reference
  implementation conforms to it, not the reverse.
- **Deterministic encoding.** Writers emit RFC 8949 §4.2 Core Deterministic
  Encoding, so equal wallet states produce byte-identical documents. This
  makes round-trip conformance testing exact and documents stable under
  re-export.
- **Spending/viewing separability.** All secret key material lives in a single
  section of the document that may be stored encrypted, so a viewing-only
  export is obtained by omitting one node, and an at-rest export can protect
  its secrets without encrypting chain-public data.

# Requirements and non-goals

The format MUST be able to represent the wallet state persisted by
`zcash_client_sqlite` (the librustzcash reference wallet backend) and the
state recoverable from a zcashd `wallet.dat`, without loss of any data that is
not recoverable from the block chain.

The format is a snapshot archive. It is NOT a synchronization protocol, a
backup-rotation scheme, or an on-chain format. Nothing in this specification
defines network behavior.

# Specification

## Container format

A ZeWIF document is a single CBOR data item, a nesting of two tags around a
`[version, payload]` array:

```text
#6.55799(#6.<TN>([version, payload]))
```

where, from the outside in:

- **`#6.55799(...)`** is the "Self-Described CBOR" tag (RFC 8949 §3.4.6). It
  carries no semantics beyond marking its content; its purpose here is its
  encoding, the three bytes `0xD9 0xD9 0xF7`, which are a registered magic
  number identifying the byte stream as CBOR to generic content-sniffing
  tools. Every ZeWIF document begins with these three bytes.
- **`#6.<TN>(...)`** is the ZeWIF tag, `<TN>` being the tag number assigned in
  the IANA "CBOR Tags" registry for this format (see [Container tag](#container-tag)).
  It gives a decoder that knows the tag positive identification of the item as
  a ZeWIF document.
- **`[version, payload]`** is a definite-length two-element array: an unsigned
  `version` (this document defines version 1) followed by the `payload`, a
  single CBOR data item conforming to the `zewif` rule of the schema below.

Readers MUST reject a document not framed by these two tags in this order, and
MUST NOT attempt to interpret the payload of a document whose version they do
not implement. The container version selects the schema revision and every
parsing rule applicable to the payload; implementations supporting multiple
versions MUST dispatch on it rather than attempting to unify parsers. Because
the version precedes the payload in the array, a reader determines the version
before decoding the payload. Version 1 payloads are not compressed;
compression, if ever introduced, will be signalled by a new container version.

### Container tag

The ZeWIF tag number `<TN>` is registered in the First Come First Served range
of the IANA "CBOR Tags" registry [^RFC8949]. The registration requests the
value **133133**, which echoes Zcash's SLIP-0044 registered coin type (133) by
repetition. Until IANA confirms the assignment this value is provisional, and
implementations of pre-1.0 release-candidate revisions MUST NOT treat any
document as stable across a change to the assigned number.

## CBOR profile

- Writers MUST emit RFC 8949 §4.2 Core Deterministic Encoding: definite
  lengths everywhere, integers in their shortest form, and map keys sorted in
  bytewise lexicographic order of their encodings. Readers SHOULD accept any
  well-formed CBOR that satisfies the schema.
- Optional record fields are expressed by *omitting* the map entry. Writers
  MUST NOT encode an absent optional field as CBOR `null`; readers SHOULD
  treat a `null` value in an optional field position as if the entry were
  absent. (The reader tolerance is a defense in depth: encoder libraries
  have been observed to disagree on the encoding of absent optional values,
  and a document produced by a nonconformant writer should degrade to a
  readable document rather than an unreadable one.)
- Readers MUST ignore map keys not defined in the schema version they
  implement. This is the format's forward-compatibility mechanism.
- A field index (map key), once assigned a meaning in a published revision of
  this schema, MUST NOT be reused or assigned a different type. New fields
  are added under fresh indices.
- A boolean field documented with a default MUST be omitted by writers when it
  takes the default value (so that each state has exactly one encoding).

## Structural conventions

The schema uses three shapes, chosen so that every logical state has exactly
one encoding:

1. **Records** are CBOR maps with small unsigned-integer keys (the COSE/CWT
   convention [^RFC9052]). The integer registry in the CDDL below maps each
   index to a field name.
2. **Enumerations without payload** (key scope, account purpose) are bare
   unsigned integers.
3. **Tagged unions** (sums-of-products) are arrays `[variant-id, body?]`:
   an unsigned variant identifier, followed for data-bearing variants by
   exactly one body item — a record, or, where the payload is a single
   canonical encoding, that encoding's byte or text string directly.
   Payload-free variants are the one-element array `[variant-id]`. Variant
   identifiers follow the same never-reuse rule as field indices.

Byte sequences are CBOR byte strings (`bstr`); text is UTF-8 (`tstr`). Block
heights are unsigned integers less than 2^32. Monetary values are unsigned
integers in zatoshis, at most 2,100,000,000,000,000 (`MAX_MONEY`). Timestamps
are integer seconds since the Unix epoch.

Where a value has a canonical Zcash encoding, ZeWIF stores that encoding
verbatim rather than a decomposition, so that consumers do not require
protocol-library support to carry the data. Addresses and keys use their
canonical *string* encodings — unified addresses and viewing keys per
ZIP 316 [^ZIP316], Sapling extended keys per ZIP 32 [^ZIP32], Sprout keys
and transparent private keys (WIF) per the Zcash protocol specification's
Base58Check forms [^PROTOCOL], and extracted unified spending keys per the
unified raw encodings draft [^ZIPRAW] — which carry a checksum and embed
type and network discrimination, so each key is independently
integrity-checked; seed fingerprints likewise use their ZIP 32 Bech32m
string encoding (Human-Readable Part "zip32seedfp"). Raw transactions use
their canonical byte encodings.

## Sensitive material

All secret key material in a ZeWIF document lives in the `secret-store`
record, referenced from the public wallet structure by public identifiers:
seeds by their ZIP 32 seed fingerprint, transparent private keys by their
public key, Sapling spending keys by their extended full viewing key,
extracted unified spending keys by their unified full viewing key, and
Sprout spending keys by their address.

The `secrets` node of the top-level record is either the secret store in
plain CBOR, or an age ciphertext [^AGE] whose plaintext is the CBOR encoding
of the secret store. The choice of age recipients (passphrase-derived or
X25519) is between the exporter and its user; the document carries only the
ciphertext.

A viewing-only export omits the `secrets` node entirely. Importers MUST treat
the absence of an expected secret-store entry (e.g. for an address marked as
having an imported key) as a viewing-only import of the affected item, not as
an error.

## Schema

The following CDDL is normative. Comments give the field names used by the
reference implementation.

```cddl
zewif = {
  0: [* wallet],                ; wallets
  1: [* transaction],           ; global transaction table, sorted
                                ; ascending by txid, unique by txid
  2: height,                    ; export-height: chain tip at export time
  3: bytes32,                   ; hash of the block at export-height;
                                ; advisory — a chain reorganization may
                                ; orphan this block after export
  ? 4: secrets,                 ; sensitive key material (see below)
  ? 5: bytes32,                 ; export-id: random identifier for this export
  ? 6: extensions,
  ? 7: tstr,                    ; embedded copy of the CDDL schema for this
                                ; document's container version, for archival
                                ; self-description; informative only — the
                                ; container version remains authoritative
}

wallet = {
  0: network,
  1: [* account],
  2: [* address-book-entry],
  ? 3: extensions,
}

network = [0]                     ; mainnet
        / [1]                     ; testnet
        / [2, regtest-params]     ; regtest

; Regtest networks vary in their network-upgrade activation schedules, and
; wallet data recorded against one activation schedule is in general
; incompatible with a chain using another. The activation map makes the
; network's composition legible to the importer, which SHOULD refuse or
; flag data whose activation schedule does not match the chain it operates
; against.
regtest-params = {
  0: {* uint => height},        ; consensus branch ID (as defined by ZIP 200
                                ; and successors) => activation height, for
                                ; each network upgrade active on the chain
}

account = {
  0: tstr,                      ; name (may be empty; no uniqueness semantics)
  1: account-viewing-key,
  ? 2: key-source,
  ? 3: height,                  ; birthday-height: first height to scan
  ? 4: bytes32,                 ; birthday-block: hash of the block at
                                ; birthday-height
  ? 5: chain-state,             ; birthday-chain-state: tree state at the end
                                ; of a block strictly BEFORE birthday-height
                                ; (canonically the immediately preceding
                                ; block); scanning begins at the following
                                ; block
  ? 6: height,                  ; recover-until-height (exclusive): scanning
                                ; below this height counts as recovery
  ? 7: account-purpose,
  ? 8: tstr,                    ; provenance: free-form key-material origin
                                ; tag, e.g. "zcashd_mnemonic"
  9: [* scan-range],            ; fully-scanned ranges
  10: [* address],
  11: {* txid => [* received-output]},  ; received outputs by transaction
  12: {* txid => [* sent-output]},      ; sent outputs by transaction
  ? 13: extensions,
}

account-viewing-key = [0, ufvk]                ; ZIP 316 UFVK
                    / [1, sapling-extfvk]      ; standalone Sapling extfvk
                    / [2, sprout-vk]           ; Sprout viewing key
                    / [3]                      ; transparent address set
                                               ; (legacy zcashd)

; Viewing keys are carried in their canonical string encodings, which
; embed a checksum plus type and network discrimination.
ufvk           = tstr           ; ZIP 316 Bech32m ("uview1...")
sapling-extfvk = tstr           ; ZIP 32 Bech32 ("zxviews..." /
                                ; "zxviewtestsapling...")
sprout-vk      = tstr           ; Base58Check ("ZiVK..." / "ZiVt...")

key-source = [0, key-source-derived]
           / [1]                ; imported

key-source-derived = {
  0: seed-fingerprint,
  1: uint,                      ; ZIP 32 account index (hardened)
  ? 2: uint,                    ; zcashd legacy address index (< 2^31); the
                                ; address-index component of the legacy path
                                ; m/32h/coin_h/0x7FFFFFFFh/index_h
}

account-purpose = 0             ; spending: source wallet held spend authority
                / 1             ; view-only

chain-state = {
  0: height,                    ; the block whose end-state this describes
  ? 1: bytes32,                 ; hash of that block
  ? 2: frontier,                ; Sapling note commitment tree frontier
  ? 3: frontier,                ; Orchard note commitment tree frontier
  ? 4: frontier,                ; Ironwood note commitment tree frontier
}                               ; future pools: new indices

frontier = [0]                  ; the tree is empty as of the block
         / [1, frontier-data]
                                ; a more compact representation — omitting a
                                ; right-hand leaf in favor of the root of the
                                ; subtree it completes — may be added as a
                                ; future variant under a fresh identifier

frontier-data = {
  0: uint,                      ; position: 0-based index of the most
                                ; recently appended leaf
  1: bytes32,                   ; that leaf's node value
  2: [* bytes32],               ; ommers: roots of completed left subtrees,
                                ; leaf-to-root order; the count is fully
                                ; determined by position
}

scan-range = {
  0: height,                    ; start (inclusive)
  1: height,                    ; end (inclusive)
}

address = {
  0: protocol-address,
  ? 1: key-scope,
  ? 2: height,                  ; exposed-at-height: when the address was
                                ; first exposed to a user or counterparty;
                                ; not chain-recoverable; absent = never
                                ; exposed (e.g. zcashd keypool keys)
  ? 3: extensions,
}

key-scope = 0                   ; external: user-facing receiving
          / 1                   ; internal: change/shielding, never exposed
          / 2                   ; ephemeral: ZIP 320 single-use transparent
          / 3                   ; foreign: imported standalone key or script

protocol-address = [0, transparent-address]
                 / [1, sprout-address]
                 / [2, sapling-address]
                 / [3, unified-address]

transparent-address = {
  0: tstr,                      ; canonical address string
  ? 1: transparent-spend-authority,
  ? 2: transparent-pubkey,      ; pubkey: watch-only imported P2PK/P2PKH;
                                ; omitted when spend authority is present
  ? 3: bstr,                    ; redeem-script: watch-only imported P2SH
}

transparent-spend-authority
  = [0, derivation-info]        ; derived: recoverable from seed
  / [1]                         ; imported: private key, if exported, is in
                                ; the secret store under this address's pubkey

derivation-info = {
  0: uint,                      ; change component (0 external, 1 internal,
                                ; 2 ephemeral)
  1: uint,                      ; address index (non-hardened)
}

sprout-address  = { 0: tstr }
sapling-address = { 0: tstr, ? 1: bytes11 }   ; diversifier index
unified-address = { 0: tstr, ? 1: bytes11 }   ; diversifier index

transaction = {
  0: txid,
  ? 1: transaction-data,
  ? 2: height,                  ; target-height
  ? 3: height,                  ; mined-height
  ? 4: tx-block-position,
  ? 5: uint,                    ; fee in zatoshis
  ? 6: height,                  ; expiry-height
  ? 7: int,                     ; created-time: unix seconds; creation time
                                ; for wallet-authored transactions, first-
                                ; observed time otherwise
  ? 8: bool,                    ; trusted (ZIP 315); default false, omitted
                                ; when false
  ? 9: extensions,
}

transaction-data = [0, raw-tx-data]
                 / [1, compact-tx-data]

raw-tx-data = { 0: bstr }       ; canonical Zcash transaction encoding

compact-tx-data = {
  0: bstr,                      ; protobuf-encoded CompactTx
  1: tstr,                      ; lightwalletd protocol semver that produced
                                ; the encoding (the protobuf schema is not
                                ; self-describing)
}

tx-block-position = {
  0: bytes32,                   ; block hash
  1: uint,                      ; index of the transaction within the block
}

; Value, memo, change status, and nullifiers are optional enrichment:
; recoverable from the raw transaction plus the account viewing key. The raw
; transaction is authoritative where both are present. Exporters SHOULD
; populate them when raw transaction data is absent.
received-output = {
  0: uint,                      ; output-index within the pool's output list
                                ; (Sprout: 2*joinsplit_index + n, each
                                ; JoinSplit having exactly two outputs)
  1: received-output-pool,
  ? 2: uint,                    ; value in zatoshis
  ? 3: bstr,                    ; memo (at most 512 bytes)
  ? 4: bool,                    ; is-change; absent = unknown
  ? 5: txid,                    ; spent-by
}

received-output-pool = [0, transparent-output-data]
                     / [1, sprout-output-data]
                     / [2, sapling-output-data]
                     / [3, orchard-output-data]
                     / [4, ironwood-output-data]

transparent-output-data = {
  ? 0: bstr,                    ; scriptPubKey, for UTXOs whose containing
                                ; transaction is unavailable; the raw
                                ; transaction is authoritative when present
  ? 1: height,                  ; max-observed-unspent-height
}

sprout-output-data = {
  ? 0: bytes32,                 ; nullifier
}                               ; Sprout spendability is not reconstructible
                                ; from this data; a Sprout-capable importer
                                ; must rescan

sapling-output-data = {
  ? 0: commitment-tree-data,
  ? 1: bytes32,                 ; nullifier
}

orchard-output-data = {
  ? 0: commitment-tree-data,
  ? 1: bytes32,                 ; nullifier
}

; The Ironwood pool (introduced by the NU6.3 network upgrade) uses the
; Orchard protocol -- the same circuit and bundle schema -- but constitutes
; a distinct value pool with its own note commitment tree.
ironwood-output-data = {
  ? 0: commitment-tree-data,
  ? 1: bytes32,                 ; nullifier
}

commitment-tree-data = [0, tree-position]
                     / [1, incremental-witness]

tree-position = { 0: uint }     ; 0-based leaf position of the note
                                ; commitment in its pool's tree

incremental-witness = {
  0: bytes32,                   ; note commitment
  1: uint,                      ; note position
  2: [* bytes32],               ; merkle path, leaf to root
  3: bytes32,                   ; anchor
  4: uint,                      ; tree size as of the anchor
  5: [* bytes32],               ; tree frontier as of the anchor
}

; No Sprout variant is defined: Sprout provides no outgoing-viewing-key
; mechanism by which a sender could later recover its non-change outputs,
; and zcashd persists no Sprout sent-output metadata (its recipient mapping
; records apply only to unified-address sends). A wallet that independently
; tracked such records may carry them as extension data.
sent-output = [0, transparent-sent-output]
            / [1, sapling-sent-output]
            / [2, orchard-sent-output]
            / [3, ironwood-sent-output]

transparent-sent-output = {
  0: uint,                      ; output-index within the transaction's vout
  1: tstr,                      ; recipient address, verbatim as used
  2: uint,                      ; value in zatoshis
}

sapling-sent-output = {
  0: uint,                      ; output-index within the Sapling output list
  1: tstr,                      ; recipient address, verbatim (may be a
                                ; unified address; not reconstructible from
                                ; the pool component alone)
  2: uint,                      ; value in zatoshis
  ? 3: bstr,                    ; memo
}

orchard-sent-output = {
  0: uint,                      ; action index within the Orchard action list
  1: tstr,                      ; recipient address, verbatim
  2: uint,                      ; value in zatoshis
  ? 3: bstr,                    ; memo
}

ironwood-sent-output = {
  0: uint,                      ; action index within the Ironwood action list
  1: tstr,                      ; recipient address, verbatim
  2: uint,                      ; value in zatoshis
  ? 3: bstr,                    ; memo
}

address-book-entry = {
  0: tstr,                      ; address, canonical string (any protocol);
                                ; may be wallet-owned (recording whom it was
                                ; given to) or a counterparty address
  ? 1: tstr,                    ; label (zcashd "name" records)
  ? 2: tstr,                    ; purpose, e.g. "receive"/"send"/"unknown"
                                ; (zcashd "purpose" records)
  ? 3: extensions,
}

secrets = [0, secret-store]     ; plaintext
        / [1, encrypted-store]

encrypted-store = {
  0: bstr,                      ; age ciphertext; plaintext is the CBOR
                                ; encoding of a secret-store
}

secret-store = {
  0: [* seed-entry],
  1: [* transparent-key-entry],
  2: [* sapling-key-entry],
  3: [* sprout-key-entry],
  ? 4: extensions,
  ? 5: [* unified-key-entry],   ; omitted when empty
}

seed-entry = {
  0: seed-fingerprint,          ; referenced by key-source-derived entries
  1: seed-material,
}

seed-material = [0, bip39-mnemonic]
              / [1, legacy-seed]

legacy-seed = bytes32           ; raw pre-mnemonic HD seed bytes

bip39-mnemonic = {
  0: tstr,                      ; the mnemonic phrase
  ? 1: tstr,                    ; language, BCP 47 tag (e.g. "en")
}

; An extracted single-account unified spending key, stored under the
; unified full viewing key it corresponds to. Most wallets hold spend
; authority as seeds, from which per-account unified spending keys are
; derived on demand; this entry represents a wallet holding only an
; extracted spending key. The encoding is the Bech32m string obtained by
; applying F4Jumble to the key's raw encoding, per the unified raw
; encodings draft ZIP.
unified-key-entry = {
  0: ufvk,
  1: tstr,                      ; unified spending key text encoding
}

transparent-key-entry = {
  0: transparent-pubkey,        ; secp256k1 public key
  1: tstr,                      ; private key in WIF Base58Check encoding
                                ; (version 0x80 mainnet / 0xEF testnet; a
                                ; trailing 0x01 marks a compressed pubkey)
}

sapling-key-entry = {
  0: sapling-extfvk,            ; the extended full viewing key this
                                ; spending key corresponds to
  1: tstr,                      ; extended spending key, ZIP 32 Bech32
                                ; ("secret-extended-key-main..." / "-test...")
}

sprout-key-entry = {
  0: tstr,                      ; Sprout address
  1: tstr,                      ; Sprout spending key, Base58Check
                                ; ("SK..." / "ST...")
}

; Vendor-namespaced extension data. Vendor identifiers SHOULD be reverse-DNS
; or another collision-resistant convention. Re-exporting software MUST
; preserve extension entries it does not understand.
extensions = {* tstr => {* tstr => extension-value}}

; A single embedded CBOR data item (the semantics of RFC 8949 tag 24).
extension-value = bstr

; A ZIP 32 seed fingerprint in its canonical string encoding: Bech32m with
; the Human-Readable Part "zip32seedfp" over the 32 fingerprint bytes.
; Fingerprints are not network-bound.
seed-fingerprint = tstr

transparent-pubkey = bstr .size 33 / bstr .size 65

height  = uint .lt 4294967296
txid    = bytes32
bytes32 = bstr .size 32
bytes11 = bstr .size 11
```

## Schema evolution

A revision of this specification MAY:

- add new optional fields to a record under fresh indices;
- add new variants to a tagged union under fresh identifiers;
- introduce a new container version, incrementing the `version` element of
  the container array, to signal a schema revision that a version-1 reader
  MUST NOT attempt to parse.

A revision MUST NOT change the type or meaning of an existing index or
variant identifier, and MUST NOT convert an optional field to required.
Importers encountering an unknown variant identifier in a tagged union MUST
NOT misinterpret it; software that re-exports a document it read SHOULD
preserve unrecognized variants and extension data opaquely, and MUST report
to its caller any data it drops.

# Rationale

**Why CBOR and CDDL.** The candidate encodings seriously considered were
CBOR+CDDL, Protocol Buffers, and JSON+JSON-Schema. Protocol Buffers offer the
strongest field-evolution discipline and are already deployed in the Zcash
light-client protocol, but a protobuf document is not self-describing (the
`.proto` is required to recover even the structure), serialization is
explicitly non-canonical, and code generation imposes toolchain weight on
every implementation. JSON maximizes ubiquity and eyeball-durability but
handles the format's pervasive byte strings poorly. CBOR is an IETF Internet
Standard with a defined deterministic profile and native byte strings, and a
generic CBOR decoder recovers the full structure of a ZeWIF file without any
schema in hand.

**Why integer map keys.** Field-name strings would make documents fully
self-describing, but integer keys with a published registry follow the
established practice of COSE and CWT, produce materially smaller documents
(wallet exports repeat record shapes thousands of times), and carry the same
never-reuse evolution discipline as protobuf field numbers. The CDDL registry
in this document, which is versioned and published, supplies the names.

**Why `[id, body?]` unions.** Encoding data-bearing variants with exactly
one body item gives every variant body a named schema rule, keeps the
encoding of "no payload" (the one-element array `[id]`) distinct from any
body, and — in the reference implementation — sidesteps a class of encoder
disagreements about optional fields embedded directly in variant bodies. A
body is a record unless the payload is a single canonical encoding, in
which case that encoding's byte or text string is carried directly: a
one-field record shell around such an encoding would name the same concept
twice.

**Prior format.** An earlier iteration of ZeWIF serialized to Gordian
Envelope (dcbor). That design imported a large dependency stack (223 crates
locked, including unrelated cryptography) for the reference implementation,
had no format version marker, and relied on encoding conventions defined
outside any standards process. No dcbor-based ZeWIF files are known to have
been produced outside development, so this specification makes a clean break;
the Envelope layer's useful property — deterministic encoding — is retained
via RFC 8949 §4.2.

**Why age for secret encryption.** age is a small, well-specified,
widely-implemented file-encryption format with both passphrase and public-key
recipients, and is already the at-rest key-material encryption used by zallet
(the zcashd successor wallet). Embedding an age ciphertext rather than
defining a bespoke scheme keeps cryptographic agility and audit surface
outside this specification.

**Enrichment fields.** Data recoverable from a raw transaction plus a viewing
key (output values, memos, nullifiers, change status) is optional and
subordinate to the raw transaction. This lets exporters that hold raw
transactions skip trial decryption, lets compact-data-only wallets export
what they know, and defines conflict resolution when both are present.

**Witness policy.** Note commitment tree positions plus a per-account
birthday frontier are sufficient for an importer with chain access to rebuild
witnesses by scanning forward from the birthday. Full incremental witnesses
are carried optionally for importers without chain access. Neither is
required: a rescan-based importer (like zallet's zcashd migration) may ignore
both.

**No compression in version 1.** Wallet exports are dominated by
already-compact byte strings; a compression layer adds a decompression
dependency to every future reader for marginal size benefit. External
compression of the whole file remains possible without affecting the format.

# Reference implementation

The `zewif` Rust crate (https://github.com/zcash/zewif) implements this
specification. Implementation notes, non-normative:

- The crate uses `minicbor` with derived codecs; integer field indices in the
  schema correspond to `#[n(...)]` attributes, records use `#[cbor(map)]`,
  payload-free enumerations use `#[cbor(index_only)]`, fixed-size byte types
  carry generated length-checked `bstr` codecs, and canonically-text-encoded
  keys are transparent newtypes over `tstr`.
- Deterministic map-key ordering is obtained by declaring record fields in
  ascending index order and using ordered collections (sorted arrays keyed
  by txid) rather than hash maps.
- Conformance is tested by randomized round-trip tests plus byte-exact
  re-encoding checks. Conformance test vectors derived from this
  specification independently of the codec implementation will accompany
  submission for community review.
- The normativity of this schema, rather than of any codec library, is
  enforced mechanically: golden byte-exact fixture documents are committed
  to the repository and asserted in continuous integration, so a behavioral
  change in the codec dependency fails the build rather than shipping
  spec-divergent bytes; emitted documents are additionally validated against
  the CDDL with an independent tool. Codec dependency upgrades are treated
  as format-affecting changes, permitted only when the golden vectors
  continue to pass.

# References

[^BCP14]: BCP 14: RFC 2119 and RFC 8174, Key words for use in RFCs.
[^RFC8949]: RFC 8949: Concise Binary Object Representation (CBOR). STD 94.
[^RFC8610]: RFC 8610: Concise Data Definition Language (CDDL).
[^RFC9052]: RFC 9052: CBOR Object Signing and Encryption (COSE): Structures.
[^ZIP32]: ZIP 32: Shielded Hierarchical Deterministic Wallets.
[^ZIP200]: ZIP 200: Network Upgrade Mechanism.
[^ZIP315]: ZIP 315: Best Practices for Wallet Handling of Multiple Pools.
[^ZIP316]: ZIP 316: Unified Addresses and Unified Viewing Keys.
[^ZIP320]: ZIP 320: Defining an Address Type to which funds can only be sent
  from Transparent Addresses.
[^ZIPRAW]: Unified raw encodings (draft ZIP).
  https://github.com/zcash/zips/pull/660
[^PROTOCOL]: Zcash Protocol Specification, section "Encodings of Addresses
  and Keys".
[^AGE]: age: a simple, modern and secure file encryption format.
  https://age-encryption.org/v1
