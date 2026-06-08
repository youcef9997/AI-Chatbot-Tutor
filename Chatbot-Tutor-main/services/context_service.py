# This service is responsible for structuring transcript chunks 
# received by retrieval_service.py.
# selected chunks are formatted into readable context for Gemini.

import re

# CLEAN TRANSCRIPT TEXT
def clean_transcript(text):
    text = re.sub(r'\s+', ' ', text)
    text = text.replace(" ,", ",").replace(" .", ".")
    return text.strip()



# CHUNK TRANSCRIPT
def chunk_transcript(text, chunk_size=80):  
    words = text.split()
    chunks = []

    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)

    return chunks



# POST RETRIEVED CHUNKS
def process_retrieved_chunks(chunks):
    
    processed = []

    for chunk in chunks:
        cleaned = clean_transcript(chunk)
        if cleaned:
            processed.append(cleaned)

    return processed


# STRUCTURE CONTEXT
def structure_context(chunks):
    
    if not chunks:
        return "No relevant context found."

    structured = "The following are key concepts extracted from the video:\n\n"

    for i, chunk in enumerate(chunks, 1):
        structured += f"Concept {i}:\n{chunk.strip()}\n\n"

    return structured


# BUILD THE CONTEXT
def build_context(raw_chunks):
    
    if not raw_chunks:
        return "No relevant transcript context found."

    # If raw_chunks is a string, split it into chunks first
    # This prevents Python treating the string as individual characters
    if isinstance(raw_chunks, str):
        raw_chunks = raw_chunks.split("\n\n")

    processed = process_retrieved_chunks(raw_chunks)
    structured = structure_context(processed)

    return structured