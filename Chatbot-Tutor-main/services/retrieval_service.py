# Responsible for selecting relevant transcript chunks.
# A lightweight retrieval algorithm that compares transcript
# chunks with user question for relevance.

import re
from collections import Counter


STOP_WORDS = {
    "the", "is", "a", "an", "and", "or", "to", "of", "in", "on",
    "this", "that", "it", "for", "with", "as", "by", "at", "from",
    "me", "you", "video", "please"
}


def tokenise(text):
    words = re.findall(r"\b[a-zA-Z]+\b", text.lower())
    return [word for word in words if word not in STOP_WORDS]


def score_chunk(question, chunk):
    question_terms = tokenise(question)
    chunk_terms = tokenise(chunk)

    if not question_terms or not chunk_terms:
        return 0

    chunk_counts = Counter(chunk_terms)
    score = 0

    for term in question_terms:
        score += chunk_counts.get(term, 0)

    return score


def select_relevant_chunks(question, chunks, top_k=4):
    scored_chunks = []

    for chunk in chunks:
        score = score_chunk(question, chunk)
        scored_chunks.append((chunk, score))

    scored_chunks.sort(key=lambda item: item[1], reverse=True)

    selected = [chunk for chunk, score in scored_chunks[:top_k] if score > 0]

    if not selected:
        selected = chunks[:top_k]

    return "\n\n".join(selected)