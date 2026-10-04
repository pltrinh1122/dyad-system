# Falsification — signing can be batched (d-work #207)

**Claim (Operator, 2026-10-04, verbatim):** "signing can be batched. falsify."

**Context.** In this cloud container, git signs every commit through `/tmp/code-sign`, which
`/root/.gitconfig` points to. `/tmp/code-sign` links to `/opt/env-runner/environment-manager`, a
31 MB binary. The public key file `/home/claude/.ssh/commit_signing_key.pub` is empty, and there is
no private key on the box, so the key is held off-box (#206 findings).

**Measured (n=15 to 20, warm, 2026-10-04):**

| step | cost |
|---|---|
| one commit, unsigned | 11 ms |
| one commit, signed | 99 ms |
| signer process start (`code-sign --help`, which exits early) | 15 ms |
| so the signing operation itself | about 73 ms |

That 73 ms is most likely the round trip to the remote signer. This is inferred: the key is not on
the box. The signing call itself was not exercised outside git, so as not to sign arbitrary bytes
with the environment's key. `ssh-keygen` is not installed, so it could not be compared.

| # | Attack | Result | Survivor |
|---|--------|--------|----------|
| 1 | Several commits can share one signature. | **Refuted.** | A git signature covers one commit object's own bytes: tree, parents, author, committer and message. A commit's id includes its signature, and every child names its parent's id, so each signed commit needs its own signature. Nothing can be shared. |
| 2 | The signer calls can be batched into one process that signs many commits. | **Refuted inside git; survives only outside it, at disproportionate cost.** | Git invokes `gpg.ssh.program -Y sign` once per object and offers no multi-object interface. `code-sign` only accepts `-Y sign`. Doing it outside git means building commits by hand (`commit-tree`, a batch signer, `hash-object`) and assumes a batch mode the remote signer is not known to offer. That replaces git's own commit path for well under 1 s a day (attack 5). |
| 3 | Sign later in one pass, by committing unsigned and signing the branch before push. | **Refuted as batching; survives as deferral.** | Re-signing rewrites every commit (`rebase --exec 'commit --amend -S'`), so there is still one signer call per commit. It also changes every sha after the fact, breaking any recorded sha such as the evidence head (Rule-2 Binding) and the plan's base commit. |
| 4 | One signature on the tip covers its ancestors through the hash chain. | **Survives as cryptography; refuted for the hosting.** | A signed tip does commit to its whole history (SHA-1 chain). But GitHub shows Verified per commit, and a "require signed commits" protection rejects any unsigned commit in the push. Signed pushes (`--signed`, push certificates) are not supported by GitHub. On this repo GitHub already signs every merge commit on `main`, which is in effect one signature per landed PR. |
| 5 | Batching would save time that matters. | **Refuted.** | Since #206, test fixtures never sign. The remaining signed commits are the Agent's own real ones: 12 across 2026-10-02 to 10-04, each about 88 ms, so about 1 s in two days. The fixture cost (about 36 s per core run) was removed by not signing what nothing reads, not by batching. |
| 6 | Turning signing off for real commits is the batch-free way to save the remaining cost. | **Out of scope; the Operator's decision.** | It is an environment setting, not a repo setting. It saves about 1 s in two days, and it drops GitHub's Verified mark and the one artifact that could tell the Agent's commits apart (Rule-2's proposer/disposer note, #206). |

**Survivor.**
- Git signing cannot be batched: each commit needs its own signature, and git calls the signer once
  per commit.
- The only batch-shaped forms are a signed tip, a signed tag, or GitHub's signed merge commit. Each
  gives one signature per landed unit, and the hosting's per-commit view does not honor it.
- The cost batching was meant to save is already gone (#206). What remains is about 1 s per two days
  of real commits.

Disposition: see ledger #207.
