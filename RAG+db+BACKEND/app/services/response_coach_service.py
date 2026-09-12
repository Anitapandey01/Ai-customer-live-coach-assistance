from app.services.rag_service import generate_with_gemini


# --------------------------------------------------
# Build conversation text
# --------------------------------------------------

def build_conversation_text(
    conversation: list[dict],
) -> str:
    """
    Convert the conversation history into readable text.
    """

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


# --------------------------------------------------
# Get latest customer message
# --------------------------------------------------

def get_latest_customer_message(
    conversation: list[dict],
) -> str:
    """
    Return the most recent customer message.
    """

    for message in reversed(conversation):

        if message.get("sender") == "customer":

            text = message.get(
                "text",
                "",
            ).strip()

            if text:
                return text

    return ""


# --------------------------------------------------
# Clean model response
# --------------------------------------------------

def clean_response(response: str) -> str:
    """
    Clean unnecessary markdown formatting from
    Gemini's response.
    """

    response = response.strip()

    if response.startswith("```"):
        lines = response.splitlines()

        if len(lines) >= 2:
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        response = "\n".join(lines).strip()

    return response


# --------------------------------------------------
# Build response coach prompt
# --------------------------------------------------

def build_response_coach_prompt(
    conversation: list[dict],
    analysis: dict,
    knowledge: dict,
) -> str:
    """
    Build the prompt for generating a support-agent
    suggested reply and coaching tip.
    """

    conversation_text = build_conversation_text(
        conversation
    )

    customer_message = get_latest_customer_message(
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

    knowledge_answer = knowledge.get(
        "answer",
        "",
    )

    sources = knowledge.get(
        "sources",
        [],
    )

    source_text = "\n".join(
        [
            (
                f"- {source.get('document_name')} "
                f"(version {source.get('version')}, "
                f"page {source.get('page_number')})"
            )
            for source in sources
        ]
    )

    if not source_text:
        source_text = "No knowledge source was retrieved."

    return f"""
You are a customer support response coaching agent.

Your job is to help a support agent respond to the
customer's latest message.

You must provide:

1. A professional suggested reply.
2. A short coaching tip for the support agent.

CONVERSATION
------------
{conversation_text}


LATEST CUSTOMER MESSAGE
-----------------------
{customer_message}


CURRENT ANALYSIS
----------------
Intent: {intent}
Sentiment: {sentiment}
Emotion: {emotion}
Frustration Level: {frustration_level}/10


KNOWLEDGE BASE INFORMATION
--------------------------
{knowledge_answer}


KNOWLEDGE SOURCES
-----------------
{source_text}


SUGGESTED REPLY RULES
---------------------

1. Directly address the customer's latest issue.

2. Be professional, empathetic, and concise.

3. Use the retrieved knowledge base information
   when it is relevant.

4. Do not invent policies, refund amounts, dates,
   timelines, or guarantees.

5. Do not request sensitive information such as:
   - password
   - OTP
   - PIN
   - CVV
   - full card number

6. If the knowledge base indicates that escalation
   is required, do not pretend that the issue can
   be resolved immediately.

7. Do not mention AI, Gemini, RAG, embeddings,
   prompts, or internal systems.

8. The suggested reply should sound like something
   a real support agent would send to a customer.

9. Keep the suggested reply between 1 and 4 sentences.


COACHING TIP RULES
------------------

Give one short practical tip based on the customer's
current emotional state and issue.

Examples:

- Acknowledge the customer's frustration before
  asking for additional information.

- Clearly explain the next step instead of giving
  a vague response.

- Avoid asking the customer to repeat information
  they have already provided.

- Since the customer appears calm, keep the response
  concise and solution-focused.

- Because the customer is highly frustrated, use
  empathy and clearly explain what will happen next.


OUTPUT FORMAT
-------------

Return exactly:

SUGGESTED_REPLY:
<reply>

COACH_TIP:
<one short coaching tip>

Return nothing else.
"""


# --------------------------------------------------
# Generate response coaching
# --------------------------------------------------

def generate_response_coaching(
    conversation: list[dict],
    analysis: dict,
    knowledge: dict,
) -> dict:
    """
    Generate a suggested support reply and coaching tip.
    """

    if not conversation:
        return {
            "suggested_reply": "",
            "coach_tip": "",
        }

    prompt = build_response_coach_prompt(
        conversation=conversation,
        analysis=analysis,
        knowledge=knowledge,
    )

    response = generate_with_gemini(
        prompt
    )

    if not response:
        return {
            "suggested_reply": "",
            "coach_tip": "",
        }

    response = clean_response(
        response
    )

    suggested_reply = ""
    coach_tip = ""

    lines = response.splitlines()

    current_section = None

    reply_lines = []
    tip_lines = []

    for line in lines:

        stripped_line = line.strip()

        if stripped_line.upper().startswith(
            "SUGGESTED_REPLY:"
        ):
            current_section = "reply"

            content = stripped_line[
                len("SUGGESTED_REPLY:"):
            ].strip()

            if content:
                reply_lines.append(
                    content
                )

            continue

        if stripped_line.upper().startswith(
            "COACH_TIP:"
        ):
            current_section = "tip"

            content = stripped_line[
                len("COACH_TIP:"):
            ].strip()

            if content:
                tip_lines.append(
                    content
                )

            continue

        if current_section == "reply":
            reply_lines.append(
                stripped_line
            )

        elif current_section == "tip":
            tip_lines.append(
                stripped_line
            )

    suggested_reply = " ".join(
        line
        for line in reply_lines
        if line
    ).strip()

    coach_tip = " ".join(
        line
        for line in tip_lines
        if line
    ).strip()

    return {
        "suggested_reply": suggested_reply,
        "coach_tip": coach_tip,
    }