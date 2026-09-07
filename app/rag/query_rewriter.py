REWRITE_RULES = {
    "What is a Python variable?":
        "What is a Python variable and what does it store?",
    "What is a Python module?":
        "What is a Python module and how is it used to organize Python code?",
    "What is a Git branch?":
        "What is a Git branch and how is it used for separate lines of development?",
}


def rewrite_query(question: str) -> str:
    if not question or not question.strip():
        raise ValueError("question cannot be empty")

    question = question.strip()

    return REWRITE_RULES.get(question, question)