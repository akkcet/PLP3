import express from "express";
import path from "path";
import dotenv from "dotenv";
import { execFile } from "child_process";
import { GoogleGenAI } from "@google/genai";
import { createServer as createViteServer } from "vite";
import { spawn } from "child_process";

dotenv.config();

const app = express();
const PORT = 3000;

// Top-Level Request Deserialization (Ordering Guarantee)
app.use(express.json({ limit: "15mb" }));
app.use(express.urlencoded({ extended: true, limit: "15mb" }));

// Lazy initialization for Gemini client using Google Cloud ADC.
let aiClient: GoogleGenAI | null = null;
function getAIClient(): GoogleGenAI | null {
  if (!aiClient) {
    const project = process.env.GOOGLE_CLOUD_PROJECT;
    const location = process.env.GOOGLE_CLOUD_LOCATION || "us-central1";
    if (project) {
      aiClient = new GoogleGenAI({
        vertexai: true,
        project,
        location,
      });
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
    throw new Error("GOOGLE_CLOUD_PROJECT is not configured in the environment.");
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
    hasGeminiKey: Boolean(process.env.GOOGLE_CLOUD_PROJECT),
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
        error: "Google Cloud ADC is not configured.",
        suggestion: "Set GOOGLE_CLOUD_PROJECT and authenticate with Application Default Credentials.",
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
        error: "Google Cloud ADC is not configured.",
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
// function runPython(args: string[]): Promise<{ stdout: string; stderr: string; exitCode: number }> {
//   return new Promise((resolve) => {
//     execFile("python", args, { cwd: process.cwd(), timeout: 15000 }, (error, stdout, stderr) => {
//       resolve({
//         stdout: stdout || "",
//         stderr: stderr || "",
//         exitCode: error && typeof error.code === "number" ? error.code : 0,
//       });
//     });
//   });
// }
function runPython(
  args: string[],
  stdinData?: string
): Promise<{
  stdout: string;
  stderr: string;
  exitCode: number;
}> {
  return new Promise((resolve) => {
    const proc = spawn("python", args, {
      cwd: process.cwd()
    });

    let stdout = "";
    let stderr = "";

    proc.stdout.on("data", (data) => {
      stdout += data.toString();
    });

    proc.stderr.on("data", (data) => {
      stderr += data.toString();
    });

    proc.on("close", (code) => {
      resolve({
        stdout,
        stderr,
        exitCode: code ?? 0,
      });
    });

    if (stdinData) {
      proc.stdin.write(stdinData);
      proc.stdin.end();
    }
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
  const password = req.body?.password || "";

  // const result = await runPython([
  //   "-m", "biovia_pipeline.cli", "notebook-connection",
  //   "--name", name,
  //   "--url", url,
  //   "--auth", auth,
  //   "--user", user,
  //   "--token", token,
  // ]);
  const args = [
  "-m",
  "biovia_pipeline.cli",
  "notebook-connection",
  "--name",
  name,
  "--url",
  url,
  "--auth",
  auth,
];

if (user) {
  args.push("--user", user);
}

if (password) {
  args.push("--password", password);
}

if (token) {
  args.push("--token", token);
}

const result = await runPython(args);
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
  const notebookUrl = req.body?.notebookUrl;
  const username = req.body?.username;
  const password = req.body?.password;

  const args = [
  "-m",
  "biovia_pipeline.cli",
  "experiment-query",
  "--connection",
  connection,
  "--filter-by",
  filterBy,
  "--filter-type",
  filterType,
  "--filter-val",
  filterVal,
  "--max",
  max,
];

if (notebookUrl) {
  args.push("--url", notebookUrl);
}

if (username) {
  args.push("--user", username);
}

if (password) {
  args.push("--password", password);
}

const result = await runPython(args);
console.log("EXPERIMENT QUERY REQuEST");
console.log({
  notebookUrl,
  username,
  password: password ? "******" : "",
  filterBy,
  filterType,
  filterVal
});

console.log("ARGS=", args);
  res.json({
    success: result.exitCode === 0,
    output: result.stdout || result.stderr,
  });
});

// 3g. Run Python Add Excel Section component CLI
app.post("/api/python/add-excel-section", async (req, res) => {
  const title = req.body?.title || "ICP-MS Calibration Curve";
  const file = req.body?.file || "calibration_data.xlsx";
  const previewMode = req.body?.previewMode || "Generate from Excel File Content";
  const cols = String(req.body?.cols || 2);
  const rows = String(req.body?.rows || 3);
  const record = JSON.stringify(req.body?.record || {});

  const result = await runPython([
    "-m", "biovia_pipeline.cli", "add-excel-section",
    "--title", title,
    "--file", file,
    "--preview-mode", previewMode,
    "--cols", cols,
    "--rows", rows,
    "--record", record,
  ]);
  res.json({
    success: result.exitCode === 0,
    output: result.stdout || result.stderr,
  });
});

// 3h. Run Python Add File Attachment Section component CLI
app.post("/api/python/add-attachment-section", async (req, res) => {
  const title = req.body?.title || "Raw Assay Archives";
  const files = req.body?.files || ["instrument_raw_log.bin"];
  const action = req.body?.action || "Replace";
  const record = JSON.stringify(req.body?.record || {});

  const args = [
    "-m", "biovia_pipeline.cli", "add-attachment-section",
    "--title", title,
    "--action", action,
    "--record", record,
    "--files", ...(Array.isArray(files) ? files : [files]),
  ];

  const result = await runPython(args);
  res.json({
    success: result.exitCode === 0,
    output: result.stdout || result.stderr,
  });
});

// 3i. Run Python Add Image Section component CLI
app.post("/api/python/add-image-section", async (req, res) => {
  const title = req.body?.title || "Spectroscopy Graph";
  const file = req.body?.file || "uv_vis_spectrum.png";
  const action = req.body?.action || "Replace";
  const record = JSON.stringify(req.body?.record || {});

  const result = await runPython([
    "-m", "biovia_pipeline.cli", "add-image-section",
    "--title", title,
    "--file", file,
    "--action", action,
    "--record", record,
  ]);
  res.json({
    success: result.exitCode === 0,
    output: result.stdout || result.stderr,
  });
});

// 3j. Run Python Add PDF Section component CLI
app.post("/api/python/add-pdf-section", async (req, res) => {
  const title = req.body?.title || "Experimental Summary Report";
  const file = req.body?.file || "synthesis_summary.pdf";
  const previewPages = req.body?.previewPages || "1-5";
  const record = JSON.stringify(req.body?.record || {});

  const result = await runPython([
    "-m", "biovia_pipeline.cli", "add-pdf-section",
    "--title", title,
    "--file", file,
    "--preview-pages", previewPages,
    "--record", record,
  ]);
  res.json({
    success: result.exitCode === 0,
    output: result.stdout || result.stderr,
  });
});

// 3k. Run Python Add PowerPoint Presentation Section component CLI
app.post("/api/python/add-powerpoint-section", async (req, res) => {
  const title = req.body?.title || "Synthesis Overview Presentation";
  const file = req.body?.file || "synthesis_summary.pptx";
  const previewText = req.body?.previewText || "Preview will be generated when the file is edited.";
  const width = String(req.body?.width || 600);
  const height = String(req.body?.height || 30);
  const record = JSON.stringify(req.body?.record || {});

  const result = await runPython([
    "-m", "biovia_pipeline.cli", "add-powerpoint-section",
    "--title", title,
    "--file", file,
    "--preview-text", previewText,
    "--width", width,
    "--height", height,
    "--record", record,
  ]);
  res.json({
    success: result.exitCode === 0,
    output: result.stdout || result.stderr,
  });
});

// 3l. Run Python Add Word Section component CLI
app.post("/api/python/add-word-section", async (req, res) => {
  const title = req.body?.title || "Assay Standard Operating Procedure";
  const file = req.body?.file || "sop_protocol.docx";
  const previewText = req.body?.previewText || "Preview will be generated when the file is edited.";
  const width = String(req.body?.width || 600);
  const height = String(req.body?.height || 30);
  const record = JSON.stringify(req.body?.record || {});

  const result = await runPython([
    "-m", "biovia_pipeline.cli", "add-word-section",
    "--title", title,
    "--file", file,
    "--preview-text", previewText,
    "--width", width,
    "--height", height,
    "--record", record,
  ]);
  res.json({
    success: result.exitCode === 0,
    output: result.stdout || result.stderr,
  });
});

// 3m. Run Python Extract Sections from Experiment component CLI
app.post("/api/python/extract-sections", async (req, res) => {
  const exp = req.body?.exp || "EXP-2026-XRF-01";
  const what = req.body?.what || "All Section Types";
  const types = Array.isArray(req.body?.types) ? req.body.types : [];
  const record = JSON.stringify(req.body?.record || {});

  const args = [
    "-m", "biovia_pipeline.cli", "extract-sections",
    "--exp", exp,
    "--what", what,
    "--record", record,
  ];
  if (types.length > 0) {
    args.push("--types", ...types);
  }

  const result = await runPython(args);
  res.json({
    success: result.exitCode === 0,
    output: result.stdout || result.stderr,
  });
});

// 3n. Run Python Subprotocol component CLI
app.post("/api/python/subprotocol", async (req, res) => {
  const name = req.body?.name || "Subprotocol";
  const runToCompletion = req.body?.runToCompletion || "False";
  const categorizeUsing = req.body?.categorizeUsing || "";
  const declareLocal = req.body?.declareLocal || "";
  const records = JSON.stringify(req.body?.records || []);

  const args = [
    "-m", "biovia_pipeline.cli", "subprotocol",
    "--name", name,
    "--run-to-completion", runToCompletion,
    "--records", records,
  ];
  if (categorizeUsing) {
    args.push("--categorize-using", categorizeUsing);
  }
  if (declareLocal) {
    args.push("--declare-local", declareLocal);
  }

  const result = await runPython(args);
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

// 8. Analyze Protocol XML (Component Discovery & Blue/Green Classification)
app.post("/api/protocols/analyze", async (req, res) => {
  try {
    const data = (req.body && typeof req.body === "object") ? req.body : {};
    const xmlContent = data.xmlContent;
    if (!xmlContent || typeof xmlContent !== "string") {
      return res.status(400).json({ error: "xmlContent string is required in request body." });
    }

    const pyScript = `
import json, sys
from biovia_pipeline.protocol_migration_engine import analyze_protocol_xml

xml_data = sys.stdin.read()
try:
    analysis = analyze_protocol_xml(xml_data)
    print(json.dumps(analysis.to_dict()))
except Exception as e:
    sys.stderr.write(str(e))
    sys.exit(1)
`;

    const result = await runPython(["-c", pyScript], xmlContent);
    if (result.exitCode !== 0) {
      return res.status(400).json({
        error: "Failed to parse and analyze protocol XML.",
        details: result.stderr || result.stdout,
      });
    }

    // const parsedResult = JSON.parse(result.stdout);
    if (!result.stdout?.trim()) {
      return res.status(500).json({
        error: "Python returned empty output",
        details: result.stderr,
      });
    }

    const parsedResult = JSON.parse(result.stdout);
    res.json({ success: true, analysis: parsedResult });
  } catch (err: unknown) {
    res.status(500).json({ error: (err as Error).message || "Protocol analysis failed." });
  }
});

// 9. Execute Reconstructed Protocol Web App
app.post("/api/protocols/execute-reconstructed", async (req, res) => {
  try {
    const data = (req.body && typeof req.body === "object") ? req.body : {};
    const { experimentNumber, files, analysis } = data;

    // Run Python pipeline orchestrator with extracted parameters
    const exp = experimentNumber || "EXP-2026-XRF-01";
    const fileList = Array.isArray(files) && files.length > 0 ? files : ["sample_analytical_data.xlsx"];

    const pyScript = `
import json
from biovia_pipeline.section_models import SectionType, ElnSectionRecord
from biovia_pipeline.experiment_query import query_experiment
from biovia_pipeline.custom_manipulator import custom_manipulator

exp_num = "${exp}"
files = ${JSON.stringify(fileList)}

# Simulate end-to-end execution of migrated components
record = {
    "experimentnumber": exp_num,
    "status": "In Progress",
    "simplesections": [],
    "_processed_files": [],
}

# Run through reusable section creation steps
for f in files:
    ext = f.split(".")[-1].lower() if "." in f else "bin"
    sec_type = SectionType.EXCEL if ext in ["xlsx", "xls"] else (
        SectionType.PDF if ext == "pdf" else (
            SectionType.WORD if ext in ["docx", "doc"] else (
                SectionType.POWERPOINT if ext in ["pptx", "ppt"] else SectionType.FILE_ATTACHMENT
            )
        )
    )
    sec = ElnSectionRecord(
        section_id=f"sec_{len(record['simplesections'])+1:03d}",
        section_title=f"Uploaded Document: {f}",
        section_type=sec_type,
        files=[f],
        metadata={"source": "Reconstructed Web App", "fileType": ext},
    )
    record["simplesections"].append(sec.to_serialized_node())
    record["_processed_files"].append(f)

record["status"] = "Completed - Synced to ELN"
print(json.dumps({
    "success": True,
    "experimentNumber": exp_num,
    "sectionsCreated": len(record["simplesections"]),
    "sections": record["simplesections"],
    "record": record,
}))
`;

    const runRes = await runPython(["-c", pyScript]);
    if (runRes.exitCode !== 0) {
      return res.status(500).json({ error: runRes.stderr || "Execution failed" });
    }

    res.json(JSON.parse(runRes.stdout));
  } catch (err: unknown) {
    res.status(500).json({ error: (err as Error).message || "Protocol execution failed." });
  }
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
