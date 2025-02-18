from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def typeform_webhook():
    data = request.json  # Get the JSON data from Typeform
    print("Received Webhook Data:", data)  # Print full data for debugging

    try:
        # Ensure "form_response" and "answers" exist
        answers = data.get('form_response', {}).get('answers', [])

        # Extract email from answers
        email = None
        for answer in answers:
            if answer.get('type') == 'email':  # Look for the email type
                email = answer.get('email', '')  # Get the email value
                break  # Stop loop when found

        if not email:
            raise ValueError("No email found in Typeform response")

        print(f"New Submission: {email}")

        return jsonify({"status": "success", "message": "Webhook received"}), 200

    except Exception as e:
        print(f"Error: {e}")  # Print error in logs
        return jsonify({"status": "error", "message": str(e)}), 400

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))  # Use Render's assigned port
    app.run(host="0.0.0.0", port=port, debug=True)
