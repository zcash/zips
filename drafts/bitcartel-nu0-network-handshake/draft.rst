::

  ZIP: 201
  Title: Network Peer Management for Overwinter
  Author: Simon Liu <simon@z.cash>
  Category: Network
  Created: 2018-01-15
  License: MIT

Terminology
===========

The key words "MUST", "MUST NOT", "SHOULD", and "MAY" in this document are to be interpreted as described in RFC 2119. [#RFC2119]_

The terms below are to be interpreted as follows:

Branch
  A chain of blocks with common consensus rules, where the first block in the chain is either the genesis
  block, or the child of a parent block created under an older set of consensus rules (i.e. the parent block
  is a member of a different branch). By definition, every block belongs to at most one branch.

Hard fork
  The creation of a new branch by a change in the consensus rules of the network. Nodes that do not recognize
  the new rules will continue to follow the old branch.

Network upgrade
  An intentional hard fork undertaken by the community in order to improve the network.

Overwinter
  Code-name for the first ZCash network upgrade, also known as Network Upgrade Zero.


Abstract
========

This proposal defines an upgrade to the network handshake and peer management required for network upgrades following the Network Upgrade Activation Mechanism [#zip-0200]_.

Related to:

- Transaction Signature Verification for Overwinter [#zip-0143]_.
- Version 3 Transaction Format for Overwinter [#zip-0202]_.
- Transaction Expiry [#zip-0203]_.

Motivation
==========

With scheduled network upgrades, at the activation height, nodes on each branch should disconnect from nodes on other branches and only accept new incoming connections from nodes on the same branch.

Specification
=============

When a new inbound connection is received or an outbound connection created, a CNode object is instantiated with the version field set to INIT_PROTO_VERSION which has a value of 209. This value is not transmitted across the network, but for legacy reasons and technical debt beyond the scope of this ZIP, this value will not be changed.

Once the two nodes have connected and started the handshake to negotiate the protocol version, the version field of CNode will be updated.  The handshake [#bitcoin-version-handshake]_ involves "version" and "verack" messages being exchanged.::

    L -> R: Send version message with the local peer's version
    R -> L: Send version message back
    R -> L: Send verack message
    R:      Sets version to the minimum of the 2 versions
    L -> R: Send verack message after receiving version message from R
    L:      Sets version to the minimum of the 2 versions

To send a version message, the node will invoke ``PushVersion()``::

    void CNode::PushVersion() {
        ...
        PushMessage("version", PROTOCOL_VERSION, nLocalServices, nTime, addrYou, addrMe, ...);
        ...
    }
      
where:

- Pre-Overwinter PROTOCOL_VERSION is 170002
- OVERWINTER_PROTO_VERSION is 170003


Rejecting Pre-Overwinter Connections
------------------------------------

Currently, nodes will reject connections from nodes with a protocol version lower than the other node's minimum supported protocol version.

This value is defined as::

    //! disconnect from peers older than this proto version
    static const int MIN_PEER_PROTO_VERSION = 170002;
    
With rejection implemented as::
    
    if (pfrom->nVersion < MIN_PEER_PROTO_VERSION)
    {
        // disconnect from old peers running protocol version we don't support.

Prior to activation, Overwinter nodes will contain the following constants::

    static const int PROTOCOL_VERSION = 170003;
    static const int MIN_PEER_PROTO_VERSION = 170002;

A pre-Overwinter node is defined to be a node for which the highest supported protocol version is < 170003.  The above constant definitions allow pre-Overwinter nodes that support protocol version 170002, and Overwinter nodes (which support both protocol versions 170002 and 170003 before Overwinter activation) to remain connected until the activation.

These values cannot be changed at run-time, so when Overwinter activates, Overwinter nodes should take steps to:

- reject new connections from pre-Overwinter nodes;
- disconnect any existing connections to pre-Overwinter nodes.


Network Coalescence
-------------------

Prior to the activation of Overwinter, nodes running pre-Overwinter protocol version 170002 and the Overwinter protocol version 170003 remain connected with the same consensus rules, but it is desirable for nodes supporting Overwinter to connect preferentially to other nodes supporting Overwinter.

This would help the network partition smoothly, since nodes should already be connected to (a majority of) peers running the same protocol version.  Otherwise an Overwinter node may find their connections to Sprout nodes dropped suddenly at the activation height, potentially leaving them isolated and susceptible to eclipse attacks. [#eclipse-attack]

To assist network coalescence before the activation height, we update the eviction process to place a higher priority on evicting Sprout nodes.

Currently, an eviction process takes place when new inbound connections arrive, but the node has already connected to the maximum number of inbound peers::

    if (nInbound >= nMaxInbound)
    {
        if (!AttemptToEvictConnection(whitelisted)) {
            // No connection to evict, disconnect the new connection
            LogPrint("net", "failed to find an eviction candidate - connection dropped (full)\n");
            CloseSocket(hSocket);
            return;
        }
    }

We update this process by adding behaviour so that the set of eviction candidates will prefer pre-Overwinter nodes, when the chain tip is in a period N blocks before the activation block height, where N is defined as::

    static const int NETWORK_UPGRADE_PEER_PREFERENCE_BLOCK_PERIOD = 1000.

The eviction candidates can be modified as so::

    static bool AttemptToEvictConnection(bool fPreferNewConnection) {
    ...
    // Protect connections with certain characteristics
    ...
    // Check version of eviction candidates...
    // If we are connected to any pre-Overwinter nodes, keep them in the eviction set and remove any Overwinter nodes
    // If we are only connected to Overwinter nodes, continue with existing behaviour.
    if ((height < nActivationHeight) &&
        (height >= (nActivationHeight - NETWORK_UPGRADE_PEER_PREFERENCE_BLOCK_PERIOD)))
    {
        // Find any nodes which don't support Overwinter protocol version
        BOOST_FOREACH(const CNodeRef &node, vEvictionCandidates) {
            if (node->nVersion < OVERWINTER_PROTO_VERSION) {
                vTmpEvictionCandidates.push_back(node);
            }
        }

        // Prioritize these nodes by replacing eviction set with them
        if (vTmpEvictionCandidates.size() > 0) {
            vEvictionCandidates = vTmpEvictionCandidates;
        }
    }

The existing method of disconnecting a candidate remains:

    vEvictionCandidates[0]->fDisconnect = true;

The existing eviction process will classify and divide eviction candidates into buckets called netgroups.  If a netgroup only has one peer, it will not be evicted.  This means at least one pre-Overwinter node will remain connected upto the activation block height, barring any network issues or a high ban score.


Disconnecting Existing Connections
----------------------------------

At the activation block height, an Overwinter node may still remain connected to pre-Overwinter nodes.  Currently, when connecting, a node can only perform the networking handshake once, where it sends the version message before any other messages are processed.  To disconnect existing pre-Overwinter connections, ``ProcessMessage`` is modified so that once Overwinter activates, if necessary, the protocol version of an existing peer is validated when inbound messages arrive.

Example code::

    bool static ProcessMessage(CNode* pfrom, string strCommand, CDataStream& vRecv, int64_t nTimeReceived)
        ...
        else if (pfrom->nVersion == 0)
        {
            // Must have a version message before anything else
            Misbehaving(pfrom->GetId(), 1);
            return false;
        }
        else if (strCommand == "verack")
        {
            ...
        }

        // Disconnect existing peer connection when:
        // 1. Minimum peer version is less than Overwinter version
        // 2. The version message has been received from a peer
        // 3. The peer's version is pre-Overwinter
        // 4. Overwinter is active
        else if (
            MIN_PEER_PROTO_VERSION < OVERWINTER_PROTO_VERSION &&
            pfrom->nVersion != 0 &&
            pfrom->nVersion < OVERWINTER_PROTO_VERSION &&
            NetworkUpgradeActive(GetHeight(), chainparams.GetConsensus(), Consensus::UPGRADE_OVERWINTER))
        {
            LogPrintf("peer=%d using obsolete version %i; disconnecting\n", pfrom->id, pfrom->nVersion);
            pfrom->PushMessage("reject", strCommand, REJECT_OBSOLETE,
                                strprintf("Version must be %d or greater", OVERWINTER_PROTO_VERSION));
            pfrom->fDisconnect = true;
            return false;
        }



Deployment
==========

This proposal will be deployed with the Overwinter network upgrade.


Backward compatibility
======================

This proposal intentionally creates what is known as a hard fork where Overwinter nodes disconnect from pre-Overwinter nodes.

Prior to the network upgrade activating, Overwinter and pre-Overwinter nodes are compatible and can connect to each other. However, Overwinter nodes will have a preference for connecting to other Overwinter nodes, so pre-Overwinter nodes will gradually be disconnected in the run up to activation.

Once the network upgrades, even though pre-Overwinter nodes can still accept the numerically larger protocol version used by Overwinter as being valid, Overwinter nodes will always disconnect peers using lower protocol versions.


Reference Implementation
========================

https://github.com/zcash/zcash/pull/2919


References
==========

.. [#RFC2119] https://tools.ietf.org/html/rfc2119
.. [#zip-0143] `Transaction Signature Verification for Overwinter <https://github.com/zcash/zips/pull/129>`_
.. [#zip-0200] `Network Upgrade Activation Mechanism <https://github.com/zcash/zips/pull/128/>`_
.. [#zip-0202] `Version 3 Transaction Format for Overwinter <https://github.com/zcash/zips/pull/133>`_
.. [#zip-0203] `Transaction Expiry <https://github.com/zcash/zips/pull/131>`_
.. [#bitcoin-verson] https://en.bitcoin.it/wiki/Protocol_documentation#version
.. [#bitcoin-version-handshake] https://en.bitcoin.it/wiki/Version_Handshake
.. [#eclipse-attack] `Eclipse Attacks on Bitcoin’s Peer-to-Peer Network <https://eprint.iacr.org/2015/263>`_
.. [#partition-discussion] `Partition nodes with old protocol version from network in advance of hard fork <https://github.com/zcash/zcash/issues/2775>`_

