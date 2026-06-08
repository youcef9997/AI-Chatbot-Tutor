# This service is responsible for detecting the user intent 
# when asking a question.
# (what does user want? a summary? or a quiz? clarification?)


def detect_intent(user_input):
    text = user_input.lower()

    if any(word in text for word in ["quiz", "test", "question me"]):
        return "quiz"

    elif any(word in text for word in ["summarise", "summary", "summarize"]):
        return "summary"

    elif any(word in text for word in ["explain", "what is", "how does"]):
        return "explanation"

    elif any(word in text for word in ["simplify", "clarify", "again"]):
        return "clarification"

    else:
        return "general"