from connectors.base import BaseERPConnector
from core.models import JobRequisition, ApplicationRecord, ApplicationStatus


class OracleHCMClient(BaseERPConnector):
    """
    Oracle HCM Recruiting Cloud connector.
    When you have Oracle access, implement each method using:
    Oracle HCM REST API v4 docs:
    https://docs.oracle.com/en/cloud/saas/human-resources/24b/farws/

    Base URL pattern:
    https://<your-tenant>.fa.oraclecloud.com/hcmRestApi/resources/latest
    """

    def __init__(self, client_id: str, client_secret: str, token_url: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = token_url
        self._token: str | None = None

    def _get_token(self) -> str:
        # OAuth2 client credentials flow
        # POST to token_url with client_id and client_secret
        raise NotImplementedError("Implement OAuth2 token fetch here")

    def get_requisition(self, requisition_id: str) -> JobRequisition:
        # GET /recruitingJobRequisitions/{id}
        raise NotImplementedError

    def list_requisitions(self) -> list[JobRequisition]:
        # GET /recruitingJobRequisitions
        raise NotImplementedError

    def create_application(
        self,
        requisition_id: str,
        candidate_name: str,
        candidate_email: str,
        resume_text: str,
    ) -> ApplicationRecord:
        # POST /recruitingCandidates
        raise NotImplementedError

    def get_application(self, application_id: str) -> ApplicationRecord:
        # GET /recruitingCandidateApplications/{id}
        raise NotImplementedError

    def update_application(self, application: ApplicationRecord) -> ApplicationRecord:
        # PATCH /recruitingCandidateApplications/{id}
        raise NotImplementedError

    def list_applications(
        self,
        requisition_id: str | None = None,
        status: ApplicationStatus | None = None,
    ) -> list[ApplicationRecord]:
        # GET /recruitingCandidateApplications
        raise NotImplementedError