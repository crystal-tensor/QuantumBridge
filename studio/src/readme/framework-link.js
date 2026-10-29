// Copyright 2026 QuantumBridge Contributors. Apache-2.0.
// Keep the documentation entry independent of the application framework's rendering.
const root = document.querySelector('#framework-app');
function connectDocumentation() {
  const english = document.documentElement.lang === 'en';
  const actions = root.querySelector('.top-actions');
  if (!actions) return;
  if (!actions.querySelector('[data-documentation]')) {
  const link = document.createElement('a');
  link.dataset.documentation = '';
  link.href = `./readme.html?lang=${english ? 'en' : 'zh'}`;
  link.textContent = english ? 'Documentation ↗' : '使用文档 ↗';
  link.style.cssText = 'font-size:12px;font-weight:600;color:#236a57;white-space:nowrap;padding:7px 10px;border:1px solid #ccded5;border-radius:5px;text-decoration:none';
  actions.prepend(link);
  }
  // The framework app adds its language query after href construction. Move it
  // before a fragment so guide routes remain valid in both languages.
  for (const anchor of root.querySelectorAll('a[href*="readme.html#"]')) {
    const url = new URL(anchor.href);
    const [fragment] = url.hash.slice(1).split('?');
    url.hash = fragment;
    url.searchParams.set('lang', english ? 'en' : 'zh');
    anchor.href = url.href;
  }
}
new MutationObserver(connectDocumentation).observe(root, {childList:true, subtree:true});
connectDocumentation();
