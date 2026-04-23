# MCP Server - Merge CRM Integration

A minimal MCP-compatible server using FastAPI to interact with Merge CRM API.

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set environment variables:**
   
   **Windows (Command Prompt):**
   ```cmd
   set MERGE_API_KEY=your_api_key_here
   set ACCOUNT_TOKEN=your_account_token_here
   ```
   
   **Windows (PowerShell):**
   ```powershell
   $env:MERGE_API_KEY="your_api_key_here"
   $env:ACCOUNT_TOKEN="your_account_token_here"
   ```
   
   **Linux/Mac:**
   ```bash
   export MERGE_API_KEY=your_api_key_here
   export ACCOUNT_TOKEN=your_account_token_here
   ```

3. **Run the server:**
   ```bash
   uvicorn main:app --reload
   ```

   The server will start on `http://localhost:8000`

## API Endpoints

### GET /tools
Returns the list of available tools.

**Response:**
```json
{
  "tools": [
    {
      "name": "get_contacts",
      "description": "Fetch contacts from Merge CRM",
      "parameters": {
        "type": "object",
        "properties": {
          "limit": {
            "type": "number",
            "description": "Maximum number of contacts to return"
          }
        }
      }
    }
  ]
}
```

### POST /tools/get_contacts
Fetches contacts from Merge CRM API.

**Request Body:**
```json
{
  "limit": 10
}
```

**Response:**
Returns the JSON response from Merge API containing contacts data.

### GET /
Health check endpoint.

## Testing

You can test the endpoints using curl or any HTTP client:

```bash
# Get tools list
curl http://localhost:8000/tools

# Get contacts (with limit)
curl -X POST http://localhost:8000/tools/get_contacts \
  -H "Content-Type: application/json" \
  -d '{"limit": 10}'
```

Or visit `http://localhost:8000/docs` for interactive API documentation (Swagger UI).
