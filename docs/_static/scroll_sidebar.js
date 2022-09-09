'use-strict';

window.addEventListener("DOMContentLoaded", main);

function main() {
    const main_ul = document.getElementById('sidebar')
        .children[0]
        .children[1]
        .children[0];

    for (const elem of main_ul.children) {
        if (elem.children[1].href === undefined) { // pls dont even ask how this works
            elem.scrollIntoView();
            break;
        }
    }
}