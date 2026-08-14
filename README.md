# Radiology Case Queue API
API to manage radiology reading queue, allowing employees to claim pending imaging cases and submit clinical reports.
Built using FastAPI, SQLite, and SQLAlchemy

1. **Activate a virtual enviroment** (recommeded)
    ''' bash 
    python3 -m venv venv
    source venv/bin/activate

2. **Install dependancies**
    pip install -r requirements.txt

3. **Run Test Suite**
    pytest -v

4. **Run Application** 
uvicorn app.main:app --reload

**Design Desisons**
I choose to use auto incrementing IDS for internal foreign keys relationship.
Also the FastAPI CaseResponse schema and serializeation allows the databse to keep track of employee id and show username for the client.

**Assumptions**
I assumed that employees being deleted was a permanent
I choose to use UTC time as a standard for claimedAt
Assumed that clients would pass exact string like "PENDING" or "IN_PROGRESS"


