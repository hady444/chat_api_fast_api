# AI Assistant for Fitness

## Overview

This project is a fully custom **Retrieval-Augmented Generation (RAG)** system designed to power a chat-based AI assistant for fitness. It enables rich, reliable, and personalized advice on workouts, nutrition, and safety by combining crawled fitness data with intelligent agent orchestration.

---

## Architecture

### 1. Data Collection & Processing

- **Web Crawling**: Automated crawlers extract content from trusted fitness websites.
- **Cleaning & Normalization**: Text is cleaned and structured into a consistent format.
- **Storage**: Articles are stored in **MongoDB**.

### 2. Document Quality Assessment

- **LLM-Based Scoring**: Articles are evaluated with a Language Model to assign a `quality_score`.
- **Filtering**: Low-quality content is removed. Final dataset includes over 1,100 high-quality articles.

### 3. Retrieval-Augmented Generation (RAG)

- **Contextual RAG**: Summarizes chunks before embedding for more accurate retrieval.

### 4. Embedding & Vector Storage

- **Embeddings**: High-quality chunks are embedded using `llama-text-embed-v2`.
- **Vector Database**: Embeddings are stored in **Pinecone** for fast semantic search.

### 5. Agent-Based System

Agents are implemented using the `smolagents` Python SDK:

- `RetrieverAgent`: Fetches relevant vectors from Pinecone.
- `SummarizationAgents`: Two redundant summarizers for fault tolerance.
- `WorkoutPlannerAgent`: Designs personalized workout plans.
- `NutritionCalculatorAgent`: Builds nutrition plans.
- `ExerciseSafetyAgent`: Ensures safety and mitigates risks.

---

## System Workflow

1. **Data Acquisition**: Crawl, clean, and store content.
2. **Quality Control**: Score and filter documents using LLMs.
3. **Chunking & Embedding**: Summarize and vectorize data.
4. **User Interaction**: Users chat with the assistant; agents are triggered as needed.
5. **Response Delivery**: Assistant returns a rich, accurate, and safety-checked response.

---

## Chat API

The system exposes a unified API for contextual chat with the assistant.

### Authentication

All endpoints require a **JWT** in the `Authorization` header.

### Endpoints

| Endpoint               | Method | Description                                 |
|------------------------|--------|---------------------------------------------|
| `/chat/message`        | POST   | Send a message to the AI assistant          |
| `/chat/end`            | POST   | End a session and persist messages          |
| `/chat/sessions/{id}`  | GET    | Retrieve chat sessions for a specific user  |

### Example Usage

#### Send a Message

```json
POST /chat/message
Authorization: Bearer <JWT>

{
  "message": "Suggest a plan for gaining muscle mass",
  "user": {
    "id": "user123",
    "role": "client",  // or "trainer"
    "firstName": "Sara"
  },
  "session_id": "abc123"
}
