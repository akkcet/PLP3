import React, { useState } from "react";
import { Sparkles, Send, Bot, User, Code2, ShieldAlert, CheckCircle2 } from "lucide-react";

interface AiMessage {
  role: "user" | "assistant";
  content: string;
  modelUsed?: string;
}

export const AiAssistant: React.FC = () => {
  const [messages, setMessages] = useState<AiMessage[]>([
    {
      role: "assistant",
      content: `Hello! I am your Biovia Pipeline Pilot & Enterprise Python Refactoring Architect.

I have analyzed the **Data model UI** protocol XML export you provided, including:
1. **PilotScript Filters & Custom Manipulators**: Transpiled 1-indexed string operations (\`FindSubstring\`, \`Substring\`) and hashtable lookups (\`HashFind\`).
2. **Embedded Python on Server Components**: Refactored the Azure File Share downloader and XML parser into pure, modular Python.
3. **Biovia Notebook API Integration**: Mapped the \`Notebook Connection\`, \`Experiment Query\`, \`Add PDF/Excel/PPT/Word Section\`, and \`Update Notebook\` components into an enterprise REST client.
4. **Security Hardening**: Fixed the critical vulnerability where Azure Storage credentials were hardcoded in plaintext.

How can I help you customize or test this Python refactoring?`,
    },
  ]);
  const [input, setInput] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const quickQuestions = [
    "How does the refactored code handle Azure credentials securely?",
    "Explain how PilotScript 1-based indexing maps to Python 0-based indexing.",
    "How does the SectionDispatcher handle unsupported file extensions?",
    "Write a pytest test case for the Biovia Notebook client.",
  ];

  const handleSend = async (questionText?: string) => {
    const textToSend = questionText || input;
    if (!textToSend.trim() || isLoading) return;

    const userMsg: AiMessage = { role: "user", content: textToSend };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setIsLoading(true);

    try {
      const resp = await fetch("/api/ai/refactor-component", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          componentName: "Biovia PLP Automation Pipeline",
          userQuestion: textToSend,
        }),
      });

      const data = await resp.json();
      if (data.analysis) {
        setMessages((prev) => [
          ...prev,
          { role: "assistant", content: data.analysis, modelUsed: data.modelUsed },
        ]);
      } else {
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: `Notice: ${data.error || "Unable to retrieve response from AI backend."}${
              data.suggestion ? ` (${data.suggestion})` : ""
            }`,
          },
        ]);
      }
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: `Connection error: ${err.message}` },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-65px)] overflow-hidden bg-slate-950">
      {/* Header */}
      <div className="border-b border-slate-800 bg-slate-900/60 px-6 py-3 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="rounded-lg bg-teal-500/10 p-2 text-teal-400 ring-1 ring-teal-500/30">
            <Sparkles className="h-4 w-4" />
          </div>
          <div>
            <h2 className="text-sm font-semibold text-slate-100">
              AI Refactoring & Architecture Assistant
            </h2>
            <p className="text-xs text-slate-400">
              Powered by Google Gemini with Resilient Fallback Protocol (3.6-flash &rarr; 3.1-flash-lite)
            </p>
          </div>
        </div>
      </div>

      {/* Message Stream */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`flex gap-3 max-w-4xl ${
              msg.role === "user" ? "ml-auto justify-end" : "mr-auto"
            }`}
          >
            {msg.role === "assistant" && (
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-teal-950 text-teal-300 border border-teal-800 flex-shrink-0 mt-1">
                <Bot className="h-4 w-4" />
              </div>
            )}
            <div
              className={`rounded-2xl p-4 text-xs leading-relaxed ${
                msg.role === "user"
                  ? "bg-teal-600 text-white shadow-sm"
                  : "bg-slate-900 text-slate-200 border border-slate-800 shadow-md"
              }`}
            >
              <div className="whitespace-pre-wrap">{msg.content}</div>
              {msg.modelUsed && (
                <div className="mt-2 text-[10px] text-teal-400/80 font-mono border-t border-slate-800 pt-1.5 flex items-center gap-1">
                  <CheckCircle2 className="h-3 w-3" />
                  <span>Generated via {msg.modelUsed}</span>
                </div>
              )}
            </div>
            {msg.role === "user" && (
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-slate-800 text-slate-300 border border-slate-700 flex-shrink-0 mt-1">
                <User className="h-4 w-4" />
              </div>
            )}
          </div>
        ))}
        {isLoading && (
          <div className="flex gap-3 items-center text-xs text-slate-400 animate-pulse">
            <Bot className="h-4 w-4 text-teal-400" />
            <span>Refactoring architecture and generating response...</span>
          </div>
        )}
      </div>

      {/* Quick Prompts */}
      <div className="border-t border-slate-800 bg-slate-900/40 px-6 py-2 overflow-x-auto flex items-center gap-2">
        <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider flex-shrink-0">
          Suggestions:
        </span>
        {quickQuestions.map((q, idx) => (
          <button
            key={idx}
            onClick={() => handleSend(q)}
            className="rounded-lg border border-slate-800 bg-slate-900/80 px-2.5 py-1 text-xs text-slate-400 hover:text-teal-300 hover:border-teal-800 whitespace-nowrap transition"
          >
            {q}
          </button>
        ))}
      </div>

      {/* Input Box */}
      <div className="border-t border-slate-800 bg-slate-900/80 p-4">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="flex items-center gap-2 max-w-4xl mx-auto"
        >
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about Biovia PLP mapping, PilotScript transpilation, or enterprise security..."
            className="flex-1 rounded-xl border border-slate-700 bg-slate-950 px-4 py-2 text-xs text-slate-100 placeholder-slate-500 focus:border-teal-500 focus:outline-none focus:ring-1 focus:ring-teal-500"
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="flex items-center gap-1.5 rounded-xl bg-teal-600 px-4 py-2 text-xs font-semibold text-white hover:bg-teal-500 transition disabled:opacity-50"
          >
            <Send className="h-3.5 w-3.5" />
            <span>Send</span>
          </button>
        </form>
      </div>
    </div>
  );
};
