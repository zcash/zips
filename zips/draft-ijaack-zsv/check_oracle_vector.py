#!/usr/bin/env python3
"""Check the ZIP's canonical oracle fixture; --write regenerates its exact JSON.

Requires the optional `cryptography` package (python3 -m pip install cryptography).
This exercises ordinary canonical Ed25519 signatures, not ZIP 215's complete
acceptance set, noncanonical point encodings or a native transaction verifier.
All seeds and network fields below are explicitly public, synthetic fixtures.
"""

import argparse
import hashlib
import json
import struct
from pathlib import Path

try:
    from cryptography.exceptions import InvalidSignature
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
except ImportError as error:
    raise SystemExit("Optional dependency missing: python3 -m pip install cryptography") from error


PATH = Path(__file__).with_name("oracle-vector.json")
SET_PREFIX = b"ZSV/OracleSet/v1\0"
REPORT_PREFIX = b"ZSV/Oracle/v1\0"
U32_MAX = (1 << 32) - 1
U64_MAX = (1 << 64) - 1
FIELD_MODULUS = (1 << 255) - 19
SUBGROUP_ORDER = (1 << 252) + 27742317777372353535851937790883648493


def sha256(data):
    return hashlib.sha256(data).digest()


def set_id(keys):
    return sha256(SET_PREFIX + bytes([7, 5]) + b"".join(keys))


def body(height, ancestor, price):
    return struct.pack("<I", height) + ancestor + struct.pack("<Q", price)


def message(genesis, branch, roster_id, report_body):
    return REPORT_PREFIX + genesis + struct.pack("<I", branch) + roster_id + report_body


def mask_indices(mask):
    if type(mask) is not int or not 0 <= mask < 128 or not 5 <= mask.bit_count() <= 7:
        raise ValueError("invalid signer mask")
    return [index for index in range(7) if mask & (1 << index)]


def verify_subset(keys, signed_message, mask, signatures):
    indices = mask_indices(mask)
    if len(signatures) != len(indices):
        raise ValueError("signature count does not match mask")
    for index, signature in zip(indices, signatures):
        keys[index].public_key().verify(signature, signed_message)


def context_valid(height, price, candidate, branch_start, previous, ancestor_matches=True):
    """Check only the listed numeric/ancestry preconditions, not full consensus."""
    return (
        type(price) is int and 1 <= price <= U64_MAX
        and type(height) is int and 0 <= height <= U32_MAX
        and 0 < branch_start <= candidate <= U32_MAX
        and branch_start - 1 <= height < candidate <= height + 12 <= U32_MAX
        and (previous is None or height > previous)
        and ancestor_matches
    )


def fixture():
    rows = []
    for seed_byte in range(1, 8):
        seed = bytes([seed_byte]) * 32
        key = Ed25519PrivateKey.from_private_bytes(seed)
        public = key.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
        rows.append((public, seed, key))
    rows.sort(key=lambda row: row[0])
    public_keys = [row[0] for row in rows]
    keys = [row[2] for row in rows]
    roster_bytes = SET_PREFIX + bytes([7, 5]) + b"".join(public_keys)
    roster_id = set_id(public_keys)
    genesis = bytes([0x11]) * 32
    branch = 0xA1B2C3D4
    ancestor = bytes([0x22]) * 32
    height, price = 100, 100_000_000
    report_body = body(height, ancestor, price)
    signed_message = message(genesis, branch, roster_id, report_body)
    signatures = [key.sign(signed_message) for key in keys]
    mask = 0x1F
    document = {
        "format": "zsv-zip-canonical-oracle-vector-v1",
        "scope": "Public deterministic fixture keys and synthetic context only; no deployment key or branch-ID allocation. Canonical signatures exercise common Ed25519 behavior, not all ZIP 215 edge cases.",
        "genesis_hash_hex": genesis.hex(),
        "active_branch_id_u32": branch,
        "active_branch_start_height": 90,
        "candidate_height": 101,
        "prior_observed_height": 99,
        "keys_sorted": [
            {"index": index, "public_key_hex": row[0].hex(), "public_fixture_seed_hex": row[1].hex()}
            for index, row in enumerate(rows)
        ],
        "roster_bytes_hex": roster_bytes.hex(),
        "reporter_set_id_hex": roster_id.hex(),
        "observed_height": height,
        "observed_block_hash_hex": ancestor.hex(),
        "price_micro_usd_per_zec": price,
        "valid_from_height": 102,
        "valid_through_height": 112,
        "body_hex": report_body.hex(),
        "signing_message_hex": signed_message.hex(),
        "oracle_id_hex": sha256(signed_message).hex(),
        "signer_mask_u8": mask,
        "effect_hex": (report_body + bytes([mask])).hex(),
        "authorization_hex": b"".join(signatures[:5]).hex(),
        "signatures_by_index": [
            {"index": index, "signature_hex": signature.hex()}
            for index, signature in enumerate(signatures)
        ],
        "expected_accept": True,
    }
    return document, keys


def expect_failure(call):
    try:
        call()
    except (ValueError, InvalidSignature):
        return
    raise AssertionError("invalid mutation was accepted")


def check(document, keys):
    report_body = bytes.fromhex(document["body_hex"])
    signed_message = bytes.fromhex(document["signing_message_hex"])
    signatures = [bytes.fromhex(row["signature_hex"]) for row in document["signatures_by_index"]]
    assert len(report_body) == 44 and len(signed_message) == 126
    assert len(bytes.fromhex(document["effect_hex"])) == 45
    assert len(bytes.fromhex(document["authorization_hex"])) == 320
    assert len(set(row["public_key_hex"] for row in document["keys_sorted"])) == 7
    for key, signature in zip(keys, signatures):
        assert len(signature) == 64
        assert (int.from_bytes(signature[:32], "little") & ((1 << 255) - 1)) < FIELD_MODULUS
        assert int.from_bytes(signature[32:], "little") < SUBGROUP_ORDER
        key.public_key().verify(signature, signed_message)

    for mask in (0x1F, 0x3F, 0x7F, 0x7C):
        selected = [signatures[index] for index in mask_indices(mask)]
        verify_subset(keys, signed_message, mask, selected)
        effect = report_body + bytes([mask])
        reconstructed_message = signed_message[:-44] + effect[:44]
        assert sha256(reconstructed_message) == bytes.fromhex(document["oracle_id_hex"])
        assert len(effect) + sum(map(len, selected)) == 45 + 64 * mask.bit_count()

    # Mutate each signed field: genesis, branch, roster, height, ancestor, price.
    for offset in (14, 46, 50, 82, 86, 118):
        mutated = bytearray(signed_message)
        mutated[offset] ^= 1
        expect_failure(lambda: keys[0].public_key().verify(signatures[0], bytes(mutated)))
    mutated_signature = bytearray(signatures[0])
    mutated_signature[0] ^= 1
    expect_failure(lambda: keys[0].public_key().verify(bytes(mutated_signature), signed_message))
    expect_failure(lambda: keys[1].public_key().verify(signatures[0], signed_message))

    for invalid_mask in (0, 0x0F, 0x9F, 0xFF):
        expect_failure(lambda: mask_indices(invalid_mask))
    expect_failure(lambda: verify_subset(keys, signed_message, 0x1F, signatures[:4]))
    expect_failure(lambda: verify_subset(keys, signed_message, 0x1F, signatures[:6]))
    expect_failure(lambda: verify_subset(keys, signed_message, 0x1F, list(reversed(signatures[:5]))))
    expect_failure(lambda: verify_subset(keys, signed_message, 0x3F, signatures[:5] + [bytes(mutated_signature)]))

    cases = [
        ((100, 100_000_000, 100, 90, 99), False),
        ((100, 100_000_000, 101, 90, 99), True),
        ((100, 100_000_000, 112, 90, 99), True),
        ((100, 100_000_000, 113, 90, 99), False),
        ((100, 100_000_000, 101, 90, 99, False), False),
        ((88, 100_000_000, 90, 90, None), False),
        ((89, 100_000_000, 90, 90, None), True),
        ((100, 100_000_000, 101, 90, 100), False),
        ((100, 0, 101, 90, 99), False),
        ((100, U64_MAX, 101, 90, 99), True),
        ((100, U64_MAX + 1, 101, 90, 99), False),
        ((U32_MAX - 1, 100_000_000, U32_MAX, 90, None), False),
    ]
    for arguments, expected in cases:
        assert context_valid(*arguments) is expected, arguments
    return len(cases)


def block_oracle(parent, accepted, height, domain_changed=False):
    """Oracle selection only; inputs are already-validated (ID, observed height).

    This fixture helper does not validate a block, ancestry or certificate.
    """
    parent = None if domain_changed else parent
    pricing = parent if parent is not None and height <= parent[1] + 12 else None
    return pricing, accepted if accepted is not None else parent


def check_rollover(document, keys):
    old_message = bytes.fromhex(document["signing_message_hex"])
    old = (sha256(old_message), 100)
    # Same price, later observation and synthetic ancestor: both quorums verify.
    new_message = old_message[:-44] + body(101, bytes([0x33]) * 32, 100_000_000)
    verify_subset(keys, new_message, 0x1F, [key.sign(new_message) for key in keys[:5]])
    new = (sha256(new_message), 101)
    assert old[0] != new[0]
    assert context_valid(101, 100_000_000, 102, 90, 100)
    crash_message = old_message[:-44] + body(101, bytes([0x33]) * 32, 20_000_000)
    verify_subset(keys, crash_message, 0x1F, [key.sign(crash_message) for key in keys[:5]])
    crash = (sha256(crash_message), 101)
    next_domain_message = message(bytes.fromhex(document["genesis_hash_hex"]),
                                  document["active_branch_id_u32"] + 1,
                                  bytes.fromhex(document["reporter_set_id_hex"]),
                                  body(101, bytes([0x33]) * 32, 100_000_000))
    verify_subset(keys, next_domain_message, 0x1F,
                  [key.sign(next_domain_message) for key in keys[:5]])
    next_domain = (sha256(next_domain_message), 101)
    cases = [
        # (parent, newly accepted, block height, domain change), (pricing, committed)
        ((None, old, 101, False), (None, old)),
        ((old, new, 102, False), (old, new)),
        ((new, None, 103, False), (new, new)),
        ((old, None, 102, False), (old, old)),
        ((old, None, 112, False), (old, old)),
        ((old, None, 113, False), (None, old)),
        ((old, new, 113, False), (None, new)),
        ((new, None, 114, False), (None, new)),
        ((old, None, 102, True), (None, None)),
        # A new-domain certificate must be verified separately before this helper.
        ((old, next_domain, 102, True), (None, next_domain)),
        ((old, crash, 102, False), (old, crash)),
        ((crash, None, 103, False), (crash, crash)),
        # Replaying a sibling uses its own parent, not the selected tip's report.
        ((old, None, 103, False), (old, old)),
    ]
    for arguments, expected in cases:
        assert block_oracle(*arguments) == expected, arguments
    return len(cases)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="regenerate the checked-in fixture")
    args = parser.parse_args()
    document, keys = fixture()
    boundary_count = check(document, keys)
    rollover_count = check_rollover(document, keys)
    encoded = json.dumps(document, indent=2) + "\n"
    if args.write:
        PATH.write_text(encoded)
    if PATH.read_text() != encoded:
        raise ValueError("oracle-vector.json differs from its deterministic fixture")
    print(f"Oracle fixture checked: 7 canonical signers, 4 quorum subsets, 16 rejection probes, {boundary_count} context cases; {rollover_count} block-selection cases; exact JSON match.")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, AssertionError) as error:
        raise SystemExit(str(error)) from error
