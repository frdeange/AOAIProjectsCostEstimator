from flask import Flask, jsonify, request
import os
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
from dotenv import load_dotenv
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS
import logging

# Load environment variables from .env file
load_dotenv()

# CosmosDB connection configuration
COSMOSDB_URI = os.getenv("AZURE_COSMOSDB_URI", "YOUR_COSMOSDB_URI")
COSMOSDB_KEY = os.getenv("AZURE_COSMOSDB_KEY", "YOUR_COSMOSDB_KEY")
COSMOSDB_DATABASE = os.getenv("AZURE_COSMOSDB_DATABASE", "AzurePricesDB")
COSMOSDB_CONTAINER = os.getenv("AZURE_COSMOSDB_CONTAINER", "Prices")
IS_LOCAL = os.getenv("ENVIROMENT") == "local"

# Initialize CosmosDB client If running locally, use the local CosmosDB Emulator
if IS_LOCAL:
    client = cosmos_client.CosmosClient(
        url="https://cosmosdb:8081",
        credential=(
            "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGG"
            "yPMbIZnqyMsEcaGQy67XIw/Jw=="
        ),
        connection_verify=False
    )
else:
    # Initialize CosmosDB client if running in Azure
    client = cosmos_client.CosmosClient(COSMOSDB_URI, {'masterKey': COSMOSDB_KEY})

# Flask API setup
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Swagger UI setup
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

# Define a function to get a specific service's pricing with optional region filter
def get_service_pricing(service_name, region=None):
    try:
        # Get reference to the container
        database = client.get_database_client(COSMOSDB_DATABASE)
        container = database.get_container_client(COSMOSDB_CONTAINER)

        # Base query to get specific service document
        query = f"SELECT * FROM c WHERE c.serviceName = '{service_name}'"

        logging.debug(f"Executing query: {query}")
        # Execute the query
        documents = list(container.query_items(
            query=query,
            enable_cross_partition_query=True
        ))

        if not documents:
            logging.warning(f"No documents found for service: {service_name}")
            return {"error": f"No data found for service: {service_name}"}, 404

        # Assuming there is only one document per service
        service_data = documents[0]["data"]["Items"]

        # Apply region filter if provided
        if region:
            service_data = [
                item for item in service_data
                if item.get("armRegionName", "").lower() == region.lower()
            ]

        return service_data

    except exceptions.CosmosHttpResponseError as e:
        logging.error(f"CosmosDB error: {e}")
        return {"error": str(e)}, 500

# Endpoint to get all prices
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
        
        logging.debug(f"Executing query: {query}")
        # Execute the query to get all documents
        documents = list(container.query_items(
            query=query,
            enable_cross_partition_query=True
        ))

        if not documents:
            logging.warning("No documents found in the container.")

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

        logging.debug(f"Filtered items: {filtered_items}")
        return jsonify(filtered_items)

    except exceptions.CosmosHttpResponseError as e:
        logging.error(f"CosmosDB error: {e}")
        return jsonify({"error": str(e)}), 500

# Endpoint for each Azure service with optional region filter
@app.route('/prices/api_management', methods=['GET'])
def get_api_management_prices():
    region = request.args.get('region')
    return jsonify(get_service_pricing("api_management", region))

@app.route('/prices/azure_ai_search', methods=['GET'])
def get_azure_ai_search_prices():
    region = request.args.get('region')
    return jsonify(get_service_pricing("azure_ai_search", region))

@app.route('/prices/azure_app_service', methods=['GET'])
def get_azure_app_service_prices():
    region = request.args.get('region')
    return jsonify(get_service_pricing("azure_app_service", region))

@app.route('/prices/azure_cosmosdb', methods=['GET'])
def get_azure_cosmosdb_prices():
    region = request.args.get('region')
    return jsonify(get_service_pricing("azure_cosmosdb", region))

@app.route('/prices/azure_dns', methods=['GET'])
def get_azure_dns_prices():
    region = request.args.get('region')
    return jsonify(get_service_pricing("azure_dns", region))

@app.route('/prices/azure_document_intelligence', methods=['GET'])
def get_azure_document_intelligence_prices():
    region = request.args.get('region')
    return jsonify(get_service_pricing("azure_document_intelligence", region))

@app.route('/prices/azure_functions', methods=['GET'])
def get_azure_functions_prices():
    region = request.args.get('region')
    return jsonify(get_service_pricing("azure_functions", region))

@app.route('/prices/azure_keyvault', methods=['GET'])
def get_azure_keyvault_prices():
    region = request.args.get('region')
    return jsonify(get_service_pricing("azure_keyvault", region))

@app.route('/prices/azure_monitor', methods=['GET'])
def get_azure_monitor_prices():
    region = request.args.get('region')
    return jsonify(get_service_pricing("azure_monitor", region))

@app.route('/prices/azure_openai', methods=['GET'])
def get_azure_openai_prices():
    region = request.args.get('region')
    return jsonify(get_service_pricing("azure_openai", region))

@app.route('/prices/blob_storage', methods=['GET'])
def get_blob_storage_prices():
    region = request.args.get('region')
    return jsonify(get_service_pricing("blob_storage", region))

# Endpoint to list all available services
@app.route('/services', methods=['GET'])
def get_services():
    """
    Get a list of all available Azure services
    ---
    responses:
      200:
        description: A list of available services
        schema:
          type: array
          items:
            type: string
    """
    try:
        # Get reference to the container
        database = client.get_database_client(COSMOSDB_DATABASE)
        container = database.get_container_client(COSMOSDB_CONTAINER)
        
        # Query to get all documents
        query = "SELECT DISTINCT VALUE c.serviceName FROM c"
        
        logging.debug(f"Executing query: {query}")
        # Execute the query to get all unique service names
        services = list(container.query_items(
            query=query,
            enable_cross_partition_query=True
        ))

        # Normalize service names to match the format used in /prices
        services = [service.lower() for service in services]

        if not services:
            logging.warning("No services found in the container.")

        logging.debug(f"Services: {services}")
        return jsonify(services)

    except exceptions.CosmosHttpResponseError as e:
        logging.error(f"CosmosDB error: {e}")
        return jsonify({"error": str(e)}), 500

# Endpoint to list all available regions
@app.route('/regions', methods=['GET'])
def get_regions():
    """
    Get a list of all available regions
    ---
    responses:
      200:
        description: A list of available regions
        schema:
          type: array
          items:
            type: string
    """
    try:
        # Get reference to the container
        database = client.get_database_client(COSMOSDB_DATABASE)
        container = database.get_container_client(COSMOSDB_CONTAINER)
        
        # Query to get all documents
        query = "SELECT * FROM c"
        
        logging.debug(f"Executing query: {query}")
        # Execute the query to get all documents
        documents = list(container.query_items(
            query=query,
            enable_cross_partition_query=True
        ))

        if not documents:
            logging.warning("No regions found in the container.")

        # Extract unique regions
        regions = set()
        for doc in documents:
            if "data" in doc and "Items" in doc["data"]:
                for item in doc["data"]["Items"]:
                    regions.add(item.get("armRegionName", "").lower())

        regions_list = list(regions)
        logging.debug(f"Regions: {regions_list}")
        return jsonify(regions_list)

    except exceptions.CosmosHttpResponseError as e:
        logging.error(f"CosmosDB error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Run Flask API
    app.run(debug=True, port=5000)
