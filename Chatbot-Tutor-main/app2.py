from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sqlite3

# IMPORTS FROM SERVICES FOLDER
from services.intent_service import detect_intent
from services.context_service import build_context, clean_transcript, chunk_transcript
from services.llm_service import build_prompt
from services.validation import validate_response
from services.database_service import init_db, log_interaction, get_recent_logs
from services.retrieval_service import select_relevant_chunks
from services.security_service import validate_question, validate_video_id, sanitise_text
from services.transcript_service import get_transcript_chunks
from services.gemini_service import configure_gemini, send_to_gemini_with_retry
from services.rate_limit import check_rate_limit


# CONFIGURATION
app = Flask(__name__)
CORS(app)

# SQL LITE DATABASE INITIALISATION
init_db()

# ENVIRONMENTAL VARIABLES
YOUTUBE_API_TOKEN = os.environ.get("YOUTUBE_API_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("Missing GEMINI_API_KEY environment variable")
configure_gemini(GEMINI_API_KEY)


# TO VIEW ENTRIES COUNT OF DATABASE - /logs-test 
@app.route("/logs-test")
def logs_test():
    

    conn = sqlite3.connect("chatbot_logs.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM interactions")
    count = cursor.fetchone()[0]

    conn.close()

    return jsonify({
        "logged_interactions": count
    })

# VIEW CURRENT DATABASE ENTRIES ENTRIES - /view-current-entries 
@app.route("/view-current-entries")
def view_logs():
    return jsonify(get_recent_logs())

# BACKEND ROUTE
@app.route("/")
def home():
    return """
    <h2>Chatbot brain is live!<h2>
    <p>Chatbot Tutor developed by student 23747739<p>
    <p>Navigate to your preferred YouTube video or choose one provided in the "How to run the Chatbot" file.<p>
    <p>Chatbot Tutor is happy to help! <p>
    """
# MAIN ROUTE
@app.route("/ask", methods=["POST"])
def ask():

    data = request.get_json()
    question = data.get("question")
    video_id = data.get("video_id")
    history = data.get("history", [])


    is_valid_question, question_result = validate_question(question)
    if not is_valid_question:
        return jsonify({"answer": question_result}), 400

    question = question_result

    is_valid_video, video_result = validate_video_id(video_id)
    if not is_valid_video:
        return jsonify({"answer": video_result}), 400

    video_id = video_result

    # RATE LIMIT (rate_limit.py)
    allowed, rate_limit_message = check_rate_limit(request.remote_addr)

    if not allowed:
        return jsonify({
            "answer": rate_limit_message
        }), 429

    try:
        # FULL TRANSCRIPT RETRIEVAL PIPELINE (transcript_service.py)
        _, chunks, transcript_error = get_transcript_chunks(
            video_id=video_id,
            youtube_api_token=YOUTUBE_API_TOKEN,
            clean_transcript=clean_transcript,
            chunk_transcript=chunk_transcript
        )

        if transcript_error:
            return jsonify({
                "answer": transcript_error
            })

        # INTENT DETECTION (intent_service.py) (what did user ask?: to summarise or to quiz or...)
        intent = detect_intent(question)
        print("\n Detected intent:", intent, flush= True)

        # RECEIVE CLEANED TRANSCRIPT AND SELECT RELEVANT SECTIONS (retrieval_service.py) 
        raw_context = select_relevant_chunks(question, chunks, top_k=4)
        
        # SEE NEW CONTEXT LENGHT + ONLY A PREVIEW
        print("Refactored context length:", len(raw_context))
        print("----------PREVIEW OF REFACTORED CONTEXT----------\n")
        print(raw_context[:300])
        print("-----------------------------\n", flush=True)
        
        # BUILD STRUCTURED CONTEXT (context_service.py)
        context = build_context(raw_context)
        # limit size
        context = context[:2500]

        # BUILD HISTORY
        history_text = ""
        for msg in history:
            role = "User" if msg["role"] == "user" else "AI"
            history_text += f"{role}: {msg['text']}\n"

        # PREPARE CONTEXT FOR GEMINI (llm_service.py)
        prompt = build_prompt(intent, context, question)

        # INJECT CONVERSATION MEMORY
        prompt = f"""
        You are an AI tutor helping a student understand video content.

        Conversation so far:
        {history_text}

        {prompt}
        """

        print("Sending to Gemini...", flush=True)

        # GEMINI CALL (gemini_service.py)
        answer_text = send_to_gemini_with_retry(prompt)

        #VALIDATE AND SANITASE (validation.py & security_service.py)
        final_response = validate_response(answer_text)
        final_response = sanitise_text (final_response)
        safe_question = sanitise_text (question)

        # REGISTER INTERACTIONS IN DB (database_service.py)
        log_interaction(
        video_id=video_id,
        question=safe_question,
        intent=intent,
        answer=final_response
        )

        return jsonify({
            "answer": final_response
        })

    except Exception as e:
        import traceback
        
        # Print error to backend with traceback
        print("\n ----- FULL ERROR: -----", e, flush=True)
        traceback.print_exc()
        print("-----------------------------\n", flush=True)

        # Print error to user
        return jsonify({
            "answer": "OOPS.. That was unexpected, try again soon."
        }), 500

# RUN SERVER 
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)