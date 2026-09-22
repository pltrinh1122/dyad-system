# Falsification record — Stage 2 scope: `CraftCliTests` fixture cost vs `FenceTests`/`guards.agent` real-git cost (d-work #110)

**Claim (scoping #108's own deferred "Stage 2"):** the two costs #107 named and #108 left
untouched — `test_craft.CraftCliTests`'s per-test real scratch-repo rebuild, and
`guards/agent/test_rows.py`'s (and `guards.agent`'s) real-git fence tests — should both be
remediated the same way #108 remediated `test_package.py`: separate unit tests (mocked) from
integration tests (real subprocess/git).

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 1 | Mocking `rows.py`'s own git layer (the option #108's plan literally named for `FenceTests`) is the right Stage-2 move. | Refuted as the right move | `rows.py`'s `check_commit`/`check_range`/`check_id_collisions` are nothing but real `git` plumbing calls (`diff-tree`, `show`, `rev-list --parents`) — this **is** the main fence Rule-2 and Rule-3 name by name as their mechanical enforcement. A mocked git layer could keep these tests green while the guard's actual parsing of real `git diff-tree --name-status` output silently diverges. Measured cost of leaving it alone: 6.09s for 25 tests in this file alone (~244ms/test, ordinary `git init`+commit subprocess overhead) — not disproportionate to the risk of weakening the one fence a self-ratification rule depends on. Not pursued. |
| 2 | Labeling `FenceTests`/`guards.agent` as integration and stopping there, no code change, fully answers Stage 2 for this half. | Survives, scoped | Zero-risk and worth doing as documentation (one line, matching the comment style #108 already added to `test_package.py`'s two remaining integration-flavored tests), but on its own leaves the profiled cost (`guards.agent`: 12.64s in #107's own measurement) unaddressed — insufficient alone. |
| 3 | `CraftCliTests`'s cost (measured here: 24.08s for 15 tests, ~1.6s/test) is inherent to what it tests and cannot be cut without weakening it. | Refuted | `setUp()` (`dyad/tests/test_craft.py:44-45`) calls `scratch()` fresh for *every* test method; `scratch()` itself runs `package.py install` as a real subprocess into a brand-new `git init` (`dyad/tests/test_craft.py:24-27`). Every test in the class installs the identical core craft into an identical, disposable scratch repo before doing anything test-specific — the repeated *install* is redundant, not essential. |
| 4 | A class-scoped install, copied per test via `shutil.copytree` (no subprocess), preserves what these tests actually test. | Survives | Several tests deliberately mutate `self.dst` (e.g. `test_install_refuses_modified_tree_unless_forced`); `shutil.copytree` gives every test its own independent directory and its own independent `.git`, byte-identical to what `scratch()` produces today, so no test's mutations leak to another. Property 5 (one code path, deterministic, idempotent install) is still exercised for real, once, at class setup — never mocked; only the redundant re-run (14 of 15 installs) is removed. |
| 5 | Overlap (Rule-16): presence read before writing the plan. | Checked, none found | `dev-main.md`, `web-sysadmin-scope.md`, `web-sysarch-adh151.md`, `web-sysarch.md` — all stale, none declaring `test_craft.py`, `test_rows.py`, or `rows.py`. This session has no presence file of its own yet (out of scope here). The one live overlap this window surfaced — a peer session's own `#109` (`dyad/VERSION`, `BUNDLE.md`) — is unrelated to these two test files and is already merged, `main` confirmed green at `8f012e0`. |

**Path (Rule-10):** two independent moves, not one. (a) `CraftCliTests`: `setUpClass`-build one
template scratch repo (real `package.py install`, once), `setUp` copies it per test via
`shutil.copytree` — real git, real install, no mock, most of the redundant subprocess cost removed.
(b) `FenceTests`/`guards.agent` generally: no code change; add the one-line integration-by-necessity
docstring note attack 2 names.

**Strongest counter:** doing (a)'s code now, under this same scoping plan-`Y`, risks the exact
failure #108 just caused — a green `check --pr` on the branch, a red `infra/bundle` guard caught
only by a peer session after merge (its own d-work #109, already closed) — if "scope it" quietly
becomes "and also ship it" under momentum.

**Reconciliation:** the counter is about sequencing, not substance — it does not dispute that (a)
is the right fix, only when to authorize writing it. This d-work's own mutation is scoping only (no
test or guard code touched); implementing (a), with a full `check --guards` run (including
`infra/bundle` explicitly, closing the exact gap #108 left open) and a measured before/after, is a
follow-on plan-`Y` this record's disposition would authorize separately.

Disposition: see ledger #110.
