import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import json
import os

# Path to your service account key file
key_file_path = 'xxx'  # Path to your JSON key file

# Verify the key file exists
if not os.path.exists(key_file_path):
    raise FileNotFoundError(f"Service account key file not found at {key_file_path}")

# Google Sheet ID and sheet name
sheet_id = 'xxx'  # Google Sheet ID
sheet_name = 'Sheet1'  # Sheet name if different

# Set up the credentials
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
try:
    credentials = ServiceAccountCredentials.from_json_keyfile_name(key_file_path, scope)
    client = gspread.authorize(credentials)
    print("Successfully authenticated.")
except Exception as e:
    print(f"Error during authentication: {e}")
    raise

try:
    # Access the Google Sheet
    sheet = client.open_by_key(sheet_id).worksheet(sheet_name)
    print(f"Successfully accessed the Google Sheet: {sheet.title}")
except gspread.exceptions.APIError as e:
    print(f"APIError: {e}")
    raise
except Exception as e:
    print(f"Unexpected error: {e}")
    raise

# Get all values in the sheet
try:
    data = sheet.get_all_records()
    print(f"Successfully retrieved data from the sheet. Number of records: {len(data)}")
except Exception as e:
    print(f"Error retrieving data: {e}")
    raise

# Convert to a pandas DataFrame
df = pd.DataFrame(data)

# Sort the data by 'Question number' and 'Decision Statement Value'
data_sorted = df.sort_values(by=['Question number', 'Decision Statement Value'])

# Convert to JSON format
data_dict = {}
for _, row in data_sorted.iterrows():
    question_number = row['Question number']
    if question_number not in data_dict:
        data_dict[question_number] = []
    data_dict[question_number].append({
        "Decision Statement": row["Decision Statement"].replace('"', ''),
        "Decision Statement Value": row["Decision Statement Value"],
        "Trait Number": row["Trait Number"],
        "Trait Name": row["Trait Name"],
        "Scenario": row["Scenario"]
    })

# Convert the dictionary to JSON
data_json = json.dumps(data_dict, indent=4)

# Save the JSON to a file
output_file_path = 'assessment_google_sheet.json'  # Change this to your desired output path
with open(output_file_path, 'w') as f:
    f.write(data_json)

print(f"JSON data has been saved to {output_file_path}")
