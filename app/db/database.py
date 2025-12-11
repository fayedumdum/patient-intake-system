from sqlalchemy.orm import joinedload
from app.db.base import AsyncSessionLocal
from app.db.models import Patient, Person, Visit
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

# -----------------------------
# DB session helper
# -----------------------------
async def get_db_session():
    async with AsyncSessionLocal() as session:
        yield session


# -----------------------------
# Patient / Person CRUD
# -----------------------------
async def get_patient_by_id(db_session: AsyncSession, id: int):
        stmt = select(Patient).options(
                    joinedload(Patient.person),
                    joinedload(Patient.visits)
        ).where(Patient.id == id)
        
        return (await db_session.scalars(stmt)).first()

async def get_patients(
    db_session: AsyncSession,
    skip: int = 0,
    limit: int = 10,
    mrn: str = None,
    first_name: str = None,
    last_name: str = None
):
    stmt = select(Patient).options(
        joinedload(Patient.person),
        joinedload(Patient.visits)
    )

    if mrn:
        stmt = stmt.filter(Patient.mrn.ilike(f"%{mrn}%"))
    if first_name or last_name:
        stmt = stmt.join(Patient.person)  # join to Person to filter
        if first_name:
            stmt = stmt.filter(Person.first_name.ilike(f"%{first_name}%"))
        if last_name:
            stmt = stmt.filter(Person.last_name.ilike(f"%{last_name}%"))

    
    total = select(func.count()).select_from(stmt.subquery())
    stmt = stmt.offset(skip).limit(limit)

    # total = await db_session.scalar(select(func.count(Person.id)))
    total = await db_session.scalar(total)

    patients_result = await db_session.execute(stmt)
    patients = patients_result.unique().scalars().all()

    return patients, total
