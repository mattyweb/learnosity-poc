from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from learnosity_sdk.request import Init
from learnosity_sdk.utils import Uuid
import config
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set variables for the web server
host = "localhost"
port = 8000

# Public & private security keys required to access Learnosity APIs
security = {
    "user_id": "abc",
    "consumer_key": config.consumer_key,
    "domain": host,
}

@app.get("/")
async def home():
    return {"message": "FastAPI Learnosity Demo", "apis": {"items": "/api/items"}}

@app.get("/api/items")
async def items_assessment():
    # Generate the user ID and session ID as UUIDs
    user_id = Uuid.generate()
    session_id = Uuid.generate()
    
    # Items API configuration parameters
    items_request = {
        "user_id": user_id,
        "activity_template_id": "react_sdk_primer_activity",
        "session_id": session_id,
        "activity_id": "quickstart_examples_activity_001",
        "rendering_type": "assess",
        "type": "submit_practice",
        "name": "Items API Quickstart",
        "state": "initial"
    }
    
    # Set up Learnosity initialization data
    init_items = Init(
        "items", security, config.consumer_secret,
        request=items_request
    )
    
    generated_request = init_items.generate()
    
    # The Learnosity SDK returns a JSON string, so we need to parse it
    if isinstance(generated_request, str):
        generated_request = json.loads(generated_request)
    
    return generated_request

def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
