from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

def get_pricing(region, is_poc):
    # Call the API to get the JSON data
    response = requests.get('http://localhost:5000/prices/azure_app_service')
    if response.status_code == 200:
        data = response.json()
    else:
        return {"Error": "Failed to retrieve data from the API."}

    # Define filtering criteria based on the type of project
    if is_poc:
        os_filter = 'Linux'
        tier_filter = 'Standard'
        sku_name_filter = 'S2'
    else:
        os_filter = 'Linux'
        tier_filter = 'Premium v2'
        sku_name_filter = 'P2 v2'

    # Filter the data
    filtered_results = [
        item for item in data
        if item['armRegionName'].lower() == region.lower() and
        os_filter.lower() in item['productName'].lower() and
        tier_filter.lower() in item['productName'].lower() and
        item['skuName'] == sku_name_filter
    ]

    # Check if any results were found and return the first one
    if filtered_results:
        return {
            "Hourly Price": filtered_results[0]['unitPrice'],
            "SKU ID": filtered_results[0]['skuId']
        }
    else:
        return {"Error": "No results matching the criteria were found."}

@app.route('/get_app_service_pricing', methods=['POST'])
def get_app_service_pricing():
    data = request.get_json()
    region = data.get('region')
    is_poc = data.get('is_poc')

    if not region or is_poc is None:
        return jsonify({"Error": "Missing required parameters: 'region' or 'is_poc'."}), 400

    result = get_pricing(region, is_poc)
    return jsonify(result)

if __name__ == '__main__':
    app.run(port=5006, debug=True)