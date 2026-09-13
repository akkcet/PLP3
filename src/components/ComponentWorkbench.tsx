import React, { useState } from "react";
import {
  Boxes,
  Play,
  CheckCircle2,
  AlertCircle,
  Copy,
  Check,
  Terminal,
  FileCode,
  Sparkles,
  Search,
  Filter,
  RefreshCw,
  Layers,
  ArrowRight,
  ShieldCheck,
  Network,
  Cpu,
  BookOpen,
} from "lucide-react";

export interface ComponentDefinition {
  id: string;
  name: string;
  module: string;
  functionName: string;
  plpLocalIds: string[];
  category: "data_flow" | "eln_integration" | "manipulation" | "file_io";
  shortDescription: string;
  fullDoc: string;
  pythonSignature: string;
  importStatement: string;
  cliCommand: string;
  defaultInput: Record<string, any>;
  testPresets: {
    label: string;
    description: string;
    payload: Record<string, any>;
  }[];
  unitTestClass: string;
}

export const REUSABLE_COMPONENTS: ComponentDefinition[] = [
  {
    id: "custom_filter",
    name: "Custom Filter",
    module: "biovia_pipeline.custom_filter",
    functionName: "custom_filter",
    plpLocalIds: ["4", "6", "14", "19", "54", "55", "56"],
    category: "data_flow",
    shortDescription: "Unified PilotScript expression filter evaluating records and global variables",
    fullDoc: "Evaluates whether an incoming record passes based on a PLP PilotScript condition. Used across file extension routing and workflow gatekeepers.",
    pythonSignature: "custom_filter(expression: str, record: Optional[Dict[str, Any]] = None, globals_dict: Optional[Dict[str, Any]] = None) -> bool",
    importStatement: "from biovia_pipeline import custom_filter",
    cliCommand: "python3 -m biovia_pipeline.cli custom-filter \"<expression>\" --record '<json>' --globals '<json>'",
    defaultInput: {
      expression: "findsubstring(DocRelativepath, '.pdf')>1",
      record: JSON.stringify({ DocRelativepath: "spectroscopy_summary.pdf" }, null, 2),
      globals: JSON.stringify({ experiment_number: "EXP-2026-XRF-01" }, null, 2),
    },
    testPresets: [
      {
        label: "PDF Extension Check",
        description: "findsubstring(DocRelativepath, '.pdf')>1",
        payload: {
          expression: "findsubstring(DocRelativepath, '.pdf')>1",
          record: JSON.stringify({ DocRelativepath: "spectroscopy_summary.pdf" }, null, 2),
          globals: JSON.stringify({}, null, 2),
        },
      },
      {
        label: "Excel Extension Check",
        description: "findsubstring(DocRelativepath, '.xlsx')>1",
        payload: {
          expression: "findsubstring(DocRelativepath, '.xlsx')>1",
          record: JSON.stringify({ DocRelativepath: "calibration_data.xlsx" }, null, 2),
          globals: JSON.stringify({}, null, 2),
        },
      },
      {
        label: "Gatekeeper 1: Missing Location",
        description: "@experiment_number is defined and @experiment_number is ne '' and @filelocation is eq ''",
        payload: {
          expression: "@experiment_number is defined and @experiment_number is ne '' and @filelocation is eq ''",
          record: JSON.stringify({}, null, 2),
          globals: JSON.stringify({ experiment_number: "EXP-2026-XRF-01", filelocation: "" }, null, 2),
        },
      },
      {
        label: "Gatekeeper 2: Stage Transition",
        description: "@xml is defined and @xml ne '' and @filelist is eq ''",
        payload: {
          expression: "@xml is defined and @xml ne '' and @filelist is eq ''",
          record: JSON.stringify({}, null, 2),
          globals: JSON.stringify({ xml: "<root/>", filelist: "" }, null, 2),
        },
      },
    ],
    unitTestClass: "tests.test_components.TestCustomFilterIsolated",
  },
  {
    id: "custom_manipulator",
    name: "Custom Manipulator",
    module: "biovia_pipeline.custom_manipulator",
    functionName: "custom_manipulator",
    plpLocalIds: ["58", "60"],
    category: "manipulation",
    shortDescription: "Unified PilotScript record, global, and local variable transformer with control flow",
    fullDoc: "Executes PilotScript statements to mutate record attributes, global workflow variables, and local counters with support for loops and branching.",
    pythonSignature: "custom_manipulator(expression: str, record: Optional[Dict[str, Any]] = None, globals_dict: Optional[Dict[str, Any]] = None, locals_dict: Optional[Dict[str, Any]] = None, initial_expression: Optional[str] = None, final_expression: Optional[str] = None) -> Tuple[Dict, Dict, Dict]",
    importStatement: "from biovia_pipeline import custom_manipulator",
    cliCommand: "python3 -m biovia_pipeline.cli custom-manipulator \"<expression>\" --record '<json>'",
    defaultInput: {
      expression: "A := 10;\nB := A * 2;\nCleanTitle := 'Clean_' . SectionTitle;\n#counter := 1;\n#counter++;",
      record: JSON.stringify({ SectionTitle: "Spectroscopy Analysis" }, null, 2),
      globals: JSON.stringify({ TargetExperiment: "EXP-2026-XRF-01" }, null, 2),
      locals: JSON.stringify({ counter: 0 }, null, 2),
    },
    testPresets: [
      {
        label: "Record Property Assignment",
        description: "A := 10; B := A * 2; Title := 'Assay Results';",
        payload: {
          expression: "A := 10; B := A * 2; Title := 'Assay Results';",
          record: JSON.stringify({ Initial: "yes" }, null, 2),
          globals: JSON.stringify({}, null, 2),
          locals: JSON.stringify({}, null, 2),
        },
      },
      {
        label: "Scoped Variables (#local, @global)",
        description: "#count := 1; #count++; @status := 'READY'; Clean := 'PROCESSED_' . File;",
        payload: {
          expression: "#count := 1;\n#count++;\n@status := 'READY';\nClean := 'PROCESSED_' . File;",
          record: JSON.stringify({ File: "spectrum.pdf" }, null, 2),
          globals: JSON.stringify({ status: "INIT" }, null, 2),
          locals: JSON.stringify({ count: 0 }, null, 2),
        },
      },
      {
        label: "Conditional Branching (IF/THEN/ELSE)",
        description: "if Score >= 90 then Grade := 'A'; elsif Score >= 75 then Grade := 'B'; else Grade := 'C'; end if;",
        payload: {
          expression: "if Score >= 90 then\n    Grade := 'A';\nelsif Score >= 75 then\n    Grade := 'B';\nelse\n    Grade := 'C';\nend if;",
          record: JSON.stringify({ Score: 88 }, null, 2),
          globals: JSON.stringify({}, null, 2),
          locals: JSON.stringify({}, null, 2),
        },
      },
      {
        label: "Iteration Loop (FOR ... LOOP)",
        description: "#sum := 0; for #i in 1 .. 5 loop #sum += #i; end loop; Total := #sum;",
        payload: {
          expression: "#sum := 0;\nfor #i in 1 .. 5 loop\n    #sum += #i;\nend loop;\nTotal := #sum;",
          record: JSON.stringify({}, null, 2),
          globals: JSON.stringify({}, null, 2),
          locals: JSON.stringify({}, null, 2),
        },
      },
    ],
    unitTestClass: "tests.test_components.TestCustomManipulatorIsolated",
  },
  {
    id: "notebook_connection",
    name: "Notebook Connection",
    module: "biovia_pipeline.notebook_connection",
    functionName: "notebook_connection",
    plpLocalIds: ["30"],
    category: "eln_integration",
    shortDescription: "Establishes secure, authenticated session with Biovia Notebook ELN application",
    fullDoc: "Configures and initializes connection credentials (session token or user/password), custom headers, and encodes the standard PLP connection hash.",
    pythonSignature: "notebook_connection(connection_name: str, server_url: str = '...', authentication_method: str = '...', session_token: Optional[str] = None, username: Optional[str] = None, password: Optional[str] = None, ...) -> NotebookConnectionObject",
    importStatement: "from biovia_pipeline import notebook_connection",
    cliCommand: "python3 -m biovia_pipeline.cli notebook-connection --name NotebookConnection --auth 'Use Notebook Session Token'",
    defaultInput: {
      name: "NotebookConnection",
      url: "https://notebook.corp.internal/eln",
      auth: "Use Notebook Session Token",
      user: "arun.khuntia",
      token: "tok_eln_mock_session_abc123",
    },
    testPresets: [
      {
        label: "Session Token Authentication",
        description: "Authenticate using existing enterprise SSO session token",
        payload: {
          name: "ProdNotebookConnection",
          url: "https://notebook.corp.internal/eln",
          auth: "Use Notebook Session Token",
          user: "arun.khuntia",
          token: "tok_sso_session_verified_99",
        },
      },
      {
        label: "Basic Credentials Authentication",
        description: "Authenticate using username and password parameters",
        payload: {
          name: "ServiceAccountConnection",
          url: "https://notebook.corp.internal/eln",
          auth: "Use Username and Password Parameters",
          user: "svc_biovia_pipeline",
          token: "",
        },
      },
    ],
    unitTestClass: "tests.test_components.TestNotebookConnectionIsolated",
  },
  {
    id: "experiment_query",
    name: "Experiment Query",
    module: "biovia_pipeline.experiment_query",
    functionName: "experiment_query",
    plpLocalIds: ["31"],
    category: "eln_integration",
    shortDescription: "Queries Biovia Notebook experiments via OData with status and section decoding",
    fullDoc: "Executes OData queries using a Notebook Connection to retrieve experiment metadata, signing status, and simple section structures.",
    pythonSignature: "experiment_query(connection: NotebookConnectionObject, filter_by: str = 'Experiment Number', filter_type: str = 'Equals', filter_value: str = '...', return_simple_section_data: bool = True, maximum: int = 10) -> List[Dict[str, Any]]",
    importStatement: "from biovia_pipeline import experiment_query, notebook_connection",
    cliCommand: "python3 -m biovia_pipeline.cli experiment-query --connection NotebookConnection --filter-val EXP-2026-XRF-01",
    defaultInput: {
      connection: "NotebookConnection",
      filterBy: "Experiment Number",
      filterType: "Equals",
      filterVal: "EXP-2026-XRF-01",
      max: "10",
    },
    testPresets: [
      {
        label: "Lookup by Experiment Number",
        description: "Find specific experiment EXP-2026-XRF-01",
        payload: {
          connection: "NotebookConnection",
          filterBy: "Experiment Number",
          filterType: "Equals",
          filterVal: "EXP-2026-XRF-01",
          max: "1",
        },
      },
      {
        label: "Lookup by Title Contains",
        description: "Search for experiments containing 'Spectroscopy'",
        payload: {
          connection: "NotebookConnection",
          filterBy: "Title",
          filterType: "Contains",
          filterVal: "Spectroscopy",
          max: "5",
        },
      },
    ],
    unitTestClass: "tests.test_components.TestExperimentQueryIsolated",
  },
  {
    id: "parse_model_xml",
    name: "Model XML Parser",
    module: "biovia_pipeline.xml_model_parser",
    functionName: "parse_model_xml",
    plpLocalIds: ["41", "42"],
    category: "file_io",
    shortDescription: "Parses instrument export XML and extracts generic file attachments and section titles",
    fullDoc: "Safely parses <generic> items from model data XML, normalizes Windows/UNC file paths, and extracts file extensions.",
    pythonSignature: "parse_model_xml(xml_source: Union[str, Path]) -> ModelXmlMetadata",
    importStatement: "from biovia_pipeline import parse_model_xml",
    cliCommand: "python3 -m biovia_pipeline.cli parse-model sample_model_data.xml",
    defaultInput: {
      xmlPath: "sample_model_data.xml",
    },
    testPresets: [
      {
        label: "Standard Model Data XML",
        description: "Parse sample_model_data.xml with 5 instrument data files",
        payload: {
          xmlPath: "sample_model_data.xml",
        },
      },
    ],
    unitTestClass: "tests.test_components.TestModelXmlParserIsolated",
  },
  {
    id: "section_dispatcher",
    name: "Section Dispatcher",
    module: "biovia_pipeline.section_dispatcher",
    functionName: "SectionDispatcher.classify_file",
    plpLocalIds: ["53", "1", "9", "15", "20", "5"],
    category: "data_flow",
    shortDescription: "Routes files to Biovia Notebook section types based on extension using Custom Filter rules",
    fullDoc: "Replaces PLP Subprotocol 'Section Router' (LocalID 53) using custom_filter to route to PDF, Excel, Word, PowerPoint, or Attachment sections.",
    pythonSignature: "SectionDispatcher.classify_file(file_name: str) -> Dict[str, Any]",
    importStatement: "from biovia_pipeline import SectionDispatcher",
    cliCommand: "python3 -c \"from biovia_pipeline import SectionDispatcher; print(SectionDispatcher.classify_file('report.pdf'))\"",
    defaultInput: {
      fileName: "assay_summary.pdf",
    },
    testPresets: [
      {
        label: "Classify PDF Document",
        description: "Route assay_summary.pdf to PDF section (Component 48/1)",
        payload: { fileName: "assay_summary.pdf" },
      },
      {
        label: "Classify Excel Spreadsheet",
        description: "Route raw_readouts.xlsx to Excel section (Component 51/9)",
        payload: { fileName: "raw_readouts.xlsx" },
      },
      {
        label: "Classify Presentation",
        description: "Route deck.pptx to PowerPoint section (Component 49/15)",
        payload: { fileName: "deck.pptx" },
      },
      {
        label: "Classify Word Document",
        description: "Route protocol.docx to Word section (Component 50/20)",
        payload: { fileName: "protocol.docx" },
      },
      {
        label: "Classify Binary / Attachment",
        description: "Route raw.dat to generic Attachment section (Component 52/5)",
        payload: { fileName: "raw.dat" },
      },
    ],
    unitTestClass: "tests.test_components.TestSectionDispatcherIsolated",
  },
];

export const ComponentWorkbench: React.FC = () => {
  const [selectedCompId, setSelectedCompId] = useState<string>("custom_filter");
  const [activePresetIndex, setActivePresetIndex] = useState<number>(0);
  const [formData, setFormData] = useState<Record<string, any>>(REUSABLE_COMPONENTS[0].defaultInput);
  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [isRunningUnitTest, setIsRunningUnitTest] = useState<boolean>(false);
  const [testOutput, setTestOutput] = useState<string>("");
  const [unitTestOutput, setUnitTestOutput] = useState<string>("");
  const [copiedImport, setCopiedImport] = useState<boolean>(false);
  const [copiedCli, setCopiedCli] = useState<boolean>(false);
  const [searchQuery, setSearchQuery] = useState<string>("");

  const currentComp = REUSABLE_COMPONENTS.find((c) => c.id === selectedCompId) || REUSABLE_COMPONENTS[0];

  const handleSelectComponent = (comp: ComponentDefinition) => {
    setSelectedCompId(comp.id);
    setActivePresetIndex(0);
    setFormData(comp.defaultInput);
    setTestOutput("");
    setUnitTestOutput("");
  };

  const handleApplyPreset = (index: number) => {
    setActivePresetIndex(index);
    const preset = currentComp.testPresets[index];
    if (preset) {
      setFormData(preset.payload);
      setTestOutput("");
    }
  };

  const handleCopy = (text: string, type: "import" | "cli") => {
    navigator.clipboard.writeText(text);
    if (type === "import") {
      setCopiedImport(true);
      setTimeout(() => setCopiedImport(false), 2000);
    } else {
      setCopiedCli(true);
      setTimeout(() => setCopiedCli(false), 2000);
    }
  };

  // Run the component with user inputs in isolation
  const handleRunComponent = async () => {
    setIsRunning(true);
    setTestOutput(`[Executing Component] ${currentComp.name} (${currentComp.module})...\n`);

    try {
      let endpoint = "";
      let bodyData: any = {};

      if (currentComp.id === "custom_filter") {
        endpoint = "/api/python/custom-filter";
        bodyData = {
          expression: formData.expression,
          record: JSON.parse(formData.record || "{}"),
          globals: JSON.parse(formData.globals || "{}"),
        };
      } else if (currentComp.id === "custom_manipulator") {
        endpoint = "/api/python/custom-manipulator";
        bodyData = {
          expression: formData.expression,
          record: JSON.parse(formData.record || "{}"),
          globals: JSON.parse(formData.globals || "{}"),
          locals: JSON.parse(formData.locals || "{}"),
        };
      } else if (currentComp.id === "notebook_connection") {
        endpoint = "/api/python/notebook-connection";
        bodyData = {
          name: formData.name,
          url: formData.url,
          auth: formData.auth,
          user: formData.user,
          token: formData.token,
        };
      } else if (currentComp.id === "experiment_query") {
        endpoint = "/api/python/experiment-query";
        bodyData = {
          connection: formData.connection,
          filterBy: formData.filterBy,
          filterType: formData.filterType,
          filterVal: formData.filterVal,
          max: formData.max,
        };
      } else if (currentComp.id === "parse_model_xml") {
        endpoint = "/api/python/parse-model";
        bodyData = { xmlPath: formData.xmlPath || "sample_model_data.xml" };
      } else if (currentComp.id === "section_dispatcher") {
        endpoint = "/api/python/exec";
        bodyData = {
          code: `from biovia_pipeline import SectionDispatcher
import json
res = SectionDispatcher.classify_file('${formData.fileName || "test.pdf"}')
print(f"--- File Classification Result ---")
print(f"File Name:      {res['file_name']}")
print(f"Section Type:   {res['section_type'].upper()}")
print(f"PLP Component:  LocalID {res['component_id']}")
`,
        };
      }

      const res = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(bodyData),
      });

      const data = await res.json();
      if (data.output || data.stdout) {
        setTestOutput(data.output || data.stdout);
      } else if (data.error) {
        setTestOutput(`[Error] Execution failed:\n${data.error}`);
      } else {
        setTestOutput(JSON.stringify(data, null, 2));
      }
    } catch (err: any) {
      setTestOutput(`[Execution Exception] ${err.message}`);
    } finally {
      setIsRunning(false);
    }
  };

  // Run isolated unittest suite for this component
  const handleRunUnitTest = async () => {
    setIsRunningUnitTest(true);
    setUnitTestOutput(`$ python3 -m unittest ${currentComp.unitTestClass} -v\nRunning test assertions...\n`);

    try {
      const res = await fetch("/api/python/run-component-test", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ target: currentComp.unitTestClass }),
      });
      const data = await res.json();
      setUnitTestOutput(data.combinedOutput || data.stdout || data.stderr || "Test executed.");
    } catch (err: any) {
      setUnitTestOutput(`Test runner error: ${err.message}`);
    } finally {
      setIsRunningUnitTest(false);
    }
  };

  const filteredComponents = REUSABLE_COMPONENTS.filter(
    (c) =>
      c.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.functionName.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.shortDescription.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="flex-1 flex flex-col overflow-hidden bg-slate-950">
      {/* Header Banner */}
      <div className="border-b border-slate-800 bg-slate-900/60 px-6 py-4 flex flex-wrap items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Boxes className="h-5 w-5 text-teal-400" />
            <h2 className="text-lg font-semibold text-slate-100">
              Pipeline Pilot Reusable Component Repository & Isolated Testing Workbench
            </h2>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Test each refactored component in isolation, verify input/output behavior, and copy modular imports to translate future PLP protocols.
          </p>
        </div>

        {/* Search */}
        <div className="relative w-64">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
          <input
            type="text"
            placeholder="Filter components..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full rounded-md border border-slate-700 bg-slate-800/80 py-1.5 pl-9 pr-3 text-xs text-slate-200 placeholder-slate-400 focus:border-teal-500 focus:outline-none"
          />
        </div>
      </div>

      {/* Main Two-Column Layout */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left: Component Catalog List */}
        <div className="w-80 border-r border-slate-800 bg-slate-900/40 flex flex-col">
          <div className="p-3 border-b border-slate-800 text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center justify-between">
            <span>Repository Catalog ({filteredComponents.length})</span>
            <span className="text-[10px] px-2 py-0.5 rounded bg-teal-950 text-teal-400 border border-teal-800">
              PLP Modules
            </span>
          </div>

          <div className="flex-1 overflow-y-auto p-2 space-y-1.5">
            {filteredComponents.map((comp) => {
              const isSelected = comp.id === selectedCompId;
              return (
                <button
                  key={comp.id}
                  onClick={() => handleSelectComponent(comp)}
                  className={`w-full text-left p-3 rounded-lg border transition-all ${
                    isSelected
                      ? "border-teal-500/80 bg-teal-950/40 text-teal-100 shadow-sm"
                      : "border-slate-800/70 bg-slate-900/30 text-slate-300 hover:border-slate-700 hover:bg-slate-800/50"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-sm">{comp.name}</span>
                    <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-800 text-slate-400">
                      {comp.plpLocalIds.length} PLP {comp.plpLocalIds.length > 1 ? "nodes" : "node"}
                    </span>
                  </div>
                  <div className="text-xs font-mono text-teal-400/90 mt-1 truncate">
                    {comp.functionName}()
                  </div>
                  <p className="text-[11px] text-slate-400 mt-1 line-clamp-2">
                    {comp.shortDescription}
                  </p>
                </button>
              );
            })}
          </div>

          <div className="p-3 border-t border-slate-800 bg-slate-900/70 text-[11px] text-slate-400">
            <div className="flex items-center gap-1.5 text-teal-400 font-medium">
              <ShieldCheck className="h-3.5 w-3.5" />
              <span>Zero-Hardcoding & Pure Python</span>
            </div>
            <p className="mt-1">All components operate without PLP server licenses and run in standard Python 3.10+.</p>
          </div>
        </div>

        {/* Right: Component Detail & Interactive Isolation Tester */}
        <div className="flex-1 flex flex-col overflow-y-auto bg-slate-950 p-6 space-y-6">
          {/* Header Card */}
          <div className="rounded-xl border border-slate-800 bg-slate-900/70 p-5 shadow-lg">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <div>
                <div className="flex items-center gap-3">
                  <h3 className="text-xl font-bold text-slate-100">{currentComp.name}</h3>
                  <span className="rounded bg-teal-950 px-2.5 py-0.5 text-xs font-mono font-medium text-teal-400 border border-teal-800">
                    {currentComp.module}
                  </span>
                  <span className="rounded bg-slate-800 px-2 py-0.5 text-xs font-mono text-slate-300">
                    PLP LocalIDs: {currentComp.plpLocalIds.join(", ")}
                  </span>
                </div>
                <p className="text-sm text-slate-300 mt-2">{currentComp.fullDoc}</p>
              </div>

              {/* Action Buttons */}
              <div className="flex items-center gap-2">
                <button
                  onClick={handleRunUnitTest}
                  disabled={isRunningUnitTest}
                  className="flex items-center gap-1.5 rounded-lg border border-teal-700 bg-teal-950/60 px-3.5 py-2 text-xs font-medium text-teal-300 hover:bg-teal-900/60 transition disabled:opacity-50"
                  title="Run Python unittest isolated test class for this component"
                >
                  <RefreshCw className={`h-3.5 w-3.5 ${isRunningUnitTest ? "animate-spin" : ""}`} />
                  {isRunningUnitTest ? "Testing..." : "Run Component Unit Tests"}
                </button>
              </div>
            </div>

            {/* Quick Reusability Code Snippet */}
            <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-3">
              {/* Import statement */}
              <div className="rounded-lg border border-slate-800 bg-slate-950/80 p-3">
                <div className="flex items-center justify-between text-[11px] text-slate-400 mb-1">
                  <span>Python Import (for future protocol scripts)</span>
                  <button
                    onClick={() => handleCopy(currentComp.importStatement, "import")}
                    className="flex items-center gap-1 text-teal-400 hover:text-teal-300"
                  >
                    {copiedImport ? <Check className="h-3 w-3" /> : <Copy className="h-3 w-3" />}
                    {copiedImport ? "Copied" : "Copy"}
                  </button>
                </div>
                <code className="text-xs font-mono text-emerald-400 block overflow-x-auto">
                  {currentComp.importStatement}
                </code>
              </div>

              {/* CLI Command */}
              <div className="rounded-lg border border-slate-800 bg-slate-950/80 p-3">
                <div className="flex items-center justify-between text-[11px] text-slate-400 mb-1">
                  <span>CLI Standalone Invocation</span>
                  <button
                    onClick={() => handleCopy(currentComp.cliCommand, "cli")}
                    className="flex items-center gap-1 text-teal-400 hover:text-teal-300"
                  >
                    {copiedCli ? <Check className="h-3 w-3" /> : <Copy className="h-3 w-3" />}
                    {copiedCli ? "Copied" : "Copy"}
                  </button>
                </div>
                <code className="text-xs font-mono text-amber-300 block truncate">
                  {currentComp.cliCommand}
                </code>
              </div>
            </div>
          </div>

          {/* Test Presets Carousel */}
          {currentComp.testPresets.length > 0 && (
            <div>
              <div className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2 flex items-center gap-1.5">
                <Layers className="h-3.5 w-3.5 text-teal-400" />
                <span>Preset Test Cases for {currentComp.name}</span>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2">
                {currentComp.testPresets.map((preset, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleApplyPreset(idx)}
                    className={`text-left p-2.5 rounded-lg border text-xs transition ${
                      activePresetIndex === idx
                        ? "border-teal-500 bg-teal-950/50 text-teal-200"
                        : "border-slate-800 bg-slate-900/50 text-slate-400 hover:border-slate-700 hover:text-slate-200"
                    }`}
                  >
                    <div className="font-semibold text-slate-200">{preset.label}</div>
                    <div className="text-[11px] font-mono text-slate-400 truncate mt-1">
                      {preset.description}
                    </div>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Interactive Tester Inputs & Live Execution */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Input Parameters Box */}
            <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-5 flex flex-col">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <Terminal className="h-4 w-4 text-teal-400" />
                  <span className="text-sm font-semibold text-slate-200">Component Input Parameters</span>
                </div>
                <span className="text-xs text-slate-400">Editable live</span>
              </div>

              {/* Dynamic Inputs based on Component ID */}
              <div className="space-y-3 flex-1">
                {currentComp.id === "custom_filter" && (
                  <>
                    <div>
                      <label className="block text-xs font-medium text-slate-400 mb-1">
                        PilotScript Filter Expression:
                      </label>
                      <input
                        type="text"
                        value={formData.expression || ""}
                        onChange={(e) => setFormData({ ...formData, expression: e.target.value })}
                        className="w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-1.5 font-mono text-xs text-slate-200 focus:border-teal-500 focus:outline-none"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-slate-400 mb-1">
                        Record Context (JSON):
                      </label>
                      <textarea
                        rows={3}
                        value={formData.record || ""}
                        onChange={(e) => setFormData({ ...formData, record: e.target.value })}
                        className="w-full rounded-md border border-slate-700 bg-slate-950 p-2 font-mono text-xs text-slate-200 focus:border-teal-500 focus:outline-none"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-slate-400 mb-1">
                        Globals Context (JSON):
                      </label>
                      <textarea
                        rows={3}
                        value={formData.globals || ""}
                        onChange={(e) => setFormData({ ...formData, globals: e.target.value })}
                        className="w-full rounded-md border border-slate-700 bg-slate-950 p-2 font-mono text-xs text-slate-200 focus:border-teal-500 focus:outline-none"
                      />
                    </div>
                  </>
                )}

                {currentComp.id === "custom_manipulator" && (
                  <>
                    <div>
                      <label className="block text-xs font-medium text-slate-400 mb-1">
                        PilotScript Statements:
                      </label>
                      <textarea
                        rows={4}
                        value={formData.expression || ""}
                        onChange={(e) => setFormData({ ...formData, expression: e.target.value })}
                        className="w-full rounded-md border border-slate-700 bg-slate-950 p-2 font-mono text-xs text-slate-200 focus:border-teal-500 focus:outline-none"
                      />
                    </div>
                    <div className="grid grid-cols-2 gap-2">
                      <div>
                        <label className="block text-xs font-medium text-slate-400 mb-1">
                          Record JSON:
                        </label>
                        <textarea
                          rows={3}
                          value={formData.record || ""}
                          onChange={(e) => setFormData({ ...formData, record: e.target.value })}
                          className="w-full rounded-md border border-slate-700 bg-slate-950 p-2 font-mono text-xs text-slate-200 focus:border-teal-500 focus:outline-none"
                        />
                      </div>
                      <div>
                        <label className="block text-xs font-medium text-slate-400 mb-1">
                          Globals JSON:
                        </label>
                        <textarea
                          rows={3}
                          value={formData.globals || ""}
                          onChange={(e) => setFormData({ ...formData, globals: e.target.value })}
                          className="w-full rounded-md border border-slate-700 bg-slate-950 p-2 font-mono text-xs text-slate-200 focus:border-teal-500 focus:outline-none"
                        />
                      </div>
                    </div>
                  </>
                )}

                {currentComp.id === "notebook_connection" && (
                  <>
                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <label className="block text-xs font-medium text-slate-400 mb-1">
                          Connection Name:
                        </label>
                        <input
                          type="text"
                          value={formData.name || ""}
                          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                          className="w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-1.5 font-mono text-xs text-slate-200 focus:border-teal-500 focus:outline-none"
                        />
                      </div>
                      <div>
                        <label className="block text-xs font-medium text-slate-400 mb-1">
                          Authentication Method:
                        </label>
                        <select
                          value={formData.auth || "Use Notebook Session Token"}
                          onChange={(e) => setFormData({ ...formData, auth: e.target.value })}
                          className="w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-1.5 text-xs text-slate-200 focus:border-teal-500 focus:outline-none"
                        >
                          <option value="Use Notebook Session Token">Use Notebook Session Token</option>
                          <option value="Use Username and Password Parameters">Use Username and Password Parameters</option>
                        </select>
                      </div>
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-slate-400 mb-1">
                        Biovia Notebook Server URL:
                      </label>
                      <input
                        type="text"
                        value={formData.url || ""}
                        onChange={(e) => setFormData({ ...formData, url: e.target.value })}
                        className="w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-1.5 font-mono text-xs text-slate-200 focus:border-teal-500 focus:outline-none"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-slate-400 mb-1">
                        Session Token:
                      </label>
                      <input
                        type="text"
                        value={formData.token || ""}
                        onChange={(e) => setFormData({ ...formData, token: e.target.value })}
                        className="w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-1.5 font-mono text-xs text-slate-200 focus:border-teal-500 focus:outline-none"
                      />
                    </div>
                  </>
                )}

                {currentComp.id === "experiment_query" && (
                  <>
                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <label className="block text-xs font-medium text-slate-400 mb-1">
                          Filter By:
                        </label>
                        <select
                          value={formData.filterBy || "Experiment Number"}
                          onChange={(e) => setFormData({ ...formData, filterBy: e.target.value })}
                          className="w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-1.5 text-xs text-slate-200 focus:border-teal-500 focus:outline-none"
                        >
                          <option value="Experiment Number">Experiment Number</option>
                          <option value="Title">Title</option>
                          <option value="Project">Project</option>
                        </select>
                      </div>
                      <div>
                        <label className="block text-xs font-medium text-slate-400 mb-1">
                          Filter Type:
                        </label>
                        <select
                          value={formData.filterType || "Equals"}
                          onChange={(e) => setFormData({ ...formData, filterType: e.target.value })}
                          className="w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-1.5 text-xs text-slate-200 focus:border-teal-500 focus:outline-none"
                        >
                          <option value="Equals">Equals</option>
                          <option value="Contains">Contains</option>
                          <option value="Starts With">Starts With</option>
                        </select>
                      </div>
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-slate-400 mb-1">
                        Filter Value:
                      </label>
                      <input
                        type="text"
                        value={formData.filterVal || ""}
                        onChange={(e) => setFormData({ ...formData, filterVal: e.target.value })}
                        className="w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-1.5 font-mono text-xs text-slate-200 focus:border-teal-500 focus:outline-none"
                      />
                    </div>
                  </>
                )}

                {currentComp.id === "parse_model_xml" && (
                  <div>
                    <label className="block text-xs font-medium text-slate-400 mb-1">
                      Model XML File Path:
                    </label>
                    <input
                      type="text"
                      value={formData.xmlPath || "sample_model_data.xml"}
                      onChange={(e) => setFormData({ ...formData, xmlPath: e.target.value })}
                      className="w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-1.5 font-mono text-xs text-slate-200 focus:border-teal-500 focus:outline-none"
                    />
                  </div>
                )}

                {currentComp.id === "section_dispatcher" && (
                  <div>
                    <label className="block text-xs font-medium text-slate-400 mb-1">
                      File Name to Classify:
                    </label>
                    <input
                      type="text"
                      value={formData.fileName || "assay_summary.pdf"}
                      onChange={(e) => setFormData({ ...formData, fileName: e.target.value })}
                      className="w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-1.5 font-mono text-xs text-slate-200 focus:border-teal-500 focus:outline-none"
                    />
                  </div>
                )}
              </div>

              {/* Run Button */}
              <div className="mt-4 pt-4 border-t border-slate-800 flex items-center justify-between">
                <span className="text-[11px] text-slate-400">
                  Calls backend Python execution engine
                </span>
                <button
                  onClick={handleRunComponent}
                  disabled={isRunning}
                  className="flex items-center gap-2 rounded-lg bg-teal-500 px-4 py-2 text-xs font-semibold text-slate-950 hover:bg-teal-400 transition disabled:opacity-50"
                >
                  <Play className={`h-4 w-4 ${isRunning ? "animate-spin" : ""}`} />
                  {isRunning ? "Executing..." : "Execute Component Test"}
                </button>
              </div>
            </div>

            {/* Output / Terminal Result Box */}
            <div className="rounded-xl border border-slate-800 bg-slate-950 p-5 flex flex-col font-mono text-xs">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-3 text-slate-400">
                <span className="flex items-center gap-2 text-slate-200 font-semibold font-sans">
                  <Terminal className="h-4 w-4 text-emerald-400" />
                  Execution Terminal Output
                </span>
                {testOutput && (
                  <span className="text-[11px] text-emerald-400 flex items-center gap-1">
                    <CheckCircle2 className="h-3 w-3" /> Ready
                  </span>
                )}
              </div>

              <div className="flex-1 overflow-y-auto min-h-[220px] max-h-[320px] text-slate-300 whitespace-pre-wrap selection:bg-teal-700">
                {testOutput || (
                  <span className="text-slate-600 italic">
                    Press "Execute Component Test" or choose a preset test case above to view isolated output.
                  </span>
                )}
              </div>

              {/* Unit Test Section if executed */}
              {unitTestOutput && (
                <div className="mt-4 pt-3 border-t border-slate-800">
                  <div className="text-[11px] text-teal-400 font-sans font-semibold mb-1 flex items-center gap-1.5">
                    <CheckCircle2 className="h-3.5 w-3.5 text-teal-400" />
                    Isolated Unit Test Assertion Output ({currentComp.unitTestClass})
                  </div>
                  <pre className="text-[11px] text-slate-300 max-h-36 overflow-y-auto whitespace-pre-wrap">
                    {unitTestOutput}
                  </pre>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
