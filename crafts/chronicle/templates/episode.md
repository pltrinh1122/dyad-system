title: <the episode's title>
season: <season number, e.g. 1>
episode: <episode number within the season, e.g. 0>
time: present, <YYYY-MM-DD>
repos: none
fiction: persona, based on a real-life model; composites: <Name>

<!-- `time:` is `present, <YYYY-MM-DD>` or `past, <YYYY-MM-DD>` (rules/serial.md §3). `repos:` is `none`, or
     space-separated `<owner>/<repo>=public|private`, one per repo a `repo:` or `commit:` citation below names (rules/chronicle.md §4). Every
     event below carries a footnote; nothing is told that no footnote holds (rules/chronicle.md §1). `fiction:` stays only while the text
     holds a passage marked `*(fiction)*`: its parts, separated by `;`, are `persona, based on a real-life model` and
     `composites: <Name>, <Name>`, every declared composite (a character drawn from more than one real person and from no
     single one) appearing only in marked passages, uncited (rules/chronicle.md §2). -->

<The body: the events, in story form — order, viewpoint and emphasis are the teller's; each fact cites.>[^1] <The
Operator's own words about the world around the work, quoted verbatim.>[^2] <A moment from an earlier repo.>[^3] <A commit's own message.>[^4]

*(fiction)* <The persona's interior — character, inner life, daemons — or a scene with a declared composite, <Name>,
written as fiction based on real-life models; no footnote.>

[^1]: path:<repo-relative path in this repo, e.g. agent-corpus/d-work/rows/1.md>
[^2]: prov:#<row id>/<entry n>
[^3]: repo:<owner>/<repo>@<40-hex commit sha>:<path in that repo>
[^4]: commit:<owner>/<repo>@<40-hex commit sha>
