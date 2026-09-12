"""
End-to-End Orchestrator Replacing the Entire Biovia PLP Protocol
Coordinates cleanup, XML model parsing, Azure downloads, section dispatch, and ELN commits.
"""
import logging
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from .xml_model_parser import parse_model_xml, ModelXmlMetadata
from .azure_downloader import AzureFileShareDownloader
from .biovia_notebook import BioviaNotebookClient
from .section_dispatcher import SectionDispatcher
from .custom_filter import custom_filter
from .file_utils import cleanup_directory

logger = logging.getLogger("biovia_pipeline.orchestrator")


@dataclass
class PipelineRunResult:
    success: bool
    experiment_number: str
    experiment_id: str
    files_processed: int
    sections_created: List[Dict[str, str]] = field(default_factory=list)
    duration_seconds: float = 0.0
    error_message: Optional[str] = None


class ElnDataTransferPipeline:
    """
    Python replacement for the Biovia Pipeline Pilot 'Data model UI' protocol.
    """

    def __init__(self, mock_mode: bool = True):
        self.mock_mode = mock_mode

    def run(
        self,
        xml_source: Union[str, Path],
        experiment_number: str,
        session_token: Optional[str] = None,
        selected_files: Optional[List[str]] = None,
        staging_dir: Optional[Union[str, Path]] = None
    ) -> PipelineRunResult:
        start_time = time.time()
        logger.info(f"Starting pipeline run for experiment '{experiment_number}'")

        try:
            # 1. Pre-cleanup staging directory (replaces PLP Component 56)
            if staging_dir:
                cleanup_directory(staging_dir)

            # 2. Gatekeeper condition check (replaces PLP Component 59: Custom Filter)
            gatekeeper_ok = custom_filter(
                "@experiment_number is defined and @experiment_number is ne '' and @filelocation is eq ''",
                globals_dict={"experiment_number": experiment_number, "filelocation": ""}
            )
            if not gatekeeper_ok:
                raise ValueError("Gatekeeper condition failed: Invalid experiment_number or filelocation not empty.")

            # 3. Parse XML Metadata (replaces PLP Component 22)
            model_meta: ModelXmlMetadata = parse_model_xml(xml_source)
            logger.info(f"Parsed XML section '{model_meta.section_name}' with {len(model_meta.files)} files.")

            # 4. File selection verification (replaces PLP Component 47: Custom Filter)
            files_to_download = selected_files or model_meta.file_names
            has_files = custom_filter(
                "@filelist is defined and @filelist is ne ''",
                globals_dict={"filelist": files_to_download}
            )
            if not has_files:
                raise ValueError("No candidate files selected for transfer.")

            # 5. Connect to Biovia Notebook (replaces PLP Component 24)
            nb_client = BioviaNotebookClient(session_token=session_token, mock_mode=self.mock_mode)
            exp = nb_client.query_experiment(experiment_number)
            exp_id = exp.get("id", f"EXP_{experiment_number}")

            # 6. Execute downloads and section creation in isolated staging directory
            sections_summary: List[Dict[str, str]] = []

            with tempfile.TemporaryDirectory() as temp_dir:
                staging_path = Path(staging_dir) if staging_dir else Path(temp_dir)

                # Azure Download (replaces PLP Component 46)
                downloader = AzureFileShareDownloader(mock_mode=self.mock_mode)
                downloaded_paths = downloader.download_selected_files(
                    directory_path=model_meta.base_location,
                    file_names=files_to_download,
                    destination_dir=staging_path
                )

                # Dispatch Sections (replaces PLP Component 53 Subprotocol)
                for file_path in downloaded_paths:
                    title = model_meta.filename_to_title.get(file_path.name, file_path.stem)
                    sec_info = SectionDispatcher.dispatch_file(
                        file_path=file_path,
                        section_title=title,
                        experiment_id=exp_id,
                        client=nb_client
                    )
                    sections_summary.append(sec_info)

            # 7. Commit Notebook Transaction (replaces PLP Component 3)
            nb_client.update_notebook(exp_id)

            duration = round(time.time() - start_time, 3)
            logger.info(f"Pipeline finished successfully in {duration}s. {len(sections_summary)} sections created.")

            return PipelineRunResult(
                success=True,
                experiment_number=experiment_number,
                experiment_id=exp_id,
                files_processed=len(sections_summary),
                sections_created=sections_summary,
                duration_seconds=duration
            )

        except Exception as exc:
            logger.error(f"Pipeline execution failure: {exc}", exc_info=True)
            return PipelineRunResult(
                success=False,
                experiment_number=experiment_number,
                experiment_id="",
                files_processed=0,
                duration_seconds=round(time.time() - start_time, 3),
                error_message=str(exc)
            )
