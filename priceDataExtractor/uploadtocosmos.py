from datetime import datetime
import os
import json
from azure.cosmos import CosmosClient, PartitionKey, exceptions
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# CosmosDB connection configuration
COSMOSDB_URI = os.getenv("AZURE_COSMOSDB_URI", "YOUR_COSMOSDB_URI")
COSMOSDB_KEY = os.getenv("AZURE_COSMOSDB_KEY", "YOUR_COSMOSDB_KEY")
COSMOSDB_DATABASE = os.getenv("AZURE_COSMOSDB_DATABASE", "AzurePricesDB")
COSMOSDB_CONTAINER = os.getenv("AZURE_COSMOSDB_CONTAINER", "Prices")

# Initialize CosmosDB client
client = CosmosClient(COSMOSDB_URI, credential=COSMOSDB_KEY)

# Paths
DATA_DIR = "priceDataExtractor/azure_prices_data"

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

                # Load the JSON data from the file
                with open(filepath, "r") as json_file:
                    service_data = json.load(json_file)

                # Create the document to upload
                document_id = f"{service_name}_{current_date}"
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
