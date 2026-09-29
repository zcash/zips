    ZIP: XXX
    Title: Circle STARK Verification as a Transparent Zcash Extension
    Owners: Abdel <abdel.dev.bitcoin@proton.me>
            Michael Zaikin <michael.z@starkware.co>
    Status: Draft
    Category: Consensus
    Created: 2025-10-14
    License: MIT
    Discussions-To: <https://forum.zcashcommunity.com/t/stark-verification-as-a-transparent-zcash-extension-tze-i-e-enabler-for-a-starknet-style-l2-on-zcash/52486>

# Terminology

The key words "MUST", "SHOULD", and "MAY" are to be interpreted as described in BCP 14 [^BCP14] when, and only when, they appear in all capitals.

## Abstract

This ZIP defines a new Transparent Zcash Extension that verifies a bounded‑size Circle STARK [^circle-stark-paper] proof. The extension has a single `type` and a single mode, and exposes a compact precondition/witness interface suitable for verifying validity proofs of a Starknet-style scaling solution [^sn-stack] on Zcash. It specifies:

- a prefix‑free encoding of precondition and witness;
- pinned verifier parameter set via a `param_id` namespace;
- strict consensus bounds on sizes and verifier parameters for DoS safety; and
- digest integration consistent with a future transaction version that supports TZEs [^zip-0245].

This ZIP does not change Sapling/Orchard; it only adds a TZE that can be used to enforce state transition of a Starknet chain or other validity claims.

## Motivation

Zcash's programmability is restricted by the Bitcoin script, which lacks sufficient expressiveness and implies high costs that limit throughput. A Starknet‑style scaling solution can address the issue by providing an expressive programming language (Cairo [^cairo-paper]), a ZK friendly virtual machine, and an effective proving system (Stwo [^stwo]) that compresses large computation into a succinct proof, suitable for onchain verification. A custom transparent extension [^zip-0222] is the cleanest way to introduce such verifier and enable scaling solutions on top of Zcash.

## Requirements

* Define a TZE `type` for Stwo/Circle STARK verification, and fully specify how this type is to be encoded, verified, and integrated into transaction digest computation, without allowing implementation‑defined behavior.
* Define a `param_id` namespace that pins the specification of the Stwo proof relation, the proof object format, field encodings, transcript/Merkle hash suite and personalization, FRI expansion and query caps, any grinding bounds, and any batch‑verification settings.
* A reference implementation of the prover and verifier, and reference test vectors (valid and invalid) must be provided for each such `param_id`.
* Limits on proof sizes, etc. must be chosen to avoid potential denial of service, and the necessary updates to ZIP 317 fee calculation [^zip-0317] must be specified.

## Specification

### TZE identification

- `tze_id`: TBD (assigned by ZIP Editors).
- `tze_mode`: 0 (only one mode is defined by this ZIP). Any other value MUST be rejected. 

All serialization below is inside the `tze_data_payload` defined by [^zip-0222]; lengths are `compactSize`.

### Precondition (prefix‑free)

```
u16  param_id         // selects a pinned Stwo verifier parameter set (see below)
u8   flags            // bit 0 = bind_ctx; all other bits MUST be 0
vec  pub_in           // public inputs to the proved statement (len + bytes)
if (flags & 0x01) {
    bytes32 ctx_digest   // non-malleable transaction digest
}
```

- `param_id` selects an enumerated, pinned Stwo parameter set. Unknown `param_id` MUST be rejected.
- `pub_in` is an opaque byte string to consensus; it MUST be absorbed by the verifier transcript exactly as specified (byte‑for‑byte).
- If `bind_ctx` is set, `ctx_digest` MUST equal the transaction's non‑malleable digest [^zip-0244]. A mismatch MUST cause rejection.

### Witness (prefix‑free)

```
vec  proof            // the Stwo (Circle STARK) proof object (len + bytes)
```

The `proof` MUST conform to the Stwo proof object format pinned by `param_id`.

### Verification

`bool tze_verify(0, precondition, witness, context)`:

1. Parse `param_id`; load the exact pinned parameter set. Reject if unknown.
2. Parse `flags`; if any reserved bits set, reject.
3. If `bind_ctx`, compute the required `ctx_digest` from `context` and compare; on mismatch, reject. ([Zcash Zips][3])
4. Parse `pub_in` and `proof`. Enforce all consensus bounds (see Bounds).
5. Initialize the Stwo transcript/channel, **absorb `pub_in` exactly**, and verify `proof` using the parameters pinned by `param_id`.
6. Return `true` iff the verifier accepts; otherwise return `false`.

### Parameter sets (`param_id`)

The namespace is 16‑bit (0x0001..0xFFFF). This ZIP introduces:

- `param_id = 0x0001` — `STWO_V1_P1`

  - Upstream: `starkware-libs/stwo` [^stwo-repo] at tag TBD, commit `TBD`.
  - Proving system: Stwo [^stwo] based on Circle STARK over the 31‑bit Mersenne field [^circle-stark-paper]
  - Proof format:
    - Stwo proof structure layout (TBD)
    - Binary codec and compression algorithm (TBD)
  - Prover parameters:
    - Stwo channel hash function (TBD)
    - Stwo preprocessed AIR configuration (TBD)
    - PoW difficulty target (TBD)
    - FRI configuration (TBD)

> Normative reference material for `STWO_V1_P1` (encodings, proof format, prover parameters) is included alongside this ZIP in `zip-XXXX/params/STWO_V1_P1.json` and the accompanying test vectors. These files are to be treated as normative parts of this specification.

Future parameter sets (e.g., different hash suite or query caps) **MAY** be proposed under new `param_id`s in a subsequent ZIP.

### Bounds (consensus)

Let the following consensus constants be defined for this `(type, mode)`:

- `PUBIN_MAX_BYTES = TBD` (discussion range: ≤ 4096).
- `PROOF_MAX_BYTES = TBD` (discussion range: 64–192 KiB; finalize from measurements on realistic proof instances).

Nodes MUST reject if any bound is exceeded, and MUST NOT allow denial of service via memory exhaustion due to allocating memory before bounds are checked.

### Fee model

Follows ZIP-317 [^zip-0317].

TODO: introduce an adapted fee model with discounted price per byte (rationale: large proof size does not reflect the cost of the verification)

TODO: introduce a rate limiting policy that prevents crowding out non-TZE transactions

## Rationale

- TZE over opcodes: Zcash's extensibility surface for new consensus checks is TZE [^zip-0222]. It avoids entangling with shielded circuit changes and keeps the change set minimal and auditable.
- Single system first: Limiting to Stwo keeps the ZIP focused and uses a Rust verifier that integrates cleanly with Zebra and (via FFI) with zcashd. We can consider additional systems (or new Stwo parameter sets) later via new `param_id`s or a new `type`.
- Optional context binding: Allowing `bind_ctx` covers common safe usage (proof binds to the transaction's non‑malleable digest) while still permitting protocols that bind to application‑level commitments inside `pub_in`. 

## Privacy Implications

No changes to Sapling/Orchard. Protocols built on top MUST document their own privacy model (e.g., DA choices, metadata leakage). This ZIP's verifier only checks validity of a statement over public inputs; it does not guarantee zero‑knowledge unless the prover uses a ZK proof generation mode.

## Backward Compatibility

Nodes that do not implement this TZE will reject transactions that use it after activation. Because TZE uses a distinct TZE unspent set and separate fields (`tze_inputs`/`tze_outputs`), existing transparent and shielded logic is unaffected.

## Deployment

- Network upgrade: Activate in a future NU alongside [^zip-0244] and [^zip-0245].
- Activation gating: Require published test vectors and an external review of the Stwo binding.

## Security Considerations

- DoS safety: Strict size caps; streaming, fail‑fast parsing; bounded allocations; early rejection on malformed encodings.
- Determinism & non‑malleability: Encodings are prefix‑free; any malleation of `precondition` MUST cause rejection; `tze_verify` is deterministic per [^zip-0222].
- Hash assumptions: Security reduces primarily to collision/preimage resistance of the pinned hash suite plus IOP soundness. No EC‑based hash is assumed; the specifics are pinned by `param_id`.
- Implementation risk: Treat the Rust verifier as consensus‑critical code; pin commit/tag and compiler settings; include cross‑checks against test vectors.

## Reference Implementation

> TBD

## Test Vectors

> TBD

## References

[^BCP14]: [Information on BCP 14 — "RFC 2119: Key words for use in RFCs to Indicate Requirement Levels" and "RFC 8174: Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words"](https://www.rfc-editor.org/info/bcp14)

[^zip-0222]: [ZIP‑222: Transparent Zcash Extensions (TZE)](https://zips.z.cash/zip-0222)


[^zip-0244]: [ZIP-244: Transaction Identifier Non-Malleability](https://zips.z.cash/zip-0244)

[^zip-0245]: [ZIP-245: Transaction Identifier Digests & Signature Validation for Transparent Zcash Extensions](https://zips.z.cash/zip-0245)

[^zip-0317]: [ZIP-317: Proportional Transfer Fee Mechanism](https://zips.z.cash/zip-0317)

[^circle-stark-paper]: [Circle STARKs paper](https://eprint.iacr.org/2024/278)

[^sn-stack]: [Starknet stack](https://www.starknet.io/sn-stack/)

[^cairo-paper]: [Cairo – a Turing-complete STARK-friendly CPU architecture](https://eprint.iacr.org/2021/1063.pdf)

[^stwo]: [Stwo proving system](https://starkware.co/blog/s-two-prover/)

[^stwo-repo]: [Stwo prover and verifier implementation](https://github.com/starkware-libs/stwo)
