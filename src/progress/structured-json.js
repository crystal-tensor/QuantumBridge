// Use ordinary JSON.parse on bounded, standard-parser-indexed byte spans.
const MAX_BYTES = 4 * 1024 ** 3;
export const structuredJSONLeafLimit = 8 * 1024 ** 2;
const decode = bytes => new TextDecoder('utf-8', { fatal: true }).decode(bytes);
const whitespace = bytes => bytes.length <= structuredJSONLeafLimit && /^[\x20\t\r\n]*$/.test(decode(bytes));
const hash = bytes => crypto.subtle.digest('SHA-256', bytes).then(value =>
  [...new Uint8Array(value)].map(x => x.toString(16).padStart(2, '0')).join(''));

export async function parseStructuredJSON(raw, structure) {
  if (!(raw instanceof Uint8Array) || raw.length < 1 || raw.length > MAX_BYTES)
    throw new Error('JSON byte bounds differ');
  if (structure === undefined) return JSON.parse(decode(raw));
  const relative = structure?.format === 'quantumbridge.structured-json-relative.v2';
  if ((!relative && structure?.format !== 'quantumbridge.structured-json.v1') || structure.bytes !== raw.length ||
      structure.leaf_byte_limit !== structuredJSONLeafLimit || !/^[a-f0-9]{64}$/.test(structure.sha256 || '') ||
      await hash(raw) !== structure.sha256) throw new Error('Structured JSON identity differs');
  let nodes = 0, largestLeaf = 0;
  function span(node, base) {
    if (!Array.isArray(node) || ![2, 4].includes(node.length) ||
        !Number.isSafeInteger(node[0]) || !Number.isSafeInteger(node[1]) || node[0] < 0 ||
        (relative && node[1] < 1)) throw new Error('Structured JSON span bounds differ');
    const start = relative ? base + node[0] : node[0];
    const end = relative ? start + node[1] : node[1];
    if (!Number.isSafeInteger(start) || !Number.isSafeInteger(end) || start < 0 || end <= start || end > raw.length)
      throw new Error('Structured JSON span bounds differ');
    return [start, end];
  }
  function parse(node, depth = 0, base = 0) {
    if (++nodes > 500000 || depth > 128 || !Array.isArray(node) || ![2, 4].includes(node.length))
      throw new Error('Structured JSON node bounds differ');
    const [start, end] = span(node, base);
    const [, , kind, children] = node;
    if (node.length === 2) {
      if (end - start > structuredJSONLeafLimit) throw new Error('Structured JSON leaf exceeds its bound');
      largestLeaf = Math.max(largestLeaf, end - start);
      return JSON.parse(decode(raw.subarray(start, end)));
    }
    if (!['array', 'object'].includes(kind) || !Array.isArray(children) || children.length < 1 ||
        raw[start] !== (kind === 'array' ? 91 : 123) || raw[end - 1] !== (kind === 'array' ? 93 : 125))
      throw new Error('Structured JSON container differs');
    const result = kind === 'array' ? [] : {};
    let cursor = start + 1;
    for (const [index, entry] of children.entries()) {
      if (!Array.isArray(entry) || entry.length !== 2 || !Array.isArray(entry[1]))
        throw new Error('Structured JSON child differs');
      const [key, child] = entry;
      const [childStart, childEnd] = span(child, cursor);
      if (childStart < cursor || childEnd >= end)
        throw new Error('Structured JSON child coverage differs');
      if (childStart - cursor > structuredJSONLeafLimit) throw new Error('Structured JSON separator exceeds its bound');
      const gap = decode(raw.subarray(cursor, childStart));
      if (kind === 'array') {
        if (key !== index || !new RegExp(index ? '^[\\x20\\t\\r\\n]*,[\\x20\\t\\r\\n]*$' : '^[\\x20\\t\\r\\n]*$').test(gap))
          throw new Error('Structured JSON array coverage differs');
        result.push(parse(child, depth + 1, cursor));
      } else {
        let prefix = gap;
        if (index) {
          const match = /^[\x20\t\r\n]*,/.exec(prefix);
          if (!match) throw new Error('Structured JSON object separator differs');
          prefix = prefix.slice(match[0].length);
        }
        const colon = prefix.lastIndexOf(':');
        if (colon < 0 || !/^[\x20\t\r\n]*$/.test(prefix.slice(colon + 1)))
          throw new Error('Structured JSON object colon differs');
        const parsedKey = JSON.parse(prefix.slice(0, colon));
        if (typeof key !== 'string' || Object.hasOwn(result, key) || typeof parsedKey !== 'string' || parsedKey !== key)
          throw new Error('Structured JSON object coverage differs');
        Object.defineProperty(result, key, { value: parse(child, depth + 1, cursor), enumerable: true, writable: true, configurable: true });
      }
      cursor = childEnd;
    }
    if (!whitespace(raw.subarray(cursor, end - 1))) throw new Error('Structured JSON trailing container content');
    return result;
  }
  const root = structure.root;
  const value = parse(root);
  const [rootStart, rootEnd] = span(root, 0);
  if (!whitespace(raw.subarray(0, rootStart)) || !whitespace(raw.subarray(rootEnd)))
    throw new Error('Structured JSON trailing document content');
  if (structure.nodes !== nodes || structure.largest_leaf_bytes !== largestLeaf)
    throw new Error('Structured JSON traversal totals differ');
  return value;
}
