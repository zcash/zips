"""Unsigned ZSV draft vectors; fictional identifiers, no consensus allocations.

Standard-library encoding/hash examples, not a node verifier or signature test.
The default checks the adjacent wire-vectors.json without changing it.
Use --check PATH for another file, or --write to regenerate the adjacent file.
"""
import argparse
import hashlib
import json
import struct
from pathlib import Path

# Deliberately fictional test-network allocations, never deployment values.
TEST_VERSION = 0x7FFFFFFE
TEST_VERSION_GROUP_ID = 0x5A535600
TEST_BRANCH_ID = 0x01020304
TEST_GENESIS = bytes.fromhex('44' * 32)
OWNER = bytes.fromhex('0279be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798')
LIQUIDATOR = bytes.fromhex('02c6047f9441ed7d6d3045406e95c07cd85c778e4b8cef3ca7abac09b95c709ee5')
PATH = Path(__file__).with_name("wire-vectors.json")


def u16(n):
    return struct.pack('<H', n)


def u32(n):
    return struct.pack('<I', n)


def u64(n):
    return struct.pack('<Q', n)


def count(n):
    assert 0 <= n <= 64
    return bytes([n])


def h(label, value):
    label = label.encode('ascii')
    assert len(label) <= 16
    return hashlib.blake2b(value, digest_size=32, person=label.ljust(16, b'\0')).digest()


def coin(previous_byte, index, amount, key):
    return (bytes([previous_byte]) * 32 + u32(index), amount, key)


def body(zec_inputs, zec_outputs, stable_inputs, stable_outputs, tag, payload, oracle_effects=None):
    assert len(payload) == {0: 0, 1: 81, 2: 84, 3: 36, 4: 121, 5: 8}[tag]
    header = b''.join(u32(v) for v in (
        TEST_VERSION | 0x80000000, TEST_VERSION_GROUP_ID,
        TEST_BRANCH_ID, 0, 100))
    fields = [header]
    for inputs, outputs in ((zec_inputs, zec_outputs), (stable_inputs, stable_outputs)):
        fields.append(count(len(inputs)))
        fields.extend(outpoint for outpoint, _, _ in inputs)
        fields.append(count(len(outputs)))
        fields.extend(u64(amount) + key for amount, key in outputs)
    fields.extend((bytes([tag]), payload, bytes([oracle_effects is not None])))
    if oracle_effects is not None:
        assert len(oracle_effects) == 45
        assert tag == 0 and not stable_inputs and not stable_outputs
        assert oracle_effects[-1] < 128 and 5 <= oracle_effects[-1].bit_count() <= 7
        fields.append(oracle_effects)
    return b''.join(fields)


def context(zec_inputs, stable_inputs, previous_vault):
    fields = []
    for inputs in (zec_inputs, stable_inputs):
        fields.append(count(len(inputs)))
        fields.extend(outpoint + u64(amount) + key for outpoint, amount, key in inputs)
    fields.append(bytes([previous_vault is not None]))
    if previous_vault:
        reference, key, collateral, principal = previous_vault
        fields.append(reference + key + u64(collateral) + u64(principal))
    return b''.join(fields)


def vector(name, zec_inputs, zec_outputs, stable_inputs, stable_outputs,
           tag, payload, previous_vault=None, action_key=None,
           collateral_after=0, minted=0, burned=0, oracle_effects=None, payouts=()):
    effects = body(zec_inputs, zec_outputs, stable_inputs, stable_outputs, tag, payload, oracle_effects)
    resolved = context(zec_inputs, stable_inputs, previous_vault)
    txid = h('ZSV_TxId_v1', TEST_GENESIS + effects)
    context_hash = h('ZSV_Context_v1', resolved)
    roles = [(0, i, key) for i, (_, _, key) in enumerate(zec_inputs)]
    roles += [(1, i, key) for i, (_, _, key) in enumerate(stable_inputs)]
    if action_key:
        roles.append((2, 0, action_key))
    digests = [{
        'role': role, 'index': index, 'verification_key_hex': key.hex(),
        'digest_hex': h('ZSV_Sign_v1', TEST_GENESIS + txid + context_hash
                        + bytes([role]) + u16(index)).hex(),
    } for role, index, key in roles]
    collateral_before = previous_vault[2] if previous_vault else 0
    fee = sum(c[1] for c in zec_inputs) + collateral_before - collateral_after - sum(c[0] for c in zec_outputs)
    stable_in = sum(c[1] for c in stable_inputs)
    stable_out = sum(c[0] for c in stable_outputs)
    assert fee >= 0
    assert stable_in + minted == stable_out + burned
    assert len({index for index, _, _ in payouts}) == len(payouts)
    for index, key, amount in payouts:
        assert amount > 0 and zec_outputs[index] == (amount, key)
    result = {
        'name': name, 'operation_tag': tag, 'effects_length': len(effects),
        'effects_hex': effects.hex(), 'txid_hex': txid.hex(),
        'resolved_context_hex': resolved.hex(), 'context_hash_hex': context_hash.hex(),
        'signature_digests': digests,
        'value_check': {
            'zec_input': sum(c[1] for c in zec_inputs),
            'zec_output': sum(c[0] for c in zec_outputs),
            'collateral_before': collateral_before, 'collateral_after': collateral_after,
            'zec_fee': fee, 'stable_input': stable_in, 'stable_output': stable_out,
            'minted': minted, 'burned': burned,
        },
    }
    if payouts:
        result['mandatory_payouts'] = [
            {'index': index, 'recipient_key_hex': key.hex(), 'value': amount}
            for index, key, amount in payouts
        ]
    if oracle_effects is not None:
        slots = oracle_effects[-1].bit_count()
        result['oracle_effect_check'] = {
            'effect_hex': oracle_effects.hex(), 'effect_length': len(oracle_effects),
            'expected_secp256k1_signature_slots': len(digests),
            'expected_ed25519_signature_slots': slots,
            'expected_total_signature_slots': len(digests) + slots,
            'expected_ed25519_authorization_bytes': 64 * slots,
            'scope': 'Unsigned certificate framing only. No reporter signatures are supplied or verified; this fictional context is separate from oracle-vector.json.',
        }
    return result


def vectors():
    zero_oracle = bytes(32)
    previous_vault = (bytes.fromhex('55' * 32), OWNER, 1_000_000_000, 400_000_000)
    liquidation = (previous_vault[0] + bytes.fromhex('66' * 32)
                   + u64(400_000_000) + u64(840_000_000)
                   + LIQUIDATOR + u32(2) + u32(1))
    update = (previous_vault[0] + u64(800_000_000) + u64(300_000_000)
              + bytes.fromhex('88' * 32) + u32(1))
    # Unlike oracle-vector.json's signed context, this framing example has no
    # supplied reporter roster or signatures. A height91 inclusion fits expiry100.
    oracle_effects = u32(90) + bytes.fromhex('99' * 32) + u64(100_000_000) + b'\x1f'
    return {
        'scope': 'Unsigned effect/context/hash vectors only; no signatures, node execution or assigned network identifiers. Previous outputs, prior vaults and operation oracle IDs are fictional context inputs, not certified chain state.',
        'hash_hex_order': 'Raw digest bytes; not reversed display hashes.',
        'test_allocations': {
            'version': TEST_VERSION, 'version_group_id': TEST_VERSION_GROUP_ID,
            'branch_id': TEST_BRANCH_ID, 'genesis_hex': TEST_GENESIS.hex(),
            'expiry_height': 100,
        },
        'cases': [
            vector('open_debt_free',
                   [coin(0x22, 3, 1_100_000_000, OWNER)], [(99_990_000, OWNER)], [], [],
                   1, OWNER + u64(1_000_000_000) + u64(0) + zero_oracle,
                   action_key=OWNER, collateral_after=1_000_000_000),
            vector('stable_transfer',
                   [coin(0x33, 1, 100_000_000, OWNER)], [(99_990_000, OWNER)],
                   [coin(0x77, 2, 400_000_000, OWNER)],
                   [(125_000_000, LIQUIDATOR), (275_000_000, OWNER)], 0, b''),
            vector('solvent_liquidation_at_50',
                   [coin(0x33, 1, 100_000_000, LIQUIDATOR)],
                   [(99_990_000, LIQUIDATOR), (840_000_000, LIQUIDATOR), (160_000_000, OWNER)],
                   [coin(0x77, 2, 400_000_000, LIQUIDATOR)], [], 4, liquidation,
                   previous_vault=previous_vault, action_key=LIQUIDATOR, burned=400_000_000,
                   payouts=[(1, LIQUIDATOR, 840_000_000), (2, OWNER, 160_000_000)]),
            vector('retire_bad_debt',
                   [coin(0x33, 1, 100_000_000, OWNER)], [(99_990_000, OWNER)],
                   [coin(0x77, 2, 400_000_000, OWNER)], [(300_000_000, OWNER)],
                   5, u64(100_000_000), burned=100_000_000),
            vector('update_repay_and_withdraw',
                   [coin(0x33, 1, 100_000_000, OWNER)],
                   [(99_990_000, OWNER), (200_000_000, OWNER)],
                   [coin(0x77, 2, 100_000_000, OWNER)], [], 2, update,
                   previous_vault=previous_vault, action_key=OWNER,
                   collateral_after=800_000_000, burned=100_000_000,
                   payouts=[(1, OWNER, 200_000_000)]),
            vector('close_with_full_repayment',
                   [coin(0x33, 1, 100_000_000, OWNER)],
                   [(99_990_000, OWNER), (1_000_000_000, OWNER)],
                   [coin(0x77, 2, 400_000_000, OWNER)], [],
                   3, previous_vault[0] + u32(1),
                   previous_vault=previous_vault, action_key=OWNER,
                   burned=400_000_000, payouts=[(1, OWNER, 1_000_000_000)]),
            vector('oracle_certificate_effects',
                   [coin(0x33, 1, 100_000_000, OWNER)], [(99_990_000, OWNER)],
                   [], [], 0, b'', oracle_effects=oracle_effects),
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', type=Path, nargs='?', const=PATH, default=PATH,
                        help='compare a vector file; defaults to the adjacent file')
    parser.add_argument('--write', action='store_true',
                        help='regenerate the adjacent checked-in vector file')
    args = parser.parse_args()
    actual = json.dumps(vectors(), indent=2, sort_keys=True) + '\n'
    if args.write:
        PATH.write_text(actual)
    if args.check.read_text() != actual:
        raise SystemExit(f'Vector mismatch: {args.check}')
    print('Seven unsigned ZSV wire/context/hash vectors match: all six operation tags and one oracle effect body.')


if __name__ == '__main__':
    main()
