from app.models.response_models import PatientResponse, PersonResponse, VisitResponse

def patient_to_response(patient) -> PatientResponse:
    return PatientResponse(
        id=patient.id,
        mrn=patient.mrn,
        created_at=patient.created_at.isoformat(),
        person=PersonResponse(
            first_name=patient.person.first_name,
            last_name=patient.person.last_name,
            birth_date=patient.person.birth_date
        ),
        visits=[
            VisitResponse(
                visit_account_number=v.visit_account_number,
                visit_date=v.visit_date,
                reason=v.reason
            ) for v in patient.visits
        ]
    )
