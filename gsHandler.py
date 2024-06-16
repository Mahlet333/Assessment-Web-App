import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import json
import os

# Path to your service account key file
key_file_path = 'letsrise-caed029c5496.json'  # Path to your JSON key file
if not os.path.exists(key_file_path): 
    raise FileNotFoundError(f"Service account key file not found at {key_file_path}")

# Set up the credentials
scope = ["https://spreadsheets.google.com/feeds", 
         "https://www.googleapis.com/auth/drive",
         "https://www.googleapis.com/auth/spreadsheets"]
try:
    credentials = ServiceAccountCredentials.from_json_keyfile_name(key_file_path, scope)
    client = gspread.authorize(credentials)
    print("Successfully authenticated.")
except Exception as e:
    print(f"Error during authentication: {e}")
    raise e

def retrieve_data(sheet_id, sheet_name):
    try:  
        sheet = client.open_by_key(sheet_id).worksheet(sheet_name)
        data = sheet.get_all_records()
        print(f"Successfully retrieved data from the sheet. Number of records: {len(data)}")
    except Exception as e:
        print(f"Error retrieving data: {e}")
        raise
    return data

def create_new_sheet(title, folder_id, sheet_name=None):
    try:
        new_sheet = client.create(title, folder_id=folder_id)
        print(f"Successfully created new sheet: {new_sheet.title} in folder {folder_id}")
        
        if sheet_name:
            worksheet = new_sheet.get_worksheet(0) 
            worksheet.update_title(sheet_name)
            print(f"Successfully renamed sheet to: {sheet_name}")
        return new_sheet
    
    except Exception as e:
        print(f"Error creating new sheet in folder: {e}")
        raise
    
def create_new_page(sheet_id, page_name):
    try:
        sheet = client.open_by_key(sheet_id)
        new_page = sheet.add_worksheet(title=page_name, rows="100", cols="20")
        print(f"Successfully created new page: {new_page.title}")
        return new_page
    
    except Exception as e:
        print(f"Error creating new page: {e}")
        raise

def append_row(sheet_id, sheet_name, row_data): #row_data should be a list
    try:
        sheet = client.open_by_key(sheet_id).worksheet(sheet_name)
        sheet.append_row(row_data)
        print(f"Successfully appended row: {row_data}")
    except Exception as e:
        print(f"Error appending row: {e}")
        raise

def update_row(sheet_id, sheet_name, row_index, row_data):  # row_data should be a list
    try:
        sheet = client.open_by_key(sheet_id).worksheet(sheet_name)
        range_name = f'A{row_index}'
        sheet.update(range_name=range_name, values=[row_data])
        print(f"Successfully updated row {row_index} with data: {row_data}")
    except Exception as e:
        print(f"Error updating row: {e}")
        raise

def delete_sheet(sheet_id): # deletes the entire sheet
    try:
        sheet = client.open_by_key(sheet_id)
        client.del_spreadsheet(sheet_id)
        print(f"Successfully deleted sheet: {sheet.title}")
    except Exception as e:
        print(f"Error deleting sheet: {e}")
        raise

def delete_page(sheet_id, sheet_name):
    try:
        sheet = client.open_by_key(sheet_id)
        worksheet = sheet.worksheet(sheet_name)
        sheet.del_worksheet(worksheet)
        print(f"Successfully deleted worksheet: {sheet_name} from sheet: {sheet.title}")
    except Exception as e:
        print(f"Error deleting worksheet: {e}")
        raise

def delete_row(sheet_id, sheet_name, row_index):
    try:
        # Access the Google Sheet
        sheet = client.open_by_key(sheet_id).worksheet(sheet_name)
        sheet.delete_rows(row_index)
        print(f"Successfully deleted row {row_index} from worksheet: {sheet_name}")
    except Exception as e:
        print(f"Error deleting row: {e}")
        raise

# Creating a new sheet inside the data visualization project folder.
folder_id = '1vkz6D8eVLwbHzvDprLYPk0bPRGOoDScN'



