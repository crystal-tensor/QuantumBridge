// Copyright 2026 QuantumBridge Contributors. Apache-2.0.
import assert from 'node:assert/strict';
import { test } from 'node:test';
import { readFile, mkdtemp, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { pages, chapters, directionPages, domainPages, version } from '../src/readme/content.js';
import { documentationResources, domainResources, directionResources, resources, resourceHref } from '../src/framework/resources.js';
import { domains, directions } from '../src/framework/data.js';
import { buildPublic } from './build-public.mjs';

test('documentation preserves the 4-domain / 19-direction taxonomy and home registration', () => {
  assert.equal(pages.length, 35);
  assert.equal(chapters.length, 12);
  assert.equal(domainPages.length, 4);
  assert.equal(directionPages.length, 19);
  assert.equal(new Set(pages.map(p => p.id)).size, pages.length);
  assert.equal(documentationResources.length, 23);
  assert.equal(resources.length, 26, 'notebook registry must remain unchanged');
  for (const domain of domains) {
    assert.ok(domainResources(domain.id).some(r => r.kind === 'guide' && r.href === `/readme.html#${domain.id}`));
  }
  for (const direction of directions) {
    const page = directionPages.find(p => p.id === direction.id);
    assert.equal(page.domain, direction.domain);
    const links = directionResources(direction.id);
    assert.ok(links.some(r => r.kind === 'guide' && r.href === `/readme.html#${direction.id}`));
    assert.equal(links.filter(r => r.kind === 'case').length, 1);
    assert.equal(page.blocks.find(b => b.type === 'case-resource').resource, links.find(r => r.kind === 'case'));
  }
});

test('all chapters are bilingual and their internal references resolve', async () => {
  const project = await readFile(new URL('../../pyproject.toml', import.meta.url), 'utf8');
  assert.ok(project.includes(`version = "${version}"`));
  for (const page of pages) {
    assert.ok(page.title['zh-CN'] && page.title.en);
    assert.ok(page.summary['zh-CN'] && page.summary.en);
    const anchors = page.blocks.filter(b => b.type === 'h2').map(b => b.id);
    assert.equal(new Set(anchors).size, anchors.length);
    for (const block of page.blocks) {
      if (block.text && typeof block.text === 'object') assert.ok(block.text['zh-CN'] && block.text.en);
      for (const text of Object.values(block.text && typeof block.text === 'object' ? block.text : {})) {
        for (const match of text.matchAll(/\]\(#([^)]*)\)/g)) {
          const [id, section] = match[1].split('/');
          const target = pages.find(p => p.id === id);
          assert.ok(target, `${page.id}: missing route ${id}`);
          if (section) assert.ok(target.blocks.some(b => b.id === section));
        }
      }
    }
  }
});

test('public export includes runnable documentation and downloads at the project base path', async () => {
  const directory = await mkdtemp(path.join(tmpdir(), 'qb-readme-export-'));
  try {
    await buildPublic(directory, '/QuantumBridge/');
    for (const file of ['readme.html', 'src/readme/app.js', 'src/readme/content.js', 'src/readme/bloch.js', 'src/readme/readme.css', 'src/readme/framework-link.js', 'downloads/quickstart.py']) {
      assert.ok((await readFile(path.join(directory, file))).length > 0);
    }
    const html = await readFile(path.join(directory, 'framework.html'), 'utf8');
    assert.ok(html.includes('src/readme/framework-link.js'));
    for (const guide of documentationResources) assert.ok(resourceHref(guide).startsWith('/readme.html#'));
    const notebook = resources.find(r => r.kind === 'case');
    assert.deepEqual(await readFile(path.join(directory, 'examples', notebook.domain, notebook.file.replace('.html', '.ipynb'))),
      await readFile(new URL(`../../output/jupyter-notebook/${notebook.domain}/${notebook.file.replace('.html', '.ipynb')}`, import.meta.url)));
  } finally { await rm(directory, {recursive: true, force: true}); }
});
