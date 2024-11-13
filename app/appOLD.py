from flask import Flask, render_template, request, send_file, jsonify
import requests
import pandas as pd
import io
import time
import tiktoken

app = Flask(__name__)

# Route for the home page
@app.route('/')
def home():
    return render_template('index.html')

# Route for the basic form
@app.route('/basic-form')
def basic_form():
    return render_template('basic_form.html')

# Route for the advanced form
@app.route('/advanced-form')
def advanced_form():
    return render_template('advanced_form.html', total_cost=None, cost_breakdown=[])

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
    app.run(debug=True, port=5001)
