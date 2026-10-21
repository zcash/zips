```
ZIP: Unassigned
Title: Shielded Voting Wallet API
Owners: Dev Ojha <dojha@berkeley.edu>
        Adam Tucker <adamleetucker@outlook.com>
        Roman Akhtariev <ackhtariev@gmail.com>
        Greg Nagy <greg@dhamma.works>
Status: Draft
Category: Standards / Wallet
Created: 2026-03-24
License: MIT
Pull-Request: <https://github.com/zcash/zips/pull/1244>
```

# Terminology

The key words "MUST", "MUST NOT", "SHOULD", and "MAY" in this document
are to be interpreted as described in BCP 14 [^BCP14] when, and only
when, they appear in all capitals.

The terms below are to be interpreted as follows:

Vote round

: A time-bounded voting session defining a set of proposals, a Zcash
  snapshot height, and a deadline. Wallet clients interact with exactly
  one vote round at a time.

Delegation

: The act of proving ownership of unspent Orchard notes at the snapshot
  height and registering a vote authority note on the vote commitment
  tree. See [^orchard-balance-proof].

Vote authority note (VAN)

: A note appended to the vote commitment tree during delegation. The VAN
  carries the delegated vote weight and is consumed (nullified) when
  the holder casts a vote.

Vote commitment tree

: An append-only Merkle tree that records vote authority notes and vote
  commitments. The tree root at a given block height serves as a public
  input to zero-knowledge proof verification.

Share

: A fragment of the holder's delegated vote weight, encrypted and
  submitted to helper servers rather than directly to the chain to
  prevent timing-based linkability.

# Abstract

This ZIP specifies the REST API endpoints, wire formats, and discovery
mechanism that wallet clients use to participate in shielded on-chain
voting rounds. It covers vote round discovery via a per-vote
configuration document, data query endpoints for reading chain state,
transaction submission endpoints for delegation and vote casting, and
the encoding conventions for all exchanged data.

# Motivation

The shielded voting protocol involves multiple ZIPs that specify the
cryptographic circuits [^voting-protocol], nullifier retrieval
[^nullifier-pir], proof-of-balance [^orchard-balance-proof], share
submission [^submission-server], and election authority key ceremony
[^ea-ceremony]. A wallet integrator currently must read several of these
specifications to understand which endpoints to call, what wire formats
to use, and how to discover an active vote.

This ZIP consolidates the wallet-facing API surface into a single
document, specifying the REST endpoints, JSON wire formats, encoding
conventions, and discovery mechanism needed to participate in a vote.

Versioning fields in the vote configuration allow the protocol to evolve
(new PIR schemes, circuit versions, tally methods) while maintaining
backwards compatibility with deployed wallets.

# Requirements

- A wallet can discover and join an active voting round using a published
configuration document.
- A wallet can submit delegation and vote commitment transactions
using the wire formats in this specification. Proof construction is
specified in companion ZIPs.
- A wallet can submit encrypted vote shares to helper servers and
confirm their on-chain inclusion.
- Each protocol component (vote server, vote protocol, tally method,
PIR) can be versioned and upgraded independently. A change to one
component has no impact on other components or the configuration schema.

# Non-requirements

- Validator onboarding, key registration, and EA key ceremony.
- Chain consensus rules and block production.
- Round creation and governance authority operations.
- The internal implementation of helper servers (specified in
[^submission-server]).

# High level summary

This section is non-normative.

This section provides an informational overview of the end-to-end
sequence a wallet follows to participate in a shielded voting round.
Each step references the normative section that specifies its details.
All requirements use the language defined in those sections.

The vote configuration itself is versioned by `config_version`, which
tracks the schema of the configuration document. It also carries four
independently versioned protocol components:

- **`vote_protocol`** — the ZKP circuits (ZKP1, ZKP2, ZKP3) and
  commitment tree structure. The circuits are designed to be
  upgradeable: a new circuit version bumps `vote_protocol` without
  affecting the other components.
- **`tally`** — threshold decryption and result aggregation.
- **`pir`** — the nullifier PIR retrieval scheme.
- **`vote_server`** — the helper server API that vote shares are submitted to.

See [Version Handling] for the normative rules.

## Discovery and Validation

1. **Obtain vote configuration.** Fetch or receive the vote
   configuration JSON document for the round.
   See [Vote Configuration Format].

2. **Validate configuration.** Check all fields against the rules in
   [Validation Rules] and verify version compatibility per
   [Compatibility Rules]. Reject the configuration and stop if any
   check fails.

3. **Fetch active round from chain.** Query `GET /shielded-vote/v1/rounds/active`
   to confirm the round is ACTIVE and retrieve on-chain parameters:
   `ea_pk`, `nullifier_imt_root`, `nc_root`, and `proposals_hash`.
   See [Active Round].

4. **Verify proposals hash.** Compute the proposals hash from the
   configuration's `proposals` array and compare it to `proposals_hash`
   from the chain response. See [Proposals Hash].

## Delegation

5. **Retrieve nullifier exclusion proofs.** Connect to a
   `pir_endpoints` server and retrieve Merkle non-membership proofs
   for the wallet's Orchard note nullifiers at `snapshot_height`.
   See [Nullifier Retrieval] and [^nullifier-pir].

6. **Construct and submit delegation transaction.** Build the ZKP1
   proof (proving Orchard note ownership at the snapshot height) and
   submit via `POST /shielded-vote/v1/delegate-vote`.
   See [Delegation Transaction] and [^orchard-balance-proof].

7. **Poll for delegation confirmation.** Poll
   `GET /shielded-vote/v1/tx/{hash}` using the `tx_hash` from the
   submission response until the response includes a non-empty `height`
   and `code` = 0. See [Confirmation Polling].

8. **Sync commitment tree and locate VAN.** Query the
   [Commitment Tree Leaves] endpoint to incrementally sync the local
   tree. Identify the wallet's vote authority note by its commitment
   `van_cmx` computed during step 6.

## Voting (repeat for each proposal)

9. **Construct and submit vote commitment.** Build the ZKP2 proof
   (consuming the current VAN and producing a new VAN) and submit
   via `POST /shielded-vote/v1/cast-vote`. The tree root at the
   anchor height is a public input to this proof.
   See [Vote Commitment Transaction] and [^voting-protocol].

10. **Poll for vote commitment confirmation.** Poll
    `GET /shielded-vote/v1/tx/{hash}` until confirmed.

11. **Sync commitment tree.** Query [Commitment Tree Leaves] again
    to locate the new VAN (needed as input for the next proposal)
    and the vote commitment leaf (needed for share construction).

12. **Construct and submit shares.** Build 16 encrypted share
    payloads and submit each to a helper server via
    `POST /shielded-vote/v1/shares`. Each share references the
    `tree_position` of the vote commitment leaf from step 11.
    See [Share Delegation] and [^submission-server].

13. **Poll share statuses.** For each submitted share, poll
    `GET /shielded-vote/v1/share-status/{roundId}/{nullifier}` until
    all return `"confirmed"`. See [Share Status].

Steps 9 through 13 are repeated sequentially for each proposal in
the round. Each iteration consumes the current VAN and produces a
new one, so proposals cannot be voted on in parallel.

## Results (optional)

14. **View tally results.** After the round reaches FINALIZED status,
    query `GET /shielded-vote/v1/tally-results/{round_id}` for
    decrypted per-proposal tallies. See [Tally Results].

# Specification

## Vote Discovery

A vote configuration is a JSON document published for each vote round.
It contains all parameters a wallet needs to locate services and
participate in the round.

### Vote Configuration Format

```json
{
  "config_version": 1,
  "vote_round_id": "<hex, 64 characters>",
  "vote_servers": [
    {"url": "https://vote1.example.com", "label": "validator-1"}
  ],
  "pir_endpoints": [
    {"url": "https://pir1.example.com", "label": "pir-1"}
  ],
  "snapshot_height": 2800000,
  "vote_end_time": 1735689600,
  "proposals": [
    {
      "id": 1,
      "title": "Approve protocol upgrade",
      "description": "Approve or oppose the proposed protocol upgrade.",
      "options": [
        {"index": 0, "label": "Support"},
        {"index": 1, "label": "Oppose"}
      ]
    }
  ],
  "supported_versions": {
    "pir": ["v0", "v1"],
    "vote_protocol": "v0",
    "tally": "v0",
    "vote_server": "v1"
  }
}
```

### Field Definitions


| Field                              | Type             | Description                                                                                                                    |
| ---------------------------------- | ---------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| `config_version`                   | integer          | Schema version of this configuration document. Currently 1.                                                                    |
| `vote_round_id`                    | string           | Hex-encoded 32-byte vote round identifier (64 characters, lowercase).                                                          |
| `vote_servers`                     | array            | One or more vote server base URLs serving both chain and helper endpoints. Each entry has `url` (string) and `label` (string). |
| `pir_endpoints`                    | array            | One or more nullifier PIR server base URLs. Each entry has `url` and `label`.                                                  |
| `snapshot_height`                  | integer          | Zcash block height at which the Orchard pool snapshot was taken.                                                               |
| `vote_end_time`                    | integer          | Unix timestamp (seconds) after which votes are no longer accepted.                                                             |
| `proposals`                        | array            | Ordered list of proposals. Each has `id` (integer, 1-indexed), `title` (string), `description` (string), and `options` (array of `{index, label}`). |
| `supported_versions.pir`           | array of strings | PIR retrieval scheme versions supported by the servers (e.g., `["v0", "v1"]`).                                                 |
| `supported_versions.vote_protocol` | string           | Vote protocol version covering the ZKP circuits and commitment tree structure (e.g., `"v0"`).                                  |
| `supported_versions.tally`         | string           | Tally method version covering threshold decryption and result aggregation (e.g., `"v0"`).                                      |
| `supported_versions.vote_server`   | string           | Vote server version covering the REST API (e.g., `"v1"`).                                                                      |


### Validation Rules

A wallet MUST validate the configuration before use:

- `config_version` MUST be a version the wallet recognizes. This
specification defines version 1.
- `vote_round_id` MUST be exactly 64 lowercase hexadecimal characters.
- `vote_servers` MUST contain at least one entry.
- `pir_endpoints` MUST contain at least one entry.
- `snapshot_height` MUST be greater than 0.
- `proposals` MUST contain between 1 and 15 entries.
- Each proposal MUST have between 2 and 8 options.
- Proposal `id` values MUST be unique and in the range 1 to 15.
- Option `index` values within a proposal MUST be unique and 0-indexed.
- The wallet MUST check version compatibility as specified in
[Version Handling]. In summary: `supported_versions.vote_server`,
`supported_versions.vote_protocol`, and `supported_versions.tally`
MUST be recognized versions; `supported_versions.pir` MUST contain
at least one version the wallet supports.

### Distribution

The vote configuration is published out-of-band for each vote round.
Distribution mechanisms include:

- A developer-merged pull request to a well-known repository linking
to the configuration file.
- A CDN or API endpoint serving the configuration.
- Bundling the configuration within a wallet release.

The choice of distribution mechanism is outside the scope of this
specification. Regardless of the mechanism, the wallet MUST validate the
configuration as described above before using it.

## Data Query Endpoints

All query endpoints are served relative to a `vote_servers` base URL
from the vote configuration. Responses are JSON-serialized protobuf
messages; byte fields are base64-encoded.

### Active Round

```
GET /shielded-vote/v1/rounds/active
```

Returns the active voting round, if any.

**Response body:** A JSON object containing a `round` field with the
`VoteRound` structure:


| Field                | Type              | Description                                                          |
| -------------------- | ----------------- | -------------------------------------------------------------------- |
| `vote_round_id`      | base64 (32 bytes) | Round identifier.                                                    |
| `snapshot_height`    | uint64            | Zcash snapshot block height.                                         |
| `snapshot_blockhash` | base64 (32 bytes) | Zcash block hash at snapshot.                                        |
| `proposals_hash`     | base64 (32 bytes) | SHA-256 hash of the proposals array (see [Proposals Hash]).          |
| `vote_end_time`      | uint64            | Unix timestamp (seconds).                                            |
| `nullifier_imt_root` | base64 (32 bytes) | Nullifier non-membership tree root.                                  |
| `nc_root`            | base64 (32 bytes) | Orchard note commitment tree root.                                   |
| `status`             | uint32            | Session status enum (4=PENDING, 1=ACTIVE, 2=TALLYING, 3=FINALIZED).  |
| `ea_pk`              | base64 (32 bytes) | Election authority public key (compressed Pallas point).             |
| `proposals`          | array             | Proposals with `id` (uint32), `title`, `description`, and `options`. |
| `description`        | string            | Human-readable round description.                                    |
| `title`              | string            | Short human-readable round title.                                    |
| `creator`            | string            | Address of the account that created the session.                     |
| `created_at_height`  | uint64            | Vote chain block height at which the round was created.              |


The response may contain additional fields related to the EA key
ceremony and threshold decryption (e.g., ceremony status, validator
keys, ECIES payloads). These fields exist for validator coordination
and have no bearing on wallet operations, so they are not documented
here. See [^ea-ceremony] for details.

The `proposals` field in the VoteRound response contains the same
proposals as the vote configuration document. The `proposals_hash`
field can be used to verify consistency between the two sources.

### Proposals Hash

The `proposals_hash` is SHA-256 over the canonical JSON serialization
of the `proposals` array, allowing wallets to verify that the
proposals shown to the user match those on the vote chain.

To compute: construct a JSON array of proposal objects containing
`id`, `title`, `description`, and `options` (each with `index`, `label`),
ordered by `id` then `index` ascending, with object keys in the order
listed. Serialize with no whitespace and SHA-256 the UTF-8 result. The
JSON serialization MUST NOT escape the forward slash character (`/`);
non-ASCII characters are emitted as UTF-8 bytes, not as `\uXXXX`
escapes. Control characters (U+0000 through U+001F) are escaped per
RFC 8259 (`\b`, `\f`, `\n`, `\r`, `\t`, or `\u00XX`).

Example preimage (from [Vote Configuration Format]):

```
[{"id":1,"title":"Approve protocol upgrade","description":"Approve or oppose the proposed protocol upgrade.","options":[{"index":0,"label":"Support"},{"index":1,"label":"Oppose"}]}]
```

SHA-256 of the above preimage: `3f9a361d43c4ddb77ad138a091374e2e2958718e64937f33df99a09bd567e63d`.

Wallets SHOULD verify `proposals_hash` against the vote
configuration before proceeding.

If no active round exists, the response contains a `round` field with
a null or empty value.

### Round Details

```
GET /shielded-vote/v1/round/{round_id}
```

Returns details for a specific vote round.

**Path parameters:**

- `round_id`: Hex-encoded 32-byte vote round identifier (64 characters).

**Response body:** Same `VoteRound` structure as [Active Round].

### List Rounds

```
GET /shielded-vote/v1/rounds
```

Returns all stored vote rounds.

**Response body:** A JSON object containing a `rounds` array of
`VoteRound` structures.

### Commitment Tree (Latest)

```
GET /shielded-vote/v1/commitment-tree/{round_id}/latest
```

Returns the latest commitment tree state for a round.

**Path parameters:**

- `round_id`: Hex-encoded 32-byte vote round identifier.

**Response body:** A JSON object containing a `tree` field:


| Field                | Type              | Description                                   |
| -------------------- | ----------------- | --------------------------------------------- |
| `next_index`         | uint64            | Next leaf index to be written.                |
| `root`               | base64 (32 bytes) | Current Merkle root.                          |
| `height`             | uint64            | Block height at which this root was computed. |
| `next_index_at_root` | uint64            | `next_index` at the time the root was stored. |


### Commitment Tree at Height

```
GET /shielded-vote/v1/commitment-tree/{round_id}/{height}
```

Returns the commitment tree state at a specific block height.

**Path parameters:**

- `round_id`: Hex-encoded 32-byte vote round identifier.
- `height`: Block height (decimal integer).

**Response body:** Same `CommitmentTreeState` structure as
[Commitment Tree (Latest)].

### Commitment Tree Leaves

```
GET /shielded-vote/v1/commitment-tree/{round_id}/leaves?from_height=X&to_height=Y
```

Returns commitment tree leaves appended in blocks within the specified
height range. Used by wallet clients to incrementally sync the local
copy of the vote commitment tree.

**Path parameters:**

- `round_id`: Hex-encoded 32-byte vote round identifier.

**Query parameters:**

- `from_height`: Start block height (inclusive).
- `to_height`: End block height (inclusive).

**Response body:** A JSON object containing a `blocks` array. Each
entry represents one block:


| Field         | Type                       | Description                                                         |
| ------------- | -------------------------- | ------------------------------------------------------------------- |
| `height`      | uint64                     | Block height.                                                       |
| `start_index` | uint64                     | Index of the first leaf appended in this block.                     |
| `leaves`      | array of base64 (32 bytes) | Commitment leaves (Pallas base field elements, little-endian each). |


### Tally Results

```
GET /shielded-vote/v1/tally-results/{round_id}
```

Returns finalized (decrypted) tally results for a vote round. Only
available after the round reaches FINALIZED status.

**Path parameters:**

- `round_id`: Hex-encoded 32-byte vote round identifier.

**Response body:** A JSON object containing a `results` array:


| Field           | Type              | Description                          |
| --------------- | ----------------- | ------------------------------------ |
| `vote_round_id` | base64 (32 bytes) | Round identifier.                    |
| `proposal_id`   | uint32            | Proposal identifier.                 |
| `vote_decision` | uint32            | Vote option index.                   |
| `total_value`   | uint64            | Decrypted aggregate value (zatoshi). |


### Transaction Status

```
GET /shielded-vote/v1/tx/{hash}
```

Returns the confirmation status of a previously submitted transaction.

**Path parameters:**

- `hash`: Hex-encoded transaction hash.

**Response body:**


| Field    | Type   | Description                                                            |
| -------- | ------ | ---------------------------------------------------------------------- |
| `height` | string | Block height at which the transaction was included (empty if pending). |
| `code`   | uint32 | Result code (0 = success).                                             |
| `log`    | string | Error message if `code` is non-zero.                                   |
| `events` | array  | ABCI events emitted by the transaction.                                |


## Delegation Transaction

The delegation transaction registers a holder's vote weight on the vote
commitment tree. It corresponds to ZKP1 (the delegation circuit) as
specified in [^orchard-balance-proof] and [^voting-protocol].

### Endpoint

```
POST /shielded-vote/v1/delegate-vote
```

### Request Body

A JSON object with the following fields:


| Field                   | Type                            | Description                                                                |
| ----------------------- | ------------------------------- | -------------------------------------------------------------------------- |
| `rk`                    | base64 (32 bytes)               | Randomized spend authorization verification key (compressed Pallas point). |
| `spend_auth_sig`        | base64 (64 bytes)               | RedPallas spend authorization signature.                                   |
| `signed_note_nullifier` | base64 (32 bytes)               | Nullifier of the dummy signed note.                                        |
| `cmx_new`               | base64 (32 bytes)               | Output note commitment (extracted x-coordinate).                           |
| `van_cmx`               | base64 (32 bytes)               | Vote authority note commitment (extracted x-coordinate).                   |
| `gov_nullifiers`        | array of base64 (32 bytes each) | Governance nullifiers (up to 5). One per claimed note.                     |
| `proof`                 | base64 (variable)               | Halo 2 ZKP1 proof.                                                         |
| `vote_round_id`         | base64 (32 bytes)               | Vote round identifier.                                                     |
| `sighash`               | base64 (32 bytes)               | Client-computed sighash for signature verification.                        |


### Sighash

The `sighash` field is the 32-byte ZIP 244 [^zip-244] shielded sighash
extracted from the signed PCZT after the hardware wallet signing flow.
The chain verifies the `spend_auth_sig` against this client-provided
sighash; it does not recompute it. See [^orchard-balance-proof] for the
PCZT construction and signing flow that produces the sighash.

### Response

All transaction submission endpoints return the same response format:

```json
{
  "tx_hash": "<hex-encoded transaction hash>",
  "code": 0,
  "log": ""
}
```


| Field     | Type         | Description                                                             |
| --------- | ------------ | ----------------------------------------------------------------------- |
| `tx_hash` | string (hex) | Transaction hash for status polling.                                    |
| `code`    | uint32       | Result code. 0 indicates the transaction was accepted into the mempool. |
| `log`     | string       | Error description when `code` is non-zero. Omitted on success.          |


## Vote Commitment Transaction

The vote commitment transaction casts a vote on a specific proposal. It
corresponds to ZKP2 (the vote commitment circuit) as specified in
[^voting-protocol].

### Endpoint

```
POST /shielded-vote/v1/cast-vote
```

### Request Body

A JSON object with the following fields:


| Field                          | Type              | Description                                                   |
| ------------------------------ | ----------------- | ------------------------------------------------------------- |
| `van_nullifier`                | base64 (32 bytes) | Nullifier of the vote authority note being consumed.          |
| `vote_authority_note_new`      | base64 (32 bytes) | New vote authority note commitment.                           |
| `vote_commitment`              | base64 (32 bytes) | Vote commitment (Poseidon hash binding the vote).             |
| `proposal_id`                  | uint32            | Proposal identifier (1 to 15).                                |
| `proof`                        | base64 (variable) | Halo 2 ZKP2 proof.                                            |
| `vote_round_id`                | base64 (32 bytes) | Vote round identifier.                                        |
| `vote_comm_tree_anchor_height` | uint64            | Block height of the vote commitment tree root used as anchor. |
| `vote_auth_sig`                | base64 (64 bytes) | RedPallas signature under the randomized voting key.          |
| `r_vpk`                        | base64 (32 bytes) | Randomized voting public key (compressed Pallas point).       |


### Response

Same response format as [Delegation Transaction].

## Share Delegation

After casting a vote commitment, the wallet constructs encrypted share
payloads and submits them to helper servers. The helper server queues
each share and submits it to the chain at the client-specified time.
See [^submission-server] for the server-side processing pipeline and
[^voting-protocol] for share construction.

The following endpoints are served from the same `vote_servers` base
URLs as the chain query endpoints.

### Submit Share

```
POST /shielded-vote/v1/shares
```

Submits a single encrypted vote share to a helper server.

**Request body:** A JSON object with the following fields:


| Field           | Type                            | Description                                                                                                                                            |
| --------------- | ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `shares_hash`   | base64 (32 bytes)               | Poseidon hash committing to all shares in this vote.                                                                                                   |
| `proposal_id`   | uint32                          | Proposal identifier (1-indexed).                                                                                                                       |
| `vote_decision` | uint32                          | Vote option index (0-indexed).                                                                                                                         |
| `enc_share`     | object                          | Encrypted share (see below).                                                                                                                           |
| `tree_position` | uint64                          | Vote commitment tree leaf index.                                                                                                                       |
| `vote_round_id` | string (hex, 64 chars)          | Hex-encoded vote round identifier.                                                                                                                     |
| `share_comms`   | array of base64 (32 bytes each) | 16 per-share Poseidon commitments.                                                                                                                     |
| `primary_blind` | base64 (32 bytes)               | Blinding factor for the revealed share.                                                                                                                |
| `submit_at`     | uint64                          | Unix timestamp (seconds) at which the helper should submit this share to the chain. 0 means submit at the last possible moment before `vote_end_time`. |


The `enc_share` object contains:


| Field         | Type              | Description                                                  |
| ------------- | ----------------- | ------------------------------------------------------------ |
| `c1`          | base64 (32 bytes) | ElGamal ciphertext component `C1` (compressed Pallas point). |
| `c2`          | base64 (32 bytes) | ElGamal ciphertext component `C2` (compressed Pallas point). |
| `share_index` | uint32            | Share index (0 to 15).                                       |


**Response body:**

```json
{"status": "queued"}
```


| Field    | Type   | Description                                                |
| -------- | ------ | ---------------------------------------------------------- |
| `status` | string | `"queued"` if accepted, `"duplicate"` if already received. |
| `error`  | string | Error description (present only on failure).               |


### Share Nullifier

Each submitted share has a deterministic nullifier derived from the
vote commitment fields and the share's blinding factor. The wallet
computes this nullifier locally and hex-encodes it (lowercase, 64
characters) for use in the [Share Status] endpoint path. The
derivation is specified in [^voting-protocol].

### Share Status

```
GET /shielded-vote/v1/share-status/{roundId}/{nullifier}
```

Polls whether a submitted share has been included on-chain.

**Path parameters:**

- `roundId`: Hex-encoded 32-byte vote round identifier (64 characters).
- `nullifier`: Hex-encoded 32-byte share nullifier (64 characters),
  computed as specified in [Share Nullifier].

**Response body:**

```json
{"status": "pending"}
```


| Field    | Type   | Description                                                                                       |
| -------- | ------ | ------------------------------------------------------------------------------------------------- |
| `status` | string | `"pending"` if not yet on-chain, `"confirmed"` if the share nullifier has been recorded on-chain. |


## Vote Commitment Tree

The vote commitment tree is an append-only Merkle tree that records
vote authority notes and vote commitments.

The vote commitment tree structure, hash function, and leaf encoding
are specified in [^voting-protocol]. Wallet clients interact with the
tree through the query endpoints defined in [Commitment Tree (Latest)],
[Commitment Tree at Height], and [Commitment Tree Leaves].

## Private Information Retrieval Nullifier Exclusion Proofs

Nullifier exclusion proofs are retrieved using the PIR protocol
specified in [^nullifier-pir]. The wallet connects to one of the
`pir_endpoints` from the vote configuration; version selection
follows the rules in [Version Handling].

## Version Handling

All version strings in `supported_versions` use the form `"v" MAJOR`
(e.g., `"v0"`, `"v1"`). A major version bump indicates a
breaking change; within the same major version, implementations remain
compatible.

A wallet MUST reject the configuration if it does not support the
advertised `vote_server`, `vote_protocol`, or `tally` version, or if
`pir` contains no version it supports. If any check fails, the wallet
MUST NOT proceed and SHOULD prompt the user to update.

### URL Path Prefix

REST endpoint paths include a version prefix (e.g.,
`/shielded-vote/v1/`). The path version corresponds to the major
version declared in `supported_versions.vote_server`. A `vote_server`
value of `"v1"` uses the `/shielded-vote/v1/` prefix.

### Relationship to `config_version`

`config_version` versions the structure of the vote configuration JSON
document itself (field names, types, nesting). The component versions
(`vote_server`, `vote_protocol`, `tally`, `pir`) version protocol
behavior. These can all evolve independently: a structural change to
the config schema (e.g., adding a new required top-level field) bumps
`config_version`, while a change to endpoint behavior bumps
`vote_server`, a change to circuits or tree structure bumps
`vote_protocol`, and a change to decryption or aggregation bumps
`tally`.

## Transaction Lifecycle

### Broadcast Semantics

Transaction submission endpoints (`/delegate-vote`, `/cast-vote`)
return synchronously after initial validation. A successful response
(HTTP 200, `code` = 0) indicates that the transaction passed validation
and entered the mempool. It does not guarantee inclusion in a block.

### Confirmation Polling

After receiving a successful broadcast response, the wallet SHOULD poll
the [Transaction Status] endpoint using the `tx_hash` from the response.
The transaction is confirmed when the response includes a non-empty
`height` and `code` = 0.

### Timeouts

Transaction validation includes zero-knowledge proof verification,
which may take 30 to 60 seconds. Wallet HTTP clients SHOULD use a
timeout of at least 120 seconds for transaction submission requests.

## Encoding Conventions

All data exchanged between wallet clients and servers uses the encodings
described in this section.

### Cryptographic Types


| Type                      | Size     | Encoding                                                                                                     |
| ------------------------- | -------- | ------------------------------------------------------------------------------------------------------------ |
| Pallas base field element | 32 bytes | Little-endian canonical representation. Implementations MUST reject values >= the Pallas base field modulus. |
| Compressed Pallas point   | 32 bytes | Standard Pallas point compression. [^protocol]                                                               |
| ElGamal ciphertext        | 64 bytes | `C1` (32 bytes) followed by `C2` (32 bytes), each a compressed Pallas point.                                 |
| Halo 2 proof              | variable | Opaque byte sequence.                                                                                        |
| RedPallas signature       | 64 bytes | `R` (32 bytes) followed by `s` (32 bytes).                                                                   |


### JSON Encoding

All REST endpoints accept and return `application/json`.

- **Byte arrays**: Standard base64 encoding with padding (RFC 4648
Section 4 [^rfc4648]).
- **`vote_round_id`**: The encoding of `vote_round_id` varies by
context. The following table lists every occurrence and its encoding:

| Context                                         | Encoding                      |
| ----------------------------------------------- | ----------------------------- |
| Vote configuration JSON (`vote_round_id` field) | Hex (64 lowercase characters) |
| URL path parameters (`{round_id}`, `{roundId}`) | Hex (64 lowercase characters) |
| Delegation request body (`vote_round_id`)       | Base64 (32 bytes)             |
| Vote commitment request body (`vote_round_id`)  | Base64 (32 bytes)             |
| Share submission request body (`vote_round_id`) | Hex (64 lowercase characters) |
| Chain query response bodies (`vote_round_id`)   | Base64 (32 bytes)             |
- **Integers**: JSON numbers. Fields typed `uint32` or `uint64` in the
protocol definition are encoded as JSON numbers.
- **Enumerations**: JSON numbers corresponding to the protobuf enum
value (e.g., `SESSION_STATUS_ACTIVE` = 1).

# Rationale

## Unified Vote Servers

All endpoints — chain queries, transaction submission, and share
submission — are served under the `/shielded-vote/v1/` path prefix
from the same `vote_servers` base URLs. In the current architecture,
a single `svoted` process hosts every endpoint on the same port, so a
separate helper URL is unnecessary.

## Independent Component Versions

Each `supported_versions` field tracks a component that can change on
its own schedule: `vote_server` covers the REST API surface,
`vote_protocol` covers the ZKP circuits and commitment tree structure,
`tally` covers threshold decryption and result aggregation, and `pir`
covers nullifier retrieval. Separating these avoids forcing a
wallet update when only one component changes — for example, a new
tally method does not require wallets to update their proof generation
code.

## JSON over Protobuf

The REST API uses JSON encoding rather than binary protobuf serialization.
JSON is broadly supported across wallet development stacks (Swift, Kotlin,
TypeScript, Rust) and does not require protobuf code generation. The
trade-off in message size is acceptable for the request and response
volumes involved.

# Open issues

# Reference implementation

A reference implementation of the vote chain REST API and helper server
is available at
[valargroup/vote-sdk](https://github.com/valargroup/vote-sdk).

# References

[^BCP14]: [Information on BCP 14 -- "RFC 2119: Key words for use in RFCs to Indicate Requirement Levels" and "RFC 8174: Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words"](https://www.rfc-editor.org/info/bcp14)

[^protocol]: [Zcash Protocol Specification, Version 2025.6.3 [NU6.1] or later](protocol/protocol.pdf)

[^protocol-poseidon]: [Zcash Protocol Specification, Version 2025.6.3 [NU6.1]. Section 5.4.2: Pseudo Random Functions](protocol/protocol.pdf#concreteprfs)

[^rfc4648]: [RFC 4648: The Base16, Base32, and Base64 Data Encodings](https://www.rfc-editor.org/rfc/rfc4648)

[^voting-protocol]: [Draft ZIP: Shielded Voting Protocol](draft-valargroup-shielded-voting.md)

[^nullifier-pir]: [Draft ZIP: Private Information Retrieval for Nullifier Exclusion Proofs](draft-valargroup-nullifier-pir.md)

[^submission-server]: [Draft ZIP: Shielded Voting Submission Server](draft-valargroup-submission-server.md)

[^orchard-balance-proof]: [Draft ZIP: Orchard Proof-of-Balance](draft-valargroup-orchard-balance-proof.md)

[^ea-ceremony]: [Draft ZIP: Election Authority Key Ceremony](draft-valargroup-ea-key-ceremony.md)

[^zip-244]: [ZIP 244: Transaction Identifier Non-Malleability](zip-0244.rst)
