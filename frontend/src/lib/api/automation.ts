// ============================================================================
// API Client — Automation Hub
// ============================================================================

const BFF_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export interface Execution {
  id: string;
  script_content: string;
  status: "Pending" | "Success" | "Failed";
  exit_code: number | null;
  output: string | null;
  created_at: string;
  updated_at: string;
}

/**
 * Runs a new shell script.
 */
export async function runScript(script_content: string): Promise<Execution> {
  const res = await fetch(`${BFF_URL}/scripts/run`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ script_content }),
    credentials: "include",
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to execute script");
  }

  return res.json();
}

/**
 * Retrieves a list of past executions.
 */
export async function getExecutions(): Promise<Execution[]> {
  const res = await fetch(`${BFF_URL}/scripts/executions`, {
    method: "GET",
    credentials: "include",
  });

  if (!res.ok) {
    throw new Error("Failed to fetch executions");
  }

  return res.json();
}

/**
 * Retrieves a single execution details.
 */
export async function getExecution(id: string): Promise<Execution> {
    const res = await fetch(`${BFF_URL}/scripts/executions/${id}`, {
      method: "GET",
      credentials: "include",
    });
  
    if (!res.ok) {
      throw new Error("Failed to fetch execution details");
    }
  
    return res.json();
  }
