# Task 5 - Knowledge Recommendation Agent
## Final Evaluation Report

---

## 1. Objective

The objective of Task 5 was to build and evaluate a Knowledge Recommendation Agent that retrieves contextually relevant support knowledge for each customer conversation turn.

The agent uses the existing RAG knowledge base to retrieve relevant:

- Support articles
- FAQs
- Troubleshooting information
- Policies

The agent also considers previous conversation context so that recommendations remain relevant during multi-turn customer conversations.

---

## 2. Implementation

The Knowledge Recommendation Agent was implemented as:

`app/services/knowledge_recommendation_service.py`

The implementation:

1. Identifies the latest customer message.
2. Builds previous conversation context.
3. Creates a context-aware retrieval query.
4. Uses the existing RAG pipeline for knowledge retrieval.
5. Retrieves additional candidates for ranking.
6. Reranks retrieved sources using semantic distance and metadata keyword matching.
7. Returns up to five knowledge recommendations.
8. Preserves source metadata such as:
   - Document name
   - Document type
   - Version
   - Page number
   - Distance
9. Handles cases where no customer message is available.
10. Handles cases where relevant knowledge is not available.

The implementation reuses the existing RAG pipeline rather than creating a separate retrieval system.

---

## 3. RAG Integration

The recommendation agent integrates with:

`app/services/rag_service.py`

The existing RAG pipeline performs:

- Query embedding
- Vector similarity search
- Active document filtering
- Latest-version filtering
- Context construction
- Gemini-based response generation
- Source/reference generation

The Knowledge Recommendation Agent uses the returned sources and applies an additional ranking layer.

This keeps retrieval and recommendation responsibilities separated.

---

## 4. API Integration

A new endpoint was added to the existing Support API:

`POST /support/knowledge-recommendations`

The endpoint accepts a conversation containing customer and assistant messages.

Example request:

```json
{
  "conversation": [
    {
      "sender": "customer",
      "text": "I requested a refund for my order."
    },
    {
      "sender": "assistant",
      "text": "I can help you with the refund process."
    },
    {
      "sender": "customer",
      "text": "What information do I need to provide?"
    }
  ]
}