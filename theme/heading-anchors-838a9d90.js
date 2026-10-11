(function () {
    var content = document.getElementById('mdbook-content');
    if (!content) return;

    content.querySelectorAll('h2[id], h3[id], h4[id]').forEach(function (h) {
        var a = document.createElement('a');
        a.className = 'heading-anchor';
        a.href = '#' + h.id;
        a.setAttribute('aria-label', 'Link to this section');
        a.setAttribute('title', 'Copy link to this section');
        a.innerHTML = '<i class="fa fa-link" aria-hidden="true"></i>';
        a.addEventListener('click', function () {
            var url = window.location.href.split('#')[0] + '#' + h.id;
            navigator.clipboard.writeText(url).then(function () {
                a.classList.add('heading-anchor--copied');
                setTimeout(function () {
                    a.classList.remove('heading-anchor--copied');
                }, 1500);
            });
        });
        h.appendChild(a);
    });
})();
