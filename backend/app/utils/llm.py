import os
import re
from typing import List, Dict

def generate_answer(question: str, context: str, sources: List[Dict[str, str]]) -> str:
    """
    Generate an answer using context from documents.
    If an external LLM API key (e.g. OPENAI_API_KEY, GEMINI_API_KEY) is available,
    it can call it. Otherwise, it provides an intelligent rule-based extraction
    from the retrieved document context so the app always functions without external keys.
    """
    source_names = [s.get("originalName", "Document") for s in sources]
    sources_str = ", ".join(source_names) if source_names else "uploaded documents"

    if not context.strip():
        return (
            "I could not find any relevant information regarding your question in the "
            "uploaded documents. Please upload documents containing relevant content."
        )

    # Check for OpenAI API key if provided
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        try:
            import httpx
            headers = {"Authorization": f"Bearer {openai_key}", "Content-Type": "application/json"}
            payload = {
                "model": os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a helpful document assistant. Answer the user question based strictly on the provided context."
                    },
                    {
                        "role": "user",
                        "content": f"Context:\n{context}\n\nQuestion: {question}"
                    }
                ],
                "temperature": 0.2
            }
            res = httpx.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=10.0)
            if res.status_code == 200:
                return res.json()["choices"][0]["message"]["content"].strip()
        except Exception:
            pass  # Fall back to built-in synthesis

    # Built-in context synthesis (intelligent mock / extractor)
    # Extract sentences matching query terms
    question_clean = re.sub(r"[^\w\s]", " ", question.lower())
    q_words = set(w for w in question_clean.split() if len(w) > 2 and w not in {
        "what", "when", "where", "which", "who", "whom", "whose", "why", "how",
        "does", "the", "and", "about", "for", "with", "say", "tell"
    })

    # Break context into lines or sentences
    lines = [line.strip() for line in context.split("\n") if line.strip()]
    matched_lines = []
    
    for line in lines:
        line_clean = re.sub(r"[^\w\s]", " ", line.lower())
        line_words = set(line_clean.split())
        overlap = q_words.intersection(line_words)
        if overlap:
            matched_lines.append((len(overlap), line))

    matched_lines.sort(key=lambda x: x[0], reverse=True)

    if matched_lines:
        top_excerpts = [item[1] for item in matched_lines[:4]]
        excerpt_text = "\n".join(f"- {exc}" for exc in top_excerpts)
        return (
            f"Based on {sources_str}, here is the relevant information:\n\n"
            f"{excerpt_text}"
        )

    # Fallback to general context summary
    preview = context[:400] + ("..." if len(context) > 400 else "")
    return (
        f"According to {sources_str}:\n\n"
        f"{preview}"
    )
