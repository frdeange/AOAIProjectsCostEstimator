from flask import Flask, render_template, request, jsonify
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../priceDataExtractor')))
import pricesapi  # Tu módulo para conectar a la API de precios

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/basic-form')
def basic_form():
    return render_template('basic-form.html')

@app.route('/advanced-form')
def advanced_form():
    return render_template('advanced-form.html')

@app.route('/calculate-pricing', methods=['POST'])
def calculate_pricing():
    form_data = request.json
    # Datos recibidos del formulario
    num_users = form_data.get('numUsers')
    num_interactions = form_data.get('numInteractions')
    model = form_data.get('genAIModel')
    preferred_region = form_data.get('preferredRegion')
    num_docs_setup = form_data.get('numDocsSetup')
    num_docs_monthly = form_data.get('numDocsMonthly')

    # Obtén los precios desde la API de Azure
    price_per_thousand_tokens = pricesapi.get_prices(model, preferred_region)
    if price_per_thousand_tokens is None:
        return jsonify({'error': 'Unable to fetch pricing information'}), 500

    # Realiza cálculos (equivalente a lo que haces en Excel)
    total_tokens_setup = num_docs_setup * 35 * 300 * 1.33 if num_docs_setup else 0
    total_tokens_monthly = num_docs_monthly * 35 * 300 * 1.33 if num_docs_monthly else 0
    total_tokens = total_tokens_setup + total_tokens_monthly
    cost = (total_tokens / 1000) * price_per_thousand_tokens

    result = {
        "model": model,
        "region": preferred_region,
        "total_tokens": total_tokens,
        "cost": round(cost, 2)
    }

    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
