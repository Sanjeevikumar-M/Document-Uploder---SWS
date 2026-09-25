import re
from typing import Dict, Any, List
from ..database import get_documents_collection, serialize_doc
from ..utils.llm import generate_answer

STOPWORDS = {
    "the", "is", "at", "which", "on", "a", "an", "and", "or", "in", "for",
    "with", "what", "does", "about", "say", "to", "of", "how", "why", "when",
    "where", "who", "whom", "can", "could", "would", "should", "it", "this", "that"
}

def tokenize(text: str) -> List[str]:
    """Extract lowercased word tokens."""
    words = re.findall(r"\b[a-zA-Z0-9_-]+\b", text.lower())
    return [w for w in words if w not in STOPWORDS and len(w) > 1]

def calculate_relevance_score(doc: dict, question_tokens: List[str]) -> float:
    """Calculate keyword overlap score between question and document."""
    if not question_tokens:
        return 0.0

    name = doc.get("originalName", "").lower()
    text = (doc.get("text", "") or "").lower()

    score = 0.0
    for token in question_tokens:
        # Match in filename gives high weight
        if token in name:
            score += 4.0

        # Match in text
        count = len(re.findall(rf"\b{re.escape(token)}\b", text))
        score += count

    return score

def answer_question(question: str) -> Dict[str, Any]:
    """
    Main document Q&A workflow:
    1. Validate question
    2. Retrieve stored documents from MongoDB
    3. Rank documents by keyword overlap
    4. Build context
    5. Call LLM/synthesis
    6. Return answer and source documents
    """
    if not question or not question.strip():
        raise ValueError("Question cannot be empty")

    clean_question = question.strip()
    q_tokens = tokenize(clean_question)

    collection = get_documents_collection()
    all_docs = list(collection.find())

    if not all_docs:
        return {
            "answer": "No documents have been uploaded yet. Please upload a document to get started.",
            "sources": []
        }

    # Rank documents
    scored_docs = []
    for doc in all_docs:
        score = calculate_relevance_score(doc, q_tokens)
        scored_docs.append((score, doc))

    scored_docs.sort(key=lambda x: x[0], reverse=True)

    # Select relevant documents (top with score > 0, or top 1-2 if none match)
    relevant = [doc for score, doc in scored_docs if score > 0]
    if relevant:
        selected_docs = relevant[:3]
    else:
        # Fallback to the most recent document
        selected_docs = [scored_docs[0][1]] if scored_docs else []

    sources = [
        {
            "_id": str(doc["_id"]),
            "originalName": doc.get("originalName", "Document")
        }
        for doc in selected_docs
    ]

    # Build context
    context_chunks = []
    for doc in selected_docs:
        orig_name = doc.get("originalName", "Document")
        doc_text = (doc.get("text", "") or "").strip()
        context_chunks.append(f"--- Document: {orig_name} ---\n{doc_text}\n")

    full_context = "\n".join(context_chunks)

    # Generate answer
    answer = generate_answer(clean_question, full_context, sources)

    return {
        "answer": answer,
        "sources": sources
    }
