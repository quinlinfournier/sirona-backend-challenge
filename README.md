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
I chose to use auto-incrementing IDs for internal foreign key relationships.
Also, the FastAPI CaseResponse schema and serialization allow the database to keep track of employee ID and show the username for the client.

**Assumptions**
I assumed that employees being deleted was permanent.
I chose to use UTC time as a standard for claimedAt. 
Assumed that clients would pass an exact string like "PENDING" or "IN_PROGRESS".


