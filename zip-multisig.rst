::

  ZIP: XXX
  Title: Multisig and threshold-sig shielded transactions 
  Authors: Omer Shlomovits <omer@kzencorp.com>
  Credits: Ariel Nof <nofdinar@gmail.com>
  Category: Informational 
  Created: 2019-03-31
  License: MIT


 Terminology
===========

 The key words "MUST" and "MUST NOT" in this document are to be interpreted as described in RFC 2119.

 Abstract
========

`SpendAuthSig` is a Schnorr based signature used in Sapling to sign transactions.
In this ZIP we describe an efficient protocol for threshold signing. The protocol can be used
to protect private signing keys by distributing them among several parties, who upon request
can run the threshold protocol to generate a signature. The transaction will remain shielded but privacy will not hold between co-signers.  

 Motivation
==========

Support for multisig transactions will level up the security available to Zcash users, and broaden the types of users who can safely take advantage of Zcash’s robust privacy while mitigating other threats to their funds.

 Specification
==========
We start by describing the two party case, followed by an extension to any number of parties and any threshold. We refer to the [paper](https://github.com/KZen-networks/paradise-city/tree/master/paper%5Bwip%5D) for the security proof of the schemes

Here is a high level description of a 2-party multisig: 

**2p-KeyGen**
1) Each party `P_i` chooses a random `ask_i` and computes `ak_i = ask_i *  G` (`G` is Jubjub ec generator)
2) The parties run a secure variant of ECDH to exchange `ak_i` and prove knowledge of `ask_i`
3) The parties set `ak = ak_1 + ak_2` as the SpendAuthSig public-key

**2p-Signing**
1) The parties run a coin-toss protocol to get random `alpha`
2) Each party locally computes `vk = ak + alpha * G`
3) Each party computes a pseudo-random function F with random key `T_i` and input `vk||m` for message `m`. We call the result  `r_i`
4) Each party computes `R_i = r_i *  G` 
5) The parties run the ECDH variant and define `R = R_1 + R_2`
6) Party `P_1` locally computes `S_1 = r_1 + H(R||vk||m) * (ask_1 + alpha)` and sends it to `P_2`
7) Party `P_2` locally computes `S_2 = r_2 + H(R||vk||m) * ask_2` and sends it to `P_1`
8) The parties set `S = S_1 + S_2` and each checks that `verify(m,(R,S)) =1`. If the equality holds, than it outputs `(S,R)`

Here is a detailed description of the protocol as it is currently implemented in [paradise-city](https://github.com/KZen-networks/paradise-city): 

**2p-KeyGen**
1) `P_1` chooses random scalar `ask_1`, plays the prover in a non-interactive (using Fiat Shamir) sigma protocol for proof of knowledge of discrete log ([proof and ref](https://github.com/KZen-networks/curv/blob/master/src/cryptographic_primitives/proofs/sigma_dlog.rs)). Finally `P_1` commits to the public key `ak_1` and to the proof of knowledge. `P_1` sends the commitment as first message to party `P_2`. We use hash based commitment
2) `P_2` chooses random scalar `ask_2`, runs a PoK of DLog and sends the proof and public key `ak_2` to `P_1`
3) `P_1` verifies the proof and if true send a decommitment to `P_2` with his public key and proof. `P_1` sets his secret share to `ask_1` and the public key to `ak = ak_1 + ak_2`.
4) `P_2` verifies makes sure the decommitment is for the commitment from the first message and verifies the proof, if true sets his secret share `ask_2` and the public key to `ak = ak_1 + ak_2`.


**2p-Signing**
Given a message `m` and the outputs of 2P-KeyGen the parties run the following protocol to get a signature: 
1) `P_1` choose a random seed and sends a Pederson commitment of it to `P_2`. This message initiates a coin flip protocol for many coins with optimal rounds ([ref](https://github.com/KZen-networks/curv/blob/master/src/cryptographic_primitives/twoparty/coin_flip_optimal_rounds.rs)). 
2) `P_2` verifies the proof, if true, chooses a random seed and sends it to `P_1`.
3) `P_1` computes the result `alpha` as the xor of the two seeds. `P_1` sends a decommitment and a proof of correct use of blinding factor. `P_1` computes `vk = ak + alpha * G`
4) `P_2` verifies the proof and computes `alpha`. `P_2` computes `vk = ak + alpha * G`
5) Since we want concurrent signing (see discussion in section 4.3 of [paper](https://eprint.iacr.org/2017/552.pdf)) we repeat 2p-KeyGen steps 1-4 with the difference that instead of PoK of DLog we prove knowledge that a tuple is a DDH tuple ([proof and ref](https://github.com/KZen-networks/curv/blob/master/src/cryptographic_primitives/proofs/sigma_ec_ddh.rs)). At the end of this phase `P_1` has secret `r_1`, `P_1` has secret `r_2` and both know  `R = R_1 + R_2`.
6) Party `P_1` locally computes `S_1 = r_1 + H(R||vk||m) * (ask_1 + alpha)` and sends it to `P_2`
7) Party `P_2` locally computes `S_2 = r_2 + H(R||vk||m) * ask_2` and sends it to `P_1`
8) The parties set `S = S_1 + S_2` and each checks that `verify(m,(R,S)) =1`. If the equality holds, than it outputs `(S,R)`





