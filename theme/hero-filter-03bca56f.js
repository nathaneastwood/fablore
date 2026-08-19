// Inject the SVG duotone filter used to colourise hero-trait icons.
// Matches FABTCG's wp-duotone-ba9554-ba9554 treatment: every opaque pixel
// maps to #BA9554 regardless of its source colour; the alpha channel (icon
// shape) is preserved untouched.
(function () {
    function inject() {
        var svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
        svg.setAttribute("xmlns", "http://www.w3.org/2000/svg");
        svg.setAttribute("aria-hidden", "true");
        svg.style.cssText = "position:absolute;width:0;height:0;overflow:hidden";
        // feColorMatrix: ignore all input RGB, output constant #BA9554 (186,149,84).
        // Row 4 preserves the original alpha unchanged.
        svg.innerHTML =
            '<defs><filter id="hero-gold" color-interpolation-filters="sRGB">' +
            '<feColorMatrix type="matrix" values="' +
            "0 0 0 0 0.729 " +
            "0 0 0 0 0.584 " +
            "0 0 0 0 0.329 " +
            "0 0 0 1 0" +
            '"/></filter></defs>';
        document.body.insertBefore(svg, document.body.firstChild);
    }
    if (document.body) {
        inject();
    } else {
        document.addEventListener("DOMContentLoaded", inject);
    }
})();
