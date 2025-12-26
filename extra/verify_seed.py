import requests
import json
import sys

USN = "1RV23CS001"
URL = f"http://localhost:8000/profiles/{USN}"

try:
    print(f"Checking profile for {USN}...")
    response = requests.get(URL)
    if response.status_code == 200:
        data = response.json()
        print(f"SUCCESS: Profile found!")
        print(f"Name: {data.get('name')}")
        print(f"Strengths: {data.get('strengths')}")
    else:
        print(f"FAILED: Status {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"Error: {e}")
