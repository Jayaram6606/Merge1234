import os
from fastapi import FastAPI, HTTPException, Request
import requests
from typing import Dict, Any

app = FastAPI(title="Google Drive MCP Server")

# Environment variable
MERGE_API_KEY = os.getenv("MERGE_API_KEY")
ACCOUNT_TOKEN = os.getenv("ACCOUNT_TOKEN")

# 🔹 Dynamic tool configuration
TOOLS_CONFIG = {
    "list_files": {
        "description": "List files from Google Drive via Merge",
        "input_schema": {
            "type": "object",
            "properties": {
                "pageSize": {
                    "type": "integer",
                    "description": "Maximum number of files to return"
                }
            }
        },
        "method": "GET",
        "url": "https://api.merge.dev/api/filestorage/v1/files",
        "param_mapping": {"pageSize": "page_size"}
    },
    "get_file": {
        "description": "Get file metadata via Merge",
        "input_schema": {
            "type": "object",
            "properties": {
                "fileId": {
                    "type": "string",
                    "description": "The ID of the file"
                }
            },
            "required": ["fileId"]
        },
        "method": "GET",
        "url": "https://api.merge.dev/api/filestorage/v1/files",
        "param_mapping": {"fileId": "remote_id"}
    }
}


def generate_tool_definitions():
    """Dynamically generate MCP tool definitions from TOOLS_CONFIG"""
    tools = []
    for tool_name, config in TOOLS_CONFIG.items():
        tools.append({
            "name": tool_name,
            "description": config["description"],
            "input_schema": config["input_schema"]
        })
    return tools


# 🔹 Root endpoint
@app.get("/")
def root():
    return {
        "tools": generate_tool_definitions()
    }


# 🔹 Tool discovery endpoint
@app.get("/tools")
def list_tools():
    return generate_tool_definitions()


# 🔹 Health check
@app.get("/health")
def health():
    return {"status": "ok"}


# 🔹 Dynamic tool execution
@app.post("/tool/{tool_name}")
async def execute_tool(tool_name: str, request: Request):
    """Execute a tool dynamically based on tool_name"""
    
    # Check if tool exists
    if tool_name not in TOOLS_CONFIG:
        raise HTTPException(
            status_code=404,
            detail=f"Tool '{tool_name}' not found. Available tools: {list(TOOLS_CONFIG.keys())}"
        )
    
    # Validate access token
    if not MERGE_API_KEY or not ACCOUNT_TOKEN:
        raise HTTPException(
            status_code=500,
            detail="Missing MERGE_API_KEY or ACCOUNT_TOKEN environment variable"
        )
    
    # Get tool configuration
    tool_config = TOOLS_CONFIG[tool_name]
    
    # Parse request body
    try:
        body = await request.json()
    except Exception:
        body = {}
    
    # Prepare headers
    headers = {
        "Authorization": f"Bearer {MERGE_API_KEY}",
        "X-Account-Token": ACCOUNT_TOKEN,
        "Content-Type": "application/json"
    }
    
    # Build URL with path parameters
    url = tool_config["url"]
    if "path_params" in tool_config:
        for param in tool_config["path_params"]:
            if param not in body:
                raise HTTPException(
                    status_code=400,
                    detail=f"Missing required parameter: {param}"
                )
            url = url.replace(f"{{{param}}}", body[param])
    
    # Build query parameters
    params = {}
    if "param_mapping" in tool_config:
        for param_name, api_param in tool_config["param_mapping"].items():
            if param_name in body:
                params[api_param] = body[param_name]
    
    # Build request body
    request_body = None
    if "body_params" in tool_config:
        request_body = {}
        for param in tool_config["body_params"]:
            if param in body:
                request_body[param] = body[param]
    
    # Execute API call
    try:
        method = tool_config["method"]
        
        if method == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=request_body)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            raise HTTPException(status_code=500, detail=f"Unsupported method: {method}")
        
        # Handle response
        if response.status_code == 204:  # No content (e.g., successful delete)
            return {"content": {"success": True, "message": f"{tool_name} executed successfully"}}
        
        response.raise_for_status()
        
        # Parse and format response for LLM
        data = response.json()
        
        # Format based on tool type
        if tool_name == "list_files":
            files = data.get("results", [])
            formatted_files = [
                {
                    "name": f.get("name", "Unknown"),
                    "type": f.get("mime_type", "Unknown"),
                    "url": f.get("file_url", "")
                }
                for f in files
            ]
            return {"content": formatted_files}
        
        elif tool_name == "get_file":
            # Return formatted single file metadata
            return {
                "content": {
                    "name": data.get("name", "Unknown"),
                    "type": data.get("mime_type", "Unknown"),
                    "url": data.get("file_url", ""),
                    "size": data.get("size", 0)
                }
            }
        
        else:
            # Default: wrap in content
            return {"content": data.get("results", data)}
    
    except requests.exceptions.HTTPError as e:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Google Drive API error: {response.text}"
        )
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to execute {tool_name}: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)