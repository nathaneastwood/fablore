(function () {
    // Button lives in index.hbs so its icons match the template's print/git SVGs.
    var btn = document.getElementById('copy-link-button');
    if (!btn) return;

    btn.addEventListener('click', function () {
        navigator.clipboard.writeText(window.location.href).then(function () {
            btn.title = 'Copied!';
            btn.setAttribute('aria-label', 'Copied!');
            btn.classList.add('copy-link-button--done');
            setTimeout(function () {
                btn.title = 'Copy link to this page';
                btn.setAttribute('aria-label', 'Copy link to this page');
                btn.classList.remove('copy-link-button--done');
            }, 2000);
        });
    });
})();
