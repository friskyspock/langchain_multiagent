from supervisor_agent.agent import supervisor
from langchain_core.messages import AIMessage
from pretty_print import pretty_print_messages
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.requests import Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uuid, uvicorn, os, requests
from fastapi import FastAPI
from fastapi.websockets import WebSocket, WebSocketDisconnect
from fastapi.encoders import jsonable_encoder
from fastapi import UploadFile, File
from elevenlabs import ElevenLabs
from schemas import SessionInfo
import os, redis
from dotenv import load_dotenv
from pydantic import BaseModel

# Load environment variables
load_dotenv()
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")

redis_client = redis.Redis(host='localhost', port=6379, db=0)
elevenlabs_client = ElevenLabs(
    api_key=ELEVENLABS_API_KEY
)

templates = Jinja2Templates(directory="templates")

app = FastAPI()

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def get_index_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.websocket(path="/ws")
async def audioCallWithAgent(websocket: WebSocket):
    await websocket.accept()
    session_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": "1"}}
    print(f"Client connected. Session ID: {session_id}")
    try:
        while True:
            user_input = await websocket.receive_text()
            async for chunk in supervisor.astream({"messages": [
                {"role": "user","content": user_input}, 
                {"role": "system", "content": f"session_id: {session_id}"}
                ]}):
                pretty_print_messages(chunk, last_message=False)
                if (ai_chunk := chunk.get('supervisor')):
                    if (ai_msg := ai_chunk['messages'][-1]) and isinstance(ai_msg, AIMessage):
                        await websocket.send_text(ai_msg.content)

    except WebSocketDisconnect:
        print(f"Client disconnected. Session ID: {session_id}")

    except Exception as e:
        print(f"Connection error: {str(e)}")
        import traceback
        traceback.print_exc()

class TranscriptionInputs(BaseModel):
    file_link: str

@app.post("/transcribe")
async def transcribe_audio(inputs: TranscriptionInputs):
    try:
        print(f"Received transcription request with file_link: {inputs.file_link}")

        # Get audio data from the provided URL
        audio_bytes = requests.get(inputs.file_link).content

        # Process with ElevenLabs API
        result = elevenlabs_client.speech_to_text.convert(
            model_id="scribe_v1",
            file=audio_bytes,
            language_code="en"
        )

        return JSONResponse(
            content=jsonable_encoder({"status": True, "text": result.text}),
            status_code=200
        )
    except Exception as e:
        print(f"Transcription error: {str(e)}")
        return JSONResponse(
            content=jsonable_encoder({"status": False, "error": str(e)}),
            status_code=500
        )

# Alternative endpoint that accepts direct file uploads for better latency
@app.post("/transcribe-upload")
async def transcribe_audio_upload(file: UploadFile = File(...)):
    try:
        print(f"Received audio upload: {file.filename}, size: {file.size if hasattr(file, 'size') else 'unknown'}")

        # Read the audio file directly from the request
        audio_bytes = await file.read()

        # Process with ElevenLabs API
        result = elevenlabs_client.speech_to_text.convert(
            model_id="scribe_v1",
            file=audio_bytes,
            language_code="en"
        )

        return JSONResponse(
            content=jsonable_encoder({"status": True, "text": result.text}),
            status_code=200
        )
    except Exception as e:
        print(f"Transcription upload error: {str(e)}")
        return JSONResponse(
            content=jsonable_encoder({"status": False, "error": str(e)}),
            status_code=500
        )

# Mock endpoint for testing - returns a fixed response without calling the API
@app.post("/transcribe-mock")
async def transcribe_audio_mock():
    try:
        print("Received mock transcription request")

        # Return a mock response for testing
        return JSONResponse(
            content=jsonable_encoder({
                "status": True,
                "text": "This is a mock transcription for testing purposes."
            }),
            status_code=200
        )
    except Exception as e:
        print(f"Mock transcription error: {str(e)}")
        return JSONResponse(
            content=jsonable_encoder({"status": False, "error": str(e)}),
            status_code=500
        )

@app.post("/speak")
async def speak_text(payload: dict):
    try:
        text = payload["text"]

        # Use a more optimized model for faster response
        audio_data = elevenlabs_client.text_to_speech.convert(
            voice_id="21m00Tcm4TlvDq8ikWAM",
            output_format="mp3_44100_128",  # Lower quality for faster response
            text=text,
            model_id="eleven_monolingual_v1",  # Faster model if available
            optimize_streaming_latency=4  # Maximum optimization for streaming latency
        )

        return StreamingResponse(
            content=audio_data,
            media_type="audio/mpeg",
            headers={"Cache-Control": "no-cache"}
        )
    except Exception as e:
        print(f"Text-to-speech error: {str(e)}")
        return JSONResponse(
            content=jsonable_encoder({"status": False, "error": str(e)}),
            status_code=500
        )

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5000)