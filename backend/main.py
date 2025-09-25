from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from learnosity_sdk.request import Init, DataApi
from learnosity_sdk.utils import Uuid
import config
import json
import requests
import logging
from pydantic import BaseModel
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

class ItemData(BaseModel):
    name: str
    reference: str
    description: str = ""
    status: str = "published"
    questions: List[str]  # List of question references
    definition: Dict[str, Any] | None = None  # Required by Learnosity

class AddItemRequest(BaseModel):
    items: List[ItemData]

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


@app.get("/api/tests/new")
async def new_test():
    try:
        logger.info("Creating new test with fresh question and item")

        # Generate unique references for this test
        test_id = Uuid.generate()
        question_reference = f"test_question_{test_id}"
        item_reference = f"test_item_{test_id}"

        logger.info(f"Generated question reference: {question_reference}")
        logger.info(f"Generated item reference: {item_reference}")

        # Create a sample question
        sample_question = Question(
            reference=question_reference,
            type="mcq",
            data=QuestionData(
                stimulus="What is the capital of Spain?",
                type="mcq",
                options=[
                    {"label": "Barcelona", "value": "A"},
                    {"label": "Madrid", "value": "B"},
                    {"label": "Valencia", "value": "C"},
                    {"label": "Seville", "value": "D"}
                ],
                validation={
                    "scoring_type": "exactMatch",
                    "valid_response": {
                        "score": 1,
                        "value": ["B"]
                    }
                }
            )
        )

        # Create the question using our existing function
        question_request = AddQuestionRequest(questions=[sample_question])

        logger.info("Creating question in Learnosity...")
        question_result = await add_question(question_request, create_item=False)  # Don't auto-create item

        if not question_result["success"]:
            raise HTTPException(status_code=500, detail="Failed to create question")

        # Create the item manually with our custom reference
        item_data = ItemData(
            name=f"Test Item {test_id}",
            reference=item_reference,
            description=f"Auto-generated test item for question {question_reference}",
            status="published",
            questions=[question_reference]
        )

        logger.info("Creating item in Learnosity...")
        item_result = await create_learnosity_item(item_data)

        if item_result["status_code"] != 200:
            raise HTTPException(status_code=500, detail="Failed to create item")

        logger.info(f"Successfully created question and item. Item reference: {item_reference}")

        # Generate the user ID and session ID as UUIDs
        user_id = Uuid.generate()
        session_id = Uuid.generate()
        # Activity ID must be <= 36 characters, so we'll use just the first 8 chars of test_id
        activity_id = f"test_{str(test_id)[:8]}"

        # Items API configuration parameters with our created item
        assessment_config = {
            "user_id": user_id,
            "session_id": session_id,
            "activity_id": activity_id,
            "rendering_type": "assess",
            "type": "submit_practice",
            "name": "Dynamic Test - Items API",
            "state": "initial",
            "items": [
                item_reference  # Include our created item reference
            ],
            "config": {
                "configuration": {
                    "fontsize": "large",
                },
                "regions": "horizontal",
            },
        }

        logger.info(f"Assessment config prepared with item: {item_reference}")

        # Set up Learnosity initialization data
        init_items = Init(
            "items", security, config.consumer_secret,
            request=assessment_config
        )

        generated_request = init_items.generate()

        # The Learnosity SDK returns a JSON string, so we need to parse it
        if isinstance(generated_request, str):
            generated_request = json.loads(generated_request)

        logger.info("Successfully generated Learnosity initialization data")

        return generated_request

    except Exception as e:
        logger.error(f"Failed to create new test: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create new test: {str(e)}")


@app.get("/api/items/get/{item_reference}")
async def get_item(item_reference: str):
    """Get an item from Learnosity Item Bank to verify it exists"""
    try:
        logger.info(f"Retrieving item: {item_reference}")

        # Data API endpoint for getting items
        endpoint = "https://data.learnosity.com/latest/itembank/items"

        # Create security configuration for Data API
        data_api_security = {
            "consumer_key": config.consumer_key,
            "domain": host
        }

        # Prepare the request data for getting a specific item
        data_request = {
            "items": [item_reference]
        }

        logger.info(f"Get item request data: {json.dumps(data_request, indent=2)}")

        # Create Data API client and make the request
        client = DataApi()
        response = client.request(
            endpoint,
            data_api_security,
            config.consumer_secret,
            data_request,
            "get"  # Use "get" action instead of "set"
        )

        logger.info(f"Get item response status: {response.status_code}")

        # Parse the response properly
        if hasattr(response, 'json'):
            try:
                response_data = response.json()
            except:
                response_data = response.text if hasattr(response, 'text') else str(response)
        else:
            response_data = str(response)

        logger.info(f"Get item response data: {json.dumps(response_data, indent=2) if isinstance(response_data, dict) else response_data}")

        return {
            "item_reference": item_reference,
            "status_code": response.status_code,
            "data": response_data
        }

    except Exception as e:
        logger.error(f"Failed to get item {item_reference}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get item: {str(e)}")




async def create_learnosity_item(item_data: ItemData):
    """Create an item in Learnosity Item Bank"""
    try:
        logger.info(f"Creating item with reference: {item_data.reference}")

        # Data API endpoint for setting items
        endpoint = "https://data.learnosity.com/latest/itembank/items"

        # Create security configuration for Data API
        data_api_security = {
            "consumer_key": config.consumer_key,
            "domain": host
        }

        # Prepare the request data
        item_payload = {
            "reference": item_data.reference,
            "name": item_data.name,
            "description": item_data.description,
            "status": item_data.status,
            "questions": item_data.questions
        }

        # Add definition if provided, or create a basic one
        if item_data.definition:
            item_payload["definition"] = item_data.definition
        else:
            # Create a basic definition with widgets (which reference the questions)
            item_payload["definition"] = {
                "template": "dynamic",
                "instant_feedback": True,
                "widgets": [{"reference": q, "widget_type": "response"} for q in item_data.questions]
            }

        data_request = {
            "items": [item_payload]
        }

        logger.info(f"Item creation request data: {json.dumps(data_request, indent=2)}")

        # Create Data API client and make the request
        client = DataApi()
        response = client.request(
            endpoint,
            data_api_security,
            config.consumer_secret,
            data_request,
            "set"
        )

        logger.info(f"Item creation response status: {response.status_code}")

        # Parse the response properly
        if hasattr(response, 'json'):
            try:
                response_data = response.json()
            except:
                response_data = response.text if hasattr(response, 'text') else str(response)
        else:
            response_data = str(response)

        logger.info(f"Item creation response data: {response_data}")

        return {
            "status_code": response.status_code,
            "data": response_data
        }

    except Exception as e:
        logger.error(f"Failed to create item: {str(e)}")
        raise e


@app.post("/api/items/add")
async def add_item(request: AddItemRequest):
    """Add items to Learnosity Item Bank"""
    try:
        logger.info(f"Adding {len(request.items)} item(s)")

        results = []
        for item in request.items:
            response = await create_learnosity_item(item)
            results.append(response)

        return {
            "success": True,
            "message": f"Successfully processed {len(request.items)} item(s)",
            "results": results
        }

    except Exception as e:
        logger.error(f"Failed to add items: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to add items: {str(e)}")


@app.post("/api/questions/add")
async def add_question(request: AddQuestionRequest, create_item: bool = True):
    """Add questions to Learnosity Item Bank and optionally create items"""
    try:
        logger.info(f"Adding {len(request.questions)} question(s)")

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
        question_references = []
        for question in request.questions:
            question_data = {
                "reference": question.reference,
                "type": question.type,
                "data": question.data.model_dump()
            }
            data_request["questions"].append(question_data)
            question_references.append(question.reference)

        logger.info(f"Question creation request data: {json.dumps(data_request, indent=2)}")

        # Create Data API client and make the request
        client = DataApi()
        response = client.request(
            endpoint,
            data_api_security,
            config.consumer_secret,
            data_request,
            "set"
        )

        logger.info(f"Question creation response status: {response.status_code}")

        # Convert response to JSON if it's not already
        if hasattr(response, 'json'):
            try:
                response_data = response.json()
            except:
                response_data = response.text if hasattr(response, 'text') else str(response)
        elif hasattr(response, 'text'):
            response_data = response.text
        else:
            response_data = str(response)

        logger.info(f"Question creation response data: {response_data}")

        result = {
            "success": True,
            "message": f"Successfully added {len(request.questions)} question(s)",
            "question_response": response_data
        }

        # If create_item is True, also create items that reference these questions
        if create_item:
            logger.info("Creating items for the added questions")

            items_to_create = []
            for question in request.questions:
                item_data = ItemData(
                    name=f"Item for {question.reference}",
                    reference=f"item_{question.reference}",
                    description=f"Auto-generated item for question {question.reference}",
                    status="published",
                    questions=[question.reference]
                )
                items_to_create.append(item_data)

            # Create items
            item_results = []
            for item in items_to_create:
                try:
                    item_response = await create_learnosity_item(item)
                    item_results.append(item_response)
                    logger.info(f"Successfully created item {item.reference}")
                except Exception as item_error:
                    logger.error(f"Failed to create item {item.reference}: {str(item_error)}")
                    item_results.append({"error": str(item_error), "reference": item.reference})

            result["item_results"] = item_results
            result["message"] += f" and {len(items_to_create)} item(s)"

        return result

    except Exception as e:
        logger.error(f"Failed to add questions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to add question: {str(e)}")



def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
