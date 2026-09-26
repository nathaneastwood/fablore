(function () {
    var VALID_SCALES = ['0.875', '1', '1.175'];
    var VALID_WIDTHS = ['560px', '750px', '980px'];
    var html = document.documentElement;

    var toggleBtn = document.getElementById('accessibility-toggle');
    var popup     = document.getElementById('accessibility-menu');
    if (!toggleBtn || !popup) return;

    function showPopup() {
        popup.style.display = 'block';
        toggleBtn.setAttribute('aria-expanded', 'true');
    }
    function hidePopup() {
        popup.style.display = 'none';
        toggleBtn.setAttribute('aria-expanded', 'false');
        toggleBtn.focus();
    }

    toggleBtn.addEventListener('click', function () {
        popup.style.display === 'block' ? hidePopup() : showPopup();
    });
    document.addEventListener('click', function (e) {
        if (popup.style.display === 'block' &&
            !toggleBtn.contains(e.target) && !popup.contains(e.target)) {
            hidePopup();
        }
    });
    popup.addEventListener('focusout', function (e) {
        if (e.relatedTarget &&
            !toggleBtn.contains(e.relatedTarget) && !popup.contains(e.relatedTarget)) {
            hidePopup();
        }
    });
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && popup.style.display === 'block') {
            e.preventDefault();
            hidePopup();
        }
    });

    function getStored(key, validSet, def) {
        try { var v = localStorage.getItem(key); if (v && validSet.indexOf(v) !== -1) return v; }
        catch (e) {}
        return def;
    }

    function applyScale(val) {
        if (val === '1') { html.style.removeProperty('--fablore-font-scale'); }
        else             { html.style.setProperty('--fablore-font-scale', val); }
        try {
            val === '1'
                ? localStorage.removeItem('fablore-font-scale')
                : localStorage.setItem('fablore-font-scale', val);
        } catch (e) {}
    }
    function applyWidth(val) {
        if (val === '750px') { html.style.removeProperty('--content-max-width'); }
        else                 { html.style.setProperty('--content-max-width', val); }
        try {
            val === '750px'
                ? localStorage.removeItem('fablore-line-width')
                : localStorage.setItem('fablore-line-width', val);
        } catch (e) {}
    }

    function updateSelected() {
        var curScale = getStored('fablore-font-scale', VALID_SCALES, '1');
        var curWidth = getStored('fablore-line-width', VALID_WIDTHS, '750px');
        popup.querySelectorAll('.font-size-choice').forEach(function (btn) {
            btn.classList.toggle('accessibility-selected', btn.dataset.scale === curScale);
        });
        popup.querySelectorAll('.width-choice').forEach(function (btn) {
            btn.classList.toggle('accessibility-selected', btn.dataset.width === curWidth);
        });
    }

    popup.querySelectorAll('.font-size-choice').forEach(function (btn) {
        btn.addEventListener('click', function () { applyScale(btn.dataset.scale); updateSelected(); });
    });
    popup.querySelectorAll('.width-choice').forEach(function (btn) {
        btn.addEventListener('click', function () { applyWidth(btn.dataset.width); updateSelected(); });
    });

    updateSelected();
})();
