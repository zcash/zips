::

  ZIP: unassigned
  Title: Orchard Address Signatures
  Owners: Blake Emerson Benthall <e@emersonbenthall.com>
  Credits: Jack Grigg <jack@electriccoin.co>
           Daira-Emma Hopwood <daira-emma@electriccoin.co>
           Sean Bowe <sean@electriccoin.co>
  Status: Draft
  Category: Standards / RPC / Wallet
  Created: 2025-12-22
  License: MIT
  Discussions-To: <https://github.com/zcash/zips/issues/XXX>
  Pull-Request: <https://github.com/zcash/zips/pull/XXX>


Terminology
===========

The key words "MUST", "MUST NOT", "SHOULD", "RECOMMENDED", and "MAY"
in this document are to be interpreted as described in BCP 14 [#BCP14]_
when, and only when, they appear in all capitals.

The terms "Orchard" and "Pallas" in this document are to be interpreted
as described in ZIP 224 [#zip-0224]_.

"RedPallas" refers to RedDSA instantiated with the Pallas curve as
specified in the Zcash Protocol Specification [#protocol-concretereddsa]_.

"Unified Address" (UA) refers to an address format as specified in
ZIP 316 [#zip-0316]_.


Abstract
========

This proposal defines a mechanism for creating cryptographic signatures
with Orchard shielded payment addresses, extending the functionality of
ZIP 304 [#zip-0304]_ to the Orchard shielded pool. The mechanism enables
users to prove control of an Orchard address without performing an
on-chain transaction.

This specification reuses the existing Orchard Action circuit with fixed,
deterministic inputs to create a "synthetic spend" proof. This proof
binds the spending key to the address and a message digest, enabling
verification.


Motivation
==========

Cryptographic message signing has become the mainstream approach for
authenticating users to web applications in the cryptocurrency ecosystem.
Ethereum's "Connect Wallet" flow, where users sign a message to prove
control of their address, is now ubiquitous across decentralized finance
applications [#ethereum-sign-in]_. Zcash users need equivalent
functionality [#zcash-forum-signed-messages]_ [#zcash-forum-wishlist]_.

ZIP 304 specifies message signing for Sapling addresses. With the
deployment of Orchard in NU5, users increasingly hold funds in Orchard
addresses or Unified Addresses (UAs) containing Orchard receivers.
Currently these users cannot securely prove control of their addresses.


Privacy Implications
====================

This signature scheme's privacy properties differ fundamentally from
shielded transactions. The purpose is authentication, not concealment;
the signer explicitly demonstrates control of a specific payment address.

Signature Linkability
---------------------

All signatures for a specific payment address are linkable without knowing
the payment address, as the first 32 bytes (the nullifier $\mathsf{nf}$)
are identical. This is consistent with conventional signature schemes.

Signatures from different diversified addresses of the same spending key
remain unlinkable, provided $\alpha$ is never reused.

Anonymity Set
-------------

Unlike transaction signatures verified against on-chain anchors, Orchard
address signatures use a synthetic Merkle tree containing only the signer's
commitment. The signature provides no anonymity set beyond the address itself.


Requirements
============

The signature scheme MUST satisfy the following properties:

* **Authentication**: A valid signature MUST NOT verify against any
  payment address other than the one used to create it.

* **Binding**: A valid signature MUST NOT verify against any modification
  of the signed message.

* **Non-malleability**: It should not be possible to obtain a second valid
  signature (with a different encoding) for the same payment address and
  message without access to the spending key for that payment address.

Non-requirements
================

Multiple signatures by a single payment address are not required to be
unlinkable.


Conventions
===========

The following constants and functions used in this ZIP are defined in the
Zcash Protocol Specification [#protocol]_:

- $\mathsf{MerkleDepth^{Orchard}} = 32$ [#protocol-constants]_
- $\mathsf{Uncommitted^{Orchard}}$ [#protocol-constants]_
- $\mathsf{SinsemillaMerkleCRH^{Orchard}}$ [#protocol-orchardmerklecrh]_
- $\mathsf{DiversifyHash^{Orchard}}(d)$ [#protocol-concretediversifyhash]_
- $\mathsf{NoteCommit^{Orchard}_{rcm}}(\mathsf{g_d}, \mathsf{pk_d}, v, \rho, \psi)$ [#protocol-concreteorchardnotecommit]_
- $\mathsf{DeriveNullifier^{Orchard}_{nk}}(\rho, \psi, \mathsf{cm})$ [#protocol-rhoandnullifiers]_
- $\mathsf{ValueCommit^{Orchard}_{rcv}}(v)$ [#protocol-concretehomomorphiccommit]_
- $\mathsf{SpendAuthSig^{Orchard}.RandomizePrivate}(\alpha, \mathsf{ask})$ [#protocol-concretereddsa]_
- $\mathsf{SpendAuthSig^{Orchard}.RandomizePublic}(\alpha, \mathsf{ak})$ [#protocol-concretereddsa]_
- $\mathsf{SpendAuthSig^{Orchard}.Sign}(\mathsf{sk}, m)$ [#protocol-concretereddsa]_
- $\mathsf{SpendAuthSig^{Orchard}.Verify}(\mathsf{vk}, m, \sigma)$ [#protocol-concretereddsa]_

We also reproduce some notation and functions here for convenience:

- $a\,||\,b$ means the concatenation of sequences $a$ then $b$.

- $\mathsf{repr}_\mathbb{P}(P)$ is the representation of the Pallas elliptic
  curve point $P$ as a bit sequence, defined in [#protocol-pallasandvesta]_.

- $\mathsf{LEBS2OSP}_\ell(B)$ converts a bit sequence to bytes with least
  significant bit first within each byte, as defined in [#protocol-endian]_.

- $\mathsf{BLAKE2b}\text{-}\mathsf{256}(p, x)$ refers to unkeyed BLAKE2b-256
  in sequential mode, with an output digest length of 32 bytes, 16-byte
  personalization string $p$, and input $x$.

- $\mathcal{G}^{\mathsf{Orchard}}$ is the spend authorization generator for
  the Pallas curve, defined in [#protocol-concretespendauthsig]_.

- $\mathcal{V}^{\mathsf{Orchard}}$ is the value commitment generator for
  the Pallas curve, defined in [#protocol-concretehomomorphiccommit]_.

- $\mathsf{Extract}_{\mathbb{P}}(P)$ extracts the x-coordinate of a Pallas
  curve point $P$ as a base field element, as defined in
  [#protocol-concreteextractorpallas]_.

- $\mathsf{GroupHash^{\mathbb{P}}}(D, M)$ is a hash function that maps
  a domain separator $D$ and message $M$ to a point on the Pallas curve,
  as defined in [#protocol-concretegrouphashpallasandvesta]_.

We define the following constant for use in this specification:

- $\mathsf{pk_d^{sig}} := \mathsf{GroupHash^{\mathbb{P}}}(\texttt{"z.cash:Orchard-sig"}, \texttt{"pk"})$
  is the synthetic output public key for Orchard address signatures. This
  constant ensures no known discrete log relationship exists between the
  synthetic output's $\mathsf{pk_d}$ and $\mathsf{g_d}$.


Specification
=============

An Orchard address signature is created by taking the process for creating
an Orchard Action description, and running it with fixed inputs:

- A synthetic Orchard note with a value of $1$ zatoshi and
  $\mathsf{rcm} = 0$, $\rho = 0$, $\psi = 0$.
- An Orchard commitment tree that is empty except for the commitment for
  the synthetic note.

Signature algorithm
-------------------

The inputs to the signature algorithm are:

- The payment address $(\mathsf{d}, \mathsf{pk_d})$,
- The Orchard spending key $\mathsf{sk}$, from which $\mathsf{ask}$,
  $\mathsf{nk}$, and $\mathsf{rivk}$ are derived as specified in
  [#protocol-orchardkeycomponents]_,
- The SLIP-44 [#slip-0044]_ coin type, and
- The message $\mathsf{msg}$ to be signed.

If the input address is a Unified Address (ZIP 316 [#zip-0316]_), the
implementation MUST extract the Orchard receiver. If the UA does not contain
an Orchard receiver, the operation MUST fail. The signature proves control
ONLY of the extracted Orchard receiver component.

The signature is created as follows:

1. Let $\mathsf{ak} = [\mathsf{ask}]\mathcal{G}^{\mathsf{Orchard}}$ and
   $\mathsf{g_d} = \mathsf{DiversifyHash^{Orchard}}(\mathsf{d})$.

2. Let $\mathsf{cm} = \mathsf{NoteCommit^{Orchard}_0}(\mathsf{g_d}, \mathsf{pk_d}, 1, 0, 0)$.

3. Let $\mathsf{rt}$ be the root of a Merkle tree with depth
   $\mathsf{MerkleDepth^{Orchard}}$ and hashing function
   $\mathsf{SinsemillaMerkleCRH^{Orchard}}$, containing $\mathsf{cm}$ at
   position 0, and $\mathsf{Uncommitted^{Orchard}}$ at all other positions.

4. Let $path$ be the Merkle path from position 0 to $\mathsf{rt}$.
   [#protocol-merklepath]_

5. Let $\mathsf{cv} = \mathsf{ValueCommit^{Orchard}_0}(1) = [1]\mathcal{V}^{\mathsf{Orchard}}$.
   This is a constant.

6. Let $\mathsf{nf} = \mathsf{DeriveNullifier^{Orchard}_{nk}}(0, 0, \mathsf{cm})$.

7. Select a random $\alpha \leftarrow \{0 .. r_\mathbb{P} - 1\}$.

8. Let $\mathsf{rk} = \mathsf{SpendAuthSig^{Orchard}.RandomizePublic}(\alpha, \mathsf{ak})$.

9. Construct the synthetic output note with $\mathsf{g_d^{new}} = \mathsf{DiversifyHash^{Orchard}}([0]^{11})$,
   $\mathsf{pk_d^{new}} = \mathsf{pk_d^{sig}}$, $v^{\mathsf{new}} = 0$, $\psi^{\mathsf{new}} = 0$,
   $\mathsf{rcm^{new}} = 0$.

10. Let $\mathsf{cmx} = \mathsf{Extract}_{\mathbb{P}}(\mathsf{NoteCommit^{Orchard}_{0}}(\mathsf{g_d^{new}}, \mathsf{pk_d^{new}}, 0, \mathsf{nf}, 0))$.

11. Let $\mathsf{zkproof}$ be an Orchard Action proof with primary input
    $(\mathsf{rt}, \mathsf{cv}, \mathsf{nf}, \mathsf{rk}, \mathsf{cmx}, 1, 1)$.
    [#protocol-actionstatement]_

    The auxiliary input consists of:

    *Spent note:* $path$, $\mathsf{pos}=0$, $\mathsf{g_d}$, $\mathsf{pk_d}$,
    $v^{\mathsf{old}}=1$, $\rho^{\mathsf{old}}=0$, $\psi^{\mathsf{old}}=0$,
    $\mathsf{rcm^{old}}=0$, $\mathsf{cm}$, $\alpha$, $\mathsf{ak}$, $\mathsf{nk}$,
    $\mathsf{rivk}$.

    *Created note:* $\mathsf{g_d^{new}}$, $\mathsf{pk_d^{new}}$, $v^{\mathsf{new}}=0$,
    $\rho^{\mathsf{new}}=\mathsf{nf}$, $\psi^{\mathsf{new}}=0$, $\mathsf{rcm^{new}}=0$,
    $\mathsf{rcv}=0$.

12. Let $\mathsf{rsk} = \mathsf{SpendAuthSig^{Orchard}.RandomizePrivate}(\alpha, \mathsf{ask})$.

13. Let $\mathsf{coinType}$ be the 4-byte little-endian encoding of the coin
    type in its index form (i.e. 133 for mainnet Zcash).

14. Let $\mathsf{digest} = \mathsf{BLAKE2b\text{-}256}(\texttt{"ZIPXXXOrchSg"}\,||\,\mathsf{coinType}, \mathsf{zkproof} \,||\, \mathsf{msg})$.

15. Let $\mathsf{spendAuthSig} = \mathsf{SpendAuthSig^{Orchard}.Sign}(\mathsf{rsk}, \mathsf{digest})$.

16. Return $(\mathsf{nf}, \mathsf{rk}, \mathsf{zkproof}, \mathsf{spendAuthSig})$.


Verification algorithm
----------------------

The inputs to the verification algorithm are:

- The payment address $(\mathsf{d}, \mathsf{pk_d})$,
- The SLIP-44 [#slip-0044]_ coin type,
- The message $\mathsf{msg}$ that is claimed to be signed, and
- The signature $(\mathsf{nf}, \mathsf{rk}, \mathsf{zkproof}, \mathsf{spendAuthSig})$.

If the address is a Unified Address, extract the Orchard receiver.
If no Orchard receiver is present, return $\mathsf{false}$.

The signature MUST be verified as follows:

1. Let $\mathsf{coinType}$ be the 4-byte little-endian encoding of the coin
   type in its index form.

2. Let $\mathsf{digest} = \mathsf{BLAKE2b\text{-}256}(\texttt{"ZIPXXXOrchSg"}\,||\,\mathsf{coinType}, \mathsf{zkproof} \,||\, \mathsf{msg})$.

3. If $\mathsf{SpendAuthSig^{Orchard}.Verify}(\mathsf{rk}, \mathsf{digest}, \mathsf{spendAuthSig}) = 0$,
   return $\mathsf{false}$.

4. Let $\mathsf{g_d} = \mathsf{DiversifyHash^{Orchard}}(\mathsf{d})$ and
   $\mathsf{cm} = \mathsf{NoteCommit^{Orchard}_0}(\mathsf{g_d}, \mathsf{pk_d}, 1, 0, 0)$.

5. Let $\mathsf{rt}$ be the root of a Merkle tree with depth
   $\mathsf{MerkleDepth^{Orchard}}$ and hashing function
   $\mathsf{SinsemillaMerkleCRH^{Orchard}}$, containing $\mathsf{cm}$ at
   position 0, and $\mathsf{Uncommitted^{Orchard}}$ at all other positions.

6. Let $\mathsf{cv} = \mathsf{ValueCommit^{Orchard}_0}(1)$.

7. Let $\mathsf{g_d^{new}} = \mathsf{DiversifyHash^{Orchard}}([0]^{11})$,
   $\mathsf{pk_d^{new}} = \mathsf{pk_d^{sig}}$, and
   $\mathsf{cmx} = \mathsf{Extract}_{\mathbb{P}}(\mathsf{NoteCommit^{Orchard}_0}(\mathsf{g_d^{new}}, \mathsf{pk_d^{new}}, 0, \mathsf{nf}, 0))$.

8. Verify $\mathsf{zkproof}$ as an Orchard Action proof with primary input
   $(\mathsf{rt}, \mathsf{cv}, \mathsf{nf}, \mathsf{rk}, \mathsf{cmx}, 1, 1)$.
   [#protocol-actionstatement]_ If verification fails, return $\mathsf{false}$.

9. Return $\mathsf{true}$.


Signature encoding
------------------

The raw form of an Orchard address signature is:

$\mathsf{nf}\,||\,\mathsf{LEBS2OSP}_{256}(\mathsf{repr}_{\mathbb{P}}(\mathsf{rk}))\,||\,\mathsf{zkproof}\,||\,\mathsf{spendAuthSig}$

where:

- $\mathsf{nf}$ is 32 bytes (the nullifier)
- $\mathsf{rk}$ is 32 bytes (the randomized spend verifying key)
- $\mathsf{zkproof}$ is 4992 bytes [#protocol-orchardproofsize]_

  The proof size follows the formula $2720 + 2272 \cdot n$ where $n$ is the
  number of actions. For this specification, $n = 1$, yielding
  $2720 + 2272 = 4992$ bytes. The 2720-byte base includes the Halo 2
  accumulator, and each action adds 2272 bytes of proof data.
- $\mathsf{spendAuthSig}$ is 64 bytes (RedPallas signature)

The total size is 5120 bytes.

When encoding in a human-readable format, implementations SHOULD use
standard Base64 [#RFC4648]_. The encoded form is the string ``"zipXXX:"``
followed by the Base64-encoded raw signature.

Comparison with ZIP 304
-----------------------

+----------------------+----------------------+----------------------+
| Aspect               | ZIP 304 (Sapling)    | This ZIP (Orchard)   |
+======================+======================+======================+
| Circuit              | Spend only           | Action (spend+output)|
+----------------------+----------------------+----------------------+
| Proof system         | Groth16              | Halo 2               |
+----------------------+----------------------+----------------------+
| Signature size       | 320 bytes            | 5120 bytes           |
+----------------------+----------------------+----------------------+
| Curve                | Jubjub               | Pallas               |
+----------------------+----------------------+----------------------+
| Personalization      | ``"ZIP304Signed"``   | ``"ZIPXXXOrchSg"``   |
+----------------------+----------------------+----------------------+


Rationale
=========

Synthetic Note Construction
---------------------------

We reuse the Orchard Action circuit to avoid defining a new circuit and
additional parameter generation. A 1-zatoshi value (rather than zero)
ensures the payment address is fully bound, as zero-value notes have
certain constraints disabled. We set $\mathsf{rcm}$, $\rho$, and $\psi$
to zero since the hiding properties are unnecessary for this application.

Synthetic Output Construction
-----------------------------

The synthetic output uses $\mathsf{pk_d^{sig}}$ (derived via $\mathsf{GroupHash}$)
rather than $\mathsf{pk_d^{new}} = \mathsf{g_d^{new}}$. Setting
$\mathsf{pk_d^{new}} = \mathsf{g_d^{new}}$ would imply $\mathsf{ivk} = 1$,
which is cryptographically pathological.

This construction is valid because the Action circuit's "Diversified address
integrity" constraint [#protocol-actionstatement]_ verifies
$\mathsf{pk_d} = [\mathsf{ivk}]\,\mathsf{g_d}$ only for the spent note,
proving the signer controls the claimed address. For the created note,
the circuit only checks that $\mathsf{cmx}$ matches the committed note values
via the "New note commitment integrity" constraint; it does not verify any
relationship between $\mathsf{pk_d^{new}}$ and the signer's $\mathsf{ivk}$.
Therefore, $\mathsf{pk_d^{sig}}$ can be any arbitrary Pallas point, and
$\mathsf{GroupHash}$ provides a well-defined, verifiable constant with no
known discrete log relationship to $\mathsf{g_d^{new}}$.

We set $\rho^{\mathsf{new}} = \mathsf{nf}$ because the Action circuit requires
$\rho^{\mathsf{new}} = \mathsf{nf^{old}} \pmod{q}$.

Proof System Choice
-------------------

We reuse the existing Orchard Action circuit rather than defining a bespoke
signature circuit. This is the path of least resistance: it minimizes
implementation effort and reduces new security assumptions, but results in
significantly larger signatures (5120 bytes vs ZIP 304's 320 bytes). This
size may present challenges for bandwidth-constrained environments and
visual encoding (QR codes and similar).

Unlike ZIP 304, where a dedicated circuit would have required a trusted
setup ceremony, Halo 2 has no trusted setup. Smaller signatures are achievable
via a dedicated ownership circuit, direct Schnorr signing with a derivation
proof, proof aggregation for batched verification, or alternative proof
systems. A future ZIP MAY define a compact scheme.

Synthetic Nullifiers
--------------------

Fixing $\rho = 0$ achieves negligible collision probability with on-chain
nullifiers (which have essentially random $\rho$ values) while enabling the
documented linkability property for signatures from the same address.

Unified Address Handling
------------------------

We mandate that the Orchard receiver be extracted from the UA. Proving control
of all constituent receivers would add significant complexity.

.. caution::

   A valid Orchard address signature for a UA does not prove that
   the signer controls the other receivers in that UA. A malicious actor
   could construct a UA containing their own Orchard receiver alongside
   another party's Transparent or Sapling receiver.

   Implementations SHOULD only permit UAs where every constituent receiver
   has a standardized signing scheme (Orchard: this spec; Sapling: ZIP 304;
   Transparent P2PKH: Bitcoin message signing). Where comprehensive
   verification is not feasible, implementations are STRONGLY RECOMMENDED
   to restrict acceptance to Orchard-only Unified Addresses.


Security Considerations
=======================

Replay Protection
-----------------

This specification does not mandate a particular message structure for replay
protection. As with Ethereum signed messages, applications SHOULD define their
own domain separation within the message content (e.g., including chain ID,
contract address, nonce, or timestamp) to prevent cross-context replay attacks.

Proof Malleability
------------------

Halo 2 proofs [#halo2-proving-system]_ can in principle be re-randomized.
We prevent this from affecting signature security by binding the encoding
of $\mathsf{zkproof}$ to the signed digest; any proof modification would
invalidate the RedPallas signature.

Most signature data is inherently non-malleable:

- $\mathsf{nf}$ is a binary public input to $\mathsf{zkproof}$.
- $\mathsf{rk}$ is bound to $\mathsf{spendAuthSig}$ by RedPallas design.
- RedPallas signatures are themselves non-malleable.

Unified Address Considerations
------------------------------

A signature using an Orchard receiver from a UA only proves control of that
component. Verifiers SHOULD be aware that this does not prove control of the
entire UA.


Reference implementation
========================

TBD


References
==========

.. [#BCP14] `Information on BCP 14 — "RFC 2119: Key words for use in RFCs to Indicate Requirement Levels" and "RFC 8174: Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words" <https://www.rfc-editor.org/info/bcp14>`_
.. [#RFC4648] `RFC 4648: The Base16, Base32, and Base64 Data Encodings <https://www.rfc-editor.org/rfc/rfc4648>`_
.. [#ethereum-sign-in] `Sign-In with Ethereum (EIP-4361) <https://eips.ethereum.org/EIPS/eip-4361>`_
.. [#zcash-forum-signed-messages] `Zcash Community Forum: Finding a path to signed messages <https://forum.zcashcommunity.com/t/finding-a-path-to-signed-messages/51236>`_
.. [#zcash-forum-wishlist] `Zcash Community Forum: The Zcasher Wish List — Signed Messages <https://forum.zcashcommunity.com/t/lets-create-the-zcasher-wish-list/51143/3>`_
.. [#protocol-orchardproofsize] `Zcash Protocol Specification, Version 2024.5.1 or later. Section 7.1: Transaction Encoding and Consensus <protocol/protocol.pdf#txnencoding>`_
.. [#protocol] `Zcash Protocol Specification, Version 2024.5.1 or later <protocol/protocol.pdf>`_
.. [#protocol-merklepath] `Zcash Protocol Specification, Version 2024.5.1 or later. Section 4.9: Merkle Path Validity <protocol/protocol.pdf#merklepath>`_
.. [#protocol-actionstatement] `Zcash Protocol Specification, Version 2024.5.1 or later. Section 4.17.4: Action Statement (Orchard) <protocol/protocol.pdf#actionstatement>`_
.. [#protocol-constants] `Zcash Protocol Specification, Version 2024.5.1 or later. Section 5.3: Constants <protocol/protocol.pdf#constants>`_
.. [#protocol-endian] `Zcash Protocol Specification, Version 2024.5.1 or later. Section 5.1: Integers, Bit Sequences, and Endianness <protocol/protocol.pdf#endian>`_
.. [#protocol-orchardmerklecrh] `Zcash Protocol Specification, Version 2024.5.1 or later. Section 5.4.1.3: SinsemillaMerkleCRH Hash Function <protocol/protocol.pdf#orchardmerklecrh>`_
.. [#protocol-concretediversifyhash] `Zcash Protocol Specification, Version 2024.5.1 or later. Section 5.4.1.6: DiversifyHash^Sapling and DiversifyHash^Orchard Hash Functions <protocol/protocol.pdf#concretediversifyhash>`_
.. [#protocol-concreteextractorpallas] `Zcash Protocol Specification, Version 2024.5.1 or later. Section 5.4.9.7: Coordinate Extractor for Pallas <protocol/protocol.pdf#concreteextractorpallas>`_
.. [#protocol-rhoandnullifiers] `Zcash Protocol Specification, Version 2024.5.1 or later. Section 4.16: Computing rho values and Nullifiers <protocol/protocol.pdf#rhoandnullifiers>`_
.. [#protocol-orchardkeycomponents] `Zcash Protocol Specification, Version 2024.5.1 or later. Section 4.2.3: Orchard Key Components <protocol/protocol.pdf#orchardkeycomponents>`_
.. [#protocol-concretespendauthsig] `Zcash Protocol Specification, Version 2024.5.1 or later. Section 5.4.7.1: Spend Authorization Signature (Sapling and Orchard) <protocol/protocol.pdf#concretespendauthsig>`_
.. [#protocol-concretereddsa] `Zcash Protocol Specification, Version 2024.5.1 or later. Section 5.4.7: RedDSA, RedJubjub, and RedPallas <protocol/protocol.pdf#concretereddsa>`_
.. [#protocol-concretehomomorphiccommit] `Zcash Protocol Specification, Version 2024.5.1 or later. Section 5.4.8.3: Homomorphic Pedersen commitments (Orchard) <protocol/protocol.pdf#concretehomomorphiccommit>`_
.. [#protocol-concreteorchardnotecommit] `Zcash Protocol Specification, Version 2024.5.1 or later. Section 5.4.8.5: Sinsemilla commitments <protocol/protocol.pdf#concreteorchardnotecommit>`_
.. [#protocol-pallasandvesta] `Zcash Protocol Specification, Version 2024.5.1 or later. Section 5.4.9.6: Pallas and Vesta <protocol/protocol.pdf#pallasandvesta>`_
.. [#protocol-concretegrouphashpallasandvesta] `Zcash Protocol Specification, Version 2024.5.1 or later. Section 5.4.9.8: Group Hash into Pallas and Vesta <protocol/protocol.pdf#concretegrouphashpallasandvesta>`_
.. [#halo2-proving-system] `The halo2 Book: 3.1. Proving system <https://zcash.github.io/halo2/design/proving-system.html>`_
.. [#zip-0224] `ZIP 224: Orchard Shielded Protocol <zip-0224.rst>`_
.. [#zip-0304] `ZIP 304: Sapling Address Signatures <zip-0304.rst>`_
.. [#zip-0316] `ZIP 316: Unified Addresses and Unified Viewing Keys <zip-0316.rst>`_
.. [#slip-0044] `SLIP-0044 : Registered coin types for BIP-0044 <https://github.com/satoshilabs/slips/blob/master/slip-0044.md>`_
