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

            Most traders stay stuck in the same cycle, never making real progress. But today, you did something different. You took action.

            Your application is officially under review.

            That means you’re already ahead of most traders who never even try.

            Keep an eye on your inbox—your next update could be the one that changes everything.

            In the meantime, stay locked in. If you’re serious about trading, check out my latest insights on Instagram (@jaynjuicee)—this is just the beginning.

            See you soon,

            Jay
            """
        send_email(email, "Thank You for Your Application", thank_you_message)

        # 2️⃣ **Processing Email** (After 7 hours)
        processing_message = f"""Hey {first_name},
            Your application just moved one step forward.

            That means you showed commitment and readiness in your type-form answers.

            Right now, I’m personally reviewing your application to see if you’re the right fit for &thejuice.

            Not everyone makes it in. I’m only bringing in serious traders—the ones ready to execute and actually level up.

            I don’t care about quantity. I care about quality.

            If that’s you, stay ready. Spots are extremely limited, and once they’re gone, they’re gone.

            You’ll hear from me soon.

            Jay

            """
        schedule_email(email, "Your Application Just Got One Step Closer", processing_message, 7)

        # 3️⃣ **Acceptance Email** (30 hours after Processing Email = 52 hours total)
        acceptance_message = f"""Hey {first_name},

       Congratulations. You’ve officially been accepted to be a part of &thejuice.

        Some members of &thejuice paid off their subscription in their first month. Others passed their  funded accounts for the first time. Whatever milestone you hit, my goal is to make sure you keep levelling up—consistently.

        Secure your spot here before it’s gone: https://whop.com/checkout/plan_uAuyFvc2bfpZw?d2c=true

        Before you make the payment, know this—what you’re about to access has already changed lives. It all depends on how badly you want it.

        You’ll have access to all of the following: 

        •⁠  ⁠Attending and watching all the current and past zoom meetings
        •⁠  ⁠Watching all the course details in depth and taking your notes
        •⁠  ⁠Competing for a chance to win funded accounts
        •⁠  ⁠Q&A section to ask any questions you have

        Just to be fair… if you don’t reserve your seat, I’m going to have to move it to the next person in line.

        Right now, payments are LIVE.

        You made it this far because you’re serious about growth. Now it’s time to show it.

        See you inside.

        Jay

        """
        schedule_email(email, "Your Results Are Out - One Final Step", acceptance_message, 11)

        # 4️⃣ **Follow-up Email** 
        follow_up_message = f"""Hey {first_name},

            A few days ago, you applied to &TheJuice—and you got accepted.

            Some traders saw the opportunity, took action, and are already inside, attending Zoom calls, breaking down charts, and competing for funded accounts.

            You’re still on the fence.

            That’s fine. But I just want to ask you: What’s stopping you?

            If it’s the price… consider this:

            In the next 6 months, if you order a coffee from Starbucks every day you’d have made the same investment but left with nothing in return. I’m providing you with the exact strategy, weekly sessions, and challenges to make it easier for you.

            If you’re serious about trading, you know what to do.

            Lock in your spot before we move forward: https://whop.com/checkout/plan_uAuyFvc2bfpZw?d2c=true

            See you on the inside,

            Jay
            """
        schedule_email(email, "They locked in. Will you?", follow_up_message, 28)

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

            Jay
"""
        send_email(email, "Welcome to &thejuice – You’re In!", payment_message)

        return jsonify({"status": "success", "message": "Payment email sent"}), 200

    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 400

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Use Render's assigned port
    app.run(host="0.0.0.0", port=port, debug=True)
