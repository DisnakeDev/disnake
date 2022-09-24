// SPDX-License-Identifier: MIT

"use strict";

window.addEventListener("DOMContentLoaded", main)

const api = "api.html";
const ext_cmds_api = "ext/commands/api.html";

function main() {
    const url = new URL(document.location.href);

    if (!url.pathname.endsWith('api.html')) return;

    let postfix = get_link(url);

    let fixed_postfix = false;

    if (!postfix) {
        if (url.pathname.endsWith(ext_cmds_api)) {
            postfix = "ext/commands/api/index.html";
        } else {
            postfix = "api/index.html";
        }
        fixed_postfix = true;
    }

    if (!fixed_postfix) {
        if (postfix.includes("disnake.ext.commands") && !url.pathname.endsWith(ext_cmds_api)) {
            postfix = "api/index.html";
        } else {
            if ((!postfix.includes("disnake.ext.commands.") && url.pathname.endsWith(ext_cmds_api))) {
                postfix = "ext/commands/api/index.html";
            }
        }
    }

    if (url.pathname.endsWith(ext_cmds_api)) {
        window.location.href = url.origin + url.pathname.slice(0, -ext_cmds_api.length) + postfix;
    } else {
        window.location.href = url.origin + url.pathname.slice(0, -api.length) + postfix;
    }
}

function get_link(url) {
    /*
    * redirects_map is set by redirects sphinx extension
    * and actually exists here at the time of loading
    * page, please sorry for eslint errors...
    */
    return redirects_map[url.hash.slice(1)];
}
