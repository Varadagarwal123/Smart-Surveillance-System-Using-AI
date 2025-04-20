# # email_notification.py
# import smtplib
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart

# def send_email_notification(subject, body, recipient="shyamsingh78790@gmail.com"):
#     sender_email = "shyamsingh78790@gmail.com"
#     sender_password = "rwzg euyn udey exes"  # Replace with your generated app password

#     msg = MIMEMultipart()
#     msg['From'] = sender_email
#     msg['To'] = recipient
#     msg['Subject'] = subject
#     msg.attach(MIMEText(body, 'plain'))

#     try:
#         server = smtplib.SMTP('smtp.gmail.com', 587)
#         server.starttls()
#         server.login(sender_email, sender_password)
#         server.sendmail(sender_email, recipient, msg.as_string())
#         server.quit()
#         print("Email sent successfully.")
#     except Exception as e:
#         print(f"Failed to send email: {e}")



# email_notification.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os

def send_email_notification(subject, body, recipient="shyamsingh78790@gmail.com", attachments=None):
    sender_email = "shyamsingh78790@gmail.com"
    sender_password = "rwzg euyn udey exes"  # Replace with your generated app password

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    # Attach snapshots if provided
    if attachments:
        for file_path in attachments:
            with open(file_path, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename= {os.path.basename(file_path)}",
            )
            msg.attach(part)

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient, msg.as_string())
        server.quit()
        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")
