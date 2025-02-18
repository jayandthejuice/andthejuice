import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import pandas as pd

def send_emails(csv_file, sender_email, sender_password, subject, body_template, attachment_path=None):
    # Read the CSV file into a pandas DataFrame
    df = pd.read_csv(csv_file)

    # Check if 'email' column exists
    if 'email' not in df.columns:
        raise ValueError("The CSV file must contain an 'email' column.")
    
    # Extract first names if 'name' column exists, otherwise set empty string
    if 'name' in df.columns:
        df['first_name'] = df['name'].apply(lambda x: str(x).split()[0] if pd.notna(x) else "")
    else:
        df['first_name'] = ""
    
    # Set up the SMTP server
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    try:
        # Connect to the SMTP server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)

        # Loop through each email address and send an email
        for email, first_name in zip(df['email'], df['first_name']):
            # Personalize the email body by replacing the placeholder
            personalized_body = body_template.replace("[First Name]", first_name)

            # Create the email message
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = email
            msg['Subject'] = subject

            # Attach the email body (plain text)
            msg.attach(MIMEText(personalized_body, 'plain'))

            # Attach a file if provided
            if attachment_path:
                try:
                    with open(attachment_path, 'rb') as attachment_file:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(attachment_file.read())
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename={attachment_path.split("/")[-1]}'
                    )
                    msg.attach(part)
                except Exception as e:
                    print(f"Could not attach file {attachment_path}: {e}")

            # Send the email
            server.sendmail(sender_email, email, msg.as_string())
            print(f"Email sent to {email}")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Close the SMTP server connection
        server.quit()

# Example usage
csv_file = 'test_emails.csv'  # Replace with your actual CSV file
sender_email = 'jayandthejuice@gmail.com'  # Replace with your email
sender_password = 'igmv gihg guya mzem'  # Replace with your email password
subject = 'Final Call – Your Spot Expires in 12 Hours'

# Email body template
body_template = """
Hey,

If you’re already in, then congrats. We caught a 1:17 RR trade in your first Zoom session. A great preview for what’s about to come.

For those of you who haven’t reserved your seat…

You were accepted because I saw potential in you. But you haven’t locked in your spot.

Meanwhile, new members are already in — and there are more than 50 applicants on the waitlist ready to claim your seat.

In 12 hours, your acceptance is gone. No exceptions.

You’re going to have to go through the application process all over again.

I can’t want this more than you do.

Secure your spot now: https://whop.com/checkout/plan_uAuyFvc2bfpZw?d2c=true

This is it. Your move.

I hope to see you on the inside my friend,
Jay
"""

attachment_path = None  # Replace with the file path of your attachment (or None if no attachment)

send_emails(csv_file, sender_email, sender_password, subject, body_template, attachment_path)
