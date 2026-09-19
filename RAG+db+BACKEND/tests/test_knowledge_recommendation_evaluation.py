from app.services.knowledge_recommendation_service import (
    get_knowledge_recommendation,
)


# --------------------------------------------------
# Task 5 Evaluation Scenarios
# --------------------------------------------------

EVALUATION_SCENARIOS = [
    {
        "name": "Refund request",
        "conversation": [
            {
                "sender": "customer",
                "text": "I want to know if I can get a refund for my order.",
            }
        ],
        "expected_keywords": ["refund", "return"],
    },
    {
        "name": "Order cancellation",
        "conversation": [
            {
                "sender": "customer",
                "text": "I want to cancel my order.",
            }
        ],
        "expected_keywords": ["cancel"],
    },
    {
        "name": "Delayed order",
        "conversation": [
            {
                "sender": "customer",
                "text": "My order is delayed and has not arrived yet.",
            }
        ],
        "expected_keywords": ["delivery", "order"],
    },
    {
        "name": "Payment issue",
        "conversation": [
            {
                "sender": "customer",
                "text": "My payment was deducted but the order is not showing.",
            }
        ],
        "expected_keywords": ["payment"],
    },
    {
        "name": "Account issue",
        "conversation": [
            {
                "sender": "customer",
                "text": "I cannot access my account.",
            }
        ],
        "expected_keywords": [
            "account",
            "login",
            "password",
        ],
    },
    {
        "name": "Delivery issue",
        "conversation": [
            {
                "sender": "customer",
                "text": (
                    "My package was supposed to arrive today "
                    "but it has not arrived."
                ),
            }
        ],
        "expected_keywords": ["delivery", "order"],
    },
    {
        "name": "Return or exchange",
        "conversation": [
            {
                "sender": "customer",
                "text": (
                    "I want to return this product and exchange "
                    "it for another one."
                ),
            }
        ],
        "expected_keywords": ["return", "exchange"],
    },
    {
        "name": "Refund process inquiry",
        "conversation": [
            {
                "sender": "customer",
                "text": "Could you explain how your refund process works?",
            }
        ],
        "expected_keywords": ["refund", "return"],
    },
    {
        "name": "Frustrated customer",
        "conversation": [
            {
                "sender": "customer",
                "text": (
                    "This is extremely frustrating. "
                    "Nobody has helped me."
                ),
            }
        ],
        "expected_keywords": ["support", "faq"],
    },
    {
        "name": "Multi-turn refund conversation",
        "conversation": [
            {
                "sender": "customer",
                "text": "I requested a refund yesterday.",
            },
            {
                "sender": "assistant",
                "text": (
                    "Please wait while we check your refund request."
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
        "expected_keywords": [
            "refund",
            "return",
        ],
    },
]


# --------------------------------------------------
# Helpers
# --------------------------------------------------

def get_source_text(source):
    """
    Combine searchable fields from a retrieved source.
    """

    return " ".join(
        str(source.get(field, ""))
        for field in [
            "document_name",
            "document_type",
        ]
    ).lower()


def get_matched_keywords(source, expected_keywords):
    """
    Return expected keywords found in a source.
    """

    source_text = get_source_text(source)

    return [
        keyword
        for keyword in expected_keywords
        if keyword.lower() in source_text
    ]


def evaluate_result(result, expected_keywords):
    """
    Calculate retrieval metrics for one scenario.
    """

    sources = result.get("sources", [])

    matched_keywords = set()
    relevant_sources = 0

    for source in sources:

        matches = get_matched_keywords(
            source,
            expected_keywords,
        )

        if matches:
            relevant_sources += 1
            matched_keywords.update(matches)

    hit_at_5 = relevant_sources > 0

    irrelevant_sources = len(sources) - relevant_sources

    return {
        "hit_at_5": hit_at_5,
        "matched_keywords": sorted(matched_keywords),
        "relevant_sources": relevant_sources,
        "irrelevant_sources": irrelevant_sources,
        "total_sources": len(sources),
    }


# --------------------------------------------------
# Main retrieval evaluation
# --------------------------------------------------

def test_knowledge_recommendation_evaluation():

    results = []

    for scenario in EVALUATION_SCENARIOS:

        result = get_knowledge_recommendation(
            conversation=scenario["conversation"]
        )

        metrics = evaluate_result(
            result,
            scenario["expected_keywords"],
        )

        results.append(
            {
                "name": scenario["name"],
                "metrics": metrics,
                "sources": result.get("sources", []),
                "query": result.get(
                    "customer_query",
                    "",
                ),
            }
        )

    # --------------------------------------------------
    # Overall metrics
    # --------------------------------------------------

    total_scenarios = len(results)

    hit_count = sum(
        1
        for item in results
        if item["metrics"]["hit_at_5"]
    )

    total_relevant_sources = sum(
        item["metrics"]["relevant_sources"]
        for item in results
    )

    total_irrelevant_sources = sum(
        item["metrics"]["irrelevant_sources"]
        for item in results
    )

    total_sources = sum(
        item["metrics"]["total_sources"]
        for item in results
    )

    hit_at_5_percentage = (
        hit_count / total_scenarios * 100
        if total_scenarios
        else 0
    )

    relevance_percentage = (
        total_relevant_sources / total_sources * 100
        if total_sources
        else 0
    )

    # --------------------------------------------------
    # Print detailed evaluation
    # --------------------------------------------------

    print()
    print("=" * 80)
    print("TASK 5 - KNOWLEDGE RECOMMENDATION EVALUATION")
    print("=" * 80)

    for item in results:

        metrics = item["metrics"]

        print()
        print("-" * 80)
        print(f"Scenario: {item['name']}")
        print(f"Query: {item['query']}")

        print(
            f"Hit@5: "
            f"{'PASS' if metrics['hit_at_5'] else 'MISS'}"
        )

        print(
            f"Matched keywords: "
            f"{metrics['matched_keywords']}"
        )

        print(
            f"Relevant sources: "
            f"{metrics['relevant_sources']}"
        )

        print(
            f"Irrelevant sources: "
            f"{metrics['irrelevant_sources']}"
        )

        print("Retrieved sources:")

        for index, source in enumerate(
            item["sources"],
            start=1,
        ):
            print(
                f"  {index}. "
                f"{source.get('document_name')} | "
                f"{source.get('document_type')} | "
                f"distance={source.get('distance')}"
            )

    # --------------------------------------------------
    # Overall summary
    # --------------------------------------------------

    print()
    print("=" * 80)
    print("OVERALL EVALUATION")
    print("=" * 80)

    print(
        f"Total scenarios: "
        f"{total_scenarios}"
    )

    print(
        f"Hit@5: "
        f"{hit_count}/{total_scenarios} "
        f"({hit_at_5_percentage:.2f}%)"
    )

    print(
        f"Relevant sources: "
        f"{total_relevant_sources}"
    )

    print(
        f"Irrelevant sources: "
        f"{total_irrelevant_sources}"
    )

    print(
        f"Source relevance rate: "
        f"{relevance_percentage:.2f}%"
    )

    print("=" * 80)

    # --------------------------------------------------
    # Structural validation
    # --------------------------------------------------

    assert total_scenarios == 10

    for item in results:

        assert item["query"]

        assert isinstance(
            item["sources"],
            list,
        )

        assert len(item["sources"]) <= 5


# --------------------------------------------------
# No customer message
# --------------------------------------------------

def test_no_customer_message():

    result = get_knowledge_recommendation(
        conversation=[
            {
                "sender": "assistant",
                "text": "How can I help you?",
            }
        ]
    )

    assert result["customer_query"] == ""
    assert result["sources"] == []
    assert "No customer message" in result["answer"]


# --------------------------------------------------
# Multi-turn context validation
# --------------------------------------------------

def test_previous_conversation_context_is_used():

    conversation = [
        {
            "sender": "customer",
            "text": "I requested a refund yesterday.",
        },
        {
            "sender": "assistant",
            "text": "I can help you check the refund request.",
        },
        {
            "sender": "customer",
            "text": "What information do I need to provide?",
        },
    ]

    result = get_knowledge_recommendation(
        conversation=conversation
    )

    assert (
        result["customer_query"]
        == "What information do I need to provide?"
    )

    assert len(result["sources"]) <= 5