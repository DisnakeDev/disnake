'use-strict';

window.onload = main;

const api = "api.html"
const ext_cmds_api = "ext/commands/api.html"

function main() {
    const url = new URL(document.location.href);

    if (!url.pathname.endsWith('api.html')) return;

    let postfix = get_link(url);

    if (!postfix) {
        if (url.pathname.endsWith(ext_cmds_api)) {
            postfix = "ext/commands/api/index.html";
        } else {
            postfix = "api/index.html";
        }
    }

    if (url.pathname.endsWith(ext_cmds_api)) {
        window.location.href = url.origin + url.pathname.slice(0, -ext_cmds_api.length) + postfix;
    } else {
        window.location.href = url.origin + url.pathname.slice(0, -api.length) + postfix;
    }
}

function get_link(url) {
    return redirects_map[url.hash.slice(1)];
}
