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
 * Runs after theme/toolbar.js (book.toml order), which is what leaves
 * #mdbook-theme-list's next sibling as the insertion point — right after
 * the theme switcher and before the secondary icons toolbar.js adds.
 */
(function () {
    "use strict";

    var STORAGE_KEY = "fablore-lang";

    var menuBar = document.getElementById("mdbook-menu-bar");
    var leftButtons = menuBar ? menuBar.querySelector(".left-buttons") : null;
    var themeList = document.getElementById("mdbook-theme-list");
    if (!leftButtons || !themeList) return;

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

    var toggle = document.createElement("button");
    toggle.id = "lang-toggle";
    toggle.className = "icon-button";
    toggle.type = "button";
    toggle.title = "Change language";
    toggle.setAttribute("aria-label", "Change language");
    toggle.setAttribute("aria-haspopup", "true");
    toggle.setAttribute("aria-expanded", "false");
    toggle.setAttribute("aria-controls", "lang-popup");
    toggle.innerHTML = '<i class="fa fa-globe" aria-hidden="true"></i>';

    var popup = document.createElement("ul");
    popup.id = "lang-popup";
    popup.className = "theme-popup lang-popup";
    popup.setAttribute("aria-label", "Language");
    popup.setAttribute("role", "menu");
    popup.innerHTML =
        '<li role="none"><button role="menuitem" class="theme lang-option" id="lang-option-en" data-lang="en">English</button></li>' +
        '<li role="none"><button role="menuitem" class="theme lang-option" id="lang-option-arcane" data-lang="arcane">Arcane</button></li>';

    var insertPoint = themeList.nextSibling;
    leftButtons.insertBefore(toggle, insertPoint);
    leftButtons.insertBefore(popup, insertPoint);

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
