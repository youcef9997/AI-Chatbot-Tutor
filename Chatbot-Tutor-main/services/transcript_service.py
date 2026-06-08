# This service is a preprocessing pipeline for transcript data.
# Responsibilities include fetching transcript from YouTube Transcript API.
# Raw text is prepared and cleaned into plain text
# A temporary cache was also implemented to avoid retrieving 
# transcript each time user asks a question 

import requests

transcript_cache = {}


def fetch_transcript_from_api(video_id, youtube_api_token):
    response = requests.post(
        "https://www.youtube-transcript.io/api/transcripts",
        headers={
            "Authorization": f"Basic {youtube_api_token}",
            "Content-Type": "application/json"
        },
        json={"ids": [video_id]}
    )

    return response.json()


def parse_transcript_response(result):
    transcript_data = None

    if isinstance(result, list):
        if len(result) == 0:
            return None, "Transcript not available for this video. Try another video with captions."

        first_item = result[0]

        if isinstance(first_item, dict) and "tracks" in first_item:
            tracks = first_item.get("tracks", [])

            if tracks and len(tracks) > 0:
                transcript_data = tracks[0].get("transcript")

        elif isinstance(first_item, dict) and "segments" in first_item:
            transcript_data = first_item.get("segments")

    elif isinstance(result, dict):
        if "data" in result:
            data = result.get("data", [])

            if data and len(data) > 0:
                transcript_data = data[0].get("segments")

        elif "error" in result:
            return None, "Could not retrieve transcript for this video."

    if not transcript_data:
        return None, "Transcript is not available for this video. Please try a video with captions."

    return transcript_data, None


def convert_transcript_to_text(transcript_data):
    transcript_text = " ".join([
        seg.get("text", "") for seg in transcript_data
    ])

    if not transcript_text.strip():
        return None, "Transcript is empty."
    
    # ONLY PRINT IN CONSOLE 'HEAD' AND 'TAIL' OF CLEANED TRANSCRIPT
    clean_preview = str(transcript_text)

    clean_start = clean_preview[:200]
    clean_end = clean_preview[-200:] if len(clean_preview) > 400 else ""

    print("\n----- CLEANED TRANSCRIPT PARTIAL PREVIEW -----\n")
    print(clean_start)

    if clean_end:
        print("\n... [TRUNCATED] ...\n")
        print(clean_end)

    print("---------------------------------------------\n", flush=True)
    return transcript_text, None


def get_transcript_chunks(video_id, youtube_api_token, clean_transcript, chunk_transcript):
    
    #if video is present in cache, use it
    if video_id in transcript_cache:
        print("\n Using cached transcript for:", video_id, flush=True)

        return (
            transcript_cache[video_id]["transcript_text"],
            transcript_cache[video_id]["chunks"],
            None
        )

    print("\n Fetching transcript from:", video_id, flush=True)
    result = fetch_transcript_from_api(video_id, youtube_api_token)

    # ONLY PRINT IN CONSOLE 'HEAD' AND 'TAIL' OF TRANSCRIPT RATHER THAN ALL
    preview = str(result)

    start = preview[:200]
    end = preview[-200:] if len(preview) > 400 else ""

    print("\n----- RAW TRANSCRIPT PARTIAL PREVIEW -----\n")
    print(start)

    if end:
        print("\n... [TRUNCATED] ...\n")
        print(end)

    print("-----------------------------\n", flush=True)

    transcript_data, error = parse_transcript_response(result)

    if error:
        return None, None, error

    transcript_text, error = convert_transcript_to_text(transcript_data)

    if error:
        return None, None, error

    print("\n Transcript length:", len(transcript_text), flush=True)

    transcript_text = clean_transcript(transcript_text)

    chunks = chunk_transcript(transcript_text)

    if not chunks:
        return None, None, "Could not process transcript."

    if len(transcript_cache) > 10:
        oldest_video_id = next(iter(transcript_cache))
        del transcript_cache[oldest_video_id]
        print("\n Removed old cached transcript:", oldest_video_id, flush=True)

    transcript_cache[video_id] = {
        "transcript_text": transcript_text,
        "chunks": chunks
    }

    print("\n Transcript cached for:", video_id, flush=True)

    return transcript_text, chunks, None