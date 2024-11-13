from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

def get_azure_functions_pricing(region, memory_size_mb, execution_time_ms, executions_per_month, is_poc):
    # Call the API to get the JSON data for Azure Functions pricing
    response = requests.get('http://localhost:5000/prices/azure_functions')
    if response.status_code == 200:
        data = response.json()
    else:
        return {"Error": "Failed to retrieve data from the API."}

    if is_poc:
        # PoC: Consumption model with free quotas
        tier_filter = "Consumption"
        
        # Filter data for "Consumption" in the specified region
        consumption_results = [
            item for item in data
            if item['armRegionName'].lower() == region.lower() and
            item['type'] == tier_filter and
            item['unitPrice'] > 0
        ]

        # Extract unit prices for "Standard Execution Time" and "Standard Total Executions"
        execution_time_data = next((item for item in consumption_results if item['meterName'] == "Standard Execution Time"), None)
        execution_count_data = next((item for item in consumption_results if item['meterName'] == "Standard Total Executions"), None)

        if not execution_time_data or not execution_count_data:
            return {"Error": "No valid pricing data found for Consumption tier."}

        # Free quotas
        free_gb_seconds = 400000
        free_executions = 1000000

        # Calculate billable GB-seconds and total cost
        total_gb_seconds = (memory_size_mb / 1024) * (execution_time_ms / 1000) * executions_per_month
        billable_gb_seconds = max(0, total_gb_seconds - free_gb_seconds)
        total_execution_time_cost = billable_gb_seconds * execution_time_data['unitPrice']

        # Calculate billable executions and total cost
        billable_executions = max(0, executions_per_month - free_executions)
        total_execution_count_cost = (billable_executions / 10) * execution_count_data['unitPrice']

        # Total cost and PoC-specific details
        total_cost = total_execution_time_cost + total_execution_count_cost
        return {
            "Total Cost (USD)": f"{total_cost:.2f}",
            "Execution Time SKU": execution_time_data['skuId'],
            "Execution Time Description": execution_time_data['meterName'],
            "Execution Time Price": execution_time_data['unitPrice'],
            "Execution Time Unit": execution_time_data['unitOfMeasure'],
            "Execution Count SKU": execution_count_data['skuId'],
            "Execution Count Description": execution_count_data['meterName'],
            "Execution Count Price": execution_count_data['unitPrice'],
            "Execution Count Unit": execution_count_data['unitOfMeasure']
        }

    else:
        # Project: Premium model
        tier_filter = "Premium"
        
        # Filter data for "Premium" in the specified region
        premium_results = [
            item for item in data
            if item['armRegionName'].lower() == region.lower() and
            item['type'] == tier_filter and
            item['unitPrice'] > 0
        ]

        # Extract unit price for "EP1" (one instance)
        instance_data = next((item for item in premium_results if item['skuName'] == "EP1"), None)

        if not instance_data:
            return {"Error": "No valid pricing data found for Premium tier."}

        # Calculate the total cost for instance usage in hours (assuming 1 instance and 730 hours per month)
        instances = 1
        hours_per_month = 730
        total_cost = instances * hours_per_month * instance_data['unitPrice']

        # Project-specific details
        return {
            "Total Cost (USD)": f"{total_cost:.2f}",
            "Instance SKU": instance_data['skuId'],
            "Instance Description": instance_data['meterName'],
            "Instance Price": instance_data['unitPrice'],
            "Instance Unit": instance_data['unitOfMeasure']
        }

@app.route('/get_azure_functions_pricing', methods=['POST'])
def get_azure_functions_pricing_api():
    data = request.get_json()
    region = data.get('region')
    memory_size_mb = data.get('memory_size_mb')
    execution_time_ms = data.get('execution_time_ms')
    executions_per_month = data.get('executions_per_month')
    is_poc = data.get('is_poc')

    if not all([region, memory_size_mb, execution_time_ms, executions_per_month]) or is_poc is None:
        return jsonify({"Error": "Missing required parameters."}), 400

    result = get_azure_functions_pricing(region, memory_size_mb, execution_time_ms, executions_per_month, is_poc)
    return jsonify(result)

if __name__ == '__main__':
    app.run(port=5008, debug=True)