# create_Demo.py
import csv
import random
import json
from pathlib import Path
import sys
from datetime import datetime

# Add parent directory to path to import from demo folder
sys.path.append(str(Path(__file__).parent.parent))
from demo.generate_demo_data import generate_student_profile as generate_student_data

def load_names_from_csv(csv_path):
    """Load USN and names from the CSV file"""
    names = []
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if 'USN' in row and 'NAME' in row:
                    names.append({
                        'usn': row['USN'].strip(),
                        'name': row['NAME'].strip()
                    })
        return names
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return []

def generate_demo_profiles(csv_path, output_path, num_profiles=600):
    # Load names from CSV
    names = load_names_from_csv(csv_path)
    
    if not names:
        print("No names found in the CSV file.")
        return
    
    # Limit to requested number of profiles
    names = names[:num_profiles]
    
    profiles = []
    for i, student in enumerate(names, 1):
        # Generate demo data using the correct function and pass USN
        demo_data = generate_student_data(student['usn'])
        
        # Create profile
        profile = {
            "id": student['usn'],
            "name": student['name'],
            "strengths": demo_data['strengths'],
            "weaknesses": demo_data['weaknesses'],
            "preferences": demo_data['preferences'],
            "description": demo_data['description'],
            "created_at": datetime.utcnow().isoformat()
        }
        profiles.append(profile)
        
        # Print progress
        if i % 50 == 0 or i == len(names):
            print(f"Generated {i}/{len(names)} profiles...")
    
    # Save to JSON file
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(profiles, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Successfully generated {len(profiles)} demo profiles at:")
    print(f"   {output_path.absolute()}")

if __name__ == "__main__":
    # Paths - using absolute paths to be safe
    base_dir = Path(__file__).parent
    csv_path = base_dir / "new.csv"  # Changed to look in the same directory
    output_path = base_dir / "demo_profiles.json"
    
    print("=== Demo Profile Generator ===")
    print(f"Reading names from: {csv_path}")
    print(f"Output will be saved to: {output_path}\n")
    
    generate_demo_profiles(csv_path, output_path)