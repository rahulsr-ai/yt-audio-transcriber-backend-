import os
import uuid
import yt_dlp
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from deepgram import Deepgram  # Deepgram SDK v2.12.0
import assemblyai as aai

app = FastAPI()





app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],   # ✅ Only this origin is allowed ['*'] FOR PUBLIC API 
    allow_credentials=True,
    allow_methods=["POST"],         
    allow_headers=["*"],
)




# ✅ API Keys for both services
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
ASSEMBLY_API_KEY = os.getenv("ASSEMBLY_API_KEY")

print("🔐 Deepgram Key Present?", bool(DEEPGRAM_API_KEY))
print("🔐 AssemblyAI Key Present?", bool(ASSEMBLY_API_KEY))

# ✅ Deepgram client
dg_client = Deepgram(DEEPGRAM_API_KEY)

# ✅ AssemblyAI settings
aai.settings.api_key = ASSEMBLY_API_KEY
config = aai.TranscriptionConfig(speech_model=aai.SpeechModel.best)

# ✅ Input schema for FastAPI
class VideoURLInput(BaseModel):
    youtube_url: str

# ✅ Function to download YouTube audio using yt_dlp
def download_audio(youtube_url: str, filename: str = None) -> str:
    if not filename:
        filename = uuid.uuid4().hex  # Generate unique name
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": filename,  # Saved as: filename + .mp3
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
        }],
        "quiet": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])
    return f"{filename}.mp3"

# ✅ Transcription endpoint with fallback logic
@app.post("/transcribe-video")
def transcribe_youtube_audio(data: VideoURLInput):
    audio_file = None

    try:
        print("📥 Downloading audio...")
        audio_file = download_audio(data.youtube_url)
        audio_file_path = os.path.join(".", audio_file)
        print(f"🎧 Audio file saved to: {audio_file_path}")

        print(f"🎧 Audio file saved to: {audio_file_path}")

        # ✅ Check file size
        try:
            file_size = os.path.getsize(audio_file_path)
            print(f"📁 File size: {file_size} bytes")
            if file_size < 1000:
                raise RuntimeError("⚠️ Audio file too small or empty. Skipping upload.")
        except Exception as size_error:
            raise HTTPException(status_code=400, detail=f"Failed to access audio file: {size_error}")



        # ✅ Try Deepgram first (Primary service) 
        print("🧠 Transcribing with Deepgram...")
        with open(audio_file_path, "rb") as audio:
            source = {"buffer": audio, "mimetype": "audio/mp3"}
            dg_response = dg_client.transcription.sync_prerecorded(
                source,
                {"punctuate": True, "language": "en"}
            )

        # ✅ Extract Deepgram transcript
        transcript_text = dg_response["results"]["channels"][0]["alternatives"][0]["transcript"]
        print("✅ Deepgram transcription successful.")

        return {"transcript": transcript_text}

    except Exception as e:
        # ✅ If Deepgram fails, fallback to AssemblyAI
        print(f"⚠️ Deepgram failed: {e}")
        try:
            print("🔁 Falling back to AssemblyAI...")
            transcript = aai.Transcriber(config=config).transcribe(audio_file)
            if transcript.status == "error":
                raise RuntimeError(f"AssemblyAI Error: {transcript.error}")
            print("✅ AssemblyAI transcription successful.")
            return {"transcript": transcript.text}

        except Exception as fallback_error:
            raise HTTPException(status_code=500, detail=f"Both Deepgram and AssemblyAI failed: {fallback_error}")
        

    finally:
        # ✅ Always delete the audio file (cleanup)
        if audio_file and os.path.isfile(audio_file):
            os.remove(audio_file)
            print(f"🧹 Deleted temp file: {audio_file}")


            
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
