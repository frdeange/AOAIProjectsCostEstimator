from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

def get_azure_monitor_pricing(region, is_poc):
    # Call the API to get the JSON data for Azure Monitor pricing
    response = requests.get('http://localhost:5000/prices/azure_monitor')
    if response.status_code == 200:
        data = response.json()
    else:
        return {"Error": "Failed to retrieve data from the API."}

    # Filter data by specified region
    region_filtered_data = [
        item for item in data
        if item['armRegionName'].lower() == region.lower()
    ]

    # Define placeholders for potential filters
    # Example: Filtering for Data Ingestion
    ingestion_data = next(
        (item for item in region_filtered_data if "Ingestion" in item['meterName']),
        None
    )

    # Example: Filtering for Data Retention
    retention_data = next(
        (item for item in region_filtered_data if "Retention" in item['meterName']),
        None
    )

    # Return fixed cost based on the project type
    if is_poc:
        # Fixed cost for PoC projects
        return {"Total Cost (USD)": 100}
    else:
        # Fixed cost for full projects
        return {"Total Cost (USD)": 300}

@app.route('/get_azure_monitor_pricing', methods=['POST'])
def get_azure_monitor_pricing_api():
    data = request.get_json()
    region = data.get('region')
    is_poc = data.get('is_poc')

    if not region or is_poc is None:
        return jsonify({"Error": "Missing required parameters: 'region' or 'is_poc'."}), 400

    result = get_azure_monitor_pricing(region, is_poc)
    return jsonify(result)

if __name__ == '__main__':
    app.run(port=5009, debug=True)