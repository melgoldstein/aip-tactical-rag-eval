export interface EvaluationStatus { accuracy: number; latency_ms: { p50: number; p95: number }; workflow: string; }
const entities: Record<string,string> = {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"};
const escapeHtml = (value: string): string => value.replace(/[&<>"']/g, character => entities[character]);
export function renderStatus(status: EvaluationStatus): string {
  if (!Number.isFinite(status.accuracy) || status.accuracy < 0 || status.accuracy > 1) throw new Error("Invalid accuracy");
  if (![status.latency_ms.p50,status.latency_ms.p95].every(value => Number.isFinite(value) && value >= 0)) throw new Error("Invalid latency");
  return `<section><h1>Retrieval evaluation</h1><p>${escapeHtml(status.workflow)}</p><dl><dt>Accuracy</dt><dd>${(100*status.accuracy).toFixed(1)}%</dd><dt>p95 latency</dt><dd>${status.latency_ms.p95.toFixed(3)} ms</dd></dl></section>`;
}
