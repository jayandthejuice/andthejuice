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

# Initialize Flask app
app = Flask(__name__)

# Logging setup for better debugging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Use SQLite for persistent scheduling
scheduler = BackgroundScheduler(
    jobstores={"default": SQLAlchemyJobStore(url="sqlite:///jobs.sqlite")},
    timezone=pytz.utc
)
scheduler.start()

# Email Configuration (Use environment variables for security)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

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
        thank_you_message_html = f"""
        <html>
            <body>
                <p>Hey {first_name},</p>
                <p>Your application is officially under review. Keep an eye on your inbox—your next update could be the one that changes everything.</p>
                <p>Stay locked in. Follow <a href="https://www.instagram.com/jaynjuicee">@jaynjuicee</a> for insights.</p>
                <p>See you soon,<br><strong>Jay</strong></p>
            </body>
        </html>
        """
        send_email(email, "Thank You for Your Application", thank_you_message_html, is_html=True)

        # 2️⃣ **Check Rejection Condition**
        if last_choice == "no, let me go spend more money on coffee and stay stuck where i am forever.":
            rejection_message_html = f"""
            <html><body><p>Hey {first_name},</p>
            <p>Unfortunately, we won’t be moving forward with your application this time.</p>
            <p>Keep pushing forward!<br>Jay</p></body></html>
            """
            schedule_email(email, "Application Update", rejection_message_html, 8, is_html=True)
            return jsonify({"status": "success", "message": "Thank you and rejection email scheduled"}), 200

        # 3️⃣ **Processing Email (7 Hours Later)**
        processing_message_html = f"""
        <html><body><p>Hey {first_name},</p>
        <p>Your application just moved one step forward.</p>
        <p>Stay ready, and I’ll be in touch soon.</p></body></html>
        """
        schedule_email(email, "Your Application Just Got One Step Closer", processing_message_html, 7, is_html=True)

        # 4️⃣ **Acceptance Email (18 Hours Later)**
        acceptance_message_html = f"""
        <html><body><p>Hey {first_name},</p>
        <p>Congratulations, you’ve been accepted to <strong>&TheJuice</strong>.</p>
        <p><a href="https://whop.com/checkout/plan_uAuyFvc2bfpZw?d2c=true">Secure your spot here</a>.</p>
        <p>See you inside!<br>Jay</p></body></html>
        """
        schedule_email(email, "Your Results Are Out - One Final Step", acceptance_message_html, 18, is_html=True)

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
