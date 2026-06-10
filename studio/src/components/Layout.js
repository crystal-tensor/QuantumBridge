export function Layout({ sidebar, header, body }) {
  return `
    <div class="studio-shell">
      ${sidebar}
      <main class="studio-main">
        ${header}
        ${body}
      </main>
    </div>
  `;
}
