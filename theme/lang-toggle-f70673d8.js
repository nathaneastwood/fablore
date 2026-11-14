/**
 * Header language switcher: English (default) or Arcane.
 *
 * Arcane is a font swap, not a translation — the same principle
 * theme/glyph-tool.js uses on the Languages pages, applied here to a whole
 * rendered chapter instead of one typed line. The markup keeps its real
 * English text throughout, so search, screen readers and copy/paste are
 * unaffected; only the typeface the reader sees changes. See
 * theme/lang-toggle.css for the font-swap rule itself.
 *
 * Mirrors mdBook's own theme switcher (button + popup + localStorage), but
 * is entirely independent of it: book.js scopes all its listeners to
 * #mdbook-theme-list and #mdbook-theme-toggle by id, so this popup's clicks
 * never reach it, and reusing the "theme" class here only borrows its
 * visual styling.
 *
 * The button and popup are in index.hbs, so the icon is the same inline SVG
 * as mdBook's own buttons.
 */
(function () {
    "use strict";

    var STORAGE_KEY = "fablore-lang";

    var toggle = document.getElementById("lang-toggle");
    var popup = document.getElementById("lang-popup");
    if (!toggle || !popup) return;

    function getLang() {
        try {
            return localStorage.getItem(STORAGE_KEY) || "en";
        } catch (e) {
            return "en";
        }
    }

    function applyLang(lang) {
        document.documentElement.setAttribute("data-lang", lang);
    }

    function setLang(lang) {
        try {
            localStorage.setItem(STORAGE_KEY, lang);
        } catch (e) {
            // Private browsing etc. — the choice just won't survive navigation.
        }
        applyLang(lang);
    }

    function updateSelected() {
        var lang = getLang();
        Array.prototype.forEach.call(popup.querySelectorAll(".lang-option"), function (btn) {
            btn.classList.toggle("theme-selected", btn.dataset.lang === lang);
        });
    }

    function showPopup() {
        popup.style.display = "block";
        toggle.setAttribute("aria-expanded", "true");
        var current = popup.querySelector('.lang-option[data-lang="' + getLang() + '"]');
        if (current) current.focus();
    }

    function hidePopup() {
        popup.style.display = "none";
        toggle.setAttribute("aria-expanded", "false");
    }

    toggle.addEventListener("click", function () {
        if (popup.style.display === "block") {
            hidePopup();
        } else {
            showPopup();
        }
    });

    popup.addEventListener("click", function (e) {
        var btn = e.target.closest(".lang-option");
        if (!btn) return;
        setLang(btn.dataset.lang);
        updateSelected();
        hidePopup();
        toggle.focus();
    });

    popup.addEventListener("focusout", function (e) {
        if (e.relatedTarget && !toggle.contains(e.relatedTarget) && !popup.contains(e.relatedTarget)) {
            hidePopup();
        }
    });

    // Mirrors book.js's own workaround for the same macOS/iOS focusout gap:
    // https://github.com/rust-lang/mdBook/issues/628
    document.addEventListener("click", function (e) {
        if (popup.style.display === "block" && !toggle.contains(e.target) && !popup.contains(e.target)) {
            hidePopup();
        }
    });

    document.addEventListener("keydown", function (e) {
        if (popup.style.display === "block" && e.key === "Escape") {
            hidePopup();
            toggle.focus();
        }
    });

    applyLang(getLang());
    updateSelected();
})();
