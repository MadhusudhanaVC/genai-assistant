from app.llm.client import generate_response


def main():
    response = generate_response(
        "Explain Artificial Intelligence in one sentence."
    )

    print("\n===================================")
    print("Model :", response["model"])
    print(
        "Latency:",
        response["latency_seconds"],
        "seconds",
    )
    print("-----------------------------------")
    print(response["text"])
    print("===================================")


if __name__ == "__main__":
    main()