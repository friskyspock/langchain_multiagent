from supervisor_agent.agent import supervisor
from langchain_core.messages import AIMessage
from pretty_print import pretty_print_messages
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.requests import Request
from fastapi.templating import Jinja2Templates
import uuid, uvicorn, os
from fastapi import FastAPI
from fastapi.websockets import WebSocket, WebSocketDisconnect
from typing import Annotated
from fastapi.encoders import jsonable_encoder
from fastapi import Depends, Form, UploadFile, File
from elevenlabs import ElevenLabs, Voice, VoiceSettings
from io import BytesIO
import tempfile
from envs import Settings
from fastapi import HTTPException
from functools import lru_cache

@lru_cache
def get_settings():
    return Settings()

client = ElevenLabs(
    api_key=get_settings().ELEVENLABS_API_KEY
)

templates = Jinja2Templates(directory="templates")

app = FastAPI()

session = {}

@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    return templates.TemplateResponse("interview_setup.html", {"request": request})

@app.get("/interview", response_class=HTMLResponse)
async def get_interview_page(request: Request):
    return templates.TemplateResponse("interview.html", {"request": request})

@app.websocket(path="/ws")
async def audioCallWithAgent(websocket: WebSocket):
    await websocket.accept()
    session_id = uuid.uuid4()
    print(f"Client connected. Session ID: {session_id}")
    try:
        while True:
            user_input = await websocket.receive_text()
            async for chunk in supervisor.astream({"messages": [{"role": "user", "content": user_input}]}):
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

@app.post('/tts')
async def text_to_speech(
    settings: Annotated[Settings, Depends(get_settings)],
    text: str = Form(...)
):
    """
    Convert text to speech using ElevenLabs API
    """
    try:
        client = ElevenLabs(
            api_key=settings.ELEVENLABS_API_KEY
        )
        
        # Use a default voice or allow specifying a voice ID
        voice = Voice(
            voice_id="21m00Tcm4TlvDq8ikWAM",  # Default voice ID (Rachel)
            settings=VoiceSettings(stability=0.5, similarity_boost=0.75)
        )
        
        # Generate audio from text
        audio = client.generate(
            text=text,
            voice=voice
        )
        
        # Return audio as streaming response
        return StreamingResponse(
            BytesIO(audio),
            media_type="audio/mpeg",
            headers={"Content-Disposition": "attachment; filename=speech.mp3"}
        )
    except Exception as e:
        print(f"TTS error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"TTS error: {str(e)}")

@app.post('/transcribe')
async def transcribe_audio(
    settings: Annotated[Settings, Depends(get_settings)],
    audio: UploadFile = File(...)
):
    """
    Transcribe audio using ElevenLabs API
    """
    try:
        # Save uploaded file to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            temp_file_path = temp_file.name
            temp_file.write(await audio.read())
        
        client = ElevenLabs(
            api_key=settings.ELEVENLABS_API_KEY
        )
        
        # Transcribe audio
        with open(temp_file_path, "rb") as audio_file:
            transcription = client.transcribe(audio_file)
        
        # Clean up temporary file
        os.unlink(temp_file_path)
        
        return JSONResponse(
            content=jsonable_encoder({
                "status": True,
                "text": transcription.text
            }),
            status_code=200
        )
    except Exception as e:
        # Clean up temporary file in case of error
        if 'temp_file_path' in locals():
            try:
                os.unlink(temp_file_path)
            except:
                pass
        
        print(f"Transcription error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Transcription error: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)