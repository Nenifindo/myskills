# Source Guide Evaluation

Use this reference when the request includes a benchmark, a comparison book,
or an unsupervised quality check.

## Supervised guides

Pin both repositories before comparing them:

- target source: full commit SHA, branch/tag, and working-tree state;
- reference material: its full commit SHA, branch/tag, and working-tree state;
- dates are useful drift signals, but a date is not a substitute for a SHA.

Run the source-reference validator on the generated guide. Separately extract
source paths mentioned by the reference and check whether they exist at the
target revision. Missing paths, renamed entry points, and changed defaults are
version-drift findings. Compare concepts and contracts, not chapter count,
wording, or raw path overlap. Reward a guide for correcting an obsolete
reference when it cites the newer implementation and explains the difference.

## Unsupervised guides

Define a small oracle from the repository itself before judging prose. Prefer
mechanical invariants and focused tests such as:

- manifest/config catalogs parse successfully;
- generated module or documentation graphs are current;
- representative syntax/type checks pass;
- focused unit tests pass, or their exact platform/dependency blocker is
  recorded;
- source citations resolve at the pinned revision.

The guide must distinguish facts observed in source/config/tests from static
interpretations. Do not turn a successful citation check into proof that the
architectural interpretation is behaviorally complete.

## Report states

Use a compact table in `verification.md` with one row per meaningful check:

| Check | State | Evidence | Limitation |
|---|---|---|---|
| Source citations | passed | validator command and count | none |
| Focused tests | blocked | exact command and error | missing dependency/platform |

Allowed states are `planned`, `executed`, `passed`, `failed`, `blocked`, and
`not run`. Do not use "待运行" or similar placeholders in a final report.

## Repeatable audit

After writing the guide, run:

```powershell
python -B C:\Users\zhoub\.codex\skills\repo-source-explainer\scripts\validate_source_refs.py --require <repo> <docs>
python -B C:\Users\zhoub\.codex\skills\repo-source-explainer\scripts\audit_source_guide.py <repo> <docs> --revision <sha> --reference <reference-repo>
```

The audit is a consistency check, not a semantic grader. Review its warnings,
especially stale reference anchors and verification claims, before delivery.

For large repositories on Windows, enable Git long paths before checkout when
the repository or its generated paths require it:

```powershell
git config --global core.longpaths true
```
