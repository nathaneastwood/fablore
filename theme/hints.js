async function getHints() {
  const url = "/hints.json";
  try {
      const response = await fetch(url);

      if (!response.ok) {
          throw new Error(`Response status: ${response.status}`);
      }
      const json = await response.json();

      return json;
  } catch (error) {
      console.error(error.message);
  }
}

async function runHints() {
  let hints = await getHints();
  tippy('*[hint]', {
      content(reference) {
          return hints[reference.getAttribute("hint")];
      },
      allowHTML: true,
      placement: "bottom",
  });
}

if (document.getElementsByClassName("hint").length > 0) {
  runHints()
}
