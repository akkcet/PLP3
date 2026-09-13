import express from "express";
import path from "path";
import dotenv from "dotenv";
import { execFile } from "child_process";
import { GoogleGenAI } from "@google/genai";
import { createServer as createViteServer } from "vite";

dotenv.config();

const app = express();
const PORT = 3000;

// Top-Level Request Deserialization (Ordering Guarantee)
app.use(express.json({ limit: "15mb" }));
app.use(express.urlencoded({ extended: true, limit: "15mb" }));

// Lazy initialization for Gemini client
let aiClient: GoogleGenAI | null = null;
function getAIClient(): GoogleGenAI | null {
  if (!aiClient) {
    const key = process.env.GEMINI_API_KEY;
    if (key && key !== "MY_GEMINI_API_KEY") {
      aiClient = new GoogleGenAI({ apiKey: key });
    }
  }
  return aiClient;
}

// Resilient Model Fallback Ladder
const MODEL_FALLBACK_LADDER = [
  "gemini-3.6-flash",
  "gemini-3.1-flash-lite",
  "gemini-flash-latest",
  "gemini-3.7-flash",
];

async function generateContentWithFallback(prompt: string, systemInstruction?: string): Promise<{ text: string; modelUsed: string }> {
  const client = getAIClient();
  if (!client) {
    throw new Error("GEMINI_API_KEY is not configured in the environment.");
  }

  let lastError: unknown = null;
  for (const model of MODEL_FALLBACK_LADDER) {
    try {
      const response = await client.models.generateContent({
        model,
        contents: prompt,
        config: systemInstruction ? { systemInstruction } : undefined,
      });

      if (response && response.text) {
        return { text: response.text, modelUsed: model };
      }
    } catch (err: unknown) {
      lastError = err;
      console.warn(`[Gemini Fallback] Model ${model} failed, attempting next in ladder... Error:`, (err as Error)?.message || err);
    }
  }

  throw new Error(`All models in fallback ladder failed. Last error: ${(lastError as Error)?.message || String(lastError)}`);
}

// ---------------- API Routes ----------------

// Health check
app.get("/api/health", (_req, res) => {
  res.json({
    status: "ok",
    hasGeminiKey: Boolean(process.env.GEMINI_API_KEY && process.env.GEMINI_API_KEY !== "MY_GEMINI_API_KEY"),
    timestamp: new Date().toISOString(),
  });
});

// AI Refactor / Explain Component Endpoint
app.post("/api/ai/refactor-component", async (req, res) => {
  try {
    const data = req.body && typeof req.body === "object" ? req.body : {};
    const { componentName, componentXml, pilotScript, pythonCode, userQuestion } = data;

    if (!componentName && !pilotScript && !pythonCode && !componentXml) {
      return res.status(400).json({ error: "No component information provided." });
    }

    const client = getAIClient();
    if (!client) {
      return res.status(503).json({
        error: "Gemini API key is not configured.",
        suggestion: "Configure GEMINI_API_KEY in the environment secrets to enable AI code generation.",
      });
    }

    const systemInstruction = `You are a Principal Software Engineer & Bioinformatics/Cheminformatics Automation Architect specializing in Biovia Pipeline Pilot (PLP), PilotScript, Enterprise ELN (Biovia Notebook), and clean Python 3.11+ refactoring.
Refactor Biovia PLP components into idiomatic, typed, testable Python code adhering to PEP 8, clean architecture, and defensive programming.`;

    const prompt = `Analyze and refactor the following Biovia Pipeline Pilot component:

Component: ${componentName || "Custom Component"}
${componentXml ? `XML Definition:\n\`\`\`xml\n${componentXml}\n\`\`\`` : ""}
${pilotScript ? `PilotScript Expression:\n\`\`\`pilotscript\n${pilotScript}\n\`\`\`` : ""}
${pythonCode ? `Embedded Python Code in PLP:\n\`\`\`python\n${pythonCode}\n\`\`\`` : ""}
${userQuestion ? `Specific Question: ${userQuestion}` : ""}

Please provide:
1. Executive Logic Summary: What this component does in the PLP data stream.
2. Clean Modular Python Function: Modern type annotations, docstring, robust error handling, and separation of concerns.
3. Unit Test example (pytest).
4. Security and Configuration considerations (e.g., credentials, file path safety).`;

    const result = await generateContentWithFallback(prompt, systemInstruction);
    res.json({ success: true, analysis: result.text, modelUsed: result.modelUsed });
  } catch (error: unknown) {
    console.error("AI Refactor error:", error);
    res.status(500).json({ error: (error as Error).message || "Failed to generate AI refactoring." });
  }
});

// AI PilotScript Transpiler Endpoint
app.post("/api/ai/transpile-expression", async (req, res) => {
  try {
    const data = req.body && typeof req.body === "object" ? req.body : {};
    const { expression, contextVariables } = data;

    if (!expression || typeof expression !== "string") {
      return res.status(400).json({ error: "Valid PilotScript expression string is required." });
    }

    const client = getAIClient();
    if (!client) {
      return res.status(503).json({
        error: "Gemini API key not configured.",
        suggestion: "Use client-side PilotScript AST transpiler.",
      });
    }

    const prompt = `Transpile this Biovia PilotScript expression into pure, idiomatic Python:

PilotScript:
\`\`\`pilotscript
${expression}
\`\`\`

Available Context Variables:
${JSON.stringify(contextVariables || {}, null, 2)}

Provide:
1. Pure Python code snippet or lambda function
2. Explanation of operators (e.g. '@' globals, 'ne', 'eq', 'is defined', 'findsubstring', 'HashFind', ':=')
3. Equivalent Python expression using a dict context \`record: dict\` and \`globals: dict\`.`;

    const result = await generateContentWithFallback(prompt);
    res.json({ success: true, pythonCode: result.text, modelUsed: result.modelUsed });
  } catch (error: unknown) {
    res.status(500).json({ error: (error as Error).message || "Expression transpilation failed." });
  }
});

// ---------------- Real Python 3 Execution Endpoints ----------------

// Helper to run python3 commands asynchronously
function runPython(args: string[]): Promise<{ stdout: string; stderr: string; exitCode: number }> {
  return new Promise((resolve) => {
    execFile("python3", args, { cwd: process.cwd(), timeout: 15000 }, (error, stdout, stderr) => {
      resolve({
        stdout: stdout || "",
        stderr: stderr || "",
        exitCode: error && typeof error.code === "number" ? error.code : 0,
      });
    });
  });
}

// 1. Python runtime status
app.get("/api/python/status", async (_req, res) => {
  const ver = await runPython(["--version"]);
  res.json({
    available: ver.exitCode === 0,
    version: ver.stdout.trim() || ver.stderr.trim(),
    cliAvailable: true,
  });
});

// 2. Run Python unittest suite
app.post("/api/python/run-tests", async (_req, res) => {
  const result = await runPython(["-m", "unittest", "discover", "tests", "-v"]);
  res.json({
    success: result.exitCode === 0,
    stdout: result.stdout,
    stderr: result.stderr,
    combinedOutput: (result.stdout + "\n" + result.stderr).trim(),
  });
});

// 3. Run Python PLP Protocol Parser CLI
app.post("/api/python/parse-plp", async (req, res) => {
  const xmlPath = req.body?.xmlPath || "sample_plp_protocol.xml";
  const result = await runPython(["-m", "biovia_pipeline.cli", "parse-plp", xmlPath]);
  res.json({
    success: result.exitCode === 0,
    output: result.stdout || result.stderr,
  });
});

// 3b. Run Python Custom Filter component CLI (single function taking PLP script expression)
app.post("/api/python/custom-filter", async (req, res) => {
  const expr = req.body?.expression || "findsubstring(DocRelativepath, '.pdf')>1";
  const record = JSON.stringify(req.body?.record || {});
  const globalsDict = JSON.stringify(req.body?.globals || {});
  const result = await runPython([
    "-m", "biovia_pipeline.cli", "custom-filter", expr,
    "--record", record,
    "--globals", globalsDict
  ]);
  res.json({
    success: result.exitCode === 0,
    output: result.stdout || result.stderr,
  });
});

// 3c. Run Python Custom Manipulator component CLI
app.post("/api/python/custom-manipulator", async (req, res) => {
  const expr = req.body?.expression || "A := 10; B := A * 2; CleanTitle := 'Clean_' . SectionTitle;";
  const record = JSON.stringify(req.body?.record || { SectionTitle: "Spectroscopy Analysis" });
  const globalsDict = JSON.stringify(req.body?.globals || {});
  const localsDict = JSON.stringify(req.body?.locals || {});
  const initExpr = req.body?.init || "";
  const finalExpr = req.body?.final || "";

  const args = [
    "-m", "biovia_pipeline.cli", "custom-manipulator", expr,
    "--record", record,
    "--globals", globalsDict,
    "--locals", localsDict,
  ];
  if (initExpr) args.push("--init", initExpr);
  if (finalExpr) args.push("--final", finalExpr);

  const result = await runPython(args);
  res.json({
    success: result.exitCode === 0,
    output: result.stdout || result.stderr,
  });
});

// 3d. Run Python Notebook Connection component CLI
app.post("/api/python/notebook-connection", async (req, res) => {
  const name = req.body?.name || "NotebookConnection";
  const url = req.body?.url || "https://notebook.corp.internal/eln";
  const auth = req.body?.auth || "Use Notebook Session Token";
  const user = req.body?.user || "arun.khuntia";
  const token = req.body?.token || "tok_eln_mock_session_abc";

  const result = await runPython([
    "-m", "biovia_pipeline.cli", "notebook-connection",
    "--name", name,
    "--url", url,
    "--auth", auth,
    "--user", user,
    "--token", token,
  ]);
  res.json({
    success: result.exitCode === 0,
    output: result.stdout || result.stderr,
  });
});

// 3e. Run Python Experiment Query component CLI
app.post("/api/python/experiment-query", async (req, res) => {
  const connection = req.body?.connection || "NotebookConnection";
  const filterBy = req.body?.filterBy || "Experiment Number";
  const filterType = req.body?.filterType || "Equals";
  const filterVal = req.body?.filterVal || "EXP-2026-XRF-01";
  const max = String(req.body?.max || 10);

  const result = await runPython([
    "-m", "biovia_pipeline.cli", "experiment-query",
    "--connection", connection,
    "--filter-by", filterBy,
    "--filter-type", filterType,
    "--filter-val", filterVal,
    "--max", max,
  ]);
  res.json({
    success: result.exitCode === 0,
    output: result.stdout || result.stderr,
  });
});

// 3f. Run isolated component tests
app.post("/api/python/run-component-test", async (req, res) => {
  const testTarget = req.body?.target || "tests.test_components";
  const result = await runPython(["-m", "unittest", testTarget, "-v"]);
  res.json({
    success: result.exitCode === 0,
    stdout: result.stdout,
    stderr: result.stderr,
    combinedOutput: (result.stdout + "\n" + result.stderr).trim(),
  });
});

// 4. Run Python Model Data XML Parser CLI
app.post("/api/python/parse-model", async (req, res) => {
  const xmlPath = req.body?.xmlPath || "sample_model_data.xml";
  const result = await runPython(["-m", "biovia_pipeline.cli", "parse-model", xmlPath]);
  res.json({
    success: result.exitCode === 0,
    output: result.stdout || result.stderr,
  });
});

// 5. Run Python PilotScript Transpiler CLI
app.post("/api/python/transpile", async (req, res) => {
  const expr = req.body?.expression || "findsubstring(DocRelativepath, '.pdf')>1";
  const result = await runPython(["-m", "biovia_pipeline.cli", "transpile", expr]);
  res.json({
    success: result.exitCode === 0,
    output: result.stdout || result.stderr,
  });
});

// 6. Run Python Full Pipeline CLI
app.post("/api/python/run-pipeline", async (req, res) => {
  const xmlPath = req.body?.xmlPath || "sample_model_data.xml";
  const exp = req.body?.experimentNumber || "EXP-2026-XRF-01";
  const result = await runPython(["-m", "biovia_pipeline.cli", "run-pipeline", "--xml", xmlPath, "--exp", exp, "--mock"]);
  res.json({
    success: result.exitCode === 0,
    output: result.stdout || result.stderr,
  });
});

// 7. Execute custom Python code snippet
app.post("/api/python/exec", async (req, res) => {
  const code = req.body?.code;
  if (!code || typeof code !== "string") {
    return res.status(400).json({ error: "Python code string is required." });
  }
  const result = await runPython(["-c", code]);
  res.json({
    success: result.exitCode === 0,
    stdout: result.stdout,
    stderr: result.stderr,
  });
});

// ---------------- Vite Middleware & Static Serving ----------------
async function startServer() {
  if (process.env.NODE_ENV !== "production") {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: "spa",
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), "dist");
    app.use(express.static(distPath));
    app.get("*", (_req, res) => {
      res.sendFile(path.join(distPath, "index.html"));
    });
  }

  app.listen(PORT, "0.0.0.0", () => {
    console.log(`Server running on http://0.0.0.0:${PORT}`);
  });
}

startServer();
