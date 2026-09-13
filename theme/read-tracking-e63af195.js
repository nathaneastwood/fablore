(function () {
    var STORAGE_KEY = 'fablore-read';
    // mdBook 0.5.3 uses chapter-fold-toggle (not the old a.toggle from 0.4.x)
    var FOLD_TOGGLE = 'a.chapter-fold-toggle';

    function getRead() {
        try { return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]'); }
        catch (e) { return []; }
    }

    var path    = window.location.pathname;
    var read    = getRead();
    var marked  = read.indexOf(path) !== -1;

    // Whether this page is eligible for tracking. Starts unknown (null) because
    // isSectionHeader can only be determined once the sidebar is populated (async).
    var trackingEnabled = null;
    // True if the sentinel was crossed before we knew trackingEnabled.
    var pendingMark = false;

    function doMarkRead(currentLink) {
        if (marked) return;
        marked = true;
        read.push(path);
        try { localStorage.setItem(STORAGE_KEY, JSON.stringify(read)); } catch (e) {}
        if (currentLink) currentLink.classList.add('fablore-read');
    }

    // Set up the scroll sentinel immediately so we don't miss a fast read.
    // Actual marking is gated on trackingEnabled once the sidebar is ready.
    var sentinelCurrentLink = null;  // filled in by applyToSidebar
    if (!marked && document.querySelector('.story-share')) {
        var main = document.querySelector('#mdbook-content main');
        if (main) {
            var sentinel = document.createElement('div');
            sentinel.style.height = '1px';
            sentinel.setAttribute('aria-hidden', 'true');
            var supplementary = main.querySelector('.related-section, .narrated-videos');
            if (supplementary) {
                main.insertBefore(sentinel, supplementary);
            } else {
                main.appendChild(sentinel);
            }
            new IntersectionObserver(function (entries, obs) {
                if (entries[0].isIntersecting) {
                    if (trackingEnabled === true) {
                        doMarkRead(sentinelCurrentLink);
                    } else if (trackingEnabled === null) {
                        pendingMark = true;  // sidebar not ready yet — defer
                    }
                    obs.disconnect();
                }
            }, { threshold: 1.0 }).observe(sentinel);
        }
    }

    // Called once the sidebar contains links. Determines isSectionHeader,
    // marks already-read links, and flushes any pending mark.
    function applyToSidebar() {
        var currentLink = null;
        document.querySelectorAll('#mdbook-sidebar a[href]').forEach(function (a) {
            try {
                var linkPath = new URL(a.href).pathname;
                if (read.indexOf(linkPath) !== -1) a.classList.add('fablore-read');
                if (linkPath === path) currentLink = a;
            } catch (e) {}
        });

        sentinelCurrentLink = currentLink;

        // A section header page has a fold-toggle button in the same
        // chapter-link-wrapper span as the chapter link.
        var isSectionHeader = currentLink &&
            currentLink.parentElement &&
            currentLink.parentElement.querySelector(FOLD_TOGGLE);

        trackingEnabled = !!document.querySelector('.story-share') && !isSectionHeader;

        if (marked && currentLink) {
            currentLink.classList.add('fablore-read');
        } else if (pendingMark && trackingEnabled) {
            doMarkRead(currentLink);
        }
    }

    // The sidebar is populated async (toc.js fetches toc.html). Use a
    // MutationObserver so we act as soon as links appear — no polling.
    var sidebar = document.getElementById('mdbook-sidebar');
    if (!sidebar) return;

    if (sidebar.querySelector('a[href]')) {
        applyToSidebar();
    } else {
        var obs = new MutationObserver(function (mutations, self) {
            if (sidebar.querySelector('a[href]')) {
                self.disconnect();
                applyToSidebar();
            }
        });
        obs.observe(sidebar, { childList: true, subtree: true });
    }
})();
