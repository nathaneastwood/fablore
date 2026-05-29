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

function renderHintContent(entry) {
  if (typeof entry === "string") return entry;
  const parts = [];
  if (entry.type) {
    const meta = [entry.type];
    if (entry.region) meta.push(entry.region);
    if (entry.species) meta.push(entry.species);
    if (entry.status && entry.status !== "Unknown") meta.push(entry.status);
    parts.push(`<div class="hint-card-badge">${meta.join(" · ")}</div>`);
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
      placement: "bottom",
      maxWidth: 300,
  });
}

if (document.getElementsByClassName("hint").length > 0) {
  runHints()
}
