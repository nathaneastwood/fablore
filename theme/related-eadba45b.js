/**
 * Equalize Related Lore card heights within each `.related-cards` grid so hero
 * and location cards share the same minimum height when both groups appear.
 */
(function () {
    "use strict";

    function equalizeOneGrid(grid) {
        var cards = [];
        for (var i = 0; i < grid.children.length; i++) {
            var el = grid.children[i];
            if (el.tagName === "A" && el.classList.contains("related-card")) {
                cards.push(el);
            }
        }
        if (cards.length < 2) {
            cards.forEach(function (c) {
                c.style.minHeight = "";
            });
            return;
        }
        cards.forEach(function (c) {
            c.style.minHeight = "";
        });
        var max = 0;
        cards.forEach(function (c) {
            var h = c.getBoundingClientRect().height;
            if (h > max) {
                max = h;
            }
        });
        if (max <= 0) {
            return;
        }
        cards.forEach(function (c) {
            c.style.minHeight = max + "px";
        });
    }

    function equalizeAll() {
        document.querySelectorAll(".related-section .related-cards").forEach(
            equalizeOneGrid
        );
    }

    function schedule() {
        equalizeAll();
        requestAnimationFrame(equalizeAll);
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", schedule);
    } else {
        schedule();
    }

    window.addEventListener("resize", function () {
        schedule();
    });
})();
