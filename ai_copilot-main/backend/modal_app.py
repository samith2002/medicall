import os
import sys
from pathlib import Path
import modal

# Create a Modal image with our dependencies
image = modal.Image.debian_slim().apt_install(
    "portaudio19-dev", "python3-pyaudio"
).run_commands(
    "pip install --upgrade pip"
).pip_install(
    "fastapi",
    "uvicorn",
    "python-dotenv",
    "pydantic",
    "httpx",
    "websockets",
    "python-multipart",
    "vapi_python",
    "groq"
)

# Conditionally install pyaudio if not skipped
if not os.getenv("MODAL_SKIP_PYAUDIO", "").lower() == "true":
    image = image.pip_install("pyaudio")

# Get the backend directory path
backend_dir = Path(__file__).parent

# Add the backend directory to the image
image = image.copy_local_dir(
    local_path=str(backend_dir),
    remote_path="/backend"
)

# Create the Modal app
app = modal.App("ai-call-assistant", image=image)

@app.function(
    container_idle_timeout=60,
    secrets=[
        modal.Secret.from_name("ai-call-assistant-secrets")
    ]
)
@modal.asgi_app()
def fastapi_app():
    # Add backend to Python path
    sys.path.append("/backend")
    
    # Import the FastAPI app
    from main import app as fastapi_app
    return fastapi_app

if __name__ == "__main__":
    # Using the method available in version 0.64.178
    modal.run(fastapi_app) 