/**
 * Floating “back to top” control (paired with .back-to-top in image.css).
 * Respects prefers-reduced-motion for scroll behaviour.
 */
(function () {
    var btn = document.getElementById('back-to-top');
    if (!btn) {
        return;
    }

    var root = document.scrollingElement || document.documentElement;
    var threshold = 400;

    function applyVisibility() {
        var visible = root.scrollTop >= threshold;
        btn.classList.toggle('back-to-top--visible', visible);
        btn.setAttribute('aria-hidden', visible ? 'false' : 'true');
        btn.tabIndex = visible ? 0 : -1;
    }

    window.addEventListener('scroll', applyVisibility, { passive: true });
    applyVisibility();

    btn.addEventListener('click', function () {
        var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        root.scrollTo({
            top: 0,
            behavior: reduceMotion ? 'auto' : 'smooth',
        });
    });
})();

// Cmd+K / Ctrl+K opens search (alias for the built-in S shortcut).
document.addEventListener('keydown', function (e) {
    if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        var toggle = document.getElementById('search-toggle');
        if (toggle) {
            e.preventDefault();
            toggle.click();
        }
    }
});
