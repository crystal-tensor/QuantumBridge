export function Card(content, extraClass = "") {
  return `<article class="card ${extraClass}">${content}</article>`;
}
