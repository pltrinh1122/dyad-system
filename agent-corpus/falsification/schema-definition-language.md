# Falsification record — schema definition language for the syseng craft (d-work #30)

**Claim (operator prompt, 2026-09-16):** a four-step flow — (1) the d-work entity mapped to a
schema, hand-authored; (2) the schema verified by code; (3a) mechanically transformed to a
surface; (3b) injected into a downstream prompt — improves the syseng craft, and pydantic should
be the schema definition language, evaluated against zod.

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 1 | The flow requires new infrastructure: no d-work schema exists today. | Refuted | Steps 1–3a already exist under other names: `dyadlib.Row`/`FIELDS`/`TRANSITIONS` (model), `parse_row_file` + `rows.py check_package`/`check_transaction` + `INVARIANTS` (verification), `rows.py describe()` consumed by the entities projector (surface). `crafts/sysarch/rules/guards.md` p3 already calls `FIELDS` "the schema constant." The real gap is 3b and a machine-readable serialization. |
| 2 | "Schema verified by code" (step 2) is one check a schema library would provide. | Refuted | It conflates three: well-formedness (exists, `dyadlib.CONTRACT`), instance conformance (exists, `check_package`), and fidelity to the Rule prose that owns the entity — `guards.md`'s own Inference-stated section already names this last one as inference, and no schema library closes it: a restatement cannot verify its original (Rule-6, master record). |
| 3 | Step 3b (schema constrains the Agent's own later prompt) is safe because it is mechanical. | Confirmed as a gap | Same party authors the schema (step 1) and is later constrained by it (3b), with no disposal between — Rule-2's proposer/disposer split does not see a schema as a ratification event today. Survivor: the schema is corpus (agent zone, changed only by a disposed d-work PR, generated for injection only from committed corpus — never from uncommitted working-tree code), so 3b injects ratified corpus, the pattern the memory cache already uses. |
| 4 | The schema only formalizes validation and projection; it doesn't touch storage. | Survives, scoped | A schema library's natural next step is JSON storage, which re-serializes the whole object on every edit — dropping the line-granular merge and the append-only fence Rule-16's store relies on, and the fenced-body defence Rule-7 property 1 relies on. Not a defect of either candidate; a risk of adopting the flow that must be named if it is adopted. |
| 5 | zod is a legitimate candidate, symmetric with pydantic. | Refuted | Rule-14 property 2's kernel has no Node row at all (`dyad/infrastructure/INFRASTRUCTURE.md`); property 3 requires every guard on the kernel alone, including the evidence-block path Rule-2's Binding reads. zod means either the guards become Node code (the kernel gains a runtime) or the schema is authored in TS and re-parsed in Python — two definitions of one model, which Rule-6 and `crafts/sysarch/rules/projection.md` p1 both forbid. `crafts/syseng/rules/imports.md` p3 ("kernel ecosystem first") settles it before any merit comparison; generating Python from zod fails the same property plus Rule-11 p6 (generated files are never tracked). |
| 6 | pydantic is unconditionally the right import: it clears `import-licenses` and `import-support`. | Survives, scoped | It clears the preferences, but `pydantic-core` is a compiled Rust wheel; putting it on the kernel-only path means `dyad check --evidence` — stdlib-only today — stops reproducing on a bare kernel (Rule-14 p3). The gain (`model_json_schema()`) is one method; the cost is the reproducibility of the merge evidence the Operator re-runs to verify a merge. Conditional: if the Operator disposes that the kernel-only path may require a `pip install`, this attack is refuted outright and pydantic is the right answer. |

**Path (Rule-10):** neither library — author a small stdlib JSON Schema emitter in `dyadlib` over
the guard contract that already exists (`FIELDS` + `describe()`); it serves 3a and 3b from one
declaration, adds no manifest row, no kernel change, no new zone, and stays the seam to swap
behind if the Operator later disposes otherwise.
**Strongest counter:** this inverts Rule-13 p1 — "import over author" exists precisely so a fit
candidate (pydantic) is taken, not re-implemented.
**Reconciliation:** `crafts/syseng/rules/imports.md` p1 conditions import on meeting the criteria,
and Rule-14 p3 is part of the criteria the kernel-only path imposes, not an afterthought; pydantic
fails it only as long as that path must run on a bare kernel — a disposition the Operator, not
this record, makes. If disposed the other way, this record's own path is the wrong one.

**Amendment — d-work #31 (2026-09-16):** the Operator disposed attack 6's conditional directly:
pydantic is now Rule-14 kernel (`dyad/rules/RULE-14-system-infrastructure.md` property 2), so the
kernel-only-path cost attack 6 named no longer applies. This record's own recommended path (the
stdlib emitter) is superseded; pydantic is the live recommendation for whichever future d-work
writes the schema code. See `dyad/falsification/rules/rule-14-system-infrastructure.md`, amendment
d-work #31, for the falsification of the kernel-membership claim itself.

Disposition: see ledger #30.
