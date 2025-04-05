"""
Configuration settings for the AI Call Assistant.
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Vapi Configuration
VAPI_CONFIG = {
    "first_message": "Hello, this is AI assistant. How can I help you today?",
    "context": "You are a helpful AI assistant on a phone call.",
    "model": "gpt-3.5-turbo",  # Vapi assistant model
    "voice": "jennifer-playht",  # Other options: "alloy", "shimmer", "nova", "echo", etc.
    "recording_enabled": True,
    "interruptions_enabled": True,
    "end_call_on_silence": True,
    "silence_timeout_seconds": 10,
    "raw_audio": True  # Request raw audio to process with Groq
}

# Webhook Configuration
WEBHOOK_CONFIG = {
    "url": os.getenv("WEBHOOK_URL", "https://your-domain.com/webhook"),
    "headers": {
        "Authorization": f"Bearer {os.getenv('WEBHOOK_SECRET', 'your-webhook-secret')}"
    }
}

# Groq Speech-to-Text Models
STT_MODELS = {
    "default": "whisper-large-v3-turbo",  # Fast, good balance of speed and accuracy
    "high_accuracy": "whisper-large-v3",   # Highest accuracy, slower
    "english_only": "distil-whisper-large-v3-en",  # Fastest, English only
    "live": "whisper-large-v3-turbo"  # Optimized for live transcription
}

# Groq LLM Models
LLM_MODELS = {
    "default": "llama3-70b-8192",
    "fast": "llama3-8b-8192",
    "mixtral": "mixtral-8x7b-32768",
    "gemma": "gemma-7b-it",
    "live_response": "llama3-8b-8192"  # Faster model for live responses
}

# Speech-to-Text Configuration
STT_CONFIG = {
    "model": STT_MODELS["live"],  # Use the live-optimized model by default
    "language": "en",  # Language code (optional)
    "response_format": "text",  # "text" or "verbose_json" for timestamps
    "chunk_size": 4096,  # Buffer size for audio chunks (in bytes)
    "sample_rate": 16000,  # Sample rate for audio (16kHz is standard for STT)
    "live_mode": True  # Indicates we're processing live audio
}

# LLM Configuration
LLM_CONFIG = {
    "model": LLM_MODELS["live_response"],  # Faster model for real-time responses
    "temperature": 0.7,
    "max_tokens": 256,  # Shorter responses for real-time applications
    "system_prompt": "You are a helpful assistant on a phone call. Keep your responses short and to the point."
}

# Server Configuration
SERVER_CONFIG = {
    "host": "0.0.0.0",
    "port": 8000,
    "reload": True
} 