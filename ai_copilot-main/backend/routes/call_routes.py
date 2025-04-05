from fastapi import APIRouter, HTTPException, BackgroundTasks, UploadFile, File
from typing import Dict, Any, List
import logging

from services.vapi_service import vapi_service
from services.call_service import call_service
from models.schemas import CallInfo

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/calls", tags=["calls"])

@router.post("/start")
async def start_call() -> Dict[str, Any]:
    """Start an outbound call"""
    try:
        # Configure the assistant
        assistant_config = vapi_service.create_assistant_config()
        
        # Start the call
        call = vapi_service.start_call(assistant_config)
        
        # Track the active call
        call_id = call.get("call_id")
        if call_id:
            call_service.register_call(call_id, call)
            
        return {"status": "success", "call_id": call_id}
    
    except Exception as e:
        logger.error(f"Error starting call: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/accept/{call_id}")
async def accept_call(call_id: str) -> Dict[str, Any]:
    """Accept an incoming call"""
    # For Vapi, calls are typically automatically answered
    return {"status": "success", "message": "Call accepted"}

@router.post("/end/{call_id}")
async def end_call(call_id: str) -> Dict[str, Any]:
    """End an active call"""
    try:
        if call_id in call_service.get_active_calls():
            vapi_service.stop_call()
            call_service.unregister_call(call_id)
            return {"status": "success", "message": "Call ended"}
        return {"status": "error", "message": "Call not found"}
    
    except Exception as e:
        logger.error(f"Error ending call: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{call_id}")
async def get_call(call_id: str) -> CallInfo:
    """Get details about a specific call"""
    call_info = call_service.get_call_info(call_id)
    if not call_info:
        raise HTTPException(status_code=404, detail="Call not found")
    return call_info

@router.get("/")
async def list_calls() -> Dict[str, List[str]]:
    """List all calls"""
    return {
        "active_calls": call_service.get_active_calls(),
        "all_calls": call_service.get_all_calls()
    }

@router.post("/upload-audio/{call_id}")
async def upload_audio(call_id: str, audio: UploadFile = File(...), background_tasks: BackgroundTasks = None) -> Dict[str, Any]:
    """Upload audio for transcription and response generation"""
    try:
        if not audio.content_type.startswith("audio/"):
            raise HTTPException(status_code=400, detail="File must be an audio file")
        
        # Read audio content
        audio_content = await audio.read()
        
        # Import services
        from services.groq_service import groq_service
        
        # Process audio file in memory
        import io
        audio_file = io.BytesIO(audio_content)
        audio_file.name = audio.filename or "audio.wav"
        
        # Transcribe audio
        transcribed_text = await groq_service.transcribe_audio_file(audio_file)
        
        if not transcribed_text:
            return {"status": "error", "message": "No transcription generated"}
        
        # Broadcast transcript to websocket clients
        background_tasks.add_task(
            call_service.broadcast_transcript,
            call_id,
            transcribed_text,
            True
        )
        
        # Generate response
        response = await groq_service.generate_response(transcribed_text)
        
        # Broadcast response to clients
        if response:
            background_tasks.add_task(
                call_service.broadcast_response,
                call_id,
                response,
                "groq-llama3-70b"
            )
        
        return {
            "status": "success",
            "call_id": call_id,
            "transcript": transcribed_text,
            "response": response
        }
    
    except Exception as e:
        logger.error(f"Error processing uploaded audio: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 