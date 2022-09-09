'use-strict';

window.addEventListener("DOMContentLoaded", main);

const url_ss = new URL(window.location.href);

function main() {
    let num = 0;

    if (url_ss.host.startsWith("disnake--") && url_ss.host.endsWith(".org.readthedocs.build")) {
        // when building docs for PRs, rtd inserts the fucking
        // "warning" telling that the page was created from PR
        // just before the main ul, thus we need to increment
        // this to skip admonition and get ul instead of div
        num = 1;
    }

    const main_ul = document.getElementById('sidebar')
        .children[0]
        .children[1]
        .children[num];

    for (const elem of main_ul.children) {
        if (elem.children[1].href === undefined) { // pls dont even ask how this works
            elem.scrollIntoView();
            break;
        }
    }
}