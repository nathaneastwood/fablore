/**
 * Class and playstyle filters for the Heroes of Rathe hub grid (pages containing `.hero-hub`).
 *
 * Single-select toggle buttons (including "All") update visibility of `.hero-hub-card`
 * links by matching `data-classes` tokens; heroes with multiple classes match any of
 * their listed classes when that filter is active.
 *
 * The playstyle buttons (`data-playstyle`) are a second, single-select group: pressing
 * one keeps the cards whose `data-playstyles` (from mdbook_hero_meta.py) hold it, and
 * pressing it again clears it. Class, playstyle and the name search all have to match.
 *
 * A card for a hero page with several forms carries `data-forms` (mdbook_hero_meta.py):
 * each form's anchor, name, art, talents and playstyles, oldest first. Its link already
 * lands on the form its image shows. While a playstyle filter, or the talent filter
 * theme/hero-card.js applies from a `#talent-` link, is on, the card shows and links
 * to the newest form that matches instead; clearing the filters restores it.
 * theme/hero-card.js reports its talent filter with a `hero-hub:talent` event on the
 * hub (`detail.talent`, `''` when cleared).
 *
 * Form art can be several megabytes, so a card never swaps its `src` straight away:
 * setCardImage fetches and decodes the new art off-screen while the card's image is
 * hidden, then shows it in one step (the newest request wins). On a page opened with
 * a `#playstyle-` or `#talent-` URL, theme/index.hbs hides multi-form card art
 * (html.hero-hub-prepick) before the page paints, and prepickFromHash starts the
 * swap as the hub is set up, so a card due to change never first shows its own art.
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
     * The forms listed in a card's `data-forms`, oldest first; `[]` for a one-form hero.
     *
     * @param {HTMLElement} card - Hero card link.
     * @returns {{id: string, name: string, art: string, talents: string[], playstyles: string[]}[]}
     */
    function cardForms(card) {
        if (!card.heroForms) {
            try {
                card.heroForms = JSON.parse(card.getAttribute('data-forms') || '[]');
            } catch (e) {
                card.heroForms = [];
            }
        }
        return card.heroForms;
    }

    /**
     * Remember a multi-form card's own link and image, before any filter or fallback changes them.
     *
     * @param {HTMLElement} hub - Root `.hero-hub` element.
     */
    function rememberCardForms(hub) {
        hub.querySelectorAll('.hero-hub-card[data-forms]').forEach(function (card) {
            var img = card.querySelector('img');
            card.setAttribute('data-hub-href', card.getAttribute('href') || '');
            if (img) {
                img.setAttribute('data-hub-src', img.getAttribute('src') || '');
                img.setAttribute('data-hub-alt', img.getAttribute('alt') || '');
            }
        });
    }

    var PENDING_CLASS = 'hero-hub-card--art-pending';

    /**
     * Resolve once `image` holds `src` decoded, or reject if it cannot load.
     * Uses `decode()` where the browser has it, else the load / error events.
     *
     * @param {HTMLImageElement} image - Image to watch (its `src` is set by the caller).
     * @returns {Promise<void>}
     */
    function whenDecoded(image) {
        if (typeof image.decode === 'function') {
            return image.decode().catch(function (err) {
                // decode() can reject an image that did load (e.g. one too large to
                // decode up front); only a load failure leaves naturalWidth at 0.
                if (image.complete && image.naturalWidth > 0) return;
                throw err;
            });
        }
        return new Promise(function (resolve, reject) {
            if (image.complete && image.naturalWidth > 0) return resolve();
            image.addEventListener('load', function () { resolve(); }, { once: true });
            image.addEventListener('error', reject, { once: true });
        });
    }

    /**
     * Point a card's image at `src` in one clean step: the art is fetched and
     * decoded off-screen while the card's image is hidden (PENDING_CLASS), and
     * only then shown, so the browser never paints the new art progressively
     * over the old. A later call wins over a pending one (`img.hubArtToken`).
     * Form art that fails is remembered in `failedArt` and the card goes back to
     * its own image; the card's own image failing gets the usual logo fallback.
     *
     * @param {HTMLImageElement} img - Hero card image element.
     * @param {string} src - Image URL.
     * @param {string} alt - Alt text.
     */
    function setCardImage(img, src, alt) {
        var card = img.closest('.hero-hub-card') || img.parentNode;
        img.alt = alt;
        if (img.hubArtPending === src) {
            return;
        }
        var token = (img.hubArtToken || 0) + 1;
        img.hubArtToken = token;
        if (img.getAttribute('src') === src) {
            // Already showing it: drop any pending swap.
            img.hubArtPending = null;
            card.classList.remove(PENDING_CLASS);
            return;
        }
        img.hubArtPending = src;
        card.classList.add(PENDING_CLASS);

        var own = img.getAttribute('data-hub-src');
        var current = function () { return img.hubArtToken === token; };
        var reveal = function () {
            if (!current()) return;
            img.hubArtPending = null;
            card.classList.remove(PENDING_CLASS);
        };
        var show = function () {
            img.removeAttribute('data-fallback-applied');
            img.classList.remove('hero-hub-card-image--fallback');
            // The bytes are already here; a lazy image out of view would not take them yet.
            img.loading = 'eager';
            img.src = src;
            whenDecoded(img).then(reveal, reveal);
        };

        var preload = new Image();
        preload.src = src;
        whenDecoded(preload).then(
            function () {
                if (current()) show();
            },
            function () {
                if (!current()) return;
                img.hubArtPending = null;
                if (src !== own) {
                    // A form's art that is missing: keep the card's own image instead.
                    failedArt[src] = true;
                    setCardImage(img, own, img.getAttribute('data-hub-alt'));
                } else if (img.getAttribute('data-fallback-applied') === 'true') {
                    reveal();
                } else {
                    // The card's own image is missing: the error handler gives it the logo.
                    show();
                }
            }
        );
    }

    /**
     * Show and link each multi-form card's newest form matching the active filters,
     * or its own image and link when no filter is on (or no form matches).
     *
     * @param {HTMLElement} hub - Root `.hero-hub` element.
     * @param {string} playstyle - `""` or a playstyle slug.
     * @param {string} talent - `""` or a talent slug.
     */
    function showMatchingForms(hub, playstyle, talent) {
        hub.querySelectorAll('.hero-hub-card[data-forms]').forEach(function (card) {
            var img = card.querySelector('img');
            var picked = null;
            if (playstyle || talent) {
                cardForms(card).forEach(function (form) {
                    if (
                        (!playstyle || form.playstyles.indexOf(playstyle) !== -1) &&
                        (!talent || form.talents.indexOf(talent) !== -1)
                    ) {
                        picked = form;
                    }
                });
            }
            var href = card.getAttribute('data-hub-href') || '';
            if (!picked) {
                card.setAttribute('href', href);
                card.removeAttribute('aria-label');
                if (img) {
                    setCardImage(img, img.getAttribute('data-hub-src'), img.getAttribute('data-hub-alt'));
                }
                return;
            }
            card.setAttribute('href', href.split('#')[0] + '#' + picked.id);
            // The visible label names the hero; the link's name says which form it opens.
            card.setAttribute('aria-label', picked.name);
            if (img) {
                // Art that failed to load once keeps the card's own image.
                var art = picked.art && !failedArt[picked.art] ? picked.art : img.getAttribute('data-hub-src');
                setCardImage(img, art, img.getAttribute('data-hub-alt'));
            }
        });
    }

    // Form art URLs that did not load.
    var failedArt = {};

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
                var own = img.getAttribute('data-hub-src');
                var src = img.getAttribute('src');
                // A form's art that is missing: keep the card's own image instead.
                if (own && src !== own && src !== HERO_IMAGE_FALLBACK) {
                    failedArt[src] = true;
                    setCardImage(img, own, img.getAttribute('data-hub-alt'));
                    return;
                }
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
     * @param {string} selectedPlaystyle - `""` or a playstyle slug.
     * @param {string} selectedTalent - `""` or the talent slug theme/hero-card.js filters by.
     */
    function applyFilters(hub, selectedClass, query, selectedPlaystyle, selectedTalent) {
        var cards = hub.querySelectorAll('.hero-hub-card');
        var filters = hub.querySelectorAll('.hero-hub-filter[data-class]');
        var playstyleButtons = hub.querySelectorAll('.hero-hub-filter[data-playstyle]');
        var normalizedQuery = (query || '').trim().toLowerCase();

        filters.forEach(function (btn) {
            var isActive = btn.getAttribute('data-class') === selectedClass;
            btn.classList.toggle('hero-hub-filter--active', isActive);
            btn.setAttribute('aria-pressed', isActive ? 'true' : 'false');
        });
        playstyleButtons.forEach(function (btn) {
            var isActive = btn.getAttribute('data-playstyle') === selectedPlaystyle;
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
            var playstyleMatch =
                !selectedPlaystyle ||
                (card.getAttribute('data-playstyles') || '').split(/\s+/).indexOf(selectedPlaystyle) !== -1;
            card.hidden = !(classMatch && searchMatch && playstyleMatch);
        });
        showMatchingForms(hub, selectedPlaystyle, selectedTalent);
    }

    /**
     * Wire click handlers for filter buttons within one hub instance.
     *
     * @param {HTMLElement} hub - Root `.hero-hub` element.
     */
    function initHub(hub) {
        var filters = hub.querySelectorAll('.hero-hub-filter[data-class]');
        var playstyleButtons = hub.querySelectorAll('.hero-hub-filter[data-playstyle]');
        var searchInput = hub.querySelector('.hero-hub-search');
        var toolbar = hub.querySelector('.hero-hub-toolbar');
        var selectedClass = 'all';
        var selectedPlaystyle = '';
        var selectedTalent = '';
        var query = '';

        decorateCards(hub);
        rememberCardForms(hub);
        setupStickyToolbar(hub, toolbar);
        setupImageFallbacks(hub);

        filters.forEach(function (btn) {
            btn.addEventListener('click', function () {
                selectedClass = btn.getAttribute('data-class') || 'all';
                applyFilters(hub, selectedClass, query, selectedPlaystyle, selectedTalent);
            });
        });

        playstyleButtons.forEach(function (btn) {
            btn.addEventListener('click', function () {
                var slug = btn.getAttribute('data-playstyle') || '';
                selectedPlaystyle = selectedPlaystyle === slug ? '' : slug;
                applyFilters(hub, selectedClass, query, selectedPlaystyle, selectedTalent);
            });
        });

        if (searchInput) {
            var updateFromSearch = function () {
                query = searchInput.value || '';
                applyFilters(hub, selectedClass, query, selectedPlaystyle, selectedTalent);
            };
            searchInput.addEventListener('input', updateFromSearch);
            searchInput.addEventListener('keyup', updateFromSearch);
            searchInput.addEventListener('search', updateFromSearch);
            searchInput.addEventListener('change', updateFromSearch);
        }

        // theme/hero-card.js filters by talent from a `#talent-` link.
        hub.addEventListener('hero-hub:talent', function (e) {
            selectedTalent = (e.detail && e.detail.talent) || '';
            showMatchingForms(hub, selectedPlaystyle, selectedTalent);
        });

        applyFilters(hub, selectedClass, query, selectedPlaystyle, selectedTalent);
        prepickFromHash(hub);
    }

    /**
     * Start the form swap a `#playstyle-` or `#talent-` URL will ask for, before the
     * card's own art has a chance to paint. theme/hero-card.js still applies the
     * filter itself (on a later tick); when it does, showMatchingForms asks for the
     * same art, which is already pending, so nothing changes. Only the slug is read
     * here; what the filter means stays in theme/hero-card.js.
     *
     * @param {HTMLElement} hub - Root `.hero-hub` element.
     */
    function prepickFromHash(hub) {
        var m = /^#(talent|playstyle)-([a-z0-9-]+)$/.exec(location.hash);
        if (!m) {
            return;
        }
        if (m[1] === 'playstyle') {
            // theme/hero-card.js presses the button only if there is one.
            if (hub.querySelector('.hero-hub-filter[data-playstyle="' + m[2] + '"]')) {
                showMatchingForms(hub, m[2], '');
            }
        } else {
            showMatchingForms(hub, '', m[2]);
        }
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
            var menuBar = document.getElementById('mdbook-menu-bar');
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
        // theme/index.hbs hides multi-form card art on a filter URL until now;
        // from here each card that is changing form carries its own pending class.
        document.documentElement.classList.remove('hero-hub-prepick');
    }

    // mdBook loads this script after the page content, so a hub already in the
    // DOM can be set up now rather than after the scripts that follow (sooner for
    // prepickFromHash). theme/hero-card.js wires its hash filter on a later tick.
    if (document.readyState === 'loading' && !document.querySelector('.hero-hub')) {
        document.addEventListener('DOMContentLoaded', initAllHubs);
    } else {
        initAllHubs();
    }
})();
