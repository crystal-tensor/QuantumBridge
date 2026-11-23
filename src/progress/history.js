// This pointer describes storage only, never function acceptance or test freshness.
export function archiveDescriptor(value) {
  if (!value || value.format !== "quantumbridge.engineering-history-pointer.v1" ||
      !/^history\/catalog-[0-9a-f]{64}\.json$/.test(value.file) ||
      !/^[0-9a-f]{64}$/.test(value.sha256) || !value.file.includes(value.sha256) ||
      !Number.isSafeInteger(value.bytes) || value.bytes <= 0 || value.bytes > 16 * 1024 ** 2 ||
      value.replayIsNotNewVerification !== true || value.newFunctionAcceptances !== 0) return null;
  return value;
}
