from fastapi import FastAPI
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
    template_id = "NY-activity"
    # template_id = "react_sdk_primer_activity"
    activity_id = "quickstart_examples_activity_001"

    # Items API configuration parameters
    assessment_config = {
        "user_id": user_id,
        "session_id": session_id,
        "activity_template_id": template_id,
        "activity_id": activity_id,
        "rendering_type": "assess",
        "type": "submit_practice",
        "name": "Items API Quickstart",
        "state": "initial",
        "config": {
            "configuration": {
                "fontsize": "large"
            }
        }
    }
    
    # Set up Learnosity initialization data
    init_items = Init(
        "items", security, config.consumer_secret,
        request=assessment_config
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
