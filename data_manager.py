import pandas as pd
import os
import calendar
from datetime import datetime, date

DATA_FILE = "data/DOB.xlsx"
COLUMNS = [
    "Name", "email", "dob", "phoneno", "skills", 
    "designation", "achievements", "about", "hobbies", "image0"
]

def initialize_data_file():
    """Creates the Excel file if it doesn't exist."""
    if not os.path.exists(DATA_FILE):
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        df = pd.DataFrame(columns=COLUMNS)
        df.to_excel(DATA_FILE, index=False)
        print(f"Created new data file at {DATA_FILE}")

def load_data():
    """Loads employee data from Excel."""
    initialize_data_file()
    try:
        df = pd.read_excel(DATA_FILE)
        df['dob'] = pd.to_datetime(df['dob'], errors='coerce')
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return pd.DataFrame(columns=COLUMNS)

def save_employee(employee_dict):
    """Appends a new employee to the Excel file."""
    initialize_data_file()
    try:
        df = pd.read_excel(DATA_FILE)
        if isinstance(employee_dict.get('dob'), str):
            employee_dict['dob'] = pd.to_datetime(employee_dict['dob'])
        df = pd.concat([df, pd.DataFrame([employee_dict])], ignore_index=True)
        df.to_excel(DATA_FILE, index=False)
        return True
    except Exception as e:
        print(f"Error saving employee: {e}")
        return False

def is_birthday(dob, today):
    """Logic to check if today is someone's birthday, including leap year handling."""
    if pd.isnull(dob) or today is None:
        return False

    if dob.month == 2 and dob.day == 29:
        if calendar.isleap(today.year):
            return today.month == 2 and today.day == 29
        else:
            return today.month == 2 and today.day == 28

    return dob.month == today.month and dob.day == today.day

def get_birthday_employees():
    df = load_data()
    today = date.today()
    birthday_employees = df[df['dob'].apply(lambda dob: is_birthday(dob, today))]
    return birthday_employees.to_dict('records')

def get_non_birthday_employees():
    df = load_data()
    today = date.today()
    birthday_mask = df['dob'].apply(lambda dob: is_birthday(dob, today))
    non_birthday_employees = df[~birthday_mask]
    return non_birthday_employees.to_dict('records')
