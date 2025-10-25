import os
import json
import requests

script_dir = os.path.dirname(os.path.abspath(__file__))
response_file = os.path.join(script_dir, "response.json")

# Fetch data from API
def fetch_data():
    url = "https://community-api.coinmetrics.io/v4/catalog/asset-metrics?pretty=true"  # Replace with actual API endpoint
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return {}

# Load existing data or initialize
if not os.path.exists(response_file):
    print(f"Creating a new {response_file}.")
    with open(response_file, "w") as file:
        json.dump({}, file)

# Fetch and update data
with open(response_file, "r+") as json_file:
    try:
        data = json.load(json_file)
        new_data = fetch_data()  # Replace with your data-fetching logic
        data.update(new_data)  # Merge new data
        json_file.seek(0)
        json.dump(data, json_file, indent=4)
        json_file.truncate()
        print("Data updated successfully!")
    except json.JSONDecodeError:
        print(f"Invalid JSON in {response_file}. Resetting file.")
        with open(response_file, "w") as file:
            json.dump(fetch_data(), file)
