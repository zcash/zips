Abstract
========

This ZIP describes the Zcash variant of the Stratum protocol, used by miners to
communicate with mining pool servers.


Specification
=============

The Stratum protocol is an instance of [JSON-RPC-1.0]_. The miner is a JSON-RPC
client, and the Stratum server is a JSON-RPC server. The miner starts a session
by opening a standard TCP connection to the server, which is then used for
two-way line-based communication:

- The miner can send requests to the server.
- The server can respond to requests.
- The server can send notifications to the client.

All communication for a particular session happens through a single connection,
which is kept open for the duration of the session. If the connection is broken
or either party disconnects, the active session is ended. Servers MAY support
session resuming; this is negotiated between the client and server during intial
setup.

Each request or response is a JSON string, terminated by an ASCII LF character
(denoted in the rest of this specification by ``\n``). The LF character MUST NOT
appear elsewhere in a request or response. Client and server implementations MAY
assume that once they read a LF character, the current message has been
completely received.

.. [JSON-RPC-1.0] JSON-RPC.org. *JSON-RPC 1.0 Specifications*.
  URL: http://json-rpc.org/wiki/specification (visited on 2016-09-24).

Protocol Flow
~~~~~~~~~~~~~

- Client sends ``mining.subscribe`` to set up the session.
- Server replies with the session information.
- Client sends ``mining.authorize`` for their worker(s).
- Server replies with the result of authorization.
- Server sends ``mining.set_target``.
- Server sends ``mining.notify`` with a new job.
- Client mines on that job.
- Client sends ``mining.submit`` for each solution found.
- Server replies with whether the solution was accepted.
- Server sends ``mining.notify`` again when there is a new job.

Methods
~~~~~~~

``mining.subscribe()``
----------------------

Request::

    {"id": 1, "method": "mining.subscribe", "params": ["CONNECT_HOST", CONNECT_PORT, "MINER_USER_AGENT", "SESSION_ID"]}\n

``CONNECT_HOST`` (str)
  The host that the miner is connecting to (from the server URL).

  Example: ``pool.example.com``

``CONNECT_PORT`` (int)
  The port that the miner is connecting to (from the server URL).

  Example: ``3337``

``MINER_USER_AGENT`` (str)
  A free-form string specifying the type and version of the mining software.
  Recommended syntax is the User Agent format used by Zcash nodes.

  Example: ``Zatoshi/1.0.0``

``SESSION_ID`` (str)
  The id for a previous session that the miner wants to resume (e.g. after a
  temporary network disconnection).

  MAY be ``null`` indicating that the miner wants to start a new session.

Response::

    {"id": 1, "result": ["NONCE_1", "SESSION_ID"], "error": null}\n

``SESSION_ID`` (str)
  The session id, for use when resuming.

  MAY be ``null`` indicating that the server does not support session resuming.

``NONCE_1`` (hex)
  The first part of the block header nonce.

  The nonce in Zcash's block header is 32 bytes long. The miner MUST pick
  ``NONCE_2`` such that ``len(NONCE_2) = 32 - len(NONCE_1)`` in bytes, or
  ``len(NONCE_2) = 64 - len(NONCE_1)`` in hex.


``mining.authorize()``
----------------------

A miner MUST authorize a worker in order to submit solutions. A miner MAY
authorize multiple workers in the same session; this could be for statistical
purposes on the particular server being used. Details of such purposes are
outside the scope of this specification.

Request::

    {"id": 2, "method": "mining.authorize", "params": ["WORKER_NAME", "WORKER_PASSWORD"]}\n

``WORKER_NAME`` (str)
  The worker name.

``WORKER_PASSWORD`` (str)
  The worker name.

Response::

    {"id": 2, "result": AUTHORIZED, "error": "MESSAGE"}\n

``AUTHORIZED`` (bool)
  Whether authorization succeeded.

``MESSAGE`` (str)
  An error message. MUST be ``null`` if authorization succeeded.

  If authorization failed, the server MUST provide an error message describing
  the reason.

  [TODO: Specify format of error messages]

``mining.set_target()``
-----------------------

Server message::

    {"id": null, "method": "mining.set_target", "params": ["TARGET"]}\n

``TARGET`` (hex)
  The server target for the next received job and all subsequent jobs (until the
  next time this message is sent). The miner compares proposed block hashes with
  this target as a 256-bit big-endian integer, and valid blocks MUST NOT have
  hashes larger than (above) the current target (in accordance with the Zcash
  network consensus rules [Zcash-Target]_).

  Miners SHOULD NOT submit work above this target. Miners SHOULD validate their
  solutions before submission (to avoid both unnecessary network traffic and
  wasted miner time).

  Servers MUST NOT accept submissions above this target for jobs sent after this
  message. Servers MAY accept submissions above this target for jobs sent before
  this message, but MUST check them against the previous target.

When displaying the current target in the UI to users, miners MAY convert the
target to an integer difficulty as used in Bitcoin miners. When doing so, miners
SHOULD use ``powLimit`` (as defined in ``src/chainparams.cpp``) as the basis for
conversion.

.. [Zcash-Target] Daira Hopwood, Sean Bowe, Taylor Hornby, Nathan Wilcox.
  "Difficulty filter". In: *Zcash Protocol Specification*.
  Version 2016.0-beta-1.5, Section 6.4.2. September 22, 2016.
  URL: https://github.com/zcash/zips/blob/master/protocol/protocol.pdf
  (visited on 2016-09-24).

``mining.notify()``
-------------------

Server message::

    {"id": null, "method": "mining.notify", "params": ["JOB_ID", "VERSION", "PREVHASH", "MERKLEROOT", "RESERVED", "TIME", "BITS", CLEAN_JOBS]}\n

``JOB_ID`` (str)
  The id of this job.

``VERSION`` (int)
  The block header version. Used as a switch for subsequent parameters.

The following parameters are only valid for ``VERSION == 4``:

``PREVHASH`` (hex)
  The hash of the previous block.

``MERKLEROOT`` (hex)
  The Merkle root of the transactions in this block.

``RESERVED`` (hex)
  A 256-bit reserved field; zero by convention.

``TIME`` (hex)
  The block time suggested by the server.

``BITS`` (compactBits)
  The current network difficulty target.

``CLEAN_JOBS`` (bool)
  If true, a new block has arrived. The miner SHOULD abandon all previous jobs.

``mining.submit()``
-------------------

Request::

    {"id": 4, "method": "mining.submit", "params": ["WORKER_NAME", "JOB_ID", "TIME", "NONCE_2", "EQUIHASH_SOLUTION"]}\n

``WORKER_NAME`` (str)
  A previously-authenticated worker name.

  Servers MUST NOT accept submissions from unauthenticated workers.

``JOB_ID`` (str)
  The id of the job this submission is for.

  Miners MAY make multiple submissions for a single job id.

``TIME`` (hex)
  The block time used in the submission.

  MAY be enforced by the server to be unchanged.

``NONCE_2`` (hex)
  The second part of the block header nonce.

Result::

    {"id": 4, "result": ACCEPTED, "error": "MESSAGE"}\n

``ACCEPTED`` (bool)
  Whether the block was accepted.

``MESSAGE`` (str)
  An error message. MUST be ``null`` if the block was accepted.

  If the block was not accepted, the server MUST provide an error message
  describing the reason for not accepting the block.

  [TODO: Specify format of error messages]

``client.reconnect()``
----------------------

Server message::

    {"id": null, "method": "client.reconnect", "params": [("HOST", PORT, WAIT_TIME)]}\n

``HOST`` (str)
  The host to reconnect to.

  Example: ``pool.example.com``

``PORT`` (int)
  The port to reconnect to.

  Example: ``3337``

``WAIT_TIME`` (int)
  Time in seconds that the miner should wait before reconnecting.

If ``client.reconnect`` is sent with empty parameters, the miner SHOULD
reconnect to the same host and port it is currently connected to.

``mining.suggest_target()``
---------------------------

Request (optional)::

    {"id": 3, "method": "mining.suggest_target", "params": ["TARGET"]}\n

``TARGET`` (hex)
  The target suggested by the miner for the next received job and all subsequent
  jobs (until the next time this message is sent).

The server SHOULD reply with ``mining.set_target``. The server MAY set the
result id equal to the request id.


Motivation
==========

Many existing cryptocurrency miners and pools use the original Stratum protocol
for communication, in situations where the miner does not require any control
over what they mine (for example, a miner connected to a local P2Pool node).
However, the protocol is very specific to Bitcoin, in that it makes assumptions
about the block header format, and the available nonce space. Zcash has made
changes that invalidate these assumptions.

Having a formal specification for a Zcash-compatible Stratum-style mining
protocol means that existing pool operators and miner authors can quickly and
easily migrate their frameworks to the Zcash network, with no ambiguity about
interoperability.


Rationale
=========

Why does ``mining.subscribe`` include the host and port?

- It has the same use cases as the ``Host:`` header in HTTP. Specifically, it
  enables virtual hosting, where virtual pools or private URLs might be used
  for DDoS protection, but that are aggregated on Stratum server backends.
  As with HTTP, the server CANNOT trust the host string.

- The port is included separately to parallel the ``client.reconnect`` method;
  both are extracted from the server URL that the miner is connecting to (e.g.
  ``stratum+tcp://pool.example.com:3337``).

Why use the 256-bit target instead of a numerical difficulty?

- There is no protocol ambiguity when using a target. A server can pick a
  specific target (by whatever algorithm), and enforce it cleanly on submitted
  jobs.

  - A numerical difficulty must be converted into a target by miners, which adds
    unnecessary complexity, results in a loss of precision, and leaves ambiguity
    over the conversion and the validity of resulting submissions.

- The minimum numerical difficulty in Bitcoin's Stratum protocol is 1, which
  corresponds to ``powLimit``. This makes it harder to test miners and servers.
  A target can represent difficulties lower than the minimum.

Does a 256-bit target waste bandwidth?

- The target is generally not set as often as solutions are submitted, so any
  effect is minimal.

- Zcash's proof-of-work, Equihash, is much slower than Bitcoin's, so any latency
  caused by the size of the target is minimal compared to the overall solver
  time.

- For the current Equihash parameters (200/9), the Equihash solution dominates
  bandwidth usage.

Why does ``mining.submit`` include ``WORKER_NAME``?

- ``WORKER_NAME`` is only included here for statistical purposes (like
  monitoring performance and/or downtime). ``JOB_ID`` is used for pairing
  server-stored jobs with submissions.


Reference Implementation
========================

- `str4d's standalone miner`_

.. _`str4d's standalone miner`: https://github.com/str4d/zcash/tree/standalone-miner


Acknowledgements
================

Thanks to:

- 5a1t for the initial brainstorming session.

- Daira Hopwood for her input on API selection and design.

- Marek Palatinus (slush) and his colleagues for their refinements, suggestions, and
  robust discussion.

This ZIP was edited by [TODO: fill in]


References
==========

Documentation for the original Stratum protocol:

- https://slushpool.com/help/#!/manual/stratum-protocol
- https://bitcointalk.org/index.php?topic=557866.0
