/*
 * Click-to-expand for story images. A zoomable image opens in a
 * full-viewport <dialog>; click anywhere, press Escape, or use the close
 * button to dismiss. Only images the page shrinks below their natural size
 * are zoomable — expanding one already shown at full size would add nothing.
 * Images inside links or buttons keep their own behaviour. Add `no-zoom` to an
 * image, or to any ancestor, to opt it out.
 */
(function () {
    var main = document.querySelector('#mdbook-content main');
    if (!main || typeof HTMLDialogElement === 'undefined') return;

    // Natural width must exceed rendered width by this factor to be worth expanding.
    var MIN_GAIN = 1.15;
    var SKIP = 'a, button, .no-zoom, .intro-landing-logo, .world-hub-card';

    var dialog = null;
    var full = null;
    var caption = null;

    function build() {
        dialog = document.createElement('dialog');
        dialog.className = 'lightbox';
        dialog.setAttribute('aria-label', 'Expanded image');

        var close = document.createElement('button');
        close.type = 'button';
        close.className = 'lightbox-close';
        close.setAttribute('aria-label', 'Close image');
        close.innerHTML = '<i class="fa fa-times" aria-hidden="true"></i>';

        full = document.createElement('img');
        full.className = 'lightbox-image';

        caption = document.createElement('p');
        caption.className = 'lightbox-caption';

        dialog.appendChild(close);
        dialog.appendChild(full);
        dialog.appendChild(caption);
        document.body.appendChild(dialog);

        // Any click inside the dialog — image, backdrop or button — closes it.
        dialog.addEventListener('click', function () { dialog.close(); });
        dialog.addEventListener('close', function () {
            document.documentElement.classList.remove('lightbox-open');
            full.removeAttribute('src');
        });
    }

    function zoomable(img) {
        if (img.closest(SKIP)) return false;
        var shown = img.getBoundingClientRect().width;
        return shown > 0 && img.naturalWidth >= shown * MIN_GAIN;
    }

    function open(img) {
        if (!dialog) build();
        full.src = img.currentSrc || img.src;
        full.alt = img.alt || '';
        // Filenames like "azalea-6" are not useful captions; only show real text.
        var title = img.getAttribute('title') || '';
        caption.textContent = title;
        caption.hidden = !title;
        document.documentElement.classList.add('lightbox-open');
        dialog.showModal();
    }

    function mark(img) {
        if (!zoomable(img)) return;
        img.classList.add('zoomable');
        img.setAttribute('tabindex', '0');
        img.setAttribute('role', 'button');
        img.setAttribute('aria-label', 'Expand image' + (img.alt ? ': ' + img.alt : ''));
    }

    main.addEventListener('click', function (e) {
        var img = e.target.closest('img.zoomable');
        if (img) open(img);
    });

    main.addEventListener('keydown', function (e) {
        if (e.key !== 'Enter' && e.key !== ' ') return;
        var img = e.target.closest('img.zoomable');
        if (!img) return;
        e.preventDefault();
        open(img);
    });

    // Rendered width is only known once each image has loaded.
    main.querySelectorAll('img').forEach(function (img) {
        if (img.complete && img.naturalWidth) {
            mark(img);
        } else {
            img.addEventListener('load', function () { mark(img); }, { once: true });
        }
    });
})();
