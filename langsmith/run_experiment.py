from datetime import datetime
from dotenv import load_dotenv

load_dotenv(".env")

from langsmith import Client

from resume_review_agent import (
    run_agent,
    llm_judge,
    extract_resume_score,
    EXPECTED_TOOLS,
)

client = Client()

DATASET_NAME = "resume-review-eval"


def target(inputs: dict) -> dict:
    """Run the agent on one dataset example. Output feeds the evaluators."""
    resume_text = inputs["resume_text"]
    review, called = run_agent(resume_text)
    return {
        "review": review,
        "tools_called": sorted(called),
        "resume_text": resume_text,
    }


def eval_tools_completeness(outputs: dict, **kwargs) -> dict:
    called = set(outputs["tools_called"])
    return {
        "key": "tools_completeness",
        "score": int(EXPECTED_TOOLS.issubset(called)),
        "comment": f"Called: {sorted(called)}",
    }


def eval_resume_score(outputs: dict, **kwargs) -> dict:
    score = extract_resume_score(outputs["review"])
    return {
        "key": "resume_score",
        "score": score if score is not None else 0,
        "comment": "X/10 from agent" if score is not None else "no X/10 found",
    }


def eval_resume_score_in_range(outputs: dict, reference_outputs: dict, **kwargs) -> dict:
    score = extract_resume_score(outputs["review"])
    if score is None:
        return {"key": "score_in_expected_range", "score": 0, "comment": "no X/10 found"}

    expected = reference_outputs or {}
    lo = expected.get("expected_score_min", 0)
    hi = expected.get("expected_score_max", 10)
    in_range = lo <= score <= hi
    return {
        "key": "score_in_expected_range",
        "score": int(in_range),
        "comment": f"score={score}, expected [{lo}, {hi}]",
    }


def eval_judge(outputs: dict, **kwargs) -> list[dict]:
    verdict = llm_judge(outputs["resume_text"], outputs["review"])
    results = []
    for criterion, r in verdict.model_dump().items():
        results.append({
            "key": f"judge_{criterion}",
            "score": r["score"],
            "comment": r["reason"],
        })
    avg = sum(c["score"] for c in verdict.model_dump().values()) / 4
    results.append({
        "key": "judge_overall",
        "score": avg,
        "comment": "Mean of 4 judge criteria",
    })
    return results


def main():
    run_name = f"agent-eval-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    result = client.evaluate(
        target,
        data=DATASET_NAME,
        evaluators=[
            eval_tools_completeness,
            eval_resume_score,
            eval_resume_score_in_range,
            eval_judge,
        ],
        experiment_prefix=run_name,
        max_concurrency=3,
        description="Evaluate agent across varied resumes; checks tool use, score range, and LLM-judged quality.",
    )
    print(f"\nExperiment: {run_name}")
    print(f"Results: {result}")


if __name__ == "__main__":
    main()
