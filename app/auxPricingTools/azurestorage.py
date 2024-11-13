from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

def get_blob_storage_pricing(region):
    # Call the API to get the JSON data for Azure Blob Storage pricing
    response = requests.get('http://localhost:5000/prices/blob_storage')
    if response.status_code == 200:
        data = response.json()
    else:
        return {"Error": "Failed to retrieve data from the API."}

    # Define filters for each required metric
    write_operations = next(
        (item for item in data
         if item['armRegionName'].lower() == region.lower() and
         item['meterName'] == "Hot LRS Write Operations" and
         item['skuName'] == "Hot LRS"), 
        None
    )

    read_operations = next(
        (item for item in data
         if item['armRegionName'].lower() == region.lower() and
         item['meterName'] == "Hot Read Operations" and
         item['skuName'] == "Hot LRS"), 
        None
    )

    storage = next(
        (item for item in data
         if item['armRegionName'].lower() == region.lower() and
         item['meterName'] == "Hot LRS Data Stored" and
         item['skuName'] == "Hot LRS"), 
        None
    )

    # Check if all required data is found
    if not write_operations or not read_operations or not storage:
        return {"Error": "Some pricing data for Hot LRS metrics were not found in the specified region."}

    results = {
        "Write Operations": {
            "SKU": write_operations['skuId'],
            "Description": write_operations['meterName'],
            "Price per Unit": write_operations['unitPrice'],
            "Unit": write_operations['unitOfMeasure']
        },
        "Read Operations": {
            "SKU": read_operations['skuId'],
            "Description": read_operations['meterName'],
            "Price per Unit": read_operations['unitPrice'],
            "Unit": read_operations['unitOfMeasure']
        },
        "Storage": {
            "SKU": storage['skuId'],
            "Description": storage['meterName'],
            "Price per Unit": storage['unitPrice'],
            "Unit": storage['unitOfMeasure']
        }
    }
    return results

@app.route('/get_blob_pricing', methods=['POST'])
def get_blob_pricing():
    data = request.get_json()
    region = data.get('region')

    if not region:
        return jsonify({"Error": "Missing required parameter: 'region'."}), 400

    result = get_blob_storage_pricing(region)
    return jsonify(result)

if __name__ == '__main__':
    app.run(port=5002, debug=True)
