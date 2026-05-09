from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain.agents import create_agent as create_react_agent
from langfuse.langchain import CallbackHandler

load_dotenv(".env")

langfuse_handler = CallbackHandler()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


@tool
def score_resume(resume_text: str) -> str:
    """Score a resume out of 10 based on clarity, structure, and completeness."""
    prompt = f"""
    Score the following resume out of 10. Consider:
    - Clarity and writing quality
    - Structure and formatting
    - Completeness (contact info, experience, skills, education)

    Resume:
    {resume_text}

    Respond with: Score: X/10 followed by brief reasoning.
    """
    response = llm.invoke(prompt)
    return response.content


@tool
def identify_strengths(resume_text: str) -> str:
    """Identify the top 3 strengths in the resume."""
    prompt = f"""
    Identify the top 3 strengths in this resume. Be specific.

    Resume:
    {resume_text}

    List them as:
    1. ...
    2. ...
    3. ...
    """
    response = llm.invoke(prompt)
    return response.content


@tool
def suggest_improvements(resume_text: str) -> str:
    """Suggest the top 3 improvements for the resume."""
    prompt = f"""
    Suggest the top 3 improvements for this resume. Be actionable and specific.

    Resume:
    {resume_text}

    List them as:
    1. ...
    2. ...
    3. ...
    """
    response = llm.invoke(prompt)
    return response.content


tools = [score_resume, identify_strengths, suggest_improvements]

agent = create_react_agent(llm, tools)


def review_resume(resume_text: str) -> str:
    result = agent.invoke(
        {"messages": [("human", f"Please review this resume:\n\n{resume_text}")]},
        config={"callbacks": [langfuse_handler]},
    )
    return result["messages"][-1].content


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
