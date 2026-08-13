/* Lore Graph — pure helpers, extracted so they can be tested.
 *
 * Everything here is a plain function over plain data: no canvas, no DOM, no
 * module state. `theme/graph.js` keeps the parts that genuinely need a browser
 * (the simulation loop, rendering, pointer handling) and calls into this file
 * for the decisions worth pinning down — which is where the bugs were.
 *
 * Loaded as a bare script in the browser (globals on `window.fabloreGraphCore`)
 * and as a CommonJS module under `node --test`, following the same dual-export
 * shape as Cardulary's `order-token.js`.
 */
(function (root) {
    "use strict";

    var HTML_ESCAPES = {
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;"
    };

    /** Escape a string for interpolation into innerHTML. */
    function escapeHtml(s) {
        return String(s).replace(/[&<>"']/g, function (c) {
            return HTML_ESCAPES[c];
        });
    }

    /**
     * Radius of a node's mark in world units, from its connection count.
     * Square-rooted so a hub with 40 connections is legible beside a leaf with
     * one, without swamping it — area, not radius, tracks the count.
     */
    function nodeRadius(degree) {
        return 1.9 + Math.sqrt(Math.max(0, degree || 0)) * 1.25;
    }

    /**
     * Canvas label for each node, disambiguating repeated names.
     *
     * A name is not unique in this archive: a set, its flavour page and its
     * digital-tile page are all "Bright Lights", and several heroes share a name
     * with their own short story. On the canvas those are told apart by colour
     * alone, so a repeated name carries its type. The type alone is enough — no
     * name repeats within a single type.
     *
     * @param {Array<{name: string, sub: string}>} nodes
     * @returns {Array<string>} label per node, positionally matching `nodes`
     */
    function buildLabels(nodes) {
        var counts = Object.create(null);
        var i;
        for (i = 0; i < nodes.length; i++) {
            var name = nodes[i].name;
            counts[name] = (counts[name] || 0) + 1;
        }
        var labels = [];
        for (i = 0; i < nodes.length; i++) {
            labels.push(
                counts[nodes[i].name] > 1
                    ? nodes[i].name + " (" + nodes[i].sub + ")"
                    : nodes[i].name
            );
        }
        return labels;
    }

    /**
     * Group a node's connections into the inspector panel's sections.
     *
     * Sections follow `subOrder` (supplied by the preprocessor, so sets lead and
     * story types run in reading order). Within a section the busiest node comes
     * first, ties broken by name so the order is stable. Any sub not named in
     * `subOrder` is appended after the known ones rather than dropped — a new
     * story type should look wrong, not vanish.
     *
     * @param {Array<{sub: string, degree: number, name: string}>} neighbours
     * @param {Array<string>} subOrder
     * @returns {Array<{sub: string, rows: Array}>} non-empty sections, in order
     */
    function groupConnections(neighbours, subOrder) {
        var buckets = Object.create(null);
        var order = [];
        var i;
        for (i = 0; i < subOrder.length; i++) {
            if (!(subOrder[i] in buckets)) {
                buckets[subOrder[i]] = [];
                order.push(subOrder[i]);
            }
        }
        for (i = 0; i < neighbours.length; i++) {
            var sub = neighbours[i].sub;
            if (!(sub in buckets)) {
                buckets[sub] = [];
                order.push(sub);
            }
            buckets[sub].push(neighbours[i]);
        }

        var sections = [];
        for (i = 0; i < order.length; i++) {
            var rows = buckets[order[i]];
            if (!rows.length) {
                continue;
            }
            rows.sort(function (a, b) {
                return b.degree - a.degree || String(a.name).localeCompare(String(b.name));
            });
            sections.push({ sub: order[i], rows: rows });
        }
        return sections;
    }

    /**
     * Points of a five-pointed star, ready to stroke as a closed path.
     *
     * The first point sits at the top (-90°). `outer` is the tip reach; the
     * caller scales it above the plain circle radius because a star of equal
     * radius carries well under half the ink, and heroes and regions must not
     * read as smaller than the characters and locations they outrank.
     *
     * @returns {Array<[number, number]>} ten points, tip and valley alternating
     */
    function starPoints(cx, cy, outer, innerRatio) {
        var points = [];
        for (var p = 0; p < 10; p++) {
            var reach = p % 2 === 0 ? outer : outer * innerRatio;
            var angle = (Math.PI / 5) * p - Math.PI / 2;
            points.push([cx + Math.cos(angle) * reach, cy + Math.sin(angle) * reach]);
        }
        return points;
    }

    /**
     * Find a node by its deep-link slug, tolerating a leading `#` and case.
     * Returns null rather than throwing on an unknown or empty slug, so a stale
     * shared link opens the graph rather than breaking it.
     */
    function findBySlug(nodes, hash) {
        var wanted = String(hash == null ? "" : hash)
            .replace(/^#/, "")
            .toLowerCase();
        if (!wanted) {
            return null;
        }
        for (var i = 0; i < nodes.length; i++) {
            if (nodes[i].slug === wanted) {
                return nodes[i];
            }
        }
        return null;
    }

    /**
     * True when two label boxes overlap. Used to drop the later of two colliding
     * canvas labels; candidates are visited busiest-first so the more connected
     * node keeps the space.
     */
    function boxesOverlap(a, b) {
        return a.x0 < b.x1 && a.x1 > b.x0 && a.y0 < b.y1 && a.y1 > b.y0;
    }

    var api = {
        escapeHtml: escapeHtml,
        nodeRadius: nodeRadius,
        buildLabels: buildLabels,
        groupConnections: groupConnections,
        starPoints: starPoints,
        findBySlug: findBySlug,
        boxesOverlap: boxesOverlap
    };

    if (typeof module !== "undefined" && module.exports) {
        module.exports = api;
    } else {
        root.fabloreGraphCore = api;
    }
})(typeof window !== "undefined" ? window : globalThis);
