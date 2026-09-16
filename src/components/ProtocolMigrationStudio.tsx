import React, { useState, useEffect } from "react";
import {
  FileText,
  Upload,
  CheckCircle,
  AlertTriangle,
  Play,
  Layers,
  ArrowRight,
  Eye,
  Sliders,
  Code2,
  Database,
  Monitor,
  RefreshCw,
  Info,
  Check,
  X,
  FileSpreadsheet,
  FileCode,
  Sparkles,
  HelpCircle,
} from "lucide-react";

export interface ResolvedNodeDTO {
  localId: string;
  visualName: string;
  coreName: string;
  componentType: string;
  isSubprotocol: boolean;
  status: "AVAILABLE" | "MISSING";
  role: "BLUE_DATA_MANIPULATOR" | "GREEN_UI_GENERATOR";
  matchedKey?: string;
  parameters: Record<string, any>;
  pilotscriptCode?: string;
  incomingConnections: string[];
  outgoingConnections: string[];
  remediationNote?: string;
  uiWidget?: string;
}

export interface ProtocolAnalysisDTO {
  protocolName: string;
  protocolVersion: string;
  author: string;
  totalNodes: number;
  blueCount: number;
  greenCount: number;
  matchedCount: number;
  missingCount: number;
  coveragePercentage: number;
  nodes: ResolvedNodeDTO[];
  connections: Array<{ from: string; to: string }>;
  declaredGlobals: Record<string, any>;
  webAppSchema: {
    title: string;
    description: string;
    interactiveFields: Array<{
      id: string;
      label: string;
      type: string;
      targetNodeId: string;
      paramKey: string;
      defaultValue: any;
      description: string;
      role: string;
    }>;
    executionMode: string;
    supportedFormats: string[];
    pipelineFlow: string[];
  };
  summaryMessage: string;
}

// Sample protocol XML for quick one-click load
const SAMPLE_MIGRATION_XML = `<?xml version="1.0" encoding="UTF-8"?>
<sci:protocol xmlns:sci="http://www.scitegic.com/protocol" name="Analytical Lab Ingestion & ELN Section Creator" version="3.1" author="Analytical Informatics Team">
    <sci:arg name="DefaultNotebookURL">https://notebook.corp.internal/eln/api/v1</sci:arg>
    <sci:arg name="BatchRunMode">Online</sci:arg>

    <!-- Green Component 1: Web Application Header / Page Canvas -->
    <sci:component localid="1" name="Analytical Portal Canvas" type="WebPageBuilder">
        <sci:arg name="Title">Biovia Notebook Automated Ingestion Portal</sci:arg>
        <sci:arg name="Subtitle">Attach analytical spectra, raw spreadsheets, and PDF documents to active experiments</sci:arg>
    </sci:component>

    <!-- Green Component 2: Interactive Experiment Query Input -->
    <sci:component localid="2" name="Experiment ID Input Box" type="WebFormInput">
        <sci:arg name="Label">Target Experiment Number</sci:arg>
        <sci:arg name="ExperimentNumber">EXP-2026-XRF-01</sci:arg>
    </sci:component>

    <!-- Green Component 3: Drag-and-Drop Document Uploader -->
    <sci:component localid="3" name="Document File Dropzone" type="WebFileUpload">
        <sci:arg name="Label">Upload Analytical Documents (Excel, PDF, Word, PPTX)</sci:arg>
        <sci:arg name="FileLocation">sample_analytical_data.xlsx</sci:arg>
    </sci:component>

    <!-- Blue Component 1: Notebook Session Authenticator -->
    <sci:component localid="4" name="Step 1: Check Session Token" type="{9B1E4A32-12C5-4F8A-9871-332D76EF12A0}">
        <sci:arg name="BaseURL">https://notebook.corp.internal/eln/api/v1</sci:arg>
        <sci:arg name="ApiKey">secret_token_99384</sci:arg>
    </sci:component>

    <!-- Blue Component 2: Query Target Experiment in ELN -->
    <sci:component localid="5" name="Fetch Experiment Details" type="Query Experiment">
        <sci:arg name="ExperimentNumber">EXP-2026-XRF-01</sci:arg>
    </sci:component>

    <!-- Blue Component 3: File Type Router / Dispatcher -->
    <sci:component localid="6" name="Route by File Extension" type="Section Dispatcher">
        <sci:arg name="DefaultAction">RouteToSectionType</sci:arg>
    </sci:component>

    <!-- Blue Component 4: Gatekeeper 1 - Excel Format Filter -->
    <sci:component localid="7" name="Gatekeeper 1: Excel Filter" type="{470B2F2A-5A0D-47C0-8FD6-36BDD2C318F8}">
        <sci:arg name="Expression">Find(FileLocation, ".xlsx") gt 0 or Find(FileLocation, ".xls") gt 0</sci:arg>
    </sci:component>

    <!-- Blue Component 5: Add Excel Worksheet Section -->
    <sci:component localid="8" name="Add Excel Section" type="Add Excel Section">
        <sci:arg name="SectionTitle">Elemental XRF Assay Raw Data</sci:arg>
        <sci:arg name="ColumnsToPreview">4</sci:arg>
        <sci:arg name="RowsToPreview">6</sci:arg>
    </sci:component>

    <!-- Blue Component 6: Gatekeeper 2 - PDF Format Filter -->
    <sci:component localid="9" name="Gatekeeper 2: PDF Filter" type="{470B2F2A-5A0D-47C0-8FD6-36BDD2C318F8}">
        <sci:arg name="Expression">Find(FileLocation, ".pdf") gt 0</sci:arg>
    </sci:component>

    <!-- Blue Component 7: Add PDF Document Section -->
    <sci:component localid="10" name="Embed PDF Report" type="Add PDF Section">
        <sci:arg name="SectionTitle">Instrument Calibration Certificate</sci:arg>
    </sci:component>

    <!-- Green Component 4: Execution Trigger Button -->
    <sci:component localid="11" name="Submit and Sync Button" type="WebActionButton">
        <sci:arg name="ButtonText">Process and Sync to Biovia Notebook</sci:arg>
    </sci:component>

    <!-- Green Component 5: Results & Verification Table -->
    <sci:component localid="12" name="Processing Results Table" type="WebTable">
        <sci:arg name="ShowColumns">SectionID, SectionTitle, Type, Status</sci:arg>
    </sci:component>

    <!-- Missing Component: Unimplemented Laboratory LIMS synchronizer -->
    <sci:component localid="13" name="Legacy Thermo LIMS Sync" type="LegacyLimsBridgeService">
        <sci:arg name="ServerAddress">lims01.corp.internal</sci:arg>
    </sci:component>

    <!-- Connections -->
    <sci:connectid from="1" to="2" />
    <sci:connectid from="2" to="3" />
    <sci:connectid from="3" to="4" />
    <sci:connectid from="4" to="5" />
    <sci:connectid from="5" to="6" />
    <sci:connectid from="6" to="7" />
    <sci:connectid from="7" to="8" />
    <sci:connectid from="6" to="9" />
    <sci:connectid from="9" to="10" />
    <sci:connectid from="10" to="11" />
    <sci:connectid from="11" to="12" />
    <sci:connectid from="12" to="13" />
</sci:protocol>`;

export const ProtocolMigrationStudio: React.FC = () => {
  // Tabs & Views
  const [activeSubTab, setActiveSubTab] = useState<"analysis" | "reconstructed_app" | "ui_comparison">("analysis");
  const [showHelpGuide, setShowHelpGuide] = useState<boolean>(false);

  // Protocol XML State
  const [xmlContent, setXmlContent] = useState<string>(SAMPLE_MIGRATION_XML);
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
  const [analysisResult, setAnalysisResult] = useState<ProtocolAnalysisDTO | null>(null);
  const [filterRole, setFilterRole] = useState<"ALL" | "BLUE" | "GREEN" | "MISSING">("ALL");

  // Screenshot Comparison State
  const [screenshotUrl, setScreenshotUrl] = useState<string | null>(null);
  const [opacity, setOpacity] = useState<number>(50);
  const [compareMode, setCompareMode] = useState<"side_by_side" | "overlay" | "reconstructed_only">("side_by_side");

  // Live Reconstructed App Interactive State
  const [formValues, setFormValues] = useState<Record<string, string>>({
    exp_number: "EXP-2026-XRF-01",
    notebook_url: "https://notebook.corp.internal/eln/api/v1",
  });
  const [uploadedFiles, setUploadedFiles] = useState<string[]>([
    "Elemental_XRF_Assay.xlsx",
    "Calibration_Report.pdf",
    "Synthesis_Overview.pptx",
  ]);
  const [isExecutingApp, setIsExecutingApp] = useState<boolean>(false);
  const [appExecutionResult, setAppExecutionResult] = useState<any | null>(null);

  // Analyze XML
  const handleAnalyzeProtocol = async () => {
    if (!xmlContent.trim()) return;
    setIsAnalyzing(true);
    try {
      const resp = await fetch("/api/protocols/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ xmlContent }),
      });
      const data = await resp.json();
      if (data.success) {
        setAnalysisResult(data.analysis);
      } else {
        alert("Error analyzing protocol XML: " + (data.details || data.error));
      }
    } catch (err: any) {
      alert("Analysis failed: " + err.message);
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Run Reconstructed Web App
  const handleExecuteReconstructedApp = async () => {
    setIsExecutingApp(true);
    try {
      const resp = await fetch("/api/protocols/execute-reconstructed", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          experimentNumber: formValues.exp_number,
          files: uploadedFiles,
          analysis: analysisResult,
        }),
      });
      const data = await resp.json();
      setAppExecutionResult(data);
    } catch (err: any) {
      alert("Web App Execution Error: " + err.message);
    } finally {
      setIsExecutingApp(false);
    }
  };

  // Auto-analyze initial sample on mount so user sees immediate results
  useEffect(() => {
    if (!analysisResult) {
      handleAnalyzeProtocol();
    }
  }, []);
  const handleScreenshotUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (loadEvt) => {
        setScreenshotUrl(loadEvt.target?.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  // Filtered nodes
  const filteredNodes = (analysisResult?.nodes || []).filter((n) => {
    if (filterRole === "BLUE") return n.role === "BLUE_DATA_MANIPULATOR";
    if (filterRole === "GREEN") return n.role === "GREEN_UI_GENERATOR";
    if (filterRole === "MISSING") return n.status === "MISSING";
    return true;
  });

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 border border-slate-800 rounded-xl p-6 text-white shadow-xl">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center space-x-3 mb-2">
              <span className="px-2.5 py-1 text-xs font-semibold uppercase tracking-wider bg-blue-500/20 text-blue-300 border border-blue-500/30 rounded-full">
                Migration & Component Discovery Studio
              </span>
              <span className="px-2.5 py-1 text-xs font-semibold uppercase tracking-wider bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 rounded-full">
                PLP Web App Reconstructor
              </span>
            </div>
            <h1 className="text-2xl font-bold tracking-tight">
              Biovia Pipeline Pilot Protocol to Web App Migration
            </h1>
            <p className="text-slate-400 text-sm mt-1 max-w-3xl">
              Upload any complete Pipeline Pilot protocol XML. Automatically identify all internal components,
              classify into <strong>Blue (Data Manipulators)</strong> mapped to Python and <strong>Green (UI Generators)</strong> responsible for user experience,
              flag missing items, and reconstruct the exact web application alongside your PLP screenshot.
            </p>
          </div>

          <div className="flex items-center space-x-3">
            <button
              onClick={() => setShowHelpGuide(!showHelpGuide)}
              className="px-3.5 py-2 bg-indigo-900/60 hover:bg-indigo-800 text-indigo-200 text-sm font-medium rounded-lg border border-indigo-700/60 transition flex items-center space-x-2"
            >
              <HelpCircle className="w-4 h-4 text-indigo-300" />
              <span>How This Works</span>
            </button>
            <button
              onClick={() => {
                setXmlContent(SAMPLE_MIGRATION_XML);
                handleAnalyzeProtocol();
              }}
              className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-sm font-medium rounded-lg border border-slate-700 transition flex items-center space-x-2"
            >
              <RefreshCw className="w-4 h-4" />
              <span>Load Sample Protocol</span>
            </button>
            <button
              onClick={handleAnalyzeProtocol}
              disabled={isAnalyzing}
              className="px-5 py-2 bg-blue-600 hover:bg-blue-500 text-white text-sm font-semibold rounded-lg shadow transition flex items-center space-x-2 disabled:opacity-50"
            >
              {isAnalyzing ? (
                <RefreshCw className="w-4 h-4 animate-spin" />
              ) : (
                <Sparkles className="w-4 h-4" />
              )}
              <span>Analyze & Discover Components</span>
            </button>
          </div>
        </div>

        {/* 3-Step Interactive Workflow Bar */}
        <div className="mt-6 pt-5 border-t border-slate-800/80 grid grid-cols-1 md:grid-cols-3 gap-3">
          <div
            onClick={() => setActiveSubTab("analysis")}
            className={`cursor-pointer p-3 rounded-lg border transition flex items-start space-x-3 ${
              activeSubTab === "analysis"
                ? "bg-blue-950/50 border-blue-500/60 ring-1 ring-blue-500/30"
                : "bg-slate-900/40 border-slate-800 hover:border-slate-700"
            }`}
          >
            <div className="w-6 h-6 rounded-full bg-blue-500/20 text-blue-400 font-bold text-xs flex items-center justify-center flex-shrink-0 mt-0.5">
              1
            </div>
            <div>
              <div className="text-xs font-bold text-slate-200 flex items-center space-x-1.5">
                <span>Step 1: Discover & Map</span>
                {analysisResult && <Check className="w-3.5 h-3.5 text-emerald-400" />}
              </div>
              <p className="text-[11px] text-slate-400 mt-0.5">
                Inspect components: Blue (Python data logic) vs Green (UI form inputs) & flag missing parts.
              </p>
            </div>
          </div>

          <div
            onClick={() => setActiveSubTab("reconstructed_app")}
            className={`cursor-pointer p-3 rounded-lg border transition flex items-start space-x-3 ${
              activeSubTab === "reconstructed_app"
                ? "bg-emerald-950/50 border-emerald-500/60 ring-1 ring-emerald-500/30"
                : "bg-slate-900/40 border-slate-800 hover:border-slate-700"
            }`}
          >
            <div className="w-6 h-6 rounded-full bg-emerald-500/20 text-emerald-400 font-bold text-xs flex items-center justify-center flex-shrink-0 mt-0.5">
              2
            </div>
            <div>
              <div className="text-xs font-bold text-slate-200 flex items-center space-x-1.5">
                <span>Step 2: Run Migrated Web App</span>
                <span className="text-[10px] px-1.5 py-0.2 bg-emerald-500/20 text-emerald-300 rounded">Live</span>
              </div>
              <p className="text-[11px] text-slate-400 mt-0.5">
                Enter an Experiment ID, attach lab files, and execute the actual Python pipeline.
              </p>
            </div>
          </div>

          <div
            onClick={() => setActiveSubTab("ui_comparison")}
            className={`cursor-pointer p-3 rounded-lg border transition flex items-start space-x-3 ${
              activeSubTab === "ui_comparison"
                ? "bg-purple-950/50 border-purple-500/60 ring-1 ring-purple-500/30"
                : "bg-slate-900/40 border-slate-800 hover:border-slate-700"
            }`}
          >
            <div className="w-6 h-6 rounded-full bg-purple-500/20 text-purple-400 font-bold text-xs flex items-center justify-center flex-shrink-0 mt-0.5">
              3
            </div>
            <div>
              <div className="text-xs font-bold text-slate-200">
                <span>Step 3: 1:1 Screenshot Match</span>
              </div>
              <p className="text-[11px] text-slate-400 mt-0.5">
                Upload your Biovia PLP web app screenshot to verify pixel-accurate layout match side-by-side.
              </p>
            </div>
          </div>
        </div>

        {/* Expandable Help Guide Modal / Drawer */}
        {showHelpGuide && (
          <div className="mt-5 p-5 bg-indigo-950/40 border border-indigo-500/30 rounded-xl space-y-4 text-xs text-slate-300">
            <div className="flex items-center justify-between border-b border-indigo-500/20 pb-2">
              <div className="flex items-center space-x-2">
                <HelpCircle className="w-4 h-4 text-indigo-400" />
                <h3 className="font-bold text-sm text-indigo-200">Plain English Guide: What is this feature?</h3>
              </div>
              <button
                onClick={() => setShowHelpGuide(false)}
                className="text-slate-400 hover:text-white"
              >
                ✕ Close
              </button>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="space-y-1">
                <span className="font-bold text-blue-400 uppercase tracking-wide text-[10px]">What is the Goal?</span>
                <p>
                  Biovia Pipeline Pilot protocols often act as <strong>web applications</strong> that scientists use to attach data to experiments. This feature migrates those protocols directly into a modern React web app without rewriting pipeline logic from scratch.
                </p>
              </div>
              <div className="space-y-1">
                <span className="font-bold text-emerald-400 uppercase tracking-wide text-[10px]">Blue vs. Green Components</span>
                <p>
                  <strong>Blue components</strong> do the math and data processing (like checking tokens, filtering by file extension, parsing spreadsheets) — they run on our <strong>Python backend</strong>.
                  <strong>Green components</strong> define what the user sees (text boxes, dropzones, action buttons).
                </p>
              </div>
              <div className="space-y-1">
                <span className="font-bold text-purple-400 uppercase tracking-wide text-[10px]">How do I use it right now?</span>
                <p>
                  Just click <strong>"Load Sample Protocol"</strong> above! Then click <strong>"Step 2: Run Migrated Web App"</strong>, enter an experiment ID like <code className="text-emerald-300">EXP-2026-XRF-01</code>, and click <strong>"Run Pipeline Application"</strong> to watch it execute live.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* View Switcher Tabs */}
        <div className="flex border-b border-slate-800 mt-6 -mb-2 space-x-2">
          <button
            onClick={() => setActiveSubTab("analysis")}
            className={`pb-3 px-4 text-sm font-medium border-b-2 transition flex items-center space-x-2 ${
              activeSubTab === "analysis"
                ? "border-blue-400 text-blue-400"
                : "border-transparent text-slate-400 hover:text-slate-200"
            }`}
          >
            <Layers className="w-4 h-4" />
            <span>Component Classification & Mapping</span>
            {analysisResult && (
              <span className="ml-2 px-2 py-0.5 text-xs bg-slate-800 text-slate-300 rounded-full">
                {analysisResult.totalNodes}
              </span>
            )}
          </button>

          <button
            onClick={() => setActiveSubTab("reconstructed_app")}
            className={`pb-3 px-4 text-sm font-medium border-b-2 transition flex items-center space-x-2 ${
              activeSubTab === "reconstructed_app"
                ? "border-emerald-400 text-emerald-400"
                : "border-transparent text-slate-400 hover:text-slate-200"
            }`}
          >
            <Monitor className="w-4 h-4" />
            <span>Reconstructed Web Application (Live)</span>
            <span className="ml-1 px-2 py-0.5 text-xs bg-emerald-500/20 text-emerald-300 rounded-full">
              Executable
            </span>
          </button>

          <button
            onClick={() => setActiveSubTab("ui_comparison")}
            className={`pb-3 px-4 text-sm font-medium border-b-2 transition flex items-center space-x-2 ${
              activeSubTab === "ui_comparison"
                ? "border-purple-400 text-purple-400"
                : "border-transparent text-slate-400 hover:text-slate-200"
            }`}
          >
            <Eye className="w-4 h-4" />
            <span>1:1 Screenshot Migration Studio</span>
          </button>
        </div>
      </div>

      {/* TAB 1: Analysis & Component Discovery */}
      {activeSubTab === "analysis" && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left Column: XML Editor & Upload */}
          <div className="lg:col-span-5 space-y-4">
            <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 shadow-sm">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center space-x-2">
                  <FileCode className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                  <h2 className="text-sm font-bold text-slate-900 dark:text-slate-100">
                    Input Protocol XML
                  </h2>
                </div>
                <label className="cursor-pointer text-xs font-semibold text-blue-600 dark:text-blue-400 hover:underline flex items-center space-x-1">
                  <Upload className="w-3.5 h-3.5" />
                  <span>Upload .XML</span>
                  <input
                    type="file"
                    accept=".xml"
                    className="hidden"
                    onChange={(e) => {
                      const file = e.target.files?.[0];
                      if (file) {
                        const r = new FileReader();
                        r.onload = (evt) => setXmlContent(evt.target?.result as string);
                        r.readAsText(file);
                      }
                    }}
                  />
                </label>
              </div>

              <textarea
                value={xmlContent}
                onChange={(e) => setXmlContent(e.target.value)}
                placeholder="Paste Pipeline Pilot protocol XML here..."
                rows={18}
                className="w-full font-mono text-xs p-3 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />

              <div className="mt-3 flex justify-between items-center text-xs text-slate-500">
                <span>{xmlContent.split("\n").length} lines</span>
                <button
                  onClick={handleAnalyzeProtocol}
                  disabled={isAnalyzing}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-md font-medium flex items-center space-x-1 shadow transition"
                >
                  <Sparkles className="w-3.5 h-3.5" />
                  <span>Run Analysis</span>
                </button>
              </div>
            </div>

            {/* Role Color Legend */}
            <div className="bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4 text-xs space-y-3">
              <h3 className="font-semibold text-slate-900 dark:text-slate-100 uppercase tracking-wider text-[11px]">
                Pipeline Pilot Classification Legend
              </h3>
              <div className="flex items-start space-x-3">
                <div className="w-3.5 h-3.5 rounded bg-blue-500 mt-0.5 flex-shrink-0" />
                <div>
                  <strong className="text-blue-600 dark:text-blue-400">
                    Blue Components (Data Manipulators):
                  </strong>
                  <p className="text-slate-600 dark:text-slate-400 mt-0.5">
                    Pipeline processing nodes translated to our Python repository (Filters, Manipulators, Section Builders, ELN Queries, Subprotocols).
                  </p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <div className="w-3.5 h-3.5 rounded bg-emerald-500 mt-0.5 flex-shrink-0" />
                <div>
                  <strong className="text-emerald-600 dark:text-emerald-400">
                    Green Components (UI Generators):
                  </strong>
                  <p className="text-slate-600 dark:text-slate-400 mt-0.5">
                    Components responsible for creating the web application UI (Web forms, inputs, file upload zones, execution buttons, tables).
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Right Column: Analysis Results & Component Bill of Materials */}
          <div className="lg:col-span-7 space-y-4">
            {!analysisResult ? (
              <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-12 text-center text-slate-500">
                <Layers className="w-12 h-12 mx-auto text-slate-300 dark:text-slate-700 mb-3" />
                <h3 className="text-base font-semibold text-slate-700 dark:text-slate-300">
                  No Protocol Analyzed Yet
                </h3>
                <p className="text-xs max-w-sm mx-auto mt-1">
                  Click "Analyze & Discover Components" or upload an XML file to parse nodes, inspect parameters, and identify reusable vs missing building blocks.
                </p>
                <button
                  onClick={handleAnalyzeProtocol}
                  className="mt-4 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold rounded-lg shadow"
                >
                  Analyze Sample Protocol
                </button>
              </div>
            ) : (
              <div className="space-y-4">
                {/* Protocol Metrics Bar */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                  <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg p-3">
                    <span className="text-[11px] text-slate-500 uppercase tracking-wider block font-semibold">
                      Total Nodes
                    </span>
                    <span className="text-xl font-bold text-slate-900 dark:text-slate-100">
                      {analysisResult.totalNodes}
                    </span>
                  </div>
                  <div className="bg-blue-50/50 dark:bg-blue-950/20 border border-blue-200 dark:border-blue-900/50 rounded-lg p-3">
                    <span className="text-[11px] text-blue-600 dark:text-blue-400 uppercase tracking-wider block font-semibold">
                      Blue (Data)
                    </span>
                    <span className="text-xl font-bold text-blue-700 dark:text-blue-300">
                      {analysisResult.blueCount}
                    </span>
                  </div>
                  <div className="bg-emerald-50/50 dark:bg-emerald-950/20 border border-emerald-200 dark:border-emerald-900/50 rounded-lg p-3">
                    <span className="text-[11px] text-emerald-600 dark:text-emerald-400 uppercase tracking-wider block font-semibold">
                      Green (UI)
                    </span>
                    <span className="text-xl font-bold text-emerald-700 dark:text-emerald-300">
                      {analysisResult.greenCount}
                    </span>
                  </div>
                  <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg p-3">
                    <span className="text-[11px] text-slate-500 uppercase tracking-wider block font-semibold">
                      Coverage
                    </span>
                    <span className="text-xl font-bold text-emerald-600 dark:text-emerald-400">
                      {analysisResult.coveragePercentage}%
                    </span>
                  </div>
                </div>

                {/* Summary Alert */}
                <div
                  className={`p-4 rounded-xl border flex items-start space-x-3 text-sm ${
                    analysisResult.missingCount === 0
                      ? "bg-emerald-50 dark:bg-emerald-950/30 border-emerald-200 dark:border-emerald-800 text-emerald-900 dark:text-emerald-200"
                      : "bg-amber-50 dark:bg-amber-950/30 border-amber-200 dark:border-amber-800 text-amber-900 dark:text-amber-200"
                  }`}
                >
                  {analysisResult.missingCount === 0 ? (
                    <CheckCircle className="w-5 h-5 text-emerald-600 flex-shrink-0 mt-0.5" />
                  ) : (
                    <AlertTriangle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
                  )}
                  <div>
                    <strong className="font-semibold block">
                      {analysisResult.protocolName} (v{analysisResult.protocolVersion})
                    </strong>
                    <p className="text-xs mt-0.5">{analysisResult.summaryMessage}</p>
                  </div>
                </div>

                {/* Filter Pills */}
                <div className="flex items-center justify-between">
                  <div className="flex space-x-2">
                    <button
                      onClick={() => setFilterRole("ALL")}
                      className={`px-3 py-1 text-xs rounded-full font-medium transition ${
                        filterRole === "ALL"
                          ? "bg-slate-900 dark:bg-slate-100 text-white dark:text-slate-900"
                          : "bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400"
                      }`}
                    >
                      All Components ({analysisResult.nodes.length})
                    </button>
                    <button
                      onClick={() => setFilterRole("BLUE")}
                      className={`px-3 py-1 text-xs rounded-full font-medium transition ${
                        filterRole === "BLUE"
                          ? "bg-blue-600 text-white"
                          : "bg-blue-100 dark:bg-blue-950 text-blue-700 dark:text-blue-300"
                      }`}
                    >
                      Blue (Data) ({analysisResult.blueCount})
                    </button>
                    <button
                      onClick={() => setFilterRole("GREEN")}
                      className={`px-3 py-1 text-xs rounded-full font-medium transition ${
                        filterRole === "GREEN"
                          ? "bg-emerald-600 text-white"
                          : "bg-emerald-100 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300"
                      }`}
                    >
                      Green (UI) ({analysisResult.greenCount})
                    </button>
                    {analysisResult.missingCount > 0 && (
                      <button
                        onClick={() => setFilterRole("MISSING")}
                        className={`px-3 py-1 text-xs rounded-full font-medium transition ${
                          filterRole === "MISSING"
                            ? "bg-red-600 text-white"
                            : "bg-red-100 dark:bg-red-950 text-red-700 dark:text-red-300"
                        }`}
                      >
                        Missing ({analysisResult.missingCount})
                      </button>
                    )}
                  </div>

                  <button
                    onClick={() => setActiveSubTab("reconstructed_app")}
                    className="text-xs font-semibold text-blue-600 dark:text-blue-400 hover:underline flex items-center space-x-1"
                  >
                    <span>Launch Web App</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>

                {/* Component List Cards */}
                <div className="space-x-0 space-y-2.5 max-h-[560px] overflow-y-auto pr-1">
                  {filteredNodes.map((node) => {
                    const isBlue = node.role === "BLUE_DATA_MANIPULATOR";
                    const isAvailable = node.status === "AVAILABLE";

                    return (
                      <div
                        key={node.localId}
                        className={`p-3.5 rounded-xl border transition ${
                          isAvailable
                            ? isBlue
                              ? "bg-white dark:bg-slate-900 border-blue-200 dark:border-blue-900/50 hover:border-blue-300"
                              : "bg-white dark:bg-slate-900 border-emerald-200 dark:border-emerald-900/50 hover:border-emerald-300"
                            : "bg-red-50/50 dark:bg-red-950/20 border-red-300 dark:border-red-900"
                        }`}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex items-start space-x-3">
                            <span
                              className={`w-2.5 h-2.5 rounded-full mt-1.5 flex-shrink-0 ${
                                isBlue ? "bg-blue-500" : "bg-emerald-500"
                              }`}
                            />
                            <div>
                              <div className="flex items-center space-x-2">
                                <span className="text-xs font-mono px-1.5 py-0.5 bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 rounded font-bold">
                                  #{node.localId}
                                </span>
                                <h4 className="text-sm font-bold text-slate-900 dark:text-slate-100">
                                  {node.visualName}
                                </h4>
                              </div>

                              <div className="flex items-center space-x-2 text-xs text-slate-500 mt-1">
                                <span>Core: <strong className="text-slate-700 dark:text-slate-300">{node.coreName}</strong></span>
                                <span>•</span>
                                <span className="font-mono text-[11px] truncate max-w-[200px]" title={node.componentType}>
                                  {node.componentType}
                                </span>
                              </div>
                            </div>
                          </div>

                          <div className="flex items-center space-x-2">
                            <span
                              className={`px-2 py-0.5 text-[11px] font-bold rounded-full uppercase tracking-wider ${
                                isBlue
                                  ? "bg-blue-100 dark:bg-blue-950 text-blue-700 dark:text-blue-300"
                                  : "bg-emerald-100 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300"
                              }`}
                            >
                              {isBlue ? "Blue (Data)" : "Green (UI)"}
                            </span>

                            {isAvailable ? (
                              <span className="px-2 py-0.5 text-[11px] font-bold bg-emerald-100 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300 rounded-full flex items-center space-x-1">
                                <Check className="w-3 h-3" />
                                <span>Mapped</span>
                              </span>
                            ) : (
                              <span className="px-2 py-0.5 text-[11px] font-bold bg-red-100 dark:bg-red-950 text-red-700 dark:text-red-300 rounded-full flex items-center space-x-1">
                                <X className="w-3 h-3" />
                                <span>Missing</span>
                              </span>
                            )}
                          </div>
                        </div>

                        {/* Missing Remediation Note */}
                        {node.remediationNote && (
                          <div className="mt-2 text-xs text-red-700 dark:text-red-300 bg-red-100/50 dark:bg-red-950/50 p-2 rounded border border-red-200 dark:border-red-900">
                            <strong>Remediation Notice:</strong> {node.remediationNote}
                          </div>
                        )}

                        {/* Parameters preview */}
                        {Object.keys(node.parameters).length > 0 && (
                          <div className="mt-2.5 pt-2 border-t border-slate-100 dark:border-slate-800/80 flex flex-wrap gap-1.5">
                            {Object.entries(node.parameters).map(([k, v]) => (
                              <span
                                key={k}
                                className="text-[11px] font-mono px-2 py-0.5 bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 rounded"
                              >
                                {k}: {String(v)}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* TAB 2: Reconstructed Web Application (Live Executable) */}
      {activeSubTab === "reconstructed_app" && (
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-sm space-y-6">
          <div className="border-b border-slate-200 dark:border-slate-800 pb-4 flex items-center justify-between">
            <div>
              <span className="text-xs font-semibold text-emerald-600 dark:text-emerald-400 uppercase tracking-wider">
                Synthesized Web Application
              </span>
              <h2 className="text-xl font-bold text-slate-900 dark:text-slate-100">
                {analysisResult?.protocolName || "Biovia ELN Analytical Attachment Portal"}
              </h2>
              <p className="text-xs text-slate-500 mt-0.5">
                Automatically generated from Green UI components and powered by Blue Python pipeline components.
              </p>
            </div>

            <button
              onClick={handleExecuteReconstructedApp}
              disabled={isExecutingApp}
              className="px-5 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-semibold rounded-lg shadow flex items-center space-x-2 transition disabled:opacity-50"
            >
              {isExecutingApp ? (
                <RefreshCw className="w-4 h-4 animate-spin" />
              ) : (
                <Play className="w-4 h-4 fill-white" />
              )}
              <span>Run Pipeline Application</span>
            </button>
          </div>

          {/* Interactive UI Fields generated from Green Components */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                  Target Experiment Number
                </label>
                <input
                  type="text"
                  value={formValues.exp_number}
                  onChange={(e) => setFormValues({ ...formValues, exp_number: e.target.value })}
                  placeholder="e.g. EXP-2026-XRF-01"
                  className="w-full text-sm p-2.5 bg-slate-50 dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                  Biovia Notebook Server URL
                </label>
                <input
                  type="text"
                  value={formValues.notebook_url}
                  onChange={(e) => setFormValues({ ...formValues, notebook_url: e.target.value })}
                  className="w-full text-sm p-2.5 bg-slate-50 dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none"
                />
              </div>
            </div>

            {/* Document Upload Zone */}
            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                Document File Attachments (Excel, PDF, Word, PowerPoint)
              </label>
              <div className="border-2 border-dashed border-slate-300 dark:border-slate-700 rounded-xl p-5 text-center bg-slate-50 dark:bg-slate-950/50 hover:bg-slate-100/50 transition">
                <Upload className="w-8 h-8 mx-auto text-slate-400 mb-2" />
                <p className="text-xs text-slate-600 dark:text-slate-300 font-medium">
                  Drag and drop files or click to add attachments
                </p>
                <p className="text-[11px] text-slate-400 mt-1">
                  Supported: .xlsx, .pdf, .docx, .pptx, .png
                </p>
                <input
                  type="file"
                  multiple
                  className="mt-3 text-xs"
                  onChange={(e) => {
                    const files = Array.from(e.target.files || []).map((f) => f.name);
                    if (files.length > 0) setUploadedFiles([...uploadedFiles, ...files]);
                  }}
                />
              </div>

              {/* Uploaded File Pills */}
              <div className="flex flex-wrap gap-2 mt-3">
                {uploadedFiles.map((fn, idx) => (
                  <span
                    key={idx}
                    className="inline-flex items-center space-x-1.5 px-2.5 py-1 text-xs bg-slate-200 dark:bg-slate-800 text-slate-800 dark:text-slate-200 rounded-md font-mono"
                  >
                    <FileText className="w-3.5 h-3.5 text-blue-500" />
                    <span>{fn}</span>
                    <button
                      onClick={() => setUploadedFiles(uploadedFiles.filter((_, i) => i !== idx))}
                      className="text-slate-400 hover:text-red-500"
                    >
                      ×
                    </button>
                  </span>
                ))}
              </div>
            </div>
          </div>

          {/* Live Pipeline Flow Visualizer */}
          <div className="bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-xl p-4">
            <h3 className="text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-3">
              Executed Component Flow (Reusing Python Implementations)
            </h3>
            <div className="flex flex-wrap items-center gap-2">
              {(analysisResult?.nodes || []).map((node, i) => (
                <React.Fragment key={node.localId}>
                  <div
                    className={`px-3 py-1.5 rounded-lg border text-xs font-semibold flex items-center space-x-1.5 ${
                      node.role === "BLUE_DATA_MANIPULATOR"
                        ? "bg-blue-50 dark:bg-blue-950/40 border-blue-300 dark:border-blue-800 text-blue-700 dark:text-blue-300"
                        : "bg-emerald-50 dark:bg-emerald-950/40 border-emerald-300 dark:border-emerald-800 text-emerald-700 dark:text-emerald-300"
                    }`}
                  >
                    <span
                      className={`w-2 h-2 rounded-full ${
                        node.role === "BLUE_DATA_MANIPULATOR" ? "bg-blue-500" : "bg-emerald-500"
                      }`}
                    />
                    <span>{node.visualName}</span>
                  </div>
                  {i < (analysisResult?.nodes.length || 0) - 1 && (
                    <ArrowRight className="w-3.5 h-3.5 text-slate-400" />
                  )}
                </React.Fragment>
              ))}
            </div>
          </div>

          {/* Results Display */}
          {appExecutionResult && (
            <div className="border border-emerald-200 dark:border-emerald-900 bg-emerald-50/50 dark:bg-emerald-950/20 rounded-xl p-5 space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <CheckCircle className="w-5 h-5 text-emerald-600" />
                  <h4 className="text-sm font-bold text-emerald-900 dark:text-emerald-200">
                    Application Execution Succeeded
                  </h4>
                </div>
                <span className="text-xs font-mono text-emerald-700 dark:text-emerald-400">
                  {appExecutionResult.sectionsCreated} sections created
                </span>
              </div>

              {/* Sections Table */}
              <div className="overflow-x-auto">
                <table className="w-full text-xs text-left">
                  <thead className="bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 font-semibold">
                    <tr>
                      <th className="p-2">Section ID</th>
                      <th className="p-2">Section Title</th>
                      <th className="p-2">Section Type</th>
                      <th className="p-2">Associated Files</th>
                      <th className="p-2">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-200 dark:divide-slate-800">
                    {(appExecutionResult.sections || []).map((sec: any) => (
                      <tr key={sec.sectionId} className="hover:bg-slate-50 dark:hover:bg-slate-800/50">
                        <td className="p-2 font-mono">{sec.sectionId}</td>
                        <td className="p-2 font-medium">{sec.sectionTitle}</td>
                        <td className="p-2">
                          <span className="px-2 py-0.5 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded font-semibold text-[10px]">
                            {sec.sectionType}
                          </span>
                        </td>
                        <td className="p-2 font-mono text-slate-500">
                          {sec.files?.join(", ") || "-"}
                        </td>
                        <td className="p-2 text-emerald-600 font-semibold">Ready for Notebook</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}

      {/* TAB 3: 1:1 Screenshot Migration Studio */}
      {activeSubTab === "ui_comparison" && (
        <div className="space-y-6">
          {/* Controls Bar */}
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4 flex flex-wrap items-center justify-between gap-4 shadow-sm">
            <div className="flex items-center space-x-3">
              <label className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold rounded-lg shadow cursor-pointer flex items-center space-x-2 transition">
                <Upload className="w-4 h-4" />
                <span>Upload Original PLP Screenshot</span>
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleScreenshotUpload}
                  className="hidden"
                />
              </label>

              {screenshotUrl && (
                <button
                  onClick={() => setScreenshotUrl(null)}
                  className="text-xs text-red-500 hover:underline"
                >
                  Clear Screenshot
                </button>
              )}
            </div>

            <div className="flex items-center space-x-6">
              {/* Mode Selector */}
              <div className="flex items-center space-x-2 bg-slate-100 dark:bg-slate-800 p-1 rounded-lg text-xs">
                <button
                  onClick={() => setCompareMode("side_by_side")}
                  className={`px-3 py-1 rounded-md font-medium transition ${
                    compareMode === "side_by_side"
                      ? "bg-white dark:bg-slate-700 text-slate-900 dark:text-slate-100 shadow-sm"
                      : "text-slate-500"
                  }`}
                >
                  Side-by-Side
                </button>
                <button
                  onClick={() => setCompareMode("overlay")}
                  className={`px-3 py-1 rounded-md font-medium transition ${
                    compareMode === "overlay"
                      ? "bg-white dark:bg-slate-700 text-slate-900 dark:text-slate-100 shadow-sm"
                      : "text-slate-500"
                  }`}
                >
                  Diff Overlay Slider
                </button>
                <button
                  onClick={() => setCompareMode("reconstructed_only")}
                  className={`px-3 py-1 rounded-md font-medium transition ${
                    compareMode === "reconstructed_only"
                      ? "bg-white dark:bg-slate-700 text-slate-900 dark:text-slate-100 shadow-sm"
                      : "text-slate-500"
                  }`}
                >
                  Reconstructed Only
                </button>
              </div>

              {/* Opacity Slider for Overlay */}
              {compareMode === "overlay" && (
                <div className="flex items-center space-x-2 text-xs">
                  <Sliders className="w-3.5 h-3.5 text-slate-500" />
                  <span className="text-slate-600 dark:text-slate-400">Screenshot Opacity: {opacity}%</span>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={opacity}
                    onChange={(e) => setOpacity(Number(e.target.value))}
                    className="w-28 cursor-pointer"
                  />
                </div>
              )}
            </div>
          </div>

          {/* Comparison Canvas */}
          {compareMode === "side_by_side" && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Left: Original Biovia PLP Screenshot */}
              <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 shadow-sm">
                <div className="flex items-center justify-between mb-3 border-b border-slate-100 dark:border-slate-800 pb-2">
                  <span className="text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider">
                    Original Biovia PLP UI Screenshot
                  </span>
                  <span className="text-[11px] px-2 py-0.5 bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 rounded">
                    Source Reference
                  </span>
                </div>

                {screenshotUrl ? (
                  <div className="border border-slate-200 dark:border-slate-800 rounded-lg overflow-hidden max-h-[600px] flex items-center justify-center bg-slate-950">
                    <img
                      src={screenshotUrl}
                      alt="Original Biovia PLP Interface"
                      className="object-contain w-full h-auto max-h-[600px]"
                    />
                  </div>
                ) : (
                  <div className="border-2 border-dashed border-slate-200 dark:border-slate-800 rounded-xl p-12 text-center text-slate-400">
                    <Monitor className="w-12 h-12 mx-auto mb-2 text-slate-300 dark:text-slate-700" />
                    <p className="text-xs font-medium text-slate-600 dark:text-slate-400">
                      No screenshot uploaded yet
                    </p>
                    <p className="text-[11px] text-slate-400 mt-1 max-w-xs mx-auto">
                      Upload the screenshot of how the web application looks in Biovia PLP so we can verify exact 1:1 UI alignment.
                    </p>
                  </div>
                )}
              </div>

              {/* Right: Reconstructed Live Application */}
              <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 shadow-sm">
                <div className="flex items-center justify-between mb-3 border-b border-slate-100 dark:border-slate-800 pb-2">
                  <span className="text-xs font-bold text-emerald-600 dark:text-emerald-400 uppercase tracking-wider">
                    Migrated Live Web Application (React + Python)
                  </span>
                  <span className="text-[11px] px-2 py-0.5 bg-emerald-100 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300 rounded font-semibold">
                    1:1 Migration Target
                  </span>
                </div>

                {/* Live Form Mimicking PLP UI */}
                <div className="space-y-4 p-4 border border-slate-200 dark:border-slate-800 rounded-lg bg-slate-50/50 dark:bg-slate-950/50">
                  <div className="border-b border-slate-200 dark:border-slate-800 pb-3">
                    <h3 className="text-base font-bold text-slate-900 dark:text-slate-100">
                      {analysisResult?.protocolName || "Analytical Lab Section Ingestion"}
                    </h3>
                    <p className="text-xs text-slate-500">Biovia Notebook Automated Ingestion</p>
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                      Target Experiment Number:
                    </label>
                    <input
                      type="text"
                      value={formValues.exp_number}
                      onChange={(e) => setFormValues({ ...formValues, exp_number: e.target.value })}
                      className="w-full text-xs p-2 bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-700 rounded"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                      Select Files to Attach:
                    </label>
                    <div className="border border-slate-300 dark:border-slate-700 rounded p-3 bg-white dark:bg-slate-900 text-xs">
                      {uploadedFiles.map((f, i) => (
                        <div key={i} className="flex items-center space-x-2 py-1 font-mono text-slate-600 dark:text-slate-300">
                          <Check className="w-3.5 h-3.5 text-emerald-500" />
                          <span>{f}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <button
                    onClick={handleExecuteReconstructedApp}
                    disabled={isExecutingApp}
                    className="w-full py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold rounded shadow transition"
                  >
                    {isExecutingApp ? "Processing with Python Pipeline..." : "Process and Sync to Biovia Notebook"}
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Overlay Diff Mode */}
          {compareMode === "overlay" && (
            <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 relative min-h-[500px]">
              <div className="relative w-full overflow-hidden border border-slate-200 dark:border-slate-800 rounded-lg">
                {/* Underlay: Live App */}
                <div className="p-8 bg-slate-50 dark:bg-slate-950">
                  <h2 className="text-xl font-bold mb-2">Biovia Notebook Automated Ingestion Portal</h2>
                  <div className="space-y-4 max-w-md">
                    <div>
                      <label className="text-xs font-bold block mb-1">Experiment Number:</label>
                      <input
                        type="text"
                        readOnly
                        value={formValues.exp_number}
                        className="w-full p-2 border rounded text-xs"
                      />
                    </div>
                    <div>
                      <label className="text-xs font-bold block mb-1">Attached Files:</label>
                      <div className="p-2 border rounded text-xs bg-white">
                        {uploadedFiles.join(", ")}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Overlay: Screenshot with variable opacity */}
                {screenshotUrl && (
                  <img
                    src={screenshotUrl}
                    alt="PLP Reference Overlay"
                    style={{ opacity: opacity / 100 }}
                    className="absolute inset-0 w-full h-full object-cover pointer-events-none"
                  />
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
