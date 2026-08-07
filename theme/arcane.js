/*
 * Live English -> Arcane translator for src/languages/arcane.md.
 *
 * Arcane is a 1:1 substitution alphabet, so "translation" is really just a
 * font swap — the markup keeps the original Latin text and lets the typeface
 * do the work. That means the output stays selectable, searchable and
 * screen-reader friendly, and copying it out yields readable English.
 *
 * Only A-Y are attested. Z has no published glyph and renders as a hollow box,
 * so the widget warns when the input contains one.
 */
(function () {
    "use strict";

    var MOUNT = "[data-arcane-translator]";
    var FONT = '"Arcane of Rathe"';
    var DEFAULT_TEXT = "Fear not the lightning, fear the darkness that follows";
    var UNWRITABLE = /z/i;

    /*
     * Everything the face can actually draw: letters and space, nothing else.
     *
     * No published Arcane text contains a punctuation mark or a numeral — not
     * the Runechant token, the Arcane Rising box, nor the Barthimont book — so
     * a comma or a digit would have to be invented rather than traced, which is
     * the same objection that rules out inventing a glyph for Z.
     *
     * Unsupported characters are dropped and reported rather than left to the
     * browser's Latin fallback, which would render Georgia next to brush-drawn
     * Arcane. A mixture like that reads as broken however good either half is.
     */
    var SUPPORTED = /[A-Za-z \n]/;

    function el(tag, cls, text) {
        var n = document.createElement(tag);
        if (cls) n.className = cls;
        if (text != null) n.textContent = text;
        return n;
    }

    function build(mount) {
        var head = el("div", "arcane-tool-head");
        head.appendChild(el("span", "arcane-tool-title", "Write in Arcane"));
        head.appendChild(el("span", "arcane-tool-note",
            "A 1:1 alphabet — type English, read Arcane."));

        var input = el("textarea", "arcane-input");
        input.rows = 1;
        input.value = DEFAULT_TEXT;
        input.setAttribute("aria-label", "English text to render in Arcane");
        input.setAttribute("spellcheck", "false");

        var plate = el("div", "arcane-plate");
        var out = el("div", "arcane-output");
        // The glyphs carry no semantic meaning of their own; the Latin caption
        // below is the accessible copy, so keep the plate out of the a11y tree.
        out.setAttribute("aria-hidden", "true");
        var latin = el("span", "arcane-latin");
        plate.appendChild(out);
        plate.appendChild(latin);

        var foot = el("div", "arcane-tool-foot");
        var warn = el("span", "arcane-warn");
        var save = el("button", "arcane-save", "Download PNG");
        save.type = "button";
        foot.appendChild(warn);
        foot.appendChild(save);

        mount.className = "arcane-tool";
        mount.appendChild(head);
        mount.appendChild(input);
        mount.appendChild(plate);
        mount.appendChild(foot);

        return { input: input, out: out, latin: latin, warn: warn, save: save };
    }

    /* Grow the box to fit its content so Enter never hides a line. */
    function autosize(input) {
        input.style.height = "auto";
        input.style.height = input.scrollHeight + "px";
    }

    function writable(text) {
        var kept = "", dropped = [];
        for (var i = 0; i < text.length; i++) {
            var ch = text[i];
            if (SUPPORTED.test(ch)) kept += ch;
            else if (dropped.indexOf(ch) === -1) dropped.push(ch);
        }
        // Removing a character leaves the spaces that surrounded it, which shows
        // up as a hole in the line. Collapse runs per line so newlines survive.
        kept = kept.split("\n").map(function (line) {
            return line.replace(/ {2,}/g, " ");
        }).join("\n");
        return { text: kept, dropped: dropped };
    }

    function render(ui) {
        autosize(ui.input);
        var w = writable(ui.input.value);
        ui.out.textContent = w.text;
        ui.latin.textContent = w.text.replace(/\s+/g, " ").trim();

        var notes = [];
        if (UNWRITABLE.test(w.text)) {
            notes.push("No glyph for Z has ever been published — it shows as an empty rune.");
        }
        // Grouped rather than listed: punctuation and digits are dropped
        // constantly, and naming every character is noise. Say why, and what
        // to do about it.
        var digits = w.dropped.filter(function (c) { return c >= "0" && c <= "9"; });
        var marks = w.dropped.filter(function (c) { return c < "0" || c > "9"; });
        if (marks.length) {
            notes.push("Arcane has no punctuation — no card art shows a single mark.");
        }
        if (digits.length) {
            notes.push("It has no numerals either — spell numbers out.");
        }
        ui.warn.dataset.active = notes.length ? "true" : "false";
        ui.warn.textContent = notes.join(" ");
    }

    /*
     * Export at a fixed 3x scale so the PNG is usable for social posts without
     * asking the reader to think about pixel dimensions.
     */
    function download(ui) {
        var lines = writable(ui.input.value).text.split("\n");
        var scale = 3;
        var size = 64 * scale;
        var padX = 56 * scale;
        var padY = 44 * scale;
        var lead = size * 1.6;

        var canvas = document.createElement("canvas");
        var ctx = canvas.getContext("2d");
        ctx.font = size + "px " + FONT + ", serif";

        var widest = 0;
        lines.forEach(function (line) {
            widest = Math.max(widest, ctx.measureText(line).width);
        });

        canvas.width = Math.ceil(widest + padX * 2);
        canvas.height = Math.ceil(lead * lines.length + padY * 2);

        ctx = canvas.getContext("2d");
        var bg = ctx.createRadialGradient(
            canvas.width / 2, canvas.height * 0.4, 0,
            canvas.width / 2, canvas.height * 0.4, canvas.width * 0.75);
        bg.addColorStop(0, "#16151f");
        bg.addColorStop(1, "#08080c");
        ctx.fillStyle = bg;
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        var ink = ctx.createLinearGradient(0, 0, canvas.width, 0);
        ink.addColorStop(0, "#8d93a8");
        ink.addColorStop(0.42, "#d8dce8");
        ink.addColorStop(0.5, "#ffffff");
        ink.addColorStop(0.58, "#d8dce8");
        ink.addColorStop(1, "#8d93a8");

        ctx.font = size + "px " + FONT + ", serif";
        ctx.fillStyle = ink;
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        lines.forEach(function (line, i) {
            ctx.fillText(line, canvas.width / 2, padY + lead * (i + 0.5));
        });

        canvas.toBlob(function (blob) {
            if (!blob) return;
            var url = URL.createObjectURL(blob);
            var a = document.createElement("a");
            a.href = url;
            a.download = "arcane.png";
            document.body.appendChild(a);
            a.click();
            a.remove();
            URL.revokeObjectURL(url);
        });
    }

    function init() {
        var mount = document.querySelector(MOUNT);
        if (!mount || mount.dataset.ready === "true") return;
        mount.dataset.ready = "true";

        var ui = build(mount);
        render(ui);
        ui.input.addEventListener("input", function () { render(ui); });

        // Canvas fillText silently falls back unless the face is already loaded.
        ui.save.addEventListener("click", function () {
            if (document.fonts && document.fonts.load) {
                document.fonts.load('64px ' + FONT).then(function () { download(ui); });
            } else {
                download(ui);
            }
        });
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();
