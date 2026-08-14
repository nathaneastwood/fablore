/* Lore Graph — force-directed map of the story/entity connections.
 *
 * Reads the payload that `src/data/mdbook_graph.py` inlines as
 * `window.FABLORE_GRAPH` and renders it to a canvas. No external libraries: the
 * force simulation below is a compact re-implementation of the standard
 * many-body + link-spring model.
 *
 * Repulsion is computed pairwise rather than with a Barnes-Hut approximation.
 * The visible subgraph peaks at ~800 nodes (~320k pairs per tick), which costs
 * a few milliseconds, and the simulation stops once it cools. The tree is not
 * worth the surface area it would add.
 *
 * Colour carries five groups — set, story, character, place, and a neutral
 * "other". A force layout places arbitrary pairs of nodes side by side, so the
 * hues must clear the *all-pairs* colour-vision separation floor rather than the
 * adjacent-pair one; four hues is what clears it, and the remaining kinds share
 * the neutral and are told apart by the legend text and the inspector panel.
 */
(function () {
    "use strict";

    // Selected by class, not id: mdBook derives heading ids from the title, so
    // the page's `# Lore Graph` heading holds `id="lore-graph"`.
    var root = document.querySelector(".lore-graph");
    var data = window.FABLORE_GRAPH;
    var core = window.fabloreGraphCore;
    if (!root || !data || !data.nodes || !data.nodes.length || !core) {
        return;
    }
    var escapeHtml = core.escapeHtml;

    var canvas = document.getElementById("lore-graph-canvas");
    var stage = document.getElementById("lore-graph-stage");
    var panel = document.getElementById("lore-graph-panel");
    var listEl = document.getElementById("lore-graph-list");
    var status = document.getElementById("lore-graph-status");
    var legend = document.getElementById("lore-graph-legend");
    var input = document.getElementById("lore-graph-input");
    var dropdown = document.getElementById("lore-graph-dropdown");
    var degreeSlider = document.getElementById("lore-graph-degree");
    var degreeValue = document.getElementById("lore-graph-degree-value");
    var resetButton = document.getElementById("lore-graph-reset");
    if (!canvas) {
        return;
    }
    var ctx = canvas.getContext("2d");

    var reducedMotion =
        window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    // --- List mode ---------------------------------------------------------
    //
    // Below this width the canvas is dropped for a ranked list. A force layout
    // needs area a phone does not have: at 390px the stage is 348x506 for 417
    // nodes — about 420px² each — and a mark lands near 19px against the 44px
    // minimum tap target. Panning and zooming out of that is not a graph, it is
    // a puzzle.
    //
    // The breakpoint lives here and nowhere else. The stylesheet keys off the
    // `is-list-mode` class this sets, so the two can never drift apart, and the
    // simulation has to know the mode anyway — it must not run for a hidden
    // canvas.
    var listQuery = window.matchMedia ? window.matchMedia("(max-width: 700px)") : null;
    var listMode = !!(listQuery && listQuery.matches);
    // How many rows the list shows before "Show more". The whole filtered run is
    // often several hundred nodes, which is a lot of DOM to hand a phone at once.
    var LIST_PAGE = 60;
    var listShown = LIST_PAGE;
    var listScrollY = 0;

    // --- Model -------------------------------------------------------------

    // Degree is measured on the whole graph, not on the filtered view, so a
    // node's "connections" count means the same thing at every filter setting.
    var nodes = data.nodes.map(function (n, i) {
        return {
            id: i,
            name: n.n,
            kind: n.k,
            group: n.g,
            url: n.u,
            sub: n.s,
            slug: n.sl || "",
            degree: 0,
            neighbours: [],
            x: 0,
            y: 0,
            vx: 0,
            vy: 0
        };
    });
    var links = data.links.map(function (l) {
        return { source: nodes[l[0]], target: nodes[l[1]] };
    });
    links.forEach(function (l) {
        l.source.degree++;
        l.target.degree++;
        l.source.neighbours.push(l.target);
        l.target.neighbours.push(l.source);
    });

    var maxDegree = nodes.reduce(function (m, n) {
        return Math.max(m, n.degree);
    }, 1);

    // Mark shape per kind, from the preprocessor. Heroes and regions draw as
    // stars: each shares a hue with the kind beside it (npc, location) because
    // the palette has no fifth hue to spend, so shape carries the distinction.
    var shapeByKind = Object.create(null);
    (data.groups || []).forEach(function (g) {
        shapeByKind[g.k] = g.s || "circle";
    });
    nodes.forEach(function (n) {
        n.star = shapeByKind[n.kind] === "star";
    });

    // Section order for the inspector panel, supplied by the preprocessor.
    // Falls back to first-seen order if an older payload omits it.
    var subOrder = data.subs && data.subs.length ? data.subs.slice() : [];
    if (!subOrder.length) {
        nodes.forEach(function (n) {
            if (subOrder.indexOf(n.sub) === -1) {
                subOrder.push(n.sub);
            }
        });
    }

    core.buildLabels(nodes).forEach(function (label, i) {
        nodes[i].label = label;
    });

    // --- View state --------------------------------------------------------

    var minDegree = 2;
    // Repulsion coefficient. Scaling every distance uniformly would be invisible
    // — fitToView simply zooms back out — so "spread" means the strength of
    // repulsion *relative* to the link springs, which is what decides how far
    // clusters sit from each other.
    var spread = 240;
    var hiddenKinds = Object.create(null);
    var view = { x: 0, y: 0, k: 1 };
    // Once the reader pans, zooms or jumps to a search hit, the auto-fit stops
    // fighting them for control of the viewport until they reset it.
    var userAdjusted = false;
    var hovered = null;
    var selected = null;
    var dragNode = null;
    var panning = null;
    // A node to centre once the layout settles — see revealNode.
    var pendingFocus = null;
    var active = []; // visible nodes
    var activeLinks = [];
    var highlight = null; // Set of highlighted node ids, or null

    /** Node radius in world units — what the simulation spaces nodes by. */
    function radius(n) {
        return core.nodeRadius(n.degree);
    }

    /**
     * Node radius in world units corrected so the mark keeps a constant size on
     * screen. The auto-fit zoom varies with the filter, so a purely world-space
     * radius would render the whole graph as specks at one setting and as blobs
     * at another. Zooming in therefore spreads nodes apart rather than
     * magnifying them, which is what makes a dense cluster readable.
     */
    function screenRadius(n) {
        return radius(n) / view.k;
    }

    function isVisible(n) {
        return n.degree >= minDegree && !hiddenKinds[n.kind];
    }

    // --- Colours -----------------------------------------------------------
    //
    // Canvas cannot read CSS custom properties, so resolve them once per theme
    // and re-resolve when mdBook swaps the theme class on <html>.

    var palette = {};

    function readPalette() {
        var cs = getComputedStyle(root);
        function v(name) {
            return cs.getPropertyValue(name).trim();
        }
        palette = {
            story: v("--lg-story"),
            character: v("--lg-character"),
            place: v("--lg-place"),
            set: v("--lg-set"),
            other: v("--lg-other"),
            link: v("--lg-link"),
            linkActive: v("--lg-link-active"),
            dim: v("--lg-dim"),
            label: v("--lg-label"),
            surface: v("--lg-surface"),
            accent: v("--lg-accent")
        };
    }

    function nodeColour(n) {
        return palette[n.group] || palette.other;
    }

    // --- Layout ------------------------------------------------------------

    var alpha = 1;
    var alphaTarget = 0;
    var running = false;
    var width = 0;
    var height = 0;

    function seedPositions() {
        // Phyllotaxis start: an even spread that avoids the symmetric artefacts
        // of a random seed and settles in fewer ticks.
        var golden = Math.PI * (3 - Math.sqrt(5));
        active.forEach(function (n, i) {
            if (n.seeded) {
                return;
            }
            var r = 12 * Math.sqrt(i + 0.5);
            var a = golden * i;
            n.x = Math.cos(a) * r;
            n.y = Math.sin(a) * r;
            n.vx = 0;
            n.vy = 0;
            n.seeded = true;
        });
    }

    function tick() {
        var i;
        var n;
        var decay = 0.6;

        // Many-body repulsion, symmetric so each pair is visited once.
        for (i = 0; i < active.length; i++) {
            var a = active[i];
            for (var j = i + 1; j < active.length; j++) {
                var b = active[j];
                var dx = b.x - a.x;
                var dy = b.y - a.y;
                var d2 = dx * dx + dy * dy;
                if (d2 === 0) {
                    dx = (Math.random() - 0.5) * 0.1;
                    dy = (Math.random() - 0.5) * 0.1;
                    d2 = dx * dx + dy * dy;
                }
                // Collision floor. Repulsion alone falls off as 1/d², so it is
                // far too weak at close range to stop nodes stacking — this is
                // what actually clears the pile-up in the middle.
                var minSep = radius(a) + radius(b) + 7;
                if (d2 < minSep * minSep) {
                    var d = Math.sqrt(d2) || 1;
                    var push = ((minSep - d) / d) * 0.4;
                    a.vx -= dx * push;
                    a.vy -= dy * push;
                    b.vx += dx * push;
                    b.vy += dy * push;
                }

                if (d2 > 640000) {
                    continue; // beyond 800px the term is negligible
                }
                // Busier nodes push harder, which opens space around the hubs
                // instead of letting them collapse into one another.
                var f = (-spread * (2 + Math.sqrt(a.degree + b.degree)) * alpha) / d2;
                var fx = dx * f;
                var fy = dy * f;
                a.vx += fx;
                a.vy += fy;
                b.vx -= fx;
                b.vy -= fy;
            }
        }

        // Link springs. Stiffness falls off with the busier endpoint so hubs
        // are not dragged apart by their own popularity.
        for (i = 0; i < activeLinks.length; i++) {
            var l = activeLinks[i];
            var s = l.source;
            var t = l.target;
            var lx = t.x + t.vx - s.x - s.vx;
            var ly = t.y + t.vy - s.y - s.vy;
            var dist = Math.sqrt(lx * lx + ly * ly) || 1;
            var rest = 34 + radius(s) + radius(t);
            var strength = 1 / Math.min(s.degree, t.degree);
            var amount = ((dist - rest) / dist) * alpha * strength * 0.7;
            lx *= amount;
            ly *= amount;
            var share = t.degree / (s.degree + t.degree);
            t.vx -= lx * share;
            t.vy -= ly * share;
            s.vx += lx * (1 - share);
            s.vy += ly * (1 - share);
        }

        // Weak gravity keeps detached components from drifting off for ever.
        // It stays low so it shapes the layout rather than compressing it —
        // fitToView does the work of getting everything on screen.
        //
        // The pull is weaker along the wider axis, so the cloud settles into the
        // shape of the stage instead of a circle. fitToView scales by whichever
        // axis binds first, so a circular layout in a 4:3 box wastes the sides.
        var aspect = height > 0 ? width / height : 1;
        var gx = (0.003 * alpha) / (aspect > 1 ? aspect * aspect : 1);
        var gy = 0.003 * alpha * (aspect < 1 ? aspect * aspect : 1);
        for (i = 0; i < active.length; i++) {
            n = active[i];
            n.vx -= n.x * gx;
            n.vy -= n.y * gy;
        }

        for (i = 0; i < active.length; i++) {
            n = active[i];
            if (n === dragNode) {
                n.vx = 0;
                n.vy = 0;
                continue;
            }
            n.vx *= decay;
            n.vy *= decay;
            n.x += n.vx;
            n.y += n.vy;
        }

        alpha += (alphaTarget - alpha) * 0.0228;
    }

    function reheat(target) {
        alpha = Math.max(alpha, target || 0.4);
        if (!running) {
            running = true;
            requestAnimationFrame(frame);
        }
    }

    function frame() {
        // A rotation into list mode can land mid-settle. The canvas is hidden by
        // then, so every further tick is work nobody sees.
        if (listMode) {
            running = false;
            pendingFocus = null;
            return;
        }
        tick();
        if (!userAdjusted) {
            fitToView();
        }
        draw();
        if (alpha > 0.005 || dragNode) {
            requestAnimationFrame(frame);
        } else {
            running = false;
            if (pendingFocus) {
                var target = pendingFocus;
                pendingFocus = null;
                centreOn(target);
            }
        }
    }

    /** Frame every visible node, unless the reader has panned or zoomed. */
    function fitToView() {
        if (!active.length || !width || !height) {
            return;
        }
        var minX = Infinity;
        var minY = Infinity;
        var maxX = -Infinity;
        var maxY = -Infinity;
        for (var i = 0; i < active.length; i++) {
            var n = active[i];
            var r = radius(n);
            if (n.x - r < minX) minX = n.x - r;
            if (n.y - r < minY) minY = n.y - r;
            if (n.x + r > maxX) maxX = n.x + r;
            if (n.y + r > maxY) maxY = n.y + r;
        }
        var pad = 28;
        var k = Math.min(
            (width - pad * 2) / Math.max(maxX - minX, 1),
            (height - pad * 2) / Math.max(maxY - minY, 1)
        );
        view.k = Math.min(2.5, Math.max(0.12, k));
        view.x = -((minX + maxX) / 2) * view.k;
        view.y = -((minY + maxY) / 2) * view.k;
    }

    // --- Rendering ---------------------------------------------------------

    function resize() {
        var rect = canvas.getBoundingClientRect();
        var dpr = window.devicePixelRatio || 1;
        width = rect.width;
        height = rect.height;
        canvas.width = Math.round(width * dpr);
        canvas.height = Math.round(height * dpr);
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
        draw();
    }

    function toScreen(n) {
        return {
            x: n.x * view.k + view.x + width / 2,
            y: n.y * view.k + view.y + height / 2
        };
    }

    // A five-pointed star of outer radius R covers well under half the ink of a
    // circle of the same R, so it needs enlarging to carry the same visual
    // weight — otherwise heroes and regions would read as smaller than the
    // characters and locations they outrank.
    var STAR_OUTER = 1.45;
    var STAR_INNER = 0.46;

    /** Outermost extent of the drawn mark — what labels and hit tests clear. */
    function markRadius(n) {
        return n.star ? screenRadius(n) * STAR_OUTER : screenRadius(n);
    }

    /** Path the node's mark at `r`, leaving it ready to fill and stroke. */
    function tracePath(n, r) {
        ctx.beginPath();
        if (!n.star) {
            ctx.arc(n.x, n.y, r, 0, Math.PI * 2);
            return;
        }
        var points = core.starPoints(n.x, n.y, r * STAR_OUTER, STAR_INNER);
        for (var p = 0; p < points.length; p++) {
            if (p === 0) {
                ctx.moveTo(points[p][0], points[p][1]);
            } else {
                ctx.lineTo(points[p][0], points[p][1]);
            }
        }
        ctx.closePath();
    }

    function draw() {
        if (!width || !height) {
            return;
        }
        ctx.save();
        ctx.clearRect(0, 0, width, height);
        ctx.translate(width / 2 + view.x, height / 2 + view.y);
        ctx.scale(view.k, view.k);

        var focus = selected || hovered;
        var i;
        var l;

        // Edges first, so nodes sit on top of them.
        ctx.lineWidth = 1 / view.k;
        ctx.strokeStyle = highlight ? palette.dim : palette.link;
        ctx.beginPath();
        for (i = 0; i < activeLinks.length; i++) {
            l = activeLinks[i];
            if (highlight && (l.source === focus || l.target === focus)) {
                continue;
            }
            ctx.moveTo(l.source.x, l.source.y);
            ctx.lineTo(l.target.x, l.target.y);
        }
        ctx.stroke();

        if (highlight && focus) {
            ctx.strokeStyle = palette.linkActive;
            ctx.lineWidth = 1.4 / view.k;
            ctx.beginPath();
            for (i = 0; i < activeLinks.length; i++) {
                l = activeLinks[i];
                if (l.source === focus || l.target === focus) {
                    ctx.moveTo(l.source.x, l.source.y);
                    ctx.lineTo(l.target.x, l.target.y);
                }
            }
            ctx.stroke();
        }

        // Nodes.
        for (i = 0; i < active.length; i++) {
            var n = active[i];
            var r = screenRadius(n);
            var lit = !highlight || highlight.has(n.id);
            tracePath(n, r);
            ctx.fillStyle = lit ? nodeColour(n) : palette.dim;
            ctx.fill();
            if (n === focus) {
                ctx.lineWidth = 2 / view.k;
                ctx.strokeStyle = palette.accent;
                ctx.stroke();
            } else if (lit && r * view.k > 4) {
                // A surface-coloured ring separates overlapping marks.
                ctx.lineWidth = 1 / view.k;
                ctx.strokeStyle = palette.surface;
                ctx.stroke();
            }
        }

        drawLabels(focus);
        ctx.restore();
    }

    /**
     * Label the focused node, its neighbours, and otherwise only the busiest
     * hubs — and drop any label whose box would collide with one already drawn.
     * Candidates are visited in descending degree so the more connected node
     * wins the space when two overlap.
     */
    function drawLabels(focus) {
        var candidates = active.filter(function (n) {
            return (
                n === focus ||
                (highlight && highlight.has(n.id)) ||
                (!highlight && n.degree >= Math.max(8, maxDegree * 0.3))
            );
        });
        if (!candidates.length) {
            return;
        }
        candidates.sort(function (a, b) {
            return (b === focus ? 1 : 0) - (a === focus ? 1 : 0) || b.degree - a.degree;
        });

        var fontSize = 12 / view.k;
        var lineHeight = fontSize * 1.15;
        ctx.textAlign = "center";
        ctx.textBaseline = "top";
        ctx.font = fontSize + "px system-ui, -apple-system, 'Segoe UI', sans-serif";
        ctx.lineWidth = 3.5 / view.k;
        ctx.strokeStyle = palette.surface;
        ctx.fillStyle = palette.label;

        var placed = [];
        for (var i = 0; i < candidates.length; i++) {
            var m = candidates[i];
            var w = ctx.measureText(m.label).width;
            var x0 = m.x - w / 2;
            var y0 = m.y + markRadius(m) + 3 / view.k;
            var box = { x0: x0, y0: y0, x1: x0 + w, y1: y0 + lineHeight };
            var clash = false;
            for (var j = 0; j < placed.length; j++) {
                if (core.boxesOverlap(box, placed[j])) {
                    clash = true;
                    break;
                }
            }
            if (clash) {
                continue;
            }
            placed.push(box);
            ctx.strokeText(m.label, m.x, y0);
            ctx.fillText(m.label, m.x, y0);
        }
    }

    // --- Filtering ---------------------------------------------------------

    function applyFilter(options) {
        active = nodes.filter(isVisible);
        var live = new Set(
            active.map(function (n) {
                return n.id;
            })
        );
        activeLinks = links.filter(function (l) {
            return live.has(l.source.id) && live.has(l.target.id);
        });
        if (selected && !live.has(selected.id)) {
            select(null);
        }
        if (status) {
            status.textContent =
                active.length +
                " nodes, " +
                activeLinks.length +
                " connections shown of " +
                nodes.length +
                " and " +
                links.length +
                ".";
        }
        // The list is rebuilt from `active`, so it re-ranks itself for free; the
        // simulation is skipped entirely because there is no canvas to settle.
        if (listMode) {
            listShown = LIST_PAGE;
            renderList();
            return;
        }
        seedPositions();
        if (options && options.settle && reducedMotion) {
            for (var i = 0; i < 300; i++) {
                tick();
            }
            alpha = 0;
            fitToView();
            draw();
            return;
        }
        reheat(1);
    }

    // --- Selection and the inspector panel ---------------------------------

    function setHighlight(node) {
        if (!node) {
            highlight = null;
            return;
        }
        highlight = new Set([node.id]);
        node.neighbours.forEach(function (m) {
            if (isVisible(m)) {
                highlight.add(m.id);
            }
        });
    }

    /**
     * Swatch matching the node's mark on the canvas — same hue, same shape.
     * The legend is where a reader learns that a star means hero or region, so
     * it has to be the same star.
     */
    function dotMarkup(kind, group) {
        return (
            '<span class="lore-graph-dot lore-graph-dot-' +
            group +
            (shapeByKind[kind] === "star" ? " lore-graph-dot-star" : "") +
            '" aria-hidden="true"></span>'
        );
    }

    var FOCUS_ICON =
        '<svg viewBox="0 0 16 16" width="12" height="12" aria-hidden="true" focusable="false">' +
        '<circle cx="8" cy="8" r="4.2" fill="none" stroke="currentColor" stroke-width="1.6"/>' +
        '<path d="M8 0.8v2.6M8 12.6v2.6M0.8 8h2.6M12.6 8h2.6" stroke="currentColor"' +
        ' stroke-width="1.6" stroke-linecap="round"/></svg>';

    function panelHtml(node) {
        var parts = [];
        // Two controls, and the difference between them is the point: ← undoes
        // one step of the walk, × leaves it altogether. Without the arrow the
        // only way back a step is the browser's own button, which is a long
        // reach on a phone and easy to miss on a desktop.
        //
        // Disabled rather than hidden at the start of a walk — a deep link opens
        // straight into a node with nothing of ours behind it, and an arrow that
        // silently became "leave the site" is worse than one that is visibly
        // spent. Keeping it in place also stops the title reflowing mid-walk.
        parts.push(
            '<button type="button" class="lore-graph-panel-back"' +
                (currentDepth() > 0 ? "" : " disabled") +
                ' title="Back" aria-label="Back to the previous entry">←</button>'
        );
        // Over the canvas × dismisses an overlay and the graph is still there
        // behind it. In list mode this view *is* the page, so it goes out to the
        // list, and only the label can say so.
        parts.push('<button type="button" class="lore-graph-panel-close"');
        parts.push(
            ' aria-label="' + (listMode ? "Back to the list" : "Close") + '">×</button>'
        );
        parts.push('<p class="lore-graph-panel-kind">' + escapeHtml(node.sub) + "</p>");
        if (node.url) {
            parts.push(
                '<h3 class="lore-graph-panel-title"><a href="' +
                    escapeHtml(node.url) +
                    '">' +
                    escapeHtml(node.name) +
                    "</a></h3>"
            );
        } else {
            parts.push(
                '<h3 class="lore-graph-panel-title">' + escapeHtml(node.name) + "</h3>"
            );
        }

        var shown = node.neighbours.filter(isVisible);
        parts.push(
            '<p class="lore-graph-panel-count">' +
                node.degree +
                (node.degree === 1 ? " connection" : " connections") +
                (shown.length !== node.degree ? " (" + shown.length + " shown)" : "") +
                // Without this the trailing numbers are unexplained.
                '<br><span class="lore-graph-panel-hint">grouped by type, ' +
                "most connected first</span></p>"
        );

        // Grouped by type, then most-connected first within each group, with the
        // count shown. The list used to be one flat run sorted by connection
        // count — a defensible order, but the key was never displayed, so it
        // read as random. Chronological was the other candidate and is not
        // available: only a quarter of the stories carry a publication date.
        //
        // Stories are grouped by their specific type (`sub`), so a set's flavour
        // page and its digital tiles land in separate sections rather than one
        // undifferentiated "Story" run.
        core.groupConnections(shown, subOrder).forEach(function (section) {
            var rows = section.rows;
            parts.push(
                '<p class="lore-graph-panel-group">' +
                    escapeHtml(section.sub) +
                    ' <span class="lore-graph-panel-group-count">' +
                    rows.length +
                    "</span></p>"
            );
            parts.push('<ul class="lore-graph-panel-list">');
            rows.slice(0, 25).forEach(function (m) {
                var label = escapeHtml(m.name);
                var body = m.url
                    ? '<a href="' + escapeHtml(m.url) + '">' + label + "</a>"
                    : label;
                parts.push(
                    "<li>" +
                        dotMarkup(m.kind, m.group) +
                        body +
                        ' <span class="lore-graph-panel-sub" title="' +
                        m.degree +
                        ' connections">' +
                        m.degree +
                        "</span>" +
                        // Separate from the name link on purpose: the link
                        // leaves for the page, this stays and re-roots the
                        // panel, so the reader can walk the graph. In list mode
                        // there is no graph to move, so it is named for what it
                        // does there instead: open that node's own connections.
                        '<button type="button" class="lore-graph-focus"' +
                        ' data-node="' +
                        m.id +
                        '" title="' +
                        (listMode ? "Show its connections" : "Show this in the graph") +
                        '" aria-label="Show ' +
                        escapeHtml(m.name) +
                        (listMode ? "'s connections" : " in the graph") +
                        '">' +
                        FOCUS_ICON +
                        "</button></li>"
                );
            });
            if (rows.length > 25) {
                parts.push(
                    '<li class="lore-graph-panel-more">and ' +
                        (rows.length - 25) +
                        " more…</li>"
                );
            }
            parts.push("</ul>");
        });
        return parts.join("");
    }

    // --- The narrow-viewport list ------------------------------------------
    //
    // Master and detail in one container. The master is the ranked run of what
    // is visible; the detail is `panelHtml` unchanged, so the connection view a
    // reader gets on a phone is the same one they get on the canvas.

    /** The ranked master list: what is biggest in the archive right now. */
    function listHtml() {
        var ranked = core.rankNodes(active, input ? input.value : "");
        if (!ranked.length) {
            return (
                '<p class="lore-graph-list-empty">Nothing matches. Try a shorter ' +
                "search, turn a type back on, or lower the minimum connections.</p>"
            );
        }
        var parts = [];
        parts.push(
            '<p class="lore-graph-list-count">' +
                ranked.length +
                (ranked.length === 1 ? " entry" : " entries") +
                ", most connected first</p>"
        );
        parts.push('<ul class="lore-graph-list-rows">');
        ranked.slice(0, listShown).forEach(function (n) {
            // A button, not a link: tapping opens the connections, which is what
            // the canvas does on a click. The page itself is one tap further in,
            // from the title link in the detail.
            parts.push(
                '<li><button type="button" class="lore-graph-list-row" data-node="' +
                    n.id +
                    '">' +
                    dotMarkup(n.kind, n.group) +
                    '<span class="lore-graph-list-text">' +
                    '<span class="lore-graph-list-name">' +
                    escapeHtml(n.name) +
                    "</span>" +
                    '<span class="lore-graph-list-sub">' +
                    escapeHtml(n.sub) +
                    "</span></span>" +
                    '<span class="lore-graph-list-degree" title="' +
                    n.degree +
                    ' connections">' +
                    n.degree +
                    "</span></button></li>"
            );
        });
        parts.push("</ul>");
        if (ranked.length > listShown) {
            parts.push(
                '<button type="button" class="lore-graph-list-more">Show ' +
                    Math.min(LIST_PAGE, ranked.length - listShown) +
                    " more</button>"
            );
        }
        return parts.join("");
    }

    function renderList() {
        if (!listEl) {
            return;
        }
        listEl.innerHTML = selected ? panelHtml(selected) : listHtml();
    }

    /**
     * Put the top of the list under the reader's thumb. The detail replaces the
     * whole master in place, so without this a reader who tapped the fortieth
     * row opens its connections already scrolled past the title.
     */
    function scrollListToTop() {
        if (!listEl) {
            return;
        }
        var top = listEl.getBoundingClientRect().top + (window.pageYOffset || 0);
        window.scrollTo(0, Math.max(0, top - 12));
    }

    /** Open a master row, remembering the place in the list to come back to. */
    function openFromList(node) {
        if (!node) {
            return;
        }
        listScrollY = window.pageYOffset || 0;
        select(node);
        scrollListToTop();
    }

    /**
     * Reveal a node whatever the current filters hide, then select and centre
     * it. Shared by the search box and by an incoming `#slug` deep link — both
     * mean "show me this", and neither should silently do nothing because the
     * minimum-connections slider happens to exclude it.
     */
    function revealNode(node) {
        var changed = false;
        if (node.degree < minDegree) {
            minDegree = 1;
            if (degreeSlider) {
                degreeSlider.value = "1";
            }
            if (degreeValue) {
                degreeValue.textContent = "1";
            }
            changed = true;
        }
        if (hiddenKinds[node.kind]) {
            hiddenKinds[node.kind] = false;
            if (legend) {
                var chip = legend.querySelector('[data-kind="' + node.kind + '"]');
                if (chip) {
                    chip.classList.add("is-on");
                    chip.setAttribute("aria-pressed", "true");
                }
            }
            changed = true;
        }
        // Only re-run the layout if a filter actually moved — otherwise this
        // reheats a settled graph for nothing.
        if (changed) {
            applyFilter();
        }
        select(node);
        if (listMode) {
            // Nothing to centre — the detail is already the whole view. The
            // reader may be anywhere down a long page, so bring it into sight.
            scrollListToTop();
            return;
        }
        // Centring locks the zoom (fitToView stops once the reader takes over),
        // so it must wait for the layout to settle. Centring mid-settle froze
        // the zoom the compact early layout had been fitted to, which is what
        // made a deep link open zoomed right in.
        if (running) {
            pendingFocus = node;
        } else {
            centreOn(node);
        }
    }

    // --- History -----------------------------------------------------------
    //
    // Each selection is a history entry, so Back retraces the walk a node at a
    // time. This replaced a `replaceState` that kept the address bar shareable
    // without ever stacking an entry — which left Back with nothing to retrace,
    // so a reader four connections deep lost the whole route in one press and
    // had no way to remember how they got there.
    //
    // The cost is real and was the original reason for `replaceState`: clicking
    // twenty nodes now takes twenty Backs to leave the page. Retracing is worth
    // more than a fast exit, and the panel's × still closes in one press.

    /** True while an entry is being applied, so it does not re-push itself. */
    var applyingHistory = false;

    /** How many selections deep the current entry is; 0 means start of walk. */
    function currentDepth() {
        return core.historyDepth(window.history && window.history.state);
    }

    /** Push the selection onto the history, unless it is already the entry. */
    function recordInHistory(node) {
        if (!window.history || !window.history.pushState) {
            return;
        }
        var hash = node && node.slug ? "#" + node.slug : "";
        // Re-selecting what is already showing is not a step in the walk. This
        // also covers applying an entry that already names the node, which is
        // what stops a Back press from pushing the entry it just came from.
        if (hash === window.location.hash) {
            return;
        }
        if (applyingHistory) {
            return;
        }
        window.history.pushState(
            { fabloreGraph: currentDepth() + 1 },
            "",
            window.location.pathname + hash
        );
    }

    function select(node) {
        selected = node;
        setHighlight(node || hovered);
        recordInHistory(node);
        // One selection, rendered wherever the current mode puts it. Keeping
        // `selected` mode-independent is what lets a rotation carry the reader's
        // place across with it.
        if (listMode) {
            renderList();
            return;
        }
        if (panel) {
            if (node) {
                panel.innerHTML = panelHtml(node);
                panel.hidden = false;
            } else {
                panel.hidden = true;
                panel.innerHTML = "";
            }
        }
        draw();
    }

    /**
     * Pan the node into the middle of the stage at the current zoom.
     * Deliberately does not change `view.k`: zooming in on a search hit throws
     * away the overview the reader was using to place it.
     */
    function centreOn(node) {
        userAdjusted = true;
        view.x = -node.x * view.k;
        view.y = -node.y * view.k;
        draw();
    }

    // --- Hit testing -------------------------------------------------------

    function nodeAt(px, py) {
        var wx = (px - width / 2 - view.x) / view.k;
        var wy = (py - height / 2 - view.y) / view.k;
        var best = null;
        var bestD = Infinity;
        for (var i = 0; i < active.length; i++) {
            var n = active[i];
            var dx = n.x - wx;
            var dy = n.y - wy;
            var d = dx * dx + dy * dy;
            var r = markRadius(n) + 5 / view.k; // hit target larger than the mark
            if (d < r * r && d < bestD) {
                best = n;
                bestD = d;
            }
        }
        return best;
    }

    function pointerPos(e) {
        var rect = canvas.getBoundingClientRect();
        return { x: e.clientX - rect.left, y: e.clientY - rect.top };
    }

    // --- Events ------------------------------------------------------------

    canvas.addEventListener("pointermove", function (e) {
        var p = pointerPos(e);
        if (dragNode) {
            dragNode.x = (p.x - width / 2 - view.x) / view.k;
            dragNode.y = (p.y - height / 2 - view.y) / view.k;
            reheat(0.3);
            return;
        }
        if (panning) {
            userAdjusted = true;
            view.x = panning.vx + (e.clientX - panning.x);
            view.y = panning.vy + (e.clientY - panning.y);
            draw();
            return;
        }
        var hit = nodeAt(p.x, p.y);
        if (hit !== hovered) {
            hovered = hit;
            canvas.style.cursor = hit ? "pointer" : "grab";
            if (!selected) {
                setHighlight(hovered);
            }
            draw();
        }
    });

    canvas.addEventListener("pointerdown", function (e) {
        var p = pointerPos(e);
        var hit = nodeAt(p.x, p.y);
        canvas.setPointerCapture(e.pointerId);
        if (hit) {
            dragNode = hit;
            dragNode.moved = false;
            reheat(0.3);
        } else {
            panning = { x: e.clientX, y: e.clientY, vx: view.x, vy: view.y };
            canvas.style.cursor = "grabbing";
        }
    });

    canvas.addEventListener("pointerup", function (e) {
        var wasDrag = dragNode;
        var movedFar = panning && (Math.abs(e.clientX - panning.x) > 3 || Math.abs(e.clientY - panning.y) > 3);
        if (wasDrag) {
            var p = pointerPos(e);
            var stillOn = nodeAt(p.x, p.y) === wasDrag;
            dragNode = null;
            if (stillOn) {
                select(wasDrag === selected ? null : wasDrag);
            }
        } else if (!movedFar) {
            select(null);
        }
        panning = null;
        canvas.style.cursor = hovered ? "pointer" : "grab";
        canvas.releasePointerCapture(e.pointerId);
    });

    canvas.addEventListener("dblclick", function (e) {
        var hit = nodeAt(pointerPos(e).x, pointerPos(e).y);
        if (hit && hit.url) {
            window.location.href = hit.url;
        }
    });

    canvas.addEventListener(
        "wheel",
        function (e) {
            e.preventDefault();
            userAdjusted = true;
            var p = pointerPos(e);
            var factor = Math.pow(1.0015, -e.deltaY);
            var next = Math.min(6, Math.max(0.2, view.k * factor));
            var wx = (p.x - width / 2 - view.x) / view.k;
            var wy = (p.y - height / 2 - view.y) / view.k;
            view.k = next;
            view.x = p.x - width / 2 - wx * view.k;
            view.y = p.y - height / 2 - wy * view.k;
            draw();
        },
        { passive: false }
    );

    canvas.addEventListener("pointerleave", function () {
        if (hovered && !selected) {
            hovered = null;
            setHighlight(null);
            draw();
        }
        hovered = null;
    });

    /**
     * Clicks inside the inspector. The same markup renders into the stage panel
     * and into the list, so both bind this; only what "close" and "focus" then
     * mean to the viewport differs.
     */
    function handleInspectorClick(e) {
        // Deliberately the browser's own Back rather than a private trail: the
        // arrow and the Back button then cannot disagree about where "back" is,
        // and the phone's back gesture retraces the walk for free.
        if (e.target.closest(".lore-graph-panel-back")) {
            window.history.back();
            return true;
        }
        if (e.target.closest(".lore-graph-panel-close")) {
            select(null);
            if (listMode) {
                // Back to the master — and back to the row they came from, which
                // is otherwise lost every time they look at a connection.
                window.scrollTo(0, listScrollY);
            }
            return true;
        }
        var focusButton = e.target.closest(".lore-graph-focus");
        if (focusButton) {
            var next = nodes[parseInt(focusButton.dataset.node, 10)];
            if (next) {
                select(next);
                if (listMode) {
                    scrollListToTop();
                } else {
                    centreOn(next);
                    panel.scrollTop = 0;
                }
            }
            return true;
        }
        return false;
    }

    if (panel) {
        panel.addEventListener("click", handleInspectorClick);
    }

    if (listEl) {
        listEl.addEventListener("click", function (e) {
            if (e.target.closest(".lore-graph-list-more")) {
                listShown += LIST_PAGE;
                renderList();
                return;
            }
            var row = e.target.closest(".lore-graph-list-row");
            if (row) {
                openFromList(nodes[parseInt(row.dataset.node, 10)]);
                return;
            }
            handleInspectorClick(e);
        });
    }

    document.addEventListener("keydown", function (e) {
        if (e.key === "Escape" && selected && document.activeElement !== input) {
            select(null);
            if (listMode) {
                window.scrollTo(0, listScrollY);
            }
        }
    });

    // --- Legend ------------------------------------------------------------

    if (legend) {
        (data.groups || []).forEach(function (g) {
            var chip = document.createElement("button");
            chip.type = "button";
            chip.className = "lore-graph-chip is-on";
            chip.dataset.kind = g.k;
            chip.setAttribute("aria-pressed", "true");
            chip.innerHTML =
                dotMarkup(g.k, g.g) +
                escapeHtml(g.l) +
                ' <span class="lore-graph-chip-count">' +
                g.c +
                "</span>";
            chip.addEventListener("click", function () {
                var off = !hiddenKinds[g.k];
                hiddenKinds[g.k] = off;
                chip.classList.toggle("is-on", !off);
                chip.setAttribute("aria-pressed", String(!off));
                applyFilter();
            });
            legend.appendChild(chip);
        });
    }

    // --- Degree slider -----------------------------------------------------

    if (degreeSlider) {
        degreeSlider.addEventListener("input", function () {
            minDegree = parseInt(degreeSlider.value, 10) || 1;
            if (degreeValue) {
                degreeValue.textContent = String(minDegree);
            }
            applyFilter();
        });
    }

    var spreadSlider = document.getElementById("lore-graph-spread");
    if (spreadSlider) {
        spreadSlider.value = String(spread);
        spreadSlider.addEventListener("input", function () {
            spread = parseInt(spreadSlider.value, 10) || 240;
            reheat(0.7);
        });
    }

    // --- Search ------------------------------------------------------------

    if (input && dropdown) {
        var closeDropdown = function () {
            dropdown.hidden = true;
            dropdown.innerHTML = "";
        };

        input.addEventListener("input", function () {
            // In list mode the box filters the list in place rather than opening
            // a dropdown over it: the list is already a list of results, so a
            // second one on top of it would be the same rows twice. Typing from
            // a detail view returns to the master, which is where the matches are.
            if (listMode) {
                listShown = LIST_PAGE;
                if (selected) {
                    select(null);
                } else {
                    renderList();
                }
                return;
            }
            var q = input.value.trim().toLowerCase();
            if (q.length < 2) {
                closeDropdown();
                return;
            }
            var matches = nodes
                .filter(function (n) {
                    return n.name.toLowerCase().indexOf(q) !== -1;
                })
                .sort(function (a, b) {
                    return b.degree - a.degree;
                })
                .slice(0, 10);
            if (!matches.length) {
                closeDropdown();
                return;
            }
            dropdown.innerHTML = "";
            matches.forEach(function (n) {
                var li = document.createElement("li");
                li.innerHTML =
                    dotMarkup(n.kind, n.group) +
                    escapeHtml(n.name) +
                    ' <span class="lore-graph-panel-sub">' +
                    escapeHtml(n.sub) +
                    "</span>";
                li.addEventListener("mousedown", function (e) {
                    e.preventDefault();
                    revealNode(n);
                    input.value = "";
                    closeDropdown();
                });
                dropdown.appendChild(li);
            });
            dropdown.hidden = false;
        });

        input.addEventListener("blur", function () {
            window.setTimeout(closeDropdown, 120);
        });
        input.addEventListener("keydown", function (e) {
            if (e.key === "Escape") {
                closeDropdown();
            }
        });
    }

    if (resetButton) {
        resetButton.addEventListener("click", function () {
            userAdjusted = false;
            select(null);
            fitToView();
            draw();
        });
    }

    // --- Theme changes -----------------------------------------------------

    var themeObserver = new MutationObserver(function () {
        readPalette();
        draw();
    });
    themeObserver.observe(document.documentElement, {
        attributes: true,
        attributeFilter: ["class"]
    });

    // --- Mode switching ----------------------------------------------------

    /** Show the half of the page the current mode uses, and hide the other. */
    function applyModeToDom() {
        root.classList.toggle("is-list-mode", listMode);
        if (stage) {
            stage.hidden = listMode;
        }
        if (listEl) {
            listEl.hidden = !listMode;
        }
    }

    /**
     * Cross the breakpoint — a rotation, or a desktop window being dragged
     * narrow. The selection survives the crossing; only how it is drawn changes.
     */
    function setListMode(on) {
        if (on === listMode) {
            return;
        }
        listMode = on;
        applyModeToDom();
        if (listMode) {
            if (panel) {
                panel.hidden = true;
                panel.innerHTML = "";
            }
            listShown = LIST_PAGE;
            renderList();
            return;
        }
        if (listEl) {
            listEl.innerHTML = "";
        }
        if (panel && selected) {
            panel.innerHTML = panelHtml(selected);
            panel.hidden = false;
        }
        // The canvas measured zero while it was hidden, and the simulation has
        // not run for however long the reader spent in the list, so the layout
        // has to be measured and settled again before anything is drawn.
        resize();
        seedPositions();
        reheat(1);
    }

    if (listQuery) {
        var onModeChange = function (e) {
            setListMode(e.matches);
        };
        if (listQuery.addEventListener) {
            listQuery.addEventListener("change", onModeChange);
        } else if (listQuery.addListener) {
            listQuery.addListener(onModeChange);
        }
    }

    // --- Boot --------------------------------------------------------------

    readPalette();
    if (degreeValue && degreeSlider) {
        degreeSlider.value = String(minDegree);
        degreeValue.textContent = String(minDegree);
    }
    applyModeToDom();
    resize();
    applyFilter({ settle: true });

    // Deep link. Opening `graph.html#dorinthea` selects that node, and every
    // page that has a node links in this way — so the graph is reachable from
    // the archive rather than only from the table of contents.
    /**
     * Bring the view in line with the address bar — on load, on a Back or
     * Forward, and on a hash typed or linked in.
     *
     * Returning early when the view already matches is what makes it safe to
     * bind twice: a traversal between two hashes fires `popstate` *and*
     * `hashchange`, and applying the same entry twice would re-centre the
     * canvas and throw away the reader's scroll position in the list.
     */
    function applyHash() {
        var target = core.findBySlug(nodes, window.location.hash);
        if (target === selected) {
            return;
        }
        // The entry is already in the bar; recording it again would push a
        // duplicate and, on a Back, one the reader could never get past.
        applyingHistory = true;
        try {
            if (target) {
                revealNode(target);
            } else {
                select(null);
            }
        } finally {
            applyingHistory = false;
        }
    }
    applyHash();
    window.addEventListener("popstate", applyHash);
    window.addEventListener("hashchange", applyHash);

    if (window.ResizeObserver) {
        new ResizeObserver(resize).observe(canvas.parentElement || canvas);
    } else {
        window.addEventListener("resize", resize);
    }
})();
