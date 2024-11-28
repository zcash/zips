::

  ZIP: XXX
  Title: Complete Diversifier Hashing for Sapling
  Owners: Daira-Emma Hopwood <daira-emma@electriccoin.co>
          Jack Grigg <str4d@electriccoin.co>
  Credits: Kris Nuttycombe
  Status: Draft
  Category: Standards / Wallet
  Created: 2024-11-28
  License: MIT


Terminology
===========

The key words "MUST" and "MUST NOT" in this document are to be interpreted as described in
BCP 14 [#BCP14]_ when, and only when, they appear in all capitals.

The character § is used when referring to sections of the Zcash Protocol Specification.
[#protocol]_

The terms "Mainnet" and "Testnet" are to be interpreted as described in
§ 3.12 ‘Mainnet and Testnet’. [#protocol-networks]_

"Jubjub" refers to the elliptic curve defined in § 5.4.9.3 ‘Jubjub’ [#protocol-jubjub]_.


Abstract
========

In the original design of the Sapling shielded protocol, the "diversifier hash" that maps
diversifiers to curve points was an incomplete function, resulting in about half of all
diversifiers being invalid. When used with ZIP 32 [#zip-0032]_, this also meant that about
half of all Sapling diversifier *indices* are invalid for a given ZIP 32 account.

This proposal modifies the Sapling protocol to make its diversifier hash complete.


Motivation
==========

TBD


Requirements
============

* Every Sapling diversifier must be valid, except possibly with negligible probability.
* The proposal must be compatible with the existing Sapling design in the sense that any
  previously valid diversifier (or diversifier index) will map to the same curve point.
  This property is essential in order for previously created addresses and notes to
  remain valid.
* The algorithm to decrypt a note ciphertext must be well specified for transactions
  at any block height.


Specification
=============

In general terms, the method used to make the diversifier hash complete while maintaining
compatibility is to:

* Define a new complete random-oracle encoding into the large prime-order subgroup of the
  Jubjub curve, following RFC 9380 [#RFC-9380]_.
* Define the new diversifier hash to use the incomplete group hash for diversifiers on which
  it is defined (i.e. does not return $\bot$), and the complete random-oracle encoding
  otherwise.

The complete random-oracle encoding is considered to be an internal primitive only. It
MUST NOT be used for diversifiers on which the incomplete group hash is defined.

Complete random-oracle encoding
-------------------------------

In this section we define a complete random-oracle encoding [#RFC-9380-random-oracle-encodings]_
to the large prime-order subgroup of the Jubjub curve, named $\texttt{jubjub\_XMD:BLAKE2b\_ELL2\_RO\_}$.
The name of this primitive follows the convention established by section 8.10 of RFC 9380
[#RFC-9380-suite-id-naming-conventions]_. This name is not by itself sufficient to infer all
parameters of the algorithm, which are specified below.

Jubjub is a complete Twisted Edwards curve ([#protocol-jubjub]_ and section 4.3.4 of [#BL2017]_).
In that respect it is similar mathematically to the Edwards25519 curve; in particular it is
birationally equivalent to a particular Montgomery curve [#protocol-ecbackground]_. RFC 9380
already defines a parameter suite for Edwards25519 [#RFC-9380-suites-for-curve25519-and-e]_, and
we specify $\texttt{jubjub\_XMD:BLAKE2b\_ELL2\_RO\_}$ following the same pattern for Jubjub.

The result of the encoding is obtained by adding (as curve points) the results of two maps to
the Montgomery curve using the method of section 6.8.2 of RFC 9380 [#RFC-9380-elligator-2-method-2]_
(based on the Elligator 2 mapping originally defined in [#BHKL13]_), and then applying a rational
map to obtain a Jubjub curve point.

Let $q_{\mathbb{J}}$, $a_{\mathbb{J}}$, $d_{\mathbb{J}}$, and $h_{\mathbb{J}}$ be as defined in
[#protocol-jubjub]_.

$\texttt{jubjub\_XMD:BLAKE2b\_ELL2\_RO\_}$ is defined as an RFC-9380 hash-to-curve suite
[#RFC-9380-suites-for-hashing]_ with the following parameters:

* encoding type: hash_to_curve
* $E$ (Jubjub curve):
    $a_{\mathbb{J}} \cdot v^2 + w^2 = 1 + d_{\mathbb{J}} \cdot v^2 \cdot w^2$
* $p$ (field characteristic): $q_{\mathbb{J}}$
* $m$ (field extension degree): $1$
* $k$ (target security bits): $256$
* expand_message: expand_message_xmd
* $H$: BLAKE2b-512
* $L$: $64$
* $f$: Twisted Edwards Elligator 2 method (Section 6.8.2) [#RFC-9380-elligator-2-method-2]_
* $M$ (Montgomery curve birationally equivalent to Jubjub):
    $K \cdot t^2 = s^3 + J \cdot s^2 + s$, where $K = 1$ and $J = 40962$
* rational_map: the "generic mapping" defined in RFC 9380 Appendix D.1 [#RFC-9380-generic-mapping-from-montgo]_
* $Z$: $5$
* h_eff: $h_{\mathbb{J}}$

Non-normative notes:

* RFC 9380 denotes Twisted Edwards coordinates as $(v, w)$ rather than $(u, v)$.
  This is because it uses $u$ for the field element to be mapped.
* The "security level" $k$ in the RFC is taken to be $256$. Although this is greater than
  the conjectured $125.8$-bit security of the Jubjub curve against generic (e.g. Pollard rho)
  attacks [#Hopwood2022]_, this design choice is consistent with other instances of extracting
  a uniformly distributed field element from a hash output in the Sapling protocol, such as
  $\mathsf{ToScalar^{Sapling}}$ defined in [#protocol-saplingkeycomponents]_, and
  $\mathsf{H}^⊛$ defined in [#protocol-concretereddsa]_.
* $Z = 5$ is the non-square of smallest magnitude in $\mathbb{F}_{q_{\mathbb{J}}}$, as
  determined using the algorithm in RFC 9380 Appendix H.3 [#RFC-9380-finding-z-for-elligator-2]_.
* The "generic mapping" from the Montgomery form to the Twisted Edwards form of Jubjub
  defined by [#RFC-9380-generic-mapping-from-montgo]_ is *not* the same mapping as
  $\mathsf{MontToCtEdwards}$ [#protocol-cctconversion]_ used in the Sapling circuits.
  The latter has an extra factor of ${}^{+}\kern-0.65em\sqrt{-40964}$ in the resulting first
  Twisted Edwards coordinate.

DiversifyHash
-------------

Modify the definition of $\mathsf{DiversifyHash}$ in ... [#protocol-concretediversifyhash].

.. math::

    \begin{array}{l}
      \mathsf{CompleteHash}(M \;{\small ⦂}\; \mathbb{B}^{{\tiny\mathbb{Y}}[\mathbb{N}]}) \;{\small ⦂}\; \mathbb{J}^{(r)} = \\
      \hspace{2em}\texttt{jubjub\_XMD:BLAKE2b\_ELL2\_RO\_}\mathsf{.hash\_to\_curve}(\texttt{"z.cash:Sapling-gd-jubjub\_XMD:BLAKE2b\_ELL2\_RO\_"}, M) \\
      \\
      \mathsf{IncompleteHash}(M \;{\small ⦂}\; \mathbb{B}^{{\tiny\mathbb{Y}}[\mathbb{N}]}) \;{\small ⦂}\; \mathbb{J}^{(r)} = \\
      \hspace{2em}\mathsf{GroupHash}_U^{\mathbb{J}^{(r)*}}(\texttt{"Zcash\_gd"}, \mathsf{LEBS2OSP_{\ell_d}}(\mathsf{d})) \\[2ex]
    \end{array}
 
    \mathsf{DiversifyHash^{Sapling}}(\mathsf{d}) = \begin{cases}
      \mathsf{IncompleteHash}(\mathsf{d}),&\text{ if } \mathsf{IncompleteHash}(\mathsf{d}) \neq \bot \\
      \mathsf{CompleteHash}(\mathsf{d}),  &\text{ if } \mathsf{IncompleteHash}(\mathsf{d}) = \bot \text{ and } \mathsf{CompleteHash}(\mathsf{d}) \neq \bot \hspace{6em} \\
      \mathsf{CompleteHash}(\texttt{""}), &\text{ otherwise}
    \end{cases}


Note Encryption
---------------

Modify the uses of $\mathsf{DiversifyHash^{Sapling}}$ as follows: TBD


Deployment
==========

Let $\mathsf{ZipXXXActivationHeight}$ be the activation height of this ZIP. This is the first block
height at which it is valid for transactions in that block to contain Sapling Output descriptions
with notes having a diversifier that would be invalid using the previously defined
$\mathsf{DiversifyHash^{Sapling}}$.

TODO:

* replace XXX with the number of this ZIP;
* specify the activation height.

Before the activation height, all relevant wallets implementing Sapling should be confirmed
to have implemented this specification (apart from setting the mainnet height) and to have
conducted comprehensive interoperability testing.


Test Vectors
============

``jubjub_XMD:BLAKE2b_ELL2_RO_`` test vectors
--------------------------------------------

The following test vectors for the $\texttt{jubjub\_XMD:BLAKE2b\_ELL2\_RO\_}$ random-oracle
encoding are in the same format as used in Appendix J of RFC 9380 [#RFC-9380-appendix-J]_.
Note that the RFC denotes Twisted Edwards coordinates as ``(x,`` ``y)`` rather than $(u, v)$.

::

  suite   = jubjub_XMD:BLAKE2b_ELL2_RO_
  dst     = z.cash:Sapling-gd-jubjub_XMD:BLAKE2b_ELL2_RO_

  msg     = Everybody's right to beautiful, radiant things
  P.x     =
  P.y     =
  u[0]    =
  u[1]    =
  Q0.x    =
  Q0.y    =
  Q1.x    =
  Q1.y    =

DiversifyHash test vectors
--------------------------

TBD


Reference Implementation
========================

TBD


References
==========

.. [#BCP14] `Information on BCP 14 — "RFC 2119: Key words for use in RFCs to Indicate Requirement Levels" and "RFC 8174: Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words" <https://www.rfc-editor.org/info/bcp14>`_
.. [#protocol] `Zcash Protocol Specification, Version 2024.6.0 or later [NU6] <protocol/protocol.pdf>`_
.. [#protocol-networks] `Zcash Protocol Specification, Version 2024.6.0. Section 3.12: Mainnet and Testnet <protocol/protocol.pdf#networks>`_
.. [#protocol-saplingkeycomponents] `Zcash Protocol Specification, Version 2024.6.0. Section 4.2.2: Sapling Key Components <protocol/protocol.pdf#saplingkeycomponents>`_
.. [#protocol-concretereddsa] `Zcash Protocol Specification, Version 2024.6.0. Section 5.4.7: RedDSA, RedJubjub, and RedPallas <protocol/protocol.pdf#concretereddsa>`_
.. [#protocol-jubjub] `Zcash Protocol Specification, Version 2024.6.0. Section 5.4.9.3: Jubjub <protocol/protocol.pdf#jubjub>`_
.. [#protocol-ecbackground] `Zcash Protocol Specification, Version 2024.6.0. Appendix A.2: Elliptic curve background <protocol/protocol.pdf#ecbackground>`_
.. [#protocol-cctconversion] `Zcash Protocol Specification, Version 2024.6.0. Appendix A.3.3.3: ctEdwards ↔ Montgomery conversion <protocol/protocol.pdf#cctconversion>`_
.. [#RFC-9380] `RFC 9380: Hashing to Elliptic Curves <https://www.rfc-editor.org/rfc/rfc9380.html#elligator2>`_
.. [#RFC-9380-random-oracle-encodings] `RFC 9380: Hashing to Elliptic Curves. Section 2.2.3: Random Oracle Encodings <https://www.rfc-editor.org/rfc/rfc9380.html#name-random-oracle-encodings>`_
.. [#RFC-9380-elligator-2-method-2] `RFC 9380: Hashing to Elliptic Curves. Section 6.8.2: Elligator 2 Method <https://www.rfc-editor.org/rfc/rfc9380.html#elligator-2-method-2>`_
.. [#RFC-9380-suites-for-hashing] `RFC 9380: Hashing to Elliptic Curves. Section 8: Suites for Hashing <https://www.rfc-editor.org/rfc/rfc9380.html#https://www.rfc-editor.org/rfc/rfc9380.html#name-suites-for-hashing>`_
.. [#RFC-9380-suites-for-curve25519-and-e] `RFC 9380: Hashing to Elliptic Curves. Section 8.5: Suites for curve25519 and edwards25519 <https://www.rfc-editor.org/rfc/rfc9380.html#name-suites-for-curve25519-and-e>`_
.. [#RFC-9380-suite-id-naming-conventions] `RFC 9380: Hashing to Elliptic Curves. Section 8.10: Suite ID Naming Conventions <https://www.rfc-editor.org/rfc/rfc9380.html#name-suite-id-naming-conventions>`_
.. [#RFC-9380-generic-mapping-from-montgo] `RFC 9380: Hashing to Elliptic Curves. Appendix D.1: Generic Mapping from Montgomery to Twisted Edwards <https://www.rfc-editor.org/rfc/rfc9380.html#name-generic-mapping-from-montgo>`_
.. [#RFC-9380-finding-z-for-elligator-2] `RFC 9380: Hashing to Elliptic Curves. Appendix H.3: Finding Z for Elligator 2 <https://www.rfc-editor.org/rfc/rfc9380.html#name-finding-z-for-elligator-2>`_
.. [#RFC-9380-appendix-j] `RFC 9380: Hashing to Elliptic Curves. Appendix J: Suite Test Vectors <https://www.rfc-editor.org/rfc/rfc9380.html#appendix-J>`_
.. [#zip-0032] `ZIP 32: Shielded Hierarchical Deterministic Wallets <zip-0032.rst>`_
.. [#BHKL13] `Daniel Bernstein, Mike Hamburg, Anna Krasnova, and Tanje Lange. "Elligator: elliptic-curve points indistinguishable from uniform random strings." DOI:10.1145/2508859.2516734 <https://doi.org/10.1145/2508859.2516734>`_ 
.. [#BL2017] `Daniel Bernstein and Tanja Lange. "Montgomery curves and the Montgomery ladder." Cryptology ePrint Archive: Report 2017/293 <https://eprint.iacr.org/2017/293>`_
.. [#Hopwood2022] `Daira Hopwood. "Understanding the Security of Zcash." Slide 41: Cryptographic strength <https://raw.githubusercontent.com/daira/zcash-security/main/zcash-security.pdf>`_
