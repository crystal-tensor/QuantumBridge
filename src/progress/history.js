// This pointer describes storage only, never function acceptance or test freshness.
export function archiveDescriptor(value) {
  const compressed = value?.format === "quantumbridge.engineering-history-pointer.v2";
  if (!value || (!compressed && value.format !== "quantumbridge.engineering-history-pointer.v1") ||
      !(compressed ? /^history\/catalog-[0-9a-f]{64}\.json\.gz$/ : /^history\/catalog-[0-9a-f]{64}\.json$/).test(value.file) ||
      !/^[0-9a-f]{64}$/.test(value.sha256) || !value.file.includes(value.sha256) ||
      !Number.isSafeInteger(value.bytes) || value.bytes <= 0 || value.bytes > 16 * 1024 ** 2 ||
      value.replayIsNotNewVerification !== true || value.newFunctionAcceptances !== 0) return null;
  if (compressed && (value.encoding !== "gzip-bytes" || !value.original ||
      !/^catalog-[0-9a-f]{64}\.json$/.test(value.original.file) ||
      !/^[0-9a-f]{64}$/.test(value.original.sha256) || !value.original.file.includes(value.original.sha256) ||
      !Number.isSafeInteger(value.original.bytes) || value.original.bytes <= 0 || value.original.bytes > 16 * 1024 ** 2)) return null;
  return value;
}
