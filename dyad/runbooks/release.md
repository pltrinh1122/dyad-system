# Run-book: release (when a change set warrants a release, and which number) — play-book `dyad/playbooks/release.md`, #493
# sections: Changes, Number

A core run-book (package, `dyad/runbooks/`; agent zone): the release play-book's two steps as `dyad-cmd` blocks,
both read-only, run by either party through the core runner from the git root of the authoring repository, with
its tags fetched (an unfit clone reads every craft as untagged; `dyad bootstrap` fetches them, #474). `number`
reads its arguments from the environment: `CRAFT` (`dyad-operator`, a Tended craft's name, or `bundle`) and
`CLASS` (one of the play-book's five classes, as `critical-fix`, `capability`, `enhancement`, `breaking`,
`maintenance`).

```text
dyad runbook run release changes
CRAFT=dyad-operator CLASS=capability dyad runbook run release number
```

## Changes
What changed under each craft's root since that craft's last release tag: the commit count and the d-works its
commit messages cite (Rule-3: a commit claims its d-work as `d-work #<id>`), then the bundle's last tag beside
`BUNDLE.md`'s version. The seat classifies from this list, one d-work at a time, never from memory (Rule-13).
```dyad-cmd
name: changes
class: read-only
role: any
undo: none
postcondition: none
scope: repo history and tags (read)

for c in dyad-operator $(ls crafts 2>/dev/null | grep -v '\.md$'); do r=dyad; [ "$c" = dyad-operator ] || r="crafts/$c"; [ -f "$r/VERSION" ] || continue; t=$(git tag -l "$c-v[0-9]*" --sort=-v:refname | head -1); n=$(git rev-list --count ${t:+$t..}HEAD -- "$r"); ids=$(git log --format='%s%n%b' ${t:+$t..}HEAD -- "$r" | grep -o 'd-work #[0-9]*' | sort -u | tr '\n' ' '); printf '%s since %s (VERSION %s): %s commits; %s\n' "$c" "${t:-no tag}" "$(cat "$r/VERSION")" "$n" "${ids:-no d-work cited}"; done; t=$(git tag -l 'v[0-9]*' --sort=-v:refname | head -1); printf 'bundle since %s (BUNDLE.md %s)\n' "${t:-no tag}" "$(sed -n 's/^version: *//p' BUNDLE.md 2>/dev/null)"
```

## Number
The tag a class implies for one craft or the bundle, from its last release tag (the play-book's mapping:
critical fix → patch; new capability or significant enhancement → minor; breaking → major, or minor while the
major is 0; maintenance → no release). Exit 2 on an unknown class.
```dyad-cmd
name: number
class: read-only
role: any
undo: none
postcondition: none
scope: repo tags (read)

: "${CRAFT:?dyad-operator, a craft or bundle}" "${CLASS:?critical-fix, capability, enhancement, breaking or maintenance}"; case "$CRAFT" in bundle) p=v;; *) p="$CRAFT-v";; esac; t=$(git tag -l "${p}[0-9]*" --sort=-v:refname | head -1); v=${t#"$p"}; v=${v:-0.0.0}; M=${v%%.*}; r=${v#*.}; m=${r%%.*}; P=${r#*.}; case "$CLASS" in critical-fix) P=$((P+1));; capability|enhancement) m=$((m+1)); P=0;; breaking) if [ "$M" = 0 ]; then m=$((m+1)); P=0; else M=$((M+1)); m=0; P=0; fi;; maintenance) echo "maintenance: no release; the change set waits (last ${t:-none})"; exit 0;; *) echo "unknown CLASS $CLASS"; exit 2;; esac; echo "${p}${M}.${m}.${P} (last ${t:-none}, class $CLASS)"
```
