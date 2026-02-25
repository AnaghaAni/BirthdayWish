from ai_generator import generate_birthday_wish
import os

def generate_html_card_content(template_path, employee_data):
    if not os.path.exists(template_path): return None, None
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()

    wish = generate_birthday_wish(employee_data)
    photo_file = str(employee_data.get('image0', '')).strip()
    photo_path = os.path.join("assets", "photos", photo_file)
    final_path = photo_path if photo_file and os.path.exists(photo_path) else None

    replacements = {
        "{{PHOTO_DATA}}": f"cid:{photo_file}" if final_path else "",
        "{{NAME}}": employee_data.get('Name', 'Colleague'),
        "{{MESSAGE}}": wish,
        "{{PHOTO_DISPLAY}}": "table-row" if final_path else "none",
        "{{CARD_PADDING}}": "30px 20px",
        "{{FRAME_BG}}": "#e9f4ef" if final_path else "transparent",
        "{{FRAME_PADDING}}": "15px" if final_path else "0",
        "{{FRAME_SHADOW}}": "box-shadow: 0 8px 20px rgba(0,0,0,0.08);" if final_path else "",
        "{{NAME_PADDING_TOP}}": "12px" if final_path else "0",
        "{{NAME_FONT_SIZE}}": "22px" if final_path else "32px",
        "{{MESSAGE_PADDING_TOP}}": "25px",
        "{{MESSAGE_FONT_SIZE}}": "15px" if final_path else "18px"
    }

    for k, v in replacements.items():
        content = content.replace(k, str(v))
    return content, final_path
