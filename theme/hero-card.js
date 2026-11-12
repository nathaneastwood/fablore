/*
 * Hero pages and the hero hub. Markup comes from src/data/mdbook_hero_meta.py.
 *
 * - Stat block: Adult | Young switch when a block carries both variants;
 *   Card | Printings switch; picking a printing shows it on the large card.
 * - Hero videos (video[data-hero-autoplay]) play only while at least half on
 *   screen, and never under prefers-reduced-motion.
 * - On a page with several forms (.hero-form), the "Forms of <hero>" rail after
 *   them shows one form at a time; picking one scrolls up to its banner. The URL
 *   anchor picks it; the newest form is the default. The story card and share
 *   sheet follow the shown form's banner, and the source link beside Related
 *   Lore follows its data-source (the form's fabtcg.com page).
 * - Hero banner: the pause / play button is the video's only control.
 * - On the hub, #class-<slug>, #talent-<slug> and #playstyle-<slug> in the URL
 *   apply a filter.
 */
(function () {
    'use strict';

    // --- Stat block -----------------------------------------------------------

    // theme/lightbox.js only marks images shown well below their natural
    // width, and cannot measure one in a hidden variant or form. Hero cards
    // always open, at one fixed size (data-lightbox-size, see hero-card.css),
    // so mark every one that has loaded.
    function markZoomable(scope) {
        scope.querySelectorAll('.hero-statblock-thumb').forEach(function (img) {
            img.setAttribute('data-lightbox-size', 'card');
            if (img.classList.contains('zoomable')) return;
            var mark = function () {
                if (!img.naturalWidth) return;
                img.classList.add('zoomable');
                img.setAttribute('tabindex', '0');
                img.setAttribute('role', 'button');
                img.setAttribute('aria-label', 'Expand image' + (img.alt ? ': ' + img.alt : ''));
            };
            if (img.complete && img.naturalWidth) mark();
            else img.addEventListener('load', mark, { once: true });
        });
    }

    function press(buttons, attr, value) {
        buttons.forEach(function (btn) {
            btn.setAttribute('aria-pressed', btn.getAttribute(attr) === value ? 'true' : 'false');
        });
    }

    // Adult | Young and Card | Printings live in one header above the variants.
    // Switching changes the name and the shown variant in place: nothing moves
    // focus or scrolls, and the Card | Printings choice (on the block) carries over.
    function initBlock(block) {
        var name = block.querySelector('.hero-statblock-head .hero-statblock-name');
        var variantButtons = block.querySelectorAll('.hero-variant-switch .hero-seg-btn');
        var viewButtons = block.querySelectorAll('.hero-view-switch .hero-seg-btn');
        var variants = block.querySelectorAll('.hero-statblock-variant');

        function view(value) {
            block.setAttribute('data-view', value);
            press(viewButtons, 'data-view', value);
        }
        viewButtons.forEach(function (btn) {
            btn.addEventListener('click', function () { view(btn.getAttribute('data-view')); });
        });
        if (viewButtons.length) view('card');

        function select(value) {
            press(variantButtons, 'data-variant', value);
            variants.forEach(function (v) {
                var show = v.getAttribute('data-variant') === value;
                v.hidden = !show;
                if (show) {
                    if (name) name.textContent = v.getAttribute('data-name') || name.textContent;
                    markZoomable(v);
                }
            });
        }
        variantButtons.forEach(function (btn) {
            btn.addEventListener('click', function () { select(btn.getAttribute('data-variant')); });
        });
        if (variantButtons.length) select('adult');
        block.heroView = view;
    }

    // Card | Printings, and picking a printing to show on the large card.
    function initVariantViews(variant) {
        var block = variant.closest('.hero-statblock');
        var main = variant.querySelector('.hero-statblock-thumb');
        var print = variant.querySelector('.hero-statblock-print');
        var caption = variant.querySelector('.hero-statblock-caption');
        var thumbs = Array.prototype.slice.call(variant.querySelectorAll('.hero-printing'));

        function current(thumb) {
            thumbs.forEach(function (t) {
                if (t === thumb) t.setAttribute('aria-current', 'true');
                else t.removeAttribute('aria-current');
            });
        }

        function pick(thumb, quiet) {
            if (!main) return;
            main.src = thumb.currentSrc || thumb.src;
            main.alt = thumb.alt;
            var fig = thumb.closest('figure');
            var cap = fig && fig.querySelector('figcaption');
            if (print && cap) print.innerHTML = cap.innerHTML;
            var artist = caption && caption.querySelector('.hero-statblock-artist');
            var name = thumb.getAttribute('data-artist') || '';
            if (caption && !artist && name) {
                artist = document.createElement('span');
                artist.className = 'hero-statblock-artist';
                caption.appendChild(artist);
            }
            if (artist) {
                artist.textContent = name;
                artist.hidden = !name;
            }
            current(thumb);
            markZoomable(variant);
            if (quiet) return;
            // On a phone the card sits above the grid, out of view.
            var top = main.getBoundingClientRect().top;
            if (top < 0 || top > window.innerHeight * 0.6) main.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
        }

        // A printing with no image is dropped from the grid; the count follows.
        var title = variant.querySelector('.hero-panel--printings .hero-panel-title');
        var failed = {};
        function drop(thumb) {
            failed[thumb.src] = true;
            var fig = thumb.closest('figure');
            if (fig) fig.remove();
            thumbs = Array.prototype.filter.call(thumbs, function (t) { return t !== thumb; });
            if (title) title.textContent = 'Printings (' + thumbs.length + ')';
            if (!thumbs.length) {
                var panel = variant.querySelector('.hero-panel--printings');
                if (panel) panel.remove();
                // No printing left in any variant: back to the card, without the control.
                if (block && !block.querySelector('.hero-printing')) {
                    if (block.heroView) block.heroView('card');
                    var control = block.querySelector('.hero-view-switch');
                    if (control) control.remove();
                }
            }
        }

        // The large card has no image: show the next printing that loads.
        function fallback() {
            failed[main.src] = true;
            main.classList.remove('zoomable');
            var next = Array.prototype.filter.call(thumbs, function (t) { return !failed[t.src]; })[0];
            if (next) pick(next, true);
            else main.closest('figure').hidden = true;
        }
        if (main) {
            main.addEventListener('error', fallback);
            if (main.complete && !main.naturalWidth) fallback();
        }

        thumbs.forEach(function (thumb) {
            thumb.addEventListener('error', function () { drop(thumb); });
            if (thumb.complete && !thumb.naturalWidth && thumb.getAttribute('src')) drop(thumb);
            thumb.setAttribute('tabindex', '0');
            thumb.setAttribute('role', 'button');
            thumb.setAttribute('aria-label', 'Show this printing: ' + thumb.alt);
            if (main && thumb.src === main.src) current(thumb);
            thumb.addEventListener('click', function () { pick(thumb); });
            thumb.addEventListener('keydown', function (e) {
                if (e.key !== 'Enter' && e.key !== ' ') return;
                e.preventDefault();
                pick(thumb);
            });
        });
    }

    // --- Hero videos ---------------------------------------------------------

    // Pause without counting it as the reader's choice (off screen, hidden form).
    function autoPause(video) {
        if (video.paused) return;
        video.dataset.heroAutoPaused = 'true';
        video.pause();
    }

    function initVideos() {
        var videos = document.querySelectorAll('video[data-hero-autoplay]');
        if (!videos.length) return;
        var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)');
        var autoplay = !(reduce && reduce.matches) && typeof IntersectionObserver !== 'undefined';

        function sync(video) {
            var btn = video.parentNode.querySelector('.hero-banner-play');
            if (!btn) return;
            btn.setAttribute('aria-pressed', video.paused ? 'true' : 'false');
            btn.setAttribute('aria-label', video.paused ? 'Play video' : 'Pause video');
        }

        var observer = autoplay && new IntersectionObserver(
            function (entries) {
                entries.forEach(function (entry) {
                    var video = entry.target;
                    if (entry.isIntersecting && entry.intersectionRatio >= 0.5) {
                        // A reader who paused it keeps it paused.
                        if (video.dataset.heroPausedByUser === 'true') return;
                        var played = video.play();
                        if (played && played.catch) played.catch(function () {});
                    } else {
                        autoPause(video);
                    }
                });
            },
            { threshold: [0, 0.5] }
        );

        videos.forEach(function (video) {
            video.muted = true;
            video.addEventListener('pause', function () {
                if (video.dataset.heroAutoPaused === 'true') {
                    video.dataset.heroAutoPaused = '';
                } else {
                    video.dataset.heroPausedByUser = 'true';
                }
                sync(video);
            });
            video.addEventListener('play', function () {
                video.dataset.heroPausedByUser = '';
                sync(video);
            });
            // The only control on the banner: pause / play.
            var btn = video.parentNode.querySelector('.hero-banner-play');
            if (btn) {
                btn.addEventListener('click', function () {
                    if (video.paused) {
                        var played = video.play();
                        if (played && played.catch) played.catch(function () {});
                    } else {
                        video.pause();
                    }
                });
            }
            sync(video);
            if (observer) observer.observe(video);
        });
    }

    // --- Hub filter from the URL ----------------------------------------------

    function talentLabel(slug) {
        return slug
            .split('-')
            .map(function (w) { return w.charAt(0).toUpperCase() + w.slice(1); })
            .join(' ');
    }

    function initHubFilter() {
        var hub = document.querySelector('.hero-hub');
        if (!hub) return;
        var chip = null;

        function clearTalent() {
            hub.querySelectorAll('.hero-hub-card--talent-out').forEach(function (card) {
                card.classList.remove('hero-hub-card--talent-out');
            });
            if (chip) {
                chip.remove();
                chip = null;
            }
        }

        function applyTalent(slug) {
            clearTalent();
            hub.querySelectorAll('.hero-hub-card').forEach(function (card) {
                var talents = (card.getAttribute('data-talents') || '').split(/\s+/);
                if (talents.indexOf(slug) === -1) card.classList.add('hero-hub-card--talent-out');
            });
            chip = document.createElement('button');
            chip.type = 'button';
            chip.className = 'hero-hub-talent-chip';
            chip.setAttribute('aria-label', 'Remove talent filter: ' + talentLabel(slug));
            chip.innerHTML = 'Talent: <strong></strong> <span aria-hidden="true">×</span>';
            chip.querySelector('strong').textContent = talentLabel(slug);
            chip.addEventListener('click', function () {
                clearTalent();
                history.replaceState(null, '', location.pathname + location.search);
            });
            var toolbar = hub.querySelector('.hero-hub-filters') || hub.querySelector('.hero-hub-toolbar');
            if (toolbar) toolbar.appendChild(chip);
            else hub.insertBefore(chip, hub.firstChild);
        }

        function fromHash() {
            var m = /^#(class|talent|playstyle)-([a-z0-9-]+)$/.exec(location.hash);
            if (!m) return;
            if (m[1] === 'playstyle') {
                // A link from a hero page's Details panel: press that playstyle (once).
                var style = hub.querySelector('.hero-hub-filter[data-playstyle="' + m[2] + '"]');
                if (style && style.getAttribute('aria-pressed') !== 'true') style.click();
            } else if (m[1] === 'class') {
                clearTalent();
                var btn = hub.querySelector('.hero-hub-filter[data-class="' + m[2] + '"]');
                if (btn) btn.click();
            } else {
                applyTalent(m[2]);
            }
            hub.scrollIntoView({ block: 'start' });
        }

        window.addEventListener('hashchange', fromHash);
        fromHash();
    }

    // --- One form at a time ---------------------------------------------------

    function initForms() {
        var forms = Array.prototype.slice.call(document.querySelectorAll('.hero-form'));
        if (forms.length < 2) return;
        var tabs = Array.prototype.slice.call(document.querySelectorAll('.hero-forms .hero-tab'));
        // The rail lists the forms in release order, so the last tab is the newest.
        var newest = tabs.length ? tabs[tabs.length - 1].getAttribute('href').slice(1) : forms[0].dataset.form;
        // The source link (mdbook_story_meta) points at the page's first form;
        // each form carries its own fabtcg.com page in data-source.
        var source = document.querySelector('#mdbook-content a.related-source-btn');
        var defaultSource = source && source.getAttribute('href');
        // The story card and share sheet belong to the page, not to the first
        // form: mdbook_story_meta puts them under the first banner, so they
        // would hide with that form. Either may be absent (a hero page's card
        // is dropped when it holds nothing).
        var pageBlock = ['.story-card', '.story-share']
            .map(function (sel) { return document.querySelector('#mdbook-content ' + sel); })
            .filter(Boolean);

        function formFor(id) {
            if (!id) return null;
            var match = forms.filter(function (f) { return f.dataset.form === id; })[0];
            if (match) return match;
            var target = document.getElementById(id);
            return target ? target.closest('.hero-form') : null;
        }

        function show(form) {
            forms.forEach(function (f) {
                if (f === form) {
                    f.removeAttribute('hidden');
                    markZoomable(f);
                } else {
                    // until-found: Ctrl+F still finds the text and fires beforematch.
                    f.setAttribute('hidden', 'until-found');
                    f.querySelectorAll('video').forEach(autoPause);
                }
            });
            tabs.forEach(function (tab) {
                var on = tab.getAttribute('href').slice(1) === form.dataset.form;
                tab.setAttribute('aria-selected', on ? 'true' : 'false');
                if (on) tab.setAttribute('aria-current', 'true');
                else tab.removeAttribute('aria-current');
            });
            if (source) source.setAttribute('href', form.dataset.source || defaultSource);
            // The card and share sheet sit under the shown form's banner.
            var banner = form.querySelector('.hero-banner');
            if (banner) {
                pageBlock.reduceRight(function (next, el) {
                    banner.parentNode.insertBefore(el, next);
                    return el;
                }, banner.nextSibling);
            }
        }

        // Land on the top of the banner, never on the H1 text inside it.
        function toBanner(form, smooth) {
            var banner = form.querySelector('.hero-banner');
            if (!banner) return;
            var bar = document.getElementById('mdbook-menu-bar');
            var offset = bar ? bar.getBoundingClientRect().bottom : 0;
            var top = banner.getBoundingClientRect().top + window.scrollY - Math.max(offset, 0);
            var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
            window.scrollTo({ top: top, behavior: smooth && !reduce ? 'smooth' : 'auto' });
        }

        function fromHash(land) {
            var id = decodeURIComponent(location.hash.slice(1));
            var picked = formFor(id);
            show(picked || formFor(newest) || forms[0]);
            if (picked && land) toBanner(picked);
        }

        // A tab is a real link (it works without JS). With JS it switches in
        // place, then takes the reader up to the new form's banner.
        tabs.forEach(function (tab) {
            tab.addEventListener('click', function (e) {
                var form = formFor(tab.getAttribute('href').slice(1));
                if (!form) return;
                e.preventDefault();
                show(form);
                history.replaceState(null, '', '#' + form.dataset.form);
                toBanner(form, true);
            });
        });
        forms.forEach(function (f) {
            f.addEventListener('beforematch', function () { show(f); });
        });
        window.addEventListener('hashchange', function () { fromHash(true); });
        document.body.classList.add('hero-forms-tabbed');
        fromHash(true);
        // The browser's own jump to the anchor can land after this script runs.
        if (location.hash) window.addEventListener('load', function () { fromHash(true); }, { once: true });
    }

    function init() {
        document.querySelectorAll('.hero-statblock').forEach(initBlock);
        document.querySelectorAll('.hero-statblock-variant').forEach(initVariantViews);
        document.querySelectorAll('.hero-statblock').forEach(markZoomable);
        initForms();
        initVideos();
        // After hero-hub.js has wired its filter buttons on the same event.
        setTimeout(initHubFilter, 0);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
