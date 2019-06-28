::

  ZIP: 0221
  Title: FlyClient ZCash SPV
  Owners: 
  Ying Tong, <yingtong@ethereum.org>,
  James Prestwich, <james@summa.one>,
  Georgios Konstantopoulos, <me@gakonst.com>
  Status: Draft
  Category: Consensus
  Created: 2019-03-30
  License: MIT 

Terminology
-----------
The key words "**MUST**", "**SHOULD**", and "**MAY**" in this document are to be interpreted as described in RFC 2119. [#RFC2119]_

The terms "branch" and "network upgrade" in this document are to be interpreted as described in ZIP 200. [#zip-0200]_

*Light client*
  A client that is not a full participant in the network of Zcash peers. It can send and receive payments, but does not store or validate a copy of the blockchain.

*High probability*
  An event occurs with high probability if it occurs with probability 1-O(1/2^λ), where λ is a security parameter.

*Negligible probability*
  An event occurs with negligible probability if it occurs with probability O(1/2^λ), where λ is the security parameter.

*Merkle mountain range (MMR)*
  A Merkle mountain range (MMR) is binary hash tree that allows for efficient appends of new leaves without changing the value of existing nodes.

  
Abstract
---------
This ZIP specifies modifications to be made to the Zcash block header format to include Merkle Mountain Range (MMR) commitments. Sapling (NU2) introduced the ``hashFinalSaplingRoot`` field to Zcash headers. This ZIP replaces the ``hashFinalSaplingRoot`` commitment with ``hashChainHistoryRoot``, which is the root of an MMR that commits that commits to many features of the chain's history, including all information present in ``hashFinalSaplingRoot``.

The MMR that produces the root provides a number of benefits to light clients, and enables future specification of the FlyClient protocol [#FlyClient]_. This ZIP specifies only consensus-layer changes. It does not provide any specification about the FlyClient protocol's operation.

Background
-----------

An MMR is a Merkle tree which allows for efficient appends, proofs, and verifications. Informally, appending data to an MMR consists of creating a new leaf and then iteratively merging neighboring subtrees with the same size. This takes at most `log(n)` operations and only requires knowledge of the previous subtree roots, of which there are fewer than `log(n)`.

(example adapted from [#mimblewimble]_)
To illustrate this, consider a list of 11 leaves. We first construct the biggest perfect binary subtrees possible by joining any balanced sibling trees that are the same size. We do this starting from the left to the right, adding a parent as soon as 2 children exist. This leaves us with three subtrees ("mountains") of heights 3, 1, and 0:

.. code-block:: C

       /\
      /  \
     /\  /\   
    /\/\/\/\ /\ /

Note that the first leftmost peak is always the highest. We can number this structure in order of insertion:

.. code-block:: C

      Height

        3              14
                     /    \
                    /      \
                   /        \
                  /          \
        2        6            13
               /   \        /    \
        1     2     5      9     12     17
             / \   / \    / \   /  \   /  \   /
        0   0   1 3   4  7   8 10  11 15  16 18

and represent this numbering in a flat list:

.. code-block:: python

    Position    0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18
    Height      0  0  1  0  0  1  2  0  0  1  0  0  1  2  3  0  0  1  0

This allows us to easily jump to the right sibling of a node by adding ``2^(h+1) - 1`` to its position, and its left sibling by subtracting ``2^h``.  This allows us to efficiently find the subtree roots ("peaks") of the mountains.

Once we have the positions of the mountain peaks, we "bag" them using the following algorithm:

1. add a peak connecting the 2 left-most peaks
2. repeat 1. until we have a single peak

.. code-block:: C

      Height

        5                     20
                             /  \
        4                   19   \
                          /   \   \
                         /     \   \
                        /       \   \
        3              14        \   \
                     /    \       \   \
                    /      \       \   \
                   /        \       \   \
                  /          \       \   \
        2        6           13       \   \
               /   \       /    \      \   \
        1     2     5      9     12     17  \
             / \   / \    / \   /  \   /  \  \
        0   0   1 3   4  7   8 10  11 15  16 18

The MMR tree allow for efficient incremental set update operations (push, pop, prune). In addition, MMR update operations and Merkle proofs for recent additions to the leaf set are more efficient than other incremental Merkle tree implementations (e.g. Bitcoin's padded leafset, sparse Merkle trees, and ZCash's incremental note commitment trees). 

Motivation
----------
MMR proofs are used in the FlyClient protocol to reduce the proof size needed for light clients to verify

- the validity of a blockchain received from a full node, and
- the inclusion of a block ``B`` in that chain, and 
- certain metadata of any block or range of blocks in that chain

The protocol requires that an MMR that commits to the inclusion of all blocks since the most recent network upgrade (``B_x, ..., B_(n-1))`` is formed for each block ``B_n``. The root ``M_n`` of the MMR MUST be included in the header of ``B_n``.

(``x`` is the activation height of the most recent upgrade network upgrade)

FlyClient reduces the number of block headers needed for light client verification of a valid chain, from linear (as in the current reference protocol) to logarithmic in blockchain length. This verification is correct with high probability. It also allows creation of subtree proofs, so light clients need only check blocks later than the most recently verified block index. Following that, verification of a transaction inclusion within that block follows the usual reference protocol [#ZIP-0307]_.

A smaller proof size could enable the verification of Zcash SPV Proofs in blockchains such as Ethereum, enabling efficient cross-chain communication and pegs. It also reduces bandwidth and storage requirements for resource-limited clients like mobile or IoT devices.


Security and Privacy Considerations
------------------------------------
This ZIP imposes an additional validation cost on new blocks. While this validation cost is small, it may exacerbate any existing DoS opportunities, particularly during abnormal events like long reorgs. Fortunately, these costs are logarithmic in the number of delete and append operations. In the worst case scenario, a well-resourced attacker could maintain 2 chains of approximately equal length, and alternate which chain they extend. This would result in repeated reorgs of increasing length.

Given the performance of Blake2b, we expect this validation cost to be negligible. However, it seems prudent to benchmark potential MMR implementations during the implementation process. Should the validation cost be higher than expected, there are several potential mitigations, e.g. holding recently seen nodes in memory after a reorg.

Generally, header commitments have no impact on privacy. However, FlyClient has additional security and privacy implications. Because FlyClient is a motivating factor for this ZIP, it seems prudent to include a brief overview. A more in-depth security analysis of FlyClient should be performed before designing a FlyClient-based light client ecosystem for ZCash.

FlyClient, like all light clients, requires a connection to a light client server. That server may collect information about client requests, and may use that information to attempt to deanonymize clients. However, because FlyClient proofs are non-interactive and publicly verifiable, they could be shared among many light clients after the initial server interaction.

FlyClient proofs are probabilistic. When properly constructed, there is negligible probability that a dishonest chain commitment will be accepted by the verifier. The security analysis assumes adversary mining power is bounded by a known fraction of combined mining power of honest nodes, and cannot drop or tamper with messages between client and full nodes. It also assumes the client is connected to at least one full node and knows the genesis block. However, these security properties have not been examined closely in chain models with rapidly-adjusting difficulty.



Specification
--------------
.. image:: https://i.imgur.com/hhRyI99.png
    :alt: zcash_MMR

*Fig 1. MMR commitment scheme*

The leaves of the MMR at block ``B_n`` are hash commitments to the header data and metadata of each previous block ``B_x, ..., B_(n-1)``, where ``x`` is the block height of the most recent network upgrade. We extend the standard MMR to allow metadata to propagate upwards through the tree by either summing the metadata of both children, or inheriting the metadata of a specific child as necessary. This allows us to create efficient proofs of selected properties of a range of blocks without transmitting the entire range of blocks or headers.

Tree Node specification
~~~~~~~~~~~~~~~~~~~~~~~~

Unless otherwise noted, all hashes use BLAKE2b-256 with the personalization field set to ``'ZcashHistory' || CONSENSUS_BRANCH_ID``. ``CONSENSUS_BRANCH_ID`` is the little-endian encoding of ``BRANCH_ID`` for the epoch of the block containing the commitment. [#zip-0200]_ Which is to say, each node in the tree commits to the consensus branch that produced it.

.. image:: https://i.imgur.com/9Ct2llE.png
    :alt: zcash_MMR_hash

*Fig 2. Hashing MMR leaf nodes and internal nodes*

Each MMR node is defined as follows:

1. ``hashSubtreeCommitment``

- If the node is a leaf node, then ``hashSubtreeCommitment`` is the consensus-defined block hash for the corresponding block. 

  * This hash is encoded in internal byte order, and does NOT use the BLAKE2b-256 personalization string described above.
  * For clarity, the ``hashSubtreeCommitment`` field of leaf ``n-1`` is *precisely equal* to the ``hashPrevBlock`` field of header ``n``
  
- If the node is an internal or root node

  * Both child nodes are serialized
  * ``hashSubtreeCommitment`` is the BLAKE2b-256 hash of ``left_child || right_child``
  * For clarity, this digest uses the BLAKE2b-256 personalization string described above.
- serialized as ``char[32]``

2. ``nEarliestTimestamp``

- If the node is a leaf node

  * ``nEarliestTimestamp`` is the header's timestamp
    
- If the node is an internal or root node
    
  * ``nEarliestTimestamp`` is inherited from the left child
  
- serialized as ``nTime`` (uint32)

3. ``nLatestTimestamp``

- If the node is a leaf node

  * ``nLatestTimestamp`` is the header's timestamp
  
- If the node is an internal or root node
  * ``nLatestTimestamp`` is inherited from the right child
  
- Note that due to timestamp consensus rules, ``nLatestTimestamp`` may be smaller than ``nEarliestTimestamp`` in some subtrees. This may occur within subtrees smaller than ``PoWMedianBlockSpan`` blocks.
- serialized as ``nTime`` (uint32)
    
4. ``nEarliestTarget``

- If the node is a leaf node

  * ``nEarliestTarget`` is the header's ``nBits`` field
  
- If the node is an internal or root node
  * ``nEarliestTarget`` is inherited from the left child
  
- serialized as ``nBits`` (uint32)
    
5. ``nLatestTarget``

- If the node is a leaf node

  * ``nLatestTarget`` is the header's ``nBits`` field
  
- If the node is an internal or root node
  * ``nLatestTarget`` is inherited from the right child
  
- serialized as ``nBits`` (uint32)
    
6. ``hashEarliestSaplingRoot``

- If the node is a leaf node

  * ``hashEarliestSaplingRoot`` is calculated as ``hashFinalSaplingRoot``, as implemented in Sapling

- If the node is an internal or root node

  * ``hashEarliestSaplingRoot`` is inherited from the left child
  
- serialized as ``char[32]``
    
7. ``hashLatestSaplingRoot``

- If the node is a leaf node

  * ``hashLatestSaplingRoot`` is calculated as ``hashFinalSaplingRoot``, as implemented in Sapling

- If the node is an internal or root node

  * ``hashLatestSaplingRoot`` is inherited from the right child

- serialized as ``char[32]``

8. ``nEarliestHeight``

- If the node is a leaf node

  * ``nEarliestHeight`` is the header's height
  
- If the node is an internal or root node
  * ``nEarliestHeight`` is inherited from the left child
  
- serialized as ``CompactSize uint``
    
9. ``nLatestHeight``

- If the node is a leaf node

  * ``nLatestHeight`` the header's height

- If the node is an internal or root node

  * ``nLatestHeight`` is inherited from the right child
  * serialized as ``CompactSize uint``

10. ``nSubTreeTotalWork``

- If the node is a leaf node

  * ``nSubTreeTotalWork`` is the protocol-defined work of the block: `floor(2 ** 256 / (toTarget(nBits) + 1))`.

- If the node is an internal or root node

  * ``nSubTreeTotalWork`` is the sum of the ``nSubTreeTotalWork`` fields of both children
  
- serialized as ``CompactSize uint``
    
11. ``nShieldedTxCount``

- If the node is a leaf node

  * ``nShieldedTxCount`` is the number of transactions in the leaf block where any of ``vJoinSplit``, ``vShieldedSpend``, or `vShieldedOutput` is non-empty

- If the node is an internal or root node

  * ``nShieldedTxCount`` is the sum of the ``nShieldedTxCount`` field of both children
  
- serialized as ``CompactSize uint``

Each node, when serialized, is between 132 and 164 bytes long. The canonical serialized representation of a node is used whenever creating child commitments for future nodes. Other than the metadata commitments, the MMR tree's construction is standard.

Once the MMR has been generated, we produce ``hashChainHistoryRoot``, which we define as the BLAKE2b-256 digest of the serialization of the root node.


Tree nodes and hashing (pseudocode)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python 

    CONSENSUS_BRANCH_ID: bytes = b''
    
    
    def H(msg: bytes) -> bytes:
        return blake2b256(msg, personalization=b'ZcashHistory' + CONSENSUS_BRANCH_ID)

    class ZcashMMRNode():
        # leaf nodes have no children
        left_child: 'Optional[ZcashMMRNode]'
        right_child: 'Optional[ZcashMMRNode]'

        # commitments
        subtree_commitment: bytes 
        start_time: int
        end_time: int
        start_target: int
        end_target: int
        start_sapling_root: bytes # left child's sapling root
        end_sapling_root: bytes # right child's sapling root
        start_height: int
        end_height: int
        subtree_total_work: int  # total difficulty accumulated within each subtree
        count_shielded_txs: int # number of shielded transactions in block

        @classmethod
        def from_block(Z, block: ZcashBlock) -> 'ZcashMMRNode':
            '''Create a leaf node from a block'''
            return Z(
                left_child=None,
                right_child=None,
                subtree_commitment=block.header_hash,
                start_time=block.timestamp,
                end_time=block.timestamp,
                start_target=block.nBits,
                end_target=block.nBits,
                start_sapling_root=block.sapling_root,
                end_sapling_root=block.sapling_root,
                start_height=block.height,
                end_height=block.height,
                subtree_total_work=calculate_work(block.nBits),
                count_shielded_txs=block_shielded_tx_count)
            
        def serialize(self) -> bytes:
            '''serializes a node'''
            return (
                self.subtree_commitment
                + serialize_uint32(self.start_time)
                + serialize_uint32(self.end_time)
                + serialize_uint32(self.start_target)
                + serialize_uint32(self.end_target)
                + start_sapling_root
                + end_sapling_root
                + serialize_compact_uint(self.start_height)
                + serialize_compact_uint(self.end_height)
                + serialize_compact_uint(self.subtree_total_work)
                + serialize_compact_uint(self.count_shielded_txs))    
    
    
    def make_parent(
            left_child: ZcashMMRNode, 
            right_child: ZcashMMRNode) -> ZcashMMRNode:
        return ZcashMMRNode(
            left_child=left_child,
            right_child=right_child,
            subtree_commitment=H(left_child.serialize() + right_child.serialize()),
            start_time=left_child.start_time,
            end_time=right_child.end_time,
            start_target=left_child.start_target,
            end_target=left_child.end_target,
            start_sapling_root=left_child.sapling_root,
            end_sapling_root=right_child.sapling_root,
            start_height=left_child.start_height,
            end_height=right_child.end_height,
            subtree_total_work=left_child.subtree_total_work + right_child.subtree_total_work,
            count_shielded_txs=left_child.count_shield + right_child.count_shield)
    
    def make_root_commitment(root: ZcashMMRNode) -> bytes:
        '''Makes the root commitment for a blockheader'''
        return H(root.serialize())

Incremental push and pop (pseudocode)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

With each new block ``B_n``, we append a new MMR leaf node corresponding to block ``B_(n-1)``. The ``append`` operation is detailed below in pseudocode (adapted from [#FlyClient]_):

.. code-block:: python

    def append(root: ZcashMMRNode, leaf: ZcashMMRNode) -> ZcashMMRNode:
        '''Recursive function to append a new leaf node to an existing MMR'''
    
        # find the number of leaves in the subtree
        n_leaves = root.latest_height - root.earliest_height + 1
        
        # if the subtree under this root has power of 2 no. of leaves
        # then we append the leaf to the current root
        if !(n_leaves & (n_leaves - 1)):
            new_subtree_root = make_parent(root, leaf)
            return new_subtree_root
            
        # otherwise, we append the leaf to the right subtree
        # note that this recursive call will naturally merge balanced subtrees after it appends the leaf
        else:
            new_right_child = append(root.right_child, leaf);
            new_subtree_root = make_parent(root.left_child, new_right_child)
            return new_subtree_root
            
In case of a block reorg, we have to delete the latest (i.e. rightmost) MMR leaf nodes, up to the reorg length. This operation is ``O(log(k))`` where ``k`` is the number of leaves in the right subtree of the MMR root. 

.. code-block:: python

    def delete(root: ZcashMMRNode) -> ZcashMMRNode:
        '''
        Delete the rightmost leaf node from an existing MMR
        Return the new tree root
        '''
        
        n_leaves = root.latest_height - root.earliest_height + 1
        # if there were an odd number of leaves, 
        # simply replace root with left_child
        if n_leaves & 1:
            return root.left_child
        
        # otherwise, we need to re-bag the peaks.
        else:
            # first peak
            peaks = [root.left_child]

            # we do this traversing the right (unbalanced) side of the tree
            # we keep the left side (balanced subtree or leaf) of each subtree
            # until we reach a leaf
            subtree_root = root.right_child
            while subtree_root.left_child:
                peaks.push(tmp_root.left_child)
                subtree_root = tmp_root.right_child
                
        new_root = bag_peaks(peaks)
        return new_root
        
    def bag_peaks(peaks: List[ZcashMMRNode]) -> ZcashMMRNode:
        '''
        "Bag" a list of peaks, and return the final root
        '''
        root = peaks[0]
        for i in range(1, len(peaks)):
            root = make_parent(root, peaks[i])
        return root

Header modifications specification
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This ZIP introduces a new header version. It is identical to the current v4 header [#zcashBlock]_, except for the following changes:

1. The version number is changed to `5`.
2. ``hashSaplingFinalRoot`` is replaced by ``hashChainHistoryRoot``, as described above.

The new block header format is:

.. code-block:: C

    class CBlockHeader
    {
    public:
        // header
        static const size_t HEADER_SIZE=4+32+32+32+4+4+32; // excluding Equihash solution
        static const int32_t CURRENT_VERSION=5;
        int32_t nVersion;
        uint256 hashPrevBlock;
        uint256 hashMerkleRoot;
        uint256 hashChainHistoryRoot;
        uint32_t nTime;
        uint32_t nBits;
        uint256 nNonce;
        std::vector<unsigned char> nSolution;
        ...
    }


Rationale
-----------

Tree nodes
~~~~~~~~~~~

Nodes in the commitment tree are canonical and immutable. They are cheap to generate, as (with the exception of ``nShieldedTxCount`` and ``nSubTreeTotalWork``) all metadata is already generated during block construction and checked during block validation. Nodes are relatively compact in memory. Approximately 140,000 blocks have elapsed since Sapling activation. Assuming a 164 byte commitment to each of these, we would have generated approximately 23 MB of additional storage cost for the set of leaf nodes (and an additional ~23 MB for storage of intermediate nodes).

``hashSubtreeCommitment`` forms the strucuture of the commitment tree. Other metadata commitments were chosen to serve specific purposes. Variable-length commitments are placed last, so that most metadata in a node can be directly indexed. We considered using fixed-length commitments here, but opted for variable-length, in order to marginally reduce the memory requirements for managing and updating the commitment trees.

In leaf nodes, some information is repeated. We chose to do this so that leaf nodes could be treated identically to internal and root nodes for all algorithms and (de)serializers. Leaf nodes are easily identifiable, as they will show proof of work in the ``hashSubtreeCommitment`` field, and their block range (calculated as ``nLatestHeight - nEarliestHeight + 1``) will be precisely 1. For the same reason, we change the semantics of ``hashSubtreeCommitment`` in leaf nodes to commit 

Personalized BLAKE2b-256 was selected to match existing ZCash conventions. Adding the consensus branch ID to the hash personalization string ensures that valid nodes from one branch cannot be used to make false statements about parallel consensus branches. 

FlyClient Requirements and Recommendations
===============================================
These commitments enable FlyClient in the variable-difficulty model. Specifically, they allow light clients to reason about application of the difficulty adjustment algorithm over a range of blocks. They were chosen via discussion with an author of the FlyClient paper.

- ``nEarliestTimestamp``
- ``nLatestTimestamp``
- ``nEarliestTarget``
- ``nLatestTarget``
- ``nEarliestHeight``
- ``nLatestHeight``
- ``nSubTreeTotalWork``

Non-FlyClient Commitments
==========================

Additional metadata commitments were chosen primarily to improve light client security guarantees. We specified commitments where we could see an obvious security benefit, but there may be other useful metadata that we missed. We're interested in feedback and suggestions from the implementers of the current light client.

We considered adding a commitment to the nullifier vector at each block. We would appreciate comments from light client teams on the utility of this commitment, as well as the proper serialization and commitment format for the nullifier vector.

- ``hashEarliestSaplingRoot``

  * Committing to the earliest Sapling root of a range of blocks allows light clients to check the consistency of treestate transitions over a range of blocks, without recalculating the root from genesis.
  
- ``hashLatestSaplingRoot``

  * This commitment serves the same purpose as ``hashFinalSaplingRoot`` in current Sapling semantics.
  * However, because the MMR tree commits to blocks ``B_x ... B_(n-1)``, the latest commitment will descrie the final treestate of the previous block, rather than the current block. 
  * Concretely: block 500 currently commits to the final treestate of block 500 in its header. With this ZIP, block 500 will commit to all roots up to block 499, but not the final root of block 500.
  * We feel this is an acceptable tradeoff. Using the most recent treestate as a transaction anchor is already unsafe in reorgs. Clients should never use the most recent treestate to generate transactions, so it is acceptable to delay commitment by one block. 
    
- ``nShieldedTxCount``

  * By committing to the number of shielded transactions in blocks (and ranges of blocks), a light client may reliably learn whether a malicious server is witholding any shielded transactions. 
  * In addition, this commitment allows light clients to avoid syncing header ranges that do not contain shielded transactions. As the primary cost of a light client is transmission of equihash solution information in block headers, this optimization would significantly decrease the bandwidth requirements of light clients.

Header Format Change
~~~~~~~~~~~~~~~~~~~~~~

Our primary goal was to minimize header changes. The version number is incremented to signify the change in field semantics. This is not strictly necessary. Old light client parsers will generally not reject the new header semantics and we expect full nodes to follow the network upgrade. It may be the case that mining related hardware or software has (unwisely) hardcoded the version to 4. In which case, we would recommend not changing the header version number.

We considered adding ``hashChainHistoryRoot`` to the header as a new field. We decided against that, as it will inherently affect more of the ecosystem. As stated earlier, we would prefer not to introduce changes that could affect mining hardware or embedded software.

We also considered putting ``hashChainHistoryRoot`` in the ``hashPrevBlock`` field as it commits to the entire chain history, but quickly realized it would require massive refactoring of the existing code base and would negatively impact performance. Reorgs in particular are fragile, performance-critical, and rely on backwards iteration over the chain history. If a chain were to be designed from scratch there may be some efficient implementation that would join these commitments, but it is clearly not appropriate for ZCash as it exists.


Additional Reading
-------------------

- `Bitcoin difficulty calculation <https://en.bitcoin.it/wiki/Difficulty>`_
- `Flyclient enabled geth fork by FlyClient authors <https://github.com/mahdiz/flyeth>`_
- `ECIP-1055: Succinct PoW Using Merkle Mountain Ranges <https://github.com/etclabscore/ECIPs/pull/11/files?short_path=44c106e#diff-44c106ea0ef54fab09596596934d3d15>`_
- `Grin project MMR implementation in Rust <https://github.com/mimblewimble/grin/tree/milestone/2.0.0/core/src/core>`_
- `Tari Project MMR implementation in Rust <https://github.com/tari-project/tari/tree/development/infrastructure/merklemountainrange>`_
- `Beam Project MMR implementation in C++ <https://github.com/BeamMW/beam/blob/master/core/merkle.cpp>`_
- `Mimblewimble MMR docs <https://github.com/mimblewimble/grin/blob/master/doc/mmr.md>`_
- `MMR Python implementation <https://github.com/proofchains/python-proofmarshal/blob/master/proofmarshal/mmr.py>`_
- `Tari MMR documentation <https://docs.rs/merklemountainrange/0.0.1/src/merklemountainrange/lib.rs.html#23-183>`_
- `Zcash Protocol Specification, Version 2018.0-beta-37 [Overwinter+Sapling] <https://github.com/zcash/zips/blob/master/protocol/protocol.pdf>`_
- `opentimestamps-server Merkle Mountain Range documentation <https://github.com/opentimestamps/opentimestamps-server/blob/master/doc/merkle-mountain-range.md>`_

References
-----------

.. [#RFC2119] `Key words for use in RFCs to Indicate Requirement Levels <https://tools.ietf.org/html/rfc2119>`_
.. [#zip-0200] `ZIP 200: Network Upgrade Mechanism <https://github.com/zcash/zips/blob/master/zip-0200.rst>`_
.. [#zcashBlock] `zCash block primitive <https://github.com/zcash/zcash/blob/master/src/primitives/block.h>`_
.. [#ZIP-0307] `ZCash reference light client protocol <https://github.com/zcash/zips/blob/master/zip-0307/zip-0307.rst>`_
.. [#mimblewimble] `MimbleWimble Grin MMR implementation <https://github.com/mimblewimble/grin/blob/aedac483f5a116b91a8baf6acffd70e5f980b8cc/core/src/core/pmmr/pmmr.rs>`_
.. [#FlyClient] `FlyClient protocol <https://eprint.iacr.org/2019/226.pdf>`_