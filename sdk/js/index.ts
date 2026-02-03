export class AgenticRAGClient {
  baseUrl: string;
  constructor(baseUrl: string) {
    this.baseUrl = baseUrl.replace(/\/$/, "");
  }
  async chat(sessionId: string, query: string) {
    const resp = await fetch(`${this.baseUrl}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: sessionId, query }),
    });
    if (!resp.ok) throw new Error(await resp.text());
    return resp.json();
  }
  async upload(files: File[]) {
    const fd = new FormData();
    files.forEach((f) => fd.append("files", f, f.name));
    const resp = await fetch(`${this.baseUrl}/api/upload`, {
      method: "POST",
      body: fd,
    });
    if (!resp.ok) throw new Error(await resp.text());
    return resp.json();
  }
}
