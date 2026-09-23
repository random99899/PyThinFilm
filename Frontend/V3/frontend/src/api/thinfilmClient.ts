import type { DesignDraft, DesignSimulationResult, MaterialOption } from "@/types/design";

const browserApiHost = window.location.hostname || "127.0.0.1";
export const API_BASE_URL = window.thinfilmDesktop?.apiBaseUrl ?? `http://${browserApiHost}:8122`;

async function responseJson<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const payload = (await response.json().catch(() => null)) as { detail?: string } | null;
    throw new Error(payload?.detail ?? `请求失败：${response.status}`);
  }
  return (await response.json()) as T;
}
export async function listMaterials(signal?: AbortSignal): Promise<MaterialOption[]> {
  return responseJson<MaterialOption[]>(await fetch(`${API_BASE_URL}/api/materials`, { signal }));
}

export async function simulateDesign(
  draft: DesignDraft,
  requestId: string,
  signal?: AbortSignal,
): Promise<DesignSimulationResult> {
  return responseJson<DesignSimulationResult>(
    await fetch(`${API_BASE_URL}/api/designs/simulate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ...draft, request_id: requestId }),
      signal,
    }),
  );
}
