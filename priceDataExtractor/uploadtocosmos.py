from datetime import datetime
import os
import json
import urllib3
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
from azure.cosmos import PartitionKey
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


# Ruta al certificado descargado del emulador CosmosDB
cert_path = "cosmos_emulator_cert.pem"

# CosmosDB connection configuration
COSMOSDB_URI = os.getenv("AZURE_COSMOSDB_URI", "YOUR_COSMOSDB_URI")
COSMOSDB_KEY = os.getenv("AZURE_COSMOSDB_KEY", "YOUR_COSMOSDB_KEY")
COSMOSDB_DATABASE = os.getenv("AZURE_COSMOSDB_DATABASE", "AzurePricesDB")
COSMOSDB_CONTAINER = os.getenv("AZURE_COSMOSDB_CONTAINER", "Prices")
IS_LOCAL = os.getenv("ENVIROMENT") == "local"

if IS_LOCAL:
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
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

# Paths
DATA_DIR = "./priceDataExtractor/azure_prices_data"

# Create database and container if they do not exist
def setup_cosmosdb():
    try:
        database = client.create_database_if_not_exists(id=COSMOSDB_DATABASE)
        container = database.create_container_if_not_exists(
            id=COSMOSDB_CONTAINER,
            partition_key=PartitionKey(path="/serviceName")
        )
        print("CosmosDB setup complete.")
    except exceptions.CosmosHttpResponseError as e:
        print(f"Error setting up CosmosDB: {e}")

# Upload JSON files from the directory to CosmosDB
def upload_data_to_cosmosdb():
    try:
        # Get reference to the container
        database = client.get_database_client(COSMOSDB_DATABASE)
        container = database.get_container_client(COSMOSDB_CONTAINER)

        # Get the current date to use as an identifier
        current_date = datetime.now().strftime("%Y-%m-%d")

        # Iterate over each JSON file in the directory
        for filename in os.listdir(DATA_DIR):
            if filename.endswith(".json"):
                filepath = os.path.join(DATA_DIR, filename)

                # Extract service name from filename (e.g., "azure_app_service.json" -> "azure_app_service")
                service_name = filename.replace(".json", "")

                # Check if a document with the same service name and current date already exists
                query = f"SELECT * FROM c WHERE c.serviceName = '{service_name}' AND c.date = '{current_date}'"
                items = list(container.query_items(query=query, enable_cross_partition_query=True))
                if items:
                    print(f"Document for service '{service_name}' with date '{current_date}' already exists. Skipping upload.")
                    continue

                # Load the JSON data from the file
                with open(filepath, "r") as json_file:
                    service_data = json.load(json_file)

                # Create the document to upload
                document_id = f"{service_name}"
                document = {
                    "id": document_id,
                    "serviceName": service_name,
                    "date": current_date,
                    "data": service_data  # Store all items related to this serviceName
                }

                # Insert or update the document in CosmosDB
                print(f"Inserting or updating document for service: {service_name}")
                container.upsert_item(document)

        print("Data uploaded to CosmosDB successfully.")
    except FileNotFoundError:
        print(f"JSON file not found in directory {DATA_DIR}")
    except exceptions.CosmosHttpResponseError as e:
        print(f"Error uploading data to CosmosDB: {e}")

if __name__ == "__main__":
    # Setup CosmosDB
    setup_cosmosdb()
    # Upload data to CosmosDB
    upload_data_to_cosmosdb()
