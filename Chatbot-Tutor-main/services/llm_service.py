# This service is responsible for building the prompt for gemini
# Intents detected by intent_service.py will trigger a unique 
# prompt format to Gemini for "awarness"


def build_prompt(intent, context, question):

    if intent == "explanation":
        return f"""
You are an educational tutor.

Explain the following concept clearly and step-by-step using the context.

Context:
{context}

Question:
{question}
"""

    elif intent == "summary":
        return f"""
You are an AI tutor summarising a specific video.
Use ONLY the transcript context below.

Write a short but complete summary:
- 2 overview sentences
- 3 key bullet points
- 1 final takeaway sentence

Rules:
- Do not write a long answer.
- Do not cut off mid-sentence.
- Every bullet point must be a complete sentence.
- If the transcript context is limited, summarise only what is available.

Context:
{context}
"""

    elif intent == "quiz":
        return f"""
Generate 3 short quiz questions based on this content.

Context:
{context}
"""

    elif intent == "clarification":
        return f"""
Explain this in a simpler way for a beginner.

Context:
{context}

Question:
{question}
"""

    else:
        return f"""
Answer the question based on the context.

Context:
{context}

Question:
{question}
"""