from app.llm.validator import validate_response


sample = """
{
    "label": "Request",
    "reason": "Customer requested replacement."
}
"""


success, result, category = validate_response(
    "classification",
    sample,
)

print("\n========== RESULT ==========\n")

print("Success :", success)

print("Category:", category)

print("Result:")

print(result)