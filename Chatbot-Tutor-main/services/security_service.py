# This service is responsible for user input validation
# Additionally, some sanitisation steps are implemented 
# to avoid Cross Site Scripting

import re


YOUTUBE_ID_PATTERN = re.compile(r"^[a-zA-Z0-9_-]{11}$")


def validate_question(question):
    if not question:
        return False, "Please enter a question."

    if not isinstance(question, str):
        return False, "Invalid question format."

    question = question.strip()

    if len(question) == 0:
        return False, "Please enter a question."

    if len(question) > 500:
        return False, "Question is too long. Please keep it under 500 characters."

    return True, question


def validate_video_id(video_id):
    if not video_id:
        return False, "Please open a valid YouTube video first."

    if not isinstance(video_id, str):
        return False, "Invalid video ID format."

    video_id = video_id.strip()

    if not YOUTUBE_ID_PATTERN.match(video_id):
        return False, "Invalid YouTube video ID."

    return True, video_id


# Defensive sanitisation, the frontend uses textContent, 
# but this also removes script tags before storage/logging.
def sanitise_text(text):
    
    if text is None:
        return ""

    text = str(text)

    text = re.sub(
        r"<\s*script.*?>.*?<\s*/\s*script\s*>",
        "",
        text,
        flags=re.IGNORECASE | re.DOTALL
    )

    return text.strip()