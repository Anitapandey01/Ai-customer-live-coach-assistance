from app.services.rag_service import generate_rag_answer


# --------------------------------------------------
# Build customer query from conversation
# --------------------------------------------------

def get_latest_customer_message(
    conversation: list[dict],
) -> str:
    """
    Get the latest message sent by the customer.
    """

    for message in reversed(conversation):
        if message.get("sender") == "customer":
            text = message.get("text", "").strip()

            if text:
                return text

    return ""


# --------------------------------------------------
# Knowledge recommendation
# --------------------------------------------------

def get_knowledge_recommendation(
    conversation: list[dict],
) -> dict:
    """
    Retrieve relevant support knowledge for the
    customer's latest message using the existing RAG
    pipeline.
    """

    customer_message = get_latest_customer_message(
        conversation
    )

    if not customer_message:
        return {
            "customer_query": "",
            "answer": (
                "No customer message is available "
                "for knowledge retrieval."
            ),
            "sources": [],
        }

    rag_result = generate_rag_answer(
        question=customer_message,
        number_of_results=3,
    )

    return {
        "customer_query": customer_message,
        "answer": rag_result.get(
            "answer",
            "",
        ),
        "sources": rag_result.get(
            "sources",
            [],
        ),
    }