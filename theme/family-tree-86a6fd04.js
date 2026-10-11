// Renders the ```mermaid fenced blocks create_character_kin_md.py writes into
// src/data/md/character-kin.md. mdBook/pulldown-cmark has no native Mermaid
// support, so this converts each `<pre><code class="language-mermaid">` into
// rendered SVG — twice per diagram (see family-tree.css), since Mermaid bakes
// colours into the SVG at render time and can't follow a live theme switch.
(function () {
    var blocks = document.querySelectorAll("pre > code.language-mermaid");
    if (!blocks.length) {
        return;
    }

    var script = document.createElement("script");
    script.src = "https://cdn.jsdelivr.net/npm/mermaid@11.4.1/dist/mermaid.min.js";
    script.onload = function () {
        renderAll(Array.prototype.slice.call(blocks));
    };
    document.head.appendChild(script);

    function renderAll(codeBlocks) {
        codeBlocks.reduce(function (chain, code, i) {
            return chain.then(function () {
                return renderOne(code, i);
            });
        }, Promise.resolve());
    }

    function renderOne(code, i) {
        var source = code.textContent;
        var pre = code.parentElement;

        var wrap = document.createElement("div");
        wrap.className = "kin-mermaid";
        var light = document.createElement("div");
        light.className = "kin-mermaid-light";
        var dark = document.createElement("div");
        dark.className = "kin-mermaid-dark";
        wrap.appendChild(light);
        wrap.appendChild(dark);
        pre.replaceWith(wrap);

        window.mermaid.initialize({ startOnLoad: false, theme: "default" });
        return window.mermaid
            .render("kin-tree-" + i + "-light", source)
            .then(function (result) {
                light.innerHTML = result.svg;
                window.mermaid.initialize({ startOnLoad: false, theme: "dark" });
                return window.mermaid.render("kin-tree-" + i + "-dark", source);
            })
            .then(function (result) {
                dark.innerHTML = result.svg;
            })
            .catch(function (err) {
                wrap.replaceWith(pre); // leave the raw block visible rather than an empty page
                console.error("family-tree.js: failed to render diagram", err);
            });
    }
})();
