import React, { useState } from "react";
import { PlpComponent } from "../types/pipeline";
import { PLP_COMPONENTS } from "../data/protocolData";
import {
  FileText,
  Filter,
  Terminal,
  Database,
  Trash2,
  CheckCircle2,
  Layers,
  ArrowRight,
  Code2,
  Copy,
  Check,
  ExternalLink,
  Shield,
  Eye,
} from "lucide-react";

interface PipelineCanvasProps {
  onSelectComponentForRepl?: (script: string) => void;
  onNavigateToCode?: (filename: string) => void;
}

export const PipelineCanvas: React.FC<PipelineCanvasProps> = ({
  onSelectComponentForRepl,
  onNavigateToCode,
}) => {
  const [selectedId, setSelectedId] = useState<string>("node_22");
  const [copied, setCopied] = useState<boolean>(false);
  const [viewMode, setViewMode] = useState<"visual" | "table">("visual");

  const selectedComponent = PLP_COMPONENTS.find((c) => c.id === selectedId) || PLP_COMPONENTS[0];

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const getNodeIcon = (type: PlpComponent["type"]) => {
    switch (type) {
      case "filter":
        return Filter;
      case "python":
        return Terminal;
      case "file_op":
        return Trash2;
      case "notebook":
        return Database;
      case "subprotocol":
        return Layers;
      default:
        return FileText;
    }
  };

  const getNodeColor = (type: PlpComponent["type"], isSelected: boolean) => {
    if (isSelected) {
      return "border-teal-400 bg-teal-950/70 text-teal-200 ring-2 ring-teal-500/50 shadow-lg shadow-teal-950/50";
    }
    switch (type) {
      case "filter":
        return "border-amber-500/40 bg-amber-950/20 text-amber-200 hover:border-amber-400";
      case "python":
        return "border-blue-500/40 bg-blue-950/20 text-blue-200 hover:border-blue-400";
      case "file_op":
        return "border-rose-500/40 bg-rose-950/20 text-rose-200 hover:border-rose-400";
      case "notebook":
        return "border-emerald-500/40 bg-emerald-950/20 text-emerald-200 hover:border-emerald-400";
      case "subprotocol":
        return "border-cyan-500/40 bg-cyan-950/20 text-cyan-200 hover:border-cyan-400";
      default:
        return "border-slate-700 bg-slate-800/40 text-slate-300 hover:border-slate-500";
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-65px)] overflow-hidden">
      {/* Top Controls Bar */}
      <div className="flex flex-wrap items-center justify-between border-b border-slate-800 bg-slate-900/60 px-4 py-2.5 sm:px-6">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
              Protocol Canvas Flow
            </span>
            <span className="rounded bg-slate-800 px-2 py-0.5 text-xs text-slate-300">
              {PLP_COMPONENTS.length} Components Mapped
            </span>
          </div>
          <div className="hidden sm:flex items-center gap-2 text-xs text-slate-400">
            <span className="inline-block h-2 w-2 rounded-full bg-emerald-400"></span>
            <span>Refactored to 8 Modular Python Files</span>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <div className="flex rounded-lg bg-slate-950 p-0.5 border border-slate-800 text-xs">
            <button
              onClick={() => setViewMode("visual")}
              className={`rounded px-2.5 py-1 font-medium transition ${
                viewMode === "visual" ? "bg-slate-800 text-teal-300" : "text-slate-400 hover:text-slate-200"
              }`}
            >
              Interactive DAG
            </button>
            <button
              onClick={() => setViewMode("table")}
              className={`rounded px-2.5 py-1 font-medium transition ${
                viewMode === "table" ? "bg-slate-800 text-teal-300" : "text-slate-400 hover:text-slate-200"
              }`}
            >
              Component Table
            </button>
          </div>
        </div>
      </div>

      {/* Main split view: DAG Canvas on left, Inspector on right */}
      <div className="grid grid-cols-1 lg:grid-cols-12 flex-1 overflow-hidden">
        {/* Left Side: Canvas / Workflow Graph */}
        <div className="lg:col-span-7 xl:col-span-8 flex flex-col border-r border-slate-800 overflow-y-auto bg-slate-950/70 p-4 sm:p-6">
          {viewMode === "visual" ? (
            <div className="space-y-6">
              {/* Branch 1: Pre-Execution Cleanup */}
              <div className="rounded-xl border border-slate-800/80 bg-slate-900/40 p-4">
                <div className="text-xs font-semibold text-slate-400 mb-3 flex items-center gap-2">
                  <span className="h-2 w-2 rounded-full bg-rose-400"></span>
                  Phase 0: Pre-Run Workspace Teardown
                </div>
                <div className="flex items-center gap-4">
                  {PLP_COMPONENTS.filter((c) => c.id === "node_56").map((comp) => {
                    const Icon = getNodeIcon(comp.type);
                    const isSelected = selectedId === comp.id;
                    return (
                      <button
                        key={comp.id}
                        onClick={() => setSelectedId(comp.id)}
                        className={`flex items-center gap-3 rounded-xl border p-3 text-left transition-all ${getNodeColor(
                          comp.type,
                          isSelected
                        )}`}
                      >
                        <div className="rounded-lg bg-slate-900/80 p-2">
                          <Icon className="h-5 w-5" />
                        </div>
                        <div>
                          <div className="text-xs font-semibold text-slate-100">{comp.displayName}</div>
                          <div className="text-[11px] text-slate-400 font-mono">E:\Model Data Transfer\...</div>
                        </div>
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Branch 2: Web Form & XML Submission */}
              <div className="rounded-xl border border-slate-800/80 bg-slate-900/40 p-4">
                <div className="text-xs font-semibold text-slate-400 mb-3 flex items-center gap-2">
                  <span className="h-2 w-2 rounded-full bg-amber-400"></span>
                  Phase 1 & 2: Client Web Form & Model XML Parsing
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3 items-center">
                  {PLP_COMPONENTS.filter((c) => ["node_59", "node_44", "node_22", "node_28"].includes(c.id)).map(
                    (comp, index) => {
                      const Icon = getNodeIcon(comp.type);
                      const isSelected = selectedId === comp.id;
                      return (
                        <div key={comp.id} className="flex items-center gap-2">
                          <button
                            onClick={() => setSelectedId(comp.id)}
                            className={`w-full flex items-center gap-2.5 rounded-xl border p-3 text-left transition-all ${getNodeColor(
                              comp.type,
                              isSelected
                            )}`}
                          >
                            <div className="rounded-lg bg-slate-900/80 p-2 flex-shrink-0">
                              <Icon className="h-4 w-4" />
                            </div>
                            <div className="overflow-hidden">
                              <div className="text-xs font-semibold truncate text-slate-100">{comp.displayName}</div>
                              <div className="text-[10px] text-slate-400 truncate">
                                {comp.pilotScript ? "PilotScript Condition" : comp.mappedPythonFunction.functionName}
                              </div>
                            </div>
                          </button>
                          {index < 3 && <ArrowRight className="h-4 w-4 text-slate-600 flex-shrink-0 hidden md:block" />}
                        </div>
                      );
                    }
                  )}
                </div>
              </div>

              {/* Branch 3: Azure Downloader & Biovia Notebook Dispatcher */}
              <div className="rounded-xl border border-slate-800/80 bg-slate-900/40 p-4">
                <div className="text-xs font-semibold text-slate-400 mb-3 flex items-center gap-2">
                  <span className="h-2 w-2 rounded-full bg-teal-400"></span>
                  Phase 3: Azure File Share Download & Biovia Notebook Section Dispatch
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3">
                  {PLP_COMPONENTS.filter((c) =>
                    ["node_47", "node_54", "node_46", "node_51", "node_53", "node_24", "node_55"].includes(c.id)
                  ).map((comp) => {
                    const Icon = getNodeIcon(comp.type);
                    const isSelected = selectedId === comp.id;
                    return (
                      <button
                        key={comp.id}
                        onClick={() => setSelectedId(comp.id)}
                        className={`flex items-start gap-2.5 rounded-xl border p-3 text-left transition-all ${getNodeColor(
                          comp.type,
                          isSelected
                        )}`}
                      >
                        <div className="rounded-lg bg-slate-900/80 p-2 flex-shrink-0 mt-0.5">
                          <Icon className="h-4 w-4" />
                        </div>
                        <div className="overflow-hidden">
                          <div className="text-xs font-semibold text-slate-100">{comp.displayName}</div>
                          <div className="text-[10px] text-slate-400 font-mono mt-0.5 truncate">
                            {comp.mappedPythonFunction.module}.{comp.mappedPythonFunction.functionName}
                          </div>
                          {comp.threatAnalysis && (
                            <div className="mt-1 flex items-center gap-1 text-[10px] text-amber-400/90">
                              <Shield className="h-3 w-3" />
                              <span>Security Hardened</span>
                            </div>
                          )}
                        </div>
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Data Flow Legend */}
              <div className="flex flex-wrap items-center gap-4 text-xs text-slate-400 p-2">
                <span className="font-semibold text-slate-300">Legend:</span>
                <span className="flex items-center gap-1.5">
                  <span className="h-2.5 w-2.5 rounded border border-amber-500 bg-amber-500/20"></span>
                  PilotScript Gatekeeper Filter
                </span>
                <span className="flex items-center gap-1.5">
                  <span className="h-2.5 w-2.5 rounded border border-blue-500 bg-blue-500/20"></span>
                  Server-side Python Logic
                </span>
                <span className="flex items-center gap-1.5">
                  <span className="h-2.5 w-2.5 rounded border border-cyan-500 bg-cyan-500/20"></span>
                  Subprotocol / Section Dispatcher
                </span>
                <span className="flex items-center gap-1.5">
                  <span className="h-2.5 w-2.5 rounded border border-emerald-500 bg-emerald-500/20"></span>
                  Biovia Notebook ELN API
                </span>
              </div>
            </div>
          ) : (
            /* Table View */
            <div className="rounded-xl border border-slate-800 overflow-hidden bg-slate-900/60">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-950 text-slate-400 uppercase tracking-wider font-semibold border-b border-slate-800">
                  <tr>
                    <th className="p-3">Component</th>
                    <th className="p-3">Type</th>
                    <th className="p-3">Mapped Python Function</th>
                    <th className="p-3">PilotScript / Logic</th>
                    <th className="p-3 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800">
                  {PLP_COMPONENTS.map((comp) => (
                    <tr
                      key={comp.id}
                      onClick={() => setSelectedId(comp.id)}
                      className={`cursor-pointer transition ${
                        selectedId === comp.id ? "bg-teal-950/40 text-teal-200" : "hover:bg-slate-800/40"
                      }`}
                    >
                      <td className="p-3 font-medium text-slate-200">{comp.displayName}</td>
                      <td className="p-3">
                        <span className="rounded bg-slate-800 px-2 py-0.5 font-mono text-[11px] text-slate-300">
                          {comp.type}
                        </span>
                      </td>
                      <td className="p-3 font-mono text-teal-300">{comp.mappedPythonFunction.functionName}</td>
                      <td className="p-3 text-slate-400 truncate max-w-xs font-mono text-[11px]">
                        {comp.pilotScript || "Native Python Component"}
                      </td>
                      <td className="p-3 text-right">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            setSelectedId(comp.id);
                          }}
                          className="rounded bg-slate-800 px-2.5 py-1 text-xs text-slate-200 hover:bg-teal-600 hover:text-white transition"
                        >
                          Inspect
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Right Side: Component Inspector */}
        <div className="lg:col-span-5 xl:col-span-4 flex flex-col overflow-y-auto bg-slate-900 p-4 sm:p-6 space-y-5">
          {/* Component Header */}
          <div className="border-b border-slate-800 pb-4">
            <div className="flex items-center justify-between">
              <span className="rounded bg-teal-950 px-2.5 py-0.5 text-xs font-semibold text-teal-400 border border-teal-800 uppercase tracking-wide">
                {selectedComponent.type}
              </span>
              <span className="font-mono text-xs text-slate-500">ID: {selectedComponent.id}</span>
            </div>
            <h2 className="text-lg font-bold text-slate-100 mt-2">{selectedComponent.displayName}</h2>
            <p className="text-xs text-slate-400 mt-1">{selectedComponent.description}</p>
          </div>

          {/* PilotScript section if exists */}
          {selectedComponent.pilotScript && (
            <div className="rounded-xl border border-amber-500/30 bg-amber-950/20 p-3 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-amber-300 flex items-center gap-1.5">
                  <Filter className="h-3.5 w-3.5" />
                  Original PilotScript Expression
                </span>
                {onSelectComponentForRepl && (
                  <button
                    onClick={() => onSelectComponentForRepl(selectedComponent.pilotScript!)}
                    className="flex items-center gap-1 text-[11px] text-amber-400 hover:underline"
                  >
                    <span>Test in REPL</span>
                    <ExternalLink className="h-3 w-3" />
                  </button>
                )}
              </div>
              <pre className="overflow-x-auto rounded bg-slate-950 p-2.5 font-mono text-xs text-amber-200 border border-amber-900/50">
                {selectedComponent.pilotScript}
              </pre>
            </div>
          )}

          {/* Embedded Python in PLP if exists */}
          {selectedComponent.pythonScript && (
            <div className="rounded-xl border border-blue-500/30 bg-blue-950/20 p-3 space-y-2">
              <div className="text-xs font-semibold text-blue-300 flex items-center gap-1.5">
                <Terminal className="h-3.5 w-3.5" />
                Original Embedded Python (PilotPython SDK)
              </div>
              <pre className="overflow-x-auto rounded bg-slate-950 p-2.5 font-mono text-xs text-blue-200 max-h-36 border border-blue-900/50">
                {selectedComponent.pythonScript}
              </pre>
            </div>
          )}

          {/* Refactored Clean Python Function */}
          <div className="rounded-xl border border-slate-800 bg-slate-950 p-4 space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Code2 className="h-4 w-4 text-teal-400" />
                <span className="text-xs font-semibold text-slate-200">
                  Refactored Python: <span className="font-mono text-teal-300">{selectedComponent.mappedPythonFunction.functionName}</span>
                </span>
              </div>
              <button
                onClick={() => handleCopy(selectedComponent.mappedPythonFunction.code)}
                className="flex items-center gap-1 rounded bg-slate-800 px-2 py-1 text-xs text-slate-300 hover:bg-slate-700 transition"
              >
                {copied ? <Check className="h-3.5 w-3.5 text-emerald-400" /> : <Copy className="h-3.5 w-3.5" />}
                <span>{copied ? "Copied" : "Copy"}</span>
              </button>
            </div>

            <div className="text-xs text-slate-400">
              Module: <span className="font-mono text-slate-300">{selectedComponent.mappedPythonFunction.module}</span>
            </div>

            <pre className="overflow-x-auto rounded-lg bg-slate-900 p-3 font-mono text-xs text-slate-200 leading-relaxed max-h-64 border border-slate-800">
              {selectedComponent.mappedPythonFunction.code}
            </pre>

            {onNavigateToCode && (
              <button
                onClick={() => onNavigateToCode(selectedComponent.mappedPythonFunction.module)}
                className="w-full rounded-lg border border-slate-700 bg-slate-800/80 px-3 py-1.5 text-xs font-medium text-slate-200 hover:bg-teal-600 hover:text-white transition flex items-center justify-center gap-1.5"
              >
                <Eye className="h-3.5 w-3.5" />
                <span>View Full Module in Code Explorer</span>
              </button>
            )}
          </div>

          {/* Threat Model Insight */}
          {selectedComponent.threatAnalysis && (
            <div className="rounded-xl border border-amber-500/20 bg-amber-950/10 p-3 space-y-1.5 text-xs">
              <div className="font-semibold text-amber-300 flex items-center gap-1.5">
                <Shield className="h-3.5 w-3.5" />
                Security Consideration
              </div>
              <p className="text-slate-400">
                <strong className="text-slate-300">Risk:</strong> {selectedComponent.threatAnalysis.risk}
              </p>
              <p className="text-teal-300/90 font-mono bg-slate-950/70 p-2 rounded border border-slate-800">
                <strong className="text-teal-400">Mitigation:</strong> {selectedComponent.threatAnalysis.countermeasure}
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
