from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_add_question():
    """Test the add_question endpoint with a sample MCQ question."""
    test_data = {
        "questions": [
            {
                "reference": "engen_test_mcq_001",
                "type": "mcq",
                "data": {
                    "stimulus": "What is the capital of France?",
                    "type": "mcq",
                    "options": [
                        {"label": "London", "value": "0"},
                        {"label": "Berlin", "value": "1"},
                        {"label": "Paris", "value": "2"},
                        {"label": "Madrid", "value": "3"}
                    ],
                    "validation": {
                        "scoring_type": "exactMatch",
                        "valid_responses": [{"score": 1, "value": ["2"]}]
                    }
                }
            }
        ]
    }

    response = client.post("/api/questions/add", json=test_data)

    # Assert the response status
    assert response.status_code == 200

    # Assert the response structure
    response_data = response.json()
    print(response_data)
    assert "success" in response_data
    assert "message" in response_data
    assert response_data["success"] is True
    assert "Successfully added 1 question(s)" in response_data["message"]