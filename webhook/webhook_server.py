from flask import Flask, request, jsonify
import smtplib
import datetime
import pytz
import os
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from sqlalchemy import create_engine
# Initialize Flask app
app = Flask(__name__)

# Logging setup for better debugging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Use SQLite for persistent scheduling
POSTGRES_URL = os.getenv("DATABASE_URL")  # Get it from .env

jobstores = {
    "default": SQLAlchemyJobStore(url=POSTGRES_URL)  # Use PostgreSQL instead of SQLite
}

scheduler = BackgroundScheduler(jobstores=jobstores, timezone=pytz.utc)
scheduler.start()
print("✅ Job store initialized in PostgreSQL!")


# Email Configuration (Use environment variables for security)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_EMAIL = 'jayandthejuice@gmail.com'
SMTP_PASSWORD = 'igmv gihg guya mzem'
def send_email(email, subject, message, is_html=False):
    """ Sends an email using SMTP """
    try:
        logging.info(f"📧 Sending email to {email} | Subject: {subject}")

        msg = MIMEMultipart()
        msg["From"] = SMTP_EMAIL
        msg["To"] = email
        msg["Subject"] = subject
        msg.attach(MIMEText(message, "html" if is_html else "plain"))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.sendmail(SMTP_EMAIL, email, msg.as_string())

        logging.info(f"✅ Email sent successfully to {email}")

    except Exception as e:
        logging.error(f"❌ Error sending email: {e}")

def schedule_email(email, subject, message, delay_hour, is_html=False):
    """ Schedules an email to be sent after a delay """
    run_time = datetime.datetime.now(pytz.utc) + datetime.timedelta(hours=delay_hour)
    job_id = f"{email}_{subject.replace(' ', '_')}"

    logging.info(f"⏳ Scheduling email to {email} in {delay_hour} hours (at {run_time})")

    scheduler.add_job(
        send_email,
        'date',
        run_date=run_time,
        args=[email, subject, message, is_html],
        id=job_id,
        replace_existing=True  # Avoid duplicate scheduling
    )

@app.route("/schedule-email", methods=["POST"])
def schedule_email_api():
    """ API endpoint to schedule an email """
    data = request.json
    email = data.get("email")
    subject = data.get("subject", "No Subject")
    message = data.get("message", "")
    delay_hour = data.get("delay_hour", 0)
    is_html = data.get("is_html", False)

    if not email:
        return jsonify({"error": "Email is required"}), 400

    schedule_email(email, subject, message, delay_hour, is_html)
    return jsonify({"message": f"Email to {email} scheduled in {delay_hour} hours"}), 200

@app.route('/webhook', methods=['POST'])
def typeform_webhook():
    """ Handles Typeform webhook submissions """
    data = request.json
    logging.info(f"📩 Received Webhook Data: {data}")

    try:
        # Extract Email and First Name
        answers = data.get('form_response', {}).get('answers', [])
        email = None
        first_name = "there"
        last_choice = None

        if answers:
            first_name = answers[0].get('text', 'there')
            for answer in answers:
                if answer.get('type') == 'email':
                    email = answer.get('email', '')

            for answer in reversed(answers):
                if answer.get('type') == 'choice':
                    last_choice = answer.get('choice', {}).get('label', '')
                elif answer.get('type') == 'choices':
                    last_choice = ", ".join(answer.get('choices', {}).get('labels', []))
                if last_choice:
                    last_choice = last_choice.strip().lower()
                    break

        if not email:
            raise ValueError("No email found in Typeform response")

        logging.info(f"📌 New Submission: {email}, Name: {first_name}, Last Choice: {last_choice}")

        # 1️⃣ **Thank You Email** (Immediate)
        thank_you_message_html = f"""\
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <p style="font-size: 16px; margin-bottom: 10px;">Hey {first_name},</p>
                
                <p>Your application is officially under review.</p>
                
                <p>That means you’re already ahead of most traders who never even try.</p>
                
                <p>If approved, we will contact you within the next 48 hours.</p>
                
                <p><strong>OR</strong></p>
                
                <p>Want to skip the wait? You can <a href="https://calendly.com/jayandthejuice/15" target="_blank" style="color: #007BFF; text-decoration: none;">book a call now</a> to see if you qualify.</p>
                
                <p>Most traders stay stuck in the same cycle, never making real progress. But today, you did something different. You took action.</p>
                
                <p>See you on the inside…..hopefully 😉</p>
                
                <p>Best,</p>
                <p><strong>Jay</strong></p>
            </body>
        </html>
        """
        send_email(email, "Thank You for Your Application", thank_you_message_html, is_html=True)

        # 2️⃣ **Check Rejection Condition**
        # if last_choice == "no, let me go spend more money on coffee and stay stuck where i am forever.":
        #     rejection_message_html = f"""\
        #     <html>
        #         <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        #             <p style="font-size: 16px; margin-bottom: 10px;">Hey {first_name},</p>
        #             <p>Regrettably,</p>
        #             <p>I am unable to move forward with your application at this time. While this may not be the news you hoped for, I truly appreciate the time and effort you invested in applying.</p>
        #             <p>Here’s the good news: this isn’t the end of your journey. Every great trader knows that persistence is the key to success. We encourage you to refine your skills, revisit your goals, and try applying again in the future when the next opportunity arises.</p>
        #             <p>Remember, the journey to success is built on continuous growth and determination. I’m here to support you every step of the way.</p>
        #             <p>Stay motivated, and I hope to see you back for the next round of applications.</p>
        #         </body>
        #     </html>
        #     """
        #     schedule_email(email, "Application Update", rejection_message_html, 8, is_html=True)
        #     return jsonify({"status": "success", "message": "Thank you and rejection email scheduled"}), 200

        # # 3️⃣ **Processing Email (7 Hours Later)**
        # processing_message_html = f"""\
        # <html>
        #     <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        #         <p style="font-size: 16px; margin-bottom: 10px;">Hey {first_name},</p>
        #         <p>Your application just moved one step forward.</p>
        #         <p>That means you showed commitment and readiness in your Typeform answers.</p>
        #         <p>Right now, I’m personally reviewing your application to see if you’re the right fit for <strong>&TheJuice</strong>.</p>
        #         <p>Not everyone makes it in. I’m only bringing in serious traders—the ones ready to execute and actually level up.</p>
        #         <p>If that’s you, stay ready. Spots are extremely limited, and once they’re gone, they’re gone.</p>
        #         <p>You’ll hear from me soon.</p>
        #         <p><strong>Jay</strong></p>
        #     </body>
        # </html>
        # """
        # schedule_email(email, "Your Application Just Got One Step Closer", processing_message_html, 7, is_html=True)

        # # 4️⃣ **Acceptance Email (18 Hours Later)**
        # acceptance_message_html = f"""\
        # <html>
        #     <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        #        <p style="font-size: 16px; margin-bottom: 10px;">Hey {first_name},</p>

        #         <p>Congratulations. You’ve officially been accepted to be a part of <strong>&TheJuice</strong>.</p>

        #         <p>Some members of &TheJuice paid off their subscription in their first month. Others passed their funded accounts for the first time. 
        #         Whatever milestone you hit, my goal is to make sure you keep leveling up—consistently.</p>

        #         <p><strong>Secure your spot here before it’s gone:</strong> 
        #         <a href="https://whop.com/checkout/plan_uAuyFvc2bfpZw?d2c=true" target="_blank">Click here to make your payment</a>.</p>

        #         <p><strong>Before you make the payment, know this—what you’re about to access has already changed lives.</strong> 
        #         It all depends on how badly you want it.</p>

        #         <p><strong>You’ll have access to:</strong></p>
        #         <ul>
        #             <li>Attending and watching all the current and past Zoom meetings</li>
        #             <li>Watching all the course details in-depth and taking notes</li>
        #             <li>Competing for a chance to win funded accounts</li>
        #             <li>Q&A section to ask any questions you have</li>
        #         </ul>

        #         <p>Just to be fair… if you don’t reserve your seat, I’m going to have to move it to the next person in line.</p>

        #         <p>Right now, payments are <strong>LIVE</strong>.</p>

        #         <p>You made it this far because you’re serious about growth. Now it’s time to show it.</p>

        #         <p>See you inside,</p>
        #         <p><strong>Jay</strong></p>
        #     </body>
        # </html>
        # """
        # schedule_email(email, "Your Results Are Out - One Final Step", acceptance_message_html, 18, is_html=True)

        return jsonify({"status": "success", "message": "Webhook received, emails scheduled"}), 200

    except Exception as e:
        logging.error(f"❌ Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/payment-confirmation', methods=['POST'])
def payment_confirmation():
    """ Handles payment confirmation webhook """
    data = request.json
    logging.info(f"💳 Received Payment Webhook Data: {data}")

    try:
        email = data.get("email")
        if not email:
            raise ValueError("No email found in payment webhook")

        # **Thank You for Payment Email**
        payment_message = "Thank you for your commitment! You’re in. Check your email for access details. See you inside. - Jay"
        send_email(email, "Welcome to &TheJuice – You’re In!", payment_message)

        return jsonify({"status": "success", "message": "Payment email sent"}), 200

    except Exception as e:
        logging.error(f"❌ Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)), debug=True)
