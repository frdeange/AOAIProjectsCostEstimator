from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

def get_dns_pricing(region, is_poc):
    # Call the API to get the JSON data
    response = requests.get('http://localhost:5000/prices/azure_dns')
    if response.status_code == 200:
        data = response.json()
    else:
        return {"Error": "Failed to retrieve data from the API."}

    # If it's a PoC, no data is required
    if is_poc:
        return {"Message": "No data required for PoC."}

    # Define the zone based on the region
    zone = "Zone 3" if region.lower() == "italynorth" else "Zone 1"

    # Filter for "Azure DNS Private" in the correct zone, "Private Zone" and "Private Queries", with no minimum units
    filtered_results = [
        item for item in data
        if item['skuName'] == "Private" and
        item['meterName'] in ["Private Zone", "Private Queries"] and
        item['armRegionName'] == zone and
        item['tierMinimumUnits'] == 0
    ]

    # Format the results
    if filtered_results:
        return [
            {
                "Meter": item['meterName'],
                "Price per Unit": item['unitPrice'],
                "SKU ID": item['skuId']
            } for item in filtered_results
        ]
    else:
        return {"Error": "No results matching the criteria were found."}

@app.route('/get_dns_pricing', methods=['POST'])
def get_dns_pricing_api():
    data = request.get_json()
    region = data.get('region')
    is_poc = data.get('is_poc')

    if not region or is_poc is None:
        return jsonify({"Error": "Missing required parameters: 'region' or 'is_poc'."}), 400

    result = get_dns_pricing(region, is_poc)
    return jsonify(result)

if __name__ == '__main__':
    app.run(port=5007, debug=True)