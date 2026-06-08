# AI Chatbot Tutor - Backend

This repository contains the backend API for my final year project: **AI Chatbot Tutor**. The project was designed to support learners while watching YouTube educational videos by generating transcript-aware summaries, quizzes, clarifications, and answers.

The full system was built as a Chrome extension frontend connected to this Flask backend. This repository focuses on the backend services responsible for transcript processing, context retrieval, AI response generation, logging, validation, and deployment.

## Project Overview

Many learners use YouTube tutorials for independent study, but the experience is often passive. Users may need to pause, rewind, or leave the video page when they want clarification, a summary, or a way to test their understanding.

This backend helps solve that problem by receiving a user question and YouTube video ID from the frontend, retrieving the video transcript, processing the transcript, selecting relevant context, and using Gemini to generate an educational response.

## Main Features

* Flask REST API for chatbot requests
* YouTube transcript retrieval
* Transcript parsing, cleaning, chunking, and caching
* Lightweight context retrieval from transcript chunks
* Intent detection for:

  * Summary requests
  * Quiz generation
  * Clarification
  * General question answering
* Prompt construction for Gemini
* Gemini API integration
* SQLite interaction logging
* Input validation and sanitisation
* Basic rate limiting
* Privacy-aware logging with limited stored data
* Azure App Service deployment support

## Tech Stack

* **Python**
* **Flask**
* **SQLite**
* **Gemini API**
* **YouTube Transcript API**
* **Gunicorn**
* **Microsoft Azure App Service**

## Backend Processing Flow

The backend follows a structured pipeline:

```text
User request
→ Validate input
→ Apply rate limiting
→ Retrieve or reuse transcript
→ Clean and chunk transcript
→ Select relevant context
→ Detect user intent
→ Build Gemini prompt
→ Generate AI response
→ Validate and sanitise response
→ Log interaction in SQLite
→ Return JSON response
```

This means the system does not simply forward the user question directly to Gemini. It prepares video-specific context first so the response is more relevant to the YouTube video being watched.

## API Endpoints

### `GET /`

Returns a simple message confirming that the backend is running.

### `POST /ask`

Main chatbot endpoint.

Expected JSON body:

```json
{
  "question": "Summarise this video",
  "video_id": "YouTubeVideoID",
  "history": []
}
```

Example response:

```json
{
  "answer": "Here is a summary of the video..."
}
```

### `GET /interactions-register`

Returns recent logged chatbot interactions from the SQLite database. This was used during development and evaluation to inspect stored interactions.

## Security and Privacy Considerations

The backend includes several safeguards:

* API keys are stored as environment variables, not hard-coded in the source code
* User input is validated before processing
* SQLite queries use parameterised statements
* Rate limiting helps reduce repeated rapid requests
* Recent interactions are logged only for testing and evaluation
* The system avoids storing user names, emails, passwords, or YouTube account details

## Environment Variables

The backend requires API keys to be provided through environment variables:

```text
GEMINI_API_KEY=your_gemini_api_key
YOUTUBE_API_TOKEN=your_transcript_api_token
```

These should be configured locally or through the hosting platform, such as Azure App Service application settings.

## Project Outcome

The backend was successfully connected to a Chrome extension frontend and tested with YouTube educational videos. The final system allowed users to ask questions, request summaries, generate quizzes, and clarify concepts based on video transcript content.

The project strengthened my experience with backend development, APIs, databases, validation, debugging, cloud deployment, and building AI-powered applications around real user requirements.

## Note

This repository contains the backend part of the project. The full project also included a Chrome extension frontend that injected the chatbot interface directly into YouTube.
