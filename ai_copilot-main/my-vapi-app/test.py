import requests
import json

# --- Configuration ---
# This should match the host and port your app.py is running on
FLASK_SERVER_URL = "http://localhost:5001/vapi-webhook"
# ------------------

def test_schedule_meeting():
    """
    Sends a simulated function call request for 'scheduleMeeting'
    to the running Flask server.
    """
    print(f"Attempting to send request to: {FLASK_SERVER_URL}")

    # 1. Construct the payload simulating Vapi's function call
    #    This structure should match what your handle_vapi_webhook expects
    test_payload = {
        "message": {
            "type": "assistant-request", # Common type containing function calls
            "functionCall": {
                "name": "scheduleMeeting",
                "parameters": {
                    "attendeeName": "Dr. Evelyn Reed",
                    "date": "next Wednesday",
                    "time": "4:00 PM"
                }
            },
            # You can add other dummy fields if your handler expects them,
            # but keep it minimal for testing the function call itself.
            "call": {"id": "test-call-123"},
            "requestType": "function-call-request" # Example, actual value might differ
        }
    }

    print("\n--- Sending Payload ---")
    print(json.dumps(test_payload, indent=2))
    print("-----------------------\n")

    try:
        # 2. Send the POST request with the JSON payload
        response = requests.post(
            FLASK_SERVER_URL,
            json=test_payload, # requests library handles Content-Type header
            headers={"Content-Type": "application/json"} # Explicitly set header
        )

        # 3. Process the response
        print(f"--- Server Response ---")
        print(f"Status Code: {response.status_code}")

        try:
            response_data = response.json()
            print("Response Body (JSON):")
            print(json.dumps(response_data, indent=2))

            # 4. Check if the response indicates success (basic check)
            if response.status_code == 200 and 'result' in response_data:
                print("\n✅ Test Result: SUCCESS!")
                print(f"Server returned result message: '{response_data['result']}'")
                # More specific check: Does the result contain the attendee's name?
                if test_payload["message"]["functionCall"]["parameters"]["attendeeName"] in response_data.get("result", ""):
                     print("Result message correctly includes the attendee's name.")
                else:
                     print("⚠️ Warning: Result message might not contain the expected attendee name.")

            elif response.status_code == 200:
                 print("\n⚠️ Test Result: OK (Status 200), but 'result' field missing in JSON response.")
                 print(f"Full response: {response_data}")
            else:
                print(f"\n❌ Test Result: FAIL (Status Code: {response.status_code})")
                print(f"Response Body: {response.text}") # Print raw text for non-JSON or error responses

        except json.JSONDecodeError:
            print("\n❌ Test Result: FAIL (Server response was not valid JSON)")
            print(f"Response Body (Raw Text): {response.text}")
        except Exception as e:
             print(f"\n❌ Test Result: FAIL (Error processing response: {e})")
             print(f"Response Body (Raw Text): {response.text}")


    except requests.exceptions.ConnectionError:
        print("\n❌ Test Result: FAIL (Connection Error)")
        print(f"Could not connect to the server at {FLASK_SERVER_URL}.")
        print("--> Please ensure the Flask app (app.py) is running.")
    except Exception as e:
        print(f"\n❌ Test Result: FAIL (An unexpected error occurred)")
        print(f"Error details: {e}")

# --- Run the test ---
if __name__ == "__main__":
    test_schedule_meeting()