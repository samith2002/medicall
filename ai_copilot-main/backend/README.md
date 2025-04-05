# AI Call Assistant

An AI-powered call assistant that accepts calls, captures live audio, transcribes it using Groq's speech-to-text API, and processes the text using Groq's LLM models, with real-time transcripts for frontend support interfaces.

## Documentation

The API documentation is available at: https://pujariaditya--ai-call-assistant-fastapi-app.modal.run/docs

## Architecture

The application follows a modular architecture:

```
backend/
├── models/          # Pydantic models for data validation
├── services/        # Service modules for external APIs
├── routes/          # API route handlers
├── config.py        # Configuration settings
├── main.py          # Main FastAPI application
├── requirements.txt # Dependencies
└── .env             # Environment variables
```

## Setup

1. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your environment variables in the `.env` file:
```
VAPI_API_KEY=your_vapi_api_key_here
GROQ_API_KEY=your_groq_api_key_here
WEBHOOK_URL=https://your-domain.com/webhook
WEBHOOK_SECRET=your_webhook_secret
```

- Get your Vapi API key from [Vapi.ai](https://vapi.ai)
- Get your Groq API key from [Groq Console](https://console.groq.com)

## Configuration

The application uses a configuration system in `config.py` that allows you to easily change:

- Groq speech-to-text models
- Groq LLM models
- System prompts
- Temperature, max tokens, and other parameters
- Server configuration

You can update these settings:
1. Directly by editing `config.py`
2. At runtime through the API endpoints

### Available Models

#### Speech-to-Text Models
- `default` (whisper-large-v3-turbo) - Fast, good balance of speed and accuracy
- `high_accuracy` (whisper-large-v3) - Highest accuracy, slower
- `english_only` (distil-whisper-large-v3-en) - Fastest, English only

#### LLM Models
- `default` (llama3-70b-8192) - High quality model with large context window
- `fast` (llama3-8b-8192) - Faster, smaller model
- `mixtral` (mixtral-8x7b-32768) - Alternative model with large context
- `gemma` (gemma-7b-it) - Alternative smaller model

## Call Processing Flow

1. Vapi captures live audio from phone calls
2. Raw audio is sent to your webhook endpoint
3. Groq transcribes the audio to text using their speech-to-text API
4. Groq processes the transcribed text with its LLM
5. The response is sent back to the caller
6. Live transcripts and responses are broadcast to frontend clients via WebSockets

## Live Audio Transcription

The system now supports direct live audio transcription without requiring the Vapi telephony intermediary:

1. Client applications can stream audio directly to the backend via WebSocket
2. Audio is transcribed in real-time using Groq's speech-to-text API
3. Transcribed text is processed by Groq's LLM for response generation
4. Both transcripts and responses are broadcasted in real-time

### Using the Live Audio WebSocket

```javascript
// Connect to the live audio WebSocket
const ws = new WebSocket(`ws://your-server.com/ws/live-audio/${callId}`);

// Set up event handlers
ws.onopen = () => {
  console.log('WebSocket connection established');
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  switch (data.type) {
    case 'transcript':
      console.log('Live Transcript:', data.text);
      break;
    case 'response':
      console.log('AI Response:', data.text);
      break;
  }
};

// Stream audio data
function sendAudioChunk(audioChunk) {
  if (ws.readyState === WebSocket.OPEN) {
    ws.send(audioChunk);
  }
}

// Example with getUserMedia
navigator.mediaDevices.getUserMedia({ audio: true })
  .then(stream => {
    const mediaRecorder = new MediaRecorder(stream);
    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        sendAudioChunk(event.data);
      }
    };
    
    // Set up to capture audio in chunks
    mediaRecorder.start(100); // Capture in 100ms chunks
  });
```

### Using the Audio Upload Endpoint

For clients that can't use WebSockets, there's a REST endpoint:

```javascript
async function uploadAudio(callId, audioBlob) {
  const formData = new FormData();
  formData.append('audio', audioBlob);
  
  const response = await fetch(`http://your-server.com/calls/upload-audio/${callId}`, {
    method: 'POST',
    body: formData
  });
  
  return response.json();
}
```

### Testing Live Audio

Use the included test script to verify audio transcription:

```bash
# Install required dependencies
pip install pyaudio websockets

# Run the test script
python test_live_audio.py --call-id my-test-call
```

This script will:
1. Record audio from your microphone
2. Stream it to the backend via WebSocket
3. Show the transcribed text and AI responses in real-time

## Running the Application

Run the FastAPI server:
```bash
python main.py
```

The server will start on http://localhost:8000

## API Endpoints

### Call Management
- `POST /calls/start` - Start an outbound call
- `POST /calls/accept/{call_id}` - Accept an incoming call
- `POST /calls/end/{call_id}` - End an active call
- `GET /calls/{call_id}` - Get details about a specific call
- `GET /calls` - List all calls
- `POST /calls/upload-audio/{call_id}` - Upload audio for transcription and response generation

### Model Configuration
- `GET /models` - Get information about available models and current configuration
- `POST /models/update` - Update model settings at runtime

### Webhook
- `POST /webhook` - Webhook endpoint for Vapi events

### WebSockets
- `WebSocket /ws/call/{call_id}` - WebSocket for real-time call updates for a specific call
- `WebSocket /ws/monitor` - WebSocket for monitoring all calls (admin use)
- `WebSocket /ws/live-audio/{call_id}` - WebSocket for streaming live audio for real-time transcription

### Health
- `GET /` - Root endpoint with service info
- `GET /health` - Health check endpoint

## WebSocket for Real-time Updates

Connect to the WebSocket endpoint to receive real-time transcription and response updates:

```javascript
// Connect to a specific call
const ws = new WebSocket(`ws://your-server.com/ws/call/${callId}`);

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  // Handle different message types
  switch (data.type) {
    case 'transcript':
      console.log('Transcription:', data.text);
      // Update UI with live transcript
      break;
    case 'response':
      console.log('AI Response:', data.text);
      // Update UI with AI response
      break;
    case 'connected':
      console.log('Connected to call:', data.call_id);
      break;
  }
};
```

## Webhook Setup

To receive events and audio from Vapi:

1. Deploy this application to a server with a public URL
2. Configure your Vapi webhook URL to point to `https://your-domain.com/webhook`
3. Make sure your assistant configuration has `rawAudio: true`

## Notes

- For production, set up proper authentication and HTTPS
- Edit the `config.py` file to customize default settings
- Use the `/models/update` endpoint to change models at runtime without restarting 