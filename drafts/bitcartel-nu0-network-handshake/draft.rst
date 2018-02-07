::

  ZIP: ???
  Title: Network Upgrade Zero ("OverWinter") Network Handshake
  Author: Simon Liu <simon@z.cash>
  Comments-Summary: No comments yet.
  Category: Process
  Created: 2018-01-15
  License: MIT

Terminology
===========

The key words "MUST", "MUST NOT", "SHOULD", and "MAY" in this document are to be interpreted as described in RFC 2119.

"Legacy" - pre-NU0

"NU0" - Network upgade zero

"Overwinter" - Code-name for NU0

Abstract
========

This proposal defines an upgrade to network handshake format required for Network Upgrade Activation Mechanism [#zip-0???]_.

Related to [#zip-0143]_

Motivation
==========

With scheduled network upgrades, at the activation height, nodes on each branch should disconnect from nodes on other branches and only accept new incoming connections from nodes on the same branch.

Specification
=============

When a new inbound connection is received or an outbound connection created, a CNode object is instantiated with the version field set to INIT_PROTO_VERSION which has a value of 209. This value is not transmitted across the network, but for legacy reasons and technical debt beyond the scope of this ZIP, this value will not be changed.

Once the two nodes have connected and started the handshake to negotiate the protocol version, the version field of CNode will be updated.  The handshake involves "version" and "verack" messages being exchanged.::

    L -> R: Send version message with the local peer's version
    R -> L: Send version message back
    R -> L: Send verack message
    R:      Sets version to the minimum of the 2 versions
    L -> R: Send verack message after receiving version message from R
    L:      Sets version to the minimum of the 2 versions
    
    Source: https://en.bitcoin.it/wiki/Version_Handshake

To send a version message, the node will invoke PushVersion()::

    void CNode::PushVersion() {
        ...
        PushMessage("version", PROTOCOL_VERSION, nLocalServices, nTime, addrYou, addrMe,
        ...
    }
      
Where:

- Pre-Overwinter PROTOCOL_VERSION is 170002
- OVERWINTER_PROTO_VERSION is 170003


Rejecting Pre-Overwinter Connections
------------------------------------

Currently, nodes will reject connections from nodes with a protocol version lower than the other node's minimum supported protocol version.

This value is defined as::

    //! disconnect from peers older than this proto version
    static const int MIN_PEER_PROTO_VERSION = 170002;
    
With rejection codified as::
    
    if (pfrom->nVersion < MIN_PEER_PROTO_VERSION)
    {
        // disconnect from old peers running protocol version we don't support.

Prior to activation, Overwinter nodes will contain the following constants::

    static const int PROTOCOL_VERSION = 170003;
    static const int MIN_PEER_PROTO_VERSION = 170002;

This allows pre-Overwinter nodes (which only supports protocol version 170002) and Overwinter nodes (which support both 170002 and 170003) to remain connected prior to activation.

However, once Overwinter activates, Overwinter nodes should:

- reject new connections from pre-Overwinter nodes
- disconnect any existing conncetions to pre-Overwinter nodes


Network Coalescence
-------------------

Prior to the activation of Overwinter, nodes running pre-Overwinter protocol version 170002 and the Overwinter protocol version 170003 remain connected with the same consensus rules, but it would be preferable for nodes supporting Overwinter to connect to other nodes supporting Overwinter.

This will help the network partition smoothly, since nodes should already be connected to (a majority of) peers running the same protocol version.  Otherwise am Overwinter node may find their connections to legacy nodes dropped at the activation height, leaving them isolated and potentially susceptible to eclipse attacks. [link]

To assist network coalescence before the activation height, we update the eviction process to place a higher priority on evicting legacy nodes.

This can be activated at n blocks before the activation block height, where n could be defined by a constant such as::

    static const int NETWORK_COALESCE_BLOCK_PERIOD = 1000.

The eviction code can be updated as follows::

    static bool AttemptToEvictConnection(bool fPreferNewConnection) {
    ...
    // Protect connections with certain characteristics
    ...
    // Check version of eviction candidates
    if (current_block_height >= (activationheight - NETWORK_COALESCE_BLOCK_PERIOD)) {
      // if there exist any legacy nodes, keep them in the eviction set
      // and at the same time remove overwinter nodes from eviction set.
      // if there do not exist any legacy nodes,
      // continue with existing behaviour.


Disconnecting Existing Connections
----------------------------------

It is likely that at the activation block height, an Overwinter node will still be connected to some Legacy nodes.

Currently, when connecting, a node must perform the networking handshake, and send the version message, before any other messages are processed.

To disconnect existing connections, we can modify ProcessMessage so that the protocol version is always checked after Overwinter activates.

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

        // Disconnect existing connection if:
        // 1. The version message has been received
        // 2. Overwinter is active
        // 3. Version is legacy
        else if (
            pfrom->nVersion != 0 &&
            isOverwinterActivated() &&
            pfrom->nVersion < OVERWINTER_PROTO_VERSION )
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

Testnet:

Mainnet:

Backward compatibility
======================

This proposal intentionally creates what is known as a "bilateral hard fork" between Legacy software and Overwinter compatible software. Use of this new handshake requires that all network participants upgrade their software to a compatible version within the upgrade window

Legacy software will accept the numerically larger Overwinter protocol version as valid, but Overwinter compatible software will reject the legacy nodes once Overwinter activates by rejecting protocol versions lower than the Overwinter protocol version number. 

Reference Implementation
========================

TBC


References
==========

Partition nodes with old protocol version from network in advance of hard fork https://github.com/zcash/zcash/issues/2775

https://en.bitcoin.it/wiki/Protocol_documentation#version

.. [#zip-0???] Network Upgrade Activation Mechanism
