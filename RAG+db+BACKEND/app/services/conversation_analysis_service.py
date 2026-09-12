import json
import re

from app.services.rag_service import generate_with_gemini


DEFAULT_ANALYSIS = {
    "intent": "Unknown",
    "sentiment": "Neutral",
    "emotion": "Calm",
    "frustration_level": 1,
    "confidence_score": 0,
}


def clean_json_response(response: str) -> str:
    response = response.strip()

    response = re.sub(
        r"^```json\s*",
        "",
        response,
        flags=re.IGNORECASE,
    )

    response = re.sub(
        r"^```\s*",
        "",
        response,
    )

    response = re.sub(
        r"\s*```$",
        "",
        response,
    )

    return response.strip()


def validate_analysis(data: dict) -> dict:
    intent = str(
        data.get("intent", "Unknown")
    ).strip()

    sentiment = str(
        data.get("sentiment", "Neutral")
    ).strip().capitalize()

    emotion = str(
        data.get("emotion", "Calm")
    ).strip().capitalize()

    try:
        frustration_level = int(
            data.get("frustration_level", 1)
        )
    except (TypeError, ValueError):
        frustration_level = 1

    try:
        confidence_score = int(
            data.get("confidence_score", 0)
        )
    except (TypeError, ValueError):
        confidence_score = 0

    frustration_level = max(
        1,
        min(frustration_level, 10),
    )

    confidence_score = max(
        0,
        min(confidence_score, 100),
    )

    allowed_sentiments = {
        "Positive",
        "Neutral",
        "Negative",
    }

    allowed_emotions = {
        "Calm",
        "Concerned",
        "Frustrated",
        "Angry",
        "Happy",
        "Satisfied",
    }

    if sentiment not in allowed_sentiments:
        sentiment = "Neutral"

    if emotion not in allowed_emotions:
        emotion = "Calm"

    return {
        "intent": intent,
        "sentiment": sentiment,
        "emotion": emotion,
        "frustration_level": frustration_level,
        "confidence_score": confidence_score,
    }


def build_analysis_conversation(
    conversation: list[dict],
) -> str:
    if not conversation:
        return "No conversation available."

    messages = []

    for message in conversation:
        sender = message.get(
            "sender",
            "unknown",
        ).upper()

        text = message.get(
            "text",
            "",
        ).strip()

        if not text:
            continue

        messages.append(
            f"{sender}: {text}"
        )

    if not messages:
        return "No conversation available."

    return "\n".join(messages)


def build_analysis_prompt(
    conversation: list[dict],
) -> str:
    conversation_text = build_analysis_conversation(
        conversation
    )

    return f"""
You are an AI customer support conversation analysis agent.

Your task is to analyze the customer's current issue
and emotional state from the conversation below.

Analyze ONLY the information present in the conversation.

Do not invent facts.

CONVERSATION
------------
{conversation_text}

RETURN EXACTLY ONE JSON OBJECT

Use this structure:

{{
    "intent": "Payment Issue",
    "sentiment": "Negative",
    "emotion": "Frustrated",
    "frustration_level": 8,
    "confidence_score": 92
}}

FIELD RULES

1. intent

Identify the customer's main support intent.

Examples:
- Payment Issue
- Refund Request
- Delayed Order
- Order Cancellation
- Account Issue
- Delivery Issue
- Technical Issue

Do not create an unrelated intent.

2. sentiment

Choose exactly one:
- Positive
- Neutral
- Negative

3. emotion

Choose exactly one:
- Calm
- Concerned
- Frustrated
- Angry
- Happy
- Satisfied

Use Happy when the customer expresses
happiness, excitement, appreciation, or delight.

Use Satisfied when the customer clearly indicates
that their issue has been resolved or they are
satisfied with the support provided.

4. frustration_level

Give a number from 1 to 10.

Consider:
- customer's wording
- repeated complaints
- urgency
- unresolved issue
- money/payment problems
- previous failed attempts
- dissatisfaction with support

For a happy or satisfied customer, the frustration
level should normally be low.

1 means very calm, happy, or satisfied.

10 means extremely frustrated or angry.

5. confidence_score

Give a number from 0 to 100 representing how confident
you are in this analysis.

Consider:
- how clearly the customer describes the problem
- how much relevant conversation evidence exists
- whether the intent is obvious
- whether sentiment and emotion are clearly expressed

Do NOT always return the same score.

For example:
- Very clear issue and strong evidence -> high confidence
- Somewhat unclear issue -> medium confidence
- Very vague message -> low confidence

IMPORTANT

If the customer becomes happy or satisfied after
receiving a helpful support response, reflect that
change in sentiment and emotion.

Return ONLY valid JSON.

Do not use markdown.

Do not include explanations.

Do not include "Customer:" or "Agent:" outside the JSON.

Do not mention AI, Gemini, prompts, or internal systems.
"""


def analyze_conversation(
    conversation: list[dict],
) -> dict:
    if not conversation:
        return DEFAULT_ANALYSIS.copy()

    prompt = build_analysis_prompt(
        conversation
    )

    response = generate_with_gemini(
        prompt
    )

    if not response:
        return DEFAULT_ANALYSIS.copy()

    cleaned_response = clean_json_response(
        response
    )

    try:
        analysis = json.loads(
            cleaned_response
        )
    except json.JSONDecodeError:
        return DEFAULT_ANALYSIS.copy()

    if not isinstance(analysis, dict):
        return DEFAULT_ANALYSIS.copy()

    return validate_analysis(
        analysis
    )