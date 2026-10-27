# Local Page Navigation

- The owner-facing home page is `http://127.0.0.1:8765/framework.html`.
- Every new case, notebook, diagnostic report or other local page must be linked
  from its corresponding domain/direction on that home page. Never deliver only
  a `file://` URL or a separate temporary server port.
- Register local notebook HTML pages in `src/framework/resources.js`; keep their
  files under `../output/jupyter-notebook/<domain>/`. The local server exposes
  registered HTML and paired notebooks at `/examples/<domain>/<file>` and adds
  return navigation without changing scientific outputs or receipts.
- Keep Chinese and English navigation labels, existing status/accuracy caveats,
  and links to downloadable notebooks. Do not imply verified parity from pages.
- Run `node scripts/framework-check.mjs` and
  `node --test scripts/artifact-pages.test.mjs` after navigation/server edits.
- Verify desktop/mobile layouts and the actual home-to-report-to-home journey.
