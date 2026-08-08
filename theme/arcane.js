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
    var ALPHABET_MOUNT = "[data-arcane-alphabet]";
    var LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
    var INPUT_ID = "arcane-translator-input";
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

    /*
     * The alphabet chart, drawn in the typeface rather than shipped as an
     * image. Being live text it follows the reader's theme, stays sharp at any
     * zoom, and cannot fall out of step with the face the translator uses —
     * the chart and the widget below it are now the same glyphs by
     * construction. Z is left to render as the hollow rune the font draws for
     * it; that gap is the point, and the prose on the page explains it.
     *
     * Nothing writes to this after build: it is a reference, not an output.
     */
    function buildAlphabet(mount) {
        mount.className = "arcane-alphabet";
        for (var i = 0; i < LETTERS.length; i++) {
            var cell = el("div", "arcane-letter");
            var glyph = el("span", "arcane-letter-glyph", LETTERS[i]);
            // Glyph and label are the same character in two faces, so let the
            // Latin one speak and keep the pair from being read out twice.
            glyph.setAttribute("aria-hidden", "true");
            cell.appendChild(glyph);
            cell.appendChild(el("span", "arcane-letter-name", LETTERS[i]));
            mount.appendChild(cell);
        }
    }

    function build(mount) {
        var head = el("div", "arcane-tool-head");
        head.appendChild(el("span", "arcane-tool-title", "Write in Arcane"));
        head.appendChild(el("span", "arcane-tool-note",
            "A 1:1 alphabet — type English, read Arcane."));

        var input = el("textarea", "arcane-input");
        input.id = INPUT_ID;
        input.rows = 1;
        input.value = DEFAULT_TEXT;
        input.setAttribute("spellcheck", "false");
        input.placeholder = "Type anything…";

        // A bare textarea carrying a sample sentence reads as body copy, not as
        // a control. The visible label plus the boxed field in arcane.css are
        // what tell a reader this line is theirs to change.
        var label = el("label", "arcane-input-label", "Type your text here");
        label.setAttribute("for", INPUT_ID);

        /*
         * A textarea only shows a caret once it is focused, which is too late —
         * the caret is what tells the reader the box is a box. So an unfocused
         * field gets a fake one: a mirror layered over the textarea holding the
         * same text in transparent ink, with a blinking bar after it. Matching
         * the textarea's metrics (arcane.css keeps the two rules together) makes
         * the mirror wrap identically, so the bar lands where the real caret
         * would. It hides on focus and the browser's own caret takes over.
         */
        var mirror = el("div", "arcane-mirror");
        mirror.setAttribute("aria-hidden", "true");
        var mirrorText = el("span", "arcane-mirror-text");
        mirror.appendChild(mirrorText);
        mirror.appendChild(el("span", "arcane-caret"));

        var field = el("div", "arcane-field");
        // "Armed" is the cold-start state: caret showing, keystrokes captured.
        // It is given up for good the first time the reader leaves the field.
        field.dataset.armed = "true";
        field.appendChild(mirror);
        field.appendChild(input);

        var row = el("div", "arcane-input-row");
        row.appendChild(label);
        row.appendChild(field);

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
        mount.appendChild(row);
        mount.appendChild(plate);
        mount.appendChild(foot);

        return {
            input: input, field: field, mirrorText: mirrorText,
            plate: plate, out: out, latin: latin, warn: warn, save: save
        };
    }

    /* Something else already owns the keyboard — a search box, another field. */
    function isEditable(node) {
        if (!node) return false;
        var tag = node.tagName;
        return tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT" ||
            node.isContentEditable === true;
    }

    function onScreen(node) {
        var r = node.getBoundingClientRect();
        return r.bottom > 0 && r.top < (window.innerHeight ||
            document.documentElement.clientHeight);
    }

    /* Grow the box to fit its content so Enter never hides a line. */
    function autosize(input) {
        input.style.height = "auto";
        // scrollHeight is the content box; the field is border-box and bordered,
        // so without adding the borders back the last line is clipped.
        var borders = input.offsetHeight - input.clientHeight;
        input.style.height = input.scrollHeight + borders + "px";
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
        // The mirror tracks the raw value, not the filtered one: it sits over
        // the box the reader is typing into, so it has to wrap exactly as the
        // textarea does. Filtering happens on the way to the plate only.
        ui.mirrorText.textContent = ui.input.value;
        ui.field.dataset.empty = ui.input.value.length ? "false" : "true";

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
        // Independent of the translator: a page may want the chart alone.
        var chart = document.querySelector(ALPHABET_MOUNT);
        if (chart && chart.dataset.ready !== "true") {
            chart.dataset.ready = "true";
            buildAlphabet(chart);
        }

        var mount = document.querySelector(MOUNT);
        if (!mount || mount.dataset.ready === "true") return;
        mount.dataset.ready = "true";

        var ui = build(mount);
        render(ui);
        ui.input.addEventListener("input", function () { render(ui); });

        /*
         * The field ships with a sample sentence so the plate is never blank,
         * but that sentence is in the reader's way. Selecting it on first focus
         * makes the first keystroke replace it — the box behaves like a
         * placeholder without giving up the demo.
         */
        var pristine = true;
        ui.input.addEventListener("focus", function () {
            if (pristine && ui.input.value === DEFAULT_TEXT) ui.input.select();
            pristine = false;
            /*
             * Type-to-start is a cold-start affordance, spent on first use. The
             * reader has now been in the box, so from here on the field behaves
             * like any other: click in to type, click away and it stops
             * listening. Disarming on focus rather than on the blur that
             * follows is the same thing observed from outside — while the field
             * has focus the real caret is showing and keystrokes go there
             * natively — and it means the widget cannot be left armed by a blur
             * that never fires.
             */
            ui.field.dataset.armed = "false";
        });

        /*
         * A caret blinking in a field that does not have focus is a lie: it says
         * "type and it lands here" when nothing would happen. Rather than drop
         * the caret — it is the affordance that makes the widget look usable —
         * make the promise true, but only while the caret is actually showing.
         * A letter pressed on an armed, on-screen field that nothing else has
         * claimed starts typing into it.
         *
         * Letters only, for two reasons. Anything else is dropped by the
         * typeface anyway, so claiming it would insert nothing and consume the
         * keystroke; and it leaves mdBook's '/' search shortcut, digits and
         * punctuation doing what the reader expects. Space is excluded on the
         * same principle — no sentence opens with one, and swallowing it would
         * break space-to-scroll for a reader passing the widget.
         *
         * Capture phase, because mdBook's searcher binds 's' on document during
         * bubble: without claiming the event first, 's' would both type here and
         * throw the reader up to the search box. stopPropagation only fires when
         * the keystroke is actually taken, so every other key is untouched.
         */
        document.addEventListener("keydown", function (e) {
            if (e.ctrlKey || e.metaKey || e.altKey) return;
            if (!/^[A-Za-z]$/.test(e.key)) return;
            if (ui.field.dataset.armed !== "true") return;
            if (document.activeElement === ui.input) return;
            if (isEditable(document.activeElement)) return;
            if (!onScreen(ui.field)) return;

            e.preventDefault();
            e.stopPropagation();
            // Same rule as the select-on-focus above: while the box still holds
            // the untouched sample, the first letter typed replaces it.
            if (ui.input.value === DEFAULT_TEXT) ui.input.value = "";
            // Inserted by hand rather than left to fall through after focus(),
            // which browsers disagree about.
            ui.input.value += e.key;
            ui.input.focus();
            var end = ui.input.value.length;
            ui.input.setSelectionRange(end, end);
            render(ui);
        }, true);

        // Clicking the render is a natural "let me change this" gesture. Ignore
        // it mid-selection, so copying the Latin caption still works.
        ui.plate.addEventListener("click", function () {
            var sel = window.getSelection();
            if (sel && String(sel)) return;
            ui.input.focus();
        });

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
