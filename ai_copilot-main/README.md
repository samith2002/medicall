# AI Call Assistant

An AI-powered call assistant that transcribes and processes calls using Groq. Supports live audio transcription and real-time responses.

## Deployment with Modal

This application is now deployed using [Modal](https://modal.com/), a cloud platform for running Python applications.

### Setting up Modal

1. Install Modal CLI:
   ```
   pip install modal
   ```

2. Authenticate with Modal:
   ```
   modal token new
   ```

3. Set up secrets for the app:
   ```
   modal secret create ai-call-assistant-secrets \
     VAPI_API_KEY=your_vapi_key \
     GROQ_API_KEY=your_groq_key \
     WEBHOOK_URL=your_webhook_url \
     WEBHOOK_SECRET=your_webhook_secret \
     FRONTEND_URL=your_frontend_url
   ```

### Deploying the App

Run the deployment script:
```
./deploy-to-modal.sh
```

Or deploy manually:
```
modal deploy backend/modal_app.py
```

### Getting the Deployment URL

After deployment, you can find your app's URL with:
```
modal endpoints list
```

## Development

For local development:

1. Install requirements:
   ```
   pip install -r backend/requirements.txt
   ```

2. Run the application:
   ```
   python backend/main.py
   ```

## Frontend Development

1. Navigate to the frontend project directory:
   ```
   cd frontend/project
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Start development server:
   ```
   npm run dev
   ```

Make sure to update your frontend API endpoints to point to your Modal deployment URL instead of the previous Netlify function URLs. 