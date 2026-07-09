async function getHints() {
  const url = "/hints.json";
  try {
      const response = await fetch(url);
      if (!response.ok) {
          throw new Error(`Response status: ${response.status}`);
      }
      return await response.json();
  } catch (error) {
      console.error(error.message);
  }
}

function buildBadgeText(entry) {
  const parts = [entry.type];
  if (entry.region) parts.push(entry.region);
  if (entry.species) parts.push(entry.species);
  if (entry.status && entry.status !== "Unknown") parts.push(entry.status);
  return parts.join(" · ");
}

function renderHintContent(entry) {
  if (typeof entry === "string") return entry;

  const parts = [];

  if (entry.type) {
    const badge = `<span class="hint-card-badge">${buildBadgeText(entry)}</span>`;
    const link = entry.url
      ? `<a class="hint-card-link" href="${entry.url}" title="Read more" aria-label="Read more">` +
        `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" aria-hidden="true">` +
        `<path d="M320 0c-17.7 0-32 14.3-32 32s14.3 32 32 32l82.7 0L201.4 265.4c-12.5 12.5-12.5 32.8 0 45.3s32.8 12.5 45.3 0L448 109.3l0 82.7c0 17.7 14.3 32 32 32s32-14.3 32-32l0-160c0-17.7-14.3-32-32-32L320 0zM80 32C35.8 32 0 67.8 0 112L0 432c0 44.2 35.8 80 80 80l320 0c44.2 0 80-35.8 80-80l0-112c0-17.7-14.3-32-32-32s-32 14.3-32 32l0 112c0 8.8-7.2 16-16 16L80 448c-8.8 0-16-7.2-16-16l0-320c0-8.8 7.2-16 16-16l112 0c17.7 0 32-14.3 32-32s-14.3-32-32-32L80 32z"/>` +
        `</svg></a>`
      : "";
    parts.push(`<div class="hint-card-header">${badge}${link}</div>`);
  }

  if (entry.summary) {
    parts.push(`<div class="hint-card-summary">${entry.summary}</div>`);
  }

  return `<div class="hint-card">${parts.join("")}</div>`;
}

async function runHints() {
  const hints = await getHints();
  tippy('*[hint]', {
      content(reference) {
          const entry = hints[reference.getAttribute("hint")];
          return entry ? renderHintContent(entry) : "";
      },
      allowHTML: true,
      interactive: true,
      placement: "bottom",
      maxWidth: 320,
      offset: [0, 4],
      theme: "hint-card",
      onShow(instance) {
          const rects = instance.reference.getClientRects();
          const rect = rects.length ? rects[0] : instance.reference.getBoundingClientRect();
          instance.setProps({ getReferenceClientRect: () => rect });
      },
  });
}

if (document.getElementsByClassName("hint").length > 0) {
  runHints()
}
