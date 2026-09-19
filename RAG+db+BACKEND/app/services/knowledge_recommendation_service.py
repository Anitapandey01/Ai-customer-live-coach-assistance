from app.services.rag_service import generate_rag_answer


# --------------------------------------------------
# Get latest customer message
# --------------------------------------------------

def get_latest_customer_message(
    conversation: list[dict],
) -> str:
    """
    Get the latest non-empty message sent by the customer.
    """

    for message in reversed(conversation):

        if message.get("sender") == "customer":

            text = message.get("text", "").strip()

            if text:
                return text

    return ""


# --------------------------------------------------
# Build conversation context
# --------------------------------------------------

def build_conversation_context(
    conversation: list[dict],
) -> str:
    """
    Build context from previous customer and assistant
    messages.

    The latest customer message is excluded because it
    will be added separately as the current message.
    """

    if not conversation:
        return ""

    latest_customer_index = -1

    for index in range(
        len(conversation) - 1,
        -1,
        -1
    ):

        if (
            conversation[index].get("sender")
            == "customer"
            and conversation[index].get("text", "").strip()
        ):
            latest_customer_index = index
            break

    if latest_customer_index <= 0:
        return ""

    previous_messages = conversation[
        :latest_customer_index
    ]

    context_parts = []

    for message in previous_messages:

        sender = message.get(
            "sender",
            ""
        ).strip()

        text = message.get(
            "text",
            ""
        ).strip()

        if not text:
            continue

        if sender == "customer":
            context_parts.append(
                f"Customer: {text}"
            )

        elif sender == "assistant":
            context_parts.append(
                f"Assistant: {text}"
            )

    return "\n".join(context_parts)


# --------------------------------------------------
# Build context-aware RAG query
# --------------------------------------------------

def build_knowledge_query(
    conversation: list[dict],
) -> str:
    """
    Build a retrieval query using the current customer
    message and previous conversation context.
    """

    customer_message = get_latest_customer_message(
        conversation
    )

    if not customer_message:
        return ""

    conversation_context = build_conversation_context(
        conversation
    )

    if not conversation_context:
        return customer_message

    return f"""
Previous conversation:

{conversation_context}

Current customer message:

{customer_message}

Retrieve support knowledge relevant to the current
customer message.

Use the previous conversation only to understand
references, context, and the customer's ongoing issue.
Prioritize knowledge that directly helps resolve the
current customer issue.
""".strip()


# --------------------------------------------------
# Query keyword extraction
# --------------------------------------------------

def extract_query_keywords(
    conversation: list[dict],
) -> set[str]:
    """
    Extract simple keywords from the current customer
    message and previous customer context.

    Common stop words are removed so that generic words
    do not influence source ranking.
    """

    customer_message = get_latest_customer_message(
        conversation
    )

    conversation_context = build_conversation_context(
        conversation
    )

    combined_text = (
        f"{conversation_context} "
        f"{customer_message}"
    ).lower()

    stop_words = {
        "i",
        "me",
        "my",
        "we",
        "our",
        "you",
        "your",
        "the",
        "a",
        "an",
        "and",
        "or",
        "but",
        "is",
        "are",
        "was",
        "were",
        "to",
        "for",
        "of",
        "in",
        "on",
        "at",
        "it",
        "this",
        "that",
        "what",
        "how",
        "why",
        "can",
        "could",
        "would",
        "do",
        "does",
        "did",
        "have",
        "has",
        "had",
        "be",
        "been",
        "still",
        "please",
        "want",
        "need",
        "know",
        "tell",
        "me",
        "information",
        "provide",
    }

    words = set()

    for word in combined_text.replace(
        ".", " "
    ).replace(
        ",", " "
    ).replace(
        "?", " "
    ).replace(
        "!", " "
    ).split():

        word = word.strip()

        if (
            len(word) >= 3
            and word not in stop_words
        ):
            words.add(word)

    return words


# --------------------------------------------------
# Source relevance scoring
# --------------------------------------------------

def calculate_source_score(
    source: dict,
    query_keywords: set[str],
) -> float:
    """
    Calculate a ranking score for a retrieved source.

    Semantic distance remains the primary signal.
    Keyword matches in document metadata provide an
    additional relevance signal.

    Lower final score is better.
    """

    distance = source.get(
        "distance",
        999.0
    )

    try:
        distance = float(distance)
    except (TypeError, ValueError):
        distance = 999.0

    document_name = str(
        source.get(
            "document_name",
            ""
        )
    ).lower()

    document_type = str(
        source.get(
            "document_type",
            ""
        )
    ).lower()

    metadata_text = (
        f"{document_name} {document_type}"
    )

    matched_keywords = 0

    for keyword in query_keywords:

        if keyword in metadata_text:
            matched_keywords += 1

    # Stronger metadata match receives a ranking boost.
    keyword_bonus = matched_keywords * 0.15

    return distance - keyword_bonus


# --------------------------------------------------
# Rerank retrieved sources
# --------------------------------------------------

def rerank_sources(
    sources: list[dict],
    conversation: list[dict],
) -> list[dict]:
    """
    Rerank retrieved sources using semantic distance
    together with query/context keyword matches.

    Only the best five recommendations are returned.
    """

    query_keywords = extract_query_keywords(
        conversation
    )

    scored_sources = []

    for source in sources:

        score = calculate_source_score(
            source=source,
            query_keywords=query_keywords,
        )

        source_copy = dict(source)

        source_copy["recommendation_score"] = round(
            score,
            6,
        )

        scored_sources.append(
            source_copy
        )

    scored_sources.sort(
        key=lambda item: item[
            "recommendation_score"
        ]
    )

    return scored_sources[:5]


# --------------------------------------------------
# Knowledge recommendation
# --------------------------------------------------

def get_knowledge_recommendation(
    conversation: list[dict],
) -> dict:
    """
    Retrieve contextually relevant support knowledge
    for the current customer conversation.

    Uses the existing RAG pipeline and then reranks
    retrieved sources using conversation-aware metadata
    matching.
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

    rag_question = build_knowledge_query(
        conversation
    )

    # Retrieve additional candidates so that the
    # recommendation layer has more sources to rank.
    rag_result = generate_rag_answer(
        question=rag_question,
        number_of_results=10,
    )

    retrieved_sources = rag_result.get(
        "sources",
        [],
    )

    sources = rerank_sources(
        sources=retrieved_sources,
        conversation=conversation,
    )

    return {
        "customer_query": customer_message,
        "answer": rag_result.get(
            "answer",
            "",
        ),
        "sources": sources,
    }