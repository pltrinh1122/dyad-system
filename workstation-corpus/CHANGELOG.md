# Host change log (Rule-8)

One row per reversible or destructive host action, written in the same d-work. Read-only
actions are not logged. `actor` is `operator` or `agent` — the party whose hands executed
it; a divergent credential is named in `outcome`.

| date | d-work | class | action | undo | outcome | actor |
|------|--------|-------|--------|------|---------|-------|
| 2026-09-29 | #182 | reversible | `gh auth switch --user pltrinh1122` — make `pltrinh1122` the active `gh` account for github.com on this host | `gh auth switch --user asg-peter` | `✓ Switched active account for github.com to pltrinh1122`; `gh auth status` then shows `pltrinh1122` active and `asg-peter` logged in but inactive, and `gh pr list` on this repo returns instead of refusing with `must be a collaborator` (the refusal that forced #178 to merge locally) | agent |
| 2026-10-09 | #256 | reversible | append `.claude/` to `.git/info/exclude` — git's per-checkout, never-tracked exclude file — so `package.py` `pushed_refs`' dirty check stops seeing the harness's delegated-fork worktree at `.claude/worktrees/` and pushes can proceed (plan #256 revision 2 step 1) | restore the file to its five seeded comment lines, sha256 `6671fe83b7a07c8932ee89164d1f2793b2318058eb8b98dc5c06ee0a5a3b0ec1`; a copy was taken before the edit | `git status --porcelain --untracked-files=normal` went from `?? .claude/` to empty, and the push of `main` that had been refused with *the working tree has changes the push does not carry (.claude/)* then succeeded, `39fa1bd..355c6b6`. In force at the time of writing: it is reverted once `.gitignore` on `main` carries the line (PR #359), and the revert gets its own row | agent |
