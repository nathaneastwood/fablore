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
     * Rank nodes for the narrow-viewport list, keeping only those whose name
     * contains `query`.
     *
     * Below the canvas breakpoint the list *is* the graph, so it has to answer
     * the question the map answers at a glance: what is most connected here.
     * That means the same sort key a panel section uses — busiest first, name to
     * break ties — so a node holds the same relative position in both views.
     *
     * The match is a substring, not a prefix, because a reader knows an epithet
     * rather than a full title: "dawn" has to find "Ser Boltyn, Breaker of Dawn".
     *
     * Returns a new array — the caller passes the live visible-node list, and
     * sorting that in place would reorder what the canvas draws.
     *
     * @param {Array<{name: string, degree: number}>} nodes
     * @param {string} query — empty or blank keeps every node
     * @returns {Array} matching nodes, busiest first
     */
    function rankNodes(nodes, query) {
        var q = String(query == null ? "" : query)
            .trim()
            .toLowerCase();
        var out = [];
        for (var i = 0; i < nodes.length; i++) {
            if (!q || String(nodes[i].name).toLowerCase().indexOf(q) !== -1) {
                out.push(nodes[i]);
            }
        }
        out.sort(function (a, b) {
            return (b.degree || 0) - (a.degree || 0) ||
                String(a.name).localeCompare(String(b.name));
        });
        return out;
    }

    /**
     * How many selections deep into the graph a history entry is.
     *
     * Every selection pushes an entry stamped with its own depth, so the panel's
     * back arrow can tell a walk it can retrace from the first entry, where the
     * only thing behind it is whatever page the reader came from. Anything that
     * is not a whole count this page wrote reads as zero: the entry may predate
     * the feature, or belong to another script, and `"2" + 1` is `"21"`, which
     * would stamp nonsense on every entry after it.
     *
     * @param {?Object} state — `history.state`, which is null far more often
     *     than not
     * @returns {number} depth, never negative
     */
    function historyDepth(state) {
        var depth = state ? state.fabloreGraph : 0;
        if (typeof depth !== "number" || !isFinite(depth) || depth < 0) {
            return 0;
        }
        return Math.floor(depth);
    }

    /**
     * Why is there nothing to show?
     *
     * A blank stage with no words on it reads as broken rather than as filtered.
     * Each way of emptying the graph has its own undo, so the message names the
     * one that applies rather than listing all of them. Order is by how recently
     * the reader did it, except that hiding stories comes with an explanation:
     * every edge in this graph is an appearance in a story, so removing stories
     * takes almost everything with it, which is not guessable from the outside.
     *
     * @param {{hasQuery: boolean, storyHidden: boolean, allKindsHidden: boolean,
     *          minDegree: number}} state
     * @returns {string} never empty
     */
    function emptyStateMessage(state) {
        var s = state || {};
        if (s.hasQuery) {
            return "Nothing matches that search. Try a shorter one, or clear it.";
        }
        if (s.allKindsHidden) {
            return "Every type is switched off. Turn one back on to see it.";
        }
        if (s.storyHidden) {
            var why =
                "Every line here is an appearance in a story, so with stories " +
                "hidden there is almost nothing left to join. ";
            // A dashed line runs only from a card to a set, so pointing at one
            // while every card type is switched off would send the reader
            // looking for something that cannot be there.
            return s.printedHidden
                ? why + "Turn Story back on, or turn on Hero, Weapon or Equipment to see the sets that printed them."
                : why + "Turn Story back on, or follow the dashed lines from a card to the set that printed it.";
        }
        var n = typeof s.minDegree === "number" && s.minDegree > 0 ? s.minDegree : 1;
        return (
            "Nothing here has " +
            n +
            (n === 1 ? " connection" : " connections") +
            " or more. Lower the minimum, or turn a type back on."
        );
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
        rankNodes: rankNodes,
        historyDepth: historyDepth,
        emptyStateMessage: emptyStateMessage,
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
