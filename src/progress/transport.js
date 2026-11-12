const CHUNK_BYTES = 1024 * 1024;
const CONCURRENCY = 8;

function byteLength(value) {
  return /^\d+$/.test(value || "") && Number.isSafeInteger(Number(value)) && Number(value) > 0 ? Number(value) : null;
}

export async function verifiedBytes(url, descriptor, { fetcher = globalThis.fetch, chunkBytes = CHUNK_BYTES, concurrency = CONCURRENCY } = {}) {
  if (!/^[0-9a-f]{64}$/.test(descriptor.sha256 || "")) throw new Error("Missing artifact SHA-256");
  if (!Number.isSafeInteger(chunkBytes) || chunkBytes < 1 || !Number.isSafeInteger(concurrency) || concurrency < 1 || concurrency > CONCURRENCY) throw new Error("Invalid transfer bounds");
  const target = new URL(url);
  target.searchParams.set("sha256", descriptor.sha256);
  const options = { cache: "no-cache" };
  let size = descriptor.bytes ?? null;
  if (size !== null && (!Number.isSafeInteger(size) || size < 1)) throw new Error("Invalid artifact size");
  let ranged = false;
  try {
    const head = await fetcher(target, { ...options, method: "HEAD" });
    if (head.ok) {
      const observed = byteLength(head.headers.get("content-length"));
      if (size !== null && observed !== null && size !== observed) throw new Error("Artifact size mismatch");
      size ??= observed;
      ranged = head.headers.get("accept-ranges") === "bytes";
    }
  } catch (error) {
    if (error.message === "Artifact size mismatch") throw error;
  }
  let bytes;
  if (ranged && size > chunkBytes) {
    const controller = new AbortController();
    const chunks = new Array(Math.ceil(size / chunkBytes));
    let cursor = 0;
    async function worker() {
      while (cursor < chunks.length) {
        const index = cursor++, start = index * chunkBytes, end = Math.min(size - 1, start + chunkBytes - 1);
        const response = await fetcher(target, { ...options, signal: controller.signal, headers: { Range: `bytes=${start}-${end}` } });
        if (response.status !== 206 || response.headers.get("content-range") !== `bytes ${start}-${end}/${size}`) throw new Error("Invalid artifact range response");
        const chunk = new Uint8Array(await response.arrayBuffer());
        if (chunk.byteLength !== end - start + 1) throw new Error("Incomplete artifact range");
        chunks[index] = chunk;
      }
    }
    const workers = Array.from({ length: Math.min(concurrency, chunks.length) }, () => worker());
    try { await Promise.all(workers); }
    catch (error) { controller.abort(); await Promise.allSettled(workers); throw error; }
    bytes = new Uint8Array(size);
    chunks.forEach((chunk, index) => bytes.set(chunk, index * chunkBytes));
  } else {
    const response = await fetcher(target, options);
    if (!response.ok) throw new Error(`Artifact HTTP ${response.status}`);
    bytes = new Uint8Array(await response.arrayBuffer());
    if (size !== null && bytes.byteLength !== size) throw new Error("Artifact size mismatch");
  }
  const hash = [...new Uint8Array(await crypto.subtle.digest("SHA-256", bytes))].map(value => value.toString(16).padStart(2, "0")).join("");
  if (hash !== descriptor.sha256) throw new Error("Artifact integrity mismatch");
  return bytes;
}

export async function verifiedJSON(url, descriptor, options) {
  const bytes = await verifiedBytes(url, descriptor, options);
  const stream = new Blob([bytes]).stream().pipeThrough(new DecompressionStream("gzip"));
  return new Response(stream).json();
}
