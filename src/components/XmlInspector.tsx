import React, { useState } from "react";
import { FileCode, Search, Code, CheckCircle, Copy, Check, Upload } from "lucide-react";

export const XmlInspector: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState<string>("");
  const [copied, setCopied] = useState<boolean>(false);

  // Summary statistics from the XML
  const xmlStats = [
    { label: "Protocol Object", value: "SciTegic.Protocol.1" },
    { label: "Format Version", value: "8.0.0" },
    { label: "Total Components", value: "14 nodes" },
    { label: "Subprotocols", value: "3 nested pipelines" },
    { label: "Embedded Python", value: "2 script blocks" },
    { label: "PilotScript Filters", value: "6 expressions" },
  ];

  const highlightedSnippets = [
    {
      title: "Embedded Python Component (Azure Downloader - LocalID 46)",
      snippet: `<sci:component name="Python (on Server)" version="2">
    <sci:arg name="Script" type="PythonScriptType">
        from azure.storage.fileshare import ShareServiceClient
        service_client = ShareServiceClient(account_url=f"https://{account_name}.file.core.windows.net/", credential=account_key)
        share_client = service_client.get_share_client(share_name)
        # downloads selected_files from directory_path to download_folder
    </sci:arg>
</sci:component>`,
    },
    {
      title: "PilotScript Gatekeeper Filter (LocalID 59)",
      snippet: `<sci:component name="Custom Filter (PilotScript)" version="2">
    <sci:arg name="Expression" type="ExpressionType">
        <sci:value>@experiment_number is defined and @experiment_number is ne '' and @filelocation is eq ''</sci:value>
    </sci:arg>
</sci:component>`,
    },
    {
      title: "Subprotocol Section Dispatcher (LocalID 53)",
      snippet: `<sci:component name="Subprotocol" version="2">
    <sci:arg name="RunToCompletion" type="StringType">
        <sci:legalval selected="true">True - For Each Data Record</sci:legalval>
    </sci:arg>
    <!-- Checks findsubstring(DocRelativepath, '.pdf') > 1 -> Add PDF Section -->
    <!-- Checks findsubstring(DocRelativepath, '.xlsx') > 1 -> Add Excel Section -->
    <!-- Checks findsubstring(DocRelativepath, '.ppt') > 1 -> Add PowerPoint Section -->
    <!-- Checks findsubstring(DocRelativepath, '.docx') > 1 -> Add Word Section -->
</sci:component>`,
    },
    {
      title: "Biovia Notebook Connection & Section Add (LocalID 24, 1, 9, 15, 20)",
      snippet: `<sci:component name="Notebook Connection" version="2">
    <sci:arg name="Connection Name" type="StringType">
        <sci:value>NotebookConnection</sci:value>
    </sci:arg>
    <sci:arg name="Authentication Method" type="StringType">
        <sci:legalval selected="true">Use Notebook Session Token</sci:legalval>
    </sci:arg>
</sci:component>`,
    },
  ];

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const filteredSnippets = highlightedSnippets.filter(
    (s) =>
      s.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      s.snippet.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="flex flex-col h-[calc(100vh-65px)] overflow-hidden">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between border-b border-slate-800 bg-slate-900/60 px-6 py-3">
        <div className="flex items-center gap-2.5">
          <div className="rounded-lg bg-teal-500/10 p-2 text-teal-400 ring-1 ring-teal-500/30">
            <FileCode className="h-4 w-4" />
          </div>
          <div>
            <h2 className="text-sm font-semibold text-slate-100">
              Pipeline Pilot (PLP) XML Protocol Architecture
            </h2>
            <p className="text-xs text-slate-400">
              Structural analysis of the SciTegic XML schema, component definitions, and connection graph
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <div className="relative">
            <Search className="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-slate-500" />
            <input
              type="text"
              placeholder="Search components or XML..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="rounded-lg border border-slate-700 bg-slate-950 pl-8 pr-3 py-1 text-xs text-slate-200 placeholder-slate-500 focus:border-teal-500 focus:outline-none w-56"
            />
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-slate-950">
        {/* Statistics Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          {xmlStats.map((stat, i) => (
            <div key={i} className="rounded-xl border border-slate-800 bg-slate-900/50 p-3 text-center">
              <div className="text-[11px] text-slate-400 font-medium">{stat.label}</div>
              <div className="text-sm font-bold text-teal-300 font-mono mt-1">{stat.value}</div>
            </div>
          ))}
        </div>

        {/* High-level component decomposition */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/40 p-5 space-y-4">
          <h3 className="text-sm font-semibold text-slate-200">
            Automated PLP Component to Python Mapping Hierarchy
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
            <div className="rounded-lg border border-slate-800 bg-slate-950 p-3.5 space-y-2">
              <div className="font-bold text-amber-300 flex items-center gap-1.5">
                <span className="h-2 w-2 rounded-full bg-amber-400"></span>
                <span>Branch 1: User Form UI</span>
              </div>
              <p className="text-slate-400 text-[11px] leading-relaxed">
                In PLP, this renders HTML Web Port form elements (File Chooser, Submit Button). In modern Python, this is refactored into a clean REST API / CLI arguments receiver with schema validation.
              </p>
            </div>

            <div className="rounded-lg border border-slate-800 bg-slate-950 p-3.5 space-y-2">
              <div className="font-bold text-blue-300 flex items-center gap-1.5">
                <span className="h-2 w-2 rounded-full bg-blue-400"></span>
                <span>Branch 2: XML Metadata Parser</span>
              </div>
              <p className="text-slate-400 text-[11px] leading-relaxed">
                Replaces Node 22 with defusedxml-based <span className="font-mono text-teal-300">parse_model_xml()</span>. Extracts generic instrument outputs, file names, section titles, and user paths.
              </p>
            </div>

            <div className="rounded-lg border border-slate-800 bg-slate-950 p-3.5 space-y-2">
              <div className="font-bold text-teal-300 flex items-center gap-1.5">
                <span className="h-2 w-2 rounded-full bg-teal-400"></span>
                <span>Branch 3: Azure & ELN Dispatcher</span>
              </div>
              <p className="text-slate-400 text-[11px] leading-relaxed">
                Eliminates hardcoded credentials. Connects to Azure ShareServiceClient, streams files to staging, and dispatches to Biovia Notebook v2 REST API (PDF, Excel, PPT, Word, Attachment).
              </p>
            </div>
          </div>
        </div>

        {/* XML Key Snippets */}
        <div className="space-y-4">
          <h3 className="text-sm font-semibold text-slate-200">
            Key Protocol Components from Uploaded XML
          </h3>
          <div className="space-y-4">
            {filteredSnippets.map((item, idx) => (
              <div key={idx} className="rounded-xl border border-slate-800 bg-slate-900/60 overflow-hidden">
                <div className="flex items-center justify-between border-b border-slate-800 bg-slate-950/70 px-4 py-2 text-xs">
                  <span className="font-semibold text-slate-300">{item.title}</span>
                  <button
                    onClick={() => handleCopy(item.snippet)}
                    className="flex items-center gap-1 rounded bg-slate-800 px-2 py-0.5 text-xs text-slate-300 hover:bg-slate-700 transition"
                  >
                    {copied ? <Check className="h-3 w-3 text-emerald-400" /> : <Copy className="h-3 w-3" />}
                    <span>{copied ? "Copied" : "Copy"}</span>
                  </button>
                </div>
                <pre className="p-4 font-mono text-xs text-slate-300 overflow-x-auto bg-slate-950/40">
                  <code>{item.snippet}</code>
                </pre>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
