from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.api.dependencies import get_authenticated_user
from app.models.user import User

from app.services.conversation_analysis_service import (
    analyze_conversation,
)

from app.services.customer_simulator_service import (
    PERSONAS,
    SCENARIOS,
    EMOTIONS,
    create_session,
    generate_customer_message,
    get_session_log,
    save_session_log,
    update_session_after_response,
)

from app.services.knowledge_recommendation_service import (
    get_knowledge_recommendation,
)

from app.services.response_coach_service import (
    generate_response_coaching,
)

from app.services.escalation_risk_service import (
    analyze_escalation_risk,
)


router = APIRouter(
    prefix="/simulator",
    tags=["Customer Simulator"],
)


class SimulatorStartRequest(BaseModel):
    persona: str = "calm"
    initial_emotion: str = "calm"
    scenario: str = "refund"

    issue_severity: int = Field(
        default=3,
        ge=1,
        le=5,
    )

    patience_level: int = Field(
        default=60,
        ge=1,
        le=100,
    )

    expected_resolution: str = (
        "A fair resolution to the issue."
    )


class SimulatorTurnRequest(BaseModel):
    session_id: str

    support_response: str = Field(
        min_length=1,
        max_length=3000,
    )


@router.get("/config")
def get_simulator_config(
    current_user: User = Depends(
        get_authenticated_user
    ),
):
    return {
        "personas": [
            {
                "id": key,
                **value,
            }
            for key, value in PERSONAS.items()
        ],
        "scenarios": [
            {
                "id": key,
                **value,
            }
            for key, value in SCENARIOS.items()
        ],
        "emotions": EMOTIONS,
        "issue_severity": {
            "min": 1,
            "max": 5,
        },
        "patience_level": {
            "min": 1,
            "max": 100,
        },
    }


@router.post("/start")
def start_simulator(
    request: SimulatorStartRequest,
    current_user: User = Depends(
        get_authenticated_user
    ),
):
    try:

        session = create_session(
            persona=request.persona,
            initial_emotion=request.initial_emotion,
            scenario=request.scenario,
            issue_severity=request.issue_severity,
            patience_level=request.patience_level,
            expected_resolution=request.expected_resolution,
        )

        customer_message = generate_customer_message(
            session=session
        )

        session["turn_number"] = 1

        session["conversation"].append(
            {
                "turn": 1,
                "sender": "customer",
                "text": customer_message,
            }
        )

        save_session_log(session)

        analysis = analyze_conversation(
            session["conversation"]
        )

        knowledge = get_knowledge_recommendation(
            session["conversation"]
        )

        coaching = generate_response_coaching(
            conversation=session["conversation"],
            analysis=analysis,
            knowledge=knowledge,
        )

        escalation_risk = analyze_escalation_risk(
            conversation=session["conversation"],
            analysis=analysis,
        )

        return {
            "session_id": session["session_id"],
            "customer_message": customer_message,
            "analysis": analysis,
            "knowledge": knowledge,
            "coaching": coaching,
            "escalation_risk": escalation_risk,
            "state": {
                "persona": session["persona"],
                "scenario": session["scenario"],
                "emotion": session["current_emotion"],
                "emotion_score": session["emotion_score"],
                "satisfaction_status": session[
                    "satisfaction_status"
                ],
                "issue_severity": session["issue_severity"],
                "patience_level": session["patience_level"],
                "turn_number": session["turn_number"],
            },
        }

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to start customer simulation: "
                + str(error)
            ),
        )


@router.post("/turn")
def simulator_turn(
    request: SimulatorTurnRequest,
    current_user: User = Depends(
        get_authenticated_user
    ),
):

    support_response = (
        request.support_response.strip()
    )

    if not support_response:

        raise HTTPException(
            status_code=400,
            detail="Support response cannot be empty.",
        )

    session = get_session_log(
        request.session_id
    )

    if not session:

        raise HTTPException(
            status_code=404,
            detail="Simulator session not found.",
        )

    try:

        customer_message = generate_customer_message(
            session=session,
            support_response=support_response,
        )

        update_session_after_response(
            session=session,
            support_response=support_response,
            customer_message=customer_message,
        )

        save_session_log(session)

        analysis = analyze_conversation(
            session["conversation"]
        )

        knowledge = get_knowledge_recommendation(
            session["conversation"]
        )

        coaching = generate_response_coaching(
            conversation=session["conversation"],
            analysis=analysis,
            knowledge=knowledge,
        )

        escalation_risk = analyze_escalation_risk(
            conversation=session["conversation"],
            analysis=analysis,
        )

        return {
            "session_id": session["session_id"],
            "customer_message": customer_message,
            "analysis": analysis,
            "knowledge": knowledge,
            "coaching": coaching,
            "escalation_risk": escalation_risk,
            "state": {
                "persona": session["persona"],
                "scenario": session["scenario"],
                "emotion": session["current_emotion"],
                "emotion_score": session["emotion_score"],
                "satisfaction_status": session[
                    "satisfaction_status"
                ],
                "issue_severity": session["issue_severity"],
                "patience_level": session["patience_level"],
                "turn_number": session["turn_number"],
            },
        }

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to generate customer response: "
                + str(error)
            ),
        )


@router.get("/session/{session_id}")
def get_simulator_session(
    session_id: str,
    current_user: User = Depends(
        get_authenticated_user
    ),
):

    session = get_session_log(
        session_id
    )

    if not session:

        raise HTTPException(
            status_code=404,
            detail="Simulator session not found.",
        )

    return session