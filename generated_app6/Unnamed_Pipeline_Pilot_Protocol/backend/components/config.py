"""
Configuration Management with Zero-Hardcoding Hygiene
"""
import os
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class PipelineConfig:
    azure_account_name: str = os.getenv("AZURE_STORAGE_ACCOUNT", "bnlwestges01005")
    azure_storage_key: Optional[str] = os.getenv("AZURE_STORAGE_KEY")
    azure_connection_string: Optional[str] = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    azure_share_name: str = os.getenv("AZURE_SHARE_NAME", "rdplp-sbx1")
    biovia_notebook_url: str = os.getenv("BIOVIA_NOTEBOOK_URL", "https://notebook.corp.internal/eln")
    biovia_session_token: Optional[str] = os.getenv("BIOVIA_SESSION_TOKEN")
    staging_directory: str = os.getenv("STAGING_DIRECTORY", "/tmp/biovia_downloads")
    verify_ssl: bool = os.getenv("VERIFY_SSL", "true").lower() in ("true", "1", "yes")

    def validate_azure_credentials(self) -> bool:
        return bool(self.azure_connection_string or (self.azure_account_name and self.azure_storage_key))
