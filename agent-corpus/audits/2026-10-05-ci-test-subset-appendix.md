# Appendix to the CI test-subset audit: the dependency map and its sizing scripts (2026-10-05)

*d-work #243, banking residue of d-work #219 (and #220). The audit
`2026-10-05-ci-test-subset.md` states its sizes and calls the map "the input to a `dyad check --impacted`"
and session-local; this file keeps the map and the scripts that produced the sizes, so a later d-work that
builds `--impacted` need not rebuild them. They are instance data and scratch code, not package code: nothing
here is imported, and Rule-12 asks no check of them.*

## What they are
- **The map** (`dep`, `cnt`): a static dependency map of the 45 test files (921 tests) at `9fafb51`. `dep` maps
  each test file to the modules it imports, loads with `load_guard` or `load_package`, or names by `*.py`;
  `cnt` maps each file to its test count.
- **`t219.py`** sizes a change: the test files whose dependency set meets the changed modules, their test
  count, and their summed time. Time per file is the sum of that module's #204 per-test durations for the core
  root, and the craft root's median scaled by the file's share of that root's tests.
- **`n220.py`** reuses it for #220: the same sizes restricted to *gate code* (guards, runner, install path),
  which is 31 of 45 files, 707 of 921 tests and 94% of summed time.

## Blind spots (as the audit states them)
The map cannot see a spawned `dyad/bin/dyad` (it imports whatever it dispatches to), `load_module` by a built
path, or guard and craft discovery. A `--impacted` built on it must always run the entrypoint-spawning tests and
treat a hub module (`dyadlib`, `package`, `livetest`, `rows`) or the runner as a full-suite change.

## To rebuild
Walk each file under `dyad/tests/` and `crafts/*/tests/`, record the module names it imports, passes to
`load_guard` or `load_package`, or names as `<module>.py`, and count its `def test_` methods. `t219.py` below
reads `impact219.json` and the #204 per-test durations, `p204/measure/durations.d1.err.json` (session-local,
not kept; #204's audit describes how it was measured).

## `impact219.json`

```json
{
"dep": {
"crafts/countersign/tests/test_project_countersign.py": [
"dyadlib",
"livetest",
"project_countersign"
],
"crafts/disclosure/tests/test_project_disclosure.py": [
"dyadlib",
"incidents",
"project_disclosure",
"redaction"
],
"crafts/disclosure/tests/test_redaction.py": [
"dyadlib",
"package",
"provenance",
"redaction",
"rows"
],
"crafts/sysadmin/tests/guards/test_changelog.py": [
"changelog",
"dyadlib"
],
"crafts/sysadmin/tests/guards/test_events.py": [
"dyadlib",
"events",
"rows"
],
"crafts/sysadmin/tests/guards/test_ops_scripts.py": [
"dyadlib",
"ops_scripts"
],
"crafts/sysadmin/tests/guards/test_runbooks.py": [
"dyadlib",
"runbooks"
],
"crafts/sysadmin/tests/test_project_events.py": [
"dyadlib",
"events",
"livetest",
"project_events"
],
"crafts/sysarch/tests/guards/test_registry.py": [
"containment",
"dyadlib",
"project_erd",
"registry",
"rows"
],
"crafts/sysarch/tests/test_project_entities.py": [
"dyadlib",
"events",
"livetest",
"package",
"project_entities",
"project_erd",
"registry",
"rows"
],
"crafts/sysarch/tests/test_project_erd.py": [
"dyadlib",
"livetest",
"project_erd"
],
"crafts/sysarch/tests/test_project_instances.py": [
"dyadlib",
"livetest",
"project_entities",
"project_instances"
],
"crafts/sysarch/tests/test_project_kanban.py": [
"dyadlib",
"project_kanban"
],
"crafts/sysarch/tests/test_project_schema.py": [
"containment",
"dyadlib",
"livetest",
"manifest",
"package",
"project_erd",
"project_schema",
"rows"
],
"crafts/syseng/tests/guards/test_invariants.py": [
"dyadlib",
"invariants",
"naming"
],
"crafts/syseng/tests/guards/test_naming.py": [
"dyadlib",
"naming"
],
"crafts/syseng/tests/guards/test_tests.py": [
"dyadlib",
"events",
"package",
"project_erd",
"rows",
"tests"
],
"dyad/tests/guards/agent/test_frame.py": [
"dyadlib",
"frame"
],
"dyad/tests/guards/agent/test_plans.py": [
"dyadlib",
"plans"
],
"dyad/tests/guards/agent/test_provenance.py": [
"dyadlib",
"provenance",
"rows"
],
"dyad/tests/guards/agent/test_prs.py": [
"dyadlib",
"prs"
],
"dyad/tests/guards/agent/test_records.py": [
"dyadlib",
"records"
],
"dyad/tests/guards/agent/test_references.py": [
"containment",
"dyadlib",
"frame",
"package",
"project_erd",
"references"
],
"dyad/tests/guards/agent/test_rows.py": [
"dyadlib",
"rows"
],
"dyad/tests/guards/agent/test_rules.py": [
"dyadlib",
"rules"
],
"dyad/tests/guards/agent/test_sessions.py": [
"dyadlib",
"provenance",
"sessions"
],
"dyad/tests/guards/agent/test_vocabulary.py": [
"dyadlib",
"vocabulary"
],
"dyad/tests/guards/craft/test_crafts.py": [
"crafts",
"dyadlib",
"package",
"project_kanban",
"runbooks"
],
"dyad/tests/guards/infra/test_bundle.py": [
"bundle",
"dyadlib"
],
"dyad/tests/guards/infra/test_containment.py": [
"containment",
"dyadlib",
"manifest"
],
"dyad/tests/guards/infra/test_manifest.py": [
"distribute",
"dyadlib",
"manifest",
"rows"
],
"dyad/tests/guards/preferences/test_preferences.py": [
"dyadlib",
"preferences"
],
"dyad/tests/test_concurrency.py": [
"dyadlib",
"package",
"rows"
],
"dyad/tests/test_craft.py": [
"craft",
"dyadlib",
"livetest",
"package",
"references"
],
"dyad/tests/test_distribute.py": [
"distribute"
],
"dyad/tests/test_dyadlib.py": [
"dyadlib",
"livetest",
"package",
"runbooks"
],
"dyad/tests/test_dyadlib_rows.py": [
"dyadlib",
"livetest"
],
"dyad/tests/test_entrypoint.py": [
"package"
],
"dyad/tests/test_hostadapter.py": [
"hostadapter"
],
"dyad/tests/test_incidents.py": [
"dyadlib",
"incidents"
],
"dyad/tests/test_livetest.py": [
"dyadlib",
"livetest",
"package",
"rows"
],
"dyad/tests/test_package.py": [
"distribute",
"dyadlib",
"events",
"manifest",
"package",
"provenance",
"references",
"rows",
"runbook",
"runbooks"
],
"dyad/tests/test_playbooks.py": [
"dyadlib",
"runbook"
],
"dyad/tests/test_runbook.py": [
"dyadlib",
"events",
"livetest",
"runbook",
"runbooks"
],
"dyad/tests/test_trace.py": [
"dyadlib",
"trace"
]
},
"cnt": {
"crafts/countersign/tests/test_project_countersign.py": 40,
"crafts/disclosure/tests/test_project_disclosure.py": 17,
"crafts/disclosure/tests/test_redaction.py": 18,
"crafts/sysadmin/tests/guards/test_changelog.py": 20,
"crafts/sysadmin/tests/guards/test_events.py": 15,
"crafts/sysadmin/tests/guards/test_ops_scripts.py": 28,
"crafts/sysadmin/tests/guards/test_runbooks.py": 22,
"crafts/sysadmin/tests/test_project_events.py": 9,
"crafts/sysarch/tests/guards/test_registry.py": 10,
"crafts/sysarch/tests/test_project_entities.py": 14,
"crafts/sysarch/tests/test_project_erd.py": 13,
"crafts/sysarch/tests/test_project_instances.py": 11,
"crafts/sysarch/tests/test_project_kanban.py": 27,
"crafts/sysarch/tests/test_project_schema.py": 14,
"crafts/syseng/tests/guards/test_invariants.py": 23,
"crafts/syseng/tests/guards/test_naming.py": 35,
"crafts/syseng/tests/guards/test_tests.py": 4,
"dyad/tests/guards/agent/test_frame.py": 5,
"dyad/tests/guards/agent/test_plans.py": 7,
"dyad/tests/guards/agent/test_provenance.py": 60,
"dyad/tests/guards/agent/test_prs.py": 10,
"dyad/tests/guards/agent/test_records.py": 6,
"dyad/tests/guards/agent/test_references.py": 40,
"dyad/tests/guards/agent/test_rows.py": 35,
"dyad/tests/guards/agent/test_rules.py": 7,
"dyad/tests/guards/agent/test_sessions.py": 31,
"dyad/tests/guards/agent/test_vocabulary.py": 8,
"dyad/tests/guards/craft/test_crafts.py": 34,
"dyad/tests/guards/infra/test_bundle.py": 29,
"dyad/tests/guards/infra/test_containment.py": 27,
"dyad/tests/guards/infra/test_manifest.py": 40,
"dyad/tests/guards/preferences/test_preferences.py": 12,
"dyad/tests/test_concurrency.py": 5,
"dyad/tests/test_craft.py": 15,
"dyad/tests/test_distribute.py": 18,
"dyad/tests/test_dyadlib.py": 40,
"dyad/tests/test_dyadlib_rows.py": 5,
"dyad/tests/test_entrypoint.py": 10,
"dyad/tests/test_hostadapter.py": 11,
"dyad/tests/test_incidents.py": 8,
"dyad/tests/test_livetest.py": 12,
"dyad/tests/test_package.py": 84,
"dyad/tests/test_playbooks.py": 8,
"dyad/tests/test_runbook.py": 22,
"dyad/tests/test_trace.py": 12
}
}
```

## `t219.py`

```python
import json,collections
S='/tmp/claude-0/-home-user-dyad-system/d3441afa-afc8-58a3-9e93-fb6f07990b98/scratchpad'
imp=json.load(open(S+'/impact219.json')); dep,cnt=imp['dep'],imp['cnt']
dur=json.load(open(S+'/p204/measure/durations.d1.err.json'))
per=collections.Counter()
for s,name,mod in dur: per[mod]+=s
craft_root={'countersign':(1.40,40),'disclosure':(0.80,35),'sysadmin':(5.87,94),'sysarch':(3.59,89),'syseng':(2.21,62)}
def t(f):
    base=f.rsplit('/',1)[1][:-3]
    if f.startswith('dyad/tests/'):
        key=f[len('dyad/tests/'):-3].replace('/','.')
        return per.get(key, per.get(base))
    c=f.split('/')[1]; s,n=craft_root[c]; return s*cnt[f]/n
tot=sum((t(f) or 0) for f in dep); miss=[f for f in dep if t(f) is None]
print('total',round(tot,1),'missing',miss)
cases={'package.py':['package'],'trace.py + package.py':['trace','package'],'rows guard':['rows'],'dyadlib':['dyadlib'],'record-only':[]}
for k,m in cases.items():
    fs=[f for f in dep if set(dep[f])&set(m)]
    print(k,len(fs),sum(cnt[f] for f in fs),round(sum((t(f) or 0) for f in fs),1))
print('---')
for k,m in {'trace.py':['trace'],'changelog guard':['changelog'],'vocabulary guard':['vocabulary'],'project_kanban':['project_kanban'],'provenance guard':['provenance'],'redaction':['redaction'],'livetest':['livetest']}.items():
    fs=[f for f in dep if set(dep[f])&set(m)]
    print(k,len(fs),sum(cnt[f] for f in fs),round(sum((t(f) or 0) for f in fs),1),[f.rsplit('/',1)[1] for f in fs][:8])
import collections
c=collections.Counter(x for v in dep.values() for x in v); print(c.most_common(10))
```

## `n220.py`

```python
exec(open(S:='/tmp/claude-0/-home-user-dyad-system/d3441afa-afc8-58a3-9e93-fb6f07990b98/scratchpad/t219.py').read().split("print('total'")[0])
GATE={'bundle','changelog','containment','crafts','events','frame','invariants','manifest','naming','ops_scripts','plans','preferences','provenance','prs','records','references','registry','rows','rules','runbooks','sessions','tests','vocabulary','package','dyadlib','distribute','craft','runbook','entrypoint','dyadlib_rows','concurrency'}
def subj(f): return f.rsplit('/',1)[1][5:-3]
gatefiles=[f for f in dep if subj(f) in GATE]
print('gate test files',len(gatefiles),sum(cnt[f] for f in gatefiles),round(sum((t(f) or 0) for f in gatefiles),1))
print('non-gate',sorted(subj(f) for f in dep if f not in gatefiles))
cases={'package.py':['package'],'rows guard':['rows'],'dyadlib':['dyadlib'],'provenance guard':['provenance'],'livetest':['livetest'],'project_kanban':['project_kanban'],'trace.py':['trace'],'changelog guard':['changelog'],'vocabulary guard':['vocabulary'],'record-only':[]}
for k,m in cases.items():
    fs=[f for f in gatefiles if set(dep[f])&set(m)] if set(m)&GATE else []
    print(k,len(fs),sum(cnt[f] for f in fs),round(sum((t(f) or 0) for f in fs),1))
```
