.. Title: Specifications and Zcash Improvement Proposals


What are ZIPs?
--------------

Zcash Improvement Proposals (ZIPs) are the way to:

* propose new features for the the `Zcash cryptocurrency <https://z.cash/>`__ and their rationale,
* specify the implementation details of the feature,
* collect community input on the proposal, and
* document design decisions.


Contributing
------------

The authors of a ZIP are responsible for building consensus within the community
and documenting / addressing dissenting opinions.

Anyone can write a ZIP! We encourage community contributions and decentralization
of work on the Zcash protocol. If you’d like to bounce ideas off people before formally
writing a ZIP, we encourage it! Visit the `ZcashCommunity Discord chat <https://discord.gg/kdjfvps>`__
to talk about your idea.

Participation in the Zcash project is subject to a `Code of
Conduct <https://github.com/zcash/zcash/blob/master/code_of_conduct.md>`__.

The Zcash protocol is documented in its `Protocol Specification <protocol/protocol.pdf>`__.

To start contributing, first read `ZIP 0 <zip-0000.rst>`__ which documents the ZIP process.
Then clone `this repo <https://github.com/zcash/zips>`__ from GitHub, and start adding
your draft ZIP, formatted either as reStructuredText or as Markdown.

For example, if using reStructuredText, use a filename matching ``draft-*.rst``.
Use ``make`` to check that you are using correct
`reStructuredText <https://docutils.sourceforge.io/rst.html>`__ or
`Markdown <https://pandoc.org/MANUAL.html#pandocs-markdown>`__ syntax,
and double-check the generated ``draft-*.html`` file before filing a Pull Request.


Canopy ZIPs
-----------

This is the list of ZIPs included in Canopy (Network Upgrade 4), due to activate on
mainnet in mid-November 2020:

- `ZIP 207: Funding Streams <zip-0207.rst>`__
- `ZIP 211: Disabling Addition of New Value to the Sprout Value Pool <zip-0211.rst>`__
- `ZIP 212: Allow Recipient to Derive Sapling Ephemeral Secret from Note Plaintext <zip-0212.rst>`__
- `ZIP 214: Consensus rules for a Zcash Development Fund <zip-0214.rst>`__
- `ZIP 215: Explicitly Defining and Modifying Ed25519 Validation Rules <zip-0215.rst>`__
- `ZIP 251: Deployment of the Canopy Network Upgrade <zip-0251.rst>`__


License
-------

Unless otherwise stated in this repository’s individual files, the
contents of this repository are released under the terms of the MIT
license. See `COPYING <COPYING.rst>`__ for more information or see
https://opensource.org/licenses/MIT .

Index of ZIPs
-------------

.. raw:: html

  <embed><table>
    <tr> <th>ZIP</th> <th>Title</th> <th>Status</th> </tr>
    <tr> <td>0</td> <td class="left"><a href="zip-0000.rst">ZIP Process</a></td> <td>Active</td>
    <tr> <td><span class="reserved">1</span></td> <td class="left"><a class="reserved" href="zip-0001.rst">Network Upgrade Policy and Scheduling</a></td> <td>Reserved</td>
    <tr> <td><span class="reserved">2</span></td> <td class="left"><a class="reserved" href="zip-0002.rst">Design Considerations for Network Upgrades</a></td> <td>Reserved</td>
    <tr> <td><span class="reserved">22</span></td> <td class="left"><a class="reserved" href="zip-0022.rst">Specification of getblocktemplate for Zcash</a></td> <td>Reserved</td>
    <tr> <td>32</td> <td class="left"><a href="zip-0032.rst">Shielded Hierarchical Deterministic Wallets</a></td> <td>Final</td>
    <tr> <td><span class="reserved">76</span></td> <td class="left"><a class="reserved" href="zip-0076.rst">Transaction Signature Validation before Overwinter</a></td> <td>Reserved</td>
    <tr> <td>143</td> <td class="left"><a href="zip-0143.rst">Transaction Signature Validation for Overwinter</a></td> <td>Final</td>
    <tr> <td>173</td> <td class="left"><a href="zip-0173.rst">Bech32 Format</a></td> <td>Final</td>
    <tr> <td>200</td> <td class="left"><a href="zip-0200.rst">Network Upgrade Mechanism</a></td> <td>Final</td>
    <tr> <td>201</td> <td class="left"><a href="zip-0201.rst">Network Peer Management for Overwinter</a></td> <td>Final</td>
    <tr> <td>202</td> <td class="left"><a href="zip-0202.rst">Version 3 Transaction Format for Overwinter</a></td> <td>Final</td>
    <tr> <td>203</td> <td class="left"><a href="zip-0203.rst">Transaction Expiry</a></td> <td>Final</td>
    <tr> <td><span class="reserved">204</span></td> <td class="left"><a class="reserved" href="zip-0204.rst">P2P Network Protocol Differences from Bitcoin</a></td> <td>Reserved</td>
    <tr> <td>205</td> <td class="left"><a href="zip-0205.rst">Deployment of the Sapling Network Upgrade</a></td> <td>Final</td>
    <tr> <td>206</td> <td class="left"><a href="zip-0206.rst">Deployment of the Blossom Network Upgrade</a></td> <td>Final</td>
    <tr> <td>207</td> <td class="left"><a href="zip-0207.rst">Funding Streams</a></td> <td>Implemented (zcashd)</td>
    <tr> <td>208</td> <td class="left"><a href="zip-0208.rst">Shorter Block Target Spacing</a></td> <td>Final</td>
    <tr> <td>209</td> <td class="left"><a href="zip-0209.rst">Prohibit Negative Shielded Chain Value Pool Balances</a></td> <td>Final</td>
    <tr> <td><strike>210</strike></td> <td class="left"><strike><a href="zip-0210.rst">Sapling Anchor Deduplication within Transactions</a></strike></td> <td>Withdrawn</td>
    <tr> <td>211</td> <td class="left"><a href="zip-0211.rst">Disabling Addition of New Value to the Sprout Chain Value Pool</a></td> <td>Implemented (zcashd)</td>
    <tr> <td>212</td> <td class="left"><a href="zip-0212.rst">Allow Recipient to Derive Sapling Ephemeral Secret from Note Plaintext</a></td> <td>Implemented (zcashd)</td>
    <tr> <td>213</td> <td class="left"><a href="zip-0213.rst">Shielded Coinbase</a></td> <td>Final</td>
    <tr> <td>214</td> <td class="left"><a href="zip-0214.rst">Consensus rules for a Zcash Development Fund</a></td> <td>Implemented (zcashd)</td>
    <tr> <td>215</td> <td class="left"><a href="zip-0215.rst">Explicitly Defining and Modifying Ed25519 Validation Rules</a></td> <td>Implemented (zcashd)</td>
    <tr> <td>216</td> <td class="left"><a href="zip-0216.rst">Require Canonical Jubjub Point Encodings</a></td> <td>Proposed</td>
    <tr> <td><span class="reserved">217</span></td> <td class="left"><a class="reserved" href="zip-0217.rst">Aggregate Signatures</a></td> <td>Reserved</td>
    <tr> <td><span class="reserved">218</span></td> <td class="left"><a class="reserved" href="zip-0218.rst">User-Defined Assets and Wrapped Assets</a></td> <td>Reserved</td>
    <tr> <td><span class="reserved">219</span></td> <td class="left"><a class="reserved" href="zip-0219.rst">Disabling Addition of New Value to the Sapling Chain Value Pool</a></td> <td>Reserved</td>
    <tr> <td>221</td> <td class="left"><a href="zip-0221.rst">FlyClient - Consensus-Layer Changes</a></td> <td>Final</td>
    <tr> <td>222</td> <td class="left"><a href="zip-0222.rst">Transparent Zcash Extensions</a></td> <td>Draft</td>
    <tr> <td><span class="reserved">224</span></td> <td class="left"><a class="reserved" href="zip-0224.rst">Orchard Shielded Protocol</a></td> <td>Reserved</td>
    <tr> <td>225</td> <td class="left"><a href="zip-0225.rst">Version 5 Transaction Format</a></td> <td>Proposed</td>
    <tr> <td>243</td> <td class="left"><a href="zip-0243.rst">Transaction Signature Validation for Sapling</a></td> <td>Final</td>
    <tr> <td>244</td> <td class="left"><a href="zip-0244.rst">Transaction Identifier Non-Malleability</a></td> <td>Proposed</td>
    <tr> <td>245</td> <td class="left"><a href="zip-0245.rst">Transaction Identifier Digests & Signature Validation for Transparent Zcash Extensions</a></td> <td>Draft</td>
    <tr> <td>250</td> <td class="left"><a href="zip-0250.rst">Deployment of the Heartwood Network Upgrade</a></td> <td>Final</td>
    <tr> <td>251</td> <td class="left"><a href="zip-0251.rst">Deployment of the Canopy Network Upgrade</a></td> <td>Implemented (zcashd)</td>
    <tr> <td><span class="reserved">252</span></td> <td class="left"><a class="reserved" href="zip-0252.rst">Deployment of the NU5 Network Upgrade</a></td> <td>Reserved</td>
    <tr> <td>300</td> <td class="left"><a href="zip-0300.rst">Cross-chain Atomic Transactions</a></td> <td>Proposed</td>
    <tr> <td>301</td> <td class="left"><a href="zip-0301.rst">Zcash Stratum Protocol</a></td> <td>Final</td>
    <tr> <td><span class="reserved">302</span></td> <td class="left"><a class="reserved" href="zip-0302.rst">Standardized Memo Field Format</a></td> <td>Reserved</td>
    <tr> <td><span class="reserved">303</span></td> <td class="left"><a class="reserved" href="zip-0303.rst">Sprout Payment Disclosure</a></td> <td>Reserved</td>
    <tr> <td>304</td> <td class="left"><a href="zip-0304.rst">Sapling Address Signatures</a></td> <td>Draft</td>
    <tr> <td><span class="reserved">305</span></td> <td class="left"><a class="reserved" href="zip-0305.rst">Best Practices for Hardware Wallets supporting Sapling</a></td> <td>Reserved</td>
    <tr> <td><span class="reserved">306</span></td> <td class="left"><a class="reserved" href="zip-0306.rst">Security Considerations for Anchor Selection</a></td> <td>Reserved</td>
    <tr> <td>307</td> <td class="left"><a href="zip-0307.rst">Light Client Protocol for Payment Detection</a></td> <td>Draft</td>
    <tr> <td>308</td> <td class="left"><a href="zip-0308.rst">Sprout to Sapling Migration</a></td> <td>Final</td>
    <tr> <td><span class="reserved">309</span></td> <td class="left"><a class="reserved" href="zip-0309.rst">Blind Off-chain Lightweight Transactions (BOLT)</a></td> <td>Reserved</td>
    <tr> <td>310</td> <td class="left"><a href="zip-0310.rst">Security Properties of Sapling Viewing Keys</a></td> <td>Draft</td>
    <tr> <td><span class="reserved">311</span></td> <td class="left"><a class="reserved" href="zip-0311.rst">Sapling Payment Disclosure</a></td> <td>Reserved</td>
    <tr> <td><span class="reserved">312</span></td> <td class="left"><a class="reserved" href="zip-0312.rst">Shielded Multisignatures using FROST</a></td> <td>Reserved</td>
    <tr> <td>313</td> <td class="left"><a href="zip-0313.rst">Reduce Conventional Transaction Fee to 1000 zatoshis</a></td> <td>Active</td>
    <tr> <td>321</td> <td class="left"><a href="zip-0321.rst">Payment Request URIs</a></td> <td>Proposed</td>
    <tr> <td><span class="reserved">339</span></td> <td class="left"><a class="reserved" href="zip-0339.rst">Wallet Recovery Words</a></td> <td>Reserved</td>
    <tr> <td>400</td> <td class="left"><a href="zip-0400.rst">Wallet.dat format</a></td> <td>Draft</td>
    <tr> <td>401</td> <td class="left"><a href="zip-0401.rst">Addressing mempool denial-of-service</a></td> <td>Final</td>
    <tr> <td><span class="reserved">402</span></td> <td class="left"><a class="reserved" href="zip-0402.rst">New Wallet Database Format</a></td> <td>Reserved</td>
    <tr> <td><span class="reserved">403</span></td> <td class="left"><a class="reserved" href="zip-0403.rst">Verification Behaviour of zcashd</a></td> <td>Reserved</td>
    <tr> <td><strike>1001</strike></td> <td class="left"><strike><a href="zip-1001.rst">Keep the Block Distribution as Initially Defined — 90% to Miners</a></strike></td> <td>Obsolete</td>
    <tr> <td><strike>1002</strike></td> <td class="left"><strike><a href="zip-1002.rst">Opt-in Donation Feature</a></strike></td> <td>Obsolete</td>
    <tr> <td><strike>1003</strike></td> <td class="left"><strike><a href="zip-1003.rst">20% Split Evenly Between the ECC and the Zcash Foundation, and a Voting System Mandate</a></strike></td> <td>Obsolete</td>
    <tr> <td><strike>1004</strike></td> <td class="left"><strike><a href="zip-1004.rst">Miner-Directed Dev Fund</a></strike></td> <td>Obsolete</td>
    <tr> <td><strike>1005</strike></td> <td class="left"><strike><a href="zip-1005.rst">Zcash Community Funding System</a></strike></td> <td>Obsolete</td>
    <tr> <td><strike>1006</strike></td> <td class="left"><strike><a href="zip-1006.rst">Development Fund of 10% to a 2-of-3 Multisig with Community-Involved Third Entity</a></strike></td> <td>Obsolete</td>
    <tr> <td><strike>1007</strike></td> <td class="left"><strike><a href="zip-1007.rst">Enforce Development Fund Commitments with a Legal Charter</a></strike></td> <td>Obsolete</td>
    <tr> <td><strike>1008</strike></td> <td class="left"><strike><a href="zip-1008.rst">Fund ECC for Two More Years</a></strike></td> <td>Obsolete</td>
    <tr> <td><strike>1009</strike></td> <td class="left"><strike><a href="zip-1009.rst">Five-Entity Strategic Council</a></strike></td> <td>Obsolete</td>
    <tr> <td><strike>1010</strike></td> <td class="left"><strike><a href="zip-1010.rst">Compromise Dev Fund Proposal With Diverse Funding Streams</a></strike></td> <td>Obsolete</td>
    <tr> <td><strike>1011</strike></td> <td class="left"><strike><a href="zip-1011.rst">Decentralize the Dev Fee</a></strike></td> <td>Obsolete</td>
    <tr> <td><strike>1012</strike></td> <td class="left"><strike><a href="zip-1012.rst">Dev Fund to ECC + ZF + Major Grants</a></strike></td> <td>Obsolete</td>
    <tr> <td><strike>1013</strike></td> <td class="left"><strike><a href="zip-1013.rst">Keep It Simple, Zcashers: 10% to ECC, 10% to ZF</a></strike></td> <td>Obsolete</td>
    <tr> <td>1014</td> <td class="left"><a href="zip-1014.rst">Establishing a Dev Fund for ECC, ZF, and Major Grants</a></td> <td>Active</td>
    <tr> <td>guide</td> <td class="left"><a href="zip-guide.rst">{Something Short and To the Point}</a></td> <td>Draft</td>
  </table></embed>
