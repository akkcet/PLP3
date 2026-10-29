# app_reconstruction_agent_v2.py

from dataclasses import dataclass
import os
from pathlib import Path
from typing import List, Optional

from .protocol_migration_engine import (
    analyze_protocol_xml
)
from .workflow_api_binding_builder import (
    WorkflowApiBindingBuilder
)
from .layout_classifier import (
    LayoutClassifier
)

from .screen_flow_builder import (
    ScreenFlowBuilder
)

from .workflow_label_extractor import (
    WorkflowLabelExtractor
)

from .repository_component_binding_engine import (
    RepositoryComponentBindingEngine
)

from .workflow_state_mapper import (
    WorkflowStateMapper
)

from .application_blueprint_builder import (
    ApplicationBlueprintBuilder
)

from .backend_workflow_generator_v2 import (
    BackendWorkflowGeneratorV2
)

from .react_app_generator_v3 import (
    ReactAppGeneratorV3
)

from .api_contract_generator import (
    APIContractGenerator
)
from .business_flow_interpreter import (
    BusinessFlowInterpreter
)

from .screen_to_page_mapper import (
    ScreenToPageMapper
)

from .component_parameter_resolver import (
    ComponentParameterResolver
)

from .component_parameter_to_backend_mapper import (
    ComponentParameterToBackendMapper
)

from .component_parameter_to_workflow_mapper import (
    ComponentParameterToWorkflowMapper
)

from .application_runtime_builder import (
    ApplicationRuntimeBuilder
)

from .full_project_scaffolder import (
    FullProjectScaffolder
)

from .component_library_generator import (
    ComponentLibraryGenerator
)
from .missing_component_generator import (
    MissingComponentGenerator
)

from .repository_self_learning_engine import (
    RepositorySelfLearningEngine
)

from .component_metadata_registry import (
    ComponentMetadataRegistry
)
from .missing_component_generator import (
    MissingComponentGenerator,
    MissingComponent
)
from .repository_self_learning_engine import (
    RepositorySelfLearningEngine
)

from .registry_synchronizer import (
    RegistrySynchronizer
)
from .pipeline_validation_engine import (
    PipelineValidationEngine
)
from .reconstruction_diagnostics import (
    ReconstructionDiagnosticsEngine
)
from .pattern_similarity_engine import (
    PatternSimilarityEngine
)
from .component_pattern_mining_engine import (
    ComponentPatternMiningEngine
)

from .pattern_reconstruction_assistant import (
    PatternReconstructionAssistant
)
from .workflow_template_engine import (
    WorkflowTemplateEngine,
    WorkflowTemplateMatcher,
    WorkflowTemplateReconstructor,
    WorkflowTemplateExporter
)
from .workflow_template_engine import (
    WorkflowTemplateEngine
)

from .template_reconstruction_engine import (
    TemplateReconstructionEngine
)

from .template_completion_engine import (
    TemplateCompletionEngine
)
from .reconstruction_knowledge_graph import (
    ReconstructionKnowledgeGraph,
    KnowledgeGraphExporter
)
from .ai_reconstruction_engine import (
    AIReconstructionEngine
)
from .reconstruction_context_validator import (
    ReconstructionContextValidator
)
from .ai_application_reconstruction_engine import (
    AIApplicationReconstructionEngine
)
from .ai_prompt_builder import (
    AIPromptBuilder
)
from .gemini_reconstruction_engine import (
    GeminiReconstructionEngine
)
from .ai_ui_generation_engine import (
    AIUIGenerationEngine
)

from .ai_ui_exporter import (
    AIUIExporter
)
from .ai_backend_generation_engine import (
    AIBackendGenerationEngine
)

from .ai_backend_exporter import (
    AIBackendExporter
)
from .ai_missing_component_engine import (
    AIMissingComponentEngine,
    AIMissingComponentRequest
)

from .ai_missing_component_exporter import (
    AIMissingComponentExporter
)

from .missing_component_context_builder import (
    MissingComponentContextBuilder
)
from .ai_application_review_engine import (
    AIApplicationReviewEngine
)

from .ai_review_exporter import (
    AIReviewExporter
)
from .ai_auto_fix_engine import (
    AIAutoFixEngine
)

from .ai_auto_fix_exporter import (
    AutoFixExporter
)
from .ai_code_merge_engine import (
    AICodeMergeEngine
)
from .ai_component_confidence_engine import (
    AIComponentConfidenceEngine
)
from .component_test_generator import (
    ComponentTestGenerator
)

from .component_test_runner import (
    ComponentTestRunner
)

from .component_quality_score import (
    ComponentQualityScore
)

from .component_refinement_engine import (
    ComponentRefinementEngine
)

from .component_refinement_loop import (
    ComponentRefinementLoop
)
from .component_similarity_engine import (
    ComponentSimilarityEngine
)
from .repository_context_builder import (
    RepositoryContextBuilder,
    RepositoryContextExporter
)
from .generated_application_validator import (
    GeneratedApplicationValidator
)
from .repository_analysis_engine import (
    RepositoryAnalysisEngine
)

from .repository_knowledge_exporter import (
    RepositoryKnowledgeExporter
)
from .repository_knowledge_builder import (
    RepositoryKnowledgeBuilder
)

from .repository_knowledge_prompt_builder import (
    RepositoryKnowledgePromptBuilder
)
from .generation_context_engine import (
    GenerationContextEngine
)

from .generation_summary_builder import (
    GenerationSummaryBuilder
)

from .ai_response_parser import (
    AIResponseParser
)
# ============================================================
# INPUT MODELS
# ============================================================
@dataclass
class ReconstructionContext:

    protocol_analysis: object
    screenshot_analysis: object
    business_workflow: object
    binding_result: object
    backend_parameters: object
    workflow_bindings: object
    stateful_workflow: object
    page_graph: object
    application_blueprint: object
    output_dir: str
    api_contracts: object
    workflow_api_bindings: object
    pattern_catalog: object
    template_catalog : object
    template_matches : object
    #template_reconstruction : object
    template_missing : object
    #ai_enhancement: object
    # repository_context: object
    repository_knowledge_base: object
    ui_pattern: str
    component_confidence: object = None
    
    

@dataclass
class ReconstructionRequest:

    protocol_xml: str

    screenshot_descriptions: Optional[
        List[str]
    ] = None

    business_description: Optional[
        str
    ] = None

    output_dir: str = "./generated_apps"
    ui_pattern: str = "wizard"

class ReconstructionContextBuilder:

    def build(
        self,
        protocol_analysis,
        screenshot_analysis,
        business_workflow,
        binding_result,
        backend_parameters,
        workflow_bindings,
        stateful_workflow,
        page_graph,
        application_blueprint,
        api_contracts,
        output_dir,
        workflow_api_bindings,
        pattern_catalog,
        template_catalog,
        template_matches,
        #template_reconstruction,
        template_missing,
        #ai_enhancement,
        repository_knowledge_base,
        ui_pattern
        
    ):

        return ReconstructionContext(

            protocol_analysis=
                protocol_analysis,

            screenshot_analysis=
                screenshot_analysis,

            business_workflow=
                business_workflow,

            binding_result=
                binding_result,

            backend_parameters=
                backend_parameters,

            workflow_bindings=
                workflow_bindings,

            stateful_workflow=
                stateful_workflow,

            page_graph=
                page_graph,

            application_blueprint=
                application_blueprint,

            output_dir=
                output_dir,
            workflow_api_bindings=
                workflow_api_bindings,

            api_contracts=
                api_contracts,

            pattern_catalog=
                pattern_catalog,
            template_catalog=
                template_catalog,

            template_matches=
                template_matches,

            # template_reconstruction=
            #     template_reconstruction,

            template_missing=
                template_missing,
            repository_knowledge_base=
                repository_knowledge_base,
            ui_pattern=
                ui_pattern,
            # ai_enhancement=
            #     ai_enhancement,
        )
@dataclass
class ReconstructionResult:

    application_name: str

    generated_path: str

    mapped_components: int

    missing_components: int

    pages_generated: int

    workflow_generated: bool


# ============================================================
# MAIN AGENT
# ============================================================

class AppReconstructionAgentV2:

    def __init__(self):
        self.workflow_api_binding_builder = (
            WorkflowApiBindingBuilder()
        )
        self.layout_classifier = (
            LayoutClassifier()
        )

        self.screen_flow_builder = (
            ScreenFlowBuilder()
        )

        self.workflow_extractor = (
            WorkflowLabelExtractor()
        )

        self.binding_engine = (
            RepositoryComponentBindingEngine()
        )

        self.state_mapper = (
            WorkflowStateMapper()
        )

        self.blueprint_builder = (
            ApplicationBlueprintBuilder()
        )

        self.react_generator = (
            ReactAppGeneratorV3()
        )

        self.backend_generator = (
            BackendWorkflowGeneratorV2()
        )

        self.api_generator = (
            APIContractGenerator()
        )
        self.business_flow_interpreter = (
            BusinessFlowInterpreter()
        )

        self.screen_to_page_mapper = (
            ScreenToPageMapper()
        )

        self.parameter_resolver = (
            ComponentParameterResolver()
        )

        self.backend_parameter_mapper = (
            ComponentParameterToBackendMapper()
        )

        self.workflow_parameter_mapper = (
            ComponentParameterToWorkflowMapper()
        )

        self.runtime_builder = (
            ApplicationRuntimeBuilder()
        )

        self.project_scaffolder = (
            FullProjectScaffolder()
        )

        self.component_library_generator = (
            ComponentLibraryGenerator()
        )

        self.context_builder = (
            ReconstructionContextBuilder()
        )
        self.missing_component_generator = (
            MissingComponentGenerator()
        )

        self.self_learning_engine = (
            RepositorySelfLearningEngine()
        )

        self.metadata_registry = (
            ComponentMetadataRegistry()
        )
        

        self.registry_synchronizer = (
            RegistrySynchronizer()
        )
        self.pipeline_validator = (
            PipelineValidationEngine()
        )
        self.diagnostics_engine = (
            ReconstructionDiagnosticsEngine()
        )
        self.pattern_mining_engine = (
            ComponentPatternMiningEngine()
        )

        self.pattern_reconstruction_assistant = (
            PatternReconstructionAssistant()
        )
        self.workflow_template_engine = (
            WorkflowTemplateEngine()
        )

        self.workflow_template_matcher = (
            WorkflowTemplateMatcher()
        )

        self.workflow_template_reconstructor = (
            WorkflowTemplateReconstructor()
        )

        self.workflow_template_exporter = (
            WorkflowTemplateExporter()
        )
        self.template_reconstruction_engine = (
            TemplateReconstructionEngine()
        )

        self.template_completion_engine = (
            TemplateCompletionEngine()
        )
        self.knowledge_graph = (
            ReconstructionKnowledgeGraph()
        )

        self.graph_exporter = (
            KnowledgeGraphExporter()
        )
        self.ai_reconstruction_engine = (
            AIReconstructionEngine()
        )
        self.context_validator = (
            ReconstructionContextValidator()
        )
        self.ai_application_reconstruction_engine = (
            AIApplicationReconstructionEngine()
        )
        self.ai_prompt_builder = (
            AIPromptBuilder()
        )
        self.gemini_engine = (
            GeminiReconstructionEngine(
                project_id=os.getenv(
            "GOOGLE_CLOUD_PROJECT"
            ),
            )
        )
        self.ai_ui_generation_engine = (
            AIUIGenerationEngine(
                self.gemini_engine
            )
        )

        self.ai_ui_exporter = (
            AIUIExporter()
        )
        self.ai_backend_generation_engine = (
            AIBackendGenerationEngine(
                self.gemini_engine
            )
        )

        self.ai_backend_exporter = (
            AIBackendExporter()
        )
        self.ai_missing_component_engine = (
            AIMissingComponentEngine(
                self.gemini_engine
            )
        )
        self.component_similarity_engine = (
            ComponentSimilarityEngine()
        )
        self.ai_missing_component_exporter = (
            AIMissingComponentExporter()
        )

        self.missing_component_context_builder = (
            MissingComponentContextBuilder()
        )
        self.ai_review_engine = (
            AIApplicationReviewEngine()
        )

        self.ai_review_exporter = (
            AIReviewExporter()
        )
        self.ai_auto_fix_engine = (
            AIAutoFixEngine()
        )

        self.auto_fix_exporter = (
            AutoFixExporter()
        )
        self.ai_code_merge_engine = (
            AICodeMergeEngine()
        )
        self.confidence_engine = (
            AIComponentConfidenceEngine()
        )
        self.component_test_generator = (
            ComponentTestGenerator()
        )

        self.component_test_runner = (
            ComponentTestRunner()
        )

        self.component_quality_score = (
            ComponentQualityScore()
        )

        self.refinement_engine = (
            ComponentRefinementEngine()
        )

        self.refinement_loop = (
            ComponentRefinementLoop()
        )
        self.repository_context_builder = (
            RepositoryContextBuilder()
        )

        self.repository_context_exporter = (
            RepositoryContextExporter()
        )
        self.generated_application_validator = (
            GeneratedApplicationValidator()
        )
        self.repository_analysis_engine = (
            RepositoryAnalysisEngine()
        )

        self.repository_knowledge_exporter = (
            RepositoryKnowledgeExporter()
        )
        self.repository_knowledge_builder = (
            RepositoryKnowledgeBuilder()
        )

        self.repository_knowledge_prompt_builder = (
            RepositoryKnowledgePromptBuilder()
        )
        

        self.generation_summary_builder = (
            GenerationSummaryBuilder()
        )
        self.generation_context = (
            GenerationContextEngine()
        )

        self.ai_response_parser = (
            AIResponseParser()
        )
    # ==========
    # ==============================================
    # PUBLIC ENTRYPOINT
    # ========================================================

    def generate_application(
        self,
        request: ReconstructionRequest
    ) -> ReconstructionResult:

        print()
        print("=" * 80)
        print("APPLICATION RECONSTRUCTION")
        print("=" * 80)
        print()

        # ====================================================
        # STEP 1
        # Analyze Protocol
        # ====================================================

        protocol_analysis = (
            analyze_protocol_xml(
                request.protocol_xml
            )
        )

        app_name = (

            getattr(
                protocol_analysis,
                "protocol_name",
                None
            )

            or

            "GeneratedApplication"
        )

        target = (

            Path(
                request.output_dir
            )

            /

            self._safe_name(
                app_name
            )
        )

        target.mkdir(
            parents=True,
            exist_ok=True
        )
        #####################
        
        # ====================================================
        # STEP 2
        # Workflow Labels
        # ====================================================

        workflow_labels = (

            self._collect_labels(

                protocol_analysis,

                request
            )
        )

        workflow_definition = (

            self.workflow_extractor
            .extract(
                workflow_labels
            )
        )

        # ====================================================
        # STEP 3
        # Layout
        # ====================================================

        layout = (
            self.layout_classifier.classify(

                "\n".join(
                    workflow_labels
                )
            )
        )

        # ====================================================
        # STEP 4
        # Screen Flow
        # ====================================================

        screenshot_analysis = (
            self._mock_ui_analysis(
                workflow_labels
            )
        )

        screen_flow_graph = (

            self.screen_flow_builder.build(

                protocol_analysis,

                screenshot_analysis
            )
        )

        # ====================================================
        # STEP 5
        # Component Binding
        # ====================================================

        binding_result = (

            self.binding_engine.bind(
                protocol_analysis
            )
        )

        # ====================================================
        # STEP 5.1
        # Repository Context to build the components catalog
        # ====================================================
        
        repository_knowledge_base = (
            self.repository_analysis_engine
            .analyze()
        )
        self.repository_knowledge_exporter.save(
            repository_knowledge_base,
            str(target)
        )
        repository_summary = (

            self.repository_knowledge_prompt_builder
            .build(
                repository_knowledge_base
            )
        )
        # ====================================================
        # STEP 6
        # Business Workflow
        # ====================================================

        business_workflow = (

            self.business_flow_interpreter
            .interpret(

                request.business_description
                or ""
            )
        )

        # ====================================================
        # STEP 7
        # Page Graph
        # ====================================================

        page_graph = (

            self.screen_to_page_mapper.build(

                business_workflow,

                screen_flow_graph,
                request.ui_pattern
            )
        )
        print()
        print("=" * 80)
        print("PAGE GRAPH BEFORE CONTEXT")
        print("=" * 80)

        for page in page_graph.pages:

            print(
                page
            )

        print()
        print(
            "UI Pattern:",
            request.ui_pattern
        )
        # ====================================================
        # STEP 8
        # Component Parameters
        # ====================================================

        parameter_result = (

            self.parameter_resolver
            .resolve(
                protocol_analysis
            )
        )

        # ====================================================
        # STEP 9
        # Backend Parameters
        # ====================================================

        backend_parameters = (

            self.backend_parameter_mapper
            .map_all(

                binding_result,

                parameter_result
            )
        )

        # ====================================================
        # STEP 10
        # Stateful Workflow
        # ====================================================

        stateful_workflow = (

            self.state_mapper.build(
                binding_result
            )
        )
        
        #
        # STEP 10.5
        # Pattern Mining
        #
        pattern_catalog = (

            self.pattern_mining_engine
            .mine(
                [
                    stateful_workflow
                ]
            )
        )
        template_catalog = (

            self.workflow_template_engine
            .build(
                pattern_catalog
            )
        )
        # template_reconstruction = (

        #     self.template_reconstruction_engine
        #     .reconstruct(

        #         stateful_workflow,

        #         template_catalog
        #     )
        # )
        # template_missing = (

        #     self.template_completion_engine
        #     .complete(

        #         stateful_workflow,

        #         template_reconstruction
        #     )
        # )
        template_matches = (

            self.workflow_template_matcher
            .find_matches(

                stateful_workflow,

                template_catalog
            )
        )
        best_match = (
            template_matches[0]
            if template_matches
            else None
        )

        template_missing = []

        if best_match:

            template_missing = (
                self.template_completion_engine
                .complete(
                    stateful_workflow,
                    best_match
                )
            )
        # ====================================================
        # STEP 11
        # Workflow Bindings
        # ====================================================

        workflow_bindings = (

            self.workflow_parameter_mapper
            .build(
                stateful_workflow
            )
        )

        # ====================================================
        # STEP 11.5
        # API Contracts
        # ====================================================

        contracts = (
            self.api_generator.generate(
                stateful_workflow
            )
        )
        print(50*'=')
        print('API CONTRCTS')
        print(contracts)
        # ====================================================
        # STEP 11.6
        # Workflow API Bindings
        # ====================================================

        workflow_api_bindings = (

            self.workflow_api_binding_builder
            .build(

                page_graph,

                contracts,

                stateful_workflow
            )
        )

        # ====================================================
        # STEP 12
        # Application Blueprint
        # ====================================================

        blueprint = (

            self.blueprint_builder.build(

                protocol_analysis,

                screen_flow_graph
            )
        )
        
        
        # ====================================================
        # STEP 13
        # Build Reconstruction Context
        # ====================================================

        context = (

            self.context_builder.build(

                protocol_analysis=
                    protocol_analysis,

                screenshot_analysis=
                    screenshot_analysis,

                business_workflow=
                    business_workflow,

                binding_result=
                    binding_result,

                backend_parameters=
                    backend_parameters,

                workflow_bindings=
                    workflow_bindings,

                workflow_api_bindings=
                    workflow_api_bindings,

                stateful_workflow=
                    stateful_workflow,

                page_graph=
                    page_graph,

                application_blueprint=
                    blueprint,

                api_contracts=
                    contracts,
                pattern_catalog=
                    pattern_catalog,
                template_catalog=
                    template_catalog,

                template_matches=
                    template_matches,

                # template_reconstruction=
                #     template_reconstruction,

                template_missing=
                    template_missing,
                repository_knowledge_base=
                    repository_knowledge_base ,
                # ai_enhancement=
                #     ai_enhancement,
                output_dir=
                    str(target),
                    ui_pattern=
                    request.ui_pattern
            )
        )
        #######################
        ai_result = (
        
            self.ai_reconstruction_engine
            .analyze(
                context
            )
        )

        self.ai_reconstruction_engine.print_result(
            ai_result
        )

        # ====================================================
        # STEP 12.9
        # Knowledge Graph
        # ====================================================

        self.knowledge_graph.from_protocol(
            protocol_analysis
        )

        self.knowledge_graph.from_business_workflow(
            business_workflow
        )

        self.knowledge_graph.from_templates(
            template_catalog
        )

        self.knowledge_graph.from_stateful_workflow(
            stateful_workflow
        )

        self.graph_exporter.save(

            self.knowledge_graph.graph,

            str(
                target /
                "knowledge_graph.json"
            )
        )

        ai_enhancement = (

            self.ai_application_reconstruction_engine
            .enhance(
                context
            )
        )
        merge_result = (

            self.ai_code_merge_engine
            .merge(

                blueprint,

                ai_enhancement
            )
        )

        blueprint = (
            merge_result
            .enhanced_blueprint
        )
        self.ai_code_merge_engine.print_report(
            merge_result
        )

        context_validation = (

            self.context_validator
            .validate(
                context
            )
        )

        self.context_validator.print_report(
            context_validation
        )

        self.context_validator.ensure_valid(
            context_validation
        )
        reconstruction_prompt = (

            self.ai_prompt_builder
            .build(
                context
            )
        )

        self.ai_prompt_builder.print_prompt(
            reconstruction_prompt
        )
        print("Calling Gemini Reconstruction...")
        # commenting out coz it hits TPM quota and fails for now. Uncomment when quota is available
        # gemini_result = (

        #     self.gemini_engine.generate(
        #         reconstruction_prompt
        #     )
        # )
        # print(50*('='))
        # print('GEMINI RESULT: ')
        # print(gemini_result)
        # optimized_request = (

        #     self.ai_request_optimizer
        #     .build(

        #         context,

        #         reconstruction_prompt
        #     )
        # )
        # gemini_result = (

        #     self.gemini_engine
        #     .generate_optimized(
        #         optimized_request
        #     )
        # )
        # split_result = (

        #     self.ai_response_splitter
        #     .split(
        #         gemini_result.generated_text
        #     )
        # )
        print("Gemini Reconstruction Complete")
        print("Generating AI UI...")
        generated_ui = (

            self.ai_ui_generation_engine
            .generate(
                context,
                reconstruction_prompt
            )
        )
        # self.generation_context.add_summary(
        #     generated_ui.summary
        # )
        generation_context_text = generated_ui.summary
        self.generation_context.add_summary(

            "ui",

            generated_ui.summary
        )
        print()
        print("=" * 80)
        print("AI GENERATED PAGES")
        print("AI GENERATED SUMMARY")
        print(generated_ui.summary)
        print("=" * 80)
        
        for page in generated_ui.pages:
            print(page.page_name)
        print("AI UI Complete")
        self.ai_ui_exporter.save(

            generated_ui,

            str(
                target
                /
                "frontend"
                /
                "src"
                /
                "pages"
            )
        )
      
        print("Generating AI Backend...")
        
        backend_generation = (

            self.ai_backend_generation_engine
            .generate(

                context,
                reconstruction_prompt,
                self.generation_context
            )
        )
        print("AI Backend Complete")
        self.ai_backend_exporter.save(

            backend_generation,

            str(
                target /
                "backend"
            )
        )
        ############################
        

        # ====================================================
        # STEP 13.2
        # AI Missing Component Generation
        # ====================================================
        print("AI missing components started...")
        print()
        print("=" * 80)
        print("UI COMPONENTS")
        print("=" * 80)

        for component in (
            protocol_analysis.ui_missing_components
        ):
            print(component)

        print()
        print("=" * 80)
        print("BACKEND COMPONENTS")
        print("=" * 80)

        for component in (
            protocol_analysis.backend_missing_components
        ):
            print(component)
        # for component_name in (
        #     protocol_analysis.backend_missing_components
        # ):
        unique_backend_components = sorted(
            set(
                protocol_analysis.backend_missing_components
            )
        )

        for component_name in (
            unique_backend_components
        ):
        # for component_name in (
        #     binding_result.missing_components
        # ):
            print("AI missing components similarity analysis started...")
            similar = (
                self.component_similarity_engine
                .top_matches(
                    component_name,
                    self.metadata_registry
                )
            )
            print("AI missing components similarity analysis ended...")
            print("AI missing components building knowledge context started...")
            knowledge_context = (
                self.missing_component_context_builder
                .build(
                    context,
                    component_name
                )
            )
            print("AI missing components building knowledge context ended...")
            print("AI missing components building ...")
            ai_component = (

                self.ai_missing_component_engine
                .generate(

                    AIMissingComponentRequest(

                        component_name=
                            component_name,

                        component_type=
                            "Unknown",

                        component_xml="",

                        pilotscript="",

                        business_description=
                            request.business_description
                            or "",

                        similar_components=
                            similar,

                        knowledge_context=
                            knowledge_context
                    )
                )
            )

            generated_test = (

                self.component_test_generator
                .generate(
                    ai_component
                )
            )

            test_path = (

                self.component_test_generator
                .save(
                    generated_test,
                    str(
                        target
                        /
                        "generated_tests"
                    )
                )
            )

            test_result = (

                self.component_test_runner
                .run(
                    test_path
                )
            )

            quality_score = (

                self.component_quality_score
                .calculate(
                    test_result
                )
            )

            if not test_result["passed"]:

                refinement_result = (

                    self.refinement_loop
                    .run(

                        ai_component,

                        self.component_test_generator,

                        self.component_test_runner,

                        self.refinement_engine
                    )
                )

                ai_component = (
                    refinement_result[
                        "component"
                    ]
                )

            ai_component.quality_score = (
                quality_score
            )

            self.ai_missing_component_exporter.save(

                ai_component,

                str(
                    target
                    /
                    "generated_components"
                )
            )

            self.self_learning_engine.register_generated_component(

                ai_component,

                self.metadata_registry
            )
        
        ######################
        ##VALIDATION ENGINE##
        ######################
        validation_report = (

            self.pipeline_validator.validate(

                protocol_analysis,

                binding_result,

                parameter_result,

                backend_parameters,

                workflow_bindings,

                stateful_workflow,

                page_graph,

                blueprint,

                contracts
            )
        )
        self.pipeline_validator.print_report(
            validation_report
        )
        self.pipeline_validator.ensure_valid(
            validation_report
        )
        diagnostics = (

            self.diagnostics_engine.build(

                context,

                validation_report
            )
        )

        self.diagnostics_engine.print_report(
            diagnostics
        )

        self.diagnostics_engine.save(

            diagnostics,

            str(target)
        )
        # ====================================================
        # STEP 14
        # Runtime Generation
        # ====================================================

        self.runtime_builder.build(

            context,

            self.react_generator,

            self.backend_generator,

            self.project_scaffolder,

            self.component_library_generator
        )

        print()
        print("=" * 80)
        print("APPLICATION GENERATED")
        print("=" * 80)
        print()
        review = (

            self.ai_review_engine
            .review(
                context
            )
        )
        auto_fix_result = (

            self.ai_auto_fix_engine
            .apply(

                review,

                blueprint
            )
        )
        self.ai_auto_fix_engine.print_result(
            auto_fix_result
        )
        self.auto_fix_exporter.save(
            auto_fix_result,
            str(target)
        )
        self.ai_review_engine.print_review(
            review
        )

        self.ai_review_exporter.save(

            review,

            str(target)
        )
        validation = (

            self.generated_application_validator
            .validate(
                str(target)
            )
        )

        self.generated_application_validator.print_report(
            validation
        )
        # ====================================================
        # STEP 15
        # RETURN RESULT
        # ====================================================

        return ReconstructionResult(

            application_name=
                app_name,

            generated_path=
                str(target),

            mapped_components=
                len(
                    binding_result
                    .bound_components
                ),

            missing_components=
                len(
                    binding_result
                    .missing_components
                ),

            pages_generated=
                len(
                    blueprint.pages
                ),

            workflow_generated=
                True
        )

    # ========================================================
    # HELPERS
    # ========================================================

    def _collect_labels(
        self,
        protocol_analysis,
        request
    ):

        labels = []

        #
        # Screenshot descriptions
        #
        if request.screenshot_descriptions:

            labels.extend(
                request.screenshot_descriptions
            )

        #
        # Business description
        #
        if request.business_description:

            labels.append(
                request.business_description
            )

        #
        # Protocol component names
        #
        for node in protocol_analysis.nodes:

            if getattr(
                node,
                "visual_name",
                None
            ):

                labels.append(
                    node.visual_name
                )

        return labels

    # ========================================================
    # TEMP UI BUILD
    # ========================================================

    def _mock_ui_analysis(
        self,
        labels
    ):

        class Widget:

            def __init__(
                self,
                widget_type
            ):
                self.widget_type = (
                    widget_type
                )

        class Screen:

            def __init__(
                self
            ):
                self.widgets = []

        class Analysis:

            def __init__(
                self
            ):
                self.screens = []

        analysis = Analysis()

        screen = Screen()

        for label in labels:

            lower = (
                str(label)
                .lower()
            )

            if (
                "browse" in lower
                or
                "upload" in lower
                or
                "file chooser" in lower
            ):

                screen.widgets.append(
                    Widget(
                        "FileUpload"
                    )
                )

            if (
                "process" in lower
                or
                "submit" in lower
                or
                "import" in lower
            ):

                screen.widgets.append(
                    Widget(
                        "PrimaryButton"
                    )
                )

            if (
                "list" in lower
                or
                "table" in lower
                or
                "grid" in lower
            ):

                screen.widgets.append(
                    Widget(
                        "DataGrid"
                    )
                )

        analysis.screens.append(
            screen
        )

        return analysis

    # ========================================================
    # SAFE NAME
    # ========================================================

    def _safe_name(
        self,
        name
    ):

        return (
            name
            .replace(" ", "_")
            .replace("/", "_")
            .replace("\\", "_")
            .strip()
        )

    # ========================================================
    # REPORT
    # ========================================================

    def print_result(
        self,
        result
    ):

        print()

        print("=" * 80)

        print(
            "RECONSTRUCTION RESULT"
        )

        print("=" * 80)

        print()

        print(
            f"Application Name : "
            f"{result.application_name}"
        )

        print(
            f"Generated Path   : "
            f"{result.generated_path}"
        )

        print(
            f"Mapped Components: "
            f"{result.mapped_components}"
        )

        print(
            f"Missing Components: "
            f"{result.missing_components}"
        )

        print(
            f"Pages Generated  : "
            f"{result.pages_generated}"
        )

        print(
            f"Workflow Created : "
            f"{result.workflow_generated}"
        )

        print()