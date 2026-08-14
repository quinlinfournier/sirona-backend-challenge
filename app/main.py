from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from .database import engine, Base, get_db
from .models import Case, Employee
from .schemas import CaseResponse, EmployeeCreate, EmployeeUpdate, EmployeeResponse, ClaimCaseRequest, SubmitReportRequest
from .seed import seed_database

Base.metadata.create_all(bind=engine)

app = FastAPI(title= " Radiology Case Queue API")

@app.on_event("startup")
def startup_event():
    db = next(get_db())
    seed_database(db)

def serialize_case(case: Case) -> CaseResponse:
    return CaseResponse(
        id=case.id,
        patientName=case.patientName,
        modality=case.modality,
        studyDate=case.studyDate,
        status=case.status,
        report=case.report,
        claimedAt=case.claimedAt,
        claimedBy=case.claimed_by_employee.username if case.claimed_by_employee else None
    )

# 1

@app.get("/cases",response_model=List[CaseResponse])
def list_cases(
    status: Optional[str] = Query(None),
    claimedBy: Optional[str] = Query(None),
    db: Session = Depends(get_db)
    ):
    query = db.query(Case)

    # Filtered by status if available
    if status:
        query = query.filter(Case.status == status)
    # Filtered by claimedBy username if available
    if claimedBy:
        query = query.join(Case.claimed_by_employee).filter(Employee.username == claimedBy)

    # Decided to add tie breaker with id 
    query = query.order_by(Case.studyDate.asc(), Case.id.asc())

    cases = query.all()
    return [serialize_case(c) for c in cases]

# 2 Single Case

@app.get("/cases/{id}", response_model=CaseResponse)
def get_case(id: int, db: Session = Depends(get_db)):
    case = db.query(Case).filter(Case.id == id).first()
    if not case:
        raise HTTPException( status_code=status.HTTP_404_NOT_FOUND, detail=f"Case id {id} not found")
    return serialize_case(case)

# 3
@app.get("/employees", response_model=List[EmployeeResponse])
def get_employees(db: Session = Depends(get_db)):
    return db.query(Employee).all()

@app.post("/employees", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
def create_employee(payload: EmployeeCreate, db: Session = Depends(get_db)):
    existing = db.query(Employee).filter(Employee.username == payload.username).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username is already taken")
    
    emp = Employee(username=payload.username)
    db.add(emp)
    db.commit()
    db.refresh(emp)
    return emp

@app.put("/employees/{id}", response_model=EmployeeResponse)
def update_employee(id: int, payload: EmployeeUpdate, db: Session = Depends(get_db)):
    emp = db.query(Employee).filter(Employee.id == id).first()
    if not emp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")

    duplicate = db.query(Employee).filter(Employee.username == payload.username, Employee.id != id).first()
    if duplicate:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username is already taken")

    emp.username = payload.username
    db.commit()
    db.refresh(emp)
    return emp

@app.delete("/employees/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employee(id: int, db: Session = Depends(get_db)):
    emp = db.query(Employee).filter(Employee.id == id).first()
    if not emp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")

    db.delete(emp)
    db.commit()
    return None

# 4

@app.post("/cases/{id}/claim", response_model=CaseResponse)
def claim_case(id: int, payload: ClaimCaseRequest, db: Session = Depends(get_db)):
    # check if case exists
    case = db.query(Case).filter(Case.id == id).first()
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")

    # check if case is PENDING
    if case.status != "PENDING":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Only PENDING cases can be claimed"
        )

    # check if employee exists
    employee = db.query(Employee).filter(Employee.username == payload.claimedBy).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Employee not found"
        )

    # update the case
    case.status = "IN_PROGRESS"
    case.claimedAt = datetime.utcnow()
    case.claimedBy = employee.id

    db.commit()
    db.refresh(case)
    return serialize_case(case)

# 5
@app.post("/cases/{id}/report",response_model=CaseResponse)
def submit_report(id: int, payload: SubmitReportRequest, db: Session = Depends(get_db)):

    # check if case exists
    case = db.query(Case).filter(Case.id == id).first()
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")

    # check if case is IN_PROGRESS
    if case.status != "IN_PROGRESS":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Only IN_PROGRESS cases can be claimed"
        )

    # check if employee exists
    employee = db.query(Employee).filter(Employee.username == payload.author).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Employee not found"
        )

    # check if the author is the one who claimed the case
    if case.claimedBy != employee.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the claiming employee may submit a report")

    # update the case
    case.status = "COMPLETED"
    case.report = payload.report

    db.commit()
    db.refresh(case)
    return serialize_case(case)


    