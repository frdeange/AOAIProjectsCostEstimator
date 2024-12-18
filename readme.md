# Azure Prices Estimator

Welcome to the **Azure Prices Estimator** project! This application helps to extract, process, and display Azure pricing information in an efficient way. It uses Azure's retail pricing API to gather information, stores data in Azure CosmosDB, and provides an API for quick and easy access to the pricing details.

## Features

- **Data Extraction from Azure Pricing API**: Extracts data from Azure retail pricing API for multiple services like Azure Cosmos DB, Azure Cognitive Services, Azure AI Search, etc.
- **Combined Data Storage**: Stores extracted pricing data in CosmosDB, ensuring efficient and quick retrieval without the need to repeatedly call the Azure Pricing API.
- **REST API Access**: Provides a REST API for querying Azure service prices. The API supports filters to query based on `serviceName` and `region`.
- **Swagger UI for API Documentation**: The application comes with a Swagger UI that provides an interactive interface to explore the available API endpoints.
- **Daily Data Upload**: Extracts and uploads data to CosmosDB on a daily basis, ensuring that the information is always up-to-date.

## Getting Started

### Prerequisites

- **Python 3.8+**
- **Azure CosmosDB** account
- **Azure Pricing API Access**
- **Git**
- **Virtual Environment (optional)**: Recommended to keep dependencies isolated.

### Installation

1. **Clone the repository**:

   ```sh
   git clone https://github.com/yourusername/azure-prices-estimator.git
   cd azure-prices-estimator
   ```

2. **Create a virtual environment** (optional but recommended):

   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies**:

   ```sh
   pip install -r requirements.txt
   ```

### Configuration

1. **.env File**:

   Create a `.env` file in the root directory with the following content:

   ```env
   AZURE_COSMOSDB_URI=https://your-cosmosdb-account.documents.azure.com:443/
   AZURE_COSMOSDB_KEY=your_cosmosdb_key
   AZURE_COSMOSDB_DATABASE=AzurePricesDB
   AZURE_COSMOSDB_CONTAINER=Prices
   ```

2. **Endpoints Configuration**:

   The endpoints for Azure services are stored in a file named `endpoints.txt` located in the `priceDataExtractor` directory. You can add or modify endpoints as required.

### Running the Application

1. **Extract and Upload Data to CosmosDB**:

   To extract the pricing data from Azure Pricing API and upload it to CosmosDB, run the following command:

   ```sh
   python priceDataExtractor/uploadtocosmos.py
   ```

   This will extract data for all the services specified in the `endpoints.txt` file and upload them to CosmosDB.

2. **Run the Flask API**:

   To start the REST API server:

   ```sh
   python pricesapi.py
   ```

   The API will be available at `http://localhost:5000`.

3. **Access Swagger UI**:

   You can access the Swagger UI documentation at `http://localhost:5000/swagger` to explore and interact with the available endpoints.

### Usage

- **Get All Prices**:
  
  Endpoint: `GET /prices`
  
  This returns all the pricing data available in CosmosDB.

- **Filter by Service Name**:

  Endpoint: `GET /prices?serviceName=<service_name>`

  Example: `GET /prices?serviceName=Azure Cosmos DB`

- **Filter by Region**:

  Endpoint: `GET /prices?region=<region_name>`

  Example: `GET /prices?region=westeurope`

- **Combined Filters**:

  Endpoint: `GET /prices?serviceName=<service_name>&region=<region_name>`

## Project Structure

- **priceDataExtractor/**: Contains scripts to extract data from Azure Pricing API.
  - `pricesextractor.py`: Extracts data from Azure Pricing API.
  - `uploadtocosmos.py`: Uploads the extracted data to Azure CosmosDB.
  - `endpoints.txt`: Contains the list of endpoints for different Azure services.
- **static/**: Contains the Swagger JSON file for API documentation.
- **pricesapi.py**: The Flask API that provides the pricing information.
- **requirements.txt**: Lists all the dependencies required for the project.

## Dependencies

- **Flask**: Web framework for creating the API.
- **Azure Cosmos**: Python SDK for interacting with CosmosDB.
- **Python Dotenv**: Loads environment variables from a `.env` file.
- **Flask Swagger UI**: Provides an interactive Swagger interface for the API.

## Future Enhancements

- **Authentication**: Add API key or OAuth-based authentication for the endpoints.
- **Scheduled Extraction**: Automate the daily extraction and upload process using a job scheduler like `cron` or Azure Functions.
- **Improved Query Performance**: Add indexing to CosmosDB for frequently queried fields to enhance performance.

## Contributing

Feel free to open issues or submit pull requests if you have suggestions or improvements.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

