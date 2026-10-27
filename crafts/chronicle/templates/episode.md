title: <the episode's title>
season: <season number, e.g. 1>
episode: <episode number within the season, e.g. 0>
time: present, <YYYY-MM-DD>
repos: none
fiction: persona, based on a real-life model

<!-- `time:` is `present, <YYYY-MM-DD>` or `past, <YYYY-MM-DD>` (rules/chronicle.md §4). `repos:` is `none`, or
     space-separated `<owner>/<repo>=public|private`, one per repo a `repo:` or `commit:` citation below names (§5). Every
     event below carries a footnote; nothing is told that no footnote holds (§1). `fiction:` stays only while the text
     holds a passage marked `*(fiction)*`: the persona's character, inner life and daemons, uncited (§2). -->

<The body: the events, in story form — order, viewpoint and emphasis are the teller's; each fact cites.>[^1] <The
Operator's own words about the world around the work, quoted verbatim.>[^2] <A moment from an earlier repo.>[^3] <A commit's own message.>[^4]

*(fiction)* <The persona's interior — character, inner life, daemons — written as fiction based on a real-life
model; no footnote.>

[^1]: path:<repo-relative path in this repo, e.g. agent-corpus/d-work/rows/1.md>
[^2]: prov:#<row id>/<entry n>
[^3]: repo:<owner>/<repo>@<40-hex commit sha>:<path in that repo>
[^4]: commit:<owner>/<repo>@<40-hex commit sha>
