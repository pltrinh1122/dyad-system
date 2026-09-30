# Host change log (Rule-8)

One row per reversible or destructive host action, written in the same d-work. Read-only
actions are not logged. `actor` is `operator` or `agent` — the party whose hands executed
it; a divergent credential is named in `outcome`.

| date | d-work | class | action | undo | outcome | actor |
|------|--------|-------|--------|------|---------|-------|
| 2026-09-29 | #182 | reversible | `gh auth switch --user pltrinh1122` — make `pltrinh1122` the active `gh` account for github.com on this host | `gh auth switch --user asg-peter` | `✓ Switched active account for github.com to pltrinh1122`; `gh auth status` then shows `pltrinh1122` active and `asg-peter` logged in but inactive, and `gh pr list` on this repo returns instead of refusing with `must be a collaborator` (the refusal that forced #178 to merge locally) | agent |
