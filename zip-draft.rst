::

  ZIP: ????
  Title: Enable Staked Polling from the Sapling Pool
  Owners: Josh Cincinnati
  Status: Draft
  Type: Consensus
  Created: 2019-03-30
  License: BSD-2-Clause


Terminology
===========

The key words "MUST", "SHOULD", "SHOULD NOT", "MAY", "RECOMMENDED",
"OPTIONAL", and "REQUIRED" in this document are to be interpreted as
described in RFC 2119. [#RFC2119]_

Abstract
========

This ZIP is inspired by Zcash Issue 1119 [#zcash-issue-1119]_ and the
need for more scalable community polling mechanisms. The proposal would
seek to implement changes to enable holders of Sapling-shielded ZEC
to vote on multiple choices within arbitrary proposals without spending
their ZEC or revealing their holdings and only revealing the aggregate results
of the poll.

For a more concrete, hypothetical example: let's say 100,000 ZEC is stored
across an unknown number of users in shielded Sapling addresses. The Zcash
Foundation wants to run a poll on whether shielded Sapling holders support
their latest budget. Upon prompting the question and the choices, users
submit non-spending transactions from their shielded Sapling addresses,
which are aggregated and shared on the Zcash Foundation website. Upon
completion of the poll, which expires by a block height, the non-spending
transactions could be compared against the Zcash blockchain and give us
a result that shows the aggregate number of shielded ZEC that voted for
a given choice (without revealing individual holdings). In this case,
a result may look like:

10,000 ZEC strongly approve of the budget
20,000 ZEC approve of the budget
30,000 ZEC disapprove of the budget
40,000 ZEC strongly disapprove of the budget

Motivation
==========

In 2018 the Zcash Foundation had `a governance advisory panel,
<https://www.zfnd.org/blog/governance-results/>`__ which was a reasonable attempt
at soliciting more community feedback, but it suffered from a few flaws:

- Individual authority by the Foundation could accept/decline membership
- Not scalable to thousands of potential participants
- Required too much orchestration to do frequent polls
- Membership in the panel required identity/pseudonymity
- Possible that membership didn't adequately represent the interest of ZEC users

This proposal would give the Zcash Foundation (and any other group) the opportunity
to engage in community polling that would preserve users' privacy while supplying
a representative sample of ZEC user interest.

To be explicit: in a world with binding decisions by staked voting, there's an inherent
danger of large stakes controlling governance decisions. Thus I do not expect
this will be the only governance tool in the Zcash Foundation toolkit. But it could
be a very important one all the same, and it certainly would improve upon the Zcash
Foundation's past advisory panel.

Other sections TBD
==================

Technical details to follow. I do not intend to remain the owner of this
ZIP, but I wanted to make sure it was submitted before the NU3 deadline.


References
==========

.. [#zcash-issue-1119] `Voting based on proof-of-stake <https://github.com/zcash/zcash/issues/1112>`_
.. [#RFC2119] `Key words for use in RFCs to Indicate Requirement Levels <https://tools.ietf.org/html/rfc2119>`_
