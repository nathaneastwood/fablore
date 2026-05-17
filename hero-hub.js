/**
 * Class filters for the Heroes of Rathe hub grid (pages containing `.hero-hub`).
 *
 * Single-select toggle buttons (including "All") update visibility of `.hero-hub-card`
 * links by matching `data-classes` tokens; heroes with multiple classes match any of
 * their listed classes when that filter is active.
 */
(function () {
    'use strict';
    var HERO_IMAGE_FALLBACK =
        (window.path_to_root || '') + 'assets/logo_original_cropped.png';

    /**
     * Convert class slug tokens into user-facing labels.
     *
     * @param {string[]} classes - Lowercase class slugs.
     * @returns {string} Readable class label text.
     */
    function formatClassLabel(classes) {
        return classes
            .map(function (token) {
                if (!token) {
                    return '';
                }
                return token.charAt(0).toUpperCase() + token.slice(1);
            })
            .filter(function (label) {
                return label.length > 0;
            })
            .join(' • ');
    }

    /**
     * Add class text under each hero name.
     *
     * @param {HTMLElement} hub - Root `.hero-hub` element.
     */
    function decorateCards(hub) {
        var cards = hub.querySelectorAll('.hero-hub-card');

        cards.forEach(function (card) {
            var label = card.querySelector('.world-hub-label');
            var raw = card.getAttribute('data-classes') || '';
            var classes = raw
                .trim()
                .split(/\s+/)
                .filter(function (token) {
                    return token.length > 0;
                });

            if (!label || classes.length === 0) {
                return;
            }

            card.setAttribute(
                'data-hero-name',
                (label.childNodes[0] ? label.childNodes[0].textContent : label.textContent || '')
                    .trim()
                    .toLowerCase()
            );

            if (label.querySelector('.hero-hub-class-label')) {
                return;
            }

            var classLabel = document.createElement('span');
            classLabel.className = 'hero-hub-class-label';
            classLabel.textContent = formatClassLabel(classes);
            label.appendChild(classLabel);
        });
    }

    /**
     * Swap missing hero artwork to a default image.
     *
     * @param {HTMLImageElement} img - Hero card image element.
     */
    function applyImageFallback(img) {
        if (img.getAttribute('data-fallback-applied') === 'true') {
            return;
        }
        img.setAttribute('data-fallback-applied', 'true');
        img.classList.add('hero-hub-card-image--fallback');
        img.src = HERO_IMAGE_FALLBACK;
        img.alt = 'Hero artwork unavailable';
    }

    /**
     * Register image fallback handlers on hero cards.
     *
     * @param {HTMLElement} hub - Root `.hero-hub` element.
     */
    function setupImageFallbacks(hub) {
        var images = hub.querySelectorAll('.hero-hub-card img');

        images.forEach(function (img) {
            img.addEventListener('error', function () {
                applyImageFallback(img);
            });

            if (img.complete && img.naturalWidth === 0) {
                applyImageFallback(img);
            }
        });
    }

    /**
     * Apply class and name filters, and sync button active states.
     *
     * @param {HTMLElement} hub - Root `.hero-hub` element.
     * @param {string} selectedClass - `"all"` or a lowercase class slug.
     * @param {string} query - Search query for hero name.
     */
    function applyFilters(hub, selectedClass, query) {
        var cards = hub.querySelectorAll('.hero-hub-card');
        var filters = hub.querySelectorAll('.hero-hub-filter');
        var normalizedQuery = (query || '').trim().toLowerCase();

        filters.forEach(function (btn) {
            var isActive = btn.getAttribute('data-class') === selectedClass;
            btn.classList.toggle('hero-hub-filter--active', isActive);
            btn.setAttribute('aria-pressed', isActive ? 'true' : 'false');
        });

        cards.forEach(function (card) {
            var raw = card.getAttribute('data-classes') || '';
            var classes = raw
                .trim()
                .split(/\s+/)
                .filter(function (token) {
                    return token.length > 0;
                });
            var classMatch =
                selectedClass === 'all' || classes.indexOf(selectedClass) !== -1;
            var heroName =
                card.getAttribute('data-hero-name') ||
                (card.textContent || '').toLowerCase();
            var searchMatch =
                normalizedQuery.length === 0 ||
                heroName.indexOf(normalizedQuery) !== -1;
            card.hidden = !(classMatch && searchMatch);
        });
    }

    /**
     * Wire click handlers for filter buttons within one hub instance.
     *
     * @param {HTMLElement} hub - Root `.hero-hub` element.
     */
    function initHub(hub) {
        var filters = hub.querySelectorAll('.hero-hub-filter');
        var searchInput = hub.querySelector('.hero-hub-search');
        var toolbar = hub.querySelector('.hero-hub-toolbar');
        var selectedClass = 'all';
        var query = '';

        decorateCards(hub);
        setupStickyToolbar(hub, toolbar);
        setupImageFallbacks(hub);

        filters.forEach(function (btn) {
            btn.addEventListener('click', function () {
                selectedClass = btn.getAttribute('data-class') || 'all';
                applyFilters(hub, selectedClass, query);
            });
        });

        if (searchInput) {
            var updateFromSearch = function () {
                query = searchInput.value || '';
                applyFilters(hub, selectedClass, query);
            };
            searchInput.addEventListener('input', updateFromSearch);
            searchInput.addEventListener('keyup', updateFromSearch);
            searchInput.addEventListener('search', updateFromSearch);
            searchInput.addEventListener('change', updateFromSearch);
        }

        applyFilters(hub, selectedClass, query);
    }

    /**
     * JS sticky fallback for layouts where CSS sticky is disabled by parent overflow.
     *
     * @param {HTMLElement} hub - Root `.hero-hub` element.
     * @param {HTMLElement | null} toolbar - Sticky toolbar node.
     */
    function setupStickyToolbar(hub, toolbar) {
        if (!toolbar) {
            return;
        }

        var spacer = document.createElement('div');
        spacer.className = 'hero-hub-toolbar-spacer';
        toolbar.parentNode.insertBefore(spacer, toolbar);

        /**
         * Bottom edge of the mdBook menu bar in viewport coordinates (flush under bar).
         *
         * @returns {number} Pixel position from top of viewport.
         */
        function getMenuBarBottom() {
            var menuBar = document.getElementById('menu-bar');
            if (!menuBar) {
                return 0;
            }
            return menuBar.getBoundingClientRect().bottom;
        }

        function updateStickyState() {
            var menuBottom = getMenuBarBottom();
            var spacerRect = spacer.getBoundingClientRect();
            var hubRect = hub.getBoundingClientRect();
            var toolbarHeight = toolbar.offsetHeight;
            var shouldFix =
                spacerRect.top <= menuBottom &&
                hubRect.bottom > menuBottom + toolbarHeight + 8;

            if (shouldFix) {
                toolbar.classList.add('hero-hub-toolbar--fixed');
                spacer.style.height = toolbarHeight + 'px';
                toolbar.style.left = spacerRect.left + 'px';
                toolbar.style.width = spacerRect.width + 'px';
                toolbar.style.top = menuBottom + 'px';
            } else {
                toolbar.classList.remove('hero-hub-toolbar--fixed');
                spacer.style.height = '0px';
                toolbar.style.left = '';
                toolbar.style.width = '';
                toolbar.style.top = '';
            }
        }

        window.addEventListener('scroll', updateStickyState, { passive: true });
        window.addEventListener('resize', updateStickyState);
        updateStickyState();
    }

    function initAllHubs() {
        document.querySelectorAll('.hero-hub').forEach(initHub);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initAllHubs);
    } else {
        initAllHubs();
    }
})();
