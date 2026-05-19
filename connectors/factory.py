from config.settings import get_settings
from connectors.base import BaseERPConnector


def get_erp_connector() -> BaseERPConnector:
    settings = get_settings()

    if settings.erp_connector == "mock":
        from connectors.mock_erp.client import MockERPClient
        return MockERPClient()

    elif settings.erp_connector == "oracle":
        from connectors.oracle_hcm.client import OracleHCMClient
        import os
        return OracleHCMClient(
            client_id=os.environ["ORACLE_CLIENT_ID"],
            client_secret=os.environ["ORACLE_CLIENT_SECRET"],
            token_url=os.environ["ORACLE_TOKEN_URL"],
        )

    else:
        raise ValueError(f"Unknown ERP connector: {settings.erp_connector}")