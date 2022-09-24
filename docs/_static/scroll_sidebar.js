// SPDX-License-Identifier: MIT

"use strict";

window.addEventListener("DOMContentLoaded", main);

function main() {
    const currentSection = document.querySelector("#sidebar li.current");

    if (currentSection) {
        currentSection.scrollIntoView();
    }
}
