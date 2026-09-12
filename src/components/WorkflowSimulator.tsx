import React, { useState } from "react";
import { SAMPLE_INPUT_XML } from "../data/protocolData";
import { parse_model_xml } from "./../utils/mockPipelineRunner";
import {
  Play,
  RotateCcw,
  CheckCircle2,
  AlertCircle,
  FileCheck,
  Server,
  Database,
  Terminal,
  Clock,
  Layers,
  Sparkles,
} from "lucide-react";

export const WorkflowSimulator: React.FC = () => {
  const [xmlInput, setXmlInput] = useState<string>(SAMPLE_INPUT_XML);
  const [expNumber, setExpNumber] = useState<string>("EXP-2026-XRF-001");
  const [sessionToken, setSessionToken] = useState<string>("sec_tok_enterprise_eln_9941");
  const [selectedFiles, setSelectedFiles] = useState<string[]>([]);
  const [discoveredFiles, setDiscoveredFiles] = useState<any[]>([]);

  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [currentStep, setCurrentStep] = useState<number>(0);
  const [logs, setLogs] = useState<string[]>([]);
  const [executionResult, setExecutionResult] = useState<any | null>(null);

  // Initialize discovered files on load or XML edit
  React.useEffect(() => {
    try {
      const parsed = parse_model_xml(xmlInput);
      setDiscoveredFiles(parsed.files);
      setSelectedFiles(parsed.files.map((f: any) => f.file_name));
    } catch {
      // ignore draft parse error
    }
  }, [xmlInput]);

  const toggleFile = (name: string) => {
    setSelectedFiles((prev) =>
      prev.includes(name) ? prev.filter((f) => f !== name) : [...prev, name]
    );
  };

  const runSimulation = async () => {
    setIsRunning(true);
    setCurrentStep(1);
    setLogs([]);
    setExecutionResult(null);

    const appendLog = (msg: string) => {
      const time = new Date().toLocaleTimeString();
      setLogs((prev) => [...prev, `[${time}] ${msg}`]);
    };

    try {
      // Step 1: Pre-cleanup
      appendLog("STAGE 0: Executing cleanup_directory('E:\\Model Data Transfer\\DownloadedFile')...");
      await new Promise((r) => setTimeout(r, 450));
      appendLog("Workspace staging directory purged. Zero orphan files remaining.");

      // Step 2: XML Parsing
      setCurrentStep(2);
      appendLog("STAGE 1: Parsing model XML with defusedxml...");
      await new Promise((r) => setTimeout(r, 550));
      const modelMeta = parse_model_xml(xmlInput);
      appendLog(`Parsed Section Name: '${modelMeta.section_name}'`);
      appendLog(`Extracted base storage directory: '${modelMeta.base_location}'`);
      appendLog(`Identified ${modelMeta.files.length} candidate files in XML.`);

      // Step 3: File Selection Check
      setCurrentStep(3);
      appendLog(`STAGE 2: Validating file selection list (${selectedFiles.length} files selected)...`);
      await new Promise((r) => setTimeout(r, 400));
      if (selectedFiles.length === 0) {
        throw new Error("No files selected! Selection required to proceed.");
      }
      appendLog(`Verified ${selectedFiles.length} files approved by operator.`);

      // Step 4: Azure Download Simulation
      setCurrentStep(4);
      appendLog("STAGE 3: Connecting to Azure File Share 'rdplp-sbx1' (using AZURE_STORAGE_KEY)...");
      await new Promise((r) => setTimeout(r, 650));
      for (const f of selectedFiles) {
        appendLog(`[Azure] Stream downloaded '${f}' -> Staging /tmp/biovia_downloads/${f}`);
      }
      appendLog(`All ${selectedFiles.length} files secured in temporary staging.`);

      // Step 5: Notebook Connection & Experiment Query
      setCurrentStep(5);
      appendLog(`STAGE 4: Querying Biovia Notebook API for experiment '${expNumber}'...`);
      await new Promise((r) => setTimeout(r, 550));
      const expId = `EXP_${expNumber}_UUID_772`;
      appendLog(`Target experiment verified in Notebook: ID = ${expId} (Status: Not Submitted)`);

      // Step 6: Dispatch Sections by File Extension
      setCurrentStep(6);
      appendLog("STAGE 5: Dispatching sections to Biovia Notebook by file extension...");
      const sectionsCreated: any[] = [];

      for (const f of selectedFiles) {
        await new Promise((r) => setTimeout(r, 350));
        const fileObj = modelMeta.files.find((item: any) => item.file_name === f);
        const title = fileObj?.section_title || f;
        const ext = f.slice(f.lastIndexOf(".")).toLowerCase();

        let secType = "attachment";
        if (ext === ".pdf") secType = "pdf";
        else if (ext.includes("xls")) secType = "excel";
        else if (ext.includes("ppt")) secType = "powerpoint";
        else if (ext.includes("doc")) secType = "word";

        const secId = `sec_${Math.floor(Math.random() * 90000) + 10000}`;
        sectionsCreated.push({
          fileName: f,
          sectionType: secType,
          sectionTitle: title,
          sectionId: secId,
        });
        appendLog(`[ELN Upload] Created ${secType.toUpperCase()} section '${title}' (ID: ${secId})`);
      }

      // Step 7: Notebook Commit
      setCurrentStep(7);
      appendLog(`STAGE 6: Committing transaction to Biovia Notebook for experiment ${expId}...`);
      await new Promise((r) => setTimeout(r, 500));
      appendLog("Experiment committed and persisted in ELN database!");

      // Step 8: Post Cleanup
      setCurrentStep(8);
      appendLog("STAGE 7: Post-run cleanup: Deleting temporary files in staging...");
      await new Promise((r) => setTimeout(r, 300));
      appendLog("Cleanup completed. Session closed cleanly.");

      setExecutionResult({
        success: true,
        experimentNumber: expNumber,
        experimentId: expId,
        sectionsCount: sectionsCreated.length,
        sections: sectionsCreated,
        duration: "3.75s",
      });
    } catch (err: any) {
      appendLog(`ERROR: Pipeline terminated: ${err.message}`);
      setExecutionResult({
        success: false,
        error: err.message,
      });
    } finally {
      setIsRunning(false);
    }
  };

  const stepsList = [
    { num: 1, label: "0. Pre-Cleanup" },
    { num: 2, label: "1. Parse XML" },
    { num: 3, label: "2. Verify Files" },
    { num: 4, label: "3. Azure Download" },
    { num: 5, label: "4. Query ELN" },
    { num: 6, label: "5. Dispatch Sections" },
    { num: 7, label: "6. Commit Notebook" },
    { num: 8, label: "7. Teardown" },
  ];

  return (
    <div className="flex flex-col h-[calc(100vh-65px)] overflow-hidden">
      {/* Top action header */}
      <div className="flex items-center justify-between border-b border-slate-800 bg-slate-900/60 px-6 py-3">
        <div className="flex items-center gap-3">
          <div className="rounded-lg bg-teal-500/10 p-2 text-teal-400 ring-1 ring-teal-500/30">
            <Play className="h-4 w-4" />
          </div>
          <div>
            <h2 className="text-sm font-semibold text-slate-100">
              Interactive Workflow Dry-Run Simulator
            </h2>
            <p className="text-xs text-slate-400">
              Step through the refactored Python pipeline logic with sample model XML and Biovia Notebook payloads
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            id="btn-run-simulation"
            onClick={runSimulation}
            disabled={isRunning}
            className="flex items-center gap-1.5 rounded-lg bg-teal-600 px-4 py-1.5 text-xs font-semibold text-white hover:bg-teal-500 transition disabled:opacity-50 shadow-sm"
          >
            <Play className="h-3.5 w-3.5 fill-current" />
            <span>{isRunning ? "Executing Pipeline..." : "Execute Dry-Run"}</span>
          </button>
        </div>
      </div>

      {/* Stepper Bar */}
      <div className="border-b border-slate-800 bg-slate-950 px-6 py-2.5 overflow-x-auto">
        <div className="flex items-center justify-between min-w-[700px]">
          {stepsList.map((st) => {
            const isDone = currentStep > st.num || (currentStep === 8 && executionResult?.success);
            const isCurrent = currentStep === st.num && isRunning;
            return (
              <div key={st.num} className="flex items-center gap-2">
                <div
                  className={`flex h-6 w-6 items-center justify-center rounded-full text-xs font-semibold border ${
                    isDone
                      ? "border-emerald-500 bg-emerald-500/20 text-emerald-300"
                      : isCurrent
                      ? "border-teal-400 bg-teal-500/30 text-teal-200 animate-pulse"
                      : "border-slate-800 bg-slate-900 text-slate-500"
                  }`}
                >
                  {isDone ? <CheckCircle2 className="h-4 w-4" /> : st.num}
                </div>
                <span
                  className={`text-xs ${
                    isDone || isCurrent ? "text-slate-200 font-medium" : "text-slate-500"
                  }`}
                >
                  {st.label}
                </span>
                {st.num < 8 && <div className="h-0.5 w-6 bg-slate-800 hidden sm:block"></div>}
              </div>
            );
          })}
        </div>
      </div>

      {/* Main split */}
      <div className="grid grid-cols-1 lg:grid-cols-12 flex-1 overflow-hidden">
        {/* Left Inputs */}
        <div className="lg:col-span-5 border-r border-slate-800 bg-slate-950 p-6 overflow-y-auto space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div className="space-y-1">
              <label className="text-xs font-semibold text-slate-300">Target Experiment Number</label>
              <input
                type="text"
                value={expNumber}
                onChange={(e) => setExpNumber(e.target.value)}
                className="w-full rounded-lg border border-slate-800 bg-slate-900 p-2 font-mono text-xs text-teal-300 focus:border-teal-500 focus:outline-none"
              />
            </div>
            <div className="space-y-1">
              <label className="text-xs font-semibold text-slate-300">Session Token</label>
              <input
                type="password"
                value={sessionToken}
                onChange={(e) => setSessionToken(e.target.value)}
                className="w-full rounded-lg border border-slate-800 bg-slate-900 p-2 font-mono text-xs text-slate-400 focus:border-teal-500 focus:outline-none"
              />
            </div>
          </div>

          {/* Model XML Input */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between">
              <label className="text-xs font-semibold text-slate-300">
                Sample Instrument / Model Export XML
              </label>
              <button
                onClick={() => setXmlInput(SAMPLE_INPUT_XML)}
                className="text-[11px] text-teal-400 hover:underline"
              >
                Reset Default XML
              </button>
            </div>
            <textarea
              value={xmlInput}
              onChange={(e) => setXmlInput(e.target.value)}
              rows={8}
              className="w-full rounded-xl border border-slate-800 bg-slate-900 p-3 font-mono text-xs text-slate-300 focus:border-teal-500 focus:outline-none leading-relaxed"
            />
          </div>

          {/* Discovered Files Selector (replicates PLP List Box component) */}
          <div className="space-y-2">
            <label className="text-xs font-semibold text-slate-300 flex items-center justify-between">
              <span>Files Discovered for ELN Transfer ({discoveredFiles.length})</span>
              <span className="text-[11px] text-slate-500">Select files to upload</span>
            </label>
            <div className="space-y-1.5 rounded-xl border border-slate-800 bg-slate-900/60 p-3 max-h-48 overflow-y-auto">
              {discoveredFiles.map((file, idx) => {
                const isChecked = selectedFiles.includes(file.file_name);
                return (
                  <div
                    key={idx}
                    onClick={() => toggleFile(file.file_name)}
                    className={`flex items-center justify-between rounded-lg p-2 text-xs cursor-pointer border transition ${
                      isChecked
                        ? "bg-teal-950/40 border-teal-800/80 text-teal-200"
                        : "bg-slate-900/50 border-slate-800/60 text-slate-400 hover:bg-slate-800"
                    }`}
                  >
                    <div className="flex items-center gap-2 truncate">
                      <input
                        type="checkbox"
                        checked={isChecked}
                        onChange={() => {}}
                        className="rounded border-slate-700 text-teal-600 focus:ring-teal-500"
                      />
                      <span className="font-mono text-[11px] truncate">{file.file_name}</span>
                    </div>
                    <span className="rounded bg-slate-800 px-1.5 py-0.5 text-[10px] font-mono text-slate-400">
                      {file.extension}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Right Output: Execution Console & Results */}
        <div className="lg:col-span-7 flex flex-col bg-slate-900 p-6 overflow-y-auto space-y-4">
          {/* Execution summary banner */}
          {executionResult && (
            <div
              className={`rounded-xl border p-4 text-xs ${
                executionResult.success
                  ? "border-emerald-500/40 bg-emerald-950/20 text-emerald-200"
                  : "border-rose-500/40 bg-rose-950/20 text-rose-200"
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="font-bold flex items-center gap-1.5 text-sm">
                  {executionResult.success ? (
                    <CheckCircle2 className="h-5 w-5 text-emerald-400" />
                  ) : (
                    <AlertCircle className="h-5 w-5 text-rose-400" />
                  )}
                  {executionResult.success
                    ? "Upload to Biovia Notebook Successful!"
                    : "Pipeline Execution Failed"}
                </span>
                <span className="font-mono text-xs">{executionResult.duration}</span>
              </div>
              {executionResult.success && (
                <p className="text-slate-300">
                  {executionResult.sectionsCount} sections created and committed to Experiment{" "}
                  <strong className="text-teal-300 font-mono">{executionResult.experimentNumber}</strong>.
                  Please return to Biovia Notebook to review attached data items.
                </p>
              )}
            </div>
          )}

          {/* Terminal Logs */}
          <div className="space-y-1.5 flex-1 flex flex-col">
            <div className="flex items-center justify-between text-xs font-semibold text-slate-300">
              <span className="flex items-center gap-1.5">
                <Terminal className="h-4 w-4 text-teal-400" />
                Execution Trace Logs
              </span>
              <span className="font-mono text-[11px] text-slate-500">{logs.length} events</span>
            </div>
            <div className="flex-1 rounded-xl border border-slate-800 bg-slate-950 p-4 font-mono text-xs text-slate-300 overflow-y-auto min-h-[220px] space-y-1 leading-relaxed">
              {logs.length === 0 ? (
                <div className="text-slate-600 italic">Ready. Click "Execute Dry-Run" to simulate the automated pipeline.</div>
              ) : (
                logs.map((line, i) => (
                  <div key={i} className={line.includes("ERROR") ? "text-rose-400" : line.includes("SUCCESS") || line.includes("committed") ? "text-emerald-300" : line.includes("STAGE") ? "text-amber-300 font-bold" : "text-slate-300"}>
                    {line}
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Sections Result Table if completed */}
          {executionResult?.sections && (
            <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-4 space-y-2 text-xs">
              <div className="font-semibold text-slate-200">Biovia Notebook Committed Sections Payload</div>
              <div className="overflow-x-auto">
                <table className="w-full text-left">
                  <thead className="border-b border-slate-800 font-semibold text-slate-400 text-[11px]">
                    <tr>
                      <th className="pb-1.5">File Name</th>
                      <th className="pb-1.5">Section Type</th>
                      <th className="pb-1.5">Assigned Section Title</th>
                      <th className="pb-1.5 text-right">Notebook Section ID</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-850 font-mono text-[11px]">
                    {executionResult.sections.map((sec: any, idx: number) => (
                      <tr key={idx}>
                        <td className="py-1.5 text-slate-300">{sec.fileName}</td>
                        <td className="py-1.5">
                          <span className="rounded bg-slate-800 px-1.5 py-0.5 text-[10px] text-teal-300">
                            {sec.sectionType}
                          </span>
                        </td>
                        <td className="py-1.5 text-slate-400">{sec.sectionTitle}</td>
                        <td className="py-1.5 text-right text-emerald-400">{sec.sectionId}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
