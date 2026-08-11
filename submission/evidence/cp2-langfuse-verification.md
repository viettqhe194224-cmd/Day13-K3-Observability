# CP2 Langfuse verification

Prompt: `day13-chat`

## Same-input version comparison

Input: `Explain why metrics traces and logs work together`

| Scenario | Session ID | Trace ID | Label | Version | Source |
|---|---|---|---|---:|---|
| Baseline | `s_prompt_baseline_v1` | `4c23f2aba0af7bbf580de31e58cdd6d4` | `baseline` | 1 | `langfuse` |
| Candidate | `s_prompt_candidate_v2` | `ded016c30daf75bb9f984c943308be7d` | `candidate` | 2 | `langfuse` |
| Production rollout | `s_prompt_production_v2` | `891cd6e0a7d91f1fa7fd28119e0446bc` | `production` | 2 | `langfuse` |
| Production rollback | `s_prompt_rollback_v1` | `e53f2fc551dbd650bb323fab4225d286` | `production` | 1 | `langfuse` |

## Final prompt state

- Version 1 labels: `baseline`, `production`.
- Version 2 labels: `candidate`, `latest`.
- Both baseline and candidate generations include a non-null Langfuse prompt ID.
- Production was moved to version 2, verified by a trace, then rolled back to version 1.

UI screenshots should capture the version list, baseline/candidate trace metadata, and the final rollback state.
