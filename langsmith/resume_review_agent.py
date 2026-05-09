import re
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import AIMessage
from langchain.agents import create_agent as create_react_agent
from langsmith import Client, traceable
from langsmith.run_helpers import get_current_run_tree

load_dotenv(".env")

client = Client()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

EXPECTED_TOOLS = {"score_resume", "identify_strengths", "suggest_improvements"}

_PROMPT_CACHE: dict = {}


def render(name: str, **vars) -> str:
    if name not in _PROMPT_CACHE:
        _PROMPT_CACHE[name] = client.pull_prompt(name)
    return _PROMPT_CACHE[name].format(**vars)


@tool
def score_resume(resume_text: str) -> str:
    """Score a resume out of 10 based on clarity, structure, and completeness."""
    return llm.invoke(render("resume-review-score", resume_text=resume_text)).content


@tool
def identify_strengths(resume_text: str) -> str:
    """Identify the top 3 strengths in the resume."""
    return llm.invoke(render("resume-review-strengths", resume_text=resume_text)).content


@tool
def suggest_improvements(resume_text: str) -> str:
    """Suggest the top 3 improvements for the resume."""
    return llm.invoke(render("resume-review-improvements", resume_text=resume_text)).content


tools = [score_resume, identify_strengths, suggest_improvements]

system_template = client.pull_prompt("resume-review-system")
agent = create_react_agent(
    llm,
    tools,
    system_prompt=system_template.format(),
)


class CriterionScore(BaseModel):
    score: float = Field(ge=0.0, le=1.0, description="Score between 0.0 and 1.0")
    reason: str = Field(description="One sentence justification")


class JudgeVerdict(BaseModel):
    relevance: CriterionScore
    specificity: CriterionScore
    actionability: CriterionScore
    coverage: CriterionScore


judge_llm = llm.with_structured_output(JudgeVerdict)


def llm_judge(resume_text: str, review: str) -> JudgeVerdict:
    prompt = render("resume-review-judge", resume_text=resume_text, review=review)
    return judge_llm.invoke(prompt)


def extract_resume_score(text: str) -> float | None:
    match = re.search(r"(\d+(?:\.\d+)?)\s*/\s*10", text)
    return float(match.group(1)) if match else None


def tools_called(messages) -> set[str]:
    called = set()
    for msg in messages:
        if isinstance(msg, AIMessage) and msg.tool_calls:
            for tc in msg.tool_calls:
                called.add(tc["name"])
    return called


def run_agent(resume_text: str) -> tuple[str, set[str]]:
    """Invoke the agent without attaching feedback. Used by experiments."""
    result = agent.invoke(
        {"messages": [("human", f"Please review this resume:\n\n{resume_text}")]}
    )
    return result["messages"][-1].content, tools_called(result["messages"])


def post_feedback(run_id, messages, resume_text: str, final_output: str):
    resume_score = extract_resume_score(final_output)
    if resume_score is not None:
        client.create_feedback(
            run_id=run_id,
            key="resume_score",
            score=resume_score,
            comment="Score (X/10) extracted from agent output",
        )

    called = tools_called(messages)
    client.create_feedback(
        run_id=run_id,
        key="tools_completeness",
        value=EXPECTED_TOOLS.issubset(called),
        comment=f"Called: {sorted(called)}; expected: {sorted(EXPECTED_TOOLS)}",
    )

    verdict = llm_judge(resume_text, final_output)
    for criterion, result in verdict.model_dump().items():
        client.create_feedback(
            run_id=run_id,
            key=f"judge_{criterion}",
            score=result["score"],
            comment=result["reason"],
        )

    avg = sum(c["score"] for c in verdict.model_dump().values()) / 4
    client.create_feedback(
        run_id=run_id,
        key="judge_overall",
        score=avg,
        comment="Mean of relevance, specificity, actionability, coverage",
    )


@traceable(name="review_resume")
def review_resume(resume_text: str) -> str:
    result = agent.invoke(
        {"messages": [("human", f"Please review this resume:\n\n{resume_text}")]}
    )
    final_output = result["messages"][-1].content

    run_tree = get_current_run_tree()
    if run_tree is not None:
        post_feedback(run_tree.id, result["messages"], resume_text, final_output)

    return final_output


if __name__ == "__main__":
    sample_resume = """
    John Doe
    john.doe@email.com | LinkedIn: linkedin.com/in/johndoe | +1-555-0100

    SUMMARY
    Software engineer with 3 years of experience in Python and web development.

    EXPERIENCE
    Software Engineer - TechCorp (2022 - Present)
    - Built REST APIs using FastAPI and PostgreSQL
    - Reduced API response time by 40% through caching

    Junior Developer - StartupXYZ (2021 - 2022)
    - Developed React frontend components
    - Wrote unit tests with pytest

    EDUCATION
    B.Sc. Computer Science - State University (2021)

    SKILLS
    Python, FastAPI, React, PostgreSQL, Git, Docker
    """

    print("=== Resume Review Agent ===\n")
    review = review_resume(sample_resume)
    print("\n=== Final Review ===")
    print(review)
