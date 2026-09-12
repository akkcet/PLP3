/**
 * Types for Biovia Pipeline Pilot (PLP) Protocol to Python Refactoring Studio
 */

export interface PlpComponent {
  id: string;
  name: string;
  type: "filter" | "python" | "manipulator" | "ui_form" | "ui_element" | "file_op" | "notebook" | "subprotocol";
  displayName: string;
  description: string;
  point?: { x: number; y: number };
  guid?: string;
  pilotScript?: string;
  pythonScript?: string;
  parameters: Record<string, any>;
  mappedPythonFunction: {
    module: string;
    functionName: string;
    signature: string;
    docstring: string;
    code: string;
  };
  threatAnalysis?: {
    risk: string;
    countermeasure: string;
  };
}

export interface PlpConnection {
  from: string;
  to: string;
  type: "pass" | "fail" | "true" | "false";
}

export interface PlpProtocol {
  name: string;
  version: string;
  author?: string;
  registrationDate?: string;
  components: PlpComponent[];
  connections: PlpConnection[];
}

export interface PythonModuleFile {
  filename: string;
  path: string;
  description: string;
  category: "core" | "integrations" | "parser" | "orchestrator" | "tests" | "cli";
  code: string;
}

export interface PilotScriptToken {
  type: "VARIABLE" | "GLOBAL" | "KEYWORD" | "OPERATOR" | "STRING" | "NUMBER" | "FUNCTION" | "PUNCTUATION" | "UNKNOWN";
  value: string;
  position: number;
}

export interface TranspileResult {
  pythonCode: string;
  tokens: PilotScriptToken[];
  astSummary: string[];
  explanation: string;
  testEvaluation?: {
    success: boolean;
    result: any;
    error?: string;
  };
}

export interface WorkflowSimulationStep {
  stepId: string;
  title: string;
  componentName: string;
  status: "idle" | "running" | "completed" | "failed";
  timestamp?: string;
  details: string;
  inputData: Record<string, any>;
  outputData: Record<string, any>;
  logOutput: string[];
}
