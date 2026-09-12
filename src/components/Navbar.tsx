import React from "react";
import {
  GitFork,
  Code2,
  Terminal,
  PlayCircle,
  FileCode,
  ShieldAlert,
  Sparkles,
  Layers,
  Cpu,
} from "lucide-react";

export type ActiveTab =
  | "canvas"
  | "codebase"
  | "python"
  | "transpiler"
  | "simulator"
  | "xml"
  | "threats"
  | "ai";

interface NavbarProps {
  activeTab: ActiveTab;
  setActiveTab: (tab: ActiveTab) => void;
  onOpenThreats: () => void;
  hasGeminiKey?: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({
  activeTab,
  setActiveTab,
  onOpenThreats,
  hasGeminiKey,
}) => {
  const navItems: { id: ActiveTab; label: string; icon: React.ComponentType<{ className?: string }> }[] = [
    { id: "canvas", label: "Protocol DAG Canvas", icon: GitFork },
    { id: "python", label: "Python CLI & Runtime", icon: Cpu },
    { id: "codebase", label: "Modular Python Code", icon: Code2 },
    { id: "transpiler", label: "PilotScript Transpiler", icon: Terminal },
    { id: "simulator", label: "Pipeline Dry-Run", icon: PlayCircle },
    { id: "xml", label: "PLP XML Inspector", icon: FileCode },
    { id: "ai", label: "AI Refactor Assistant", icon: Sparkles },
  ];

  return (
    <header className="sticky top-0 z-30 border-b border-slate-800 bg-slate-900/90 backdrop-blur-md">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6">
        {/* Brand & Protocol Tag */}
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-teal-500/10 text-teal-400 ring-1 ring-teal-500/30">
            <Layers className="h-5 w-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-base font-semibold text-slate-100 tracking-tight">
                Biovia PLP to Python Studio
              </h1>
              <span className="rounded bg-teal-950/80 px-2 py-0.5 text-xs font-mono font-medium text-teal-400 border border-teal-800">
                v8.0.0 Refactored
              </span>
            </div>
            <p className="text-xs text-slate-400">
              Protocol: <span className="font-mono text-slate-300">Data model UI</span> &rarr; Clean Python 3.11+ Modules
            </p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="hidden lg:flex items-center gap-1 rounded-xl bg-slate-950/60 p-1 ring-1 ring-slate-800">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                id={`nav-tab-${item.id}`}
                onClick={() => setActiveTab(item.id)}
                className={`flex items-center gap-2 rounded-lg px-3 py-1.5 text-xs font-medium transition-all ${
                  isActive
                    ? "bg-teal-600 text-white shadow-sm ring-1 ring-teal-400/40"
                    : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/60"
                }`}
              >
                <Icon className="h-3.5 w-3.5" />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>

        {/* Threat Model Trigger & Security Status */}
        <div className="flex items-center gap-2">
          <button
            id="btn-threat-model"
            onClick={onOpenThreats}
            className="flex items-center gap-1.5 rounded-lg border border-amber-500/30 bg-amber-500/10 px-3 py-1.5 text-xs font-medium text-amber-300 hover:bg-amber-500/20 transition"
            title="View Threat Summary Table (5 Threat Zones)"
          >
            <ShieldAlert className="h-3.5 w-3.5 text-amber-400" />
            <span className="hidden sm:inline">Threat Model</span>
          </button>
        </div>
      </div>

      {/* Mobile Nav */}
      <div className="flex lg:hidden overflow-x-auto border-t border-slate-800 px-3 py-1.5 gap-1">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`flex items-center gap-1.5 whitespace-nowrap rounded-md px-2.5 py-1 text-xs font-medium ${
                isActive ? "bg-teal-600 text-white" : "text-slate-400 hover:bg-slate-800"
              }`}
            >
              <Icon className="h-3 w-3" />
              <span>{item.label}</span>
            </button>
          );
        })}
      </div>
    </header>
  );
};
