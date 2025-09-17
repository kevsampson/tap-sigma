tap-sigma-computing
A Singer tap for extracting data from the Sigma Computing API. Built to work with Meltano.

Features
Extracts data from multiple Sigma Computing endpoints
Supports incremental extraction using bookmarks
Handles OAuth 2.0 client credentials authentication
Respects API rate limits
Full catalog discovery with schema inference
Supported Streams
Stream	Endpoint	Replication Method	Primary Key
workbooks	/v2/workbooks	INCREMENTAL	workbookId
users	/v2/members	INCREMENTAL	memberId
teams	/v2/teams	INCREMENTAL	teamId
connections	/v2/connections	INCREMENTAL	connectionId
datasets	/v2/datasets	INCREMENTAL	datasetId
folders	/v2/folders	INCREMENTAL	folderId
user_attributes	/v2/user-attributes	INCREMENTAL	attributeId
Prerequisites
A Sigma Computing account with API access
API credentials (Client ID and Client Secret)
Python 3.8+
Meltano (recommended) or Singer ecosystem tools
Quick Start with Meltano
1. Install Meltano
bash
pip install meltano
2. Initialize Meltano Project
bash
meltano init my_sigma_project
cd my_sigma_project
3. Add the Tap
bash
# Clone this repository or copy the tap files to your project
# Then add it as a custom extractor
meltano add --custom extractor tap-sigma-computing
4. Configure the Tap
bash
# Set your Sigma Computing API credentials
meltano config tap-sigma-computing set client_id "your_client_id"
meltano config tap-sigma-computing set client_secret "your_client_secret"
meltano config tap-sigma-computing set base_url "https://your-region-api.sigmacomputing.com"
5. Test the Connection
bash
meltano invoke tap-sigma-computing --discover
6. Run a Test Extraction
bash
meltano run tap-sigma-computing target-jsonl
Sigma Computing API Setup
1. Generate API Credentials
Log in to your Sigma Computing account
Go to Administration > Developer Access
Click Create Client Credentials
Copy the Client ID and Client Secret
Note your API Base URL from the same page
2. Determine Your Base URL
Your base URL depends on where your Sigma organization is hosted:

Provider	Base URL
AWS-US (West)	https://aws-api.sigmacomputing.com
AWS-US (East)	https://api.us-a.aws.sigmacomputing.com
AWS-CA	https://api.ca.aws.sigmacomputing.com
AWS-EU	https://api.eu.aws.sigmacomputing.com
AWS-UK	https://api.uk.aws.sigmacomputing.com
AWS-AU	https://api.au.aws.sigmacomputing.com
Azure-US	https://api.us.azure.sigmacomputing.com
Azure-EU	https://api.eu.azure.sigmacomputing.com
Azure-CA	https://api.ca.azure.sigmacomputing.com
Azure-UK	https://api.uk.azure.sigmacomputing.com
GCP	https://api.sigmacomputing.com
Configuration
Required Settings
client_id: Your Sigma Computing API Client ID
client_secret: Your Sigma Computing API Client Secret
base_url: Your Sigma Computing API base URL (see table above)
Optional Settings
The tap uses sensible defaults for:

Rate limiting (respects the 1 req/sec limit on token endpoint)
Pagination (50 records per page, max 1000)
Token refresh (automatically handles expired tokens)
Installation for Development
1. Clone the Repository
bash
git clone https://github.com/yourusername/tap-sigma-computing.git
cd tap-sigma-computing
2. Create a Virtual Environment
bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
3. Install Dependencies
bash
pip install -e .
4. Run Tests
bash
pytest tests/
Usage Examples
Discovery
bash
tap-sigma-computing --config config.json --discover > catalog.json
Full Sync
bash
tap-sigma-computing --config config.json --catalog catalog.json
Incremental Sync with State
bash
tap-sigma-computing --config config.json --catalog catalog.json --state state.json
Example Config File
json
{
  "client_id": "your_client_id_here",
  "client_secret": "your_client_secret_here", 
  "base_url": "https://aws-api.sigmacomputing.com"
}
Example Catalog (Select Specific Streams)
json
{
  "streams": [
    {
      "tap_stream_id": "workbooks",
      "stream": "workbooks", 
      "schema": {...},
      "metadata": [
        {
          "breadcrumb": [],
          "metadata": {
            "selected": true,
            "replication-method": "INCREMENTAL"
          }
        }
      ]
    },
    {
      "tap_stream_id": "users",
      "stream": "users",
      "schema": {...},
      "metadata": [
        {
          "breadcrumb": [],
          "metadata": {
            "selected": true,
            "replication-method": "INCREMENTAL" 
          }
        }
      ]
    }
  ]
}
Data Output
The tap outputs data in Singer format with three types of messages:

SCHEMA Messages
Define the structure of each stream.

RECORD Messages
Contain the actual data records.

STATE Messages
Track incremental extraction progress.

Example record:

json
{
  "type": "RECORD",
  "stream": "workbooks",
  "record": {
    "workbookId": "wb_abc123",
    "name": "Sales Dashboard",
    "createdAt": "2024-01-15T10:30:00Z",
    "updatedAt": "2024-01-20T14:45:00Z",
    "ownerId": "user_xyz789",
    "folderId": "folder_def456"
  },
  "time_extracted": "2024-01-21T09:00:00Z"
}
Rate Limiting
The tap automatically handles Sigma Computing's rate limits:

Token endpoint: Limited to 1 request per second
General API: Uses conservative 0.1 second delays between requests
Automatic retries: On 401 responses (token expiry)
Error Handling
The tap includes comprehensive error handling for:

Authentication failures
Network timeouts
API rate limit responses
Malformed API responses
Token expiration and refresh
Troubleshooting
Common Issues
401 Unauthorized Error

Check that your client_id and client_secret are correct
Verify your base_url matches your Sigma organization's region
Ensure your API credentials have the necessary permissions
Rate Limit Errors

The tap automatically handles rate limiting, but if you see persistent errors, try reducing concurrent requests
Connection Timeouts

Check your network connection to Sigma Computing
Verify the base_url is reachable from your environment
Empty Results

Verify you have data in your Sigma organization for the streams you're extracting
Check that your API credentials have read access to the resources
Debug Mode
For verbose logging, set the environment variable:

bash
export SINGER_LOG_LEVEL=DEBUG
tap-sigma-computing --config config.json --discover
Contributing
Fork the repository
Create a feature branch (git checkout -b feature/amazing-feature)
Make your changes
Add tests for new functionality
Commit your changes (git commit -m 'Add amazing feature')
Push to the branch (git push origin feature/amazing-feature)
Open a Pull Request
Testing
Run the test suite:

bash
pytest tests/
For integration tests with a real Sigma Computing instance:

bash
export SIGMA_CLIENT_ID="your_test_client_id"
export SIGMA_CLIENT_SECRET="your_test_client_secret"  
export SIGMA_BASE_URL="your_test_base_url"
pytest tests/integration/
License
This project is licensed under the Apache License 2.0 - see the LICENSE file for details.

Support
Create an issue in this repository for bugs or feature requests
Check the Sigma Computing API documentation for API-specific questions
Visit the Meltano documentation for general ETL pipeline help
Changelog
v0.1.0 (2024-01-21)
Initial release
Support for 7 core Sigma Computing streams
Incremental replication with bookmarks
OAuth 2.0 client credentials authentication
Rate limiting and error handling
Meltano integration
