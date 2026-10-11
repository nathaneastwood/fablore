/**
 * Reading mode for story chapters.
 *
 * The inline script in index.hbs decides whether a page is a story chapter
 * (main-story/ or short-stories/, not a hub index) and whether reading mode is
 * on — it is the default unless the reader switched it off — and sets the
 * `is-story-page` / `reading-mode` classes before first paint. This script
 * wires up the rest: the toolbar toggle, a one-off hint explaining the mode,
 * a "listen" chip near the top when a narration exists, the drop cap, and a
 * floating previous / progress / next pill. Archive pages are untouched.
 *
 * State lives in localStorage under 'fablore-reading-mode' ('on' / 'off').
 */
(function () {
    'use strict';

    var STORAGE_KEY = 'fablore-reading-mode';
    var HINT_KEY = 'fablore-reading-mode-hint-seen';
    var html = document.documentElement;
    var main = document.querySelector('#mdbook-content main');
    var toggle = document.getElementById('reading-mode-toggle');
    if (!main || !toggle || !html.classList.contains('is-story-page')) return;

    function stored(key) {
        try { return localStorage.getItem(key); } catch (e) { return null; }
    }
    function store(key, v) {
        try { localStorage.setItem(key, v); } catch (e) { /* ignore */ }
    }

    toggle.hidden = false;

    // --- "Listen" chip under the byline, when a narration exists ---
    var narration = main.querySelector('.narrated-videos');
    if (narration) {
        if (!narration.id) narration.id = 'narration';
        var narrators = narration.querySelectorAll('.nv-tab').length;
        var chip = document.createElement('a');
        chip.className = 'rm-listen';
        chip.href = '#' + narration.id;
        chip.innerHTML = '<i class="fa fa-headphones" aria-hidden="true"></i> Listen to this story' +
            (narrators > 1 ? ' <span class="rm-listen-by">· ' + narrators + ' narrations</span>' : '');
        var card = main.querySelector('.story-card');
        if (card) card.appendChild(chip);
    }

    // --- Mark the opening paragraph for the drop cap ---
    var firstPara = Array.prototype.find.call(main.querySelectorAll(':scope > p'), function (p) {
        return p.textContent.trim().length > 80;  // hint tooltips carry imgs, so test text only
    });
    if (firstPara) firstPara.classList.add('rm-opening');

    // --- Floating previous / progress / next pill ---
    var prev = document.querySelector('.nav-chapters.previous, .mobile-nav-chapters.previous');
    var next = document.querySelector('.nav-chapters.next, .mobile-nav-chapters.next');

    function chapterTitle(link) {
        if (!link) return '';
        var target = link.getAttribute('href').split('#')[0].replace(/^(\.\.\/)+/, '');
        var hit = Array.prototype.find.call(document.querySelectorAll('#mdbook-sidebar a[href]'), function (a) {
            return a.getAttribute('href').replace(/^(\.\.\/)+/, '').split('#')[0] === target;
        });
        return hit ? hit.textContent.replace(/^\s*[\d.]+\s*/, '').trim() : '';
    }

    var pill = document.createElement('nav');
    pill.className = 'rm-pill';
    pill.setAttribute('aria-label', 'Story navigation');
    pill.innerHTML =
        (prev ? '<a class="rm-pill-prev" rel="prev" href="' + prev.getAttribute('href') + '">' +
            '<i class="fa fa-angle-left" aria-hidden="true"></i><span class="rm-pill-label"></span></a>' : '<span></span>') +
        '<span class="rm-pill-progress"><span class="rm-pill-bar"><span></span></span><span class="rm-pill-left"></span></span>' +
        (next ? '<a class="rm-pill-next" rel="next" href="' + next.getAttribute('href') + '">' +
            '<span class="rm-pill-label"></span><i class="fa fa-angle-right" aria-hidden="true"></i></a>' : '<span></span>');
    document.body.appendChild(pill);

    function fillTitles() {
        var p = pill.querySelector('.rm-pill-prev .rm-pill-label');
        var n = pill.querySelector('.rm-pill-next .rm-pill-label');
        if (p) p.textContent = chapterTitle(prev) || 'Previous';
        if (n) n.textContent = chapterTitle(next) || 'Next';
    }
    fillTitles();
    window.addEventListener('load', fillTitles);  // sidebar is filled in by toc.js

    var minutes = 0;
    var clock = main.querySelector('.story-meta-item:last-child');
    var m = clock && clock.textContent.match(/(\d+)\s*min read/);
    if (m) minutes = parseInt(m[1], 10);

    var bar = pill.querySelector('.rm-pill-bar span');
    var left = pill.querySelector('.rm-pill-left');
    var lastY = window.scrollY;
    function onScroll() {
        // Progress through the story text, not the whole page (related cards etc.)
        var end = (narration || main.querySelector('.related-section') || main).getBoundingClientRect().top + window.scrollY;
        var span = Math.max(1, end - window.innerHeight);
        var frac = Math.max(0, Math.min(1, window.scrollY / span));
        bar.style.width = (frac * 100) + '%';
        left.textContent = frac >= 0.99 ? 'The end' :
            minutes ? Math.max(1, Math.round(minutes * (1 - frac))) + ' min left' : Math.round(frac * 100) + '%';
        var y = window.scrollY;
        pill.classList.toggle('rm-pill--hidden', y > lastY + 4 && frac < 0.97 && y > 200);
        if (Math.abs(y - lastY) > 4) lastY = y;
    }
    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', onScroll, { passive: true });

    // --- Mode switching ---
    var sidebarAnchor = document.getElementById('mdbook-sidebar-toggle-anchor');
    var sidebar = document.getElementById('mdbook-sidebar');

    function collapseSidebar() {
        // mdBook's own hideSidebar() would persist 'hidden' to localStorage and
        // follow the reader back into archive pages; this only collapses it here.
        if (!sidebarAnchor || !sidebarAnchor.checked) return;
        sidebarAnchor.checked = false;
        html.classList.remove('sidebar-visible');
        if (sidebar) {
            sidebar.setAttribute('aria-hidden', 'true');
            sidebar.style.display = 'none';
        }
    }

    function expandSidebar() {
        // Leaving reading mode means "show me the archive", sidebar included —
        // but only where mdBook would show it beside the page, not over it.
        if (!sidebarAnchor || sidebarAnchor.checked || document.body.clientWidth < 1080) return;
        if (sidebar) {
            sidebar.style.display = '';
            sidebar.offsetHeight;  // reflow so the slide-in animates (mdBook does the same)
            sidebar.setAttribute('aria-hidden', 'false');
        }
        sidebarAnchor.checked = true;
        html.classList.add('sidebar-visible');
    }

    function apply(on) {
        html.classList.toggle('reading-mode', on);
        toggle.setAttribute('aria-pressed', on ? 'true' : 'false');
        toggle.title = on ? 'Switch to archive view' : 'Switch to reading mode';
        toggle.setAttribute('aria-label', toggle.title);
        if (on) collapseSidebar();
        onScroll();
    }

    toggle.addEventListener('click', function () {
        var on = !html.classList.contains('reading-mode');
        store(STORAGE_KEY, on ? 'on' : 'off');
        apply(on);
        if (!on) expandSidebar();
    });

    apply(html.classList.contains('reading-mode'));

    // --- One-off hint, the first time a reader lands in reading mode ---
    function showHint() {
        if (stored(HINT_KEY) === '1' || typeof tippy !== 'function') return;
        if (!html.classList.contains('reading-mode')) return;
        store(HINT_KEY, '1');
        document.body.classList.add('reading-mode-hint-active');

        var instance = tippy(toggle, {
            content: '<strong>Reading mode</strong> — a quieter layout for stories. ' +
                'Click the book to switch back to the full archive view.',
            allowHTML: true,
            placement: 'bottom-end',
            trigger: 'manual',
            arrow: true,
            onHide: function () {
                document.body.classList.remove('reading-mode-hint-active');
            }
        });
        var hideTimer = setTimeout(function () { instance.hide(); }, 8000);
        instance.show();
        toggle.addEventListener('click', function () {
            clearTimeout(hideTimer);
            instance.hide();
        }, { once: true });
    }

    // bionic.js shows its own first-visit hint at 1.2s for 6s; wait our turn.
    window.addEventListener('load', function () {
        var bionicShowing = document.body.classList.contains('bionic-hint-active');
        setTimeout(showHint, bionicShowing ? 7000 : 1200);
    });
})();
