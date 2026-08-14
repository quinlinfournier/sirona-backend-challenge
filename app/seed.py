from datetime import date, datetime
from sqlalchemy.orm import Session
from .models import Employee, Case

# had AI generate example employees and cases

def seed_database(db: Session):
    if db.query(Employee).count() > 0 or db.query(Case).count() > 0:
        return

    # Seed 3 Employees
    employees = [
        Employee(username="jsmith"),
        Employee(username="dr_house"),
        Employee(username="m_grey"),
    ]
    db.add_all(employees)
    db.commit()

    for emp in employees:
        db.refresh(emp)

    jsmith = employees[0]
    dr_house = employees[1]

    # Seed 8+ Cases with varied modalities and statuses
    cases = [
        Case(
            patientName="Alice Cooper",
            modality="CT",
            studyDate=date(2024, 10, 1),
            status="PENDING",
        ),
        Case(
            patientName="Bob Marley",
            modality="MRI",
            studyDate=date(2024, 10, 5),
            status="IN_PROGRESS",
            claimedAt=datetime(2024, 10, 6, 14, 30),
            claimedBy=jsmith.id,
        ),
        Case(
            patientName="Charlie Brown",
            modality="XR",
            studyDate=date(2024, 10, 10),
            status="COMPLETED",
            claimedAt=datetime(2024, 10, 11, 9, 0),
            claimedBy=dr_house.id,
            report="Findings indicate normal chest radiographs with no active infiltrates.",
        ),
        Case(
            patientName="Diana Prince",
            modality="US",
            studyDate=date(2024, 10, 12),
            status="PENDING",
        ),
        Case(
            patientName="Evan Wright",
            modality="CT",
            studyDate=date(2024, 10, 15),
            status="PENDING",
        ),
        Case(
            patientName="Fiona Gallagher",
            modality="MRI",
            studyDate=date(2024, 10, 18),
            status="IN_PROGRESS",
            claimedAt=datetime(2024, 10, 19, 11, 15),
            claimedBy=dr_house.id,
        ),
        Case(
            patientName="George Clark",
            modality="XR",
            studyDate=date(2024, 10, 20),
            status="PENDING",
        ),
        Case(
            patientName="Hannah Abbott",
            modality="US",
            studyDate=date(2024, 10, 25),
            status="COMPLETED",
            claimedAt=datetime(2024, 10, 26, 16, 45),
            claimedBy=jsmith.id,
            report="Abdominal ultrasound demonstrates clear gall bladder and liver parenchymal integrity.",
        ),
    ]

    db.add_all(cases)
    db.commit()