(function () {
    var bar  = document.getElementById('reading-progress-bar');
    var fill = document.getElementById('reading-progress-fill');
    var menu = document.getElementById('mdbook-menu-bar');
    if (!bar || !fill || !menu) return;

    function update() {
        var scrolled = window.scrollY || document.documentElement.scrollTop;
        var total = document.documentElement.scrollHeight - window.innerHeight;
        fill.style.width = (total > 0 ? Math.min(100, (scrolled / total) * 100) : 0) + '%';
        var rect = menu.getBoundingClientRect();
        bar.style.top   = Math.max(0, rect.bottom) + 'px';
        bar.style.left  = rect.left + 'px';
        bar.style.width = rect.width + 'px';
    }

    window.addEventListener('scroll', update, { passive: true });
    window.addEventListener('resize', update, { passive: true });
    update();
})();
