# M8 — mock role-based workflow

A Python orchestration exercise with shared JSON history. The folder name is historical: the current implementation does not use the CrewAI library and does not call an LLM.

## Execution path

`CrewOrchestrator.automated_analysis_workflow(data)`:

1. Calls `DataAnalystAgent.analyze_data()`.
2. Passes that result to `ReportGeneratorAgent.generate_report()`.
3. Calls `RootCauseAnalyzer.analyze_issue()` when the input contains anomalies.
4. Returns the analysis, formatted report, optional root-cause result, and status.

`interactive_session()` selects a role using keywords and invokes `MockLLMAgent.process_task()`.

## Implemented versus simulated

| Implemented | Simulated or absent |
| --- | --- |
| Python classes and sequential method calls | CrewAI framework integration |
| JSON history and insight storage through `AgentMemory` | LLM inference and tool selection |
| Formatting a report from a dictionary | Data-derived trends and root-cause diagnosis |
| Keyword-based interactive routing | Model learning, autonomous planning, and measured feedback improvement |

The analysis method returns fixed trends and recommendations. Root-cause analysis returns a fixed proposed cause. Values such as `confidence` are example constants, not calibrated model estimates.

The summary uses `len(data)`, which counts dictionary keys; it does not necessarily count observations.

## Run the local mock

From the repository root, inside your Python environment:

```bash
python -m pip install -r modules/m8-crew-agents/requirements.txt
python modules/m8-crew-agents/crew_agents.py
```

No LLM credentials are needed for the mock behavior. A clean dependency installation and complete script run have not been verified as part of this documentation update.

The script writes JSON history at a path relative to the current working directory. Running from the repository root avoids an unintended nested `modules/` directory. Use sample inputs; inspect generated history before committing it.

## Limitations

- No locking or transactional storage for concurrent writers.
- No bounded-history policy or automatic learning mechanism.
- Returning `workflow_status: completed` does not establish analytical correctness.
- This module is useful for studying orchestration structure, not as evidence of a deployed multi-agent AI system.

## Source

[crew_agents.py](crew_agents.py) and [requirements.txt](requirements.txt).
