import json
import re

from app.services.rag_service import generate_with_gemini


DEFAULT_ESCALATION_RISK = {
    "risk_level": "Low",
    "risk_score": 0,
    "reasons": [],
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


def validate_escalation_risk(data: dict) -> dict:
    risk_level = str(
        data.get("risk_level", "Low")
    ).strip().capitalize()

    try:
        risk_score = int(
            data.get("risk_score", 0)
        )
    except (TypeError, ValueError):
        risk_score = 0

    reasons = data.get(
        "reasons",
        [],
    )

    if not isinstance(reasons, list):
        reasons = []

    reasons = [
        str(reason).strip()
        for reason in reasons
        if str(reason).strip()
    ]

    risk_score = max(
        0,
        min(risk_score, 100),
    )

    allowed_levels = {
        "Low",
        "Medium",
        "High",
    }

    if risk_level not in allowed_levels:
        if risk_score >= 70:
            risk_level = "High"
        elif risk_score >= 40:
            risk_level = "Medium"
        else:
            risk_level = "Low"

    return {
        "risk_level": risk_level,
        "risk_score": risk_score,
        "reasons": reasons[:5],
    }


def build_escalation_conversation(
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


def build_escalation_prompt(
    conversation: list[dict],
    analysis: dict,
) -> str:
    conversation_text = build_escalation_conversation(
        conversation
    )

    intent = analysis.get(
        "intent",
        "Unknown",
    )

    sentiment = analysis.get(
        "sentiment",
        "Neutral",
    )

    emotion = analysis.get(
        "emotion",
        "Calm",
    )

    frustration_level = analysis.get(
        "frustration_level",
        1,
    )

    return f"""
You are an Escalation Risk Monitoring Agent for a
customer support system.

Your task is to determine how likely the current
conversation is to require escalation.

Analyze ONLY the conversation and the provided
customer analysis.

Do not invent facts.

CONVERSATION
------------
{conversation_text}

CUSTOMER ANALYSIS
-----------------
Intent: {intent}
Sentiment: {sentiment}
Emotion: {emotion}
Frustration Level: {frustration_level}/10

Evaluate factors such as:

- customer frustration
- angry or strongly negative language
- repeated complaints
- unresolved issues
- previous failed support attempts
- money or payment problems
- urgent or serious requests
- customer dissatisfaction with support
- whether the support response addressed the issue
- whether the situation appears to be getting worse

IMPORTANT:

A calm customer asking a normal question should
usually have Low escalation risk.

A customer reporting a significant unresolved
problem may have Medium risk.

A highly frustrated customer, repeated unresolved
issue, previous failed support attempts, or serious
payment/problem escalation may have High risk.

The risk must change according to the actual
conversation.

Do not always return the same score.

Examples:

Initial payment problem:
Medium risk may be appropriate.

Customer later says the issue happened multiple
times and previous support did not help:
High risk may be appropriate.

Customer becomes satisfied after receiving a useful
resolution:
Risk should decrease.

Return exactly one JSON object:

{{
    "risk_level": "High",
    "risk_score": 82,
    "reasons": [
        "Customer reports that the issue has happened multiple times.",
        "Customer indicates that previous support did not resolve the issue."
    ]
}}

FIELD RULES

1. risk_level

Choose exactly one:

- Low
- Medium
- High

2. risk_score

A number from 0 to 100 representing escalation risk.

0 means very low risk.

100 means extremely high risk.

3. reasons

Provide 1 to 5 short reasons explaining the
current escalation risk.

Reasons must be based on actual conversation evidence.

Do not invent events that did not occur.

Return ONLY valid JSON.

Do not use markdown.

Do not mention AI, Gemini, prompts, RAG,
embeddings, or internal systems.
"""


def analyze_escalation_risk(
    conversation: list[dict],
    analysis: dict,
) -> dict:

    if not conversation:
        return DEFAULT_ESCALATION_RISK.copy()

    prompt = build_escalation_prompt(
        conversation=conversation,
        analysis=analysis,
    )

    response = generate_with_gemini(
        prompt
    )

    if not response:
        return DEFAULT_ESCALATION_RISK.copy()

    cleaned_response = clean_json_response(
        response
    )

    try:
        data = json.loads(
            cleaned_response
        )
    except json.JSONDecodeError:
        return DEFAULT_ESCALATION_RISK.copy()

    if not isinstance(data, dict):
        return DEFAULT_ESCALATION_RISK.copy()

    return validate_escalation_risk(
        data
    )