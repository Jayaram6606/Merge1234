from fastapi import FastAPI, Request

app = FastAPI()

# 🔹 Tool discovery
@app.get("/tools")
def list_tools():
    return {
        "tools": [
            {
                "name": "get_files",
                "description": "Fetch files (dummy data for testing)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "page_size": {"type": "number"}
                    }
                }
            }
        ]
    }

# 🔹 Tool execution
@app.post("/tools/get_files")
async def get_files(request: Request):
    body = await request.json()
    page_size = body.get("page_size", 5)

    # ✅ Dummy data
    files = [
        {"name": "report.pdf", "size": "2MB"},
        {"name": "notes.txt", "size": "5KB"},
        {"name": "image.png", "size": "1MB"},
        {"name": "data.csv", "size": "500KB"},
        {"name": "presentation.pptx", "size": "3MB"}
    ]

    return {"files": files[:page_size]}
