from flask import Flask, jsonify, request
import os
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
from dotenv import load_dotenv
from flask_swagger_ui import get_swaggerui_blueprint

# Load environment variables from .env file
load_dotenv()

# CosmosDB connection configuration
COSMOSDB_URI = os.getenv("AZURE_COSMOSDB_URI", "YOUR_COSMOSDB_URI")
COSMOSDB_KEY = os.getenv("AZURE_COSMOSDB_KEY", "YOUR_COSMOSDB_KEY")
COSMOSDB_DATABASE = os.getenv("AZURE_COSMOSDB_DATABASE", "AzurePricesDB")
COSMOSDB_CONTAINER = os.getenv("AZURE_COSMOSDB_CONTAINER", "Prices")

# Initialize CosmosDB client
client = cosmos_client.CosmosClient(COSMOSDB_URI, {'masterKey': COSMOSDB_KEY})

# Flask API setup
app = Flask(__name__)

### Swagger UI setup ###
SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Azure Prices API"
    }
)
app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)

@app.route('/prices', methods=['GET'])
def get_prices():
    """
    Get Azure prices
    ---
    parameters:
      - name: serviceName
        in: query
        type: string
        required: false
        description: The name of the Azure service to filter by.
      - name: region
        in: query
        type: string
        required: false
        description: The region to filter by.
    responses:
      200:
        description: A list of prices
        schema:
          type: array
          items:
            type: object
    """
    try:
        # Get query parameters
        service_name = request.args.get('serviceName')
        region = request.args.get('region')
        
        # Get reference to the container
        database = client.get_database_client(COSMOSDB_DATABASE)
        container = database.get_container_client(COSMOSDB_CONTAINER)
        
        # Query to get all documents
        query = "SELECT * FROM c"
        
        # Execute the query to get all documents
        documents = list(container.query_items(
            query=query,
            enable_cross_partition_query=True
        ))

        # Filter results based on parameters
        filtered_items = []
        for doc in documents:
            if "data" in doc and "Items" in doc["data"]:
                for item in doc["data"]["Items"]:
                    # Apply filters if provided
                    if service_name and service_name.lower() != item.get("serviceName", "").lower():
                        continue
                    if region and region.lower() != item.get("armRegionName", "").lower():
                        continue
                    filtered_items.append(item)

        return jsonify(filtered_items)

    except exceptions.CosmosHttpResponseError as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # Run Flask API
    app.run(debug=True, port=5000)
