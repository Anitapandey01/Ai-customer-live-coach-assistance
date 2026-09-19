from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.knowledge_recommendation_service import (
    get_knowledge_recommendation,
)


router = APIRouter(
    prefix="/support",
    tags=["Live Support"]
)


# --------------------------------------------------
# Existing Live Support models
# --------------------------------------------------

class SupportRequest(BaseModel):
    issue_type: str = Field(
        ...,
        description="Type of issue reported by the user.",
        examples=["Technical Issue"]
    )

    message: str = Field(
        ...,
        min_length=1,
        description="Description of the user's issue.",
        examples=["I am having trouble using the application."]
    )


class SupportResponse(BaseModel):
    status: str = Field(
        ...,
        description="Status of the support request."
    )

    issue_type: str = Field(
        ...,
        description="Issue category submitted by the user."
    )

    support_response: str = Field(
        ...,
        description="Response returned by the Live Support module."
    )


# --------------------------------------------------
# Knowledge Recommendation models
# --------------------------------------------------

class ConversationMessage(BaseModel):
    sender: str = Field(
        ...,
        description="Message sender. Use customer or assistant.",
        examples=["customer"]
    )

    text: str = Field(
        ...,
        min_length=1,
        description="Conversation message text.",
        examples=["I want to request a refund."]
    )


class KnowledgeRecommendationRequest(BaseModel):
    conversation: list[ConversationMessage] = Field(
        ...,
        min_length=1,
        description=(
            "Current conversation containing customer and "
            "assistant messages."
        )
    )


# --------------------------------------------------
# Existing Live Support endpoint
# --------------------------------------------------

@router.post(
    "/",
    response_model=SupportResponse,
    summary="Submit a Live Support Request",
    description="""
Submit a support request and receive an immediate response.

### Supported Issue Types

- Technical Issue
- Document Upload
- Coaching Help
- Other

The Live Support module provides immediate assistance
for common user problems.
""",
    response_description="Support response returned successfully."
)
def live_support(request: SupportRequest):

    issue = request.issue_type.lower()

    if "technical" in issue:
        response = (
            "For technical issues, please check your internet "
            "connection and try again. If the problem continues, "
            "please contact support."
        )

    elif "document" in issue or "upload" in issue:
        response = (
            "For document upload problems, make sure the file format "
            "is supported and the file is not too large. "
            "Please try uploading it again."
        )

    elif "coaching" in issue:
        response = (
            "For coaching-related help, please describe your learning "
            "goal or the difficulty you are facing. "
            "Our AI Coaching system can guide you."
        )

    else:
        response = (
            "Thank you for contacting Live Support. "
            "Your request has been received. Please provide more "
            "details about your issue for further assistance."
        )

    return {
        "status": "success",
        "issue_type": request.issue_type,
        "support_response": response
    }


# --------------------------------------------------
# Knowledge Recommendation endpoint
# --------------------------------------------------

@router.post(
    "/knowledge-recommendations",
    summary="Get Knowledge Recommendations",
    description="""
Retrieve contextually relevant support knowledge for the
current customer conversation.

The Knowledge Recommendation Agent:

- Uses the latest customer message.
- Uses previous conversation context.
- Retrieves relevant support knowledge from the existing RAG
  knowledge base.
- Returns ranked knowledge sources.
- Returns up to five recommendations.
- Handles cases where no relevant knowledge is available.
"""
)
def knowledge_recommendations(
    request: KnowledgeRecommendationRequest,
):
    conversation = [
        {
            "sender": message.sender,
            "text": message.text,
        }
        for message in request.conversation
    ]

    return get_knowledge_recommendation(
        conversation=conversation
    )