from app.services.knowledge_recommendation_service import (
    get_latest_customer_message,
    build_conversation_context,
    build_knowledge_query,
    get_knowledge_recommendation,
)


# --------------------------------------------------
# Helper
# --------------------------------------------------

def make_conversation(*messages):
    return [
        {
            "sender": sender,
            "text": text,
        }
        for sender, text in messages
    ]


# --------------------------------------------------
# Latest customer message tests
# --------------------------------------------------

def test_get_latest_customer_message():
    conversation = make_conversation(
        ("customer", "My payment failed."),
        ("assistant", "Please check your payment method."),
        ("customer", "It still does not work."),
    )

    result = get_latest_customer_message(conversation)

    assert result == "It still does not work."


def test_get_latest_customer_message_ignores_assistant():
    conversation = make_conversation(
        ("customer", "I need a refund."),
        ("assistant", "I can help with that."),
    )

    result = get_latest_customer_message(conversation)

    assert result == "I need a refund."


def test_get_latest_customer_message_empty_conversation():
    result = get_latest_customer_message([])

    assert result == ""


def test_get_latest_customer_message_ignores_empty_messages():
    conversation = [
        {
            "sender": "customer",
            "text": "",
        },
        {
            "sender": "customer",
            "text": "I need help.",
        },
    ]

    result = get_latest_customer_message(conversation)

    assert result == "I need help."


# --------------------------------------------------
# Conversation context tests
# --------------------------------------------------

def test_build_conversation_context():
    conversation = make_conversation(
        ("customer", "My payment failed."),
        ("assistant", "Please check your payment method."),
        ("customer", "I tried again."),
    )

    result = build_conversation_context(conversation)

    assert "Customer: My payment failed." in result
    assert (
        "Assistant: Please check your payment method."
        in result
    )
    assert "Customer: I tried again." not in result


def test_build_conversation_context_empty():
    result = build_conversation_context([])

    assert result == ""


def test_build_conversation_context_single_customer_message():
    conversation = make_conversation(
        ("customer", "I need a refund."),
    )

    result = build_conversation_context(conversation)

    assert result == ""


# --------------------------------------------------
# Context-aware query tests
# --------------------------------------------------

def test_build_knowledge_query_without_context():
    conversation = make_conversation(
        ("customer", "What is the refund policy?"),
    )

    result = build_knowledge_query(conversation)

    assert result == "What is the refund policy?"


def test_build_knowledge_query_with_context():
    conversation = make_conversation(
        ("customer", "I want a refund."),
        (
            "assistant",
            "I can help you check the refund requirements.",
        ),
        (
            "customer",
            "What information do I need to provide?",
        ),
    )

    result = build_knowledge_query(conversation)

    assert "Previous conversation:" in result
    assert "I want a refund." in result
    assert (
        "I can help you check the refund requirements."
        in result
    )
    assert "Current customer message:" in result
    assert (
        "What information do I need to provide?"
        in result
    )


def test_build_knowledge_query_preserves_current_message():
    conversation = make_conversation(
        ("customer", "My order is delayed."),
        (
            "assistant",
            "I can help check the delivery status.",
        ),
        (
            "customer",
            "When will it arrive?",
        ),
    )

    result = build_knowledge_query(conversation)

    assert (
        "Prioritize knowledge that directly helps resolve"
        in result
    )

    assert (
        "current customer issue."
        in result.replace("\n", " ")
    )

    assert "When will it arrive?" in result


# --------------------------------------------------
# Real recommendation service tests
# --------------------------------------------------

def test_refund_recommendation_returns_sources():
    conversation = make_conversation(
        (
            "customer",
            "What is the refund policy?",
        ),
    )

    result = get_knowledge_recommendation(conversation)

    assert result["customer_query"] == (
        "What is the refund policy?"
    )

    assert isinstance(result["answer"], str)

    assert isinstance(result["sources"], list)

    assert 0 <= len(result["sources"]) <= 5


def test_payment_recommendation_returns_sources():
    conversation = make_conversation(
        (
            "customer",
            "My payment failed and I cannot complete my order.",
        ),
    )

    result = get_knowledge_recommendation(conversation)

    assert result["customer_query"] == (
        "My payment failed and I cannot complete my order."
    )

    assert isinstance(result["sources"], list)

    assert len(result["sources"]) <= 5


def test_delivery_recommendation_returns_sources():
    conversation = make_conversation(
        (
            "customer",
            "My delivery is delayed. When will my order arrive?",
        ),
    )

    result = get_knowledge_recommendation(conversation)

    assert result["customer_query"] == (
        "My delivery is delayed. When will my order arrive?"
    )

    assert isinstance(result["sources"], list)

    assert len(result["sources"]) <= 5


# --------------------------------------------------
# Multi-turn recommendation test
# --------------------------------------------------

def test_multiturn_recommendation_uses_context():
    conversation = make_conversation(
        (
            "customer",
            "I want a refund for my order.",
        ),
        (
            "assistant",
            "I can help you check the refund requirements.",
        ),
        (
            "customer",
            "What information do I need to provide?",
        ),
    )

    result = get_knowledge_recommendation(conversation)

    assert result["customer_query"] == (
        "What information do I need to provide?"
    )

    assert isinstance(result["answer"], str)

    assert isinstance(result["sources"], list)

    assert len(result["sources"]) <= 5


# --------------------------------------------------
# No customer message
# --------------------------------------------------

def test_recommendation_without_customer_message():
    conversation = [
        {
            "sender": "assistant",
            "text": "How can I help you?",
        }
    ]

    result = get_knowledge_recommendation(conversation)

    assert result["customer_query"] == ""

    assert result["sources"] == []

    assert (
        "No customer message is available"
        in result["answer"]
    )


# --------------------------------------------------
# Source metadata validation
# --------------------------------------------------

def test_recommendation_sources_have_metadata():
    conversation = make_conversation(
        (
            "customer",
            "What is the refund policy?",
        ),
    )

    result = get_knowledge_recommendation(conversation)

    for source in result["sources"]:
        assert "chunk_id" in source
        assert "document_name" in source
        assert "document_type" in source
        assert "version" in source
        assert "page_number" in source
        assert "distance" in source


# --------------------------------------------------
# Recommendation ranking validation
# --------------------------------------------------

def test_recommendation_sources_are_ranked_by_distance():
    conversation = make_conversation(
        (
            "customer",
            "What is the refund policy?",
        ),
    )

    result = get_knowledge_recommendation(conversation)

    distances = [
        source["distance"]
        for source in result["sources"]
    ]

    assert distances == sorted(distances)


# --------------------------------------------------
# No-answer knowledge test
# --------------------------------------------------

def test_unrelated_query_returns_no_knowledge_answer():
    conversation = make_conversation(
        (
            "customer",
            "What is the policy for teleporting my order "
            "to another planet?",
        ),
    )

    result = get_knowledge_recommendation(conversation)

    assert result["customer_query"] == (
        "What is the policy for teleporting my order "
        "to another planet?"
    )

    assert isinstance(result["answer"], str)

    assert (
        "information is not available"
        in result["answer"].lower()
    )

    assert len(result["sources"]) <= 5