from abc import ABC, abstractmethod
from core.models import JobRequisition, ApplicationRecord, ApplicationStatus


class BaseERPConnector(ABC):

    @abstractmethod
    def get_requisition(self, requisition_id: str) -> JobRequisition:
        ...

    @abstractmethod
    def list_requisitions(self) -> list[JobRequisition]:
        ...

    @abstractmethod
    def create_application(
        self,
        requisition_id: str,
        candidate_name: str,
        candidate_email: str,
        resume_text: str,
    ) -> ApplicationRecord:
        ...

    @abstractmethod
    def get_application(self, application_id: str) -> ApplicationRecord:
        ...

    @abstractmethod
    def update_application(self, application: ApplicationRecord) -> ApplicationRecord:
        ...

    @abstractmethod
    def list_applications(
        self,
        requisition_id: str | None = None,
        status: ApplicationStatus | None = None,
    ) -> list[ApplicationRecord]:
        ...