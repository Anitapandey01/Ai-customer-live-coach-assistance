from app.services.knowledge_recommendation_service import (
    get_knowledge_recommendation,
)


# --------------------------------------------------
# Task 5 - Sample Multi-Turn Support Conversations
# --------------------------------------------------

MULTI_TURN_SCENARIOS = [
    {
        "name": "Refund follow-up",
        "conversation": [
            {
                "sender": "customer",
                "text": "I requested a refund for my order yesterday.",
            },
            {
                "sender": "assistant",
                "text": (
                    "I can help you check the refund process "
                    "and required information."
                ),
            },
            {
                "sender": "customer",
                "text": (
                    "I am still waiting. What information do "
                    "I need to provide?"
                ),
            },
        ],
    },
    {
        "name": "Payment failure",
        "conversation": [
            {
                "sender": "customer",
                "text": (
                    "My payment was deducted but my order "
                    "was not created."
                ),
            },
            {
                "sender": "assistant",
                "text": (
                    "I will help you understand what happens "
                    "when a payment is deducted but an order "
                    "is not created."
                ),
            },
            {
                "sender": "customer",
                "text": (
                    "Will the deducted amount be refunded "
                    "automatically?"
                ),
            },
        ],
    },
    {
        "name": "Delivery delay",
        "conversation": [
            {
                "sender": "customer",
                "text": (
                    "My order was supposed to arrive today "
                    "but it has not arrived."
                ),
            },
            {
                "sender": "assistant",
                "text": (
                    "I can help you check the available "
                    "delivery information."
                ),
            },
            {
                "sender": "customer",
                "text": (
                    "How long should I wait before contacting "
                    "support?"
                ),
            },
        ],
    },
    {
        "name": "Account access issue",
        "conversation": [
            {
                "sender": "customer",
                "text": "I cannot access my account.",
            },
            {
                "sender": "assistant",
                "text": (
                    "I can help you troubleshoot the account "
                    "access issue."
                ),
            },
            {
                "sender": "customer",
                "text": (
                    "I have already tried logging in again, "
                    "but I still cannot access it."
                ),
            },
        ],
    },
]


# --------------------------------------------------
# Multi-turn context evaluation
# --------------------------------------------------

def test_task5_multiturn_scenarios():

    print()
    print("=" * 80)
    print("TASK 5 - MULTI-TURN CONVERSATION DEMONSTRATION")
    print("=" * 80)

    for scenario in MULTI_TURN_SCENARIOS:

        result = get_knowledge_recommendation(
            conversation=scenario["conversation"]
        )

        print()
        print("-" * 80)
        print(f"Scenario: {scenario['name']}")

        print()
        print("Conversation:")

        for message in scenario["conversation"]:
            print(
                f"  {message['sender'].capitalize()}: "
                f"{message['text']}"
            )

        print()
        print(
            f"Current customer query: "
            f"{result['customer_query']}"
        )

        print()
        print("Recommended knowledge:")

        sources = result.get("sources", [])

        if not sources:
            print("  No relevant knowledge sources returned.")

        for index, source in enumerate(
            sources,
            start=1,
        ):
            print(
                f"  {index}. "
                f"{source.get('document_name')} | "
                f"{source.get('document_type')} | "
                f"page={source.get('page_number')} | "
                f"distance={source.get('distance')}"
            )

        assert result["customer_query"] == (
            scenario["conversation"][-1]["text"]
        )

        assert isinstance(
            result["sources"],
            list,
        )

        assert len(result["sources"]) <= 5

    print()
    print("=" * 80)
    print("MULTI-TURN SCENARIO TEST PASSED")
    print("=" * 80)