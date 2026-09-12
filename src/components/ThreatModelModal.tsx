import React from "react";
import { ShieldCheck, X, AlertTriangle, Lock, Key, Server, Database } from "lucide-react";

interface ThreatModelModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const ThreatModelModal: React.FC<ThreatModelModalProps> = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  const threatZones = [
    {
      zone: "1. Input Surfaces",
      icon: AlertTriangle,
      color: "text-amber-400 border-amber-500/30 bg-amber-500/10",
      threats: [
        {
          scenario: "Untrusted Model XML File Upload",
          risk: "XML External Entity (XXE) injection or Billion Laughs denial-of-service via external DTD resolution.",
          countermeasure: "Enforce defusedxml.ElementTree instead of standard xml.etree. Reject DTD expansion, entity resolving, and limit payload size to 15MB.",
        },
        {
          scenario: "Malicious ELN_value / File Basename",
          risk: "Path traversal via strings containing '../../' or absolute paths trying to write/delete outside staging directory.",
          countermeasure: "Normalize with Path(eln_val).name and resolve relative to verified temporary directory using Path.resolve() confinement check.",
        },
      ],
    },
    {
      zone: "2. Planning & Reasoning / Logic",
      icon: Key,
      color: "text-purple-400 border-purple-500/30 bg-purple-500/10",
      threats: [
        {
          scenario: "PilotScript Syntax Injection",
          risk: "Unsafe eval() or arbitrary code execution while translating PLP syntax strings into executable logic.",
          countermeasure: "Dedicated Lexer and AST evaluator with strict token whitelist (Substring, FindSubstring, equality, boolean operators). Never pass raw user script to Python eval() or exec().",
        },
        {
          scenario: "Section Type Spoofing",
          risk: "A malicious executable file renamed to '.pdf' or '.xlsx' uploaded to Biovia Notebook.",
          countermeasure: "MIME type and file signature magic bytes inspection before invoking Biovia Notebook Add Section endpoints.",
        },
      ],
    },
    {
      zone: "3. Tool Execution",
      icon: Server,
      color: "text-blue-400 border-blue-500/30 bg-blue-500/10",
      threats: [
        {
          scenario: "Server Action 'Delete File' Escalation",
          risk: "Pipeline deleting system root files or operational server assets instead of staging folder.",
          countermeasure: "Strict boundary assertion ensuring delete targets must be subdirectories of tempfile.TemporaryDirectory() or configured DOWNLOAD_STAGING_DIR.",
        },
        {
          scenario: "SSRF via Malformed Storage URL",
          risk: "Custom endpoints pointing Azure SDK client or Notebook client to internal cloud metadata IP (169.254.169.254).",
          countermeasure: "Strict URL whitelist enforcing domain schemes: https://*.file.core.windows.net and corporate Biovia ELN domains only.",
        },
      ],
    },
    {
      zone: "4. Memory & State",
      icon: Database,
      color: "text-emerald-400 border-emerald-500/30 bg-emerald-500/10",
      threats: [
        {
          scenario: "Cross-Tenant File Staging Contamination",
          risk: "Multiple pipeline runs sharing static 'E:\\Model Data Transfer\\DownloadedFile' directory causing data leaks across different experiments.",
          countermeasure: "Isolate each pipeline execution inside unique ephemeral tempfile.TemporaryDirectory() per run with guaranteed ExitStack teardown.",
        },
        {
          scenario: "Session Token Memory Leakage",
          risk: "Biovia Notebook session tokens and Azure keys printed to stdout, system logs, or error stack traces.",
          countermeasure: "Custom log sanitization filter automatically redacting Authorization headers, X-Biovia-Session-Token, and account_key parameters.",
        },
      ],
    },
    {
      zone: "5. Inter-System Communication",
      icon: Lock,
      color: "text-rose-400 border-rose-500/30 bg-rose-500/10",
      threats: [
        {
          scenario: "CRITICAL VULNERABILITY in Original PLP XML",
          risk: "Cleartext hardcoded Azure account key found in PLP Python component (account_key = 's5E2TNey9...').",
          countermeasure: "Completely purge hardcoded key from codebase. Mandate injection via environment variable (AZURE_STORAGE_KEY) or Google Cloud Secret Manager at runtime.",
        },
        {
          scenario: "Unencrypted Biovia Notebook API Calls",
          risk: "Man-in-the-Middle (MITM) interception of scientific data during transfer from Azure to ELN.",
          countermeasure: "Enforce HTTPS with verify=True in Python requests session. Refuse unencrypted HTTP transport.",
        },
      ],
    },
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 p-4 backdrop-blur-sm">
      <div className="relative max-h-[90vh] w-full max-w-4xl overflow-hidden rounded-2xl border border-slate-700 bg-slate-900 shadow-2xl flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-800 px-6 py-4 bg-slate-900/60">
          <div className="flex items-center gap-2.5">
            <div className="rounded-lg bg-amber-500/20 p-2 text-amber-400 ring-1 ring-amber-500/30">
              <ShieldCheck className="h-5 w-5" />
            </div>
            <div>
              <h2 className="text-base font-semibold text-slate-100">
                Agentic Threat Model: Biovia PLP to Python Pipeline
              </h2>
              <p className="text-xs text-slate-400">
                Structured 5-Zone Analysis mapping security risks to verified architectural countermeasures
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-800 hover:text-slate-200 transition"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Content Table */}
        <div className="overflow-y-auto p-6 space-y-6">
          <div className="rounded-xl border border-rose-500/40 bg-rose-950/20 p-4 text-xs text-rose-300">
            <strong className="font-semibold text-rose-200">Critical Remediation Note:</strong> The legacy PLP XML contained a hardcoded Azure Storage account key in plaintext inside component 46. The refactored Python architecture eliminates all hardcoded secrets in accordance with Zero-Hardcoding Hygiene (Production Directive 4).
          </div>

          <div className="space-y-4">
            {threatZones.map((zone, idx) => {
              const Icon = zone.icon;
              return (
                <div key={idx} className="rounded-xl border border-slate-800 bg-slate-950/50 p-4">
                  <div className="flex items-center gap-2 mb-3">
                    <span className={`inline-flex items-center gap-1.5 rounded-md px-2.5 py-1 text-xs font-semibold border ${zone.color}`}>
                      <Icon className="h-3.5 w-3.5" />
                      {zone.zone}
                    </span>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {zone.threats.map((threat, tIdx) => (
                      <div key={tIdx} className="rounded-lg border border-slate-800/80 bg-slate-900/60 p-3 text-xs space-y-1.5">
                        <div className="font-medium text-slate-200 flex items-center gap-1.5">
                          <span className="h-1.5 w-1.5 rounded-full bg-amber-400"></span>
                          {threat.scenario}
                        </div>
                        <p className="text-slate-400">
                          <strong className="text-slate-300">Risk:</strong> {threat.risk}
                        </p>
                        <p className="text-teal-300/90 font-mono bg-slate-950/70 p-2 rounded border border-slate-800">
                          <strong className="text-teal-400">Countermeasure:</strong> {threat.countermeasure}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Footer */}
        <div className="border-t border-slate-800 px-6 py-3 bg-slate-950/60 flex justify-end">
          <button
            onClick={onClose}
            className="rounded-lg bg-teal-600 px-4 py-1.5 text-xs font-semibold text-white hover:bg-teal-500 transition"
          >
            Close Threat Model
          </button>
        </div>
      </div>
    </div>
  );
};
