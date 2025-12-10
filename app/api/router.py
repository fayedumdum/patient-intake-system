from typing import List
from fastapi import APIRouter, HTTPException, Depends
import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.request_models import VisitRecord
from app.models.response_models import IngestResponse, PaginatedPatientResponse, PatientResponse
from app.utils.csv_utils import generate_csv_file
from app.services.s3_service import upload_to_s3
from app.utils.response_helper import patient_to_response
from app.db.database import get_db_session, get_patient_by_id, get_patients
from temporalio.client import Client
import uuid
import asyncpg

router = APIRouter()


@router.post("/ingest", response_model=IngestResponse)
async def ingest(records: List[VisitRecord]):
    """
    Accepts a JSON array where each object represents a visit record. The Medical
    Record Number (MRN) uniquely identifies a patient. The Visit Account Number uniquely
    identifies a visit.

    Store data into local CSV and upload CSV into s3 bucket
    Once the file is uploaded to S3, the API must trigger a Temporal workflow that:
    1. Fetch the CSV from S3
    2. Parse each row
    3. Resolve or create patients
    4. Update person details
    5. Insert visit records linked to the correct patient
    
    :param records: Description
    :type records: List[VisitRecord]
    """
    try:
        if not records:
            raise HTTPException(status_code=400, detail="Payload cannot be empty.")
        else:
            csv_path, file_name = generate_csv_file(records)
            bucket_name = upload_to_s3(csv_path)

            client = await Client.connect("temporal:7233")
            result = await client.execute_workflow(
                "CsvIngestWorkflow",
                file_name,
                id=str(uuid.uuid4()),
                task_queue="csv-task-queue",
            )
            print(result)
    except sqlalchemy.exc.IntegrityError as duplicate_error:
        raise HTTPException(status_code=409, detail=f"Duplicate Entry: {duplicate_error}")
    except Exception as error:
        print(error)
        raise HTTPException(status_code=400, detail=str(error))
    else:
        return IngestResponse(
            status="success",
            message="Patient information created and uploaded successfully.",
            local_path=csv_path,
            s3_location=f"s3://{bucket_name}/{file_name}"
        )


@router.get("/patients", response_model=PaginatedPatientResponse)
async def list_patients(
    mrn: str | None = None,
    first_name: str | None = None,
    last_name: str | None = None,
    page: int = 1,
    size: int = 20,
    db_session: AsyncSession = Depends(get_db_session)
    ):
    """
    Returns all the patients including the person and visit information.
    
    :param mrn: Optional medical record number to filter patients
    :type mrn: str | None
    :param first_name: Optional first name to filter patients
    :type first_name: str | None
    :param last_name: Optional last name to filter patients
    :type last_name: str | None
    :param page: Page number for pagination (default: 1)
    :type page: int
    :param size: Number of records per page (default: 20)
    :type size: int
    :param db: Database session (injected by Depends)
    :type db: Session

    :return: List of patients with their person and visit info
    :rtype: List[Patient]
    """
    try:
        skip = (page - 1) * size
        patients, total = await get_patients(db_session, skip, size, mrn, first_name, last_name)
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))
    else:
        return PaginatedPatientResponse(
            page= page,
            size= size,
            total= total,
            patients=[patient_to_response(p) for p in patients]
        )
    
@router.get("/patients/{id}", response_model=PatientResponse)
async def get_patient(id: int, db_session: AsyncSession = Depends(get_db_session)):
    """
    Retrieve a single patient information which also includes person and visit information.
    
    :param id: Description
    :type id: int
    :param db: Description
    :type db: Session
    """
    try:
        patient = await get_patient_by_id(db_session, id)
        if not patient:
            raise HTTPException(status_code=404, detail=f"Patient with ID: {id} does not exists")
    except asyncpg.errors.InvalidTextRepresentation as error:
        raise HTTPException(status_code=400, detail=str(error))
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))
    else:
        return patient
