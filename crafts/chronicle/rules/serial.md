# Chronicle: the serial (chronicle craft, Tended rule; a form section)

The serial's section of the chronicle craft: a dyad system's journey told in instalments, as a story — characters,
flaws, conflicts, climax and release. Read beside the core, `chronicle.md`, which binds every form: anchoring and
the fiction layer (§1, §2), flaws and the real Operator (§3), the private-repo flag (§4), roles (§5), publication
and change (§6). This section narrows the core, never loosens it. Terms: `../vocabulary/CRAFT.md`. Record:
`../falsification/rules/chronicle.md`, amendment #521 (the decision records DR-1 to DR-9 it cites). The serial's
terms come from three sources, each named in the vocabulary: web serials for the form, prose publishing for
editing, and television only where prose has no term (DR-3).

## 1. Episodes
The serial's pieces are **episodes**, files under `<site>/episodes/` seeded from `../templates/episode.md`. An
episode's header names its `title`, `season`, `episode` number, `time` (§3) and `repos` (the core's §4), and carries
`fiction:` whenever its text holds the fiction layer (the core's §2).

## 2. Characters
The main character is the Operator's persona (the core's §2), and the arc is the persona's growth in the
Dyad-Operator craft, readable in the record: the preferences set, the corrections given, the amends that turned
plans, the Rules made. The other characters are the parties and the seats of the system (the cos, counsel, audit,
engineer, distribute, operate, communicate, and any seat the organization opens), their flaws as the core's §3 says.
The Operator's role in the serial is the **showrunner**: the final creative say over the whole series (the core's §5).

## 3. Time and interleave
Every episode's header carries its time: `time: present, <YYYY-MM-DD>` or `time: past, <YYYY-MM-DD>` — the present
thread is the system as it grows now, the past thread the back-story in the earlier repos. The season arc sets the
**interleave**: which past arc sits beside which present one (a natural pairing is a present conflict beside the
past moment that set it up).

## 4. The serial's documents
- **Series bible** — what holds for the whole serial: its premise, its characters, its tone, its style guide.
- **Season arc** — one season's arcs, its interleave, the repos it has read and the ones it could not reach.
- **Episode outline** and its **beat sheet** — one episode's beats, each with the citation that holds it, labelled
  with the structure's steps (§5).
- **Continuity bible** — the setups and payoffs the serial has made, and which episode holds each.
- **Canon** — the published episodes (the core's §6).
- **Buffer** — two episodes drafted and not yet published, so a payoff can be fixed before its setup is canon.
Changes flow down this list freely — bible, season arc, outlines, drafts — and up only on the Operator's `Y` (the
core's §6).

## 5. Structure: the Story Circle, as a lens
The serial labels its beats with the Story Circle's eight steps (you, need, go, search, find, take, return, change),
at the scale of an episode and of a season. It is a lens on the record and never a mould: a step the record does
not hold is reported as a gap, never written to fill the shape, and a missing "take" (the price paid) in an episode
is a finding. An episode with no conflict in it may use a shape without one.

## 6. Rolling wave
The series bible and the season arc are approved by the Operator before any episode of that season is drafted. The
next one or two episodes are outlined in detail and the rest one line each; each outline is filled in as its
episode comes up, because the present thread is still happening. An episode the season arc does not cover waits for
a season arc that covers it. Each episode is approved at its publication (the core's §6).

## 7. The guard
`../guards/episodes.py` reads every episode under `<site>/episodes/*.md` (`DYAD_SITE`, default `site`; an absent
store prints one `skip` line). Beyond the core's checks (the core's §8), it fails an episode whose header lacks a key
(`title`, `season`, `episode`, `time`, `repos`), whose `season` or `episode` is not a number, whose `time:` line is
not `present|past, YYYY-MM-DD`, or which cites nothing. The documents of §4 are checked by inference, at the
questions that approve them.
