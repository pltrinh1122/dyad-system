<!-- The key of a keyed piece (rules/chronicle.md §1, §2): published beside it as `<piece>.key.md` and named by the
     piece's `key:` header line. One line per paragraph of the piece, in order. A line names its paragraph by `¶`, the
     paragraph's number counted from 1 after the header, and the paragraph's first words exactly as the piece has them;
     then ` | ` and its layer:
     - `record <citation>[; <citation>]` — a record passage, each citation one of the four forms of §1
       (`path:`, `prov:#<row>/<entry>`, `repo:<owner>/<repo>@<40-hex sha>:<path>`, `commit:<owner>/<repo>@<40-hex sha>`);
       quotes in the passage are exact, so a search of the cited repo finds them;
     - `fiction persona` — the persona's interior, based on a real-life model;
     - `fiction composites: <Name>, <Name>` — a passage telling declared composites, each in the form's character list.
     The piece's prose holds no footnote, no `*(fiction)*` marker and no `fiction:` line. -->

¶1 <first words of paragraph 1> | record path:<repo-relative path in this repo>
¶2 <first words of paragraph 2> | record prov:#<row id>/<entry n>; commit:<owner>/<repo>@<40-hex commit sha>
¶3 <first words of paragraph 3> | fiction persona
¶4 <first words of paragraph 4> | fiction composites: <Name>
