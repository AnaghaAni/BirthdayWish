import json
import os
import random
import logging
from google import genai
from dotenv import load_dotenv

# Environment Init
load_dotenv()

# Constants
API_KEY = os.getenv("GEMINI_API_KEY")
USED_WISHES_FILE = "used_wishes.json"
MODEL_NAME = "gemini-2.5-flash"

# Client Setup
client = genai.Client(api_key=API_KEY) if API_KEY else None

def load_used_wishes():
    """Load historical wishes to ensure uniqueness."""
    if os.path.exists(USED_WISHES_FILE):
        try:
            with open(USED_WISHES_FILE, "r", encoding="utf-8") as f:
                content = json.load(f)
                return set(content) if isinstance(content, list) else set()
        except Exception as e:
            logging.debug(f"Could not load used wishes: {e}")
    return set()

def save_used_wish(wish):
    """Store a newly generated wish in history."""
    try:
        used_wishes = load_used_wishes()
        used_wishes.add(wish.strip())
        with open(USED_WISHES_FILE, "w", encoding="utf-8") as f:
            json.dump(list(used_wishes), f, ensure_ascii=False, indent=4)
    except Exception as e:
        logging.error(f"Failed to save wish history: {e}")

def get_standard_fallback(name):
    """A collection of polished fallback wishes if AI fails."""
    fallbacks = [
        f"Happy Birthday, {name}! Wishing you a day filled with joy, and a year ahead as bright and impactful as you are.",
        f"Wishing a fantastic birthday to {name}! We truly appreciate the wonderful spirit you bring to our team every day.",
        f"Happy Birthday, {name}! May your special day be the start of a year full of happiness, success, and new adventures.",
        f"Cheers to {name} on your birthday! We're so glad to have you with us. Have a wonderful celebration!",
    ]
    return random.choice(fallbacks)

def generate_birthday_wish(employee):
    """Generates a personalized birthday wish using AI, with polished fallbacks."""
    name = employee.get('Name', 'Colleague')
    
    if not client:
        return get_standard_fallback(name)

    used_wishes = load_used_wishes()
    details = {
        "Name": name,
        "Role": employee.get('designation', 'Team Member'),
        "Skills": employee.get('skills', 'N/A'),
        "Hobbies": employee.get('hobbies', 'N/A'),
        "About": employee.get('about', 'N/A')
    }

    # Decide if we have enough info for a deep personalization
    missing_info = sum(1 for v in details.values() if v in ["N/A", "", None])
    themes = ["Warm and Friendly", "Encouraging and Bright", "Cheerful and Energetic", "Simple and Professional"]
    selected_theme = random.choice(themes)

    if missing_info >= 3:
        prompt = f"Write a polished, professional birthday wish for {name} (30 words). Tone: {selected_theme}."
    else:
        prompt = f"""
        Write a professional birthday wish for {name}.
        Role: {details['Role']} | Hobbies: {details['Hobbies']} | Personality: {details['About']}

        REQUIREMENTS:
        1. NO LISTING: Do not list skills like 'Python' specifically. Describe their value instead.
        2. CREATIVITY: Integrate a subtle metaphor related to their hobbies if possible.
        3. TONE: {selected_theme}.
        4. LENGTH: 30-35 words exactly.
        """

    try:
        response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
        wish = response.text.strip().replace('"', '')
        
        # Uniqueness check
        if wish not in used_wishes:
            save_used_wish(wish)
            return wish
    except Exception as e:
        logging.warning(f"AI Generation failed for {name}: {e}")

    return get_standard_fallback(name)

def generate_email_subject(context_type, details=None):
    """Returns context-appropriate email subjects."""
    if details is None: details = {}
    name = details.get('name', 'Colleague')
    
    subjects = {
        'self': f"Happy Birthday, {name}! 🎂",
        'team': f"Celebrating Birthdays Today! "
    }
    return subjects.get(context_type, "Birthday Celebration! ")
