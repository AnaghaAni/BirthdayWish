import logging
import os
import sys
from datetime import date
from data_manager import get_birthday_employees, load_data
from emailer import send_emails_batch, SENDER_EMAIL
from html_generator import generate_html_card_content
from ai_generator import generate_email_subject

# Configuration
LOG_FILE = 'birthday_bot.log'
TEMPLATE_FILE = "birthday_card_template.html"

# Setup Logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def run_daily_check():
    """Main workflow to check birthdays and dispatch emails."""
    print("--- Valoriz Birthday Bot: Daily Execution ---")
    
    # 1. Fetch Birthday Data
    birthdays = get_birthday_employees()
    if not birthdays:
        print("[Status] No birthdays found for today. Exiting.")
        return

    print(f"[Status] Found {len(birthdays)} birthday(s) today.")

    # 2. Generate Content for each Birthday Employee
    birthday_records = []
    for emp in birthdays:
        html, photo = generate_html_card_content(TEMPLATE_FILE, emp)
        if html:
            birthday_records.append({
                'name': emp['Name'],
                'email': emp['email'],
                'html': html,
                'photo': photo
            })

    # 3. Prepare Email Queue
    email_tasks = []
    
    # --- Task A: Individual Private Wishes ---
    for record in birthday_records:
        subject = generate_email_subject('self', {'name': record['name']})
        plain_text = f"Happy Birthday {record['name']}!"
        
        # Format: (to_email, subject, body, attachment_paths, bcc_emails, html_body, inline_images, cc_emails)
        email_tasks.append((
            record['email'],
            subject,
            plain_text,
            None,   # Attachments
            [],     # BCC
            record['html'],
            [record['photo']] if record['photo'] else None,
            []      # CC (None for private)
        ))
        print(f" > Queued personal wish for: {record['name']}")

    # --- Task B: Team-wide Announcement (Using CC) ---
    all_employees_df = load_data()
    team_emails = list(set([
        e.strip() for e in all_employees_df['email'].tolist() 
        if isinstance(e, str) and e.strip()
    ]))

    if team_emails:
        subject_team = generate_email_subject('team')
        summary_html = "<html><body><h2 style='text-align:center; color:#1b8f6a;'>Today's Birthday Celebrations!</h2>"
        all_photos = []
        for record in birthday_records:
            summary_html += record['html']
            if record['photo']:
                all_photos.append(record['photo'])
        summary_html += "</body></html>"

        # Strategy: One Team Announcement email with CC list
        # We send TO the sender, and CC everyone else found in the sheet.
        # This ensures the birthday person (who is in the sheet) receives it.
        cc_list = [e for e in team_emails if e.lower() != SENDER_EMAIL.lower()]
        
        logging.info(f"Team notification queued for {len(cc_list)} CC recipients.")

        email_tasks.append((
            SENDER_EMAIL,     # To: Sender
            subject_team,
            "Today's Birthday Celebrations!",
            None,
            [],               # BCC (None)
            summary_html,
            list(set(all_photos)),
            cc_list           # CC (The Team)
        ))
        print(f" > Queued one team announcement with {len(cc_list)} CC recipients.")

    # 4. Dispatch All Emails in One SMTP Session
    if email_tasks:
        print(f"\n[Delivery] Opening secure SMTP connection for {len(email_tasks)} messages...")
        if send_emails_batch(email_tasks):
            print("[Success] All notifications dispatched successfully.")
            logging.info(f"Successfully sent {len(email_tasks)} emails.")
        else:
            print("[Error] Some or all emails failed to send. Check logs.")
            logging.error("Failed to complete the email batch.")
            sys.exit(1)

if __name__ == "__main__":
    try:
        run_daily_check()
    except Exception as e:
        print(f"[Critical Error] {e}")
        logging.critical(f"Bot crashed: {e}", exc_info=True)
        sys.exit(1)
