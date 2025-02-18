from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def typeform_webhook():
    data = request.json  # Get the JSON data from Typeform
    print("Received Webhook Data:", data)  # Print full data for debugging

    try:
        # Print the full Typeform response to debug the structure
        if not data or 'form_response' not in data:
            raise ValueError("Invalid JSON format from Typeform")

        # Extract answers
        answers = data['form_response'].get('answers', [])
        email = None

        # Loop through answers to find the email field
        for answer in answers:
            if answer.get('type') == 'email':
                email = answer.get('email', '')
                break  # Stop once email is found

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
