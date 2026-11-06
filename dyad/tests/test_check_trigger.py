"""The check-trigger criterion (`dyad/dmc/check-trigger.jsonld`, d-work #618, home Rule-14 property 3): every check is
classed by the inputs it reads (`dyadlib.CHECK_INPUTS`), every input names a trigger (`dyadlib.INPUT_TRIGGERS`), and
every trigger named is delivered — in a workflow's `on:` block and steps, or in `dyad board resume`'s stall lines.
The workflows are read as text, as `infra/manifest` scans them; no YAML library enters the manifest (plan Q2)."""
import inspect, re, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import dyadlib

PKG = dyadlib.PKG
REPO = PKG.parent
WORKFLOWS = REPO / ".github" / "workflows"


def registered_labels() -> set[str]:
    """`<group>/<entity>` of every guard the registry discovers (`dyad check --list`)."""
    out = set()
    for py in dyadlib.guard_files(PKG):
        _, group, entity = dyadlib.guard_key(py, PKG)
        out.add(f"{group}/{entity}")
    return out


def on_block(text: str) -> list[str]:
    """The lines of a workflow's top-level `on:` block."""
    lines, out, inside = text.splitlines(), [], False
    for line in lines:
        if re.match(r"^on:\s*(#.*)?$", line):
            inside = True; continue
        if inside and line and not line[0].isspace() and not line.startswith("#"):
            break
        if inside:
            out.append(line)
    return out


def push_filter(text: str, key: str) -> list[str] | None:
    """The `push:` trigger's `paths:` or `paths-ignore:` list (flow form, `[a, b]`), None when the block has none;
    [] means a push trigger with no such list."""
    block = on_block(text)
    if not any(re.match(r"^\s+push:\s*$", l) for l in block):
        return None
    for l in block:
        m = re.match(rf"^\s+{re.escape(key)}:\s*\[(.*)\]", l)
        if m:
            return [x.strip().strip("'\"") for x in m.group(1).split(",") if x.strip()]
    return []


def run_lines(text: str) -> list[str]:
    """Every shell line of the steps: a `run:` value, or the indented block under `run: |`."""
    out, lines, i = [], text.splitlines(), 0
    while i < len(lines):
        m = re.match(r"^(\s*)(?:- )?run:\s*(.*)$", lines[i])
        if m:
            if m.group(2).strip() in ("|", ">"):
                indent = len(m.group(1))
                i += 1
                while i < len(lines) and (not lines[i].strip() or len(lines[i]) - len(lines[i].lstrip()) > indent):
                    out.append(lines[i].strip()); i += 1
                continue
            out.append(m.group(2).strip())
        i += 1
    return out


def ignored(path: str, patterns: list[str]) -> bool:
    return any(path.startswith(p.removesuffix("**").removesuffix("/")) for p in patterns)


def flow(name: str) -> str:
    p = WORKFLOWS / name
    return p.read_text() if p.is_file() else ""


def delivered() -> dict[str, list[str]]:
    """{input: [the reasons its trigger is not delivered]} for every input of `INPUT_TRIGGERS`; an input this test has
    no reader for is undelivered by construction, so a new input needs a reading here."""
    sweep, auto = flow("dyad-sweep.yml"), flow("dyad-automaton.yml")
    inst, events = dyadlib.instance_rel(REPO) or "agent-corpus", dyadlib.events_rel(REPO) or "workstation-corpus/runbooks/events"
    def full_sweep() -> list[str]:
        why = []
        if not any("automaton sweep" in l and "--stores" not in l for l in run_lines(sweep)):
            why.append("dyad-sweep.yml runs no full `automaton sweep`")
        ign = push_filter(sweep, "paths-ignore")
        if ign is None:
            why.append("dyad-sweep.yml has no push trigger (a merge made outside the automaton, P2)")
        elif ignored("dyad/scripts/package.py", ign):
            why.append("dyad-sweep.yml's push ignores code")
        if not any(re.search(r"gh workflow run dyad-sweep\.yml", l) for l in run_lines(auto)):
            why.append("dyad-automaton.yml dispatches no full sweep after a landed cut (P1)")
        return why
    def stores_on(path: str, what: str) -> list[str]:
        why = []
        if not any("automaton sweep --stores" in l for l in run_lines(auto)):
            why.append("dyad-automaton.yml runs no `automaton sweep --stores`")
        paths = push_filter(auto, "paths")
        if paths is None or (paths and not any(path.startswith(p.removesuffix("**").removesuffix("/")) for p in paths)):
            why.append(f"dyad-automaton.yml's push paths miss {what} ({path})")
        return why
    def resume() -> list[str]:
        bd = dyadlib.load_guard("agent", "board")
        am = dyadlib.load_module(PKG / "scripts" / "automaton.py", "automaton")
        why = [] if "stall_block(" in inspect.getsource(bd.resume_lines) else ["`board resume` prints no stall lines"]
        src = inspect.getsource(am.stall_lines)
        for part in (k for k, v in dyadlib.CHECK_INPUTS.items() if k in dyadlib.SWEEP_PARTS and dyadlib.ABSENCE in v):
            call = {"hygiene": r"hygiene_mod\.hygiene\b", "inflight": r"hygiene_mod\.inflight"}.get(part, rf"\b{part}\b")
            if not re.search(call, src):                  # called, or submitted to a pool (`sweep_ci`)
                why.append(f"`stall_lines` reads no {part}")
        return why
    readers = {dyadlib.CODE: full_sweep, dyadlib.WORLD: full_sweep, dyadlib.ABSENCE: resume,
               dyadlib.LEDGER: lambda: stores_on(f"{inst}/d-work/rows/1.md", "the ledger"),
               dyadlib.EVENTS: lambda: stores_on(f"{events}/x.jsonl", "the event store")}
    return {i: (readers[i]() if i in readers else [f"no reading of {i!r}'s trigger in this test"]) for i in dyadlib.INPUT_TRIGGERS}


class CheckTriggerTests(unittest.TestCase):
    def test_every_registered_label_and_sweep_part_is_classed(self):
        labels = registered_labels()
        missing = sorted(labels - set(dyadlib.CHECK_INPUTS))
        self.assertEqual(missing, [], "a guard reads inputs no row of dyadlib.CHECK_INPUTS names")
        core = {f"{c}/{e}" for c, e in (k.split("/") for k in dyadlib.CHECK_INPUTS if "/" in k)
                if (PKG / "guards" / c / f"{e}.py").is_file() or not (REPO / "crafts" / c).is_dir()}
        stale = sorted(k for k in dyadlib.CHECK_INPUTS if "/" in k and k not in labels and (REPO / "crafts" / k.split("/")[0]).is_dir())
        self.assertEqual(stale, [], "a row names a guard its installed craft no longer has")   # a departed craft's rows are ignored (Q3)
        corpora = {p.name for p in (PKG / "guards").iterdir() if p.is_dir()}
        stale_core = sorted(k for k in dyadlib.CHECK_INPUTS if "/" in k and k.split("/")[0] in corpora and k not in labels)
        self.assertEqual(stale_core, [], "a core row names a guard with no file")   # #619 F13: a removed core guard's row
        self.assertTrue(core)
        am = dyadlib.load_module(PKG / "scripts" / "automaton.py", "automaton")
        hy = dyadlib.load_module(PKG / "scripts" / "hygiene.py", "hygiene")
        for part in dyadlib.SWEEP_PARTS:
            self.assertTrue(callable(getattr(am, part, None) or getattr(hy, part, None)), part)
            self.assertIn(part, dyadlib.CHECK_INPUTS)
        self.assertTrue({"suite", "suite:live"} <= set(dyadlib.CHECK_INPUTS))

    def test_every_input_names_a_trigger_and_a_delay(self):
        used = {i for v in dyadlib.CHECK_INPUTS.values() for i in v}
        self.assertEqual(used, set(dyadlib.CHECK_INPUT_NAMES))                     # no input left unread
        for i in dyadlib.CHECK_INPUT_NAMES:
            trig, delay = dyadlib.INPUT_TRIGGERS[i]
            self.assertTrue(trig.strip() and delay.strip(), i)

    def test_every_trigger_is_delivered(self):
        self.assertEqual({i: w for i, w in delivered().items() if w}, {})

    def test_each_part_runs_where_its_inputs_triggers_run(self):
        """#619 Decision 4 (F9): `sweep`, `sweep --stores` and `stall_lines` run with every part stubbed; a part classed
        with an input fails when the mode that input's trigger runs never calls it."""
        import contextlib, datetime, tempfile, unittest.mock
        am = dyadlib.load_module(PKG / "scripts" / "automaton.py", "automaton")
        tmp = tempfile.mkdtemp(); self.addCleanup(__import__("shutil").rmtree, tmp, True)
        calls: list[str] = []
        def rec(name, ret):
            return lambda *a, **k: (calls.append(name), ret)[1]
        parts = {(am, "sweep_check"): [], (am, "sweep_drift"): [], (am, "sweep_ledger"): [], (am, "sweep_ci"): [],
                 (am, "sweep_audit"): [], (am.hygiene_mod, "hygiene"): ([], []), (am.hygiene_mod, "inflight_cabinets"): []}
        names = {"inflight_cabinets": "inflight"}
        others = {(am, "new_events"): (None, {}, []), (am, "home"): None, (am, "box_messages"): [],
                  (am, "land_events"): "events: none", (am, "sweep_pulls"): None, (am.land, "fetch"): "b" * 40,
                  (am.land, "prepare"): None, (am.land, "out"): tmp}
        modes = {"full": lambda: am.sweep(Path(tmp), 1), "stores": lambda: am.sweep(Path(tmp), 1, stores=True),
                 "resume": lambda: am.stall_lines(Path(tmp), "b" * 40, now=datetime.datetime.now(datetime.timezone.utc))}
        called = {}
        with contextlib.ExitStack() as st:
            for (mod, attr), ret in parts.items():
                st.enter_context(unittest.mock.patch.object(mod, attr, rec(names.get(attr, attr), ret)))
            for (mod, attr), ret in others.items():
                st.enter_context(unittest.mock.patch.object(mod, attr, lambda *a, ret=ret, **k: ret))
            st.enter_context(unittest.mock.patch.object(am.land, "locked", lambda common: contextlib.nullcontext()))
            st.enter_context(unittest.mock.patch.dict(__import__("os").environ, {"GITHUB_TOKEN": ""}))
            for mode, go in modes.items():
                calls.clear(); go(); called[mode] = set(calls)
        runs = {dyadlib.CODE: "full", dyadlib.WORLD: "full", dyadlib.LEDGER: "stores", dyadlib.EVENTS: "stores",
                dyadlib.ABSENCE: "resume"}
        self.assertEqual(set(runs), set(dyadlib.CHECK_INPUT_NAMES))
        missed = sorted(f"{p} ({i}: {runs[i]})" for p in dyadlib.SWEEP_PARTS for i in dyadlib.CHECK_INPUTS[p]
                        if p not in called[runs[i]])
        self.assertEqual(missed, [], "a part classed with an input whose trigger never calls it")
        self.assertNotIn("sweep_audit", called["stores"])                         # the full sweep only

    def test_mixed_checks_take_the_union(self):
        """H1: a check reading the code tree and the ledger runs on both triggers."""
        for label in ("agent/references", "agent/plans", "agent/merges"):
            self.assertEqual(set(dyadlib.CHECK_INPUTS[label]), {dyadlib.CODE, dyadlib.LEDGER}, label)

    def test_the_criterion_names_each_input(self):
        import json
        d = json.loads((PKG / "dmc" / "check-trigger.jsonld").read_text())
        self.assertEqual([t["name"] for t in d["hasDefinedTerm"]], list(dyadlib.CHECK_INPUT_NAMES))
        self.assertEqual(d["dyad:judgedBy"]["dyad:kind"], "mechanical")

    def test_the_text_readers(self):
        text = ("name: x\non:\n  push:\n    branches: [main]\n    paths-ignore: ['a/**', \"b/**\"]\n  workflow_dispatch: {}\n"
                "jobs:\n  j:\n    steps:\n      - run: echo one\n      - name: n\n        run: |\n          two\n          three\n"
                "      - run: four\n")
        self.assertEqual(push_filter(text, "paths-ignore"), ["a/**", "b/**"])
        self.assertEqual(push_filter(text, "paths"), [])
        self.assertIsNone(push_filter("on:\n  workflow_dispatch: {}\njobs: {}\n", "paths"))
        self.assertEqual(run_lines(text), ["echo one", "two", "three", "four"])
        self.assertTrue(ignored("a/x", ["a/**"])); self.assertFalse(ignored("c/x", ["a/**"]))


if __name__ == "__main__":
    unittest.main()
