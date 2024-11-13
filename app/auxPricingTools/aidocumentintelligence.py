from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

def get_document_intelligence_pricing(region):
    # Llamar a la API para obtener los datos JSON
    response = requests.get('http://localhost:5000/prices/azure_document_intelligence')
    if response.status_code == 200:
        data = response.json()
    else:
        return {"Error": "Failed to retrieve data from the API."}

    # Filtrar los datos para "S0 Read Pages" en la región especificada
    filtered_results = [
        item for item in data
        if item['armRegionName'].lower() == region.lower() and
        item['skuName'] == "S0" and
        item['meterName'] == "S0 Read Pages"
    ]

    # Comprobar si se encontraron resultados y devolver el primero
    if filtered_results:
        return {
            "Price per 1K Pages": filtered_results[0]['unitPrice'],
            "SKU ID": filtered_results[0]['skuId']
        }
    else:
        return {"Error": "No results matching the criteria were found."}

@app.route('/get_document_intelligence_pricing', methods=['POST'])
def get_document_pricing():
    data = request.get_json()
    region = data.get('region')

    if not region:
        return jsonify({"Error": "Missing required parameter: 'region'."}), 400

    result = get_document_intelligence_pricing(region)
    return jsonify(result)

if __name__ == '__main__':
    app.run(port=5003, debug=True)
