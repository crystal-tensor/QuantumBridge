import { lstat, readFile, realpath } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { verifiedEvidence } from "../src/progress/transport.js";

export async function readManifestEvidence(directory, descriptor) {
  const base = directory instanceof URL ? directory : pathToFileURL(path.resolve(directory) + path.sep);
  const parent = fileURLToPath(base);
  return verifiedEvidence(new URL(descriptor.file, base), descriptor, { fetcher: async (url, options) => {
    const filename = fileURLToPath(url);
    const stat = await lstat(filename);
    if (path.dirname(filename) !== path.resolve(parent) || stat.isSymbolicLink() ||
        (await lstat(parent)).isSymbolicLink() || await realpath(path.dirname(filename)) !== await realpath(parent) ||
        stat.size > 100 * 1024 ** 2 - 1) throw new Error("Evidence file escaped its bounded directory");
    return new Response(options.method === "HEAD" ? null : await readFile(filename),
      { headers: { "content-length": String(stat.size) } });
  } });
}
