.. Title: Specifications and Zcash Improvement Proposals


What are ZIPs?
--------------

Zcash Improvement Proposals (ZIPs) are the way to:

* propose new features for the `Zcash cryptocurrency <https://z.cash/>`__ and their rationale,
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

The Zcash protocol is documented in its
`Protocol Specification <rendered/protocol/protocol.pdf>`__
`(dark mode version) <rendered/protocol/protocol-dark.pdf>`__.

To start contributing, first read `ZIP 0 <zips/zip-0000.rst>`__ which documents the ZIP process.
Then clone `this repo <https://github.com/zcash/zips>`__ from GitHub, and start adding
your draft ZIP, formatted either as reStructuredText or as Markdown, into the `zips/` directory.

For example, if using reStructuredText, use a filename matching ``zips/draft-*.rst``.
Use ``make`` to check that you are using correct
`reStructuredText <https://docutils.sourceforge.io/rst.html>`__ or
`Markdown <https://pandoc.org/MANUAL.html#pandocs-markdown>`__ syntax,
and double-check the generated ``rendered/draft-*.html`` file before filing a Pull Request.
See `here <protocol/README.rst>`__ for the project dependencies.


NU7 Candidate ZIPs
------------------

The following ZIPs are under consideration for inclusion in NU7:

- `ZIP 226: Transfer and Burn of Zcash Shielded Assets <zip-0226.rst>`__
- `ZIP 227: Issuance of Zcash Shielded Assets <zip-0227.rst>`__
- `ZIP 230: Version 6 Transaction Format <zip-0230.rst>`__
- `ZIP 231: Memo Bundles <zip-0231.rst>`__
- `ZIP 233: Network Sustainability Mechanism: Burning <zip-0233.rst>`__
- `ZIP 234: Network Sustainability Mechanism: Issuance Smoothing <zip-0234.rst>`__
- `ZIP 235: Network Sustainability Mechanism: Burn 60% of Transaction Fees <zip-0235.rst>`__
- `ZIP 2002: Explicit Fees <zip-2002.rst>`__
- `ZIP 2003: Disallow version 4 transactions <zip-2003.rst>`__
- `ZIP 2004: Remove the dependency of consensus on note encryption <zip-2004.rst>`__

In addition, `ZIP 317: Proportional Transfer Fee Mechanism <zip-0317.rst>`__
may be updated.

This list is only provided here for easy reference; no decision has been made
on whether to include each of these ZIPs.

`ZIP 254: Deployment of the NU7 Network Upgrade <zip-0254.rst>`__ will define
which ZIPs are included in NU7.


License
-------

Unless otherwise stated in this repository’s individual files, the
contents of this repository are released under the terms of the MIT
license. See `COPYING <COPYING.rst>`__ for more information or see
https://opensource.org/licenses/MIT .

Released ZIPs
-------------

.. raw:: html

  <embed><table>
    <tr> <th>ZIP</th> <th>Title</th> <th>Status</th> </tr>
    <tr> <td>0</td> <td class="left"><a href="zips/zip-0000.rst">ZIP Process</a></td> <td>Active</td>
    <tr> <td>32</td> <td class="left"><a href="zips/zip-0032.rst">Shielded Hierarchical Deterministic Wallets</a></td> <td>Final</td>
    <tr> <td>143</td> <td class="left"><a href="zips/zip-0143.rst">Transaction Signature Validation for Overwinter</a></td> <td>Final</td>
    <tr> <td>155</td> <td class="left"><a href="zips/zip-0155.rst">addrv2 message</a></td> <td>Proposed</td>
    <tr> <td>173</td> <td class="left"><a href="zips/zip-0173.rst">Bech32 Format</a></td> <td>Final</td>
    <tr> <td>200</td> <td class="left"><a href="zips/zip-0200.rst">Network Upgrade Mechanism</a></td> <td>Final</td>
    <tr> <td>201</td> <td class="left"><a href="zips/zip-0201.rst">Network Peer Management for Overwinter</a></td> <td>Final</td>
    <tr> <td>202</td> <td class="left"><a href="zips/zip-0202.rst">Version 3 Transaction Format for Overwinter</a></td> <td>Final</td>
    <tr> <td>203</td> <td class="left"><a href="zips/zip-0203.rst">Transaction Expiry</a></td> <td>Final</td>
    <tr> <td>205</td> <td class="left"><a href="zips/zip-0205.rst">Deployment of the Sapling Network Upgrade</a></td> <td>Final</td>
    <tr> <td>206</td> <td class="left"><a href="zips/zip-0206.rst">Deployment of the Blossom Network Upgrade</a></td> <td>Final</td>
    <tr> <td>207</td> <td class="left"><a href="zips/zip-0207.rst">Funding Streams</a></td> <td>[Pre-NU6] Final, [NU6] Implemented (zcashd and zebrad)</td>
    <tr> <td>208</td> <td class="left"><a href="zips/zip-0208.rst">Shorter Block Target Spacing</a></td> <td>Final</td>
    <tr> <td>209</td> <td class="left"><a href="zips/zip-0209.rst">Prohibit Negative Shielded Chain Value Pool Balances</a></td> <td>Final</td>
    <tr> <td>211</td> <td class="left"><a href="zips/zip-0211.rst">Disabling Addition of New Value to the Sprout Chain Value Pool</a></td> <td>Final</td>
    <tr> <td>212</td> <td class="left"><a href="zips/zip-0212.rst">Allow Recipient to Derive Ephemeral Secret from Note Plaintext</a></td> <td>Final</td>
    <tr> <td>213</td> <td class="left"><a href="zips/zip-0213.rst">Shielded Coinbase</a></td> <td>Final</td>
    <tr> <td>214</td> <td class="left"><a href="zips/zip-0214.rst">Consensus rules for a Zcash Development Fund</a></td> <td>[Revision 0] Final, [Revision 1] Implemented (zcashd and zebrad)</td>
    <tr> <td>215</td> <td class="left"><a href="zips/zip-0215.rst">Explicitly Defining and Modifying Ed25519 Validation Rules</a></td> <td>Final</td>
    <tr> <td>216</td> <td class="left"><a href="zips/zip-0216.rst">Require Canonical Jubjub Point Encodings</a></td> <td>Final</td>
    <tr> <td>221</td> <td class="left"><a href="zips/zip-0221.rst">FlyClient - Consensus-Layer Changes</a></td> <td>Final</td>
    <tr> <td>224</td> <td class="left"><a href="zips/zip-0224.rst">Orchard Shielded Protocol</a></td> <td>Final</td>
    <tr> <td>225</td> <td class="left"><a href="zips/zip-0225.rst">Version 5 Transaction Format</a></td> <td>Final</td>
    <tr> <td>236</td> <td class="left"><a href="zips/zip-0236.rst">Blocks should balance exactly</a></td> <td>Implemented (zcashd and zebrad)</td>
    <tr> <td>239</td> <td class="left"><a href="zips/zip-0239.rst">Relay of Version 5 Transactions</a></td> <td>Final</td>
    <tr> <td>243</td> <td class="left"><a href="zips/zip-0243.rst">Transaction Signature Validation for Sapling</a></td> <td>Final</td>
    <tr> <td>244</td> <td class="left"><a href="zips/zip-0244.rst">Transaction Identifier Non-Malleability</a></td> <td>Final</td>
    <tr> <td>250</td> <td class="left"><a href="zips/zip-0250.rst">Deployment of the Heartwood Network Upgrade</a></td> <td>Final</td>
    <tr> <td>251</td> <td class="left"><a href="zips/zip-0251.rst">Deployment of the Canopy Network Upgrade</a></td> <td>Final</td>
    <tr> <td>252</td> <td class="left"><a href="zips/zip-0252.rst">Deployment of the NU5 Network Upgrade</a></td> <td>Final</td>
    <tr> <td>253</td> <td class="left"><a href="zips/zip-0253.md">Deployment of the NU6 Network Upgrade</a></td> <td>Implemented (zcashd and zebrad)</td>
    <tr> <td>300</td> <td class="left"><a href="zips/zip-0300.rst">Cross-chain Atomic Transactions</a></td> <td>Proposed</td>
    <tr> <td>301</td> <td class="left"><a href="zips/zip-0301.rst">Zcash Stratum Protocol</a></td> <td>Final</td>
    <tr> <td>308</td> <td class="left"><a href="zips/zip-0308.rst">Sprout to Sapling Migration</a></td> <td>Final</td>
    <tr> <td>316</td> <td class="left"><a href="zips/zip-0316.rst">Unified Addresses and Unified Viewing Keys</a></td> <td>[Revision 0] Final, [Revision 1] Proposed</td>
    <tr> <td>317</td> <td class="left"><a href="zips/zip-0317.rst">Proportional Transfer Fee Mechanism</a></td> <td>Active</td>
    <tr> <td>320</td> <td class="left"><a href="zips/zip-0320.rst">Defining an Address Type to which funds can only be sent from Transparent Addresses</a></td> <td>Proposed</td>
    <tr> <td>321</td> <td class="left"><a href="zips/zip-0321.rst">Payment Request URIs</a></td> <td>Proposed</td>
    <tr> <td>401</td> <td class="left"><a href="zips/zip-0401.rst">Addressing Mempool Denial-of-Service</a></td> <td>Active</td>
    <tr> <td>1014</td> <td class="left"><a href="zips/zip-1014.rst">Establishing a Dev Fund for ECC, ZF, and Major Grants</a></td> <td>Active</td>
    <tr> <td>1015</td> <td class="left"><a href="zips/zip-1015.rst">Block Subsidy Allocation for Non-Direct Development Funding</a></td> <td>Proposed</td>
    <tr> <td>2001</td> <td class="left"><a href="zips/zip-2001.rst">Lockbox Funding Streams</a></td> <td>Implemented (zcashd and zebrad)</td>
  </table></embed>

Draft ZIPs
----------

These are works-in-progress that have been assigned ZIP numbers. These will
eventually become either Proposed (and thus Released), or one of Withdrawn,
Rejected, or Obsolete.

In some cases a ZIP number is reserved by the ZIP Editors before a draft is
written.

.. raw:: html

  <embed><table>
    <tr> <th>ZIP</th> <th>Title</th> <th>Status</th> </tr>
    <tr> <td><span class="reserved">1</span></td> <td class="left"><a class="reserved" href="zips/zip-0001.rst">Network Upgrade Policy and Scheduling</a></td> <td>Reserved</td>
    <tr> <td><span class="reserved">2</span></td> <td class="left"><a class="reserved" href="zips/zip-0002.rst">Design Considerations for Network Upgrades</a></td> <td>Reserved</td>
    <tr> <td>68</td> <td class="left"><a href="zips/zip-0068.rst">Relative lock-time using consensus-enforced sequence numbers</a></td> <td>Draft</td>
    <tr> <td><span class="reserved">76</span></td> <td class="left"><a class="reserved" href="zips/zip-0076.rst">Transaction Signature Validation before Overwinter</a></td> <td>Reserved</td>
    <tr> <td>112</td> <td class="left"><a href="zips/zip-0112.rst">CHECKSEQUENCEVERIFY</a></td> <td>Draft</td>
    <tr> <td>113</td> <td class="left"><a href="zips/zip-0113.rst">Median Time Past as endpoint for lock-time calculations</a></td> <td>Draft</td>
    <tr> <td><span class="reserved">204</span></td> <td class="left"><a class="reserved" href="zips/zip-0204.rst">Zcash P2P Network Protocol</a></td> <td>Reserved</td>
    <tr> <td><span class="reserved">217</span></td> <td class="left"><a class="reserved" href="zips/zip-0217.rst">Aggregate Signatures</a></td> <td>Reserved</td>
    <tr> <td><span class="reserved">219</span></td> <td class="left"><a class="reserved" href="zips/zip-0219.rst">Disabling Addition of New Value to the Sapling Chain Value Pool</a></td> <td>Reserved</td>
    <tr> <td>222</td> <td class="left"><a href="zips/zip-0222.rst">Transparent Zcash Extensions</a></td> <td>Draft</td>
    <tr> <td>226</td> <td class="left"><a href="zips/zip-0226.rst">Transfer and Burn of Zcash Shielded Assets</a></td> <td>Draft</td>
    <tr> <td>227</td> <td class="left"><a href="zips/zip-0227.rst">Issuance of Zcash Shielded Assets</a></td> <td>Draft</td>
    <tr> <td><span class="reserved">228</span></td> <td class="left"><a class="reserved" href="zips/zip-0228.rst">Asset Swaps for Zcash Shielded Assets</a></td> <td>Reserved</td>
    <tr> <td>230</td> <td class="left"><a href="zips/zip-0230.rst">Version 6 Transaction Format</a></td> <td>Draft</td>
    <tr> <td>231</td> <td class="left"><a href="zips/zip-0231.md">Memo Bundles</a></td> <td>Draft</td>
    <tr> <td>233</td> <td class="left"><a href="zips/zip-0233.md">Network Sustainability Mechanism: Burning</a></td> <td>Draft</td>
    <tr> <td>234</td> <td class="left"><a href="zips/zip-0234.md">Network Sustainability Mechanism: Issuance Smoothing</a></td> <td>Draft</td>
    <tr> <td>235</td> <td class="left"><a href="zips/zip-0235.md">Burn 60% of Transaction Fees</a></td> <td>Draft</td>
    <tr> <td>245</td> <td class="left"><a href="zips/zip-0245.rst">Transaction Identifier Digests & Signature Validation for Transparent Zcash Extensions</a></td> <td>Draft</td>
    <tr> <td>254</td> <td class="left"><a href="zips/zip-0254.md">Deployment of the NU7 Network Upgrade</a></td> <td>Draft</td>
    <tr> <td>302</td> <td class="left"><a href="zips/zip-0302.rst">Standardized Memo Field Format</a></td> <td>Draft</td>
    <tr> <td><span class="reserved">303</span></td> <td class="left"><a class="reserved" href="zips/zip-0303.rst">Sprout Payment Disclosure</a></td> <td>Reserved</td>
    <tr> <td>304</td> <td class="left"><a href="zips/zip-0304.rst">Sapling Address Signatures</a></td> <td>Draft</td>
    <tr> <td><span class="reserved">305</span></td> <td class="left"><a class="reserved" href="zips/zip-0305.rst">Best Practices for Hardware Wallets supporting Sapling</a></td> <td>Reserved</td>
    <tr> <td><span class="reserved">306</span></td> <td class="left"><a class="reserved" href="zips/zip-0306.rst">Security Considerations for Anchor Selection</a></td> <td>Reserved</td>
    <tr> <td>307</td> <td class="left"><a href="zips/zip-0307.rst">Light Client Protocol for Payment Detection</a></td> <td>Draft</td>
    <tr> <td><span class="reserved">309</span></td> <td class="left"><a class="reserved" href="zips/zip-0309.rst">Blind Off-chain Lightweight Transactions (BOLT)</a></td> <td>Reserved</td>
    <tr> <td>310</td> <td class="left"><a href="zips/zip-0310.rst">Security Properties of Sapling Viewing Keys</a></td> <td>Draft</td>
    <tr> <td>311</td> <td class="left"><a href="zips/zip-0311.rst">Zcash Payment Disclosures</a></td> <td>Draft</td>
    <tr> <td>312</td> <td class="left"><a href="zips/zip-0312.rst">FROST for Spend Authorization Multisignatures</a></td> <td>Draft</td>
    <tr> <td><span class="reserved">314</span></td> <td class="left"><a class="reserved" href="zips/zip-0314.rst">Privacy upgrades to the Zcash light client protocol</a></td> <td>Reserved</td>
    <tr> <td>315</td> <td class="left"><a href="zips/zip-0315.rst">Best Practices for Wallet Implementations</a></td> <td>Draft</td>
    <tr> <td><span class="reserved">318</span></td> <td class="left"><a class="reserved" href="zips/zip-0318.rst">Associated Payload Encryption</a></td> <td>Reserved</td>
    <tr> <td><span class="reserved">319</span></td> <td class="left"><a class="reserved" href="zips/zip-0319.rst">Options for Shielded Pool Retirement</a></td> <td>Reserved</td>
    <tr> <td><span class="reserved">322</span></td> <td class="left"><a class="reserved" href="zips/zip-0322.rst">Generic Signed Message Format</a></td> <td>Reserved</td>
    <tr> <td><span class="reserved">323</span></td> <td class="left"><a class="reserved" href="zips/zip-0323.rst">Specification of getblocktemplate for Zcash</a></td> <td>Reserved</td>
    <tr> <td>324</td> <td class="left"><a href="zips/zip-0324.rst">URI-Encapsulated Payments</a></td> <td>Draft</td>
    <tr> <td><span class="reserved">332</span></td> <td class="left"><a class="reserved" href="zips/zip-0332.rst">Wallet Recovery from zcashd HD Seeds</a></td> <td>Reserved</td>
    <tr> <td><span class="reserved">339</span></td> <td class="left"><a class="reserved" href="zips/zip-0339.rst">Wallet Recovery Words</a></td> <td>Reserved</td>
    <tr> <td>400</td> <td class="left"><a href="zips/zip-0400.rst">Wallet.dat format</a></td> <td>Draft</td>
    <tr> <td><span class="reserved">402</span></td> <td class="left"><a class="reserved" href="zips/zip-0402.rst">New Wallet Database Format</a></td> <td>Reserved</td>
    <tr> <td><span class="reserved">403</span></td> <td class="left"><a class="reserved" href="zips/zip-0403.rst">Verification Behaviour of zcashd</a></td> <td>Reserved</td>
    <tr> <td><span class="reserved">416</span></td> <td class="left"><a class="reserved" href="zips/zip-0416.rst">Support for Unified Addresses in zcashd</a></td> <td>Reserved</td>
    <tr> <td>2002</td> <td class="left"><a href="zips/zip-2002.rst">Explicit Fees</a></td> <td>Draft</td>
    <tr> <td>2003</td> <td class="left"><a href="zips/zip-2003.rst">Disallow version 4 transactions</a></td> <td>Draft</td>
    <tr> <td>2004</td> <td class="left"><a href="zips/zip-2004.rst">Remove the dependency of consensus on note encryption</a></td> <td>Draft</td>
    <tr> <td>guide-markdown</td> <td class="left"><a href="zips/zip-guide-markdown.md">{Something Short and To the Point}</a></td> <td>Draft</td>
    <tr> <td>guide</td> <td class="left"><a href="zips/zip-guide.rst">{Something Short and To the Point}</a></td> <td>Draft</td>
  </table></embed>

Drafts without assigned ZIP numbers
-----------------------------------

These are works-in-progress, and may never be assigned ZIP numbers if their
ideas become obsoleted or abandoned. Do not assume that these drafts will exist
in perpetuity; instead assume that they will either move to a numbered ZIP, or
be deleted.

.. raw:: html

  <embed><table>
    <tr> <th>Title</th> </tr>
    <tr> <td class="left"><a href="zips/draft-noamchom67-manufacturing-consent.rst">Manufacturing Consent; Re-Establishing a Dev Fund for ECC, ZF, ZCG, Qedit, FPF, and ZecHub</a></td>
    <tr> <td class="left"><a href="zips/draft-nuttycom-funding-allocation.rst">Block Reward Allocation for Non-Direct Development Funding</a></td>
    <tr> <td class="left"><a href="zips/draft-zf-community-dev-fund-2-proposal.rst">Establishing a Hybrid Dev Fund for ZF, ZCG and a Dev Fund Reserve</a></td>
  </table></embed>

Withdrawn, Rejected, or Obsolete ZIPs
-------------------------------------

.. raw:: html

  <details>
  <summary>Click to show/hide</summary>
  <embed><table>
    <tr> <th>ZIP</th> <th>Title</th> <th>Status</th> </tr>
    <tr> <td><strike>210</strike></td> <td class="left"><strike><a href="zips/zip-0210.rst">Sapling Anchor Deduplication within Transactions</a></strike></td> <td>Withdrawn</td>
    <tr> <td><strike>220</strike></td> <td class="left"><strike><a href="zips/zip-0220.rst">Zcash Shielded Assets</a></strike></td> <td>Withdrawn</td>
    <tr> <td><strike>313</strike></td> <td class="left"><strike><a href="zips/zip-0313.rst">Reduce Conventional Transaction Fee to 1000 zatoshis</a></strike></td> <td>Obsolete</td>
    <tr> <td><strike>1001</strike></td> <td class="left"><strike><a href="zips/zip-1001.rst">Keep the Block Distribution as Initially Defined — 90% to Miners</a></strike></td> <td>Obsolete</td>
    <tr> <td><strike>1002</strike></td> <td class="left"><strike><a href="zips/zip-1002.rst">Opt-in Donation Feature</a></strike></td> <td>Obsolete</td>
    <tr> <td><strike>1003</strike></td> <td class="left"><strike><a href="zips/zip-1003.rst">20% Split Evenly Between the ECC and the Zcash Foundation, and a Voting System Mandate</a></strike></td> <td>Obsolete</td>
    <tr> <td><strike>1004</strike></td> <td class="left"><strike><a href="zips/zip-1004.rst">Miner-Directed Dev Fund</a></strike></td> <td>Obsolete</td>
    <tr> <td><strike>1005</strike></td> <td class="left"><strike><a href="zips/zip-1005.rst">Zcash Community Funding System</a></strike></td> <td>Obsolete</td>
    <tr> <td><strike>1006</strike></td> <td class="left"><strike><a href="zips/zip-1006.rst">Development Fund of 10% to a 2-of-3 Multisig with Community-Involved Third Entity</a></strike></td> <td>Obsolete</td>
    <tr> <td><strike>1007</strike></td> <td class="left"><strike><a href="zips/zip-1007.rst">Enforce Development Fund Commitments with a Legal Charter</a></strike></td> <td>Obsolete</td>
    <tr> <td><strike>1008</strike></td> <td class="left"><strike><a href="zips/zip-1008.rst">Fund ECC for Two More Years</a></strike></td> <td>Obsolete</td>
    <tr> <td><strike>1009</strike></td> <td class="left"><strike><a href="zips/zip-1009.rst">Five-Entity Strategic Council</a></strike></td> <td>Obsolete</td>
    <tr> <td><strike>1010</strike></td> <td class="left"><strike><a href="zips/zip-1010.rst">Compromise Dev Fund Proposal With Diverse Funding Streams</a></strike></td> <td>Obsolete</td>
    <tr> <td><strike>1011</strike></td> <td class="left"><strike><a href="zips/zip-1011.rst">Decentralize the Dev Fee</a></strike></td> <td>Obsolete</td>
    <tr> <td><strike>1012</strike></td> <td class="left"><strike><a href="zips/zip-1012.rst">Dev Fund to ECC + ZF + Major Grants</a></strike></td> <td>Obsolete</td>
    <tr> <td><strike>1013</strike></td> <td class="left"><strike><a href="zips/zip-1013.rst">Keep It Simple, Zcashers: 10% to ECC, 10% to ZF</a></strike></td> <td>Obsolete</td>
  </table></embed>
  </details>

Index of ZIPs
-------------

.. raw:: html

  <embed><table>
    <tr> <th>ZIP</th> <th>Title</th> <th>Status</th> </tr>
    <tr> <td>0</td> <td class="left"><a href="zips/zip-0000.rst">ZIP Process</a></td> <td>Active</td>
    <tr> <td><span class="reserved">1</span></td> <td class="left"><a class="reserved" href="zips/zip-0001.rst">Network Upgrade Policy and Scheduling</a></td> <td>Reserved</td>
    <tr> <td><span class="reserved">2</span></td> <td class="left"><a class="reserved" href="zips/zip-0002.rst">Design Considerations for Network Upgrades</a></td> <td>Reserved</td>
    <tr> <td>32</td> <td class="left"><a href="zips/zip-0032.rst">Shielded Hierarchical Deterministic Wallets</a></td> <td>Final</td>
    <tr> <td>68</td> <td class="left"><a href="zips/zip-0068.rst">Relative lock-time using consensus-enforced sequence numbers</a></td> <td>Draft</td>
    <tr> <td><span class="reserved">76</span></td> <td class="left"><a class="reserved" href="zips/zip-0076.rst">Transaction Signature Validation before Overwinter</a></td> <td>Reserved</td>
    <tr> <td>112</td> <td class="left"><a href="zips/zip-0112.rst">CHECKSEQUENCEVERIFY</a></td> <td>Draft</td>
    <tr> <td>113</td> <td class="left"><a href="zips/zip-0113.rst">Median Time Past as endpoint for lock-time calculations</a></td> <td>Draft</td>
    <tr> <td>143</td> <td class="left"><a href="zips/zip-0143.rst">Transaction Signature Validation for Overwinter</a></td> <td>Final</td>
    <tr> <td>155</td> <td class="left"><a href="zips/zip-0155.rst">addrv2 message</a></td> <td>Proposed</td>
    <tr> <td>173</td> <td class="left"><a href="zips/zip-0173.rst">Bech32 Format</a></td> <td>Final</td>
    <tr> <td>200</td> <td class="left"><a href="zips/zip-0200.rst">Network Upgrade Mechanism</a></td> <td>Final</td>
    <tr> <td>201</td> <td class="left"><a href="zips/zip-0201.rst">Network Peer Management for Overwinter</a></td> <td>Final</td>
    <tr> <td>202</td> <td class="left"><a href="zips/zip-0202.rst">Version 3 Transaction Format for Overwinter</a></td> <td>Final</td>
    <tr> <td>203</td> <td class="left"><a href="zips/zip-0203.rst">Transaction Expiry</a></td> <td>Final</td>
    <tr> <td><span class="reserved">204</span></td> <td class="left"><a class="reserved" href="zips/zip-0204.rst">Zcash P2P Network Protocol</a></td> <td>Reserved</td>
    <tr> <td>205</td> <td class="left"><a href="zips/zip-0205.rst">Deployment of the Sapling Network Upgrade</a></td> <td>Final</td>
    <tr> <td>206</td> <td class="left"><a href="zips/zip-0206.rst">Deployment of the Blossom Network Upgrade</a></td> <td>Final</td>
    <tr> <td>207</td> <td class="left"><a href="zips/zip-0207.rst">Funding Streams</a></td> <td>[Pre-NU6] Final, [NU6] Implemented (zcashd and zebrad)</td>
    <tr> <td>208</td> <td class="left"><a href="zips/zip-0208.rst">Shorter Block Target Spacing</a></td> <td>Final</td>
    <tr> <td>209</td> <td class="left"><a href="zips/zip-0209.rst">Prohibit Negative Shielded Chain Value Pool Balances</a></td> <td>Final</td>
    <tr> <td><strike>210</strike></td> <td class="left"><strike><a href="zips/zip-0210.rst">Sapling Anchor Deduplication within Transactions</a></strike></td> <td>Withdrawn</td>
    <tr> <td>211</td> <td class="left"><a href="zips/zip-0211.rst">Disabling Addition of New Value to the Sprout Chain Value Pool</a></td> <td>Final</td>
    <tr> <td>212</td> <td class="left"><a href="zips/zip-0212.rst">Allow Recipient to Derive Ephemeral Secret from Note Plaintext</a></td> <td>Final</td>
    <tr> <td>213</td> <td class="left"><a href="zips/zip-0213.rst">Shielded Coinbase</a></td> <td>Final</td>
    <tr> <td>214</td> <td class="left"><a href="zips/zip-0214.rst">Consensus rules for a Zcash Development Fund</a></td> <td>[Revision 0] Final, [Revision 1] Implemented (zcashd and zebrad)</td>
    <tr> <td>215</td> <td class="left"><a href="zips/zip-0215.rst">Explicitly Defining and Modifying Ed25519 Validation Rules</a></td> <td>Final</td>
    <tr> <td>216</td> <td class="left"><a href="zips/zip-0216.rst">Require Canonical Jubjub Point Encodings</a></td> <td>Final</td>
    <tr> <td><span class="reserved">217</span></td> <td class="left"><a class="reserved" href="zips/zip-0217.rst">Aggregate Signatures</a></td> <td>Reserved</td>
    <tr> <td><span class="reserved">219</span></td> <td class="left"><a class="reserved" href="zips/zip-0219.rst">Disabling Addition of New Value to the Sapling Chain Value Pool</a></td> <td>Reserved</td>
    <tr> <td><strike>220</strike></td> <td class="left"><strike><a href="zips/zip-0220.rst">Zcash Shielded Assets</a></strike></td> <td>Withdrawn</td>
    <tr> <td>221</td> <td class="left"><a href="zips/zip-0221.rst">FlyClient - Consensus-Layer Changes</a></td> <td>Final</td>
    <tr> <td>222</td> <td class="left"><a href="zips/zip-0222.rst">Transparent Zcash Extensions</a></td> <td>Draft</td>
    <tr> <td>224</td> <td class="left"><a href="zips/zip-0224.rst">Orchard Shielded Protocol</a></td> <td>Final</td>
    <tr> <td>225</td> <td class="left"><a href="zips/zip-0225.rst">Version 5 Transaction Format</a></td> <td>Final</td>
    <tr> <td>226</td> <td class="left"><a href="zips/zip-0226.rst">Transfer and Burn of Zcash Shielded Assets</a></td> <td>Draft</td>
    <tr> <td>227</td> <td class="left"><a href="zips/zip-0227.rst">Issuance of Zcash Shielded Assets</a></td> <td>Draft</td>
    <tr> <td><span class="reserved">228</span></td> <td class="left"><a class="reserved" href="zips/zip-0228.rst">Asset Swaps for Zcash Shielded Assets</a></td> <td>Reserved</td>
    <tr> <td>230</td> <td class="left"><a href="zips/zip-0230.rst">Version 6 Transaction Format</a></td> <td>Draft</td>
    <tr> <td>231</td> <td class="left"><a href="zips/zip-0231.md">Memo Bundles</a></td> <td>Draft</td>
    <tr> <td>233</td> <td class="left"><a href="zips/zip-0233.md">Network Sustainability Mechanism: Burning</a></td> <td>Draft</td>
    <tr> <td>234</td> <td class="left"><a href="zips/zip-0234.md">Network Sustainability Mechanism: Issuance Smoothing</a></td> <td>Draft</td>
    <tr> <td>235</td> <td class="left"><a href="zips/zip-0235.md">Burn 60% of Transaction Fees</a></td> <td>Draft</td>
    <tr> <td>236</td> <td class="left"><a href="zips/zip-0236.rst">Blocks should balance exactly</a></td> <td>Implemented (zcashd and zebrad)</td>
    <tr> <td>239</td> <td class="left"><a href="zips/zip-0239.rst">Relay of Version 5 Transactions</a></td> <td>Final</td>
    <tr> <td>243</td> <td class="left"><a href="zips/zip-0243.rst">Transaction Signature Validation for Sapling</a></td> <td>Final</td>
    <tr> <td>244</td> <td class="left"><a href="zips/zip-0244.rst">Transaction Identifier Non-Malleability</a></td> <td>Final</td>
    <tr> <td>245</td> <td class="left"><a href="zips/zip-0245.rst">Transaction Identifier Digests & Signature Validation for Transparent Zcash Extensions</a></td> <td>Draft</td>
    <tr> <td>250</td> <td class="left"><a href="zips/zip-0250.rst">Deployment of the Heartwood Network Upgrade</a></td> <td>Final</td>
    <tr> <td>251</td> <td class="left"><a href="zips/zip-0251.rst">Deployment of the Canopy Network Upgrade</a></td> <td>Final</td>
    <tr> <td>252</td> <td class="left"><a href="zips/zip-0252.rst">Deployment of the NU5 Network Upgrade</a></td> <td>Final</td>
    <tr> <td>253</td> <td class="left"><a href="zips/zip-0253.md">Deployment of the NU6 Network Upgrade</a></td> <td>Implemented (zcashd and zebrad)</td>
    <tr> <td>254</td> <td class="left"><a href="zips/zip-0254.md">Deployment of the NU7 Network Upgrade</a></td> <td>Draft</td>
    <tr> <td>300</td> <td class="left"><a href="zips/zip-0300.rst">Cross-chain Atomic Transactions</a></td> <td>Proposed</td>
    <tr> <td>301</td> <td class="left"><a href="zips/zip-0301.rst">Zcash Stratum Protocol</a></td> <td>Final</td>
    <tr> <td>302</td> <td class="left"><a href="zips/zip-0302.rst">Standardized Memo Field Format</a></td> <td>Draft</td>
    <tr> <td><span class="reserved">303</span></td> <td class="left"><a class="reserved" href="zips/zip-0303.rst">Sprout Payment Disclosure</a></td> <td>Reserved</td>
    <tr> <td>304</td> <td class="left"><a href="zips/zip-0304.rst">Sapling Address Signatures</a></td> <td>Draft</td>
    <tr> <td><span class="reserved">305</span></td> <td class="left"><a class="reserved" href="zips/zip-0305.rst">Best Practices for Hardware Wallets supporting Sapling</a></td> <td>Reserved</td>
    <tr> <td><span class="reserved">306</span></td> <td class="left"><a class="reserved" href="zips/zip-0306.rst">Security Considerations for Anchor Selection</a></td> <td>Reserved</td>
    <tr> <td>307</td> <td class="left"><a href="zips/zip-0307.rst">Light Client Protocol for Payment Detection</a></td> <td>Draft</td>
    <tr> <td>308</td> <td class="left"><a href="zips/zip-0308.rst">Sprout to Sapling Migration</a></td> <td>Final</td>
    <tr> <td><span class="reserved">309</span></td> <td class="left"><a class="reserved" href="zips/zip-0309.rst">Blind Off-chain Lightweight Transactions (BOLT)</a></td> <td>Reserved</td>
    <tr> <td>310</td> <td class="left"><a href="zips/zip-0310.rst">Security Properties of Sapling Viewing Keys</a></td> <td>Draft</td>
    <tr> <td>311</td> <td class="left"><a href="zips/zip-0311.rst">Zcash Payment Disclosures</a></td> <td>Draft</td>
    <tr> <td>312</td> <td class="left"><a href="zips/zip-0312.rst">FROST for Spend Authorization Multisignatures</a></td> <td>Draft</td>
    <tr> <td><strike>313</strike></td> <td class="left"><strike><a href="zips/zip-0313.rst">Reduce Conventional Transaction Fee to 1000 zatoshis</a></strike></td> <td>Obsolete</td>
    <tr> <td><span class="reserved">314</span></td> <td class="left"><a class="reserved" href="zips/zip-0314.rst">Privacy upgrades to the Zcash light client protocol</a></td> <td>Reserved</td>
    <tr> <td>315</td> <td class="left"><a href="zips/zip-0315.rst">Best Practices for Wallet Implementations</a></td> <td>Draft</td>
    <tr> <td>316</td> <td class="left"><a href="zips/zip-0316.rst">Unified Addresses and Unified Viewing Keys</a></td> <td>[Revision 0] Final, [Revision 1] Proposed</td>
    <tr> <td>317</td> <td class="left"><a href="zips/zip-0317.rst">Proportional Transfer Fee Mechanism</a></td> <td>Active</td>
    <tr> <td><span class="reserved">318</span></td> <td class="left"><a class="reserved" href="zips/zip-0318.rst">Associated Payload Encryption</a></td> <td>Reserved</td>
    <tr> <td><span class="reserved">319</span></td> <td class="left"><a class="reserved" href="zips/zip-0319.rst">Options for Shielded Pool Retirement</a></td> <td>Reserved</td>
    <tr> <td>320</td> <td class="left"><a href="zips/zip-0320.rst">Defining an Address Type to which funds can only be sent from Transparent Addresses</a></td> <td>Proposed</td>
    <tr> <td>321</td> <td class="left"><a href="zips/zip-0321.rst">Payment Request URIs</a></td> <td>Proposed</td>
    <tr> <td><span class="reserved">322</span></td> <td class="left"><a class="reserved" href="zips/zip-0322.rst">Generic Signed Message Format</a></td> <td>Reserved</td>
    <tr> <td><span class="reserved">323</span></td> <td class="left"><a class="reserved" href="zips/zip-0323.rst">Specification of getblocktemplate for Zcash</a></td> <td>Reserved</td>
    <tr> <td>324</td> <td class="left"><a href="zips/zip-0324.rst">URI-Encapsulated Payments</a></td> <td>Draft</td>
    <tr> <td><span class="reserved">332</span></td> <td class="left"><a class="reserved" href="zips/zip-0332.rst">Wallet Recovery from zcashd HD Seeds</a></td> <td>Reserved</td>
    <tr> <td><span class="reserved">339</span></td> <td class="left"><a class="reserved" href="zips/zip-0339.rst">Wallet Recovery Words</a></td> <td>Reserved</td>
    <tr> <td>400</td> <td class="left"><a href="zips/zip-0400.rst">Wallet.dat format</a></td> <td>Draft</td>
    <tr> <td>401</td> <td class="left"><a href="zips/zip-0401.rst">Addressing Mempool Denial-of-Service</a></td> <td>Active</td>
    <tr> <td><span class="reserved">402</span></td> <td class="left"><a class="reserved" href="zips/zip-0402.rst">New Wallet Database Format</a></td> <td>Reserved</td>
    <tr> <td><span class="reserved">403</span></td> <td class="left"><a class="reserved" href="zips/zip-0403.rst">Verification Behaviour of zcashd</a></td> <td>Reserved</td>
    <tr> <td><span class="reserved">416</span></td> <td class="left"><a class="reserved" href="zips/zip-0416.rst">Support for Unified Addresses in zcashd</a></td> <td>Reserved</td>
    <tr> <td><strike>1001</strike></td> <td class="left"><strike><a href="zips/zip-1001.rst">Keep the Block Distribution as Initially Defined — 90% to Miners</a></strike></td> <td>Obsolete</td>
    <tr> <td><strike>1002</strike></td> <td class="left"><strike><a href="zips/zip-1002.rst">Opt-in Donation Feature</a></strike></td> <td>Obsolete</td>
    <tr> <td><strike>1003</strike></td> <td class="left"><strike><a href="zips/zip-1003.rst">20% Split Evenly Between the ECC and the Zcash Foundation, and a Voting System Mandate</a></strike></td> <td>Obsolete</td>
    <tr> <td><strike>1004</strike></td> <td class="left"><strike><a href="zips/zip-1004.rst">Miner-Directed Dev Fund</a></strike></td> <td>Obsolete</td>
    <tr> <td><strike>1005</strike></td> <td class="left"><strike><a href="zips/zip-1005.rst">Zcash Community Funding System</a></strike></td> <td>Obsolete</td>
    <tr> <td><strike>1006</strike></td> <td class="left"><strike><a href="zips/zip-1006.rst">Development Fund of 10% to a 2-of-3 Multisig with Community-Involved Third Entity</a></strike></td> <td>Obsolete</td>
    <tr> <td><strike>1007</strike></td> <td class="left"><strike><a href="zips/zip-1007.rst">Enforce Development Fund Commitments with a Legal Charter</a></strike></td> <td>Obsolete</td>
    <tr> <td><strike>1008</strike></td> <td class="left"><strike><a href="zips/zip-1008.rst">Fund ECC for Two More Years</a></strike></td> <td>Obsolete</td>
    <tr> <td><strike>1009</strike></td> <td class="left"><strike><a href="zips/zip-1009.rst">Five-Entity Strategic Council</a></strike></td> <td>Obsolete</td>
    <tr> <td><strike>1010</strike></td> <td class="left"><strike><a href="zips/zip-1010.rst">Compromise Dev Fund Proposal With Diverse Funding Streams</a></strike></td> <td>Obsolete</td>
    <tr> <td><strike>1011</strike></td> <td class="left"><strike><a href="zips/zip-1011.rst">Decentralize the Dev Fee</a></strike></td> <td>Obsolete</td>
    <tr> <td><strike>1012</strike></td> <td class="left"><strike><a href="zips/zip-1012.rst">Dev Fund to ECC + ZF + Major Grants</a></strike></td> <td>Obsolete</td>
    <tr> <td><strike>1013</strike></td> <td class="left"><strike><a href="zips/zip-1013.rst">Keep It Simple, Zcashers: 10% to ECC, 10% to ZF</a></strike></td> <td>Obsolete</td>
    <tr> <td>1014</td> <td class="left"><a href="zips/zip-1014.rst">Establishing a Dev Fund for ECC, ZF, and Major Grants</a></td> <td>Active</td>
    <tr> <td>1015</td> <td class="left"><a href="zips/zip-1015.rst">Block Subsidy Allocation for Non-Direct Development Funding</a></td> <td>Proposed</td>
    <tr> <td>2001</td> <td class="left"><a href="zips/zip-2001.rst">Lockbox Funding Streams</a></td> <td>Implemented (zcashd and zebrad)</td>
    <tr> <td>2002</td> <td class="left"><a href="zips/zip-2002.rst">Explicit Fees</a></td> <td>Draft</td>
    <tr> <td>2003</td> <td class="left"><a href="zips/zip-2003.rst">Disallow version 4 transactions</a></td> <td>Draft</td>
    <tr> <td>2004</td> <td class="left"><a href="zips/zip-2004.rst">Remove the dependency of consensus on note encryption</a></td> <td>Draft</td>
    <tr> <td>guide-markdown</td> <td class="left"><a href="zips/zip-guide-markdown.md">{Something Short and To the Point}</a></td> <td>Draft</td>
    <tr> <td>guide</td> <td class="left"><a href="zips/zip-guide.rst">{Something Short and To the Point}</a></td> <td>Draft</td>
  </table></embed>
