(function () {
    "use strict";

    // heroes is an array; type and region are single strings.
    var filters = { type: "", region: "", heroes: [] };

    // --- URL helpers ---

    function readParamsIntoFilters() {
        var params = new URLSearchParams(window.location.search);
        filters.type = params.get("type") || "";
        filters.region = params.get("region") || "";
        filters.heroes = params.getAll("hero").filter(Boolean);
    }

    function updateURL() {
        var params = new URLSearchParams();
        if (filters.type) { params.set("type", filters.type); }
        if (filters.region) { params.set("region", filters.region); }
        filters.heroes.forEach(function (h) { params.append("hero", h); });
        var q = params.toString();
        history.replaceState(null, "", q ? "?" + q : window.location.pathname);
    }

    // --- Filtering ---

    function matches(story) {
        if (filters.type && story.k !== filters.type) { return false; }
        if (filters.region && story.r.indexOf(filters.region) === -1) { return false; }
        if (filters.heroes.length > 0) {
            for (var i = 0; i < filters.heroes.length; i++) {
                if (story.h.indexOf(filters.heroes[i]) === -1) { return false; }
            }
        }
        return true;
    }

    // --- Results rendering ---

    function render() {
        var data = window.FABLORE_BROWSE;
        var list = document.getElementById("browse-results");
        var countEl = document.getElementById("browse-count");
        if (!list || !countEl || !data) { return; }

        var matched = data.stories.filter(matches);
        var total = data.stories.length;
        countEl.textContent = matched.length === total
            ? total + " stories"
            : matched.length + " of " + total + " stories";

        var frag = document.createDocumentFragment();
        for (var i = 0; i < matched.length; i++) {
            var s = matched[i];
            var li = document.createElement("li");
            li.className = "browse-item";

            var a = document.createElement("a");
            a.href = s.u;
            a.className = "browse-item-title";
            a.textContent = s.t;
            li.appendChild(a);

            var metaParts = [];
            var typeLabel = "";
            for (var j = 0; j < data.types.length; j++) {
                if (data.types[j].k === s.k) { typeLabel = data.types[j].l; break; }
            }
            if (typeLabel) { metaParts.push(typeLabel); }
            if (s.h.length) { metaParts.push(s.h.join(", ")); }
            if (s.r.length) { metaParts.push(s.r.join(", ")); }

            if (metaParts.length) {
                var span = document.createElement("span");
                span.className = "browse-item-meta";
                span.textContent = metaParts.join(" · ");
                li.appendChild(span);
            }

            frag.appendChild(li);
        }
        list.innerHTML = "";
        list.appendChild(frag);
    }

    // --- Pill filters (type & region) ---

    function buildPills(containerId, values, filterKey, labelFn) {
        var container = document.getElementById(containerId);
        if (!container) { return; }

        function makePill(value, label) {
            var btn = document.createElement("button");
            btn.className = "browse-pill" + (filters[filterKey] === value ? " active" : "");
            btn.setAttribute("data-value", value);
            btn.textContent = label;
            btn.addEventListener("click", function () {
                filters[filterKey] = value;
                var pills = container.querySelectorAll(".browse-pill");
                for (var i = 0; i < pills.length; i++) {
                    pills[i].classList.toggle("active", pills[i].getAttribute("data-value") === value);
                }
                updateURL();
                render();
            });
            return btn;
        }

        container.appendChild(makePill("", "All"));
        for (var i = 0; i < values.length; i++) {
            container.appendChild(makePill(values[i], labelFn ? labelFn(values[i]) : values[i]));
        }
    }

    // --- Hero multi-select widget ---

    function buildHeroWidget() {
        var data = window.FABLORE_BROWSE;
        var widget = document.getElementById("browse-hero-widget");
        var field = document.getElementById("browse-hero-field");
        var chipsEl = document.getElementById("browse-hero-chips");
        var input = document.getElementById("browse-hero-input");
        var dropdown = document.getElementById("browse-hero-dropdown");
        if (!widget || !field || !chipsEl || !input || !dropdown || !data) { return; }

        function isSelected(name) {
            return filters.heroes.indexOf(name) !== -1;
        }

        function renderChips() {
            chipsEl.innerHTML = "";
            filters.heroes.forEach(function (name) {
                var chip = document.createElement("span");
                chip.className = "browse-hero-chip";

                var label = document.createElement("span");
                label.textContent = name;
                chip.appendChild(label);

                var remove = document.createElement("button");
                remove.className = "browse-hero-chip-remove";
                remove.setAttribute("aria-label", "Remove " + name);
                remove.setAttribute("type", "button");
                remove.textContent = "×";
                remove.addEventListener("click", function (e) {
                    e.stopPropagation();
                    filters.heroes = filters.heroes.filter(function (h) { return h !== name; });
                    renderChips();
                    renderDropdown();
                    updateURL();
                    render();
                });
                chip.appendChild(remove);
                chipsEl.appendChild(chip);
            });
        }

        function renderDropdown() {
            var q = input.value.toLowerCase();
            var visible = data.heroes.filter(function (h) {
                return !isSelected(h) && (!q || h.toLowerCase().indexOf(q) !== -1);
            });

            dropdown.innerHTML = "";
            if (visible.length === 0) {
                dropdown.hidden = true;
                return;
            }

            visible.forEach(function (name) {
                var li = document.createElement("li");
                li.className = "browse-hero-option";
                li.textContent = name;
                li.addEventListener("mousedown", function (e) {
                    // mousedown fires before blur — prevent blur from hiding dropdown first
                    e.preventDefault();
                    filters.heroes.push(name);
                    input.value = "";
                    renderChips();
                    renderDropdown();
                    updateURL();
                    render();
                    input.focus();
                });
                dropdown.appendChild(li);
            });
            dropdown.hidden = false;
        }

        // Open dropdown on focus or click inside field
        field.addEventListener("click", function () {
            input.focus();
        });

        input.addEventListener("focus", function () {
            renderDropdown();
        });

        input.addEventListener("input", function () {
            renderDropdown();
        });

        input.addEventListener("keydown", function (e) {
            if (e.key === "Escape") {
                dropdown.hidden = true;
                input.blur();
            }
            // Backspace on empty input removes last chip
            if (e.key === "Backspace" && input.value === "" && filters.heroes.length > 0) {
                filters.heroes.pop();
                renderChips();
                renderDropdown();
                updateURL();
                render();
            }
        });

        // Close dropdown when clicking outside
        document.addEventListener("click", function (e) {
            if (!widget.contains(e.target)) {
                dropdown.hidden = true;
            }
        });

        // Render initial chips (from URL params)
        renderChips();
    }

    // --- Init ---

    function init() {
        var data = window.FABLORE_BROWSE;
        if (!data || !document.getElementById("browse-app")) { return; }

        readParamsIntoFilters();

        buildPills("browse-type-pills", data.types.map(function (t) { return t.k; }), "type", function (k) {
            for (var i = 0; i < data.types.length; i++) {
                if (data.types[i].k === k) { return data.types[i].l; }
            }
            return k;
        });
        buildPills("browse-region-pills", data.regions, "region", null);
        buildHeroWidget();
        render();
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
}());
