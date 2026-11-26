import { inflateBounded, verifiedBytes } from "./transport.js?http=history-index-20261126";

export const historyIndexFormat = "quantumbridge.engineering-history-index-gzip.v1";
export const historyIndexLimit = 16 * 1024 ** 2;
const hash = value => typeof value === "string" && /^[0-9a-f]{64}$/.test(value);
const size = value => Number.isSafeInteger(value) && value > 0 && value <= historyIndexLimit;
const digest = async bytes => [...new Uint8Array(await crypto.subtle.digest("SHA-256", bytes))]
  .map(value => value.toString(16).padStart(2, "0")).join("");

export function historyIndexReference(value) {
  if (!value || Array.isArray(value) || value.format !== historyIndexFormat || value.encoding !== "gzip-bytes" ||
      value.original_file !== "history.json" || !size(value.bytes) || !hash(value.sha256) ||
      !size(value.compressed_bytes) || !hash(value.compressed_sha256) ||
      value.file !== `history-index-${value.compressed_sha256}.json.gz` ||
      value.replayIsNotNewVerification !== true || value.newFunctionAcceptances !== 0) return null;
  return value;
}

export async function historyIndexBytes(url, value, options) {
  const item = historyIndexReference(value);
  if (!item) throw new Error("Invalid historical index transport");
  const compressed = await verifiedBytes(new URL(item.file, url),
    { bytes: item.compressed_bytes, sha256: item.compressed_sha256 }, options);
  const raw = await inflateBounded(compressed, item.bytes);
  if (raw.length !== item.bytes || await digest(raw) !== item.sha256) {
    throw new Error("Original historical index bytes/hash differ");
  }
  return raw;
}

export async function restoreHistoryIndex(value, url, options) {
  if (Array.isArray(value)) return value;
  const raw = await historyIndexBytes(url, value, options);
  const result = JSON.parse(new TextDecoder("utf-8", { fatal: true }).decode(raw));
  if (!Array.isArray(result)) throw new Error("Historical index must retain its original array");
  return result;
}
