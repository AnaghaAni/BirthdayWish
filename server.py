from flask import Flask, request, render_template_string
import os
from data_manager import save_employee

app = Flask(__name__)
UPLOAD_FOLDER = 'assets/photos'

@app.route('/')
def home():
    with open('registration_form.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/register', methods=['POST'])
def register():
    try:
        data = {
            "Name": request.form.get('name'),
            "email": request.form.get('email'),
            "dob": request.form.get('dob'),
            "phoneno": request.form.get('phone'),
            "designation": request.form.get('designation'),
            "skills": request.form.get('skills'),
            "hobbies": request.form.get('hobbies'),
            "achievements": request.form.get('achievements'),
            "about": request.form.get('about')
        }

        image = request.files.get('image_path')
        img_name = ""
        if image and image.filename:
            safe_name = data['Name'].replace(" ", "_").lower() + os.path.splitext(image.filename)[1]
            image.save(os.path.join(UPLOAD_FOLDER, safe_name))
            img_name = safe_name
        data["image0"] = img_name

        if save_employee(data):
            return render_template_string("""
                <div style="font-family: Arial; text-align: center; margin-top: 50px;">
                    <h2 style="color: #27ae60;">Success!</h2>
                    <p>Employee Registered Successfully.</p>
                    <a href="/">Back</a>
                </div>
            """)
        return "Failed", 500
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
