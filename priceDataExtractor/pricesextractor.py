import requests
import json
import os
import time

data_dir = "azure_prices_data"
os.makedirs(data_dir, exist_ok=True)

# Load endpoints from an external file
endpoints_file = "endpoints.txt"
endpoints = {}

with open(endpoints_file, "r") as file:
    for line in file:
        if line.strip():
            service_name, url = line.strip().split("|", 1)
            endpoints[service_name.strip()] = url.strip()

# Function to make the request and save data to a JSON file
def fetch_and_save_data(service_name, url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            # Save the response to a JSON file
            filename = os.path.join(data_dir, f"{service_name.replace(' ', '_').lower()}.json")
            with open(filename, "w") as json_file:
                json.dump(data, json_file, indent=4)
            print(f"Data saved for {service_name} in {filename}")
        else:
            print(f"Error fetching data for {service_name}: {response.status_code}")
    except requests.RequestException as e:
        print(f"Request error for {service_name}: {e}")

# Iterate over each service and extract information
def extract_data():
    for service_name, url in endpoints.items():
        print(f"Extracting data for {service_name}...")
        fetch_and_save_data(service_name, url)
        time.sleep(1)  # Wait one second between requests to avoid overloading the API

# Function to combine all JSON files into one
def combine_json():
    combined_data = []
    for filename in os.listdir(data_dir):
        if filename.endswith(".json"):
            with open(os.path.join(data_dir, filename), "r") as json_file:
                data = json.load(json_file)
                combined_data.extend(data.get("Items", []))
    # Save the combined JSON
    combined_filename = os.path.join(data_dir, "combined_azure_prices.json")
    with open(combined_filename, "w") as combined_file:
        json.dump(combined_data, combined_file, indent=4)
    print(f"Combined data saved in {combined_filename}")

if __name__ == "__main__":
    # Extract data from endpoints
    extract_data()
    # Combine all JSON files into one
    combine_json()
