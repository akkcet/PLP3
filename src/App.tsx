import React, { useState, useEffect } from "react";
import { Navbar, ActiveTab } from "./components/Navbar";
import { PipelineCanvas } from "./components/PipelineCanvas";
import { CodeViewer } from "./components/CodeViewer";
import { PilotScriptRepl } from "./components/PilotScriptRepl";
import { WorkflowSimulator } from "./components/WorkflowSimulator";
import { XmlInspector } from "./components/XmlInspector";
import { PythonRuntimePanel } from "./components/PythonRuntimePanel";
import { ComponentWorkbench } from "./components/ComponentWorkbench";
import { AiAssistant } from "./components/AiAssistant";
import { ThreatModelModal } from "./components/ThreatModelModal";
import { ProtocolMigrationStudio } from "./components/ProtocolMigrationStudio";

export default function App() {
  const [activeTab, setActiveTab] = useState<ActiveTab>("canvas");
  const [isThreatModalOpen, setIsThreatModalOpen] = useState<boolean>(false);
  const [replScript, setReplScript] = useState<string | undefined>(undefined);
  const [codeFile, setCodeFile] = useState<string | undefined>(undefined);
  const [hasGeminiKey, setHasGeminiKey] = useState<boolean>(false);

  useEffect(() => {
    fetch("/api/health")
      .then((res) => res.json())
      .then((data) => {
        if (data && data.hasGeminiKey) {
          setHasGeminiKey(true);
        }
      })
      .catch(() => {});
  }, []);

  const handleSelectComponentForRepl = (script: string) => {
    setReplScript(script);
    setActiveTab("transpiler");
  };

  const handleNavigateToCode = (filename: string) => {
    setCodeFile(filename);
    setActiveTab("codebase");
  };

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 flex flex-col selection:bg-teal-500 selection:text-white">
      {/* Top Navigation */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onOpenThreats={() => setIsThreatModalOpen(true)}
        hasGeminiKey={hasGeminiKey}
      />

      {/* Main View Area */}
      <main className="flex-1 flex flex-col overflow-hidden">
        {activeTab === "canvas" && (
          <PipelineCanvas
            onSelectComponentForRepl={handleSelectComponentForRepl}
            onNavigateToCode={handleNavigateToCode}
          />
        )}
        {activeTab === "migration" && (
          <div className="flex-1 overflow-y-auto p-4 sm:p-6 max-w-7xl w-full mx-auto">
            <ProtocolMigrationStudio />
          </div>
        )}
        {activeTab === "workbench" && <ComponentWorkbench />}
        {activeTab === "python" && <PythonRuntimePanel />}
        {activeTab === "codebase" && <CodeViewer initialFile={codeFile} />}
        {activeTab === "transpiler" && <PilotScriptRepl initialScript={replScript} />}
        {activeTab === "simulator" && <WorkflowSimulator />}
        {activeTab === "xml" && <XmlInspector />}
        {activeTab === "ai" && <AiAssistant />}
      </main>

      {/* Mandatory Threat Model Modal (Directive 1) */}
      <ThreatModelModal
        isOpen={isThreatModalOpen}
        onClose={() => setIsThreatModalOpen(false)}
      />
    </div>
  );
}
