(function () {
    var btn = document.getElementById('random-story-button');
    if (!btn) return;

    var cache = null;

    btn.addEventListener('click', function () {
        function navigate(data) {
            var current = window.location.pathname;
            var others = data.filter(function (s) { return !current.endsWith('/' + s.u); });
            var pool = others.length ? others : data;
            var story = pool[Math.floor(Math.random() * pool.length)];
            window.location.href = ((typeof path_to_root !== 'undefined' ? path_to_root : '')) + story.u;
        }
        if (cache) { navigate(cache); return; }
        fetch(((typeof path_to_root !== 'undefined' ? path_to_root : '')) + 'stories.json')
            .then(function (r) { return r.json(); })
            .then(function (data) { cache = data; navigate(data); })
            .catch(function (e) { console.error('random story:', e); });
    });
})();
