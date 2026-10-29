from biovia_pipeline.application_generation_orchestrator import (
    ApplicationGenerationOrchestrator
)

from biovia_pipeline.protocol_migration_engine import (
    analyze_protocol_xml
)


with open(
    "tests/Data model UI.xml",
    encoding="utf-8"
) as f:

    xml = f.read()

analysis = analyze_protocol_xml(xml)

orchestrator = (
    ApplicationGenerationOrchestrator()
)

result = orchestrator.generate_application(

    protocol_analysis=analysis,

    screenshots=[

        
    ]
)

orchestrator.print_report(result)