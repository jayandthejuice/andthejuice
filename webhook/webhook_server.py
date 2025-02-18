from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def typeform_webhook():
    data = request.json  # Get the JSON data from Typeform
    print("Received Webhook Data:", data)

    # Extract useful information (adjust based on your form)
    try:
        email = data['form_response']['answers'][0]['email']
        print(f"New Submission: {email}")
        
        # You can now store this in a database or trigger email automation
        return jsonify({"status": "success", "message": "Webhook received"}), 200
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
