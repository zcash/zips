    ZIP: Unassigned
    Title: The Zcash Town Square: Official Discussion and Announcement Cross-Posting
    Owners: Blake Benthall (emersonian) <e@emersonbenthall.com>
    Status: Draft
    Category: Process
    Created: 2026-11-08
    License: MIT
    Discussions-To: <https://forum.zcashcommunity.com/t/zip-the-zcash-town-square/59049>
    Pull-Request: <https://github.com/zcash/zips/pull/1454>
    Updates: 1015, 1016


# Terminology

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this
document are to be interpreted as described in BCP 14 [^BCP14] when, and only
when, they appear in all capitals.

The terms "Zcash Community Grants" (or "ZCG"), "ZCG Committee", "Financial
Privacy Foundation" (or "FPF"), "Autonomous Entities", and "Discretionary Budget" in
this document are to be interpreted as defined in ZIP 1015 [^zip-1015].

The terms "Protocol-defined Ecosystem Funding", "Coinholder-Controlled Fund",
and "Key-Holder Organizations" in this document are to be interpreted as
defined in ZIP 1016 [^zip-1016], as amended by any later ZIP that updates those
definitions.

"Zcash Community Forum" (or "the Forum") means the discussion forum hosted at
<https://forum.zcashcommunity.com/>, or any successor forum designated by a
ZIP in accordance with [Succession of the Zcash Town Square].

"Zcash Town Square" is the designation given to the Zcash Community Forum by
this ZIP.

"Other Platform" means any public or semi-public communication channel other
than the Forum. This includes, but is not limited to: X (formerly Twitter),
Bluesky, Farcaster, Nostr, Mastodon and other federated networks, Discord,
Telegram, Signal and WhatsApp groups or channels, Reddit, YouTube, podcasts,
livestreams, Medium, Substack and other blogs, an organization's own website,
press releases, newsletters, and GitHub release notes or discussions.

"Zcash Funding Source" means any of the following:

* Protocol-defined Ecosystem Funding, including every Funding Stream
  [^zip-0207] and Lockbox Funding Stream [^zip-2001] defined by a ZIP;
* the Zcash Community Grants program, including its Discretionary Budget, as
  administered by FPF under ZIP 1015 [^zip-1015-zcg] and ZIP 1016;
* the Coinholder-Controlled Fund, including the ZIP 271 disbursement address
  [^zip-0271] and any grant approved by a coinholder-amount voting round under
  ZIP 1016; and
* any future fund, funding stream, or grant program that is defined, seeded,
  or authorized by a ZIP.

"Covered Organization" means any of the following, for as long as the
condition holds and for 12 months afterwards (the "Covered Period"):

* any organization or individual that receives, has received, or is party to
  an agreement to receive funds from a Zcash Funding Source, whether directly
  or as a grantee, sub-grantee, or Autonomous Entity;
* FPF, in its role as administrator of Zcash Community Grants;
* each Key-Holder Organization; and
* the ZCG Committee, which is treated as a Covered Organization in its own
  right, separate from FPF.

An organization that receives payment from a Covered Organization solely as an
arm's-length vendor of goods or services (for example a hosting provider, an
auditing firm, or a law firm), and that does not itself receive a grant from a
Zcash Funding Source, is not a Covered Organization by reason of that payment.

An individual who receives a grant from a Zcash Funding Source in their own
name, rather than through an organization, is treated as a Covered Organization
of which they are the sole Executive.

"Executive" means, for a Covered Organization, any natural person who holds
any of the following roles in that organization:

* chief executive officer, executive director, president, or managing
  director, or an equivalent head of the organization by any title;
* any other officer with a title of the form "Chief ... Officer", or an
  equivalent senior officer;
* a member of its board of directors, foundation council, or equivalent
  governing body;
* a founder or co-founder who continues to hold an operating or governing role;
* the named lead of any grant from a Zcash Funding Source held by the
  organization; or
* for the ZCG Committee, each member of the ZCG Committee.

"Official Account" means any account on an Other Platform that is operated by
or on behalf of a Covered Organization and that represents itself as speaking
for that organization, or for a product or project of that organization.

"Covered Speaker" means an Executive of a Covered Organization during its
Covered Period, or an Official Account of a Covered Organization during its
Covered Period.

"Announcement" has the meaning given in [Definition of Announcement].

"Official Discussion" has the meaning given in [Official Discussion].


# Abstract

This ZIP affirms that the Zcash Community Forum is the Zcash Town Square: the
one official venue for discussion of Zcash governance, funding, and protocol
direction, and the canonical public record of announcements made by
organizations that are funded by the Zcash community.

It requires every Executive and Official Account of any organization that
receives funding from a Zcash Funding Source (the ZCG stream, the
Coinholder-Controlled Fund, or any future ZIP-defined fund), together with the
Key-Holder Organizations, FPF, and the ZCG Committee, to cross-post to the Forum
every Announcement they make on any other platform, including but not limited
to X, within 24 hours. It defines what counts as an Announcement, how a
cross-post must be made, and how compliance is reported and enforced through
the grant agreements and disbursement processes that already exist.

This ZIP does not restrict anyone from speaking on any platform. It has limited
privacy implications, which are discussed in [Privacy Implications]: it does
not require pseudonymous participants to reveal legal identities.


# Motivation

Zcash is funded in large part by the Zcash community itself, through block
subsidies directed to Zcash Community Grants and to the Coinholder-Controlled
Fund. Organizations that receive those funds are accountable to the community
that funds them. That accountability depends on the community being able to
see what those organizations say and decide, in one place, in a durable and
searchable form.

In practice, important announcements are increasingly made first, and
sometimes only, on X and other commercial platforms. This creates several
problems:

* Fragmentation: following what funded organizations have said means
  watching many accounts on many platforms, some of them invite-only.
* Access: several platforms require a login to read in full, rate-limit
  readers, or rank posts so that many interested readers never see them.
* Durability: posts can be edited, deleted, or lost when an account is
  suspended or sold, or a platform changes its rules or shuts down, so the
  record of what an organization committed to can disappear.
* Discussion: short-form platforms suit careful, threaded debate poorly, and
  replies scatter across quote-posts that cannot be collected in one place.
* Capture risk: if the main channel is one commercial platform, its owner
  gains influence over Zcash governance that the community never granted.

The Forum already plays a central role in Zcash governance. ZIP 0 [^zip-0000]
directs ZIP authors to post new ideas there and asks Editors to check that
substantive ZIP updates have been announced there, ZCG grant proposals are discussed
there, and the questions and results of the NU7 coinholder polls were published
there [^zip-0259]. However, no ZIP states that the Forum is the official venue,
and no ZIP requires funded organizations to publish their announcements there.
This ZIP fills that gap.


# Privacy Implications

This ZIP does not affect the privacy of Zcash transactions or of Zcash users in
general.

It requires Covered Organizations to publish a register of their Executives
and Official Accounts (see [Register of Covered Speakers]). Some Executives,
particularly of small grantees, participate in Zcash under a pseudonym. The
register identifies Executives by the public handle under which they already
act for the organization, and does not require a legal name, address, or any
other identifying information that the Executive has not already made public.

Cross-posting copies content that a Covered Speaker has already chosen to make
public. It does not require the publication of private messages, of
communications within private groups that are not Announcements, or of
security information that is under responsible-disclosure embargo.


# Requirements

* There is one clearly identified official venue for Zcash governance
  discussion and for the public record of funded organizations' announcements.
* Anyone can read that record without an account, and it is archived and
  searchable.
* Every Announcement made by an Executive or Official Account of a funded
  organization on any other platform also appears on the Forum, in full,
  promptly.
* The obligation is defined precisely enough that a third party can determine
  whether a given post is covered and whether it was cross-posted in time.
* Non-compliance is publicly visible and has proportionate consequences tied
  to the funding that creates the obligation, using processes that already
  exist under ZIP 1015 and ZIP 1016.
* Nothing prevents anyone from using any platform they choose, and the ZIP does
  not hand new censorship powers to the operator of the Forum.
* The designation can be moved to a successor venue if the Forum ceases to
  serve the community.


# Non-requirements

* This ZIP does not regulate what people who are not Covered Speakers say, or
  where they say it.
* This ZIP does not regulate the content of Announcements, only where they
  are published.
* This ZIP does not move technical review of ZIP text away from the ZIPs
  repository on GitHub, nor replace synchronous calls such as Arborist calls.
  It does require that their governance-relevant outcomes be recorded on the
  Forum.


# Specification

## Designation of the Zcash Town Square

The Zcash Community Forum is designated the Zcash Town Square.

The Zcash Town Square is the sole official venue for Official Discussion, and
the canonical public record of Announcements made by Covered Speakers.

## Official Discussion

"Official Discussion" means public discussion, proposal, or decision-making
concerning any of the following:

1. ZIPs, including proposals for new ZIPs and changes to the Status of a ZIP;
2. network upgrades, including their scope, timing, and activation;
3. any Zcash Funding Source, including grant proposals, grant decisions,
   milestone reviews, and disbursements;
4. coinholder-amount voting rounds and any other community or coinholder
   polls or votes, including their questions, timing, and results; and
5. the obligations, conduct, or composition of Covered Organizations insofar
   as they relate to the matters above.

Discussion of these matters MAY take place on any platform. However:

* Proposals for funding from a Zcash Funding Source MUST be posted on the Forum
  before they are decided, and the decision MUST be published on the Forum.
* The questions of every coinholder-amount voting round or other community
  poll held under a ZIP MUST be published on the Forum before the voting
  period begins, and the results MUST be published on the Forum.
* A ZIP's Discussions-To header SHOULD point to a Forum thread. Where it does
  not, the Owners SHOULD create a Forum thread for the ZIP and link to it from
  the ZIP.
* Where a governance-relevant decision or outcome is reached in another venue
  (for example a call, a GitHub pull request, or a meeting of a Covered
  Organization), the Covered Organization or ZIP Owner responsible SHOULD post
  a summary to the Forum within 7 days.
* A statement made only on an Other Platform has no official standing in any
  process defined by a ZIP. Any person or body that is required by a ZIP to
  assess community sentiment or rough consensus SHOULD treat the Forum as the
  primary record, and SHOULD NOT give weight to statements made only on Other
  Platforms that were not also posted on the Forum.

## Definition of Announcement

An "Announcement" is a public post, statement, release, or broadcast made by a
Covered Speaker on an Other Platform that communicates, for the first time on
that platform, any of the following in relation to Zcash, the Covered
Organization's Zcash-related work, or Zcash governance:

1. a release, deprecation, or end of support of software, a product, or a
   service, including wallet and node releases;
2. a network upgrade, protocol change, or change to a specification;
3. a security or privacy incident, vulnerability, or risk affecting Zcash users;
4. funding, grants, revenue, treasury, fundraising, or the receipt or use of
   funds from any Zcash Funding Source;
5. a partnership, integration, listing, delisting, or other material
   relationship with a third party;
6. a change of leadership, Executives, ownership, name, legal form, or
   jurisdiction of the Covered Organization, or significant layoffs,
   restructuring, or wind-down;
7. a roadmap, plan, or commitment, or a change to or abandonment of one;
8. a position of the Covered Organization on a ZIP, network upgrade,
   coinholder-amount voting round, grant proposal, or other governance matter;
9. a response to a dispute or allegation involving the Covered Organization or
   any of its Executives in connection with Zcash; or
10. an event organized or co-organized by the Covered Organization.

For an Executive, a post is an Announcement if it meets the above test and is
made in, or could reasonably be understood as being made in, their capacity as
an Executive. A post by an Executive that states a position on a matter listed
in item 8 is presumed to be made in that capacity unless the post clearly
states that it is a personal view.

The following are not Announcements:

* replies within an existing conversation that do not communicate any new
  matter listed above;
* reposts or quotations of content that has already been posted on the Forum;
* content that is a translation or restatement of an Announcement that has
  already been cross-posted, provided that the cross-post is linked;
* private or direct messages, and messages in private groups that are not
  public or semi-public channels; and
* security information that is under a responsible-disclosure embargo, until
  that embargo ends.

A post in a semi-public channel (such as a Discord or Telegram channel that
anyone may join) is public for the purposes of this definition.

<details>
<summary>

### Rationale for the definition of Announcement

</summary>

The definition is written as a list of subject matters, rather than a test of
importance, so that a third party can apply it without judging how significant
a post is. Item 8 is included because positions taken by funded organizations
on governance matters are exactly what the community most needs to see in one
place, and are most often stated only on X. The presumption that an Executive
speaks in their official capacity on governance matters prevents the
obligation from being avoided by speaking "personally" on a matter where the
Executive's role is the reason their view carries weight; a clear statement
that a post is personal rebuts it.
</details>

## Cross-Posting Requirement

Whenever a Covered Speaker makes an Announcement on an Other Platform, the
Covered Speaker, or the Covered Organization on their behalf, MUST cross-post
it to the Forum as specified in this section.

### Timing of cross-posts

The cross-post MUST be made within 24 hours of the Announcement first being
made on any Other Platform. Covered Speakers SHOULD make the cross-post at the
same time as, or before, the Announcement on Other Platforms.

For an Announcement relating to a security or privacy incident under item 3,
the cross-post MUST be made within 24 hours of the end of any applicable
responsible-disclosure embargo, or of the Announcement, whichever is later.

If the same Announcement is made on several Other Platforms, one cross-post is
sufficient, and it SHOULD link to each of them.

### Content of cross-posts

A cross-post MUST include the full text of the Announcement (every post, for a
thread), its attachments or working links to them, a link to the original on
each Other Platform, the name or handle of the Covered Speaker (and, for an
Executive, their role and organization), and the UTC date and time it was
first made. A link alone is not a cross-post.

For audio or video, the cross-post MUST include a link to the recording and a
written summary of each matter announced, and SHOULD include a transcript
where one exists. For an Announcement not in English, it MUST include the
original text and SHOULD include an English translation.

A cross-post MUST be made from a Forum account listed for the Covered Speaker
in the [Register of Covered Speakers], in the Announcements category under
[Forum Categories], or in a relevant existing thread (such as the thread for a
ZIP or grant) with a link from the Announcements category.

### Edits and deletions

If an Announcement is materially edited or deleted on an Other Platform, the
Covered Speaker MUST, within 24 hours, update the cross-post or add a reply to
it that states what was changed or that the original was deleted. A cross-post
MUST NOT be deleted, and MUST NOT be edited in a way that removes the original
text, except where required by law or to remove information whose publication
would cause harm (such as private keys or personal data published in error);
in that case the reason MUST be stated in the cross-post.

## Register of Covered Speakers

Each Covered Organization MUST publish on the Forum, and update within 7 days
of any change, a register of its Executives (by the name or handle under which
they act for it, with their role), its Official Accounts, and the Forum and
Other Platform accounts each of them uses for Announcements.

FPF, for ZCG, and the Key-Holder Organizations, for the Coinholder-Controlled
Fund, MUST each keep on the Forum a list of the Covered Organizations they
fund, linking to each register.

Nothing in this section requires anyone to disclose their legal name or any
information they have not already made public.

## Forum Categories

The operator of the Forum is requested to maintain a category for
Announcements by Covered Speakers (limited to cross-posts and replies), and a
category or thread for reports of non-compliance under [Enforcement].

If the operator is itself a Covered Organization, it MUST maintain these, MUST
publish its moderation policy, MUST NOT remove, hide, or edit a cross-post or
non-compliance report except for spam, illegal content, or doxxing (recording
each such action and its reason in a public moderation log), and MUST publish
a downloadable archive of the Announcements category at least quarterly.

## Compliance Reporting

Each Covered Organization that reports quarterly under ZIP 1014 [^zip-1014],
ZIP 1015 [^zip-1015-transparency], or ZIP 1016 MUST state in each quarterly
report whether it, its Executives, and its Official Accounts complied with
this ZIP, describe any non-compliance and how it was remedied, and link to its
register. Grantees SHOULD include the same statement in milestone reports.

## Enforcement

### Conditions of funding

From the Effective Date, FPF (for ZCG) and the Key-Holder Organizations (for the
Coinholder-Controlled Fund) MUST include compliance with this ZIP as a condition
in every grant agreement entered into, renewed, or amended with a Covered
Organization. Grant agreements in force at the Effective Date SHOULD be amended
to include it at the earliest opportunity, and in any case MUST include it on
renewal.

FPF, the ZCG Committee, and the Key-Holder Organizations are themselves bound by
this ZIP as Covered Organizations, and compliance with it forms part of their
Transparency and Accountability obligations under ZIP 1015 and ZIP 1016.

### Reporting of non-compliance

Any person MAY report an apparent failure to comply with this ZIP by posting in
the category or thread designated under [Forum Categories]. A report SHOULD
include a link to the Announcement and an archived copy of it.

### Notice and cure

When a report is made, or when FPF, the ZCG Committee, or a Key-Holder
Organization otherwise becomes aware of an apparent failure to comply, the body
that administers the relevant Zcash Funding Source MUST give the Covered
Organization notice on the Forum. The Covered Organization has 7 days from the
notice (the "cure period") to make the missing cross-post or correction, or to
explain on the Forum why the post in question is not an Announcement.

A failure that is cured within the cure period is a "cured failure". It is
recorded, but has no further consequence except as set out below.

### Substantial violation

A Covered Organization commits a "substantial violation" of this ZIP if:

* it does not cure a failure within the cure period; or
* it has three or more cured failures within any period of 12 months.

When a grantee commits a substantial violation:

* FPF and the Key-Holder Organizations, as applicable, MUST suspend any
  scheduled disbursement to it from the Zcash Funding Source they administer
  until the violation is cured, and in the case of repeated failures, until
  30 days have passed with no new failure;
* for a grant from the Coinholder-Controlled Fund, the Key-Holder Organizations
  SHOULD treat the violation as a contentious issue for which a further
  coinholder-amount voting round is held on whether funding should continue,
  as provided in ZIP 1016 [^zip-1016-cc]; and
* the ZCG Committee, and coinholders in any coinholder-amount voting round,
  SHOULD take the violation into account in any future funding decision for
  that Covered Organization.

When FPF, the ZCG Committee, or a Key-Holder Organization commits a substantial
violation, it constitutes a failure to meet its Transparency and Accountability
obligations under ZIP 1015 and ZIP 1016, and is subject to the enforcement
provisions of those ZIPs [^zip-1015-enforcement].

All notices, explanations, cures, suspensions, and resumptions of disbursement
under this section MUST be published on the Forum.

### Disputes over coverage

If a Covered Organization disputes that a post is an Announcement, the body that
administers the relevant Zcash Funding Source MUST decide the question and
publish its decision and reasons on the Forum. Where a Key-Holder Organization
or FPF is itself the Covered Organization concerned, it MUST NOT take part in
that decision; the decision is instead made by the remaining Key-Holder
Organizations, or, for FPF, by the ZCG Committee.

<details>
<summary>

### Rationale for enforcement through funding

</summary>

A Process ZIP cannot compel anyone to do anything except through the
obligations and processes that the community already controls. For funded
organizations, that is the grant agreement and the disbursement schedule.
Tying the obligation to existing grant agreements and quarterly reports adds
no new institution, and uses the same enforcement path that ZIP 1015 already
uses for its Transparency and Accountability obligations.

The notice-and-cure step keeps the consequence proportionate: a missed
cross-post is easy to fix, and an organization that fixes it promptly loses
nothing. Only an organization that refuses to fix a failure, or repeatedly
fails, has disbursements suspended, and even then only until it complies.
</details>

## Succession of the Zcash Town Square

The designation of the Zcash Town Square may be transferred to a successor
forum only by a ZIP.

If the Forum becomes unavailable for more than 7 consecutive days, Covered
Speakers MUST, for as long as it remains unavailable, publish cross-posts on
their own website or in a public GitHub repository, and MUST additionally
cross-post them to the Forum within 7 days after it becomes available again.

## Effective Date

This ZIP takes effect 30 days after its Status becomes Active (the "Effective
Date"). Covered Organizations MUST publish their registers within 30 days after
the Effective Date. Announcements made before the Effective Date are not
covered, but Covered Speakers are encouraged to comply voluntarily from the
time this ZIP becomes Active.


# Rationale

## Why the Forum

The Forum is already the venue that ZIP 0 and the funding ZIPs rely on in
practice. It is readable without an account, its threads are durable and
searchable, it supports long-form, threaded discussion, and it is not operated
for the purpose of maximizing engagement. Designating it formally makes the
existing practice explicit and gives the community one place to check.

## Why cross-posting rather than exclusivity

Reaching people where they are is important for Zcash adoption, and requiring
funded organizations to stop using X or other platforms would be both
unenforceable and harmful. Cross-posting preserves outreach on every platform
while ensuring that the Forum holds a complete record. Covered Speakers are
encouraged, but not required, to post on the Forum first.

## Why 24 hours

A short window keeps the Forum record current enough to be useful for
discussion of the Announcement, while allowing for time zones and for
Announcements made outside working hours. A longer window would allow
discussion to form elsewhere before the Forum sees the Announcement.

## Why Executives and Official Accounts

This ZIP covers the Executives of funded organizations because they speak
for those organizations. Official Accounts
are added because organizations most often announce through their own brand
accounts, and leaving them out would leave the largest source of
announcements uncovered. Ordinary employees and contributors are not covered,
to keep the obligation focused and administrable.

## Why the Key-Holder Organizations, FPF, and ZCG Committee are covered

These bodies administer Zcash Funding Sources on the community's behalf.
Their Announcements about funding and governance are at least as important to
the community as those of grantees, and they are covered whether or not they
themselves receive grants.

## Why include an obligation on the Forum operator

Designating one venue as official gives its operator influence over what is
seen. If the operator is a Covered Organization, the moderation-log, archive,
and non-removal requirements limit the risk that this influence is used to
suppress Announcements or reports of non-compliance. The Succession section
lets the community move the designation if the Forum ceases to serve it.

## Alternatives considered

* A voluntary norm: already the informal expectation; it has not prevented
  announcements being made only on X.
* Requiring Forum-first publication: stronger, but harder to verify and
  more disruptive to coordinated launches with partners. It is recommended
  instead of required.
* Covering only Official Accounts: would miss governance positions stated
  by Executives personally, which is the case this ZIP most needs to cover.
* A de minimis exemption for small grants: not included in this draft,
  so that the rule matches its stated scope of "any organization that receives
  funding". See [Open questions].

## Open questions

The following questions are left open for discussion while this ZIP is a
Draft:

* Should individual grantees, or grants below some threshold, be exempt or
  subject to a lighter obligation?
* Should grants made by Covered Organizations from their own reserves (for
  example reserves originally derived from the earlier Dev Fund under ZIP 1014)
  be treated as a Zcash Funding Source?
* Is 12 months the right length for the Covered Period after funding ends?
* Should ZIP Editors, in their role as Editors, be asked to post decisions on
  ZIP Status changes to the Forum? This would require an update to ZIP 0.


# References

[^BCP14]: [Information on BCP 14, "RFC 2119: Key words for use in RFCs to Indicate Requirement Levels" and "RFC 8174: Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words"](https://www.rfc-editor.org/info/bcp14)

[^zip-0000]: [ZIP 0: ZIP Process](zip-0000.rst)

[^zip-0207]: [ZIP 207: Funding Streams](zip-0207.rst)

[^zip-0259]: [ZIP 259: Deployment of the NU7 Network Upgrade](zip-0259.md)

[^zip-0271]: [ZIP 271: Deferred Dev Fund Lockbox Disbursement](zip-0271.md)

[^zip-1014]: [ZIP 1014: Establishing a Dev Fund for ECC, ZF, and Major Grants](zip-1014.rst)

[^zip-1015]: [ZIP 1015: Block Subsidy Allocation for Non-Direct Development Funding](zip-1015.rst)

[^zip-1015-zcg]: [ZIP 1015: Block Subsidy Allocation for Non-Direct Development Funding, Zcash Community Grants](zip-1015.rst#zcash-community-grants-zcg)

[^zip-1015-transparency]: [ZIP 1015: Block Subsidy Allocation for Non-Direct Development Funding, Transparency and Accountability](zip-1015.rst#transparency-and-accountability)

[^zip-1015-enforcement]: [ZIP 1015: Block Subsidy Allocation for Non-Direct Development Funding, Enforcement](zip-1015.rst#enforcement)

[^zip-1016]: [ZIP 1016: Community and Coinholder Funding Model](zip-1016.md)

[^zip-1016-cc]: [ZIP 1016: Community and Coinholder Funding Model, Disbursement process](zip-1016.md#disbursement-process)

[^zip-2001]: [ZIP 2001: Lockbox Funding Streams](zip-2001.rst)
