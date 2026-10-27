# Quantum Bridge ecosystem guide / 生态学习中心

A bilingual, static learning page based on the 33-slide ecosystem architecture deck v2.4. It preserves the ten primary packages and the QuantumOS-inspired hardware → compiler/HAL → QOS → QB → applications structure.

基于 33 页生态架构 PPT v2.4 的中英文学习页面。它保留十个主分包，展示从硬件、编译器/HAL、QOS、QB 到应用的整体关系。所有目标能力均作为架构规划展示，不代表当前实现状态。

## Run / 运行

```sh
npm --prefix studio run dev
```

Open <http://127.0.0.1:8765/ecosystem.html>. No install or backend service is needed. `PORT=8766 npm --prefix studio run dev` changes the port.

无需安装依赖或启动后端。Studio 侧栏也有“生态学习中心”入口。

## Contents / 内容

- Five-layer interactive architecture, with responsibilities and interface boundaries.
- All ten packages, detailed capability dialogs and related modules.
- Four example workflows and QuantumOS MLFQ, QOS-DP and QEC explanations.
- Existing Router, Studio, plugins, experiments, mitigation, contracts and tools.
- Three learning paths, a terminology reference and phased delivery criteria.
- Downloadable editable PPT and a link to the original QuantumOS architecture.

中文/EN 切换覆盖正文、交互内容、对话框和无障碍标签。语言保存在 `quantumbridge.locale`，URL 的 `?lang=en` / `?lang=zh` 可覆盖默认值。两种语言共用选中的架构层、示例与学习路线。

## Edit / 编辑

- `src/ecosystem/content.js`: bilingual learning content and package metadata.
- `src/ecosystem/main.js`: page composition, native dialogs and interaction.
- `src/ecosystem/ecosystem.css`: responsive styling and reduced-motion support.
- `assets/quantumbridge-ecosystem.pptx`: source architecture deck.

All assets are local. External source links load only when selected. This page works independently of the Studio data-loading path.

## Validation / 验证

```sh
npm --prefix studio test
node --check studio/src/ecosystem/main.js
node --check studio/src/ecosystem/content.js
```

Browser verification should cover both languages, all layer selectors, all ten package dialogs, related-module links, four example tabs, three learning paths, keyboard navigation, locale persistence, the PPT download and mobile layout. Use `npm --prefix studio run dev` for the browser URL.
