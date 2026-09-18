One line per finding: `<file>:L<line>: <tag> <what to cut>. <what replaces it>.`

Tags:
- `delete:` dead code, unused flexibility, a speculative feature. Replacement: nothing.
- `stdlib:` a hand-rolled thing the standard library already does. Name the function.
- `native:` a dependency or code doing what the platform already does. Name the feature.
- `yagni:` an abstraction with one implementation, a config nobody sets, a layer with one caller.
- `shrink:` the same logic, fewer lines. Show the shorter form.

Ends with `net: -<N> lines possible.` If there is nothing to cut: `Lean already. Ship.`

Scope: over-engineering and complexity only (`verifiable-code.md` p7's ladder). Correctness,
security and performance findings route to an ordinary review pass, not this one. A single
runnable check (p7's floor) is never a finding here.
