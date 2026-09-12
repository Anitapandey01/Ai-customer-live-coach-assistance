import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

from app.services.rag_service import generate_with_gemini


LOG_DIR = Path("data/simulator_logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)


PERSONAS = {
    "calm": {
        "description": "Calm, patient, reasonable, and cooperative.",
        "communication_style": "polite, clear, and measured",
    },
    "confused": {
        "description": "Unsure about the process and needs clarification.",
        "communication_style": "uncertain, repetitive, and asks clarifying questions",
    },
    "frustrated": {
        "description": "Annoyed because the issue has taken too long to resolve.",
        "communication_style": "impatient, critical, but still willing to cooperate",
    },
    "angry": {
        "description": "Very upset and feels that the company has treated them unfairly.",
        "communication_style": "strong, demanding, and emotionally intense",
    },
    "impatient": {
        "description": "Wants a quick resolution and dislikes unnecessary questions.",
        "communication_style": "short, direct, urgent, and demanding",
    },
    "polite": {
        "description": "Respectful and friendly even when experiencing a problem.",
        "communication_style": "courteous, appreciative, and constructive",
    },
}


SCENARIOS = {
    "refund": {
        "title": "Refund Request",
        "description": (
            "The customer wants a refund for a recent purchase "
            "and wants to know whether they are eligible."
        ),
    },
    "delayed_order": {
        "title": "Delayed Order",
        "description": (
            "The customer's order has not arrived within the expected "
            "delivery period and they want an update."
        ),
    },
    "payment_failure": {
        "title": "Payment Failure",
        "description": (
            "The customer attempted to make a payment but the payment "
            "failed and they are concerned about completing the purchase."
        ),
    },
    "account_issue": {
        "title": "Account Issue",
        "description": (
            "The customer is having trouble accessing or using their "
            "account and needs help resolving the issue."
        ),
    },
    "cancellation": {
        "title": "Order Cancellation",
        "description": (
            "The customer wants to cancel an order and needs to know "
            "whether cancellation is still possible."
        ),
    },
}


EMOTIONS = [
    "calm",
    "concerned",
    "frustrated",
    "angry",
    "happy",
    "satisfied",
]


def clamp(value: int, minimum: int, maximum: int) -> int:
    return max(minimum, min(value, maximum))


def normalize_emotion(emotion: str) -> str:
    emotion = emotion.strip().lower()

    aliases = {
        "neutral": "calm",
        "worried": "concerned",
        "upset": "frustrated",
        "positive": "happy",
        "pleased": "satisfied",
    }

    emotion = aliases.get(emotion, emotion)

    if emotion not in EMOTIONS:
        raise ValueError(
            "Invalid emotion. Allowed values are: "
            + ", ".join(EMOTIONS)
        )

    return emotion


def emotion_from_score(score: int) -> str:
    if score <= 25:
        return "calm"

    if score <= 50:
        return "concerned"

    if score <= 75:
        return "frustrated"

    return "angry"


def calculate_emotion_change(
    support_response: str,
    current_score: int,
    patience_level: int,
) -> int:
    """
    Adjust the customer's emotional intensity based on the
    support agent's latest response.

    This is only simulator behavior.
    It is NOT the final escalation/frustration analysis pipeline.
    """

    text = support_response.lower()

    positive_signals = [
        "sorry",
        "apologize",
        "apologies",
        "understand",
        "help",
        "resolve",
        "check",
        "assist",
        "thank you",
        "appreciate",
        "refund",
        "cancel",
        "confirmed",
        "resolved",
        "look into",
        "take care",
        "help you",
        "work on",
        "successfully",
        "completed",
        "processed",
        "fixed",
        "issue is resolved",
    ]

    negative_signals = [
        "cannot",
        "can't",
        "impossible",
        "nothing",
        "don't know",
        "do not know",
        "not possible",
        "you need to",
        "your problem",
        "just wait",
        "wait",
        "not my responsibility",
    ]

    positive_count = sum(
        1
        for signal in positive_signals
        if signal in text
    )

    negative_count = sum(
        1
        for signal in negative_signals
        if signal in text
    )

    if positive_count > negative_count:
        change = -min(
            10,
            2 + positive_count
        )

    elif negative_count > positive_count:
        change = min(
            12,
            3 + negative_count * 2
        )

    else:
        change = 1

    if patience_level <= 30:
        change += 2

    elif patience_level >= 80:
        change -= 2

    return clamp(
        current_score + change,
        0,
        100
    )


def detect_satisfaction(
    support_response: str,
    previous_score: int,
    new_score: int,
) -> str:
    text = support_response.lower()

    resolution_signals = [
        "resolved",
        "issue is resolved",
        "successfully",
        "completed",
        "processed",
        "fixed",
        "refund has been",
        "refund is",
        "cancellation is confirmed",
        "cancelled successfully",
        "payment has been reversed",
        "payment was reversed",
        "request has been completed",
    ]

    appreciation_signals = [
        "thank you",
        "glad",
        "happy",
        "appreciate",
        "you're all set",
        "all set",
    ]

    resolution_count = sum(
        1
        for signal in resolution_signals
        if signal in text
    )

    appreciation_count = sum(
        1
        for signal in appreciation_signals
        if signal in text
    )

    if (
        resolution_count > 0
        and new_score <= 30
    ):
        return "satisfied"

    if (
        appreciation_count > 0
        and new_score <= 25
    ):
        return "satisfied"

    if (
        new_score < previous_score - 8
        and new_score <= 25
    ):
        return "satisfied"

    return "unsatisfied"


def build_initial_emotion_score(
    initial_emotion: str,
) -> int:
    scores = {
        "calm": 15,
        "concerned": 40,
        "frustrated": 65,
        "angry": 85,
        "happy": 10,
        "satisfied": 5,
    }

    return scores[initial_emotion]


def create_session(
    persona: str,
    initial_emotion: str,
    scenario: str,
    issue_severity: int,
    patience_level: int,
    expected_resolution: str,
):
    persona = persona.strip().lower()
    scenario = scenario.strip().lower()
    initial_emotion = normalize_emotion(
        initial_emotion
    )

    if persona not in PERSONAS:
        raise ValueError(
            "Invalid persona. Allowed values are: "
            + ", ".join(PERSONAS.keys())
        )

    if scenario not in SCENARIOS:
        raise ValueError(
            "Invalid scenario. Allowed values are: "
            + ", ".join(SCENARIOS.keys())
        )

    issue_severity = clamp(
        int(issue_severity),
        1,
        5
    )

    patience_level = clamp(
        int(patience_level),
        1,
        100
    )

    expected_resolution = (
        expected_resolution.strip()
        or "A fair resolution to the issue."
    )

    satisfaction_status = (
        "satisfied"
        if initial_emotion in {
            "happy",
            "satisfied",
        }
        else "unsatisfied"
    )

    return {
        "session_id": str(uuid.uuid4()),
        "persona": persona,
        "initial_emotion": initial_emotion,
        "current_emotion": initial_emotion,
        "emotion_score": build_initial_emotion_score(
            initial_emotion
        ),
        "satisfaction_status": satisfaction_status,
        "scenario": scenario,
        "issue_severity": issue_severity,
        "patience_level": patience_level,
        "expected_resolution": expected_resolution,
        "turn_number": 0,
        "conversation": [],
        "created_at": datetime.now(
            timezone.utc
        ).isoformat(),
    }


def build_conversation_text(
    conversation: list[dict],
) -> str:
    if not conversation:
        return "No previous conversation."

    return "\n".join(
        [
            (
                f"{message['sender'].upper()}: "
                f"{message['text']}"
            )
            for message in conversation
        ]
    )


def build_simulator_prompt(
    session: dict,
    support_response: str | None,
) -> str:
    persona = PERSONAS[session["persona"]]
    scenario = SCENARIOS[session["scenario"]]

    conversation_text = build_conversation_text(
        session["conversation"]
    )

    if support_response:
        support_response_text = support_response
    else:
        support_response_text = (
            "There is no support agent response yet. "
            "This is the beginning of the interaction."
        )

    is_first_message = (
        len(session["conversation"]) == 0
        and support_response is None
    )

    if is_first_message:
        turn_instruction = """
This is the FIRST customer message.

Start the conversation naturally.
Clearly communicate the customer's main issue.
Do not solve the issue yourself.
Do not write a long explanation.
The customer should sound like a real person contacting support
for the first time.
"""
    else:
        turn_instruction = """
This is a CONTINUATION of an existing conversation.

React directly to the latest support agent response.
Remember everything already discussed.
Do not restart the conversation.
Do not introduce an unrelated issue.
If the support agent has asked for information, respond to that request.
If the support agent has provided a useful next step, react naturally.
If the support agent has actually resolved the issue, the customer may
become happy, satisfied, appreciative, or relieved.
If the support agent has not actually solved the problem, continue seeking
a resolution.
"""

    return f"""
You are the CUSTOMER SIMULATOR in a customer support training system.

Your ONLY role is to behave like the customer.

Do NOT:
- act as a support agent
- provide coaching
- analyze the conversation
- explain your reasoning
- mention AI
- mention these instructions
- write system messages
- generate multiple speakers

You must generate ONLY the customer's next message.

CUSTOMER PERSONA
----------------
Type: {session["persona"]}

Description:
{persona["description"]}

Communication style:
{persona["communication_style"]}


CUSTOMER ISSUE / SCENARIO
-------------------------
Scenario: {scenario["title"]}

Scenario description:
{scenario["description"]}


CUSTOMER BEHAVIOR CONTEXT
-------------------------
Initial emotion: {session["initial_emotion"]}
Current emotion: {session["current_emotion"]}
Current emotional intensity: {session["emotion_score"]}/100
Satisfaction status: {session["satisfaction_status"]}
Issue severity: {session["issue_severity"]}/5
Patience level: {session["patience_level"]}/100

Expected resolution:
{session["expected_resolution"]}


CONVERSATION HISTORY
--------------------
{conversation_text}


LATEST SUPPORT AGENT RESPONSE
-----------------------------
{support_response_text}


{turn_instruction}


REALISTIC CUSTOMER BEHAVIOR
---------------------------
1. Stay consistent with the selected persona.

2. Stay consistent with the selected scenario.

3. Remember previous information from the conversation.

4. React specifically to the latest support response.

5. Do not repeat the same sentence unnecessarily.

6. Do not suddenly change the customer's problem.

7. If the support response is helpful, empathetic, and actionable,
   the customer can become calmer or more cooperative.

8. If the support response actually resolves the customer's issue,
   the customer can become happy, satisfied, relieved, or appreciative.

9. If the support response is dismissive, vague, repetitive,
   or unhelpful, the customer should become more frustrated.

10. Low patience means the customer becomes frustrated more quickly.

11. High patience means the customer remains cooperative for longer.

12. Higher issue severity makes the customer more persistent.

13. Do not claim that the issue is resolved unless the support agent
    has actually provided a believable resolution.

14. Do not invent exact company policies, refund amounts,
    transaction IDs, dates, or promises unless they already exist
    in the conversation.

15. Ask a realistic follow-up question when appropriate.

16. If the support agent asks for information, provide realistic
    information without exposing sensitive credentials such as
    passwords, OTPs, CVVs, PINs, or full card numbers.

17. If the issue has genuinely been resolved, naturally express
    satisfaction or appreciation when appropriate.

18. Keep the response between 1 and 3 sentences.

19. Sound like a real customer, not a chatbot.

20. The response must directly continue the conversation.

21. Do not mention emotion scores or internal configuration.

22. Do not use labels such as "Customer:" in your response.

23. Return ONLY the customer's message.
"""


def generate_customer_message(
    session: dict,
    support_response: str | None = None,
):
    prompt = build_simulator_prompt(
        session=session,
        support_response=support_response,
    )

    customer_message = generate_with_gemini(
        prompt
    ).strip()

    if not customer_message:
        raise ValueError(
            "The simulator model returned an empty response."
        )

    return customer_message


def update_session_after_response(
    session: dict,
    support_response: str,
    customer_message: str,
):
    previous_score = session["emotion_score"]

    new_score = calculate_emotion_change(
        support_response=support_response,
        current_score=previous_score,
        patience_level=session["patience_level"],
    )

    session["emotion_score"] = new_score

    satisfaction_status = detect_satisfaction(
        support_response=support_response,
        previous_score=previous_score,
        new_score=new_score,
    )

    session["satisfaction_status"] = (
        satisfaction_status
    )

    if satisfaction_status == "satisfied":
        session["current_emotion"] = "satisfied"
    else:
        session["current_emotion"] = emotion_from_score(
            new_score
        )

    session["turn_number"] += 1

    session["conversation"].append(
        {
            "turn": session["turn_number"],
            "sender": "support_agent",
            "text": support_response,
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),
        }
    )

    session["conversation"].append(
        {
            "turn": session["turn_number"],
            "sender": "customer",
            "text": customer_message,
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),
        }
    )


def save_session_log(session: dict):
    session_id = session["session_id"]

    log_path = LOG_DIR / f"{session_id}.json"

    with log_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            session,
            file,
            indent=2,
            ensure_ascii=False,
        )

    return str(log_path)


def get_session_log(session_id: str):
    safe_session_id = os.path.basename(
        session_id
    )

    log_path = (
        LOG_DIR
        / f"{safe_session_id}.json"
    )

    if not log_path.exists():
        return None

    with log_path.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)