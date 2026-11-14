/**
 * Injects the logos, reading-progress bar, site footer, and back-to-top button
 * into the stock mdBook template DOM. The custom toolbar buttons are in
 * index.hbs, so they get the same inline SVG icons as mdBook's own buttons.
 *
 * Must be the first entry in additional-js so injected elements exist when
 * subsequent scripts (bionic.js, back-to-top.js, etc.) run synchronously.
 */
(function () {
    'use strict';

    var isPrint = window.location.pathname.endsWith('/print.html');
    // path_to_root is a const set by the template — access as plain global, not window property
    var root = (typeof path_to_root !== 'undefined') ? path_to_root : '';

    var menuBar = document.getElementById('mdbook-menu-bar');
    if (!menuBar) return;

    var menuTitle = menuBar.querySelector('.menu-title');

    // --- Replace .menu-title text with theme-aware logo images ---
    if (menuTitle) {
        var logoLight = document.createElement('img');
        logoLight.className = 'menu-logo menu-logo--light';
        logoLight.src = root + 'assets/logo_original_cropped.png';
        logoLight.alt = document.title;
        var logoDark = document.createElement('img');
        logoDark.className = 'menu-logo menu-logo--dark';
        logoDark.src = root + 'assets/logo_transparent_white.png';
        logoDark.alt = document.title;
        menuTitle.textContent = '';
        menuTitle.appendChild(logoLight);
        menuTitle.appendChild(logoDark);
    }

    // --- Reading progress bar (after menu bar, not on print) ---
    if (!isPrint) {
        var progressBar = document.createElement('div');
        progressBar.id = 'reading-progress-bar';
        progressBar.setAttribute('aria-hidden', 'true');
        var progressFill = document.createElement('div');
        progressFill.id = 'reading-progress-fill';
        progressBar.appendChild(progressFill);
        menuBar.parentNode.insertBefore(progressBar, menuBar.nextSibling);
    }

    // --- Site footer (bottom of .page, not on print) ---
    if (!isPrint) {
        var page = document.querySelector('.page');
        if (page) {
            var footer = document.createElement('footer');
            footer.className = 'site-footer';
            footer.innerHTML =
                '<a href="' + root + 'content-creators.html">Content Creators</a>' +
                '<span aria-hidden="true">·</span>' +
                '<a href="' + root + 'about.html">About</a>' +
                '<span aria-hidden="true">·</span>' +
                '<a href="' + root + 'support.html">Support the Site</a>';
            page.appendChild(footer);
        }
    }

    // --- Back-to-top button (inside page-wrapper, not on print) ---
    if (!isPrint) {
        var pageWrapper = document.getElementById('mdbook-page-wrapper');
        if (pageWrapper) {
            var backToTop = document.createElement('button');
            backToTop.type = 'button';
            backToTop.id = 'back-to-top';
            backToTop.className = 'back-to-top';
            backToTop.setAttribute('aria-label', 'Back to top');
            backToTop.title = 'Back to top';
            backToTop.setAttribute('aria-hidden', 'true');
            backToTop.tabIndex = -1;
            backToTop.innerHTML = '<i class="fa fa-arrow-up" aria-hidden="true"></i>';
            pageWrapper.appendChild(backToTop);
        }
    }
})();
