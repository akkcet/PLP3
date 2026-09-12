import React, { useState, useEffect } from "react";
import { tokenizePilotScript, transpilePilotScriptToPython, evaluatePilotScript } from "../utils/pilotScriptParser";
import { TranspileResult } from "../types/pipeline";
import {
  Terminal,
  Play,
  Copy,
  Check,
  Sparkles,
  RefreshCw,
  HelpCircle,
  Code2,
  CheckCircle2,
  AlertCircle,
} from "lucide-react";

interface PilotScriptReplProps {
  initialScript?: string;
}

const PRESET_EXPRESSIONS = [
  {
    title: "Stage 1 Gatekeeper",
    source: "@experiment_number is defined and @experiment_number is ne '' and @filelocation is eq ''",
    description: "Gatekeeper in Node 59 to prompt user for XML upload.",
    defaultGlobals: { experiment_number: "EXP-2026-XRF-01", filelocation: "" },
    defaultRecord: {},
  },
  {
    title: "Stage 2 File List Gatekeeper",
    source: "@xml is defined and @xml ne '' and @filelist is eq ''",
    description: "Gatekeeper in Node 44 verifying XML source provided before file selection.",
    defaultGlobals: { xml: "userdata:/demo_XRF.xml", filelist: "" },
    defaultRecord: {},
  },
  {
    title: "Stage 3 Execution Trigger",
    source: "@filelist is defined and @filelist is ne ''",
    description: "Gatekeeper in Node 47 verifying files were selected for Azure download.",
    defaultGlobals: { filelist: ["Quant_Analysis.pdf", "Curves.xlsx"] },
    defaultRecord: {},
  },
  {
    title: "PDF File Type Check",
    source: "findsubstring(DocRelativepath, '.pdf')>1",
    description: "Filter in Node 4 inside section subprotocol checking for PDF extension.",
    defaultGlobals: {},
    defaultRecord: { DocRelativepath: "Quant_Analysis_Summary.pdf" },
  },
  {
    title: "Excel File Type Check",
    source: "findsubstring(DocRelativepath, '.xlsx')>1",
    description: "Filter in Node 6 inside section subprotocol checking for Excel extension.",
    defaultGlobals: {},
    defaultRecord: { DocRelativepath: "Calibration_Curves.xlsx" },
  },
  {
    title: "Section Title Hash Lookup",
    source: `IF (HashContains(@_xmltitle, DocRelativepath)) THEN
  @sec_title := HashFind(@_xmltitle, DocRelativepath);
END IF;`,
    description: "Custom Manipulator in Node 23 mapping file name to XML title from hashtable.",
    defaultGlobals: {
      _xmltitle: { "Quant_Analysis_Summary.pdf": "Spectroscopy: Quantitative Report" },
    },
    defaultRecord: { DocRelativepath: "Quant_Analysis_Summary.pdf" },
  },
  {
    title: "Section Name Substring Sanitizer",
    source: `@sectionName := Substring(SectionName, FindSubstring(SectionName, ':') + 2, StringLen(SectionName));
@location := location;`,
    description: "Custom Manipulator in Node 28 stripping prefix before colon in section title.",
    defaultGlobals: {},
    defaultRecord: { SectionName: "Spectroscopy: Quantitative Report", location: "users/analyst/runs" },
  },
];

export const PilotScriptRepl: React.FC<PilotScriptReplProps> = ({ initialScript }) => {
  const [script, setScript] = useState<string>(
    initialScript || PRESET_EXPRESSIONS[0].source
  );
  const [globalsInput, setGlobalsInput] = useState<string>(
    JSON.stringify(PRESET_EXPRESSIONS[0].defaultGlobals, null, 2)
  );
  const [recordInput, setRecordInput] = useState<string>(
    JSON.stringify(PRESET_EXPRESSIONS[0].defaultRecord, null, 2)
  );
  const [result, setResult] = useState<TranspileResult | null>(null);
  const [copied, setCopied] = useState<boolean>(false);
  const [aiLoading, setAiLoading] = useState<boolean>(false);
  const [aiAnalysis, setAiAnalysis] = useState<string | null>(null);

  useEffect(() => {
    runTranspilation();
  }, [script, globalsInput, recordInput]);

  const runTranspilation = () => {
    let parsedGlobals = {};
    let parsedRecord = {};

    try {
      parsedGlobals = JSON.parse(globalsInput);
    } catch {
      // ignore JSON parse error in draft
    }

    try {
      parsedRecord = JSON.parse(recordInput);
    } catch {
      // ignore
    }

    const res = transpilePilotScriptToPython(script, {
      globals: parsedGlobals,
      record: parsedRecord,
    });
    setResult(res);
  };

  const handleSelectPreset = (preset: (typeof PRESET_EXPRESSIONS)[0]) => {
    setScript(preset.source);
    setGlobalsInput(JSON.stringify(preset.defaultGlobals, null, 2));
    setRecordInput(JSON.stringify(preset.defaultRecord, null, 2));
    setAiAnalysis(null);
  };

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleAiTranspile = async () => {
    setAiLoading(true);
    try {
      const resp = await fetch("/api/ai/transpile-expression", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          expression: script,
          contextVariables: {
            globals: JSON.parse(globalsInput || "{}"),
            record: JSON.parse(recordInput || "{}"),
          },
        }),
      });
      const data = await resp.json();
      if (data.pythonCode) {
        setAiAnalysis(data.pythonCode);
      } else if (data.error) {
        setAiAnalysis(`AI Service Notice: ${data.error}`);
      }
    } catch (err: any) {
      setAiAnalysis(`Request error: ${err.message}`);
    } finally {
      setAiLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-65px)] overflow-hidden">
      {/* Top Header */}
      <div className="flex flex-wrap items-center justify-between border-b border-slate-800 bg-slate-900/60 px-6 py-3">
        <div className="flex items-center gap-2.5">
          <div className="rounded-lg bg-amber-500/10 p-2 text-amber-400 ring-1 ring-amber-500/30">
            <Terminal className="h-4 w-4" />
          </div>
          <div>
            <h2 className="text-sm font-semibold text-slate-100">
              PilotScript Custom Parser & AST Transpiler
            </h2>
            <p className="text-xs text-slate-400">
              Translates proprietary Pipeline Pilot expression syntax into executable Python 3.11+ logic
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleAiTranspile}
            disabled={aiLoading}
            className="flex items-center gap-1.5 rounded-lg border border-teal-500/40 bg-teal-500/10 px-3 py-1.5 text-xs font-semibold text-teal-300 hover:bg-teal-500/20 transition disabled:opacity-50"
          >
            <Sparkles className="h-3.5 w-3.5 text-teal-400" />
            <span>{aiLoading ? "Consulting Gemini..." : "Deep AI Transpile"}</span>
          </button>
        </div>
      </div>

      {/* Preset pills */}
      <div className="border-b border-slate-800 bg-slate-950/60 px-6 py-2 overflow-x-auto flex items-center gap-2">
        <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 flex-shrink-0">
          PLP Presets:
        </span>
        {PRESET_EXPRESSIONS.map((preset, idx) => (
          <button
            key={idx}
            onClick={() => handleSelectPreset(preset)}
            className="rounded-lg border border-slate-800 bg-slate-900/80 px-2.5 py-1 text-xs text-slate-300 hover:border-teal-500/50 hover:text-teal-300 whitespace-nowrap transition"
          >
            {preset.title}
          </button>
        ))}
      </div>

      {/* Split workbench */}
      <div className="grid grid-cols-1 lg:grid-cols-12 flex-1 overflow-hidden">
        {/* Left column: PilotScript Editor & Mock Context */}
        <div className="lg:col-span-6 border-r border-slate-800 flex flex-col bg-slate-950 p-6 overflow-y-auto space-y-4">
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <label className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
                <span>PilotScript Input Expression</span>
                <span className="text-[11px] text-slate-500">(PLP Syntax)</span>
              </label>
              <span className="text-[11px] text-slate-400 font-mono">
                {script.split("\n").length} lines
              </span>
            </div>
            <textarea
              value={script}
              onChange={(e) => setScript(e.target.value)}
              rows={6}
              className="w-full rounded-xl border border-slate-700 bg-slate-900 p-3 font-mono text-xs text-amber-200 focus:border-teal-500 focus:outline-none focus:ring-1 focus:ring-teal-500 leading-relaxed"
              placeholder="e.g. @experiment_number is defined and @experiment_number is ne ''..."
            />
          </div>

          {/* Context Variables (Globals and Record) */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-slate-400">
                Protocol Globals (@variables) JSON
              </label>
              <textarea
                value={globalsInput}
                onChange={(e) => setGlobalsInput(e.target.value)}
                rows={5}
                className="w-full rounded-lg border border-slate-800 bg-slate-900/90 p-2.5 font-mono text-xs text-slate-200 focus:border-teal-500 focus:outline-none"
              />
            </div>
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-slate-400">
                Data Record Properties (doc/file) JSON
              </label>
              <textarea
                value={recordInput}
                onChange={(e) => setRecordInput(e.target.value)}
                rows={5}
                className="w-full rounded-lg border border-slate-800 bg-slate-900/90 p-2.5 font-mono text-xs text-slate-200 focus:border-teal-500 focus:outline-none"
              />
            </div>
          </div>

          {/* Tokens stream preview */}
          {result && (
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-slate-400">Lexer Token Stream</label>
              <div className="flex flex-wrap gap-1.5 rounded-lg border border-slate-800 bg-slate-900/40 p-2.5 max-h-32 overflow-y-auto">
                {result.tokens.map((token, i) => (
                  <span
                    key={i}
                    className={`rounded px-1.5 py-0.5 text-[10px] font-mono border ${
                      token.type === "GLOBAL"
                        ? "bg-purple-950 text-purple-300 border-purple-800"
                        : token.type === "KEYWORD"
                        ? "bg-amber-950 text-amber-300 border-amber-800"
                        : token.type === "FUNCTION"
                        ? "bg-cyan-950 text-cyan-300 border-cyan-800"
                        : token.type === "STRING"
                        ? "bg-emerald-950 text-emerald-300 border-emerald-800"
                        : token.type === "OPERATOR"
                        ? "bg-rose-950 text-rose-300 border-rose-800"
                        : "bg-slate-800 text-slate-300 border-slate-700"
                    }`}
                  >
                    {token.value}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Right column: Transpiled Output & Live Evaluation */}
        <div className="lg:col-span-6 flex flex-col bg-slate-900 p-6 overflow-y-auto space-y-4">
          {/* Live Evaluation Badge */}
          {result?.testEvaluation && (
            <div
              className={`rounded-xl border p-3.5 flex items-center justify-between text-xs ${
                result.testEvaluation.success
                  ? "border-emerald-500/40 bg-emerald-950/20 text-emerald-300"
                  : "border-rose-500/40 bg-rose-950/20 text-rose-300"
              }`}
            >
              <div className="flex items-center gap-2">
                {result.testEvaluation.success ? (
                  <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                ) : (
                  <AlertCircle className="h-4 w-4 text-rose-400" />
                )}
                <span className="font-semibold">Live Evaluation Result:</span>
              </div>
              <div className="font-mono text-sm font-bold">
                {typeof result.testEvaluation.result === "boolean"
                  ? result.testEvaluation.result
                    ? "TRUE (Pass Port)"
                    : "FALSE (Fail Port)"
                  : JSON.stringify(result.testEvaluation.result)}
              </div>
            </div>
          )}

          {/* Transpiled Python Code */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <label className="text-xs font-semibold text-slate-200 flex items-center gap-1.5">
                <Code2 className="h-4 w-4 text-teal-400" />
                <span>Transpiled Python 3.11+ Implementation</span>
              </label>
              <button
                onClick={() => handleCopy(result?.pythonCode || "")}
                className="flex items-center gap-1 rounded bg-slate-800 px-2 py-1 text-xs text-slate-300 hover:bg-slate-700 transition"
              >
                {copied ? <Check className="h-3.5 w-3.5 text-emerald-400" /> : <Copy className="h-3.5 w-3.5" />}
                <span>{copied ? "Copied" : "Copy Python"}</span>
              </button>
            </div>
            <pre className="overflow-x-auto rounded-xl border border-slate-800 bg-slate-950 p-4 font-mono text-xs text-teal-200 leading-relaxed min-h-[120px]">
              {result?.pythonCode || "# No code generated"}
            </pre>
          </div>

          {/* AST Breakdown */}
          {result && result.astSummary.length > 0 && (
            <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-3.5 space-y-2 text-xs">
              <div className="font-semibold text-slate-300">Abstract Syntax Tree (AST) Operations</div>
              <ul className="space-y-1 text-[11px] text-slate-400 font-mono">
                {result.astSummary.map((item, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <span className="text-teal-400">&bull;</span>
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* AI Explanation if queried */}
          {aiAnalysis && (
            <div className="rounded-xl border border-teal-500/30 bg-teal-950/20 p-4 space-y-2 text-xs">
              <div className="font-semibold text-teal-300 flex items-center gap-1.5">
                <Sparkles className="h-4 w-4 text-teal-400" />
                <span>Gemini Architectural Review</span>
              </div>
              <pre className="whitespace-pre-wrap font-mono text-[11px] text-slate-200 bg-slate-950 p-3 rounded-lg border border-teal-900/50 max-h-60 overflow-y-auto">
                {aiAnalysis}
              </pre>
            </div>
          )}

          {/* Semantic mapping notes */}
          <div className="rounded-xl border border-slate-800 bg-slate-950/40 p-3.5 text-xs text-slate-400 space-y-1">
            <div className="font-semibold text-slate-300">Biovia PLP &rarr; Python Translation Rules:</div>
            <p>1. <span className="font-mono text-amber-300">@variable</span> maps to <span className="font-mono text-teal-300">globals["variable"]</span></p>
            <p>2. <span className="font-mono text-amber-300">FindSubstring(str, sub)</span> is 1-indexed in PLP; returns 0 if absent</p>
            <p>3. <span className="font-mono text-amber-300">:=</span> is the assignment operator, transpiled directly to <span className="font-mono text-teal-300">=</span></p>
            <p>4. <span className="font-mono text-amber-300">eq / ne</span> are case-insensitive equality operators</p>
          </div>
        </div>
      </div>
    </div>
  );
};
