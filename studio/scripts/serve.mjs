import { createServer } from "node:http";
import { readFile, realpath, stat } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import path from "node:path";
import { existsSync } from "node:fs";
import { artifactPage, readArtifact } from "./artifact-pages.mjs";

const root = path.resolve(fileURLToPath(new URL("../", import.meta.url)));
const port = Number(process.env.PORT || 8765);
const types = { ".html":"text/html; charset=utf-8", ".js":"text/javascript; charset=utf-8", ".mjs":"text/javascript; charset=utf-8", ".css":"text/css; charset=utf-8", ".json":"application/json; charset=utf-8", ".svg":"image/svg+xml", ".png":"image/png", ".pptx":"application/vnd.openxmlformats-officedocument.presentationml.presentation", ".docx":"application/vnd.openxmlformats-officedocument.wordprocessingml.document" };
export function createPreviewServer() {
return createServer(async (request, response) => {
  if (!["GET", "HEAD"].includes(request.method)) { response.writeHead(405, {Allow:"GET, HEAD"}); response.end(); return; }
  try {
    const url = new URL(request.url, "http://localhost");
    const pathname = decodeURIComponent(url.pathname);
    if (pathname === "/src/framework/deployment.js") {
      const privateDocuments = existsSync(path.join(root, "reports/qb-project/index.html"));
      const body = Buffer.from(`export const publicSite = false;\nexport const privateDocuments = ${privateDocuments};\n`);
      response.writeHead(200, {"Content-Type":types[".js"], "Content-Length":body.length, "Cache-Control":"no-cache"});
      response.end(request.method === "HEAD" ? undefined : body);
      return;
    }
    if (pathname.startsWith("/examples/")) {
      const artifact = await readArtifact(pathname);
      if (!artifact) { response.writeHead(404); response.end("Not found"); return; }
      const notebook = path.extname(artifact.filename) === ".ipynb";
      const body = notebook ? artifact.body : Buffer.from(artifactPage(artifact.body.toString("utf8"), artifact.resource, url.searchParams.get("lang") === "en" ? "en" : "zh-CN"));
      response.writeHead(200, {"Content-Type":notebook ? "application/x-ipynb+json" : types[".html"], "Content-Length":body.length, "X-Content-Type-Options":"nosniff", "Cache-Control":"no-cache", ...(notebook ? {"Content-Disposition":`attachment; filename="${path.basename(artifact.filename)}"`} : {})});
      response.end(request.method === "HEAD" ? undefined : body);
      return;
    }
    let filename = path.resolve(root, `.${pathname}`);
    if (filename !== path.resolve(root) && !filename.startsWith(root + path.sep)) { response.writeHead(403); response.end("Forbidden"); return; }
    if ((await stat(filename)).isDirectory()) filename = path.join(filename, "index.html");
    filename = await realpath(filename);
    if (!filename.startsWith(root + path.sep)) { response.writeHead(403); response.end("Forbidden"); return; }
    const body = await readFile(filename);
    response.writeHead(200, {"Content-Type":types[path.extname(filename)] || "application/octet-stream", "Content-Length":body.length, "X-Content-Type-Options":"nosniff", "Cache-Control":"no-cache"});
    response.end(request.method === "HEAD" ? undefined : body);
  } catch (error) { response.writeHead(error instanceof URIError ? 400 : 404, {"Content-Type":"text/plain; charset=utf-8"}); response.end(error instanceof URIError ? "Bad request" : "Not found"); }
});
}
if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
const server = createPreviewServer();
server.on("error", error => { console.error(error.message); process.exitCode = 1; });
server.listen(port, "127.0.0.1", () => {
  console.log(`Framework:       http://127.0.0.1:${port}/framework.html`);
  console.log(`Ecosystem guide: http://127.0.0.1:${port}/ecosystem.html`);
  console.log(`Studio:          http://127.0.0.1:${port}/index.html`);
});
}
