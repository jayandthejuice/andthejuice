from flask import Flask, request, jsonify
import smtplib
import datetime
import pytz
import os
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Initialize Flask app
app = Flask(__name__)

# Logging setup for better debugging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Use in-memory job store instead of PostgreSQL
scheduler = BackgroundScheduler(timezone=pytz.utc)
scheduler.start()
print("✅ Job store initialized in memory!")

# Email Configuration (Use environment variables for security)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_EMAIL = 'jayandthejuice@gmail.com'
SMTP_PASSWORD = 'igmv gihg guya mzem'  # Use environment variables for security

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

        if answers:
            first_name = answers[0].get('text', 'there')
            for answer in answers:
                if answer.get('type') == 'email':
                    email = answer.get('email', '')

        if not email:
            raise ValueError("No email found in Typeform response")

        logging.info(f"📌 New Submission: {email}, Name: {first_name}")

        # 1️⃣ **Thank You Email** (Immediate)
        thank_you_message_html = f"""\
        <html>
            <body style="font-family: Arial, sans-serif; font-size: 16px; line-height: 1.6; color: #333;">
                <p>Hey {first_name},</p>
                <p>Your application is officially under review.</p>
                <p>If approved, we will contact you within the next 48 hours.</p>
                <p>Want to skip the wait? You can <a href="https://calendly.com/jayandthejuice/15" target="_blank" style="color: #007BFF; text-decoration: none;">book a call now</a> to see if you qualify.</p>
                <p>See you on the inside…..hopefully 😉</p>
                <p>Best,</p>
                <p>Jay</p>
            </body>
        </html>
        """
        send_email(email, "Thank You for Your Application", thank_you_message_html, is_html=True)

        return jsonify({"status": "success", "message": "Webhook received, emails scheduled"}), 200

    except Exception as e:
        logging.error(f"❌ Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)), debug=True)
