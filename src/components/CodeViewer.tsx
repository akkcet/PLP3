import React, { useState } from "react";
import { PYTHON_CODEBASE } from "../data/pythonCodebase";
import { PythonModuleFile } from "../types/pipeline";
import {
  Folder,
  FileCode,
  Copy,
  Check,
  Download,
  Terminal,
  FileText,
  Layers,
  Box,
  CheckCircle2,
} from "lucide-react";
import JSZip from "jszip";

interface CodeViewerProps {
  initialFile?: string;
}

export const CodeViewer: React.FC<CodeViewerProps> = ({ initialFile }) => {
  const [selectedFile, setSelectedFile] = useState<PythonModuleFile>(() => {
    if (initialFile) {
      const match = PYTHON_CODEBASE.find((f) => f.path.includes(initialFile) || f.filename.includes(initialFile));
      if (match) return match;
    }
    return PYTHON_CODEBASE[0];
  });

  const [copied, setCopied] = useState<boolean>(false);
  const [isZipping, setIsZipping] = useState<boolean>(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(selectedFile.code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownloadSingle = () => {
    const blob = new Blob([selectedFile.code], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = selectedFile.filename;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleDownloadZip = async () => {
    setIsZipping(true);
    try {
      const zip = new JSZip();
      const folder = zip.folder("biovia_python_suite");

      PYTHON_CODEBASE.forEach((file) => {
        folder?.file(file.path, file.code);
      });

      // Add a quick requirements.txt
      folder?.file(
        "requirements.txt",
        `azure-storage-file-share>=12.15.0
requests>=2.31.0
defusedxml>=0.7.1
pytest>=8.0.0
pydantic>=2.5.0
`
      );

      const content = await zip.generateAsync({ type: "blob" });
      const url = URL.createObjectURL(content);
      const a = document.createElement("a");
      a.href = url;
      a.download = "biovia_python_suite.zip";
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error("ZIP creation failed:", err);
    } finally {
      setIsZipping(false);
    }
  };

  const getCategoryBadge = (cat: PythonModuleFile["category"]) => {
    switch (cat) {
      case "core":
        return "bg-blue-950 text-blue-300 border-blue-800";
      case "parser":
        return "bg-amber-950 text-amber-300 border-amber-800";
      case "integrations":
        return "bg-teal-950 text-teal-300 border-teal-800";
      case "orchestrator":
        return "bg-purple-950 text-purple-300 border-purple-800";
      case "cli":
        return "bg-rose-950 text-rose-300 border-rose-800";
      case "tests":
        return "bg-emerald-950 text-emerald-300 border-emerald-800";
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-65px)] overflow-hidden">
      {/* Top action bar */}
      <div className="flex items-center justify-between border-b border-slate-800 bg-slate-900/60 px-6 py-3">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <Box className="h-4 w-4 text-teal-400" />
            <h2 className="text-sm font-semibold text-slate-100">
              Refactored Python Architecture
            </h2>
          </div>
          <span className="text-xs text-slate-400">
            {PYTHON_CODEBASE.length} modules • Production-Ready Type-Annotated
          </span>
        </div>

        <div className="flex items-center gap-2">
          <button
            id="btn-copy-code"
            onClick={handleCopy}
            className="flex items-center gap-1.5 rounded-lg border border-slate-700 bg-slate-800 px-3 py-1.5 text-xs font-medium text-slate-200 hover:bg-slate-700 transition"
          >
            {copied ? <Check className="h-3.5 w-3.5 text-emerald-400" /> : <Copy className="h-3.5 w-3.5" />}
            <span>{copied ? "Copied" : "Copy File"}</span>
          </button>

          <button
            id="btn-download-single"
            onClick={handleDownloadSingle}
            className="flex items-center gap-1.5 rounded-lg border border-slate-700 bg-slate-800 px-3 py-1.5 text-xs font-medium text-slate-200 hover:bg-slate-700 transition"
          >
            <Download className="h-3.5 w-3.5" />
            <span>Download {selectedFile.filename}</span>
          </button>

          <button
            id="btn-download-zip"
            onClick={handleDownloadZip}
            disabled={isZipping}
            className="flex items-center gap-1.5 rounded-lg bg-teal-600 px-3 py-1.5 text-xs font-semibold text-white shadow-sm hover:bg-teal-500 transition disabled:opacity-50"
          >
            <Download className="h-3.5 w-3.5" />
            <span>{isZipping ? "Generating ZIP..." : "Download Full Package (.ZIP)"}</span>
          </button>
        </div>
      </div>

      {/* Main split: File Tree + Code Editor */}
      <div className="grid grid-cols-1 lg:grid-cols-12 flex-1 overflow-hidden">
        {/* Left Tree Explorer */}
        <div className="lg:col-span-4 xl:col-span-3 border-r border-slate-800 bg-slate-950 p-4 overflow-y-auto space-y-4">
          <div>
            <div className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">
              <Folder className="h-3.5 w-3.5" />
              <span>biovia_pipeline/</span>
            </div>
            <div className="space-y-1">
              {PYTHON_CODEBASE.filter((f) => !f.path.startsWith("tests")).map((file) => {
                const isSelected = selectedFile.path === file.path;
                return (
                  <button
                    key={file.path}
                    onClick={() => setSelectedFile(file)}
                    className={`w-full flex items-center justify-between rounded-lg px-2.5 py-2 text-left text-xs transition ${
                      isSelected
                        ? "bg-teal-950/80 text-teal-200 font-medium border border-teal-800/80"
                        : "text-slate-400 hover:bg-slate-900 hover:text-slate-200"
                    }`}
                  >
                    <div className="flex items-center gap-2 truncate">
                      <FileCode className={`h-4 w-4 flex-shrink-0 ${isSelected ? "text-teal-400" : "text-slate-500"}`} />
                      <span className="truncate">{file.filename}</span>
                    </div>
                    <span className={`text-[10px] px-1.5 py-0.2 rounded border font-mono ${getCategoryBadge(file.category)}`}>
                      {file.category}
                    </span>
                  </button>
                );
              })}
            </div>
          </div>

          <div>
            <div className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">
              <Folder className="h-3.5 w-3.5" />
              <span>tests/</span>
            </div>
            <div className="space-y-1">
              {PYTHON_CODEBASE.filter((f) => f.path.startsWith("tests")).map((file) => {
                const isSelected = selectedFile.path === file.path;
                return (
                  <button
                    key={file.path}
                    onClick={() => setSelectedFile(file)}
                    className={`w-full flex items-center justify-between rounded-lg px-2.5 py-2 text-left text-xs transition ${
                      isSelected
                        ? "bg-teal-950/80 text-teal-200 font-medium border border-teal-800/80"
                        : "text-slate-400 hover:bg-slate-900 hover:text-slate-200"
                    }`}
                  >
                    <div className="flex items-center gap-2 truncate">
                      <FileCode className={`h-4 w-4 flex-shrink-0 ${isSelected ? "text-teal-400" : "text-slate-500"}`} />
                      <span className="truncate">{file.filename}</span>
                    </div>
                    <span className={`text-[10px] px-1.5 py-0.2 rounded border font-mono ${getCategoryBadge(file.category)}`}>
                      test
                    </span>
                  </button>
                );
              })}
            </div>
          </div>

          <div className="rounded-xl border border-slate-800/90 bg-slate-900/60 p-3 text-xs text-slate-400 space-y-1.5">
            <div className="font-semibold text-slate-300 flex items-center gap-1.5">
              <CheckCircle2 className="h-3.5 w-3.5 text-teal-400" />
              <span>Enterprise Highlights</span>
            </div>
            <ul className="list-disc list-inside space-y-1 text-[11px] text-slate-400">
              <li>Replaces hardcoded Azure keys with Secret Manager</li>
              <li>Pure Python PilotScript AST Parser & Transpiler</li>
              <li>Safe XML handling via defusedxml</li>
              <li>Official REST client for Biovia Notebook v2</li>
              <li>Zero dependencies on deprecated Java PLP plugins</li>
            </ul>
          </div>
        </div>

        {/* Right Code Editor Display */}
        <div className="lg:col-span-8 xl:col-span-9 flex flex-col bg-slate-900 overflow-hidden">
          {/* File Tab Header */}
          <div className="border-b border-slate-800 bg-slate-950/40 px-6 py-2.5 flex items-center justify-between">
            <div>
              <div className="flex items-center gap-2">
                <span className="font-mono text-xs font-semibold text-slate-200">{selectedFile.path}</span>
                <span className={`text-[10px] px-2 py-0.5 rounded border font-mono ${getCategoryBadge(selectedFile.category)}`}>
                  {selectedFile.category}
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-0.5">{selectedFile.description}</p>
            </div>
            <span className="font-mono text-xs text-slate-500">
              {selectedFile.code.split("\n").length} lines
            </span>
          </div>

          {/* Code Content */}
          <div className="flex-1 overflow-auto p-6 font-mono text-xs bg-slate-950 text-slate-200">
            <pre className="leading-relaxed">
              <code>{selectedFile.code}</code>
            </pre>
          </div>
        </div>
      </div>
    </div>
  );
};
