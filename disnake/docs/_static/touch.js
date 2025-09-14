// SPDX-License-Identifier: MIT

"use strict";

(function(){
    let touch_start;

    // Add swipe gestures to slideout TOC
    document.addEventListener("DOMContentLoaded", () => {
        document.querySelector("aside").addEventListener("touchstart", (e) => {
            const first_touch = e.changedTouches[0];
            touch_start = [first_touch.screenX, first_touch.screenY];
        }, false);

        document.querySelector("aside").addEventListener("touchend", (e) => {
            const final_touch = e.changedTouches[e.changedTouches.length-1];

            const deltaX = final_touch.screenX - touch_start[0];
            const deltaY = final_touch.screenY - touch_start[1];

            if (-20 < deltaX && deltaX < 20) {
                // too small horizontally
                return
            }
            if (-50 > deltaY || deltaY > 50) {
                // too big vertically
                return
            }

            // Either direction is fine
            showHideSidebar();
            // No accidental clicks
            e.preventDefault();
        }, false);
    });
})()
