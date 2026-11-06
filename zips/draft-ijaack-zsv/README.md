# ZSV draft conformance material

These files support [draft-ijaack-zsv.md](../draft-ijaack-zsv.md). They test selected proposed rules beyond the existing Rust research model. They are not a full native consensus implementation or a cryptographic audit.

```sh
python3 zips/draft-ijaack-zsv/check_financial_vectors.py
python3 zips/draft-ijaack-zsv/check_wire_vectors.py
python3 zips/draft-ijaack-zsv/check_oracle_vector.py
```

Run from the repository root with Python 3.10 or later. Financial and wire checks use the standard library. The oracle fixture checker also needs `cryptography` (verified with version 50.0.0); it tests ordinary canonical Ed25519 signatures, not all ZIP 215 acceptance cases. The scripts check adjacent JSON by default. The wire and oracle scripts accept `--write` to regenerate their fixtures.

| Files | What they check | What they do not check |
|---|---|---|
| `financial-vectors.json`, `check_financial_vectors.py` | 54 operation/range/rounding cases, exact Fraction recomputation and u128 domain bounds | Native parsing, keys, signatures, actual UTXO membership or full branch state |
| `wire-vectors.json`, `check_wire_vectors.py` | Seven unsigned effect bodies covering all operation tags and oracle framing, authoritative-context encoding, transaction/context/signature digests and value equations | ECDSA authorization tails, full node parsing, real input history or allocated network identifiers |
| `oracle-vector.json`, `check_oracle_vector.py` | Report bytes/domains, seven canonical signatures, quorum subsets, rejection/context probes and 13 block-selection cases | Full ZIP 215 noncanonical edge cases, operator independence, data truth or complete native block validation |

All keys, inputs and network identifiers are fictional test data. The oracle seeds are intentionally public. No fixture supplies a deployment roster or an allocation.

Remaining conformance work includes independently implemented serialization/digests, complete signed transaction and block vectors, strict-DER/low-S and ZIP 215 edge cases, every operation with real native state, reorg/restart equivalence, resource-limit boundaries and full-node acceptance paths. The [readiness record](https://github.com/iJaack/zsv/blob/d0fe22d/docs/zip-readiness.md) records review and execution results.

Pricing uses the exact parent's committed observation for the whole block. A newly included certificate takes effect in descendants, so unchanged-price renewal cannot invalidate operations in its inclusion block. The fixture's report included at height 101 is first usable at 102 and expires after 112. Block-selection checks cover renewal, price changes, expiry, activation/domain changes and sibling parents; they are helper-level checks, not native block validation.
