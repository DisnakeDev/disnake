'use-strict';

window.addEventListener("DOMContentLoaded", main);

const url_ss = new URL(window.location.href);

function main() {
    const main_div = document.getElementById('sidebar')
        .children[0]
        .children[1];

    if (main_div.tagName === 'DIV') {
        main_div.removeChild(main_div.children[0]); // remove admonition from sidebar
    }

    const main_ul = main_div.children[0];

    for (const elem of main_ul.children) {
        if (elem.children[1].href === undefined) { // pls dont even ask how this works, its javascript
            elem.scrollIntoView();
            break;
        }
    }
}
