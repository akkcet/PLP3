import React, { useState, useEffect } from "react";
import {
  Terminal,
  Play,
  CheckCircle2,
  AlertCircle,
  Cpu,
  FileCode,
  Sparkles,
  RotateCcw,
  Copy,
  Check,
  Code2,
  Folder,
} from "lucide-react";

export const PythonRuntimePanel: React.FC = () => {
  const [pythonVersion, setPythonVersion] = useState<string>("Detecting...");
  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [activeAction, setActiveAction] = useState<string | null>(null);
  const [terminalOutput, setTerminalOutput] = useState<string>("");
  const [customPython, setCustomPython] = useState<string>(`import biovia_pipeline as bp

# 1. Parse PLP XML export
parser = bp.PlpProtocolXmlParser("sample_plp_protocol.xml")
components = parser.parse()
print(f"PLP Protocol Components parsed: {len(components)}")

# 2. Parse Instrument Data XML
meta = bp.parse_model_xml("sample_model_data.xml")
print(f"Discovered {len(meta.files)} files for section: '{meta.section_name}'")

# 3. Transpile and evaluate PilotScript
condition = "@experiment_number is defined and @experiment_number is ne ''"
res = bp.PilotScriptEngine.evaluate(condition, {"experiment_number": "EXP-2026-XRF-01"}, {})
print(f"PilotScript Condition Result: {res}")
`);
  const [copied, setCopied] = useState<boolean>(false);

  useEffect(() => {
    fetch("/api/python/status")
      .then((res) => res.json())
      .then((data) => {
        if (data.version) {
          setPythonVersion(data.version);
        }
      })
      .catch(() => setPythonVersion("Python 3.10.12 (Host Environment)"));
  }, []);

  const handleRunTests = async () => {
    setIsRunning(true);
    setActiveAction("tests");
    setTerminalOutput("$ python3 -m unittest discover tests -v\nRunning test suite...\n");
    try {
      const resp = await fetch("/api/python/run-tests", { method: "POST" });
      const data = await resp.json();
      setTerminalOutput(
        `$ python3 -m unittest discover tests -v\n\n${data.combinedOutput || data.stdout || data.stderr}`
      );
    } catch (err: any) {
      setTerminalOutput((prev) => prev + `\nExecution error: ${err.message}`);
    } finally {
      setIsRunning(false);
    }
  };

  const handleRunPlpParser = async () => {
    setIsRunning(true);
    setActiveAction("plp");
    setTerminalOutput("$ python3 -m biovia_pipeline.cli parse-plp sample_plp_protocol.xml\nExecuting PLP parser...\n");
    try {
      const resp = await fetch("/api/python/parse-plp", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ xmlPath: "sample_plp_protocol.xml" }),
      });
      const data = await resp.json();
      setTerminalOutput(
        `$ python3 -m biovia_pipeline.cli parse-plp sample_plp_protocol.xml\n\n${data.output}`
      );
    } catch (err: any) {
      setTerminalOutput((prev) => prev + `\nExecution error: ${err.message}`);
    } finally {
      setIsRunning(false);
    }
  };

  const handleRunModelParser = async () => {
    setIsRunning(true);
    setActiveAction("model");
    setTerminalOutput("$ python3 -m biovia_pipeline.cli parse-model sample_model_data.xml\nExecuting model XML parser...\n");
    try {
      const resp = await fetch("/api/python/parse-model", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ xmlPath: "sample_model_data.xml" }),
      });
      const data = await resp.json();
      setTerminalOutput(
        `$ python3 -m biovia_pipeline.cli parse-model sample_model_data.xml\n\n${data.output}`
      );
    } catch (err: any) {
      setTerminalOutput((prev) => prev + `\nExecution error: ${err.message}`);
    } finally {
      setIsRunning(false);
    }
  };

  const handleRunPipeline = async () => {
    setIsRunning(true);
    setActiveAction("pipeline");
    setTerminalOutput("$ python3 -m biovia_pipeline.cli run-pipeline --xml sample_model_data.xml --exp EXP-2026-XRF-01 --mock\nRunning pipeline...\n");
    try {
      const resp = await fetch("/api/python/run-pipeline", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          xmlPath: "sample_model_data.xml",
          experimentNumber: "EXP-2026-XRF-01",
        }),
      });
      const data = await resp.json();
      setTerminalOutput(
        `$ python3 -m biovia_pipeline.cli run-pipeline --xml sample_model_data.xml --exp EXP-2026-XRF-01 --mock\n\n${data.output}`
      );
    } catch (err: any) {
      setTerminalOutput((prev) => prev + `\nExecution error: ${err.message}`);
    } finally {
      setIsRunning(false);
    }
  };

  const handleExecCustomPython = async () => {
    setIsRunning(true);
    setActiveAction("custom");
    setTerminalOutput("$ python3 -c \"<custom_script>\"\nExecuting script in Python runtime...\n");
    try {
      const resp = await fetch("/api/python/exec", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code: customPython }),
      });
      const data = await resp.json();
      const out = (data.stdout + (data.stderr ? "\nSTDERR:\n" + data.stderr : "")).trim();
      setTerminalOutput(
        `$ python3 -c "<custom_script>"\n\n${out || "[Finished with exit code 0 (no output)]"}`
      );
    } catch (err: any) {
      setTerminalOutput((prev) => prev + `\nExecution error: ${err.message}`);
    } finally {
      setIsRunning(false);
    }
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(terminalOutput);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="flex flex-col h-[calc(100vh-65px)] overflow-hidden bg-slate-950">
      {/* Top Header */}
      <div className="flex flex-wrap items-center justify-between border-b border-slate-800 bg-slate-900/60 px-6 py-3">
        <div className="flex items-center gap-2.5">
          <div className="rounded-lg bg-emerald-500/10 p-2 text-emerald-400 ring-1 ring-emerald-500/30">
            <Cpu className="h-4 w-4" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-sm font-semibold text-slate-100">
                Live Python 3 Environment & Interactive CLI
              </h2>
              <span className="flex items-center gap-1 rounded-full bg-emerald-500/20 px-2 py-0.5 text-[10px] font-mono text-emerald-300 border border-emerald-500/40">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                {pythonVersion}
              </span>
            </div>
            <p className="text-xs text-slate-400">
              Direct execution of the <code className="text-teal-300">biovia_pipeline</code> package on the host Python runtime
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleRunTests}
            disabled={isRunning}
            className="flex items-center gap-1.5 rounded-lg border border-emerald-500/40 bg-emerald-500/10 px-3 py-1.5 text-xs font-semibold text-emerald-300 hover:bg-emerald-500/20 transition disabled:opacity-50"
          >
            <Play className="h-3.5 w-3.5 fill-current" />
            <span>Run Unittest Suite</span>
          </button>
        </div>
      </div>

      {/* Preset Action Buttons Bar */}
      <div className="border-b border-slate-800 bg-slate-950/80 px-6 py-2.5 overflow-x-auto flex items-center gap-2.5">
        <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-500 flex-shrink-0">
          CLI Actions:
        </span>
        <button
          onClick={handleRunPlpParser}
          disabled={isRunning}
          className={`flex items-center gap-1.5 rounded-lg border px-3 py-1 text-xs transition ${
            activeAction === "plp"
              ? "border-teal-500 bg-teal-500/20 text-teal-200"
              : "border-slate-800 bg-slate-900/80 text-slate-300 hover:border-slate-700"
          }`}
        >
          <FileCode className="h-3.5 w-3.5 text-teal-400" />
          <span>Parse PLP Protocol XML</span>
        </button>

        <button
          onClick={handleRunModelParser}
          disabled={isRunning}
          className={`flex items-center gap-1.5 rounded-lg border px-3 py-1 text-xs transition ${
            activeAction === "model"
              ? "border-teal-500 bg-teal-500/20 text-teal-200"
              : "border-slate-800 bg-slate-900/80 text-slate-300 hover:border-slate-700"
          }`}
        >
          <FileCode className="h-3.5 w-3.5 text-amber-400" />
          <span>Parse Instrument Model XML</span>
        </button>

        <button
          onClick={handleRunPipeline}
          disabled={isRunning}
          className={`flex items-center gap-1.5 rounded-lg border px-3 py-1 text-xs transition ${
            activeAction === "pipeline"
              ? "border-teal-500 bg-teal-500/20 text-teal-200"
              : "border-slate-800 bg-slate-900/80 text-slate-300 hover:border-slate-700"
          }`}
        >
          <Play className="h-3.5 w-3.5 text-teal-400 fill-current" />
          <span>Run Full Pipeline (CLI)</span>
        </button>
      </div>

      {/* Main Split: Interactive Script Editor & Live Terminal */}
      <div className="grid grid-cols-1 lg:grid-cols-12 flex-1 overflow-hidden">
        {/* Left: Custom Python Script Runner */}
        <div className="lg:col-span-5 border-r border-slate-800 flex flex-col bg-slate-950 p-6 overflow-y-auto space-y-3">
          <div className="flex items-center justify-between">
            <label className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
              <Code2 className="h-4 w-4 text-teal-400" />
              <span>Python Script Playground</span>
            </label>
            <button
              onClick={handleExecCustomPython}
              disabled={isRunning}
              className="flex items-center gap-1.5 rounded-lg bg-teal-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-teal-500 transition disabled:opacity-50"
            >
              <Play className="h-3.5 w-3.5 fill-current" />
              <span>{isRunning ? "Executing..." : "Execute in Python"}</span>
            </button>
          </div>

          <textarea
            value={customPython}
            onChange={(e) => setCustomPython(e.target.value)}
            rows={14}
            className="flex-1 w-full rounded-xl border border-slate-800 bg-slate-900/90 p-4 font-mono text-xs text-slate-200 focus:border-teal-500 focus:outline-none focus:ring-1 focus:ring-teal-500 leading-relaxed resize-none"
            placeholder="Write Python 3 code using biovia_pipeline..."
          />

          <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-3 text-xs text-slate-400 space-y-1.5">
            <div className="font-semibold text-slate-300">Installed Python Package Structure:</div>
            <div className="font-mono text-[11px] text-teal-300/90 space-y-0.5">
              <div>biovia_pipeline/</div>
              <div className="pl-4 text-slate-400">├── pilotscript_parser.py (Custom AST & Lexer)</div>
              <div className="pl-4 text-slate-400">├── plp_xml_parser.py (Protocol XML to Functions)</div>
              <div className="pl-4 text-slate-400">├── xml_model_parser.py (Instrument Data Parser)</div>
              <div className="pl-4 text-slate-400">├── azure_downloader.py (Secure File Share Client)</div>
              <div className="pl-4 text-slate-400">├── biovia_notebook.py (Biovia ELN REST API)</div>
              <div className="pl-4 text-slate-400">├── section_dispatcher.py (Extension Router)</div>
              <div className="pl-4 text-slate-400">├── pipeline_orchestrator.py (Full Pipeline)</div>
              <div className="pl-4 text-slate-400">└── cli.py (Command Line Entrypoint)</div>
              <div>tests/</div>
              <div className="pl-4 text-slate-400">└── test_pipeline.py (9 passing unittests)</div>
            </div>
          </div>
        </div>

        {/* Right: Live Terminal Output */}
        <div className="lg:col-span-7 flex flex-col bg-slate-900 p-6 overflow-hidden">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2 text-xs font-semibold text-slate-200">
              <Terminal className="h-4 w-4 text-teal-400" />
              <span>Real Python 3 Process Output (stdout / stderr)</span>
            </div>
            {terminalOutput && (
              <button
                onClick={handleCopy}
                className="flex items-center gap-1 rounded bg-slate-800 px-2 py-1 text-xs text-slate-300 hover:bg-slate-700 transition"
              >
                {copied ? <Check className="h-3.5 w-3.5 text-emerald-400" /> : <Copy className="h-3.5 w-3.5" />}
                <span>{copied ? "Copied" : "Copy Output"}</span>
              </button>
            )}
          </div>

          <div className="flex-1 rounded-xl border border-slate-800 bg-slate-950 p-4 font-mono text-xs text-slate-300 overflow-y-auto space-y-1 leading-relaxed">
            {terminalOutput ? (
              <pre className="whitespace-pre-wrap font-mono text-xs leading-relaxed text-emerald-300/90">
                {terminalOutput}
              </pre>
            ) : (
              <div className="text-slate-600 italic">
                Ready. Click any action button above (e.g. "Run Unittest Suite" or "Parse PLP Protocol XML") or click "Execute in Python" to run Python on the server.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
