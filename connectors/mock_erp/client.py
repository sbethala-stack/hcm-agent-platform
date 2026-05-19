import uuid
from datetime import datetime
from core.models import (
    JobRequisition,
    ApplicationRecord,
    ApplicationStatus,
)
from connectors.base import BaseERPConnector
from connectors.mock_erp.seed_data import REQUISITIONS_BY_ID


class MockERPClient(BaseERPConnector):

    def __init__(self):
        self._applications: dict[str, ApplicationRecord] = {}

    def get_requisition(self, requisition_id: str) -> JobRequisition:
        if requisition_id not in REQUISITIONS_BY_ID:
            raise ValueError(f"Requisition {requisition_id} not found")
        return REQUISITIONS_BY_ID[requisition_id]

    def list_requisitions(self) -> list[JobRequisition]:
        return list(REQUISITIONS_BY_ID.values())

    def create_application(
        self,
        requisition_id: str,
        candidate_name: str,
        candidate_email: str,
        resume_text: str,
    ) -> ApplicationRecord:
        application_id = f"APP-{uuid.uuid4().hex[:8].upper()}"
        candidate_id = f"CAND-{uuid.uuid4().hex[:8].upper()}"

        record = ApplicationRecord(
            application_id=application_id,
            candidate_id=candidate_id,
            requisition_id=requisition_id,
            status=ApplicationStatus.RECEIVED,
        )
        record.__dict__["_candidate_name"] = candidate_name
        record.__dict__["_candidate_email"] = candidate_email
        record.__dict__["_resume_text"] = resume_text

        self._applications[application_id] = record
        return record

    def get_application(self, application_id: str) -> ApplicationRecord:
        if application_id not in self._applications:
            raise ValueError(f"Application {application_id} not found")
        return self._applications[application_id]

    def update_application(self, application: ApplicationRecord) -> ApplicationRecord:
        application.updated_at = datetime.utcnow()
        self._applications[application.application_id] = application
        return application

    def list_applications(
        self,
        requisition_id: str | None = None,
        status: ApplicationStatus | None = None,
    ) -> list[ApplicationRecord]:
        apps = list(self._applications.values())
        if requisition_id:
            apps = [a for a in apps if a.requisition_id == requisition_id]
        if status:
            apps = [a for a in apps if a.status == status]
        return apps