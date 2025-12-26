import pandas as pd
import requests
import random
import time

# Configuration
EXCEL_FILE = r"D:\5th Sem\peer matcher\3rd Sem CS CY & CD 2024 Student list with Batches.xlsx"
API_URL = "http://localhost:8000/signup"
SHEETS = ['CS Lab 2 Sections', 'CD Lab 2 Section', 'CY Lab 2 Section']
DEFAULT_PASSWORD = "12345678"

# Technical skills pool
SUBJECTS = [
    "Mathematics", "Physics", "Chemistry", "Biology",
    "Computer Science", "Programming", "English Literature",
    "Creative Writing", "History", "Economics",
    "Psychology", "Business", "Statistics", "Art", "Music",
    "Python", "Java", "C++", "Web Development", "Machine Learning",
    "Data Science", "Artificial Intelligence", "Cyber Security",
    "Cloud Computing", "IoT", "Blockchain", "DevOps"
]

def generate_random_profile(usn, name):
    num_strengths = random.randint(2, 5)
    num_weaknesses = random.randint(1, 4)
    
    # Shuffle subjects to get random selection
    random.shuffle(SUBJECTS)
    
    strengths = SUBJECTS[:num_strengths]
    weaknesses = SUBJECTS[num_strengths:num_strengths+num_weaknesses]
    
    return {
        "id": usn,
        "name": name,
        "password": DEFAULT_PASSWORD,
        "strengths": ", ".join(strengths),
        "weaknesses": ", ".join(weaknesses),
        "preferences": "",
        "description": f"Student from {usn[:7]}" # Basic description
    }

def seed_database():
    print(f"Reading Excel file: {EXCEL_FILE}")
    try:
        xl = pd.ExcelFile(EXCEL_FILE)
    except Exception as e:
        print(f"Failed to load Excel file: {e}")
        return

    total_added = 0
    total_failed = 0
    
    for sheet in SHEETS:
        if sheet not in xl.sheet_names:
            print(f"Skipping missing sheet: {sheet}")
            continue
            
        print(f"\nProcessing sheet: {sheet}...")
        
        # Read first few rows to find header
        df_temp = xl.parse(sheet, header=None, nrows=10)
        header_idx = -1
        for i, row in df_temp.iterrows():
            row_str = row.astype(str).str.upper().tolist()
            if any("USN" in str(x) for x in row_str):
                header_idx = i
                break
        
        if header_idx == -1:
            print(f"  Warning: Could not find 'USN' header in first 10 rows of {sheet}")
            continue
            
        # Parse with correct header
        df = xl.parse(sheet, header=header_idx)
        
        # Clean column names (strip whitespace)
        df.columns = df.columns.str.strip()
        
        print(f"  Found header at row {header_idx}. Columns: {list(df.columns[:5])}...")
        
        # Verify columns exist
        if 'USN' not in df.columns or 'STUDENT FULL NAME' not in df.columns:
            print(f"  Warning: Required columns not found in {sheet}. Columns: {list(df.columns)}")
            continue
            
        # Iterate over rows
        for index, row in df.iterrows():
            usn = str(row['USN']).strip()
            name = str(row['STUDENT FULL NAME']).strip()
            
            # Skip invalid rows (e.g., NaN, empty strings)
            if not usn or usn.lower() == 'nan' or not name or name.lower() == 'nan':
                continue
                
            # Generate profile payload
            payload = generate_random_profile(usn, name)
            
            try:
                response = requests.post(API_URL, json=payload)
                if response.status_code in [200, 201]:
                    print(f"  [SUCCESS] Added {usn}: {name}")
                    total_added += 1
                elif response.status_code == 400 and "already exists" in response.text:
                     print(f"  [SKIPPED] {usn} already exists")
                else:
                    print(f"  [FAILED] {usn}: {response.status_code} - {response.text}")
                    total_failed += 1
            except Exception as e:
                print(f"  [ERROR] Connection failed for {usn}: {e}")
                total_failed += 1
                
    print(f"\n--- Seeding Complete ---")
    print(f"Total Added: {total_added}")
    print(f"Total Failed: {total_failed}")

if __name__ == "__main__":
    seed_database()
