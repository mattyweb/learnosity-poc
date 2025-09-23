from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from learnosity_sdk.request import Init, DataApi
from learnosity_sdk.utils import Uuid
import config
import json
import requests
from pydantic import BaseModel
from typing import Dict, Any, List

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

# Fetch Spanish labels from Learnosity i18n
url = "https://raw.githubusercontent.com/Learnosity/learnosity-i18n/master/languages/es-ES/label_bundles/assess-api.json"
response = requests.get(url)
spanish_labels = response.json()

# Pydantic models for request validation
class QuestionData(BaseModel):
    stimulus: str
    type: str
    options: List[Dict[str, str]]
    validation: Dict[str, Any]

class Question(BaseModel):
    reference: str
    type: str
    data: QuestionData

class AddQuestionRequest(BaseModel):
    questions: List[Question]

# Public & private security keys required to access Learnosity APIs
security = {
    "user_id": "abc", # what is this used for?
    "consumer_key": config.consumer_key,
    "domain": host,
}


@app.get("/api/items")
async def items_assessment():
    # Generate the user ID and session ID as UUIDs
    user_id = Uuid.generate()
    session_id = Uuid.generate()
    # template_id = "NY-activity"
    template_id = "react_sdk_primer_activity"
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
                "fontsize": "large",
            },
            "regions": "horizontal",
            "labelBundle": spanish_labels,
        },
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


@app.post("/api/questions/add")
async def add_question(request: AddQuestionRequest):
    try:
        # Data API endpoint for setting questions
        endpoint = "https://data.learnosity.com/latest/itembank/questions"

        # Create security configuration for Data API
        data_api_security = {
            "consumer_key": config.consumer_key,
            "domain": host
        }

        # Prepare the request data
        data_request = {
            "questions": []
        }

        # Convert Pydantic models to dictionary format expected by Learnosity
        for question in request.questions:
            question_data = {
                "reference": question.reference,
                "type": question.type,
                "data": question.data.model_dump()
            }
            data_request["questions"].append(question_data)

        # Create Data API client and make the request
        client = DataApi()
        response = client.request(
            endpoint,
            data_api_security,
            config.consumer_secret,
            data_request,
            "set"
        )

        # Convert response to JSON if it's not already
        if hasattr(response, 'json'):
            response_data = response.json()
        elif hasattr(response, 'text'):
            response_data = response.text
        else:
            response_data = str(response)

        return {
            "success": True,
            "message": f"Successfully added {len(request.questions)} question(s)",
            "response": response_data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add question: {str(e)}")



def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
