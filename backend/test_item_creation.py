#!/usr/bin/env python3

import requests
import json

# Test data for creating a question and item
test_data = {
    "questions": [
        {
            "reference": "test_question_001",
            "type": "mcq",
            "data": {
                "stimulus": "What is the capital of France?",
                "type": "mcq",
                "options": [
                    {"label": "A", "value": "London"},
                    {"label": "B", "value": "Paris"},
                    {"label": "C", "value": "Berlin"},
                    {"label": "D", "value": "Madrid"}
                ],
                "validation": {
                    "scoring_type": "exactMatch",
                    "valid_response": {
                        "score": 1,
                        "value": ["B"]
                    }
                }
            }
        }
    ]
}

def test_question_and_item_creation():
    """Test creating a question and automatically creating an item"""
    print("Testing question and item creation...")
    print(f"Request data: {json.dumps(test_data, indent=2)}")

    try:
        # Make request to create question (and automatically create item)
        response = requests.post(
            "http://localhost:8000/api/questions/add",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )

        print(f"Response status: {response.status_code}")
        print(f"Response body: {json.dumps(response.json(), indent=2)}")

        if response.status_code == 200:
            print("✅ Question and item creation successful!")
        else:
            print("❌ Request failed")

    except Exception as e:
        print(f"❌ Error: {e}")

def test_item_creation_only():
    """Test creating an item directly"""
    print("\nTesting direct item creation...")

    item_data = {
        "items": [
            {
                "name": "Direct Test Item",
                "reference": "direct_test_item_001",
                "description": "A test item created directly",
                "status": "published",
                "questions": ["test_question_001"]  # Reference the question created above
            }
        ]
    }

    print(f"Request data: {json.dumps(item_data, indent=2)}")

    try:
        response = requests.post(
            "http://localhost:8000/api/items/add",
            json=item_data,
            headers={"Content-Type": "application/json"}
        )

        print(f"Response status: {response.status_code}")
        print(f"Response body: {json.dumps(response.json(), indent=2)}")

        if response.status_code == 200:
            print("✅ Direct item creation successful!")
        else:
            print("❌ Request failed")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_question_and_item_creation()
    test_item_creation_only()