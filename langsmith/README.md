# Resume Review Agent — LangSmith Setup

LangSmith equivalent of the Langfuse setup. Same agent, same dataset, same evaluators — different observability backend.

## Mapping vs Langfuse

| Concept | Langfuse | LangSmith |
|---|---|---|
| Prompt store | Prompts (UI / `get_prompt`) | Prompt Hub (`pull_prompt`) |
| Trace capture | `CallbackHandler` callback | Auto-trace from env vars + `@traceable` |
| Score on a trace | `create_score(trace_id=...)` | `create_feedback(run_id=...)` |
| Dataset | `create_dataset_item` | `create_examples` |
| Experiment runner | `dataset.run_experiment(task, evaluators)` | `client.evaluate(target, data, evaluators)` |
| Evaluator return type | `Evaluation(name=...)` | `dict({"key": ..., "score": ...})` |

## File layout

| File | Role |
|---|---|
| `seed_prompts.py` | Push prompts to LangSmith Prompt Hub |
| `seed_dataset.py` | Create the `resume-review-eval` dataset with 4 sample resumes |
| `resume_review_agent.py` | Agent — pulls prompts, runs, posts feedback to the run |
| `run_experiment.py` | Run the agent over the dataset using `client.evaluate` |
| `requirements.txt` | Python dependencies |

## Setup

Add LangSmith credentials to the repo-root `.env`:

```
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=lsv2_pt_...
LANGSMITH_PROJECT=resume-review
LANGSMITH_ENDPOINT=https://api.smith.langchain.com   # or your self-hosted URL
OPENAI_API_KEY=sk-...
```

Symlink it locally so the scripts (which `load_dotenv(".env")`) pick it up:

```bash
ln -s ../.env .env
```

Install deps (or reuse `../Langfuse/venv` — `langsmith` is already in there):

```bash
pip install -r requirements.txt
```

## One-time setup

```bash
python seed_prompts.py     # push 5 prompts to Prompt Hub
python seed_dataset.py     # create dataset + 4 examples (skips if items exist)
```

## Production usage

```bash
python resume_review_agent.py
```

What happens:

1. Pulls prompts from LangSmith Prompt Hub (cached after first fetch)
2. Invokes the agent — auto-traced because `LANGSMITH_TRACING=true`
3. The `@traceable` wrapper gives a top-level run; `get_current_run_tree().id` exposes the run ID
4. Posts feedback (LangSmith's equivalent of Langfuse scores):

| Feedback key | Source |
|---|---|
| `resume_score` | Regex from agent output |
| `tools_completeness` | All 3 tools called (boolean as `value`) |
| `judge_relevance` / `_specificity` / `_actionability` / `_coverage` | LLM judge per-criterion |
| `judge_overall` | Mean of 4 judge criteria |

## Offline evaluation

```bash
python run_experiment.py
```

Calls `client.evaluate(target, data="resume-review-eval", evaluators=[...])`. LangSmith handles dataset iteration, tracing, and feedback wiring. Each experiment shows up under the dataset in the UI with side-by-side comparison against prior runs.

## Where to find things in the LangSmith UI

| Thing | Path |
|---|---|
| Production traces | **Tracing Projects → resume-review** |
| Prompts | **Prompts** (left nav) |
| Datasets | **Datasets & Testing → resume-review-eval** |
| Experiments | Inside the dataset → **Experiments** tab |
| Compare experiments | Select 2+ in the **Experiments** tab → comparison view |

## Editing prompts without code changes

1. **Prompts** → e.g. `resume-review-system`
2. Commit a new version
3. Restart the agent process (the in-memory cache pulls fresh)

To roll back: select an older commit in the UI.

## Common workflows

**Tune a prompt:**
1. Edit prompt in LangSmith UI
2. `python run_experiment.py`
3. Compare experiments in the dataset → Experiments tab

**Add a new test resume:**
1. Add an entry to `ITEMS` in `seed_dataset.py`
2. Re-run `seed_dataset.py` (or add via the UI)
3. Next experiment picks it up

**Switch model:**
1. Change `model="gpt-4o-mini"` in `resume_review_agent.py`
2. Re-run `run_experiment.py` and compare in the UI

## Troubleshooting

- **`LANGSMITH_API_KEY missing`** — add it to `.env` and re-source
- **No traces showing up** — confirm `LANGSMITH_TRACING=true` and `LANGSMITH_PROJECT` set; calls to LangChain/LangGraph auto-trace only when those vars are present
- **`get_current_run_tree() is None`** — the function isn't running inside a traced context; the `@traceable` decorator on `review_resume` provides one
- **Self-hosted instance** — set `LANGSMITH_ENDPOINT` to your URL; everything else works identically
