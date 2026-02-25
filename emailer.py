import smtplib
import os
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.utils import formatdate, make_msgid, parseaddr
from dotenv import load_dotenv

# Initialize Environment
load_dotenv()

# SMTP Configuration
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")

def create_message(to_email, subject, body, attachment_paths=None, html_body=None, inline_images=None, cc_emails=None):
    """
    Constructs a standards-compliant MIMEMultipart email message.
    """
    msg = MIMEMultipart('mixed')
    msg['From'] = f"Valoriz Birthday Bot <{SENDER_EMAIL}>"
    msg['To'] = to_email
    if cc_emails:
        msg['Cc'] = ", ".join(cc_emails)
    msg['Subject'] = subject
    msg['Date'] = formatdate(localtime=True)
    msg['Message-ID'] = make_msgid()
    
    # Anti-Spam / Auto-Response Headers
    msg['Precedence'] = 'bulk'
    msg['X-Auto-Response-Suppress'] = 'All'
    msg['Auto-Submitted'] = 'auto-generated'

    # Alternative plain/HTML part
    msg_alt = MIMEMultipart('alternative')
    msg.attach(msg_alt)
    msg_alt.attach(MIMEText(body, 'plain'))

    if html_body:
        msg_related = MIMEMultipart('related')
        msg_alt.attach(msg_related)
        msg_related.attach(MIMEText(html_body, 'html'))

        if inline_images:
            from email.mime.image import MIMEImage
            for img_path in inline_images:
                if img_path and os.path.exists(img_path):
                    try:
                        with open(img_path, 'rb') as f:
                            img = MIMEImage(f.read())
                            cid = os.path.basename(img_path)
                            img.add_header('Content-ID', f'<{cid}>')
                            img.add_header('Content-Disposition', 'inline', filename=str(cid))
                            msg_related.attach(img)
                    except Exception as e:
                        logging.warning(f"Could not attach image {img_path}: {e}")

    # File Attachments
    if attachment_paths:
        for path in attachment_paths:
            if os.path.exists(path):
                try:
                    with open(path, "rb") as attachment:
                        part = MIMEBase("application", "octet-stream")
                        part.set_payload(attachment.read())
                        encoders.encode_base64(part)
                        part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(path)}")
                        msg.attach(part)
                except Exception as e:
                    logging.warning(f"Could not attach file {path}: {e}")
                    
    return msg

def send_emails_batch(tasks):
    """
    Sends a queue of email tasks using a persistent SMTP connection.
    Each task: (to_email, subject, body, attachment_paths, bcc_emails, html_body, inline_images)
    """
    if not SENDER_EMAIL or not SENDER_PASSWORD:
        logging.error("SMTP credentials missing from environment.")
        return False

    success_count = 0
    try:
        # Establish connection
        server = smtplib.SMTP(str(SMTP_SERVER), int(SMTP_PORT))
        server.starttls()
        server.login(str(SENDER_EMAIL), str(SENDER_PASSWORD))
        
        for task in tasks:
            try:
                # Unpack task (handles varying tuple lengths safely)
                to_email = task[0]
                subject = task[1]
                body = task[2]
                attachment_paths = task[3]
                bcc_emails = task[4]
                html_body = task[5]
                inline_images = task[6]
                cc_emails = task[7] if len(task) > 7 else []

                msg = create_message(to_email, subject, body, attachment_paths, html_body, inline_images, cc_emails)
                
                # Determine Envelope Recipients (To + CC + BCC)
                _, to_addr = parseaddr(str(to_email))
                envelope_recipients = [to_addr.strip()]
                
                # Add CCs to envelope
                if cc_emails:
                    for cc in cc_emails:
                        _, addr = parseaddr(str(cc))
                        clean_addr = addr.strip()
                        if clean_addr and clean_addr not in envelope_recipients:
                            envelope_recipients.append(clean_addr)

                # Add BCCs to envelope (BCCs do NOT go in create_message/headers)
                if bcc_emails:
                    for bcc in bcc_emails:
                        _, addr = parseaddr(str(bcc))
                        clean_addr = addr.strip()
                        if clean_addr and clean_addr not in envelope_recipients:
                            envelope_recipients.append(clean_addr)
                
                # Send
                server.sendmail(str(SENDER_EMAIL), envelope_recipients, msg.as_string())
                success_count += 1
                print(f"   [OK] {subject[:30]}... -> {to_addr} (+ {len(envelope_recipients)-1} CC/BCC)")
            except Exception as e:
                logging.error(f"Failed to send email to {to_email}: {e}")
                print(f"   [FAIL] {to_email}: {e}")
            
        server.quit()
        return success_count == len(tasks)
        
    except Exception as e:
        logging.critical(f"SMTP Session Error: {e}")
        return False
