from fastapi import FastAPI, Request

app = FastAPI()

# 🔹 Tool discovery
@app.get("/tools")
def list_tools():
    return {
        "tools": [
            {
                "name": "get_files",
                "description": "Fetch files (dummy data)",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "page_size": {
                            "type": "integer",
                            "description": "Number of files to return"
                        }
                    }
                }
            }
        ]
    }

# 🔹 Root endpoint (improved)
@app.get("/")
def root():
    return {
        "name": "custom-mcp-server",
        "version": "1.0",
        "tools": list_tools()["tools"]
    }

# 🔹 Health endpoint
@app.get("/health")
def health():
    return {"status": "ok"}

# 🔹 Tool execution
@app.post("/tools/get_files")
async def get_files(request: Request):
    body = await request.json()
    page_size = body.get("page_size", 5)

    files = [
        {"name": "report.pdf", "size": "2MB"},
        {"name": "notes.txt", "size": "5KB"},
        {"name": "image.png", "size": "1MB"},
        {"name": "data.csv", "size": "500KB"},
        {"name": "presentation.pptx", "size": "3MB"}
    ]

    return {"files": files[:page_size]}