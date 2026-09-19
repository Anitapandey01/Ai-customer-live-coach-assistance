import json

from app.services.conversation_analysis_service import (
    analyze_conversation,
    validate_analysis,
)


def mock_gemini_response(monkeypatch, response):
    monkeypatch.setattr(
        "app.services.conversation_analysis_service.generate_with_gemini",
        lambda prompt: response,
    )


def test_refund_request(monkeypatch):
    mock_gemini_response(
        monkeypatch,
        json.dumps({
            "intent": "Refund Request",
            "sentiment": "Neutral",
            "emotion": "Neutral",
            "frustration_level": 1,
            "satisfaction_trend": "Stable",
            "confidence": 0.95,
        }),
    )

    result = analyze_conversation([
        {
            "sender": "customer",
            "text": "I want to know if I can get a refund for my order.",
        }
    ])

    assert result["intent"] == "Refund Request"


def test_order_cancellation(monkeypatch):
    mock_gemini_response(
        monkeypatch,
        json.dumps({
            "intent": "Order Cancellation",
            "sentiment": "Neutral",
            "emotion": "Neutral",
            "frustration_level": 1,
            "satisfaction_trend": "Stable",
            "confidence": 0.94,
        }),
    )

    result = analyze_conversation([
        {
            "sender": "customer",
            "text": "I want to cancel my order.",
        }
    ])

    assert result["intent"] == "Order Cancellation"


def test_delayed_order(monkeypatch):
    mock_gemini_response(
        monkeypatch,
        json.dumps({
            "intent": "Delayed Order",
            "sentiment": "Negative",
            "emotion": "Worried",
            "frustration_level": 4,
            "satisfaction_trend": "Declining",
            "confidence": 0.91,
        }),
    )

    result = analyze_conversation([
        {
            "sender": "customer",
            "text": "My order is delayed and has not arrived yet.",
        }
    ])

    assert result["intent"] == "Delayed Order"


def test_payment_issue(monkeypatch):
    mock_gemini_response(
        monkeypatch,
        json.dumps({
            "intent": "Payment Issue",
            "sentiment": "Negative",
            "emotion": "Worried",
            "frustration_level": 5,
            "satisfaction_trend": "Declining",
            "confidence": 0.93,
        }),
    )

    result = analyze_conversation([
        {
            "sender": "customer",
            "text": "My payment was deducted but the order is not showing.",
        }
    ])

    assert result["intent"] == "Payment Issue"


def test_account_issue(monkeypatch):
    mock_gemini_response(
        monkeypatch,
        json.dumps({
            "intent": "Account Issue",
            "sentiment": "Negative",
            "emotion": "Confused",
            "frustration_level": 4,
            "satisfaction_trend": "Stable",
            "confidence": 0.89,
        }),
    )

    result = analyze_conversation([
        {
            "sender": "customer",
            "text": "I cannot access my account.",
        }
    ])

    assert result["intent"] == "Account Issue"


def test_delivery_issue(monkeypatch):
    mock_gemini_response(
        monkeypatch,
        json.dumps({
            "intent": "Delivery Issue",
            "sentiment": "Negative",
            "emotion": "Worried",
            "frustration_level": 5,
            "satisfaction_trend": "Declining",
            "confidence": 0.92,
        }),
    )

    result = analyze_conversation([
        {
            "sender": "customer",
            "text": "My package was supposed to arrive today but it has not arrived.",
        }
    ])

    assert result["intent"] == "Delivery Issue"


def test_return_or_exchange(monkeypatch):
    mock_gemini_response(
        monkeypatch,
        json.dumps({
            "intent": "Return or Exchange",
            "sentiment": "Neutral",
            "emotion": "Neutral",
            "frustration_level": 1,
            "satisfaction_trend": "Stable",
            "confidence": 0.94,
        }),
    )

    result = analyze_conversation([
        {
            "sender": "customer",
            "text": "I want to return this product and exchange it for another one.",
        }
    ])

    assert result["intent"] == "Return or Exchange"


def test_general_inquiry(monkeypatch):
    mock_gemini_response(
        monkeypatch,
        json.dumps({
            "intent": "General Inquiry",
            "sentiment": "Neutral",
            "emotion": "Neutral",
            "frustration_level": 0,
            "satisfaction_trend": "Stable",
            "confidence": 0.88,
        }),
    )

    result = analyze_conversation([
        {
            "sender": "customer",
            "text": "Could you explain how your refund process works?",
        }
    ])

    assert result["intent"] == "General Inquiry"


def test_positive_sentiment(monkeypatch):
    mock_gemini_response(
        monkeypatch,
        json.dumps({
            "intent": "General Inquiry",
            "sentiment": "Positive",
            "emotion": "Happy",
            "frustration_level": 0,
            "satisfaction_trend": "Improving",
            "confidence": 0.96,
        }),
    )

    result = analyze_conversation([
        {
            "sender": "customer",
            "text": "Thank you so much, that was very helpful!",
        }
    ])

    assert result["sentiment"] == "Positive"


def test_neutral_sentiment(monkeypatch):
    mock_gemini_response(
        monkeypatch,
        json.dumps({
            "intent": "General Inquiry",
            "sentiment": "Neutral",
            "emotion": "Neutral",
            "frustration_level": 0,
            "satisfaction_trend": "Stable",
            "confidence": 0.91,
        }),
    )

    result = analyze_conversation([
        {
            "sender": "customer",
            "text": "Can you tell me when my order will arrive?",
        }
    ])

    assert result["sentiment"] == "Neutral"


def test_negative_sentiment(monkeypatch):
    mock_gemini_response(
        monkeypatch,
        json.dumps({
            "intent": "Complaint",
            "sentiment": "Negative",
            "emotion": "Frustrated",
            "frustration_level": 8,
            "satisfaction_trend": "Declining",
            "confidence": 0.97,
        }),
    )

    result = analyze_conversation([
        {
            "sender": "customer",
            "text": "This is extremely frustrating. Nobody has helped me.",
        }
    ])

    assert result["sentiment"] == "Negative"


def test_calm_emotion(monkeypatch):
    mock_gemini_response(
        monkeypatch,
        json.dumps({
            "intent": "General Inquiry",
            "sentiment": "Neutral",
            "emotion": "Neutral",
            "frustration_level": 0,
            "satisfaction_trend": "Stable",
            "confidence": 0.90,
        }),
    )

    result = analyze_conversation([
        {
            "sender": "customer",
            "text": "Could you please explain the refund process?",
        }
    ])

    assert result["emotion"] == "Neutral"


def test_concerned_emotion(monkeypatch):
    mock_gemini_response(
        monkeypatch,
        json.dumps({
            "intent": "Payment Issue",
            "sentiment": "Negative",
            "emotion": "Worried",
            "frustration_level": 5,
            "satisfaction_trend": "Stable",
            "confidence": 0.90,
        }),
    )

    result = analyze_conversation([
        {
            "sender": "customer",
            "text": "I am worried because the payment seems to be missing.",
        }
    ])

    assert result["emotion"] == "Worried"


def test_confused_emotion(monkeypatch):
    mock_gemini_response(
        monkeypatch,
        json.dumps({
            "intent": "General Inquiry",
            "sentiment": "Neutral",
            "emotion": "Confused",
            "frustration_level": 2,
            "satisfaction_trend": "Stable",
            "confidence": 0.87,
        }),
    )

    result = analyze_conversation([
        {
            "sender": "customer",
            "text": "I do not understand why I need to complete this step.",
        }
    ])

    assert result["emotion"] == "Confused"


def test_frustrated_emotion(monkeypatch):
    mock_gemini_response(
        monkeypatch,
        json.dumps({
            "intent": "Complaint",
            "sentiment": "Negative",
            "emotion": "Frustrated",
            "frustration_level": 8,
            "satisfaction_trend": "Declining",
            "confidence": 0.95,
        }),
    )

    result = analyze_conversation([
        {
            "sender": "customer",
            "text": "I have already contacted you twice and this is still not fixed.",
        }
    ])

    assert result["emotion"] == "Frustrated"


def test_angry_emotion(monkeypatch):
    mock_gemini_response(
        monkeypatch,
        json.dumps({
            "intent": "Complaint",
            "sentiment": "Negative",
            "emotion": "Angry",
            "frustration_level": 10,
            "satisfaction_trend": "Declining",
            "confidence": 0.98,
        }),
    )

    result = analyze_conversation([
        {
            "sender": "customer",
            "text": "This is unacceptable. I am extremely angry about this.",
        }
    ])

    assert result["emotion"] == "Angry"


def test_satisfied_emotion(monkeypatch):
    mock_gemini_response(
        monkeypatch,
        json.dumps({
            "intent": "Refund Request",
            "sentiment": "Positive",
            "emotion": "Satisfied",
            "frustration_level": 0,
            "satisfaction_trend": "Improving",
            "confidence": 0.97,
        }),
    )

    result = analyze_conversation([
        {
            "sender": "customer",
            "text": "Thank you, my refund has been processed and I am satisfied.",
        }
    ])

    assert result["emotion"] == "Satisfied"


def test_improving_satisfaction_trend(monkeypatch):
    mock_gemini_response(
        monkeypatch,
        json.dumps({
            "intent": "Refund Request",
            "sentiment": "Positive",
            "emotion": "Satisfied",
            "frustration_level": 0,
            "satisfaction_trend": "Improving",
            "confidence": 0.96,
        }),
    )

    result = analyze_conversation([
        {
            "sender": "customer",
            "text": "I was worried about my refund.",
        },
        {
            "sender": "agent",
            "text": "Your refund has now been processed.",
        },
        {
            "sender": "customer",
            "text": "Thank you, that solves my problem.",
        },
    ])

    assert result["satisfaction_trend"] == "Improving"


def test_declining_satisfaction_trend(monkeypatch):
    mock_gemini_response(
        monkeypatch,
        json.dumps({
            "intent": "Complaint",
            "sentiment": "Negative",
            "emotion": "Frustrated",
            "frustration_level": 9,
            "satisfaction_trend": "Declining",
            "confidence": 0.96,
        }),
    )

    result = analyze_conversation([
        {
            "sender": "customer",
            "text": "I have been waiting for help with this issue.",
        },
        {
            "sender": "agent",
            "text": "Please wait while we check.",
        },
        {
            "sender": "customer",
            "text": "I have explained this three times and nobody is helping me.",
        },
    ])

    assert result["satisfaction_trend"] == "Declining"


def test_stable_satisfaction_trend(monkeypatch):
    mock_gemini_response(
        monkeypatch,
        json.dumps({
            "intent": "General Inquiry",
            "sentiment": "Neutral",
            "emotion": "Neutral",
            "frustration_level": 1,
            "satisfaction_trend": "Stable",
            "confidence": 0.90,
        }),
    )

    result = analyze_conversation([
        {
            "sender": "customer",
            "text": "Can you tell me how long delivery normally takes?",
        },
        {
            "sender": "agent",
            "text": "Standard delivery usually takes three to five business days.",
        },
        {
            "sender": "customer",
            "text": "Okay, thank you.",
        },
    ])

    assert result["satisfaction_trend"] == "Stable"


def test_conversation_context_is_used(monkeypatch):
    captured_prompt = {}

    def fake_generate(prompt):
        captured_prompt["value"] = prompt

        return json.dumps({
            "intent": "Refund Request",
            "sentiment": "Negative",
            "emotion": "Frustrated",
            "frustration_level": 7,
            "satisfaction_trend": "Declining",
            "confidence": 0.94,
        })

    monkeypatch.setattr(
        "app.services.conversation_analysis_service.generate_with_gemini",
        fake_generate,
    )

    result = analyze_conversation([
        {
            "sender": "customer",
            "text": "I requested a refund yesterday.",
        },
        {
            "sender": "agent",
            "text": "Please wait while we check the request.",
        },
        {
            "sender": "customer",
            "text": "I am still waiting and nobody has resolved it.",
        },
    ])

    assert result["intent"] == "Refund Request"
    assert "I requested a refund yesterday." in captured_prompt["value"]
    assert "I am still waiting and nobody has resolved it." in captured_prompt["value"]


def test_frustration_level_is_clamped_to_10():
    result = validate_analysis({
        "intent": "Complaint",
        "sentiment": "Negative",
        "emotion": "Frustrated",
        "frustration_level": 25,
        "satisfaction_trend": "Declining",
        "confidence": 0.90,
    })

    assert result["frustration_level"] == 10


def test_frustration_level_is_clamped_to_0():
    result = validate_analysis({
        "intent": "General Inquiry",
        "sentiment": "Neutral",
        "emotion": "Neutral",
        "frustration_level": -5,
        "satisfaction_trend": "Stable",
        "confidence": 0.80,
    })

    assert result["frustration_level"] == 0


def test_confidence_is_clamped_to_1():
    result = validate_analysis({
        "intent": "Refund Request",
        "sentiment": "Negative",
        "emotion": "Frustrated",
        "frustration_level": 7,
        "satisfaction_trend": "Declining",
        "confidence": 1.50,
    })

    assert result["confidence"] == 1.0


def test_confidence_is_clamped_to_0():
    result = validate_analysis({
        "intent": "General Inquiry",
        "sentiment": "Neutral",
        "emotion": "Neutral",
        "frustration_level": 0,
        "satisfaction_trend": "Stable",
        "confidence": -0.50,
    })

    assert result["confidence"] == 0.0


def test_invalid_sentiment_defaults_to_neutral():
    result = validate_analysis({
        "intent": "General Inquiry",
        "sentiment": "Unknown Sentiment",
        "emotion": "Neutral",
        "frustration_level": 2,
        "satisfaction_trend": "Stable",
        "confidence": 0.70,
    })

    assert result["sentiment"] == "Neutral"


def test_invalid_emotion_defaults_to_neutral():
    result = validate_analysis({
        "intent": "General Inquiry",
        "sentiment": "Neutral",
        "emotion": "Unknown Emotion",
        "frustration_level": 2,
        "satisfaction_trend": "Stable",
        "confidence": 0.70,
    })

    assert result["emotion"] == "Neutral"


def test_invalid_satisfaction_trend_defaults_to_stable():
    result = validate_analysis({
        "intent": "General Inquiry",
        "sentiment": "Neutral",
        "emotion": "Neutral",
        "frustration_level": 2,
        "satisfaction_trend": "Unknown Trend",
        "confidence": 0.70,
    })

    assert result["satisfaction_trend"] == "Stable"


def test_empty_conversation_returns_default_analysis():
    result = analyze_conversation([])

    assert result["intent"] == "Unknown"
    assert result["sentiment"] == "Neutral"
    assert result["emotion"] == "Neutral"
    assert result["frustration_level"] == 0
    assert result["satisfaction_trend"] == "Stable"
    assert result["confidence"] == 0.0


def test_invalid_gemini_json_returns_default_analysis(monkeypatch):
    mock_gemini_response(
        monkeypatch,
        "This is not valid JSON.",
    )

    result = analyze_conversation([
        {
            "sender": "customer",
            "text": "I need help with my order.",
        }
    ])

    assert result["intent"] == "Unknown"
    assert result["sentiment"] == "Neutral"
    assert result["emotion"] == "Neutral"
    assert result["frustration_level"] == 0
    assert result["satisfaction_trend"] == "Stable"
    assert result["confidence"] == 0.0