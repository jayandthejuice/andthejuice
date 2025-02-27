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
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email(to_email, subject, message, is_html=False):
    try:
        # Set up the email headers
        msg = MIMEMultipart()
        msg["From"] = SMTP_EMAIL
        msg["To"] = to_email
        msg["Subject"] = subject

        # Attach content (HTML or plain text)
        if is_html:
            msg.attach(MIMEText(message, "html"))  # HTML Email
        else:
            msg.attach(MIMEText(message, "plain"))  # Plain Text Email

        # Send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.sendmail(SMTP_EMAIL, to_email, msg.as_string())

        print(f"✅ Email sent to {to_email}")
    except Exception as e:
        print(f"❌ Error sending email: {e}")



# Function to schedule follow-up emails
def schedule_email(email, subject, message, delay_hour, is_html=False):
    def job():
        print(f"⏳ Waiting {delay_hour} hours before sending '{subject}' to {email}")
        time.sleep(delay_hour * 3600)
        send_email(email, subject, message, is_html=is_html)  # ✅ Pass `is_html`
    
    threading.Thread(target=job).start()


@app.route('/webhook', methods=['POST'])
def typeform_webhook():
    data = request.json  # Get JSON data from Typeform
    print("Received Webhook Data:", data)  # Print for debugging
    delay = 5 
    try:
        # Extract Email and First Name
        answers = data.get('form_response', {}).get('answers', [])
        email = None
        first_name = "there"
        last_choice = None

        if answers:
            first_name = answers[0].get('text', 'there')  # Always get the first answer as the first name
            for answer in answers:
                if answer.get('type') == 'email':
                    email = answer.get('email', '')

        # **Find the last multiple-choice answer**
            for answer in reversed(answers):  # Reverse loop to get the LAST multiple-choice question
                if answer.get('type') == 'choice':
                    last_choice = answer.get('choice', {}).get('label', '')
                elif answer.get('type') == 'choices':  # Handles multiple-choice selection
                    last_choice = ", ".join(answer.get('choices', {}).get('labels', []))

                if last_choice:  # Stop at the last valid choice found
                    last_choice = last_choice.strip().lower()  # Ensure text is cleaned
                    break
            
        if not email:
            raise ValueError("No email found in Typeform response")

        print(f"New Submission: {email}, Name: {first_name}, Last Choice: {last_choice}")

        # 📌 **Automate Email Sequence**
        # 1️⃣ **Thank You Email** (Immediate)
        thank_you_message_html = f"""\
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <p style="font-size: 16px; margin-bottom: 10px;">Hey {first_name},</p>
                <p>Most traders stay stuck in the same cycle, never making real progress. But today, you did something different. You took action.</p>
                <p>Your application is officially under review.</p>
                <p>That means you’re already ahead of most traders who never even try.</p>
                <p>Keep an eye on your inbox—your next update could be the one that changes everything.</p>
                <p>In the meantime, stay locked in. If you’re serious about trading, check out my latest insights on <a href="https://www.instagram.com/jaynjuicee" target="_blank">@jaynjuicee</a>—this is just the beginning.</p>
                <p>See you soon,</p>
                <p><strong>Jay</strong></p>
            </body>
        </html>
        """
        send_email(email, "Thank You for Your Application", thank_you_message_html, is_html=True)

        # 📌 **Check their last answer before proceeding**
        if last_choice == "no, let me go spend more money on coffee and stay stuck where i am forever.":
            rejection_message_html = f"""\
            <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <p style="font-size: 16px; margin-bottom: 10px;">Hey {first_name},</p>
                    <p>Regrettably,</p>
                    <p>I am unable to move forward with your application at this time. While this may not be the news you hoped for, I truly appreciate the time and effort you invested in applying.</p>
                    <p>Here’s the good news: this isn’t the end of your journey. Every great trader knows that persistence is the key to success. We encourage you to refine your skills, revisit your goals, and try applying again in the future when the next opportunity arises.</p>
                    <p>Remember, the journey to success is built on continuous growth and determination. I’m here to support you every step of the way.</p>
                    <p>Stay motivated, and I hope to see you back for the next round of applications.</p>
                </body>
            </html>
            """
            schedule_email(email, "Application Update", rejection_message_html, 8, is_html=True)
            return jsonify({"status": "success", "message": "Thank you and rejection email scheduled"}), 200

        # 2️⃣ **Processing Email** (After 7 hours)
        processing_message_html = f"""\
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <p style="font-size: 16px; margin-bottom: 10px;">Hey {first_name},</p>
                <p>Your application just moved one step forward.</p>
                <p>That means you showed commitment and readiness in your Typeform answers.</p>
                <p>Right now, I’m personally reviewing your application to see if you’re the right fit for <strong>&TheJuice</strong>.</p>
                <p>Not everyone makes it in. I’m only bringing in serious traders—the ones ready to execute and actually level up.</p>
                <p>If that’s you, stay ready. Spots are extremely limited, and once they’re gone, they’re gone.</p>
                <p>You’ll hear from me soon.</p>
                <p><strong>Jay</strong></p>
            </body>
        </html>
        """
        schedule_email(email, "Your Application Just Got One Step Closer", processing_message_html, 7,is_html=True)

        # 3️⃣ **Acceptance Email** (11 hours after Processing Email = 18 hours total)
        acceptance_message_html = f"""\
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
               <p style="font-size: 16px; margin-bottom: 10px;">Hey {first_name},</p>

                <p>Congratulations. You’ve officially been accepted to be a part of <strong>&TheJuice</strong>.</p>

                <p>Some members of &TheJuice paid off their subscription in their first month. Others passed their funded accounts for the first time. 
                Whatever milestone you hit, my goal is to make sure you keep leveling up—consistently.</p>

                <p><strong>Secure your spot here before it’s gone:</strong> 
                <a href="https://whop.com/checkout/plan_uAuyFvc2bfpZw?d2c=true" target="_blank">Click here to make your payment</a>.</p>

                <p><strong>Before you make the payment, know this—what you’re about to access has already changed lives.</strong> 
                It all depends on how badly you want it.</p>

                <p><strong>You’ll have access to:</strong></p>
                <ul>
                    <li>Attending and watching all the current and past Zoom meetings</li>
                    <li>Watching all the course details in-depth and taking notes</li>
                    <li>Competing for a chance to win funded accounts</li>
                    <li>Q&A section to ask any questions you have</li>
                </ul>

                <p>Just to be fair… if you don’t reserve your seat, I’m going to have to move it to the next person in line.</p>

                <p>Right now, payments are <strong>LIVE</strong>.</p>

                <p>You made it this far because you’re serious about growth. Now it’s time to show it.</p>

                <p>See you inside,</p>
                <p><strong>Jay</strong></p>
            </body>
        </html>
        """
      
        schedule_email(email, "Your Results Are Out - One Final Step", acceptance_message_html, 18, is_html=True)

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
