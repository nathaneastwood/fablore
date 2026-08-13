const test = require("node:test");
const assert = require("node:assert/strict");
const {
  escapeHtml,
  nodeRadius,
  buildLabels,
  groupConnections,
  rankNodes,
  starPoints,
  findBySlug,
  boxesOverlap
} = require("../../theme/graph-core.js");

// ── escapeHtml ───────────────────────────────────────────────────────────────
// Node names come from the lore CSVs and land in innerHTML. Arakni's card names
// carry punctuation ("5l!p3d 7hru 7h3 Cr4x"), and titles carry apostrophes.

test("escapeHtml: escapes every character that could break out of markup", () => {
  assert.equal(escapeHtml(`<a href="x">&'`), "&lt;a href=&quot;x&quot;&gt;&amp;&#39;");
});

test("escapeHtml: leaves ordinary lore names alone", () => {
  assert.equal(escapeHtml("Arakni, 5l!p3d 7hru 7h3 Cr4x"), "Arakni, 5l!p3d 7hru 7h3 Cr4x");
});

test("escapeHtml: escapes the ampersand before the entities it introduces", () => {
  assert.equal(escapeHtml("Food & Drink"), "Food &amp; Drink");
  assert.equal(escapeHtml("&lt;"), "&amp;lt;");
});

test("escapeHtml: coerces non-strings instead of throwing", () => {
  assert.equal(escapeHtml(42), "42");
  assert.equal(escapeHtml(null), "null");
});

// ── nodeRadius ───────────────────────────────────────────────────────────────

test("nodeRadius: grows with connection count", () => {
  assert.ok(nodeRadius(40) > nodeRadius(10));
  assert.ok(nodeRadius(10) > nodeRadius(1));
});

test("nodeRadius: grows sub-linearly, so a hub does not swamp a leaf", () => {
  // 40 connections is 40x the count but must be nowhere near 40x the radius.
  assert.ok(nodeRadius(40) < nodeRadius(1) * 4);
});

test("nodeRadius: a zero-degree or missing degree still has a visible radius", () => {
  assert.ok(nodeRadius(0) > 0);
  assert.ok(nodeRadius(undefined) > 0);
  assert.ok(nodeRadius(-5) > 0, "a negative degree must not produce NaN");
});

// ── buildLabels ──────────────────────────────────────────────────────────────
// A set, its flavour page and its digital tiles all share one name. On the
// canvas they are told apart by colour alone, so repeats carry their type.

test("buildLabels: a unique name is left bare", () => {
  assert.deepEqual(buildLabels([{ name: "Dorinthea", sub: "Hero" }]), ["Dorinthea"]);
});

test("buildLabels: a repeated name takes its type", () => {
  const labels = buildLabels([
    { name: "Bright Lights", sub: "Set" },
    { name: "Bright Lights", sub: "Flavour Text" },
    { name: "Dorinthea", sub: "Hero" }
  ]);
  assert.deepEqual(labels, [
    "Bright Lights (Set)",
    "Bright Lights (Flavour Text)",
    "Dorinthea"
  ]);
});

test("buildLabels: every copy of a repeated name is suffixed, not just the later ones", () => {
  const labels = buildLabels([
    { name: "Aria", sub: "Region" },
    { name: "Aria", sub: "World of Rathe" }
  ]);
  assert.ok(labels.every((l) => l.includes("(")));
});

test("buildLabels: returns one label per node, positionally", () => {
  const nodes = [
    { name: "A", sub: "Hero" },
    { name: "B", sub: "Set" },
    { name: "A", sub: "Set" }
  ];
  assert.equal(buildLabels(nodes).length, nodes.length);
});

test("buildLabels: an empty list is answered, not thrown on", () => {
  assert.deepEqual(buildLabels([]), []);
});

// ── groupConnections ─────────────────────────────────────────────────────────

const SUB_ORDER = ["Set", "Main Story", "Short Story", "Hero", "Character"];

test("groupConnections: sections follow the given order, not the input order", () => {
  const sections = groupConnections(
    [
      { name: "c", sub: "Character", degree: 1 },
      { name: "s", sub: "Set", degree: 1 },
      { name: "m", sub: "Main Story", degree: 1 }
    ],
    SUB_ORDER
  );
  assert.deepEqual(
    sections.map((s) => s.sub),
    ["Set", "Main Story", "Character"]
  );
});

test("groupConnections: rows inside a section are busiest first", () => {
  const sections = groupConnections(
    [
      { name: "quiet", sub: "Main Story", degree: 2 },
      { name: "busy", sub: "Main Story", degree: 26 },
      { name: "middling", sub: "Main Story", degree: 9 }
    ],
    SUB_ORDER
  );
  assert.deepEqual(
    sections[0].rows.map((r) => r.name),
    ["busy", "middling", "quiet"]
  );
});

test("groupConnections: equal counts fall back to name, so the order is stable", () => {
  const sections = groupConnections(
    [
      { name: "Zyggy", sub: "Hero", degree: 3 },
      { name: "Astrea", sub: "Hero", degree: 3 }
    ],
    SUB_ORDER
  );
  assert.deepEqual(
    sections[0].rows.map((r) => r.name),
    ["Astrea", "Zyggy"]
  );
});

test("groupConnections: empty sections are omitted", () => {
  const sections = groupConnections([{ name: "s", sub: "Set", degree: 1 }], SUB_ORDER);
  assert.deepEqual(
    sections.map((s) => s.sub),
    ["Set"]
  );
});

test("groupConnections: an unknown type is appended, never dropped", () => {
  // A new story type must look wrong rather than silently vanish from the panel.
  const sections = groupConnections(
    [
      { name: "x", sub: "Spoiler", degree: 1 },
      { name: "s", sub: "Set", degree: 1 }
    ],
    SUB_ORDER
  );
  assert.deepEqual(
    sections.map((s) => s.sub),
    ["Set", "Spoiler"]
  );
});

test("groupConnections: every input row survives into exactly one section", () => {
  const rows = [
    { name: "a", sub: "Set", degree: 1 },
    { name: "b", sub: "Main Story", degree: 5 },
    { name: "c", sub: "Main Story", degree: 2 },
    { name: "d", sub: "Unknown Type", degree: 1 }
  ];
  const sections = groupConnections(rows, SUB_ORDER);
  const total = sections.reduce((n, s) => n + s.rows.length, 0);
  assert.equal(total, rows.length, "section counts must sum to the header total");
});

// ── rankNodes ────────────────────────────────────────────────────────────────
// The narrow-viewport list replaces the canvas with a ranked run of nodes. It
// sorts on the same key as a panel section — busiest first, name to break ties —
// so a node holds the same relative position in both views.

test("rankNodes: busiest first", () => {
  const ranked = rankNodes(
    [
      { name: "quiet", degree: 2 },
      { name: "busy", degree: 46 },
      { name: "middling", degree: 9 }
    ],
    ""
  );
  assert.deepEqual(
    ranked.map((n) => n.name),
    ["busy", "middling", "quiet"]
  );
});

test("rankNodes: equal counts fall back to name, so the order is stable", () => {
  const ranked = rankNodes(
    [
      { name: "Zyggy", degree: 3 },
      { name: "Astrea", degree: 3 }
    ],
    ""
  );
  assert.deepEqual(
    ranked.map((n) => n.name),
    ["Astrea", "Zyggy"]
  );
});

test("rankNodes: an empty query keeps every node", () => {
  const nodes = [
    { name: "Dorinthea", degree: 4 },
    { name: "Bravo", degree: 2 }
  ];
  assert.equal(rankNodes(nodes, "").length, 2);
  assert.equal(rankNodes(nodes, "   ").length, 2);
  assert.equal(rankNodes(nodes, null).length, 2);
  assert.equal(rankNodes(nodes, undefined).length, 2);
});

test("rankNodes: the query matches anywhere in the name, not just the start", () => {
  // "Ser Boltyn, Breaker of Dawn" has to be reachable by typing "boltyn" or
  // "dawn" — a reader searching this archive knows an epithet, not a full title.
  const nodes = [
    { name: "Ser Boltyn, Breaker of Dawn", degree: 8 },
    { name: "Dorinthea", degree: 4 }
  ];
  assert.deepEqual(
    rankNodes(nodes, "dawn").map((n) => n.name),
    ["Ser Boltyn, Breaker of Dawn"]
  );
});

test("rankNodes: the query ignores case and surrounding space", () => {
  const nodes = [{ name: "Dorinthea", degree: 4 }];
  assert.equal(rankNodes(nodes, "DORIN").length, 1);
  assert.equal(rankNodes(nodes, "  dorin  ").length, 1);
});

test("rankNodes: a query matching nothing yields an empty list, not everything", () => {
  assert.deepEqual(rankNodes([{ name: "Dorinthea", degree: 4 }], "zzzz"), []);
});

test("rankNodes: does not mutate or alias the array it was given", () => {
  // It is called with the live `active` array on every keystroke. Sorting that
  // in place would quietly reorder what the canvas draws and what the filters
  // recompute from.
  const nodes = [
    { name: "quiet", degree: 2 },
    { name: "busy", degree: 46 }
  ];
  const ranked = rankNodes(nodes, "");
  assert.deepEqual(
    nodes.map((n) => n.name),
    ["quiet", "busy"],
    "the caller's order must survive"
  );
  assert.notEqual(ranked, nodes);
});

test("rankNodes: a missing degree sorts last rather than producing NaN", () => {
  const ranked = rankNodes([{ name: "a" }, { name: "b", degree: 3 }], "");
  assert.deepEqual(
    ranked.map((n) => n.name),
    ["b", "a"]
  );
});

test("rankNodes: no nodes yields no rows", () => {
  assert.deepEqual(rankNodes([], ""), []);
});

test("groupConnections: no connections yields no sections", () => {
  assert.deepEqual(groupConnections([], SUB_ORDER), []);
});

// ── starPoints ───────────────────────────────────────────────────────────────

test("starPoints: returns ten points, tip and valley alternating", () => {
  const pts = starPoints(0, 0, 10, 0.46);
  assert.equal(pts.length, 10);
  const reach = (p) => Math.hypot(p[0], p[1]);
  assert.ok(Math.abs(reach(pts[0]) - 10) < 1e-9, "even indices are tips");
  assert.ok(Math.abs(reach(pts[1]) - 4.6) < 1e-9, "odd indices are valleys");
});

test("starPoints: the first point sits at the top", () => {
  const [x, y] = starPoints(0, 0, 10, 0.46)[0];
  assert.ok(Math.abs(x) < 1e-9);
  assert.ok(Math.abs(y + 10) < 1e-9, "canvas y grows downward, so the top is -r");
});

test("starPoints: is centred on the point it is given", () => {
  const pts = starPoints(100, 50, 10, 0.46);
  const cx = pts.reduce((n, p) => n + p[0], 0) / pts.length;
  const cy = pts.reduce((n, p) => n + p[1], 0) / pts.length;
  assert.ok(Math.abs(cx - 100) < 1e-9);
  assert.ok(Math.abs(cy - 50) < 1e-9);
});

test("starPoints: never reaches beyond the outer radius", () => {
  // Labels and hit tests are placed from that radius; a stray point would poke
  // through the label above it.
  for (const p of starPoints(0, 0, 10, 0.46)) {
    assert.ok(Math.hypot(p[0], p[1]) <= 10 + 1e-9);
  }
});

// ── findBySlug ───────────────────────────────────────────────────────────────

const NODES = [
  { name: "Dorinthea", slug: "dorinthea" },
  { name: "Aria", slug: "aria-region" }
];

test("findBySlug: finds a node by its slug", () => {
  assert.equal(findBySlug(NODES, "dorinthea").name, "Dorinthea");
});

test("findBySlug: tolerates the leading hash a location.hash carries", () => {
  assert.equal(findBySlug(NODES, "#aria-region").name, "Aria");
});

test("findBySlug: is case-insensitive, since URLs get retyped by hand", () => {
  assert.equal(findBySlug(NODES, "#Aria-Region").name, "Aria");
});

test("findBySlug: an unknown slug returns null rather than throwing", () => {
  // A stale shared link must still open the graph.
  assert.equal(findBySlug(NODES, "#no-such-node"), null);
});

test("findBySlug: an empty, bare-hash, null or undefined hash selects nothing", () => {
  assert.equal(findBySlug(NODES, ""), null);
  assert.equal(findBySlug(NODES, "#"), null);
  assert.equal(findBySlug(NODES, null), null);
  assert.equal(findBySlug(NODES, undefined), null);
});

// ── boxesOverlap ─────────────────────────────────────────────────────────────

const box = (x0, y0, x1, y1) => ({ x0, y0, x1, y1 });

test("boxesOverlap: true when two label boxes intersect", () => {
  assert.equal(boxesOverlap(box(0, 0, 10, 10), box(5, 5, 15, 15)), true);
});

test("boxesOverlap: false when they are clear of each other", () => {
  assert.equal(boxesOverlap(box(0, 0, 10, 10), box(20, 0, 30, 10)), false);
  assert.equal(boxesOverlap(box(0, 0, 10, 10), box(0, 20, 10, 30)), false);
});

test("boxesOverlap: touching edges do not count as a collision", () => {
  // Labels sitting exactly side by side are readable; treating that as a clash
  // would drop one for no reason.
  assert.equal(boxesOverlap(box(0, 0, 10, 10), box(10, 0, 20, 10)), false);
});

test("boxesOverlap: a box fully inside another overlaps", () => {
  assert.equal(boxesOverlap(box(0, 0, 100, 100), box(10, 10, 20, 20)), true);
});
