// Only equal JSON authorization tables are pooled; worker identities remain separate.
const field="verification_migration_pool", reference="approved_test_migrations_ref";
const plain=value=>value!==null&&typeof value==="object"&&!Array.isArray(value);
export async function restoreMigrationPool(value){
  const pool=value[field];
  if(pool===undefined){
    if((value.verification||[]).some(row=>Object.hasOwn(row,reference)))throw Error("Missing migration pool");
    return value;
  }
  if(!plain(pool)||pool.schema!==1||pool.encoding!=="approved-test-migrations-pool-v1"||!plain(pool.contexts)||
      Object.keys(pool).sort().join(",")!=="contexts,encoding,schema"||Object.keys(pool.contexts).length>4096)throw Error("Invalid migration pool");
  const contexts=new Map(), encoder=new TextEncoder();
  let total=0;
  for(const [key,item] of Object.entries(pool.contexts)){
    if(!/^[0-9a-f]{64}$/.test(key)||!plain(item)||item.sha256!==key||typeof item.json!=="string"||
        Object.keys(item).sort().join(",")!=="bytes,json,sha256"||!Number.isSafeInteger(item.bytes)||item.bytes<1||item.bytes>8*1024**2)throw Error("Invalid migration context");
    const bytes=encoder.encode(item.json);total+=bytes.length;
    if(total>16*1024**2||bytes.length!==item.bytes)throw Error("Migration context size differs");
    const hash=Array.from(new Uint8Array(await crypto.subtle.digest("SHA-256",bytes)),byte=>byte.toString(16).padStart(2,"0")).join("");
    if(hash!==key)throw Error("Migration context hash differs");
    const table=JSON.parse(item.json);
    if(!Array.isArray(table)||!table.length||!table.every(plain))throw Error("Expected a migration table");
    contexts.set(key,table);
  }
  const used=new Set();
  const rows=(value.verification||[]).map(original=>{
    if(!plain(original))throw Error("Invalid verification record");
    const row={...original};
    if(Object.hasOwn(row,reference)){
      const key=row[reference];
      if(typeof key!=="string"||!contexts.has(key)||Object.hasOwn(row,"approved_test_migrations"))throw Error("Missing or ambiguous migration context");
      // Most rows are never expanded. Materialize an independent table on first access.
      const materialize=value=>Object.defineProperty(row,"approved_test_migrations",{
        value,writable:true,enumerable:true,configurable:true});
      Object.defineProperty(row,"approved_test_migrations",{enumerable:true,configurable:true,
        get(){const table=structuredClone(contexts.get(key));materialize(table);return table;},
        set(value){materialize(value);}});
      delete row[reference];used.add(key);
    }
    return row;
  });
  if(used.size!==contexts.size)throw Error("Unused migration context");
  const result={...value,verification:rows};delete result[field];return result;
}
