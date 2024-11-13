from flask import Flask, request, jsonify
import requests
import re

app = Flask(__name__)

def normalize_text(text):
    """Normalize text by removing spaces, dashes, dots, and converting to lowercase."""
    return re.sub(r'[\s\-.]', '', text.lower())

def get_openai_pricing(region, usage_type, model, modality=None):
    # Call the API to get the JSON data for Azure OpenAI pricing
    response = requests.get('http://localhost:5000/prices/azure_openai')
    if response.status_code == 200:
        data = response.json()
    else:
        return {"Error": "Failed to retrieve data from the API."}

    # Base and specific keywords for models
    base_models = {
        "gpt-3.5": "gpt35",
        "gpt-4": "gpt4",
        "gpt-4o": "gpt4o",
        "gpt-o1": "gpto"
    }
    specific_versions = {
        "gpt-3.5": "1106",
        "gpt-4": "turbo128k",
        "gpt-4o": "0806",
        "gpt-o1": "o1"
    }
    
    # Obtain keywords for base model and specific version
    base_model_keyword = base_models.get(model.lower())
    specific_version_keyword = specific_versions.get(model.lower())

    if not base_model_keyword or not specific_version_keyword:
        return {"Error": f"Model '{model}' is not supported for {usage_type}."}

    # Identifiers for input, output, global, regional, and batch
    input_identifiers = ["inp", "input"]
    output_identifiers = ["outp", "output"]
    global_identifiers = ["glbl", "global"]
    regional_identifiers = ["rgnl", "regional"]
    batch_identifier = "batch"  # Avoid items with 'batch' in the name

    # Store pricing details for input and output
    pricing_details = {"input": None, "output": None}

    for item in data:
        # Check region
        if item.get("armRegionName").lower() != region.lower():
            continue

        # Normalize SKU and meter names
        sku_name = normalize_text(item.get("armSkuName", ""))
        meter_name = normalize_text(item.get("meterName", ""))

        # First Level Filter: Check base model keyword
        if base_model_keyword not in sku_name:
            continue

        # Second Level Filter: Check for specific version keyword
        if specific_version_keyword not in sku_name:
            continue

        # Exclude items with 'batch' in the SKU or meter name
        if batch_identifier in sku_name or batch_identifier in meter_name:
            continue

        # Modality check if required
        if usage_type == "completions" and modality:
            if modality.lower() == "global" and not any(identifier in sku_name for identifier in global_identifiers):
                continue
            if modality.lower() == "regional" and not any(identifier in sku_name for identifier in regional_identifiers):
                continue

        # Determine input/output based on meter name, allowing for multiple identifiers
        if any(identifier in meter_name for identifier in input_identifiers) and pricing_details["input"] is None:
            pricing_details["input"] = {
                "Token Type": "input",
                "SKU ID": item.get("skuId"),
                "Description": item.get("meterName"),
                "Price per Unit": item.get("unitPrice"),
                "Unit of Measure": item.get("unitOfMeasure")
            }
        elif any(identifier in meter_name for identifier in output_identifiers) and pricing_details["output"] is None:
            pricing_details["output"] = {
                "Token Type": "output",
                "SKU ID": item.get("skuId"),
                "Description": item.get("meterName"),
                "Price per Unit": item.get("unitPrice"),
                "Unit of Measure": item.get("unitOfMeasure")
            }

        # Stop if both input and output details are found
        if pricing_details["input"] and pricing_details["output"]:
            break

    # Final output check
    if not pricing_details["input"] and not pricing_details["output"]:
        return {"Error": "No valid pricing data found for the specified parameters."}

    # Filter out any None values from the final results
    final_pricing_details = {k: v for k, v in pricing_details.items() if v is not None}
    return {
        "Region": region,
        "Model": model,
        "Usage Type": usage_type,
        "Modality": modality if modality else "N/A",
        "Pricing Details": final_pricing_details
    }

@app.route('/get_pricing', methods=['POST'])
def get_pricing():
    data = request.get_json()
    region = data.get('region')
    usage_type = data.get('usage_type')
    model = data.get('model')
    modality = data.get('modality')

    if not region or not usage_type or not model:
        return jsonify({"Error": "Missing required parameters: 'region', 'usage_type', or 'model'."}), 400

    result = get_openai_pricing(region, usage_type, model, modality)
    return jsonify(result)

if __name__ == '__main__':
    app.run(port=5001, debug=True)
