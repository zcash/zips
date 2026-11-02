    ZIP: Unassigned
    Title: FROST Member Backup Strings for Shielded Zcash
    Owners: Khadim <openpgp-wallet@protonmail.com>
            aryaethn <aryaethn@gmail.com>
    Credits: Hanh (hhanh00), for the zkfrost string in Zkool
    Status: Draft
    Category: Wallet
    Created: 2026-10-26
    License: MIT
    Discussions-To: <https://github.com/zcash/zips/issues/1413>
    Pull-Request: <https://github.com/zcash/zips/pull/1432>


# Terminology

The key words "MUST", "MUST NOT", "SHOULD", and "SHOULD NOT" in this document
are to be interpreted as described in BCP 14 [^BCP14] when, and only when,
they appear in all capitals.

The terms "Mainnet" and "Testnet" in this document are to be interpreted as
defined in the Zcash protocol specification [^protocol-networks].

The terms below are to be interpreted as follows:

Group

: A set of $n$ participants holding a FROST threshold key for Orchard-protocol
  spend authorization [^zip-0312], any $t$ of whom can sign.

Member

: One participant of a group, identified by its FROST identifier.

Signing share

: The member's secret share of the group's Spend authorizing key, as output
  by key generation.

Group verifying key, $\mathsf{ak}$

: The FROST group public key, used as the Spend validating key
  $\mathsf{ak}$ of the group's Orchard full viewing key. Its encoding has a
  $\tilde{y}$ bit of $0$, as § 4.2.3 of the protocol specification requires
  [^protocol-updated-orchardkeycomponents].

$\mathsf{sk}$

: The 32-byte value the members agree on during key generation, from which
  the rest of the group's key components are derived [^zip-2005-usagewithfrost].

Derivation

: How $\mathsf{nk}$ and $\mathsf{rivk}$ are obtained from $\mathsf{sk}$ and
  $\mathsf{ak}$. This ZIP knows two, defined in [Derivations].

Member backup string

: The string defined in this ZIP.


# Abstract

This ZIP defines a backup string for one member of a FROST group that spends
shielded ZEC with Orchard-protocol keys (in the Orchard or Ironwood pool). The
string holds the member's identifier, the threshold, the group size, the
member's signing share and the group's $\mathsf{sk}$. Together with the group's
unified full viewing key, it is enough to rebuild the member in any wallet that
implements this ZIP, without the other members being online. Restoring checks
the string against the viewing key, which both detects a string from another
group and tells the wallet which key derivation the group uses.

Version 1 of the payload is byte-for-byte the `zkfrost` string that Zkool
already ships, so existing backups stay valid.

The string is more sensitive than the signing share it carries: it also
carries $\mathsf{sk}$, from which a holder can compute the group's quantum
spending key $\mathsf{qsk}$ [^zip-2005]. It never appears on chain.


# Motivation

Several wallets now offer FROST groups for shielded ZEC: Zkool, Zafe,
Konclave, and the Zcash Foundation's tools. Each one backs up its members in its
own format, so a member can only restore their seat in the app that created
it. In July 2026, Zkool's author described the situation: "There is no
standard for it. I choose a way that makes it restorable on Zkool only. One
day, someone will write a ZIP." [^zkool-forum]

Since then, Zkool has moved to a minimal backup string (`zkfrost`, Zkool
6.35.0) that holds only what a member needs. This ZIP takes that string as its
first version, so that:

- a user can move a seat from one wallet to another, or restore it in a
  different app after losing a device;
- a group can mix implementations, which avoids having every signer come from
  one vendor;
- funds stay reachable if one app is abandoned.

ZIP 2005 adds a reason. To recover notes with the Recovery Protocol, "it is
necessary to retain, or be able to rederive, $\mathsf{sk}$, and also to know
whether $\mathsf{use\_qsk}$ was used to derive the $\mathsf{ivk}$ and
addresses" [^protocol-updated-orchardkeycomponents]. A backup format is where
that knowledge has to live.


# Privacy Implications

The string never leaves the member's custody in normal use and is not
published on chain, so this ZIP changes nothing for on-chain privacy.

Combined with the group's unified full viewing key, a string gives no viewing
capability beyond what that viewing key already gives. Without the viewing
key, $\mathsf{sk}$ yields $\mathsf{nk}$ but not the incoming viewing key, which
also depends on $\mathsf{ak}$. The string does reveal $t$, $n$ and the member's
identifier.

A wallet that shows the string as a QR code exposes it to cameras and
onlookers, as with any secret displayed on screen.


# Requirements

- A member can be rebuilt from its string and the group's unified full viewing
  key, with no other member online.
- A wallet detects a string that belongs to another group before using it.
- The restore tells which derivation the group uses.
- The format does not depend on how $\mathsf{sk}$ was agreed.
- Backups made with Zkool's `zkfrost` string stay valid.
- The format can gain new versions without breaking existing strings.


# Non-requirements

- Key generation, including how the members agree on $\mathsf{sk}$
  [^zip-0312-key-generation].
- Signing, and the transport between members.
- Encryption of the string at rest (see [Open issues]).
- A birthday height. zips#1401 proposes to carry it in the unified full
  viewing key [^zips-1401], which the restore already needs.
- Splitting $\mathsf{qsk}$ between members.
- FROST groups using Sapling keys.


# Specification

## Derivations

Let $\mathsf{H^{ask}}$, $\mathsf{H^{nk}}$, $\mathsf{H^{rivk}}$,
$\mathsf{H^{qsk}}$, $\mathsf{H^{qk}}$ and
$\mathsf{H}^{\mathsf{rivk\_ext}}_{\mathsf{qk}}$ be as defined in § 4.2.3
of the protocol specification as updated by ZIP 2005
[^protocol-updated-orchardkeycomponents].

ZIP 2005 derivation

: $\mathsf{nk} = \mathsf{H^{nk}}(\mathsf{sk})$, and
  $\mathsf{rivk} = \mathsf{H}^{\mathsf{rivk\_ext}}_{\mathsf{qk}}(\mathsf{ak}, \mathsf{nk})$
  where $\mathsf{qk} = \mathsf{H^{qk}}(\mathsf{H^{qsk}}(\mathsf{sk}))$. This is
  the $\mathsf{use\_qsk} = \mathsf{true}$ branch that ZIP 2005 requires for
  FROST [^zip-2005-usagewithfrost]. Notes received by such a group are
  quantum recoverable.

Legacy derivation

: $\mathsf{nk} = \mathsf{H^{nk}}(\mathsf{sk})$ and
  $\mathsf{rivk} = \mathsf{H^{rivk}}(\mathsf{sk})$, with the group verifying key
  as $\mathsf{ak}$. Zkool created groups this way before supporting ZIP 2005.
  Such a group follows neither branch of § 4.2.3
  [^protocol-updated-orchardkeycomponents]: $\mathsf{ak}$ is not derived from
  $\mathsf{sk}$, and $\mathsf{rivk}$ does not commit to a $\mathsf{qk}$. Notes
  received by such a group are therefore not quantum recoverable.

## Encoding

A member backup string is the Bech32m [^bip-0350] encoding of a payload, with
the human-readable part `zkfrost`. As in ZIP 316 [^zip-0316], the length limit
of Bech32m is not applied; a version 1 string is 123 characters long.

Encoders MUST produce lowercase strings. Decoders MUST accept a string that is
entirely lowercase or entirely uppercase, and MUST reject a string in mixed
case, as Bech32m requires. A wallet can still show the string in uppercase,
for instance in a QR code (see [Rationale]), by converting it after encoding.

The human-readable part is the same on Mainnet and Testnet, and the payload
names no network: the network is given by the unified full viewing key used to
restore. A string paired with another group's viewing key, on either network,
fails the check in [Restore].

## Payload, version 1

| Offset | Size | Field |
|--------|------|-------|
| 0      | 1    | format version, $\mathtt{0x01}$ |
| 1      | 1    | member identifier $i$ |
| 2      | 1    | threshold $t$ |
| 3      | 1    | group size $n$ |
| 4      | 32   | signing share |
| 36     | 32   | $\mathsf{sk}$ |

The member's FROST identifier is the Pallas scalar with integer value $i$.

The signing share is the little-endian encoding of a Pallas scalar, as in the
FROST(Pallas, BLAKE2b-512) ciphersuite [^zip-0312]. It MUST be the share that
matches the $\mathsf{ak}$ in the group's viewing key. Key generation can output
a group key with either $\tilde{y}$ bit; when it is $1$, the group key and
every share are negated. The `reddsa` crate does this at the end of its key
generation, and frost-client does it after the DKG. An implementation that
skips this step would export a wrong share for about half of all groups.

## Decoding

A decoder MUST reject the string if any of the following holds:

- it is not valid Bech32m, including a bad checksum, a Bech32 checksum, or
  mixed case;
- the bits left over when converting its data part to bytes are more than 4
  or not all zero, as ZIP 173 requires [^zip-0173]. A version 1 string leaves
  1 bit, so each payload has only one lowercase string;
- its human-readable part, compared case-insensitively, is not `zkfrost`;
- the payload is not exactly 68 bytes long;
- the format version is not $\mathtt{0x01}$;
- $n = 0$, $i = 0$, $i > n$, $t < 2$, or $t > n$. FROST needs at least two
  signers.

## Restore

The inputs are a member backup string and the group's unified full viewing
key. The viewing key MUST contain an Orchard component (typecode
$\mathtt{0x03}$ [^zip-0316]), which holds $\mathsf{ak}$, $\mathsf{nk}$ and
$\mathsf{rivk}$. Ironwood uses the same Orchard-protocol keys.

1. Decode the string as above.
2. Reject the string if $\mathsf{sk}$ is not a valid Orchard spending key,
   that is if $\mathsf{H^{ask}}(\mathsf{sk}) = 0$, or if the signing share is
   not the canonical encoding of a Pallas scalar. (A group's $\mathsf{ask}$ is
   not derived from $\mathsf{sk}$; the first check only keeps decoders in
   agreement with the validity rule for Orchard spending keys.)
3. Take $\mathsf{ak}$ from the viewing key. Compute $\mathsf{nk}$ and
   $\mathsf{rivk}$ under each derivation of [Derivations].
4. If the ZIP 2005 derivation gives the viewing key's $\mathsf{nk}$ and
   $\mathsf{rivk}$, the group follows the ZIP 2005 derivation. Otherwise, if
   the legacy derivation does, the group follows the legacy derivation.
   Otherwise the wallet MUST reject the string: it belongs to another group.
5. Rebuild the member's key material from the identifier, the signing share,
   the threshold $t$ and $\mathsf{ak}$ as the group verifying key. If the
   wallet knows the group's verifying shares, it SHOULD check that the
   member's verifying share matches.

A wallet SHOULD tell the user which derivation was found, and SHOULD warn when
it is the legacy one, whose notes are not quantum recoverable.

The check in step 4 proves that the viewing key was derived from the string's
$\mathsf{sk}$, not that its $\mathsf{ak}$ is the group's (see
[Security Considerations]). Before it shows an address to receive funds, a
wallet SHOULD check the viewing key against a source the member trusts, such as
the export made with its own string (see [Export]), an address of the group
that the member recorded before and that the viewing key gives, or the same
viewing key obtained from at least two other members. A member that lost its
device may have lost its export too, and then has to ask the others for the
key, which is the case the attack needs: if one of the members it asks is
honest, a forged key shows up as a mismatch.

After the restore, the wallet MUST retain $\mathsf{sk}$ when the group follows
the ZIP 2005 derivation. ZIP 2005 makes $\mathsf{qsk}$, which is derived from
$\mathsf{sk}$, essential for recovering the group's notes once the current
Orchard protocol is disabled [^zip-2005-usagewithfrost], and the signing
share and viewing key alone do not give it. A wallet SHOULD also retain
$\mathsf{sk}$ for a legacy group, since without it the member cannot export
its string again.

A restored member holds no signing nonces. It MUST generate fresh ones for its
next signing session.

The check in step 4 proves $\mathsf{sk}$, not the signing share. A wrong share,
such as one stored with the wrong sign, passes the restore and is caught at the
member's first signing: the verifying shares of the $t$ signers, which travel
with their commitments, interpolate to $\mathsf{ak}$ only if every one of them
is right. The signing transport is out of scope for this ZIP, but a signing
protocol used with these strings SHOULD carry each signer's verifying share,
so that a member restored from a string is checked when it first signs.

## Export

A wallet that exports a member backup string SHOULD export the group's unified
full viewing key with it, or tell the user that the restore needs it. ZIP 2005
asks FROST members to retain the group verifying key $\mathsf{ak}$
[^protocol-updated-orchardkeycomponents]; in version 1 it is only held by the
viewing key.

A wallet MUST NOT put signing nonces, or any other secret beyond the fields
above, in a version 1 string.

## Storage and transmission

Wallets MUST protect every member backup string at least as securely and
reliably as $\mathsf{ask}$, as ZIP 2005 requires of $\mathsf{qsk}$
[^zip-2005-usagewithfrost], and not merely like one signing share.

Wallets SHOULD NOT store or transmit a string encrypted only under public-key
encryption based on discrete logarithms or on factoring, such as Orchard note
encryption, X25519, or RSA and elliptic-curve OpenPGP keys.


# Rationale

**Bech32m.** It gives a checksum that catches copy errors and a string users
can paste or show as a QR code. An uppercase string fits the QR alphanumeric
mode, which makes the code smaller. Its checksum guarantees the detection of
any error affecting at most 4 characters only for strings of at most 90
characters [^zip-0173] [^bip-0350]. A version 1 string is 123 characters
long, so it keeps the 30-bit checksum without that guarantee, as unified
addresses and viewing keys do [^zip-0316].

**No network in the string.** A member's share is the same on every network
the group lives on. The viewing key carries the network.

**$\mathsf{ak}$ is not stored.** The restore needs the viewing key anyway to
scan the chain, and checking $\mathsf{nk}$ and $\mathsf{rivk}$ against it
catches a string from another group. The cost is that the string does not
authenticate $\mathsf{ak}$ (see [Security Considerations]).

**$\mathsf{sk}$ is stored whole.** ZIP 2005 makes it necessary "to retain, or
be able to rederive, $\mathsf{sk}$" [^protocol-updated-orchardkeycomponents],
and every member already holds it, along with $\mathsf{qsk}$
[^zip-2005-usagewithfrost].

**The derivation is found, not recorded.** Version 1 is Zkool's existing
payload, which has no field for it. With two derivations and the viewing key at
hand, trying both is cheap and unambiguous: both matching would need a
collision in the hash functions behind $\mathsf{rivk}$. A later version can
record the derivation explicitly (see [Open issues]).

**One-byte identifier.** It covers groups whose identifiers are the integers
1 to $n$, as in Zkool and in frost-client's trusted-dealer key generation.
frost-client's DKG and Zafe derive 32-byte identifiers, which need another
version (see [Open issues]).

**Version 1 is Zkool's payload.** Backups users already made keep working,
and the first implementation exists today.


# Security Considerations

A string holds one signing share. Fewer than $t$ strings cannot spend, as long
as discrete logarithms on the Pallas curve stay hard.

Every string also holds $\mathsf{sk}$, which yields $\mathsf{qsk}$. ZIP 2005
notes that "a quantum adversary may be able to steal the funds with only
access to $\mathsf{qsk}$, which is held by every participant"
[^zip-2005-usagewithfrost]. Against such an adversary the threshold may give no
protection: one leaked string, from any member, may be enough to steal the
funds. ZIP 2005 requires each participant to "treat $\mathsf{qsk}$ as a
secret held at least as securely and reliably as $\mathsf{ask}$"
[^zip-2005-usagewithfrost], which is why [Storage and transmission] asks the
same for every string.

For the same reason, a string that is stored or sent encrypted only under
public-key encryption based on discrete logarithms or on factoring is exposed
to an adversary who records the ciphertext now and gains a quantum computer
later. A passphrase with a memory-hard KDF and an AEAD (see [Open issues])
does not have this weakness.

The restore does not prove the signing share (see [Restore]). A wrong share,
for instance one exported with the wrong sign (see [Payload, version 1]),
gives signature shares that fail verification. It stops that member from
signing until it is restored from a correct string, but it cannot sign
anything or leak the other shares.

The restore does not authenticate $\mathsf{ak}$ either. Every member holds
$\mathsf{sk}$, so a dishonest member can build a viewing key around another
$\mathsf{ak}$, for instance one whose secret it holds alone, with the
$\mathsf{nk}$ and $\mathsf{rivk}$ that either derivation gives for it. A string
restored with that key passes every check in [Restore], and the wallet then
shows addresses that only that member can spend from. The wallet would not see
the group's notes, and the group's signatures would not verify under that
$\mathsf{ak}$, but funds received at those addresses before anyone notices are
lost to the group. Checking the viewing key against a trusted source, as
[Restore] asks, prevents this; so would carrying $\mathsf{ak}$ in the string
(see [Open issues]).

A member restored from a string has the same authority as before: the string
adds no signer to the group. It carries no nonces, so a restore cannot bring
back a nonce that was already used or published.


# Deployment

This ZIP changes no consensus rule. Wallets can adopt it at any time.


# Reference implementation

- Zkool: `rust/src/frost/backup.rs` in hhanh00/zkool2, released in Zkool
  6.35.0 [^zkool-backup].
- frost-zec: `src/backup.rs` in OpenPGP-Wallet/frost-zec, by one of this
  ZIP's owners, written from this ZIP's rules apart from Zkool's code, with
  `backup export` and `backup restore` commands [^frost-zec-backup]. Its
  `tools/zip-vectors` generates the test vectors below.


# Test vectors

The full set is in `draft-khadim-aryaethn-frost-member-backup/vectors.json`.
It covers a 2-of-3 ZIP 2005 group, a 2-of-3 legacy group together with the
ZIP 2005 viewing key built from the same $\mathsf{sk}$ and $\mathsf{ak}$ (whose
strings restore under either key, with a different derivation), and a 3-of-5
ZIP 2005 group; an uppercase string; sixteen strings that decoders must
reject, two of them for the padding rule and one with a threshold of 1; and a
valid string paired with another group's viewing key, which the restore must
reject.

Every valid string decodes to the same fields and matches the stated
derivation with Zkool's code, and every $t$-subset of members restored from
their strings produces a FROST signature that verifies under $\mathsf{ak}$.
Zkool 6.35.0 rejects every invalid string except three. It does not check
the padding bits, and decodes the two padding strings to the same fields as
the valid string they come from; it also accepts a threshold of 1. Zkool
6.36.0 rejects all three: the padding fix, hhanh00/zkool2#1468
[^zkool-padding-fix], includes the two padding strings in its tests, and the
decoder now refuses a threshold below 2.
A third decoder, by the other owner of this ZIP, with the derivations written
directly from BIP 350, ZIP 316 and ZIP 2005 and no Zcash library, gives the
expected result for every string, both viewing keys of each group, and every
rejected case. With frost-client's version of `reddsa`, every $t$-subset also
rebuilds $\mathsf{ak}$ and signs.

One member of the 2-of-3 ZIP 2005 group (byte strings in hex):

    sk      b478b8702c1d2569fe52e5d7dbadec6223cd10fd4b504dabac7fff23a37363d1
    ak      73325d2c62873971ff54f37413d2b04e8056ea4fbd71850f5f8337df1816f126
    nk      c01df2b3b3f917a5cf78fa1be4c5ab6bd32a9bf36c524d5702ecd4aeb836381e
    qsk     ee2f78322c86d7c66fc598f21186eed3d664f46b4950170745d64bb01dd6d6ca
    qk      80f648b4c74e93ee378ddf0b3870a6078211115a72712b68566178f24b2af54c
    rivk    25f3d4723928d1c557ecb4c74be1f2f241daeccd3173d83215a277c87c6c5c34
    t, n    2, 3
    id      1
    share   f133adc1d96020157d930d1782e330926d6c662d6754ea903ea7f779dd884431
    string  zkfrost1qyqsyql3xwkurktqyq2hmycdz7pwxvyjd4kxvtt82n4fq0487auamzzyxx683wrs9swj26072tja0kada33z8ngsl494qndt43ll7garwd3az4qx9an
    ufvk    uview1lvfs3zfudj3pl6axj09t7wc0g8vgf7f98rcrmyqgtgjvxrgehte7802uptc9xt37hrauudeazeveywkd98x5ewputn0uyzadx7x3sm8nkccnraqpfvefwguwesq8s6e0hruprvkax5lw73rv2eznycd2hq3a9glq95p54ahytt8t60hm52pt6pc0czxg4


# Open issues

- **Identifier encoding.** frost-client's DKG derives identifiers as
  `Identifier::derive(session_id || pubkey)`, and Zafe from the vault id and
  the member's identity key, so groups created by either use full 32-byte
  identifiers (frost-client's trusted dealer uses 1 to $n$). For their groups
  to fit, a version 2 needs a type byte followed by a short or a full
  identifier.
- **Explicit derivation.** A version 2 could record the derivation, so a
  restore does not depend on trying each one, and a third derivation could be
  added without ambiguity.
- **Groups with no $\mathsf{sk}$.** zcash-sign's `generate`, which Konclave
  uses, derives $\mathsf{nk}$ and $\mathsf{rivk}$ from a random $\mathsf{sk}$
  and then discards it, so version 1 cannot hold its groups. A version 2 could
  record that $\mathsf{nk}$ and $\mathsf{rivk}$ come from the viewing key,
  leave $\mathsf{sk}$ out, and carry the viewing key itself (next item).
  Carrying only $\mathsf{ak}$, as first suggested in zcash/zips#1413, would let
  the restore catch a viewing key from another group, but not a different
  viewing key for the same group. Such groups are not quantum recoverable
  under ZIP 2005.
- **The viewing key in the string**, so that a restore needs only the string.
  For a group with no $\mathsf{sk}$, the viewing key is the only source of
  $\mathsf{nk}$ and $\mathsf{rivk}$. A version 2 would carry the raw 96-byte
  Orchard full viewing key rather than its unified encoding, so that the
  string stays network-agnostic. With the viewing key in the string, nothing
  outside it is left to mismatch. For a group with $\mathsf{sk}$,
  $\mathsf{ak}$ is enough, since $\mathsf{nk}$ and $\mathsf{rivk}$ follow from
  $\mathsf{sk}$ and $\mathsf{ak}$. Either way, $\mathsf{ak}$ would then come
  from the member's own backup rather than from a viewing key obtained
  elsewhere (see [Security Considerations]). A string for a group with no
  $\mathsf{sk}$ would be about 230 characters long, or 280 with a 32-byte
  identifier (see [Rationale] on Bech32m).
- **Birthday height in version 2.** A raw Orchard full viewing key does not
  carry the birthday height that zips#1401 would add to the unified encoding
  [^zips-1401], so a string that restores on its own would need a birthday
  field of its own, as Konclave noted in zcash/zips#1413. A height only means
  something on one network, so the field would either name the network or
  apply to the network the wallet restores on.
- **Passphrase profile.** An optional version encrypting the payload with a
  memory-hard KDF and an AEAD, as Zafe does for its backups.
- **Human-readable part.** `zkfrost` is kept for compatibility with existing
  backups. Should a later version use a more neutral one?


# References

[^BCP14]: [Information on BCP 14 — "RFC 2119: Key words for use in RFCs to Indicate Requirement Levels" and "RFC 8174: Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words"](https://www.rfc-editor.org/info/bcp14)

[^protocol-networks]: [Zcash Protocol Specification, Version 2026.7.0 [NU6.2] or later. Section 3.12: Mainnet and Testnet](protocol/protocol.pdf#networks)

[^protocol-updated-orchardkeycomponents]: [Zcash Protocol Specification, Version 2026.8.0 [NU6.3]. Section 4.2.3: Orchard Key Components](protocol/protocol.pdf#orchardkeycomponents)

[^zip-0173]: [ZIP 173: Bech32 Format](zip-0173.rst)

[^zip-0312]: [ZIP 312: FROST for Spend Authorization Multisignatures](zip-0312.rst)

[^zip-0312-key-generation]: [ZIP 312: FROST for Spend Authorization Multisignatures — Key Generation](zip-0312.rst#key-generation)

[^zip-0316]: [ZIP 316: Unified Addresses and Unified Viewing Keys](zip-0316.rst)

[^zip-2005]: [ZIP 2005: Ironwood Quantum Recoverability](zip-2005.md)

[^zip-2005-usagewithfrost]: [ZIP 2005: Ironwood Quantum Recoverability — Usage with FROST](zip-2005.md#usagewithfrost)

[^bip-0350]: [BIP 350: Bech32m format for v1+ witness addresses](https://github.com/bitcoin/bips/blob/master/bip-0350.mediawiki)

[^zkool-forum]: [Hanh, Zcash Community Forum, 2026-07-15](https://forum.zcashcommunity.com/t/56660/5)

[^zkool-backup]: [Zkool: the zkfrost member backup string](https://github.com/hhanh00/zkool2/blob/4ad5a89e09e939a415dd7376ec94f0a241f98c8c/rust/src/frost/backup.rs)

[^zkool-padding-fix]: [hhanh00/zkool2#1468: Bech32 decoders reject non-canonical padding](https://github.com/hhanh00/zkool2/pull/1468)

[^zips-1401]: [zcash/zips#1401: Assign a Metadata Typecode for viewing key birthday height](https://github.com/zcash/zips/issues/1401)

[^frost-zec-backup]: [frost-zec: member backup strings](https://github.com/OpenPGP-Wallet/frost-zec/blob/master/src/backup.rs)
