def validate_response(response):
    if not response or len(response.strip()) == 0:
        return "Sorry, I couldn't generate a response."

    if len(response) > 2000:
        return response[:1000] + "..."

    return response