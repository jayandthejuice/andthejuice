import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import pandas as pd

def send_emails(csv_file, sender_email, sender_password, subject, body_html, attachment_path=None):
    # Read the CSV file into a pandas DataFrame
    df = pd.read_csv(csv_file)

    # Ensure that the file has an 'email' column
    if 'email' not in df.columns:
        raise ValueError("The CSV file must contain an 'email' column.")

    # Get the list of email addresses
    email_addresses = df['email'].str.strip()

    # Set up the SMTP server
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    try:
        # Connect to the SMTP server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)

        # Loop through each email address and send an email
        for email in email_addresses:
            # Create the email message
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = email
            msg['Subject'] = subject

            # Attach the email body (HTML)
            msg.attach(MIMEText(body_html, 'html'))

            # Attach a file, if provided
            if attachment_path:
                try:
                    with open(attachment_path, 'rb') as attachment_file:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(attachment_file.read())
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename={attachment_path.split("/")[-1]}',
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
csv_file = 'emails.csv'  # Replace with your CSV file containing email addresses
sender_email = 'jayandthejuice@gmail.com'  # Replace with your email address
sender_password = 'igmv gihg guya mzem'  # Replace with your email password
subject = 'This is the last email you’ll hear from me'

body_html = '''
<html>
<body>
<p>If you’re getting this, then you’re probably late—things happen and I understand.</p>
<p>We’re already at full capacity just 10 mins after the launch, but I’ll be doing you a favour since it’s the beginning of the year & a fresh start — by opening it up just a few more seats—for you.</p>
<p>Simply because I know what it feels like to just be starting out and I don’t want you to stay stuck where you are for your whole life.</p>
<p>Attached is the PowerPoint presentation I went over with all of the participants during the webinar (almost all of them are on the inside now).</p>
<p>It walks you through everything—what’s waiting for you inside Founders & thejuice, the benefits of being part of this community, and why this opportunity is so unique at this moment in time.</p>
<p>On the 15th, the payment will at least be double and you definitely won’t be one of the FOUNDERS.</p>
<p>Imagine how it’s going to look like when you can’t get your hands on the same thing that others already have for a much cheaper price… I wouldn’t want that personally— which is why I am where I am.</p>
<p>This is it. This is the last email you’ll hear from me; I’m not going to follow you around to convince you to change YOUR OWN LIFE, all I can do is give you my advice… do what you want with it.</p>
<p>I need to focus on the people who actually took the step forward to change their lives, not the people that just SAY they want to take action—because 10/10 time these people stay where they are. (which is not the quality of people I’m looking for to begin with).</p>
<p>Most of the people I’ve accepted secured their spots within the first 10 minutes… and are now part of a community committed to growth.</p>
<p>This is your moment to decide: Will you step up and claim your spot, or will you let this pass you by?</p>
<p>Spots are limited, and they won’t stay open for long.</p>
<p>Here’s your link - go for it, or don’t:<br>
<a href="https://whop.com/thejuice/">https://whop.com/thejuice/</a></p>
<p>You’ve said you want to change your life—this is the time to do it.</p>
<p>I wish you the best on your future endeavours— I have to go focus on the people that want change.</p>
<p>The choice is yours.</p>
<p>Best,<br>Jay</p>
</body>
</html>
'''

attachment_path = 'Founders_&thejuice.pdf'  # Replace with the file path of your attachment (or None if no attachment)

send_emails(csv_file, sender_email, sender_password, subject, body_html, attachment_path)
