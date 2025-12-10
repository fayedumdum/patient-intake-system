from temporalio import activity
import csv
from app.db.models import Patient, Person, Visit
from app.models.request_models import VisitRecord
from app.services.s3_service import download_csv, S3_BUCKET
from sqlalchemy import select
from app.db.base import AsyncSessionLocal
from sqlalchemy.orm import selectinload

@activity.defn
async def process_csv(file_name: str):
    local_path = f"/tmp/{file_name}"
    download_csv(S3_BUCKET, file_name, local_path)

    async with AsyncSessionLocal() as session:
        
        with open(local_path) as f:
            reader = csv.DictReader(f)

            for row in reader:
                async with session.begin():
                    visit_record = VisitRecord.model_validate(row)
                    
                    patient = (await session.scalars(select(Patient).filter_by(mrn=visit_record.mrn).options(selectinload(Patient.person)))).first()

                    if not patient:
                        # Create new patient
                        patient = Patient(mrn=visit_record.mrn)
                        session.add(patient)
                        await session.flush()
                        
                        person = Person(
                            id=patient.id,
                            first_name=visit_record.first_name,
                            last_name=visit_record.last_name,
                            birth_date=visit_record.birth_date
                        )
                        session.add(person)
                    else:
                        # Update person
                        person = patient.person
                        person.first_name = visit_record.first_name
                        person.last_name = visit_record.last_name
                        person.birth_date = visit_record.birth_date

                    
                    visit = (await session.scalars(select(Visit).filter_by(visit_account_number=visit_record.visit_account_number))).first()

                    if not visit:
                        visit = Visit(
                            visit_account_number=visit_record.visit_account_number,
                            patient_id=patient.id,
                            visit_date=visit_record.visit_date,
                            reason=visit_record.reason
                        )
                        session.add(visit)