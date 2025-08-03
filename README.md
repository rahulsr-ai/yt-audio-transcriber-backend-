🎙️ YouTube Transcriber & AI Summarizer (FastAPI Backend)

A backend-only FastAPI project that allows users to fetch YouTube video transcripts and optionally generate AI-powered summaries using Google Gemini, with fallback to AssemblyAI or Deepgram if the transcript is not available from YouTube.

🚀 Features
🔗 Input a YouTube video link.

📜 Automatically fetch transcript (using youtube-transcript-api).

🧠 Summarize content using Gemini AI.

🔁 Fallback to AssemblyAI or Deepgram if YouTube transcript fails.

🧾 FastAPI-based API ready for frontend integration or other services.

🧰 Tech Stack
FastAPI (Python backend)

youtube-transcript-api

yt_dlp or pytube for downloading video/audio

AssemblyAI (transcription API)

Deepgram (transcription API)

Google Gemini API (AI summarization)

transformers, newspaper3k for additional features (optional)

📦 Installation
Install Python dependencies:
pip install -r requirements.txt


Make sure your requirements.txt includes:
nginx
Copy
Edit
fastapi
uvicorn
yt_dlp
youtube-transcript-api
assemblyai
deepgram-sdk
transformers
python-dotenv
google-generativeai
newspaper3k

🔐 Environment Variables
Create a .env file in your project root with the following keys:


GEMINI_API_KEY=your_google_gemini_api_key
ASSEMBLYAI_API_KEY=your_assembly_ai_key
DEEPGRAM_API_KEY=your_deepgram_key
⚙️ Running the App
Start the FastAPI development server:


uvicorn main:app --reload