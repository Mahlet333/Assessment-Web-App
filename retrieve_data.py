import pandas as pd
import json
from gsHandler import retrieve_data, create_new_sheet, create_new_page, append_row, update_row

# Retrieving the assesment data ------------------------------------------------------------>
sheet_id = '1rUDTXpzyyLuHXc_Tq8lANaqxbyaOR6DOLAP4Nq7X9Q0'  
sheet_name = 'Assessment Form'
data = retrieve_data(sheet_id, sheet_name)

df = pd.DataFrame(data)
data_sorted = df.sort_values(by=['Question number', 'Decision Statement Value'])
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

data_json = json.dumps(data_dict, indent=4)
output_file_path = 'assessment_google_sheet.json'  
with open(output_file_path, 'w') as f:
    f.write(data_json)

print(f"JSON data has been saved to {output_file_path}")

# Retrieving the onboarding assesment data ------------------------------------------------->
sheet_id = '12ST6S5grqvL2Pqxg55NweT0SvqBlNN98YNxozCpu8GQ'
sheet_names = ['Pre-Idea', 'Pre-Launch', 'Post-Launch', 'Growth']

# Retrieve data from the Google Sheet
data_dict = {}
for sheet_name in sheet_names:
    try:
        data = retrieve_data(sheet_id, sheet_name)
        print(f"Data from sheet '{sheet_name}' successfully retrieved")
        data = pd.DataFrame(data)
        
        # Strip any leading/trailing whitespace from column names
        data.columns = data.columns.str.strip()
        for _, row in data.iterrows():
            if sheet_name not in data_dict:
                data_dict[sheet_name] = []
            data_dict[sheet_name].append({
                "Challenges": row["Challenges"].strip(),
                "Explanations": row["Explanations"].strip(),
                "Prerequisites": row["Prerequisites"].strip(),
            })
    except KeyError as e:
        print(f"KeyError processing data from sheet '{sheet_name}': {e}")
    except Exception as e:
        print(f"Error processing data from sheet '{sheet_name}': {e}")

data_json = json.dumps(data_dict, indent=4)
output_file_path = 'challenges.json'  
with open(output_file_path, 'w') as f:
    f.write(data_json)

print(f"JSON data has been saved to {output_file_path}")
