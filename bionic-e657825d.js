(function () {
    var STORAGE_KEY = 'bionic-reading';
    var originalContent = null;

    var SKIP_TAGS = ['code', 'pre', 'script', 'style', 'kbd', 'var', 'samp', 'b', 'strong'];

    function bionicWord(word) {
        var boldLen = Math.max(1, Math.ceil(word.length / 2));
        return '<b>' + word.slice(0, boldLen) + '</b>' + word.slice(boldLen);
    }

    function applyBionic(root) {
        originalContent = root.innerHTML;

        var walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
            acceptNode: function (node) {
                var p = node.parentNode;
                while (p && p !== root) {
                    if (SKIP_TAGS.indexOf(p.nodeName.toLowerCase()) !== -1) {
                        return NodeFilter.FILTER_REJECT;
                    }
                    p = p.parentNode;
                }
                return NodeFilter.FILTER_ACCEPT;
            }
        });

        var textNodes = [];
        while (walker.nextNode()) {
            textNodes.push(walker.currentNode);
        }

        textNodes.forEach(function (node) {
            var text = node.textContent;
            var replaced = text.replace(/[A-Za-zÀ-ɏ]+/g, bionicWord);
            if (replaced !== text) {
                var span = document.createElement('span');
                span.innerHTML = replaced;
                node.parentNode.replaceChild(span, node);
            }
        });
    }

    function removeBionic(root) {
        if (originalContent !== null) {
            root.innerHTML = originalContent;
            originalContent = null;
        }
    }

    function getContentRoot() {
        return document.querySelector('.content main') || document.querySelector('.content');
    }

    function updateButton(active) {
        var btn = document.getElementById('bionic-toggle');
        if (!btn) return;
        btn.setAttribute('aria-pressed', active ? 'true' : 'false');
        var label = active ? 'Disable Bionic Reading' : 'Enable Bionic Reading';
        btn.title = label;
        btn.setAttribute('aria-label', label);
    }

    function enable() {
        var root = getContentRoot();
        if (root) applyBionic(root);
        document.body.classList.add('bionic-reading');
        localStorage.setItem(STORAGE_KEY, '1');
        updateButton(true);
    }

    function disable() {
        var root = getContentRoot();
        if (root) removeBionic(root);
        document.body.classList.remove('bionic-reading');
        localStorage.removeItem(STORAGE_KEY);
        updateButton(false);
    }

    function showBionicHint(btn) {
        if (localStorage.getItem('bionic-hint-seen') === '1') return;
        if (typeof tippy !== 'function') return;

        localStorage.setItem('bionic-hint-seen', '1');
        document.body.classList.add('bionic-hint-active');

        var instance = tippy(btn, {
            content: '<strong>Bionic Reading</strong> — bold anchors help your eyes skip through text faster. Click to try it.',
            allowHTML: true,
            placement: 'bottom-start',
            trigger: 'manual',
            arrow: true,
            onHide: function () {
                document.body.classList.remove('bionic-hint-active');
            }
        });

        var hideTimer = setTimeout(function () { instance.hide(); }, 6000);

        setTimeout(function () { instance.show(); }, 1200);

        btn.addEventListener('click', function () {
            clearTimeout(hideTimer);
            instance.hide();
        }, { once: true });
    }

    document.addEventListener('DOMContentLoaded', function () {
        var btn = document.getElementById('bionic-toggle');
        if (!btn) return;

        var isEnabled = localStorage.getItem(STORAGE_KEY) === '1';
        if (isEnabled) {
            enable();
        } else {
            updateButton(false);
        }

        btn.addEventListener('click', function () {
            if (document.body.classList.contains('bionic-reading')) {
                disable();
            } else {
                enable();
            }
        });

        showBionicHint(btn);
    });
})();
