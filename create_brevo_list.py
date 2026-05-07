import os
import requests
from dotenv import load_dotenv

load_dotenv()

BREVO_API_KEY = os.getenv('BREVO_API_KEY')
HEADERS = {
    "accept": "application/json",
    "api-key": BREVO_API_KEY,
    "content-type": "application/json"
}

# Step 1: Get existing folders
print("Fetching folders...")
folders_url = "https://api.brevo.com/v3/contacts/folders"
response = requests.get(folders_url, headers=HEADERS)

if response.status_code == 200:
    folders = response.json().get('folders', [])
    if folders:
        folder_id = folders[0]['id']
        print(f"Using existing folder ID: {folder_id}")
    else:
        # Create a folder if none exist
        create_folder_url = "https://api.brevo.com/v3/contacts/folders"
        folder_data = {"name": "Website"}
        folder_response = requests.post(create_folder_url, headers=HEADERS, json=folder_data)
        folder_id = folder_response.json().get('id')
        print(f"Created folder with ID: {folder_id}")
else:
    # Try creating a folder directly
    print("Creating new folder...")
    create_folder_url = "https://api.brevo.com/v3/contacts/folders"
    folder_data = {"name": "Website"}
    folder_response = requests.post(create_folder_url, headers=HEADERS, json=folder_data)
    
    if folder_response.status_code in [200, 201]:
        folder_id = folder_response.json().get('id')
        print(f"Created folder with ID: {folder_id}")
    else:
        print(f"Folder creation failed: {folder_response.status_code} - {folder_response.text}")
        exit()

# Step 2: Create the list in that folder
print("Creating Website Subscribers list...")
lists_url = "https://api.brevo.com/v3/contacts/lists"
list_data = {
    "name": "Website Subscribers",
    "folderId": folder_id
}

list_response = requests.post(lists_url, headers=HEADERS, json=list_data)
print("Status:", list_response.status_code)

if list_response.status_code in [201, 200]:
    result = list_response.json()
    print("✅ List created successfully!")
    print("📌 List ID:", result.get('id'))
    print("📌 List Name:", result.get('name'))
    print("\n👉 Add this to your .env file:")
    print(f"   BREVO_LIST_ID={result.get('id')}")
else:
    print("❌ Error:", list_response.text)