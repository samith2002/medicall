import os
import json
from flask import Flask, request, jsonify, abort
import hmac
import hashlib
import datetime # To store a timestamp

app = Flask(__name__)

# --- Configuration ---
VAPI_SERVER_URL_SECRET = os.environ.get("VAPI_SERVER_URL_SECRET", None) # Optional secret

# --- In-Memory Storage (for demo purposes only!) ---
# In a real app, use a database or calendar API
scheduled_meetings = []
# ----------------------------------------------------

# --- Security Middleware (Optional but Recommended) ---
@app.before_request
def verify_signature():
    # Same verification logic as in the previous Python example...
    # It checks the X-Vapi-Signature header if VAPI_SERVER_URL_SECRET is set.
    # It also parses the JSON payload into request.vapi_payload
    if VAPI_SERVER_URL_SECRET:
        signature = request.headers.get('X-Vapi-Signature')
        if not signature:
            print("WARN: Missing X-Vapi-Signature header")
            abort(401)
        request_body = request.get_data()
        hashed = hmac.new(VAPI_SERVER_URL_SECRET.encode('utf-8'), request_body, hashlib.sha256)
        expected_signature = hashed.hexdigest()
        if not hmac.compare_digest(expected_signature, signature):
            print(f"WARN: Invalid signature.")
            abort(403)
        else:
            try:
                request.vapi_payload = json.loads(request_body.decode('utf-8'))
            except json.JSONDecodeError:
                 print("ERROR: Could not parse JSON after signature verification")
                 abort(400, description="Invalid JSON payload")
    else:
         try:
            # Try to parse JSON even without secret
            request.vapi_payload = request.get_json(silent=True) # Use silent=True
            if request.vapi_payload is None and request.content_length > 0:
                print("WARN: Request body is not valid JSON or content type is not application/json")
                # Don't abort here immediately, let the main handler decide based on need
         except Exception as e:
            print(f"ERROR: Could not parse JSON in before_request: {e}")
            # Don't abort here, main handler might not need JSON


@app.route('/vapi-webhook', methods=['POST'])
def handle_vapi_webhook():
    """Handles incoming POST requests from Vapi."""
    payload = getattr(request, 'vapi_payload', None)

    # Fallback if before_request didn't parse or wasn't needed
    if payload is None:
        try:
            payload = request.get_json()
            if payload is None:
                 print("ERROR: Payload is missing or invalid JSON in main handler")
                 return jsonify({"error": "Invalid JSON payload"}), 400
        except Exception as e:
            print(f"ERROR: Could not parse JSON payload in main handler: {e}")
            return jsonify({"error": "Could not parse JSON payload"}), 400


    print(f"\n--- Received Vapi Webhook ---")
    print(json.dumps(payload, indent=2))
    print("-----------------------------\n")

    message = payload.get('message', {})
    message_type = message.get('type')

    try:
        # --- Handle Function Calls ---
        if (message_type == 'assistant-request' or message_type == 'function-call') and message.get('functionCall'):
            print(f"INFO: Received function call request")
            return handle_function_call(message['functionCall'])

        # --- Handle other message types (optional logging) ---
        elif message_type == 'transcript' and message.get('transcriptType') == 'final':
            print(f"TRANSCRIPT ({message.get('role')}): {message.get('transcript')}")
            return jsonify(success=True), 200
        elif message_type in ['call-start', 'call-end', 'hangup', 'speech-update']:
             print(f"INFO: Received message type: {message_type}")
             return jsonify(success=True), 200
        else:
            print(f"WARN: Received unhandled message type or structure: {message_type}")
            return jsonify({"message": f"Unhandled type: {message_type}"}), 200

    except Exception as e:
        print(f"ERROR: Exception processing webhook: {e}")
        # Add more detailed logging/tracing in production
        return jsonify({"error": "Internal server error processing request"}), 500


def handle_function_call(function_call_data):
    """Processes function calls requested by Vapi."""
    function_name = function_call_data.get('name')
    parameters = function_call_data.get('parameters')

    print(f"Executing function: {function_name}")
    print(f"Parameters: {json.dumps(parameters, indent=2)}")

    result = None
    error_message = None

    # --- Scheduling Logic ---
    if function_name == 'scheduleMeeting':
        try:
            attendee = parameters.get('attendeeName')
            date_str = parameters.get('date')
            time_str = parameters.get('time')

            if not all([attendee, date_str, time_str]):
                error_message = "Missing required parameters (attendeeName, date, or time)."
            else:
                # **Simple Demo:** Store in memory
                meeting_details = {
                    "attendee": attendee,
                    "date": date_str,
                    "time": time_str,
                    "scheduled_at": datetime.datetime.utcnow().isoformat() + "Z"
                }
                scheduled_meetings.append(meeting_details)
                print(f"INFO: Meeting scheduled: {meeting_details}")
                print(f"Total meetings stored: {len(scheduled_meetings)}")

                # **Craft success response for Vapi to say**
                result = f"Okay, I've scheduled a meeting with {attendee} for {date_str} at {time_str}."

        except Exception as e:
            print(f"ERROR: Failed to execute scheduleMeeting: {e}")
            error_message = "Sorry, I encountered an internal error while trying to schedule the meeting."

    # --- Add other function handlers here ---
    # elif function_name == 'someOtherFunction':
    #    # ... logic ...
    #    pass

    else:
        print(f"WARN: Unknown function called: {function_name}")
        error_message = f"Sorry, I don't know how to handle the function '{function_name}'."

    # --- Respond to Vapi ---
    if error_message:
         # Return the error message for Vapi to potentially say
         return jsonify({"result": error_message})
    else:
        # Return the successful result for Vapi to say
        return jsonify({"result": result})


if __name__ == '__main__':
    # Run on 0.0.0.0 to be accessible externally (like via ngrok)
    # Use a port (e.g., 5001) that ngrok will forward to
    app.run(host='0.0.0.0', port=5001, debug=True) # Turn off debug in production