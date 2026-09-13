(function () {
    var btn = document.getElementById('copy-link-button');
    if (!btn) return;

    btn.addEventListener('click', function () {
        navigator.clipboard.writeText(window.location.href).then(function () {
            var icon = btn.querySelector('.fa');
            btn.title = 'Copied!';
            btn.setAttribute('aria-label', 'Copied!');
            if (icon) { icon.classList.replace('fa-link', 'fa-check'); }
            setTimeout(function () {
                btn.title = 'Copy link to this page';
                btn.setAttribute('aria-label', 'Copy link to this page');
                if (icon) { icon.classList.replace('fa-check', 'fa-link'); }
            }, 2000);
        });
    });
})();
