/**
 * Injects all custom toolbar buttons, logos, reading-progress bar, site footer,
 * and back-to-top button into the stock mdBook template DOM.
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

    var leftButtons = menuBar.querySelector('.left-buttons');
    var rightButtons = menuBar.querySelector('.right-buttons');
    var menuTitle = menuBar.querySelector('.menu-title');

    // --- Left-side custom buttons (after theme list) ---
    if (leftButtons) {
        var themeList = document.getElementById('mdbook-theme-list');
        var insertPoint = themeList ? themeList.nextSibling : null;

        function insertLeft(el) {
            if (insertPoint) {
                leftButtons.insertBefore(el, insertPoint);
                insertPoint = el.nextSibling;
            } else {
                leftButtons.appendChild(el);
            }
        }

        // Bionic reading toggle
        var bionicBtn = document.createElement('button');
        bionicBtn.id = 'bionic-toggle';
        bionicBtn.className = 'icon-button';
        bionicBtn.type = 'button';
        bionicBtn.title = 'Enable Bionic Reading';
        bionicBtn.setAttribute('aria-label', 'Enable Bionic Reading');
        bionicBtn.setAttribute('aria-pressed', 'false');
        bionicBtn.innerHTML = '<i class="fa fa-bold"></i>';
        insertLeft(bionicBtn);

        // Accessibility toggle button
        var accessBtn = document.createElement('button');
        accessBtn.id = 'accessibility-toggle';
        accessBtn.className = 'icon-button';
        accessBtn.type = 'button';
        accessBtn.title = 'Reading preferences';
        accessBtn.setAttribute('aria-label', 'Reading preferences');
        accessBtn.setAttribute('aria-haspopup', 'true');
        accessBtn.setAttribute('aria-expanded', 'false');
        accessBtn.setAttribute('aria-controls', 'accessibility-menu');
        accessBtn.innerHTML = '<i class="fa fa-text-height"></i>';
        insertLeft(accessBtn);

        // Accessibility popup (sibling of toggle button, inside left-buttons)
        var accessMenu = document.createElement('div');
        accessMenu.id = 'accessibility-menu';
        accessMenu.className = 'accessibility-popup';
        accessMenu.setAttribute('role', 'dialog');
        accessMenu.setAttribute('aria-label', 'Reading preferences');
        accessMenu.innerHTML =
            '<div class="accessibility-section">' +
            '<span class="accessibility-label">Text size</span>' +
            '<div class="accessibility-choices">' +
            '<button class="accessibility-choice font-size-choice" data-scale="0.875">Small</button>' +
            '<button class="accessibility-choice font-size-choice" data-scale="1">Default</button>' +
            '<button class="accessibility-choice font-size-choice" data-scale="1.175">Large</button>' +
            '</div></div>' +
            '<div class="accessibility-section">' +
            '<span class="accessibility-label">Line width</span>' +
            '<div class="accessibility-choices">' +
            '<button class="accessibility-choice width-choice" data-width="560px">Narrow</button>' +
            '<button class="accessibility-choice width-choice" data-width="750px">Default</button>' +
            '<button class="accessibility-choice width-choice" data-width="980px">Wide</button>' +
            '</div></div>';
        insertLeft(accessMenu);

        // Random story button (not on print pages) — inserted before search toggle if present
        if (!isPrint) {
            var randomBtn = document.createElement('button');
            randomBtn.id = 'random-story-button';
            randomBtn.className = 'icon-button';
            randomBtn.type = 'button';
            randomBtn.title = 'Surprise me — take me to a random story';
            randomBtn.setAttribute('aria-label', 'Random story');
            randomBtn.innerHTML = '<i class="fa fa-random"></i>';
            var searchToggle = document.getElementById('mdbook-search-toggle');
            if (searchToggle) {
                leftButtons.insertBefore(randomBtn, searchToggle);
            } else {
                leftButtons.appendChild(randomBtn);
            }
        }
    }

    // --- Right-side: copy link button (first, not on print) ---
    if (!isPrint && rightButtons) {
        var copyBtn = document.createElement('button');
        copyBtn.id = 'copy-link-button';
        copyBtn.type = 'button';
        copyBtn.title = 'Copy link to this page';
        copyBtn.setAttribute('aria-label', 'Copy link to this page');
        copyBtn.innerHTML = '<i class="fa fa-link" aria-hidden="true"></i>';
        rightButtons.insertBefore(copyBtn, rightButtons.firstChild);
    }

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
