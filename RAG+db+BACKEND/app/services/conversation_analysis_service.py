import json
import re

from app.services.rag_service import generate_with_gemini


DEFAULT_ANALYSIS = {
    "intent": "Unknown",
    "sentiment": "Neutral",
    "emotion": "Neutral",
    "frustration_level": 0,
    "satisfaction_trend": "Stable",
    "confidence": 0.0,
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
        data.get("emotion", "Neutral")
    ).strip().capitalize()

    satisfaction_trend = str(
        data.get("satisfaction_trend", "Stable")
    ).strip().capitalize()

    try:
        frustration_level = int(
            data.get("frustration_level", 0)
        )
    except (TypeError, ValueError):
        frustration_level = 0

    try:
        confidence = float(
            data.get("confidence", 0.0)
        )
    except (TypeError, ValueError):
        confidence = 0.0

    # Task 4 requires frustration level from 0 to 10.
    frustration_level = max(
        0,
        min(frustration_level, 10),
    )

    # Task 4 confidence is represented from 0 to 1.
    confidence = max(
        0.0,
        min(confidence, 1.0),
    )

    allowed_sentiments = {
        "Positive",
        "Neutral",
        "Negative",
    }

    allowed_emotions = {
        # Task 4 emotion categories
        "Happy",
        "Neutral",
        "Confused",
        "Worried",
        "Frustrated",
        "Angry",
        "Satisfied",

        # Backward-compatible categories already used
        # by the existing implementation.
        "Calm",
        "Concerned",
    }

    allowed_satisfaction_trends = {
        "Improving",
        "Declining",
        "Stable",
    }

    if sentiment not in allowed_sentiments:
        sentiment = "Neutral"

    if emotion not in allowed_emotions:
        emotion = "Neutral"

    if satisfaction_trend not in allowed_satisfaction_trends:
        satisfaction_trend = "Stable"

    return {
        "intent": intent,
        "sentiment": sentiment,
        "emotion": emotion,
        "frustration_level": frustration_level,
        "satisfaction_trend": satisfaction_trend,
        "confidence": round(confidence, 2),
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

Your task is to analyze the customer's current issue,
emotional state, frustration, sentiment, and satisfaction
trend from the complete conversation below.

Analyze ONLY the information present in the conversation.

Do not invent facts.

IMPORTANT:

You must consider the conversation history when making
the analysis.

Do not analyze the latest customer message completely
independently from previous messages.

CONVERSATION
------------
{conversation_text}

RETURN EXACTLY ONE JSON OBJECT

Use this structure:

{{
    "intent": "Refund Request",
    "sentiment": "Negative",
    "emotion": "Frustrated",
    "frustration_level": 8,
    "satisfaction_trend": "Declining",
    "confidence": 0.94
}}

FIELD RULES

1. intent

Identify the customer's main support intent.

Common intents include:

- Refund Request
- Order Cancellation
- Delayed Order
- Payment Issue
- Account Issue
- Delivery Issue
- Return or Exchange
- Complaint
- General Inquiry

Use the intent that best represents what the
customer is currently trying to resolve.

Do not create an unrelated intent.

2. sentiment

Choose exactly one:

- Positive
- Neutral
- Negative

Analyze the customer's current overall sentiment
based on the conversation.

3. emotion

Choose exactly one:

- Happy
- Neutral
- Confused
- Worried
- Frustrated
- Angry
- Satisfied

Use Happy when the customer expresses
happiness, excitement, appreciation, or delight.

Use Neutral when the customer is calm and does not
show a clearly identifiable positive, negative, or
strong emotional state.

Use Confused when the customer appears uncertain,
does not understand a process, or asks for clarification.

Use Worried when the customer expresses concern,
anxiety, or uncertainty about a problem but is not
strongly frustrated or angry.

Use Frustrated when the customer shows clear
annoyance, repeated complaints, or dissatisfaction.

Use Angry when the customer shows strong anger,
hostility, or severe dissatisfaction.

Use Satisfied when the customer clearly indicates
that their issue has been resolved or they are
satisfied with the support provided.

4. frustration_level

Give an integer from 0 to 10.

Consider:

- customer's wording
- repeated complaints
- urgency
- unresolved issue
- money/payment problems
- previous failed attempts
- dissatisfaction with support
- escalation requests

For a happy or satisfied customer, the frustration
level should normally be low.

0 means no meaningful frustration.

10 means extremely frustrated or angry.

5. satisfaction_trend

Analyze the conversation history and determine
whether customer satisfaction is currently:

- Improving
- Declining
- Stable

Use Improving when:

- the customer's issue appears to be getting resolved
- the support response is helpful
- the customer becomes more positive
- frustration decreases
- the customer expresses appreciation
- the customer becomes happy or satisfied

Use Declining when:

- the issue remains unresolved
- support responses are unhelpful
- the customer becomes more frustrated
- the customer repeats complaints
- the customer becomes more negative
- the customer asks for escalation
- frustration increases

Use Stable when:

- there is no clear improvement or decline
- the customer's emotional state remains relatively
  unchanged
- the conversation does not provide enough evidence
  for a meaningful change in satisfaction

IMPORTANT:

Satisfaction trend is about the CHANGE in the
customer's satisfaction across the conversation.

Do not determine the trend only from one message.

Examples:

Customer starts concerned and later says:
"Thank you, that solves my problem."

Result:
"satisfaction_trend": "Improving"

Customer starts frustrated and later says:
"I have explained this three times and nobody is
helping me."

Result:
"satisfaction_trend": "Declining"

Customer remains calm and continues asking normal
questions without a clear change:

Result:
"satisfaction_trend": "Stable"

6. confidence

Give a decimal number from 0 to 1 representing
how confident you are in this analysis.

Consider:

- how clearly the customer describes the problem
- how much relevant conversation evidence exists
- whether the intent is obvious
- whether sentiment is clearly expressed
- whether emotion is clearly expressed
- whether there is enough conversation history to
  determine satisfaction trend

Do NOT always return the same score.

For example:

- Very clear issue and strong evidence -> high confidence
  such as 0.90 to 1.00
- Somewhat unclear issue -> medium confidence
  such as 0.60 to 0.89
- Very vague message -> low confidence
  such as 0.00 to 0.59

IMPORTANT

If the customer becomes happy or satisfied after
receiving a helpful support response, reflect that
change in sentiment, emotion, frustration level,
and satisfaction trend.

If the customer becomes increasingly frustrated
because the issue remains unresolved, reflect that
change in sentiment, emotion, frustration level,
and satisfaction trend.

The analysis must change according to the actual
conversation.

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