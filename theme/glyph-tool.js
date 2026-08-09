/*
 * Live English -> Rathe script translators for the pages under src/languages/.
 *
 * Every script documented on this site maps one-to-one onto the English
 * alphabet, so "translation" is really a font swap — the markup keeps the
 * original Latin text and lets the traced typeface do the work. That means the
 * output stays selectable, searchable and screen-reader friendly, and copying
 * it out yields readable English.
 *
 * It also means one widget serves all four. A page opts in with
 *
 *     <div data-glyph-alphabet="imperial"></div>
 *     <div data-glyph-tool="imperial"></div>
 *
 * and everything that differs between the scripts — the face, the sample line,
 * which letters have never been published, the colours of the output plate,
 * whether the script is written in more than one direction — lives in SCRIPTS
 * below rather than in the DOM or the stylesheet.
 */
(function () {
    "use strict";

    var ALPHABET_MOUNT = "[data-glyph-alphabet]";
    var TOOL_MOUNT = "[data-glyph-tool]";
    var LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";

    /*
     * Everything a face can actually draw: letters and space, nothing else.
     *
     * No published text in any of these scripts contains a punctuation mark or
     * a numeral, so a comma or a digit would have to be invented rather than
     * traced — the same objection that rules out inventing the missing letters.
     *
     * Unsupported characters are dropped and reported rather than left to the
     * browser's Latin fallback, which would render Georgia next to brush-drawn
     * glyphs. A mixture like that reads as broken however good either half is.
     */
    var SUPPORTED = /[A-Za-z \n]/;

    /*
     * Plates are described as colour stops rather than as CSS, because the same
     * palette has to be handed both to the stylesheet and to a canvas for the
     * PNG export. Declaring it once here keeps the download looking like the
     * thing the reader pressed the button on.
     *
     * A plate keeps its colours in every mdBook theme, on purpose: each one is a
     * picture of the artefact the script was traced from — silver on a black
     * card back, ink on white paper, ink on parchment, gilt on dark stone.
     * Inverting them for the light theme would misrepresent them.
     */
    var SCRIPTS = {
        arcane: {
            font: '"Arcane of Rathe"',
            title: "Write in Arcane",
            note: "A 1:1 alphabet — type English, read Arcane.",
            sample: "Fear not the lightning, fear the darkness that follows",
            unwritable: "Z",
            plate: {
                bg: [["#16151f", 0], ["#08080c", 0.75]],
                ink: [["#8d93a8", 0], ["#d8dce8", 0.42], ["#ffffff", 0.5],
                      ["#d8dce8", 0.58], ["#8d93a8", 1]],
                latin: "#6c6f80"
            }
        },
        imperial: {
            font: '"Imperial of Rathe"',
            title: "Write in Imperial",
            note: "A 1:1 alphabet — type English, read Imperial.",
            sample: "Children of the dragon, kindle your fires",
            unwritable: "QX",
            /*
             * The only script here attested in more than one direction. The
             * Proclamation of Requisition reads right to left, and the banners
             * in Spectral Procession run top to bottom in columns, so the tool
             * offers all three rather than quietly picking one.
             */
            directions: [
                ["ltr", "Left to right"],
                ["rtl", "Right to left"],
                ["vertical", "Vertical"]
            ],
            plate: {
                bg: [["#f8f5ed", 0], ["#e3dccb", 0.75]],
                ink: [["#2b2b2b", 0], ["#141414", 0.5], ["#2b2b2b", 1]],
                latin: "#8a8272"
            }
        },
        seers: {
            font: '"Seers of Rathe"',
            title: "Write in the Seers' script",
            note: "A 1:1 alphabet — but only 17 of the 26 letters have ever been published.",
            sample: "This age of gods and monsters",
            unwritable: "BCJKQVWXZ",
            plate: {
                bg: [["#ece0c0", 0], ["#c9b184", 0.75]],
                ink: [["#4a3520", 0], ["#2f2013", 0.5], ["#4a3520", 1]],
                latin: "#7d6a48"
            }
        },
        solanian: {
            font: '"Solanian of Rathe"',
            title: "Write in Solanian",
            note: "A 1:1 alphabet — type English, read Solanian.",
            sample: "By the light I speak",
            unwritable: "JQXZ",
            plate: {
                bg: [["#1d1a15", 0], ["#0a0908", 0.75]],
                ink: [["#a97c34", 0], ["#f0d89a", 0.45], ["#fff6de", 0.52],
                      ["#e6c887", 0.6], ["#a97c34", 1]],
                latin: "#8a7550"
            }
        }
    };

    function el(tag, cls, text) {
        var n = document.createElement(tag);
        if (cls) n.className = cls;
        if (text != null) n.textContent = text;
        return n;
    }

    function cssGradient(kind, stops) {
        var parts = stops.map(function (s) {
            return s[0] + " " + Math.round(s[1] * 100) + "%";
        });
        if (kind === "bg") {
            return "radial-gradient(ellipse 80% 70% at 50% 40%, " + parts.join(", ") + ")";
        }
        return "linear-gradient(100deg, " + parts.join(", ") + ")";
    }

    /* Human list: "Q", "Q or X", "B, C or K". */
    function listOf(chars) {
        if (chars.length === 1) return chars[0];
        return chars.slice(0, -1).join(", ") + " or " + chars[chars.length - 1];
    }

    /*
     * The alphabet chart, drawn in the typeface rather than shipped as an
     * image. Being live text it follows the reader's theme, stays sharp at any
     * zoom, and cannot fall out of step with the face the translator uses — the
     * chart and the widget below it are the same glyphs by construction.
     *
     * Letters with no published glyph are left to render as the hollow rune the
     * font draws for them and are marked so the stylesheet can mute the cell.
     * Those gaps are the point, and the prose on each page explains them.
     *
     * Nothing writes to this after build: it is a reference, not an output.
     */
    function buildAlphabet(mount, script) {
        mount.className = "glyph-alphabet";
        mount.style.setProperty("--glyph-font", script.font);
        for (var i = 0; i < LETTERS.length; i++) {
            var ch = LETTERS[i];
            var cell = el("div", "glyph-letter");
            var glyph = el("span", "glyph-letter-glyph", ch);
            // Glyph and label are the same character in two faces, so let the
            // Latin one speak and keep the pair from being read out twice.
            glyph.setAttribute("aria-hidden", "true");
            cell.appendChild(glyph);
            cell.appendChild(el("span", "glyph-letter-name", ch));
            if (script.unwritable.indexOf(ch) !== -1) {
                cell.dataset.unwritable = "true";
                cell.title = "No glyph for " + ch + " has ever been published.";
            }
            mount.appendChild(cell);
        }
    }

    function build(mount, script, key) {
        var head = el("div", "glyph-tool-head");
        head.appendChild(el("span", "glyph-tool-title", script.title));
        head.appendChild(el("span", "glyph-tool-note", script.note));

        var input = el("textarea", "glyph-input");
        input.id = "glyph-translator-" + key;
        input.rows = 1;
        input.value = script.sample;
        input.setAttribute("spellcheck", "false");
        input.placeholder = "Type anything…";

        // A bare textarea carrying a sample sentence reads as body copy, not as
        // a control. The visible label plus the boxed field in glyph-tool.css
        // are what tell a reader this line is theirs to change.
        var label = el("label", "glyph-input-label", "Type your text here");
        label.setAttribute("for", input.id);

        /*
         * A textarea only shows a caret once it is focused, which is too late —
         * the caret is what tells the reader the box is a box. So an unfocused
         * field gets a fake one: a mirror layered over the textarea holding the
         * same text in transparent ink, with a blinking bar after it. Matching
         * the textarea's metrics (glyph-tool.css keeps the two rules together)
         * makes the mirror wrap identically, so the bar lands where the real
         * caret would. It hides on focus and the browser's own caret takes over.
         */
        var mirror = el("div", "glyph-mirror");
        mirror.setAttribute("aria-hidden", "true");
        var mirrorText = el("span", "glyph-mirror-text");
        mirror.appendChild(mirrorText);
        mirror.appendChild(el("span", "glyph-caret"));

        var field = el("div", "glyph-field");
        // "Armed" is the cold-start state: caret showing, keystrokes captured.
        // It is given up for good the first time the reader leaves the field.
        field.dataset.armed = "true";
        field.appendChild(mirror);
        field.appendChild(input);

        var row = el("div", "glyph-input-row");
        row.appendChild(label);
        row.appendChild(field);

        var dirs = null;
        if (script.directions) {
            dirs = el("div", "glyph-dirs");
            dirs.setAttribute("role", "group");
            dirs.setAttribute("aria-label", "Writing direction");
            script.directions.forEach(function (d, i) {
                var b = el("button", "glyph-dir", d[1]);
                b.type = "button";
                b.dataset.dir = d[0];
                b.setAttribute("aria-pressed", i === 0 ? "true" : "false");
                dirs.appendChild(b);
            });
            row.appendChild(dirs);
        }

        var plate = el("div", "glyph-plate");
        plate.style.background = cssGradient("bg", script.plate.bg);
        var out = el("div", "glyph-output");
        out.style.backgroundImage = cssGradient("ink", script.plate.ink);
        out.dataset.dir = script.directions ? script.directions[0][0] : "ltr";
        // The glyphs carry no semantic meaning of their own; the Latin caption
        // below is the accessible copy, so keep the plate out of the a11y tree.
        out.setAttribute("aria-hidden", "true");
        var latin = el("span", "glyph-latin");
        latin.style.color = script.plate.latin;
        plate.appendChild(out);
        plate.appendChild(latin);

        var foot = el("div", "glyph-tool-foot");
        var warn = el("span", "glyph-warn");
        var save = el("button", "glyph-save", "Download PNG");
        save.type = "button";
        foot.appendChild(warn);
        foot.appendChild(save);

        mount.className = "glyph-tool";
        mount.style.setProperty("--glyph-font", script.font);
        mount.appendChild(head);
        mount.appendChild(row);
        mount.appendChild(plate);
        mount.appendChild(foot);

        return {
            key: key, script: script, input: input, field: field,
            mirrorText: mirrorText, dirs: dirs, plate: plate, out: out,
            latin: latin, warn: warn, save: save, dir: out.dataset.dir
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

    /*
     * On the page, direction is left entirely to the stylesheet: bidi-override
     * for right to left, writing-mode for vertical. Reversing the string here
     * instead would look right on one line and be wrong the moment it wrapped,
     * because the browser would still fill lines from the top left — the start
     * of the sentence would end up at the end of the last line. Letting CSS
     * reverse it keeps wrapping, selection and copying intact.
     *
     * The canvas has no such machinery, and draws one typed line at a time with
     * no wrapping to get wrong, so the export reverses by hand.
     */
    function reversed(text) {
        return text.split("\n").map(function (line) {
            return line.split("").reverse().join("");
        }).join("\n");
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
        ui.out.dataset.dir = ui.dir;
        // The caption is the accessible copy of what the reader typed, so it
        // stays in reading order whichever way the glyphs above it run.
        ui.latin.textContent = w.text.replace(/\s+/g, " ").trim();

        var notes = [];
        var gaps = [];
        for (var i = 0; i < ui.script.unwritable.length; i++) {
            var ch = ui.script.unwritable[i];
            if (w.text.toUpperCase().indexOf(ch) !== -1) gaps.push(ch);
        }
        if (gaps.length) {
            notes.push("No glyph for " + listOf(gaps) + " has ever been published — " +
                (gaps.length > 1 ? "they show as empty runes." : "it shows as an empty rune."));
        }
        // Grouped rather than listed: punctuation and digits are dropped
        // constantly, and naming every character is noise. Say why, and what
        // to do about it.
        var digits = w.dropped.filter(function (c) { return c >= "0" && c <= "9"; });
        var marks = w.dropped.filter(function (c) { return c < "0" || c > "9"; });
        if (marks.length) {
            notes.push("No card art shows a single punctuation mark in this script.");
        }
        if (digits.length) {
            notes.push("It has no numerals either — spell numbers out.");
        }
        ui.warn.dataset.active = notes.length ? "true" : "false";
        ui.warn.textContent = notes.join(" ");
    }

    /* Glyphs per column in a vertical export, before it wraps to a new one. */
    var COLUMN = 12;

    /*
     * Break lines into columns of at most `cap` glyphs, on word boundaries where
     * one is available. A typed newline always starts a new column, matching
     * what it does to the plate in the other two directions.
     */
    function columnise(lines, cap) {
        var cols = [];
        lines.forEach(function (line) {
            var cur = "";
            line.split(" ").forEach(function (word) {
                // A word too long for any column is cut across columns rather
                // than dropped or left to overflow the image.
                while (word.length > cap) {
                    if (cur) { cols.push(cur); cur = ""; }
                    cols.push(word.slice(0, cap));
                    word = word.slice(cap);
                }
                var next = cur ? cur + " " + word : word;
                if (next.length > cap) {
                    cols.push(cur);
                    cur = word;
                } else {
                    cur = next;
                }
            });
            cols.push(cur);
        });
        return cols;
    }

    /*
     * Export at a fixed 3x scale so the PNG is usable for social posts without
     * asking the reader to think about pixel dimensions.
     */
    function download(ui) {
        var pal = ui.script.plate;
        var body = writable(ui.input.value).text;
        var lines = (ui.dir === "rtl" ? reversed(body) : body).split("\n");
        var scale = 3;
        var size = 64 * scale;
        var padX = 56 * scale;
        var padY = 44 * scale;
        var lead = size * 1.6;
        var vertical = ui.dir === "vertical";

        var canvas = document.createElement("canvas");
        var ctx = canvas.getContext("2d");
        var font = size + "px " + ui.script.font + ", serif";
        ctx.font = font;

        if (vertical) {
            // The plate bounds its columns and wraps into more of them, so the
            // export has to as well: a sentence typed on one line would
            // otherwise come out as a single column thousands of pixels tall.
            lines = columnise(lines, COLUMN);
            var longest = lines.reduce(function (n, l) { return Math.max(n, l.length); }, 0);
            canvas.width = Math.ceil(lead * lines.length + padX * 2);
            canvas.height = Math.ceil(size * 1.25 * longest + padY * 2);
        } else {
            var widest = 0;
            lines.forEach(function (line) {
                widest = Math.max(widest, ctx.measureText(line).width);
            });
            canvas.width = Math.ceil(widest + padX * 2);
            canvas.height = Math.ceil(lead * lines.length + padY * 2);
        }

        ctx = canvas.getContext("2d");
        var bg = ctx.createRadialGradient(
            canvas.width / 2, canvas.height * 0.4, 0,
            canvas.width / 2, canvas.height * 0.4, canvas.width * 0.75);
        pal.bg.forEach(function (s) { bg.addColorStop(s[1], s[0]); });
        ctx.fillStyle = bg;
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        var ink = ctx.createLinearGradient(0, 0, canvas.width, 0);
        pal.ink.forEach(function (s) { ink.addColorStop(s[1], s[0]); });

        ctx.font = font;
        ctx.fillStyle = ink;
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";

        if (vertical) {
            lines.forEach(function (line, i) {
                var x = canvas.width - padX - lead * (i + 0.5);
                for (var j = 0; j < line.length; j++) {
                    ctx.fillText(line[j], x, padY + size * 1.25 * (j + 0.5));
                }
            });
        } else {
            lines.forEach(function (line, i) {
                ctx.fillText(line, canvas.width / 2,
                    padY + lead * (i + 0.5));
            });
        }

        canvas.toBlob(function (blob) {
            if (!blob) return;
            var url = URL.createObjectURL(blob);
            var a = document.createElement("a");
            a.href = url;
            a.download = ui.key + ".png";
            document.body.appendChild(a);
            a.click();
            a.remove();
            URL.revokeObjectURL(url);
        });
    }

    function wire(ui) {
        render(ui);
        ui.input.addEventListener("input", function () { render(ui); });

        if (ui.dirs) {
            ui.dirs.addEventListener("click", function (e) {
                var b = e.target.closest(".glyph-dir");
                if (!b) return;
                ui.dir = b.dataset.dir;
                Array.prototype.forEach.call(ui.dirs.children, function (o) {
                    o.setAttribute("aria-pressed", o === b ? "true" : "false");
                });
                render(ui);
            });
        }

        /*
         * The field ships with a sample sentence so the plate is never blank,
         * but that sentence is in the reader's way. Selecting it on first focus
         * makes the first keystroke replace it — the box behaves like a
         * placeholder without giving up the demo.
         */
        var pristine = true;
        ui.input.addEventListener("focus", function () {
            if (pristine && ui.input.value === ui.script.sample) ui.input.select();
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
            if (ui.input.value === ui.script.sample) ui.input.value = "";
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
                document.fonts.load("64px " + ui.script.font).then(function () {
                    download(ui);
                });
            } else {
                download(ui);
            }
        });
    }

    function init() {
        // Independent of the translator: a page may want the chart alone.
        Array.prototype.forEach.call(
            document.querySelectorAll(ALPHABET_MOUNT), function (mount) {
                var script = SCRIPTS[mount.dataset.glyphAlphabet];
                if (!script || mount.dataset.ready === "true") return;
                mount.dataset.ready = "true";
                buildAlphabet(mount, script);
            });

        Array.prototype.forEach.call(
            document.querySelectorAll(TOOL_MOUNT), function (mount) {
                var key = mount.dataset.glyphTool;
                var script = SCRIPTS[key];
                if (!script || mount.dataset.ready === "true") return;
                mount.dataset.ready = "true";
                wire(build(mount, script, key));
            });
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();
