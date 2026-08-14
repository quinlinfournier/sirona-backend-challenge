import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client

def test_list_cases_default_ordered_by_study_date(client):
    """GET /cases returns all seeded cases ordered chronologically by studyDate."""
    response = client.get("/cases")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 8  # 8 seeded cases

    # Verify ascending sort by studyDate
    study_dates = [c["studyDate"] for c in data]
    assert study_dates == sorted(study_dates)

def test_filter_cases_by_status(client):
    """GET /cases?status=PENDING returns only pending cases."""
    response = client.get("/cases?status=PENDING")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert all(c["status"] == "PENDING" for c in data)

def test_filter_cases_by_claimed_by(client):
    """GET /cases?claimedBy=jsmith returns only cases claimed by jsmith."""
    response = client.get("/cases?claimedBy=jsmith")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert all(c["claimedBy"] == "jsmith" for c in data)

def test_filter_cases_by_status_and_claimed_by(client):
    """GET /cases?status=IN_PROGRESS&claimedBy=jsmith filters by both."""
    response = client.get("/cases?status=IN_PROGRESS&claimedBy=jsmith")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert all(c["status"] == "IN_PROGRESS" and c["claimedBy"] == "jsmith" for c in data)
# 2
def test_get_single_case_success(client):
    """GET /cases/1 returns the first case successfully."""
    response = client.get("/cases/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert "patientName" in data
    assert "modality" in data

def test_get_single_case_not_found(client):
    """GET /cases/999 returns 404 for a non-existent case."""
    response = client.get("/cases/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Case id 999 not found"

# 3

def test_get_employees(client):
    """GET /employees returns a list of seeded employees."""
    response = client.get("/employees")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3  # We seeded 3 employees initially
    assert "username" in data[0]

def test_create_employee_success(client):
    """POST /employees creates a new employee."""
    response = client.post("/employees", json={"username": "new_radiologist"})
    assert response.status_code == 201
    assert response.json()["username"] == "new_radiologist"
    assert "id" in response.json()

def test_create_employee_duplicate_fails(client):
    """POST /employees with an existing username returns 409 Conflict."""
    # Attempting to create the exact same employee again
    response = client.post("/employees", json={"username": "new_radiologist"})
    assert response.status_code == 409
    assert response.json()["detail"] == "Username is already taken"

def test_claim_case_success(client):
    """POST /cases/:id/claim successfully claims a pending case."""
    # Using Case 1 which is seeded as PENDING
    response = client.post("/cases/1/claim", json={"claimedBy": "jsmith"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "IN_PROGRESS"
    assert data["claimedBy"] == "jsmith"
    assert data["claimedAt"] is not None

def test_claim_case_already_claimed_fails(client):
    """POST /cases/:id/claim fails if case is not PENDING."""
    # Using Case 2 which is seeded as IN_PROGRESS
    response = client.post("/cases/2/claim", json={"claimedBy": "m_grey"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Only PENDING cases can be claimed"

def test_claim_case_invalid_user_fails(client):
    """POST /cases/:id/claim fails if employee username doesn't exist."""
    # Using Case 4 which is seeded as PENDING
    response = client.post("/cases/4/claim", json={"claimedBy": "fake_user"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Employee not found"
# 5
def test_submit_report_success(client):
    """POST /cases/:id/report succeeds for IN_PROGRESS case by claiming employee."""
    # Using Case 2 which is seeded as IN_PROGRESS claimed by jsmith
    payload = {"author": "jsmith", "report": "Findings are consistent with normality."}
    response = client.post("/cases/2/report", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "COMPLETED"
    assert data["report"] == payload["report"]

def test_submit_report_wrong_status_fails(client):
    """POST /cases/:id/report fails if case is PENDING or COMPLETED."""
    # Use Case 4, which is safely PENDING (Case 1 was modified earlier)
    payload = {"author": "jsmith", "report": "This should fail."}
    response = client.post("/cases/4/report", json=payload)
    assert response.status_code == 400
    # Note: Make sure this string exactly matches the one in your main.py!
    # If your API says "Only IN_PROGRESS cases can be claimed", use that here.
    assert "IN_PROGRESS" in response.json()["detail"] 

def test_submit_report_wrong_user_fails(client):
    """POST /cases/:id/report fails if authored by an employee who didn't claim it."""
    # Use Case 6, which is claimed by dr_house, but we attempt as jsmith
    payload = {"author": "jsmith", "report": "I am taking over this case."}
    response = client.post("/cases/6/report", json=payload)
    assert response.status_code == 403
    assert response.json()["detail"] == "Only the claiming employee may submit a report"

def test_submit_report_invalid_user_fails(client):
    """POST /cases/:id/report fails if author doesn't exist."""
    # Use Case 6, which safely has an IN_PROGRESS status
    payload = {"author": "fake_user", "report": "Ghost report."}
    response = client.post("/cases/6/report", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Employee not found"

def test_submit_report_empty_body_fails(client):
    """POST /cases/:id/report fails if report body is empty."""
    payload = {"author": "jsmith", "report": ""}
    response = client.post("/cases/2/report", json=payload)
    # Pydantic schema catches the empty string and returns 422 automatically
    assert response.status_code == 422
