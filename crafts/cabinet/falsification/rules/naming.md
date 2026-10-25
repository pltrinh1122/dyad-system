# Falsification record — "a seat name carries the Operator's mental model from its tokens alone" (`../../rules/naming.md`; dyad-system #383, #369 C9)

**Claim (Operator's, provenance #366 entry 1, #369 entries 8–12):** the session name serves more than
identification — it assists the Operator's mental model; the seats are `program, counsel, audit, engineer,
distribute, operate`. The form `<function>[-<topic>]-<hp>` is plan #369 revision 10's survivor after revisions
6, 8 and 9; the attacks below are on the rule as written and on where the form lives.

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 1 | **The form admits a name that reads two ways**: `program-alice-59cec502` is a desk by the reading rule and a member pair's leader by §1. | **Refuted by construction** | For `program` the middle token is the Operator's handle, never a topic (§1), because the leader keeps no desk (it accretes nothing, `organization.md` §4), so no `program-<topic>` seat exists to collide with; `seats.py` reads every `program-…` name as a leader (its test says so) and the mandates table names which Operator's. |
| 2 | **The form belongs in the syseng craft's naming table** (plan #369 revision 4, attack 4: "the pattern's row goes in `naming_rules.txt`, one line, checkable by `naming.py`"). | **Confirmed as the plan's text; refuted as a mechanism** | A `kind:` row there selects a path by glob and every selecting native kind must accept it (`crafts/syseng/rules/naming.md`, Contributed kind widening): a row for `<instance>/d-work/sessions/<seat>.md` would reject the 70-odd presence files from before the form (`cab-2.md`, `cos-1.md`, `unnamed-*.md`, `ds-cabinet-term-1.md`, read at `main` ed5e10c), which Rule-16 keeps as history, or need an `allow:` line per file; a contributed `naming_contrib.txt` kind can only *widen* a native kind and so cannot express the form at all. Survivor: the form is this craft's own data (`guards/seats_rules.txt`), read by its advisory guard and by the core's `dyad session name`; the syseng table gains no line. A departure from revision 4's one-line sentence — less mutation, not more — stated for the Operator in the completion evidence. |
| 3 | **Eight hex of a session id collide across holders.** | **Survives as accepted** | 2³² handles per function; a collision would be two presence files of one name, which the store would show as one holder rewriting the other's (`writer` line, Rule-16's own warning). The handle is a handle (#295), never identity. |
| 4 | **`unnamed-<hex>` names are a defect of the form.** | **Refuted** | They are what a bare `dyad session touch` writes under no `DYAD_SESSION` — the store's default, which the form makes visible in one summary line (§4) and which this seat produced once itself, at its registration, from a `--help` the verb does not take (#372's evidence). The fix is the touch's (#311–#313), not the form's. |
| 5 | **The session title duplicates the name.** | **Refuted** | The title adds the kernel, the system's handle and the current topic, which the name must not carry (a name is stable, a topic moves); `dyad session name` prints both so they never drift apart (§3). |
| 6 | Easy agreement: the form was falsified four times already. | **Pushed to 2** | 2 moved the form out of the syseng table the plan named. |

**Verdict:** the claim **survives** — the tokens carry function, board and holder (§2) — with the form living in
this craft's data rather than the syseng table (2) and every `program-…` name a leader by construction (1).

**Survivor:** `../../rules/naming.md` as written; `../../guards/seats_rules.txt` as the one place the form is a regex.

**Limits.** No multi-Operator tree exists yet to read `program-<operator>-<hp>` in; the collision bound (3) is
arithmetic, not observation.

Disposition: see ledger #383 (accreted under #369; its Done rides that mandate's Done disposition).
