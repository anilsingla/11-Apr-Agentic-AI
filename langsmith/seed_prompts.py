from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langsmith import Client

load_dotenv(".env")

client = Client()


PROMPTS = {
    "resume-review-system": """You are an expert HR resume reviewer. When given a resume, you must:
1. Score it using the score_resume tool
2. Identify strengths using the identify_strengths tool
3. Suggest improvements using the suggest_improvements tool
4. Provide a final summary combining all findings.""",

    "resume-review-score": """Score the following resume out of 10. Consider:
- Clarity and writing quality
- Structure and formatting
- Completeness (contact info, experience, skills, education)

Resume:
{resume_text}

Respond with: Score: X/10 followed by brief reasoning.""",

    "resume-review-strengths": """Identify the top 3 strengths in this resume. Be specific.

Resume:
{resume_text}

List them as:
1. ...
2. ...
3. ...""",

    "resume-review-improvements": """Suggest the top 3 improvements for this resume. Be actionable and specific.

Resume:
{resume_text}

List them as:
1. ...
2. ...
3. ...""",

    "resume-review-judge": """You are an impartial evaluator grading the quality of a resume review.

You will receive the original resume and the review the agent produced. Score the review on each of the following criteria from 0.0 to 1.0, and provide a short (one sentence) reason for each:

- relevance: Does the review address what is actually in the resume (no hallucinated content)?
- specificity: Are observations concrete and tied to resume details, rather than generic advice?
- actionability: Can the candidate apply the suggested improvements directly?
- coverage: Does the review include a numeric score, strengths, and improvements?

Original Resume:
{resume_text}

Agent Review:
{review}

Return your evaluation in the required structured format.""",
}


def seed():
    for name, content in PROMPTS.items():
        template = PromptTemplate.from_template(content)
        try:
            client.push_prompt(name, object=template)
            print(f"[push] {name}")
        except Exception as e:
            print(f"[fail] {name}: {e}")


if __name__ == "__main__":
    seed()
    print("\nDone.")
