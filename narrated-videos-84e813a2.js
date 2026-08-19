// Tab switching for the narrated-videos component.
// Scoped to the nearest .narrated-videos ancestor so multiple instances on one
// page never interfere with each other.
function nvOpenTab(btn, panelId) {
    var container = btn.closest('.narrated-videos');
    var tabs = container.querySelectorAll('.nv-tab');
    var panels = container.querySelectorAll('.nv-panel');

    tabs.forEach(function (t) {
        t.classList.remove('nv-tab--active');
        t.setAttribute('aria-selected', 'false');
    });
    panels.forEach(function (p) {
        p.classList.add('nv-panel--hidden');
        p.setAttribute('hidden', '');
    });

    btn.classList.add('nv-tab--active');
    btn.setAttribute('aria-selected', 'true');
    var panel = document.getElementById(panelId);
    if (panel) {
        panel.classList.remove('nv-panel--hidden');
        panel.removeAttribute('hidden');
    }
}
