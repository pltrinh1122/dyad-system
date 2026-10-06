"""Trace-store guard tests (agent/traces.py, #227): the guard declares the contract and delegates to
`trace.check_store` — a well-formed trace for an existing row passes, a trace for no row or with a bad header
fails, an absent store passes; `describe` names the trace's sections."""
import os, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
import dyadlib
g = dyadlib.load_guard("agent", "traces")

ROW = "id: 7\ntitle: widget\nopened: 2026-10-05\nstate: done\ndisposed: 2026-10-05 Y plan\nrefs: \n"
TRACE = "# Trace #7 — widget\n\n" + "".join(f"## {s}\n\nx\n\n" for s in ("Timeline", "Buckets", "Counts", "Bottleneck", "Limits"))

def fixture(traces: dict[str, str] | None) -> Path:
    root = Path(tempfile.mkdtemp()); dw = root / "agent-corpus" / "d-work"
    (dw / "rows").mkdir(parents=True); (dw / "rows" / "7.md").write_text(ROW)
    if traces is not None:
        (dw / "traces").mkdir()
        for n, t in traces.items(): (dw / "traces" / n).write_text(t)
    return root

class TraceGuardTests(unittest.TestCase):
    def setUp(self): os.environ.pop("DYAD_INSTANCE", None)
    def test_contract(self):
        self.assertIsNone(dyadlib.contract_problem(g, "core", "agent"))
        self.assertEqual((g.ENTITY, g.CORPUS, g.TRANSACTION), ("trace", "agent", False))
        self.assertEqual(g.FIELDS, ("Timeline", "Buckets", "Counts", "Bottleneck", "Limits"))
    def test_good_store_passes(self):
        root = fixture({"7.md": TRACE})
        self.assertEqual(g.check_package(root), []); self.assertEqual(g.summary(root), "1 traces")
    def test_bad_traces_fail(self):
        msgs = g.check_package(fixture({"8.md": TRACE.replace("#7", "#8"), "7.md": TRACE.replace("# Trace #7", "# Trace #9")}))
        self.assertTrue(any("8.md: no row #8" in m for m in msgs), msgs); self.assertTrue(any("7.md: first line" in m for m in msgs), msgs)
    def test_absent_store_passes(self):
        root = fixture(None)
        self.assertEqual(g.check_package(root), []); self.assertEqual(g.summary(root), "0 traces")
    def test_describe(self):
        d = g.describe(fixture({"7.md": TRACE}), dyadlib.PKG)
        self.assertEqual([f[0] for f in d["fields"]], list(g.FIELDS)); self.assertEqual(d["observed"], 1)

if __name__ == "__main__":
    unittest.main()
