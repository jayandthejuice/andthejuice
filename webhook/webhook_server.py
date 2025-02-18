from flask import Flask, request, jsonify
import smtplib
import threading
import time
import os

app = Flask(__name__)

# SMTP Email Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_EMAIL = "jayandthejuice@gmail.com"  # Replace with your email
SMTP_PASSWORD = "igmv gihg guya mzem"  # Replace with an App Password if using Gmail

# Function to send an email
def send_email(to_email, subject, message):
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            
            # Ensure UTF-8 encoding to handle special characters
            email_message = f"Subject: {subject}\nMIME-Version: 1.0\nContent-Type: text/plain; charset=UTF-8\n\n{message}"
            
            server.sendmail(SMTP_EMAIL, to_email, email_message.encode("utf-8"))
        print(f"✅ Email sent to {to_email}")
    except Exception as e:
        print(f"❌ Error sending email: {e}")


# Function to schedule follow-up emails
def schedule_email(email, subject, message, delay_hours):
    def job():
        time.sleep(delay_hours * 3600)  # Convert hours to seconds
        send_email(email, subject, message)
    
    threading.Thread(target=job).start()

@app.route('/webhook', methods=['POST'])
def typeform_webhook():
    data = request.json  # Get JSON data from Typeform
    print("Received Webhook Data:", data)  # Print for debugging

    try:
        # Extract Email and First Name
        answers = data.get('form_response', {}).get('answers', [])
        email = None
        first_name = "there"

        for answer in answers:
            if answer.get('type') == 'email':
                email = answer.get('email', '')
            if answer.get('type') == 'text':  # First Name field
                first_name = answer.get('text', '')

        if not email:
            raise ValueError("No email found in Typeform response")

        print(f"New Submission: {email}, Name: {first_name}")

        # 📌 **Automate Email Sequence**
        # 1️⃣ **Thank You Email** (Immediate)
        thank_you_message = f"""Hey {first_name},

*Congrats—you just took the first step toward something big.*

Most traders stay stuck in the same cycle, never making real progress. You? You just did something different. You took action.

Your application has been successfully submitted.

Keep an eye on your inbox. The next time you hear from me, it’ll be about whether you’re moving forward.

In the meantime, if you’re serious about trading, take a look at my latest insights on (@jaynjuicee) on Instagram.

Stay locked in.

See you soon,

*Jay*
"""
        send_email(email, "Thank You for Your Application!", thank_you_message)

        # 2️⃣ **Processing Email** (After 22 hours)
        processing_message = """Hey,

I just wanted to tell you that your application has moved one step forward since your submission. 

Right now, I am personally reviewing your application to see if you’re the right fit for &thejuice.

Not everyone makes it in. I’m only bringing in serious traders—the ones who are ready to execute and actually change their game. 

I don’t care about quantity, I want quality traders.

If that’s you, stay ready. Spots are limited, and once they’re gone, they’re gone.

You’ll hear from me soon.

– Jay
"""
        schedule_email(email, "Processing Your Application", processing_message, 22)

        # 3️⃣ **Acceptance Email** (30 hours after Processing Email = 52 hours total)
        acceptance_message = f"""Hey {first_name},

*Congratulations.* You’ve officially been accepted into &thejuice.

📍 *Secure your spot before it’s gone:* [Payment Link]

Before you make the payment, know this—what you’re about to access has already changed lives. It all depends on how badly you want it.

This includes: 
• Attending and watching all the current and past Zoom meetings
• Watching all the course details in depth and taking your notes
• Engaging with the community to learn and help other traders

*Not everyone gets this opportunity, because not everyone can commit to winning.*

So just to be fair… if you don’t reserve your seat, I’m going to have to move it to the next person in line.

Right now, payments are *LIVE, and spots are **disappearing fast**.*

You made it this far because you’re serious about growth. Now it’s time to show it.

See you inside.

– Jay
"""
        schedule_email(email, "You’ve Been Accepted!", acceptance_message, 52)

        # 4️⃣ **Follow-up Email** (12 hours after Acceptance Email = 64 hours total)
        follow_up_message = """Hey,

Just checking in. You’ve come this far, and I want to make sure you don’t miss out.

This is your chance to get in, join the community, and take your trading game to the next level.

If you’re still interested, here’s your link again: [Payment Link]

But if you’re not serious, that’s okay too. Just know that the next round might not come anytime soon.

Hope to see you inside.

– Jay
"""
        schedule_email(email, "Last Chance – Secure Your Spot", follow_up_message, 64)

        return jsonify({"status": "success", "message": "Webhook received, emails scheduled"}), 200

    except Exception as e:
        print(f"❌ Error: {e}")  # Print error in logs
        return jsonify({"status": "error", "message": str(e)}), 400

# 📌 **Route for Payment Confirmation Webhook**
@app.route('/payment-confirmation', methods=['POST'])
def payment_confirmation():
    data = request.json
    print("Received Payment Webhook Data:", data)

    try:
        email = data.get("email")
        if not email:
            raise ValueError("No email found in payment webhook")

        # 📌 **Thank You for Payment Email**
        payment_message = """Hey,

Thank you for starting this journey.

You made the commitment, and I respect that.

I can’t wait to see how much you grow inside &thejuice. It’s time to level up.

Check your email for access details, and let’s get started.

See you inside.

– Jay
"""
        send_email(email, "Welcome to &thejuice – You’re In!", payment_message)

        return jsonify({"status": "success", "message": "Payment email sent"}), 200

    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 400

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Use Render's assigned port
    app.run(host="0.0.0.0", port=port, debug=True)
