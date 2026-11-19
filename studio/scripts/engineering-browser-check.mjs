import assert from "node:assert/strict";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import { pathToFileURL } from "node:url";
import { createHash } from "node:crypto";
import { gunzipSync } from "node:zlib";
import { createPreviewServer } from "./serve.mjs";
import { abnormalObservations, currentVerification, originalChildFollowup } from "../src/progress/model.js";
import { readProgressSnapshot } from "./read-progress-snapshot.mjs";

const snapshot=await readProgressSnapshot(new URL("../src/progress/data/manifest.json",import.meta.url));
const evidenceWire=JSON.parse(gunzipSync(await readFile(new URL("../src/progress/data/manifest-evidence.json.gz",import.meta.url))));
const evidenceUsesSnapshot=evidenceWire.schema===2&&evidenceWire.encoding==="deferred-manifest-snapshot-v2";
const manifestBody=await readFile(new URL("../src/progress/data/manifest.json",import.meta.url));
const manifestIndex=JSON.parse(manifestBody);
const snapshotSha=manifestIndex.public_snapshot_format ? manifestIndex.sha256 : createHash("sha256").update(manifestBody).digest("hex");
const core=currentVerification(snapshot);
const childFollowup=originalChildFollowup(snapshot);
const childFollowupBatch=snapshot.goal_execution?.original_child_followup_validation;
if(childFollowupBatch?.source_fingerprint===snapshot.source?.fingerprint)assert.ok(childFollowup);
else assert.equal(childFollowup,null);
const expectedMigrations=new Map(snapshot.verification.filter(run=>run.source_match)
  .flatMap(run=>run.approved_test_migrations||[]).map(row=>[row.file+":"+row.after_sha256,row]));

// A short-lived OS-assigned port is QA-only. Owner-facing delivery stays on Pages.
const { chromium } = await import(process.env.PLAYWRIGHT_MODULE ? pathToFileURL(process.env.PLAYWRIGHT_MODULE).href : "playwright");
const server=process.env.QB_QA_BASE_URL ? null : createPreviewServer();
if(server) await new Promise(resolve=>server.listen(0,"127.0.0.1",resolve));
const base=process.env.QB_QA_BASE_URL?.replace(/\/$/,"") || `http://127.0.0.1:${server.address().port}`;
let browser, activePage, activeViewport, activeNetwork, activeTimings;
const output=process.env.QB_QA_OUTPUT || "/tmp/qb-engineering-qa";
await mkdir(output,{recursive:true});
const results=[];
try{
  browser=await chromium.launch({headless:true,...(process.env.CHROMIUM_PATH?{executablePath:process.env.CHROMIUM_PATH}:{}),...(process.env.QB_QA_PROXY?{proxy:{server:process.env.QB_QA_PROXY,bypass:"127.0.0.1,localhost"}}:{})});
  for(const viewport of [{width:1440,height:1000},{width:390,height:844}]){
    const page=await browser.newPage({viewport});const errors=[],requests=[];page.on("pageerror",e=>errors.push(e.message));page.on("request",r=>requests.push(new URL(r.url()).pathname));
    activePage=page;activeViewport=viewport;activeNetwork=[];
    const network=activeNetwork,timings=activeTimings={};
    page.on("response",response=>{
      if(!new URL(response.url()).pathname.startsWith("/QuantumBridge/src/progress/")&&!new URL(response.url()).pathname.startsWith("/src/progress/"))return;
      const headers=response.headers();
      network.push({at:Date.now(),url:response.url(),method:response.request().method(),range:response.request().headers().range,
        status:response.status(),headers:Object.fromEntries(["content-length","content-range","content-encoding","accept-ranges","etag","age"].filter(key=>headers[key]!==undefined).map(key=>[key,headers[key]]))});
    });
    await page.goto(`${base}/framework.html?category=finance&lang=zh`);
    let started=Date.now();
    await page.getByRole("link",{name:"工程进展",exact:true}).click();
    await page.getByRole("heading",{name:"工程进展",exact:true}).waitFor();
    timings.initialHeadingMs=Date.now()-started;
    assert.ok(requests.some(url=>url.endsWith("/manifest-browser.json.gz")));
    assert.equal(requests.some(url=>url.endsWith("/manifest-evidence.json.gz")),false);
    assert.equal(requests.some(url=>url.endsWith("/manifest.json.gz")),false);
    assert.equal(requests.some(url=>url.endsWith("/manifest.json")),false);
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
    const skip=page.getByRole("link",{name:"跳到工程清单",exact:true});
    await page.locator(".identity").focus();
    await page.keyboard.press("Shift+Tab");
    assert.equal(await skip.evaluate(element=>element.matches(":focus-visible")),true);
    assert.ok(await skip.evaluate(element=>element.getBoundingClientRect().top>=0));
    await page.getByRole("heading",{name:"工程进展",exact:true}).click();
    await page.getByRole("button",{name:"总览",exact:true}).click();
    await page.screenshot({path:`${output}/overview-${viewport.width}.png`,fullPage:true});
    await page.getByRole("button",{name:"函数清单",exact:true}).click();
    await page.getByRole("searchbox",{name:"搜索函数"}).fill("RZXGate");
    assert.ok(await page.locator("tbody tr").count()>0);
    await page.locator("[data-filter=status]").selectOption("partial");
    await page.locator("tbody .name-link").first().click();
    assert.equal(await page.locator("dialog[open]").count(),1);
    await page.screenshot({path:`${output}/function-${viewport.width}.png`,fullPage:false});
    await page.getByRole("button",{name:"关闭",exact:true}).click();
    assert.equal(await page.locator("tbody .name-link").first().evaluate(element=>element===document.activeElement),true);
    await page.getByRole("button",{name:"Native 源码",exact:true}).click();
    await page.locator('[data-dataset="native"][aria-pressed="true"]').waitFor();
    await page.getByRole("button",{name:"重置筛选",exact:true}).click();
    await page.locator("[data-filter=status]").selectOption("not_implemented");
    assert.ok((await page.locator("tbody").innerText()).includes("ParityMapper.map"));
    started=Date.now();
    await page.getByRole("button",{name:"导出与继承",exact:true}).click();
    await page.locator('[data-dataset="runtime"][aria-pressed="true"]').waitFor({timeout:120000});
    timings.runtimeInventoryMs=Date.now()-started;
    await page.getByRole("button",{name:"重置筛选",exact:true}).click();
    await page.getByRole("searchbox",{name:"搜索函数"}).fill("pennylane.RX.matrix");
    assert.ok(await page.locator("tbody .name-link").count()>0);
    await page.locator("tbody .name-link").first().click();
    await page.getByRole("heading",{name:"公共暴露路径与继承合同",exact:true}).waitFor();
    assert.ok(requests.some(url=>/\/runtime-details-[0-9a-f]{2}\.json\.gz$/.test(url)));
    assert.equal(requests.some(url=>url.endsWith("/runtime.json.gz")),false);
    await page.locator("dialog details").first().locator("summary").click();
    assert.ok((await page.locator("dialog").innerText()).includes("POSITIONAL_OR_KEYWORD"));
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
    await page.screenshot({path:`${output}/runtime-inheritance-${viewport.width}.png`,fullPage:false});
    await page.getByRole("button",{name:"关闭",exact:true}).click();
    assert.equal(await page.locator("tbody .name-link").first().evaluate(element=>element===document.activeElement),true);
    started=Date.now();
    await page.getByRole("button",{name:"测试与真机",exact:true}).click();
    const collectionSection=page.locator("#test-collection");
    await collectionSection.getByRole("heading",{name:"测试收集：不是测试通过",exact:true}).waitFor();
    timings.completeEvidenceMs=Date.now()-started;
    assert.ok(requests.some(url=>url.endsWith("/manifest-evidence.json.gz")));
    assert.equal(requests.some(url=>url.endsWith("/manifest.json.gz")),evidenceUsesSnapshot);
    assert.equal(await collectionSection.locator("tbody tr").count(),2);
    assert.ok((await collectionSection.innerText()).includes("35,955"));
    assert.ok((await collectionSection.innerText()).includes("35,956"));
    assert.ok((await collectionSection.innerText()).includes("完整执行仍未完成"));
    const compilerSection=collectionSection.locator("#compiler-execution");
    await compilerSection.getByRole("heading",{name:"编译目录：仍有未验收案例",exact:true}).waitFor();
    assert.equal(await compilerSection.locator("li").count(),2);
    assert.ok((await compilerSection.innerText()).includes("1,300 / 1,301"));
    assert.ok((await compilerSection.innerText()).includes("140"));
    assert.ok((await compilerSection.innerText()).includes("保留旧快照的指纹和测试时间"));
    const currentValidation=page.locator("#current-validation");
    assert.ok((await currentValidation.innerText()).includes(snapshot.source.fingerprint));
    assert.ok((await currentValidation.innerText()).includes(core.batch.checkpoint));
    if(core.reviewMatches) {
      for(const [profile,count] of Object.entries(core.reviewCounts)) assert.ok((await currentValidation.innerText()).includes(`${profile}: ${count}`));
      assert.ok((await currentValidation.innerText()).includes("不是全库失败总数"));
    }
    else assert.ok((await currentValidation.innerText()).includes("严格失败身份待重新核验"));
    assert.ok((await currentValidation.innerText()).includes("当前冻结源码"));
    const unadmittedModules=(core.batch.profiles||[]).flatMap(row=>
      (row.unadmitted_modules||[]).map(name=>({profile:row.profile,name})));
    const unadmittedSection=currentValidation.locator("#unadmitted-validation");
    if(unadmittedModules.length){
      await unadmittedSection.locator("summary").click();
      assert.equal(await unadmittedSection.locator("li").count(),unadmittedModules.length);
      for(const item of unadmittedModules){
        assert.ok((await unadmittedSection.innerText()).includes(item.name));
        assert.ok((await unadmittedSection.innerText()).includes(item.profile));
      }
      assert.ok((await unadmittedSection.innerText()).includes("不计入通过"));
      assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
      await unadmittedSection.screenshot({path:`${output}/unadmitted-validation-${viewport.width}.png`});
      await unadmittedSection.locator("summary").click();
    }else assert.equal(await unadmittedSection.count(),0);
    const followupSection=currentValidation.locator("#original-child-followup");
    if(childFollowup){
      assert.equal(await followupSection.locator("[data-child-proof]").count(),4);
      for(const row of childFollowup.rows){
        assert.ok((await followupSection.innerText()).includes(row.profile));
        assert.ok((await followupSection.innerText()).includes(row.evidence_hash));
      }
      assert.ok((await followupSection.innerText()).includes("证据仍拒收"));
      assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
      await followupSection.screenshot({path:`${output}/original-child-followup-${viewport.width}.png`});
    }else assert.equal(await followupSection.count(),0);
    if(core.references.length){
      const referenceSection=currentValidation.locator("#reference-validation");
      await referenceSection.getByRole("heading",{name:"独立 SDK 参考配置",exact:true}).waitFor();
      for(const reference of core.references){
        assert.equal(reference.matches,true);
        assert.ok((await referenceSection.innerText()).includes(reference.profile));
        assert.ok((await referenceSection.innerText()).includes(`${reference.counts.failed} FAIL`));
        assert.ok((await referenceSection.innerText()).includes(`${reference.counts.skipped} SKIP`));
      }
      assert.ok((await referenceSection.innerText()).includes("不豁免"));
      await referenceSection.screenshot({path:`${output}/reference-groups-${viewport.width}.png`});
      assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
    }
    const textOverflow = await currentValidation.locator(":scope > .table-wrap > table").evaluate(table => {
      const violations = [];
      for (const cell of table.querySelectorAll("th, td")) {
        const bounds = cell.getBoundingClientRect();
        const walker = document.createTreeWalker(cell, NodeFilter.SHOW_TEXT);
        while (walker.nextNode()) {
          if (!walker.currentNode.textContent.trim()) continue;
          const range = document.createRange();
          range.selectNodeContents(walker.currentNode);
          for (const rect of range.getClientRects()) {
            if (rect.left < bounds.left - 1 || rect.right > bounds.right + 1 ||
                rect.top < bounds.top - 1 || rect.bottom > bounds.bottom + 1) {
              violations.push(walker.currentNode.textContent);
              break;
            }
          }
        }
      }
      return violations;
    });
    assert.deepEqual(textOverflow, [], "Verification text must stay inside its own table cell");
    await currentValidation.locator("#historical-validation summary").click();
    assert.ok((await currentValidation.locator("#historical-validation").innerText()).includes("85fe4e23"));
    await currentValidation.locator("#historical-ci summary").click();
    assert.ok((await currentValidation.locator("#historical-ci").innerText()).includes("8276"));
    assert.equal(await page.locator("[data-verification-run]").count(),20);
    const firstRun=await page.locator("[data-verification-run] strong").first().innerText();
    await page.getByRole("button",{name:"下一批记录",exact:true}).click();
    assert.equal(await page.locator("[data-verification-run]").count(),20);
    assert.notEqual(await page.locator("[data-verification-run] strong").first().innerText(),firstRun);
    await page.getByRole("button",{name:"上一批记录",exact:true}).click();
    await currentValidation.scrollIntoViewIfNeeded();
    await page.screenshot({path:`${output}/current-validation-${viewport.width}.png`,fullPage:false});
    await currentValidation.getByRole("heading",{name:"本地融合验证与远端 CI 分开验收",exact:true}).scrollIntoViewIfNeeded();
    await page.screenshot({path:`${output}/current-source-header-${viewport.width}.png`,fullPage:false});
    await compilerSection.locator("summary").click();
    assert.ok((await compilerSection.innerText()).includes("quantumbridge.mps-2-best"));
    await collectionSection.scrollIntoViewIfNeeded();
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
    await page.screenshot({path:`${output}/test-collection-${viewport.width}.png`,fullPage:false});
    const processSection=page.locator("section.band").filter({has:page.getByRole("heading",{name:"异常进程：不计入验证",exact:true})});
    assert.equal(await processSection.locator("details").count(),abnormalObservations(snapshot.goal_execution).length);
    for(const summary of await processSection.locator("summary").all()) await summary.click();
    assert.ok((await processSection.innerText()).includes("SIGSEGV (-11)"));
    assert.ok((await processSection.innerText()).includes("runtime-census-combined"));
    assert.ok((await processSection.innerText()).includes("采集输出 SHA-256"));
    for(const row of abnormalObservations(snapshot.goal_execution)) {
      if(row.crash_report_sha256) assert.ok((await processSection.innerText()).includes(row.crash_report_sha256));
    }
    assert.equal((await processSection.innerText()).includes("undefined"),false);
    // Capture receipts in bounded viewports rather than resizing a long page.
    const processDetails=await processSection.locator("details").all();
    for(const [index,detail] of processDetails.entries()){
      const geometry=await detail.evaluate(element=>({top:element.getBoundingClientRect().top+scrollY,
        height:element.getBoundingClientRect().height}));
      for(let offset=0;offset<geometry.height;offset+=viewport.height){
        await page.evaluate(top=>window.scrollTo({top,behavior:"instant"}),geometry.top+offset);
        assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
        await page.screenshot({path:`${output}/abnormal-long-hashes-${viewport.width}-${index}-${offset}.png`,fullPage:false});
      }
    }
    await processSection.locator("details").last().locator("summary").scrollIntoViewIfNeeded();
    assert.equal(await skip.evaluate(element=>element===document.activeElement),false);
    await page.screenshot({path:`${output}/abnormal-viewport-${viewport.width}.png`,fullPage:false});
    await processSection.getByRole("link",{name:"Arrow 版本对照：24.0.0 / 25.0.1",exact:true}).click();
    await page.locator("#diag-arrow_coexistence_dependency_review").waitFor();
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
    await page.screenshot({path:`${output}/abnormal-process-${viewport.width}.png`,fullPage:false});
    assert.ok((await page.locator("#view").innerText()).includes("INCONCLUSIVE"));
    await page.getByRole("heading",{name:"本目标冻结源码验证",exact:true}).waitFor();
    const diagnostics=page.locator("section.band").filter({has:page.getByRole("heading",{name:"诊断对照：不计入验收通过",exact:true})});
    assert.equal(await diagnostics.locator("details").count(),snapshot.diagnostic_observations.length);
    const diagnosticDownload=page.waitForEvent("download");
    await diagnostics.getByRole("link",{name:"最小 TensorFlow 对照代码",exact:true}).click();
    assert.equal((await diagnosticDownload).suggestedFilename(),"tensorflow_cached_cos_probe.py");
    const arrowDownload=page.waitForEvent("download");
    await diagnostics.getByRole("link",{name:"Arrow/Qiskit 导入对照代码",exact:true}).click();
    assert.equal((await arrowDownload).suggestedFilename(),"arrow_qiskit_import_probe.py");
    const arrowDiagnostic=diagnostics.locator("details").filter({has:page.locator("summary",{hasText:"arrow_coexistence_dependency_review"})});
    if(await arrowDiagnostic.getAttribute("open")===null) await arrowDiagnostic.locator("summary").click();
    assert.ok((await arrowDiagnostic.innerText()).includes("EXPERIMENTALLY_VERIFIED_NOT_PROMOTED"));
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
    await page.screenshot({path:`${output}/arrow-dependency-review-${viewport.width}.png`,fullPage:false});
    await diagnostics.locator("details").first().locator("summary").click();
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
    for(const observation of snapshot.diagnostic_observations.filter(row=>row.kind==="tf_atomic_account_candidate_review")){
      const detail=page.locator(`#diag-${observation.id}`);
      await detail.locator("summary").click();
      assert.ok((await detail.innerText()).includes(observation.evidence_hash));
      assert.ok((await detail.innerText()).includes("REJECTED_ATOMIC_ACCOUNT_CANDIDATE_NOT_A_REPAIR"));
      assert.ok((await detail.innerText()).includes("test_private_point_order_limit_is_a_real_refusal[2]"));
      assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
      await detail.locator("summary").scrollIntoViewIfNeeded();
      await page.screenshot({path:`${output}/atomic-candidate-${observation.profile}-${viewport.width}.png`,fullPage:false});
      await detail.locator("summary").click();
    }
    const migrationSection=page.locator("section.band").filter({has:page.getByRole("heading",{name:"经 owner 明确批准的合同迁移",exact:true})});
    assert.equal(await migrationSection.locator("details").count(),expectedMigrations.size);
    for(const summary of await migrationSection.locator("details summary").all()) await summary.click();
    assert.equal(await migrationSection.locator("li").count(),[...expectedMigrations.values()].reduce((sum,row)=>sum+row.case_ids.length,0));
    assert.ok((await migrationSection.innerText()).includes("test_managed_mps_queries_same_parent_cache_tiny_hessian_cap"));
    assert.ok((await migrationSection.innerText()).includes("不计入"));
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
    await page.screenshot({path:`${output}/approved-migrations-${viewport.width}.png`,fullPage:false});
    await page.locator("#view details summary").first().click();
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
    const failureBacklog=page.locator("section.band").filter({has:page.getByRole("heading",{name:/^逐项严格失败台账/})});
    const currentFailureIds=[...new Set(Object.values(core.failures).flat())];
    assert.ok(currentFailureIds.length>0);
    for(const id of currentFailureIds){
      const summary=failureBacklog.locator("summary").filter({has:page.getByText(id,{exact:true})});
      assert.equal(await summary.count(),1);
      assert.ok((await summary.innerText()).includes("当前批次失败"));
    }
    const failureSummary=failureBacklog.locator("summary").filter({has:page.getByText(currentFailureIds[0],{exact:true})});
    await failureSummary.click();
    const diagnosedFailure=page.locator("#view details").filter({has:page.locator("h3",{hasText:/诊断记录|历史诊断（未按当前源码复核）/})}).first();
    if(await diagnosedFailure.getAttribute("open")===null) await diagnosedFailure.locator("summary").first().click();
    await page.getByRole("heading",{name:/诊断记录|历史诊断（未按当前源码复核）/}).first().waitFor();
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
    await page.getByRole("button",{name:"六个月验收计划",exact:true}).click();
    assert.equal(await page.locator(".timeline li").count(),6);
    assert.ok((await page.getByRole("link",{name:/完整验证快照/}).getAttribute("href")).endsWith("manifest.json.gz"));
    const snapshotDownload=page.waitForEvent("download");
    await page.getByRole("link",{name:/完整验证快照/}).click();
    const downloadedSnapshot=await snapshotDownload;
    assert.equal(downloadedSnapshot.suggestedFilename(),"manifest.json.gz");
    const downloadedBytes=await readFile(await downloadedSnapshot.path());
    assert.equal(createHash("sha256").update(gunzipSync(downloadedBytes)).digest("hex"),snapshotSha);
    assert.ok((await page.getByRole("link",{name:/完整导出与继承清单/}).getAttribute("href")).endsWith("runtime.json.gz"));
    const runtimeSection=page.locator("section.band").filter({has:page.getByRole("heading",{name:"公共导出与继承清点",exact:true})});
    assert.equal(await runtimeSection.locator("details").count(),2);
    for(const summary of await runtimeSection.locator("details > summary").all()) await summary.click();
    assert.ok((await runtimeSection.innerText()).includes("按 SDK 隔离采集"));
    assert.ok((await runtimeSection.innerText()).includes("pennylane.qchem"));
    assert.ok((await runtimeSection.innerText()).includes("qiskit.transpiler.passes"));
    assert.equal(await runtimeSection.locator(".traversal-summary li").count(),4);
    assert.ok((await runtimeSection.innerText()).includes("模块已尝试"));
    assert.ok((await runtimeSection.innerText()).includes("导入未完成，仍在范围内"));
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
    const namespaceSection=page.locator("section.band").filter({has:page.getByRole("heading",{name:"递归命名空间候选",exact:true})});
    assert.equal(await namespaceSection.locator("details").count(),2);
    await namespaceSection.locator("details").first().locator("summary").click();
    assert.ok(await namespaceSection.locator("details").first().locator("tbody tr td:last-child").first().isVisible());
    assert.ok((await namespaceSection.innerText()).includes("qiskit_finance"));
    const namespaceDownload=page.waitForEvent("download");
    await namespaceSection.getByRole("link",{name:/完整命名空间清单/}).first().click();
    assert.ok((await namespaceDownload).suggestedFilename().startsWith("namespaces-"));
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
    await page.screenshot({path:`${output}/namespace-census-${viewport.width}.png`,fullPage:false});
    const downloadPromise=page.waitForEvent("download");
    await page.getByRole("link",{name:"六个月 /goal 提示词",exact:true}).click();
    assert.equal((await downloadPromise).suggestedFilename(),"quantumbridge-six-month-goal.txt");
    await page.getByRole("button",{name:"Switch to English",exact:true}).click();
    await page.getByRole("heading",{name:"Engineering progress",exact:true}).waitFor();
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
    await page.getByRole("link",{name:"Home",exact:true}).click();
    await page.getByRole("heading",{name:"QuantumBridge 应用框架",exact:true}).waitFor();
    await page.goto(`${base}/ecosystem.html`);
    await page.getByRole("link",{name:"工程进展",exact:true}).click();
    await page.getByRole("heading",{name:"工程进展",exact:true}).waitFor();
    await page.getByRole("button",{name:"4 类 / 19 方向",exact:true}).click();
    assert.equal(await page.locator(".direction-rows article").count(),19);
    await page.locator(".case-links a").first().click();
    await page.getByRole("link",{name:/返回.*首页/}).first().waitFor();
    await page.getByRole("link",{name:/返回.*首页/}).first().click();
    await page.getByRole("heading",{name:"QuantumBridge 应用框架",exact:true}).waitFor();
    assert.deepEqual(errors,[]);
    results.push({viewport,homePageHome:true,ecosystemEntrance:true,functionDetail:true,runtimeInheritanceDetail:true,casePageHome:true,consoleErrors:errors,timings});
    await writeFile(`${output}/network-${viewport.width}.json`,JSON.stringify(network,null,2)+"\n");
    await page.close();
  }
  console.log(JSON.stringify({results,screenshots:output},null,2));
}catch(error){
  if(activePage&&!activePage.isClosed()){
    await activePage.screenshot({path:`${output}/failure-${activeViewport.width}.png`,fullPage:false}).catch(()=>{});
    const body=await activePage.locator("body").innerText({timeout:5000}).catch(()=>"Unavailable");
    await writeFile(`${output}/failure.json`,JSON.stringify({error:error.message,viewport:activeViewport,url:activePage.url(),body,network:activeNetwork,timings:activeTimings},null,2)+"\n");
  }
  throw error;
}finally{await browser?.close();if(server) await new Promise(resolve=>server.close(resolve));}
