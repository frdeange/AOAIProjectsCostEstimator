from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

def get_azure_keyvault_pricing(region, is_poc):
    # Call the API to get the JSON data for Azure Key Vault pricing
    response = requests.get('http://localhost:5000/prices/azure_keyvault')
    if response.status_code == 200:
        data = response.json()
    else:
        return {"Error": "Failed to retrieve data from the API."}

    if is_poc:
        # For PoC, no pricing data is required
        return {"Info": "No pricing data required for PoC"}

    # For Project, we need Operations and Advanced Key Operations in Premium
    required_meters = ["Operations", "Advanced Key Operations"]
    premium_results = [
        item for item in data
        if item['armRegionName'].lower() == region.lower() and
        item['meterName'] in required_meters and
        item['skuName'] == "Premium"
    ]

    # Check if any results were found
    if not premium_results:
        return {"Error": "No valid pricing data found for Premium tier in the specified region."}

    # Format and return results
    results = {
        "Total Cost": sum(item['unitPrice'] for item in premium_results),
        "Details": [
            {
                "Meter": item['meterName'],
                "SKU": item['skuId'],
                "Price per Unit": item['unitPrice'],
                "Unit": item['unitOfMeasure']
            } for item in premium_results
        ]
    }
    return results

@app.route('/get_keyvault_pricing', methods=['POST'])
def get_keyvault_pricing_api():
    data = request.get_json()
    region = data.get('region')
    is_poc = data.get('is_poc')

    if not region or is_poc is None:
        return jsonify({"Error": "Missing required parameters: 'region' or 'is_poc'."}), 400

    result = get_azure_keyvault_pricing(region, is_poc)
    return jsonify(result)

if __name__ == '__main__':
    app.run(port=5011, debug=True)
