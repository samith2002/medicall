from pydantic import BaseModel
from typing import Dict, List, Optional, Any, Union


class CallWebhookEvent(BaseModel):
    """Model for Vapi webhook events"""
    event_type: str
    call_id: str
    transcript: Optional[Dict[str, Any]] = None
    call_status: Optional[str] = None
    recording_url: Optional[str] = None


class TranscriptMessage(BaseModel):
    """Model for transcript messages"""
    call_id: str
    text: str
    is_final: bool = False
    timestamp: Optional[float] = None


class ResponseMessage(BaseModel):
    """Model for AI response messages"""
    call_id: str
    text: str
    model: str
    timestamp: Optional[float] = None


class ModelUpdateRequest(BaseModel):
    """Model for updating AI models configuration"""
    stt_model: Optional[str] = None
    llm_model: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    system_prompt: Optional[str] = None


class LiveTranscriptUpdate(BaseModel):
    """Model for live transcript updates to frontend"""
    type: str = "transcript"
    call_id: str
    text: str
    is_final: bool = False
    timestamp: Optional[float] = None


class LiveResponseUpdate(BaseModel):
    """Model for live response updates to frontend"""
    type: str = "response"
    call_id: str
    text: str
    timestamp: Optional[float] = None


class CallInfo(BaseModel):
    """Model for call information"""
    call_id: str
    status: str
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    transcript_history: List[TranscriptMessage] = []
    response_history: List[ResponseMessage] = [] 