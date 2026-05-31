// SPDX-License-Identifier: MIT

/*
====================
This script is meant to be injected into all documentation versions using
https://docs.readthedocs.com/platform/stable/custom-script.html to apply
various fixes to old documentation versions.
(It could be hosted basically anywhere, but adding it to the repo is easiest.)
====================
*/

// intercept the internal Readthedocs Addons event, and disable
// link previews in (older) versions where hoverxref is still being used.
document.addEventListener(
    "readthedocs-addons-internal-data-ready",
    (event) => {
        const data = event.detail.data(true);

        if (document.querySelector('script[src*="/hoverxref.js"]')) {
            data.addons.linkpreviews.enabled = false;
        }
    }
)
