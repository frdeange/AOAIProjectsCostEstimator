from flask import Flask, render_template, request, send_file, jsonify
import requests
import pandas as pd
import io
import time
import tiktoken

app = Flask(__name__)

# Azure pricing API URL
AZURE_PRICING_API_URL = "https://prices.azure.com/api/retail/prices"

def get_azure_price(service_name, region, sku_name=None, currency="EUR", max_retries=3, timeout=10):
    params = {
        "serviceName": service_name,
        "armRegionName": region,
        "currencyCode": currency
    }
    if sku_name:
        params["skuName"] = sku_name
    retries = 0
    filtered_items = []

    while retries < max_retries:
        try:
            response = requests.get(AZURE_PRICING_API_URL, params=params, timeout=timeout)
            if response.status_code == 200:
                data = response.json()
                # Obtener todos los ítems en lugar de detenerse al primer filtro
                filtered_items = [item for item in data.get("Items", []) if service_name.lower() in item.get("productName", "").lower()]
                
                # Si se encontraron ítems, salir del bucle de reintentos
                if filtered_items:
                    break
            retries += 1
            time.sleep(2)  # Esperar antes de reintentar
        except requests.exceptions.RequestException as e:
            retries += 1
            time.sleep(2)  # Esperar antes de reintentar
            print(f"Error fetching price for {service_name} in {region}: {e}")

    return filtered_items

def get_available_price(service_name, regions, sku_name=None, currency="EUR"):
    for region in regions:
        prices = get_azure_price(service_name, region, sku_name, currency)
        if prices:
            return prices[0], region
    return None, None

@app.route('/', methods=['GET', 'POST'])
def index():
    total_cost = None
    cost_breakdown = []
    if request.method == 'POST':
        try:
            # Get form data
            num_users = int(request.form['num_users'])
            interactions_per_user = int(request.form['interactions_per_user'])
            tokens_per_interaction = int(request.form['tokens_per_interaction'])
            api_management_sku = request.form['api_management_sku']
            num_endpoints = int(request.form['num_endpoints'])
            ai_search_sku = request.form['ai_search_sku']
            regions = [
                request.form['region'],
                "West Europe", "Sweden Central", "Italy North", "Spain Central", "France Central"
            ]
            
            # Services to consider in the architecture
            services = [
                {"name": "Cognitive Services", "label": "Azure OpenAI", "sku": None},
                {"name": "Key Vault", "label": "Azure KeyVault", "sku": None},
                {"name": "App Service", "label": "Azure App Service", "sku": None},
                {"name": "Storage", "label": "Azure Storage/Blob Storage", "sku": None},
                {"name": "API Management", "label": "Azure API Management", "sku": api_management_sku},
                {"name": "Monitor", "label": "Azure Monitor", "sku": None},
                {"name": "Cosmos DB", "label": "Azure CosmosDB", "sku": None},
                {"name": "Private Link", "label": "Azure Private Links", "sku": None, "units": num_endpoints},
                {"name": "Private DNS Zones", "label": "Azure Private DNS Zones", "sku": None, "units": num_endpoints},
                {"name": "Cognitive Search", "label": "Azure AI Search", "sku": ai_search_sku},
                {"name": "Functions", "label": "Azure Functions", "sku": None}
            ]
            
            # Calculate costs for each service
            for service in services:
                sku_name = service.get("sku")
                units = service.get("units", 1)
                price_info, selected_region = get_available_price(service["name"], regions, sku_name)
                if price_info:
                    unit_price = price_info.get("retailPrice", 0)
                    # Calculate tokens only for Azure OpenAI, for other services consider a fixed unit
                    if service["name"] == "Cognitive Services":
                        total_tokens = num_users * interactions_per_user * tokens_per_interaction
                        total_cost_service = (total_tokens / 1000) * unit_price
                        units = total_tokens
                    else:
                        total_cost_service = unit_price * units
                    cost_breakdown.append({
                        "Service": service["label"],
                        "Unit Price (EUR)": unit_price,
                        "Total Units": units,
                        "Total Cost (EUR)": total_cost_service,
                        "Selected Region": selected_region
                    })
                else:
                    # Manejo cuando no se encuentra un precio
                    cost_breakdown.append({
                        "Service": service["label"],
                        "Unit Price (EUR)": None,
                        "Total Units": units,
                        "Total Cost (EUR)": None,
                        "Selected Region": "N/A"
                    })
                    print(f"No price found for {service['name']} with SKU {sku_name} in regions: {regions}")
            
            # Calculate the total estimated cost
            total_cost = sum(item["Total Cost (EUR)"] for item in cost_breakdown if isinstance(item["Total Cost (EUR)"], (int, float)))
        except ValueError:
            total_cost = "Please enter valid values."
    return render_template('index.html', total_cost=total_cost, cost_breakdown=cost_breakdown)

@app.route('/calculate_tokens', methods=['POST'])
def calculate_tokens():
    data = request.get_json()
    text = data.get('text')
    model = data.get('model')

    if not text or not model:
        return jsonify({'error': 'Invalid input'}), 400

    try:
        # Determinar el encoding en función del modelo seleccionado
        if model == 'gpt3.5-gpt4':
            encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
        elif model == 'gpt4o':
            encoding = tiktoken.encoding_for_model("gpt-4o")
        else:
            return jsonify({'error': 'Unsupported model'}), 400

        # Calcular los tokens del texto
        tokens = len(encoding.encode(text))

        return jsonify({'tokens': tokens})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download', methods=['POST'])
def download():
    # Get cost breakdown data from hidden form field
    cost_breakdown = request.form.get('cost_breakdown')
    if cost_breakdown:
        cost_breakdown = eval(cost_breakdown)  # Convert string to list of dictionaries
        df = pd.DataFrame(cost_breakdown)
        # Save to an Excel file in memory
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Cost Breakdown')
        output.seek(0)
        return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', as_attachment=True, download_name='cost_breakdown.xlsx')

if __name__ == '__main__':
    app.run(debug=True)
