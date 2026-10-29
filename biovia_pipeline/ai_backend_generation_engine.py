# ai_backend_generation_engine.py

from dataclasses import dataclass


@dataclass
class GeneratedBackendFile:

    file_name: str

    code: str


@dataclass
class BackendGenerationResult:

    workflow_code: GeneratedBackendFile

    router_code: GeneratedBackendFile

    service_code: GeneratedBackendFile

class AIBackendGenerationEngine:

    def __init__(
        self,
        gemini_engine
    ):

        self.gemini_engine = (
            gemini_engine
        )
    def parse_artifact_response(
        self,
        response_text: str
    ):

        code = ""
        summary = ""

        #
        # Extract Summary
        #
        if (
            "SUMMARY START" in response_text
            and
            "SUMMARY END" in response_text
        ):

            code_part = (
                response_text
                .split(
                    "SUMMARY START",
                    1
                )[0]
            )

            summary = (
                response_text
                .split(
                    "SUMMARY START",
                    1
                )[1]
                .split(
                    "SUMMARY END",
                    1
                )[0]
                .strip()
            )

        else:

            code_part = response_text

        #
        # Remove markdown fences
        #
        code = code_part.strip()

        if code.startswith("```"):

            first_newline = code.find("\n")

            if first_newline != -1:
                code = code[first_newline + 1:]

        if code.endswith("```"):
            code = code[:-3]

        code = code.strip()

        return (
            code,
            summary
        )
    def _backend_parameters(
        self,
        context
    ):

        lines = []

        for component in (
            context.repository_knowledge_base.components
        ):

            lines.append(
                f"Component: {component.component_name}"
            )

            lines.append(
                f"Parameters: {component.parameters}"
            )

            lines.append("")

        return "\n".join(
            lines
        )
    def _workflow_summary(
        self,
        workflow
    ):

        lines = []

        for component in (
            workflow.components
        ):

            lines.append(
                f"- {component.component_name}"
            )

        return "\n".join(lines)
    def _repository_summary(
        self,
        repository
    ):

        lines = []

        for component in repository.components:

            lines.append(
                f"Component: {component.component_name}"
            )

            lines.append(
                f"Category: {component.category}"
            )

            lines.append("")
            
            lines.append(
                "MANDATORY IMPORT"
            )

            lines.append(
                component.import_statement
            )

            lines.append("")

            lines.append(
                f"Function: {component.function_name}"
            )

            lines.append(
                f"Parameters: {component.parameters}"
            )

            lines.append("")

            lines.append(
                "Purpose:"
            )

            lines.append(
                component.docstring
            )

            lines.append("")

            lines.append(
                "Usage Example:"
            )

            lines.append(
                component.usage_example
            )

            lines.append("")

        return "\n".join(
            lines
        )  
    def generate(
        self,
        context,
        reconstruction_prompt,
        generation_context
    ) -> BackendGenerationResult:

        workflow = (
            self._generate_workflow(
                context,
                reconstruction_prompt,
                generation_context
            )
        )
        #print(workflow.code)
        workflow_code, workflow_summary = (
            self.parse_artifact_response(
                workflow.code
            )
        )
        workflow.code = workflow_code
        print(50*'=')
        print("Workflow code generated")
        print(50*'=')
        #print(workflow.code)
        # print(50*'=')
        # print(workflow_code)
        # print(50*'=')
        # print(workflow_summary)
        # print(50*'=')
        generation_context.add_summary(

            "workflow",

            workflow_summary
        )
        generation_context_text = (
            generation_context
            .build_prompt_context()
        )
        service = (
            self._generate_service(
                context,
                reconstruction_prompt,
                generation_context_text
            )
        )
        service_code, service_summary = (
            self.parse_artifact_response(
                service.code
            )
        )
        service.code = service_code
        print("Service code generated")
        print(50*'=')
        generation_context.add_summary(

            "service",

            service_summary
        )
        generation_context_text = (
            generation_context
            .build_prompt_context()
        )
        router = (
            self._generate_router(
                context,
                reconstruction_prompt,
                generation_context_text
            )
        )
        router_code, router_summary = (
                    self.parse_artifact_response(
                        router.code
                    )
                )
        router.code = router_code
        print("Router code generated")
        print(50*'=')
        return BackendGenerationResult(

            workflow_code=
                workflow,

            router_code=
                router,

            service_code=
                service
        )
    def _workflow_prompt(
        self,
        context,
        generation_context_text=""
    ):

        workflow = context.stateful_workflow

        repository = context.repository_knowledge_base
        print()
        print("REPOSITORY TYPE:")
        print(type(repository))
        print()
        return f"""
    You are generating ONLY executable Python code and its summary.

    CRITICAL RULES

    1. Return ONLY Python source code.

    2. Do NOT return markdown explanations.

    3. Do NOT return JSON.

    4. Do NOT explain anything.

    5. The first line MUST be a Python import.

    6. Output MUST compile.

    7. Reuse existing repository components.

    8. NEVER generate implementations of repository components.

    9. ONLY generate workflow orchestration logic.

    10. This artifact is generated AFTER the UI.

    11. The generated frontend already exists.

    12. The workflow must support the frontend workflow.

    13. The workflow must NOT implement API endpoints.

    14. The workflow must NOT implement FastAPI routers.

    15. The workflow must NOT implement service layer logic.

    16. The workflow is responsible ONLY for business orchestration.

    ==================================================================

    APPLICATION TYPE

    Interactive XML Import Application

    The workflow is NOT a batch process.

    The user performs actions through the UI.

    Business Flow:

    1. Upload XML

    2. Parse XML

    3. Display available files

    4. User selects files

    5. Import selected files

    The application is interactive.

    The workflow must support user-driven file selection.

    The workflow must NOT automatically import all files after parsing.

    ==================================================================

    BUSINESS WORKFLOW

    Workflow:

    {context.business_workflow.workflow_name}

    Goal:

    {context.business_workflow.business_goal}

    ==================================================================

    AVAILABLE REPOSITORY COMPONENTS

    {self._repository_summary(repository)}

    ==================================================================

    STATEFUL WORKFLOW

    {self._workflow_summary(workflow)}

    ==================================================================

    BACKEND PARAMETERS

    {self._backend_parameters(context)}

    ==================================================================

    PREVIOUSLY GENERATED ARTIFACTS

    {generation_context_text}

    ==================================================================

    WORKFLOW RESPONSIBILITIES

    The workflow layer is responsible for:

    - XML parsing orchestration
    - File discovery orchestration
    - File type determination
    - Selection-based import orchestration
    - Repository component reuse
    - Business process execution
    - Wiring component outputs to component inputs

    The workflow layer is NOT responsible for:

    - FastAPI routes
    - HTTP request handling
    - Dependency injection
    - API response models
    - Service interfaces

    ==================================================================

    WORKFLOW DESIGN RULES

    Generate a workflow class.

    Generate business operations that support the frontend workflow.

    Prefer operations such as:

    - parse_uploaded_xml()
    - import_selected_files_to_eln()

    The workflow must reuse repository components.

    The workflow must NOT create fake repository components.

    The workflow must NOT create placeholder implementations.

    The workflow must contain real orchestration logic.

    The workflow should encapsulate:

    - XML parsing
    - File classification
    - File-type dispatching
    - ELN import orchestration

    ==================================================================

    GENERATE

    workflow.py

    Requirements:

    - Create imports.
    - Create workflow class.
    - Create workflow methods.
    - Create execute() method when appropriate.
    - Wire outputs to inputs.
    - Reuse repository components.
    - Add logging.
    - Add validation.
    - Add error handling.
    - Follow PEP8.

    ==================================================================
    Return exactly in this pormat. DO NOT DEVIATE:
    '''Python
    <python code>
    '''

    SUMMARY START

    What Was Generated:
    ...

    Business Operations Implemented:
    ...

    Repository Components Used:
    ...

    Important Assumptions:
    ...

    Next Artifact Requirements:
    ...

    SUMMARY END

    """
    def _generate_workflow(
        self,
        context,
        reconstruction_prompt,
        generation_context_text=""
    ):

        prompt = (
            self._workflow_prompt(
                context,
                generation_context_text
            )
        )
        #troubleshooting bad backend
        # result = (
        #     self.gemini_engine
        #     .generate_json(
        #         reconstruction_prompt
        #     )
        # )
        result = (
            self.gemini_engine
            .generate(
                prompt
            )
        )
        
        return GeneratedBackendFile(

            file_name=
                "workflow.py",

            code=
                result.generated_text
        )
    def _router_prompt(
        self,
        context,
        generation_context_text=""
    ):

        routes = []

        for contract in (
            context.api_contracts
        ):

            routes.append(
                f"{contract.route}"
            )

        routes_text = "\n".join(
            routes
        )
        repository = (
            context.repository_knowledge_base
        )

        lines = []

        lines.append(
            "AVAILABLE REPOSITORY COMPONENTS"
        )

        lines.append("")

        for component in (
            repository.components
        ):

            lines.append(
                f"Component: {component.component_name}"
            )

            lines.append(
                f"Import: {component.import_statement}"
            )

            lines.append(
                f"Parameters: {component.parameters}"
            )

            lines.append("")

        repository_text = "\n".join(
            lines
        )

        return f"""
    You are generating ONLY executable Python code and its summary.

    CRITICAL RULES

    1. Return ONLY Python source code.

    2. Do NOT return markdown.

    3. Do NOT return JSON.

    4. Do NOT explain anything.

    5. Output MUST compile.

    6. The first line MUST be a Python import.

    7. Generate a complete FastAPI router.

    8. This artifact is generated AFTER service.py.

    9. The service layer already exists.

    10. Import and use the concrete service implementation.

    11. Do NOT generate service interfaces.

    12. Do NOT generate abstract service classes.

    13. Do NOT generate repository component implementations.

    14. Do NOT generate workflow implementations.

    15. Router must call service layer methods only.

    16. Router must NOT contain business logic.

    17. Router must NOT contain workflow orchestration.

    18. Router must NOT duplicate logic already implemented in service.py or workflow.py.

    ====================================================================

    APPLICATION TYPE

    Interactive XML Import Application

    User workflow:

    1. Upload XML

    2. Parse XML

    3. Display filenames found in XML

    4. User selects files

    5. Import selected files into ELN

    This is a user-driven interactive workflow.

    The application does NOT automatically import files after parsing.

    The user must review and select files before import.

    ====================================================================

    BUSINESS WORKFLOW

    Workflow:

    {context.business_workflow.workflow_name}

    Goal:

    {context.business_workflow.business_goal}

    ====================================================================

    AVAILABLE REPOSITORY COMPONENTS

    {repository_text}

    ====================================================================

    PREVIOUSLY GENERATED ARTIFACTS

    {generation_context_text}

    ====================================================================

    CONTEXT USAGE RULES

    The above artifacts have already been generated.

    Treat the previously generated artifact summaries as the source of truth.

    The router MUST remain consistent with all previously generated artifacts.

    Read and use all available summaries before generating code.

    Use previous summaries to identify:

    - Existing business operations
    - Existing workflow methods
    - Existing service methods
    - Existing API expectations from the UI
    - Existing assumptions and implementation decisions

    If a workflow summary defines workflow methods:

    - Preserve those method names.
    - Do not invent alternatives.

    If a service summary defines service methods:

    - Call those methods.
    - Do not redefine them.
    - Do not generate competing implementations.

    If a UI summary defines API dependencies:

    - Generate APIs that satisfy those dependencies.
    - Prefer previously generated endpoint names.

    Consistency with previous artifacts is more important than creating new names.

    Do not create new APIs, classes, or contracts when an equivalent already exists in previous summaries.

    ====================================================================

    ROUTER RESPONSIBILITIES

    The router is responsible for:

    - API endpoints
    - Request models
    - Response models
    - Request validation
    - Dependency injection
    - Error handling
    - Calling service layer methods

    The router is NOT responsible for:

    - XML parsing implementation
    - Repository component orchestration
    - Workflow implementation
    - Business logic
    - File classification
    ====================================================================
    Return exactly in this pormat. DO NOT DEVIATE:
    '''Python
    <python code>
    '''
    SUMMARY START

    What Was Generated:
    ...

    API Endpoints:
    ...

    Request Models:
    ...

    Response Models:
    ...

    Service Methods Called:
    ...

    Dependency Injection Strategy:
    ...

    HTTP Status Codes Used:
    ...

    Important Assumptions:
    ...

    Frontend Requirements Satisfied:
    ...

    Design Decisions:
    ...

    Next Artifact Requirements:
    ...

    SUMMARY END

    """
    def _generate_router(
        self,
        context,
        reconstruction_prompt,
        generation_context_text=""
    ):

        prompt = (
            self._router_prompt(
                context,
                generation_context_text
            )
        )

        # result = (
        #     self.gemini_engine
        #     .generate(
        #         reconstruction_prompt
        #     )
        # )
        result = (
            self.gemini_engine
            .generate(
                prompt
            )
        )
        return GeneratedBackendFile(

            file_name=
                "router.py",

            code=
                result.generated_text
        )
    def _service_prompt(
        self,
        context,
        generation_context_text=""
    ):

        workflow = (
            context.stateful_workflow
        )

        repository = (
            context.repository_knowledge_base
        )

        lines = []

        lines.append(
            "AVAILABLE REPOSITORY COMPONENTS"
        )

        lines.append("")

        for component in (
            repository.components
        ):

            lines.append(
                f"Component: {component.component_name}"
            )

            lines.append(
                f"Import: {component.import_statement}"
            )

            lines.append(
                f"Parameters: {component.parameters}"
            )

            lines.append("")

        repository_text = "\n".join(
            lines
        )

        workflow_lines = []

        for component in (
            workflow.components
        ):

            workflow_lines.append(
                f"- {component.component_name}"
            )

        workflow_text = "\n".join(
            workflow_lines
        )

        return f"""
    You are generating ONLY executable Python code and its summary.

    CRITICAL RULES

    1. Return ONLY Python source code.

    2. Do NOT return markdown explanations.

    3. Do NOT return JSON.

    4. Do NOT explain anything.

    5. Output MUST compile.

    6. The first line MUST be a Python import.

    7. This artifact is generated AFTER workflow.py.

    8. The workflow layer already exists.

    9. Import and use the concrete workflow implementation.

    10. Reuse repository components ONLY through the workflow layer.

    11. NEVER reimplement repository components.

    12. NEVER duplicate workflow logic.

    13. Generate ONLY business-service code.

    14. Service layer must call workflow layer.

    15. Service layer must NOT contain repository-component orchestration.

    ====================================================================

    APPLICATION TYPE

    Interactive XML Import Application

    The user will:

    1. Upload XML

    2. Parse XML

    3. Review filenames

    4. Select files

    5. Import selected files

    The application is interactive.

    The service layer must support user-driven file selection.

    The service layer must NOT automatically import files after parsing.

    ====================================================================

    BUSINESS WORKFLOW

    Workflow:

    {context.business_workflow.workflow_name}

    Goal:

    {context.business_workflow.business_goal}

    ====================================================================

    AVAILABLE REPOSITORY COMPONENTS

    {repository_text}

    ====================================================================

    STATEFUL WORKFLOW

    {workflow_text}

    ====================================================================

    PREVIOUSLY GENERATED ARTIFACTS

    {generation_context_text}

    ====================================================================

    CONTEXT USAGE RULES

    The above artifacts have already been generated.

    Use them as the source of truth.

    The service implementation must be consistent with all previously generated artifacts.

    Reuse business operations already identified in previous summaries.

    Do not redefine existing responsibilities.

    Do not generate methods that conflict with previous artifacts.

    If a workflow summary defines workflow methods, use those methods.

    If a UI summary defines expected business operations, ensure the service layer supports those operations.

    Prefer consistency with previous summaries over inventing new APIs, classes, or method names.

    ====================================================================

    SERVICE RESPONSIBILITIES

    The service layer is responsible for:

    - Business operations
    - Validation
    - Logging
    - Error handling
    - Calling workflow layer methods
    - Returning structured results

    The service layer is NOT responsible for:

    - FastAPI routes
    - Request models
    - Response models
    - Repository component orchestration
    - XML parsing implementation
    - File type dispatching
    - ELN section creation logic

    Those responsibilities belong to workflow.py.

    ====================================================================

    SERVICE DESIGN RULES

    Generate:

    class XMLImportService

    Import the workflow implementation.

    Create thin business-oriented methods.

    Prefer methods such as:

    - parse_uploaded_xml()

    - import_files_to_eln()

    These methods should:

    - Validate inputs
    - Call workflow methods
    - Handle exceptions
    - Add logging
    - Return structured business results

    Do NOT generate methods that directly call:

    - add_pdf_section()
    - add_excel_section()
    - add_word_section()
    - add_image_section()
    - add_powerpoint_section()
    - add_file_attachment_section()

    Those calls must remain inside workflow.py.

    ====================================================================

    GENERATE

    service.py

    Requirements:

    - Create imports.
    - Create XMLImportService.
    - Import workflow.py.
    - Call workflow methods.
    - Add logging.
    - Add validation.
    - Add exception handling.
    - Return structured responses.
    - Follow PEP8.

    ====================================================================
    Return exactly in this pormat. DO NOT DEVIATE:
    '''Python
    <python code>
    '''
    SUMMARY START
    What Was Generated:
    ...

    Service Methods:
    ...

    Workflow Dependencies:
    ...

    Important Assumptions:
    ...

    Next Artifact Requirements:
    ...

    SUMMARY END

    """
    def _generate_service(
        self,
        context,
        reconstruction_prompt,
        generation_context_text=""
    ):

        prompt = (
            self._service_prompt(
                context,
                generation_context_text
            )
        )

        # result = (
        #     self.gemini_engine
        #     .generate_json(
        #         reconstruction_prompt
        #     )
        # )
        result = (
            self.gemini_engine
            .generate(
                prompt
            )
        )
        return GeneratedBackendFile(

            file_name=
                "service.py",

            code=
                result.generated_text
        )