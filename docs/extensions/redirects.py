# SPDX-License-Identifier: MIT

import json
import os
from pathlib import Path
from typing import Dict

from _types import SphinxExtensionMeta
from sphinx.application import Sphinx

api_redirect_source = """
// SPDX-License-Identifier: MIT

"use strict";

window.addEventListener("DOMContentLoaded", main)

const api = "api.html";
const ext_cmds_api = "ext/commands/api.html";

function main() {
    const url = new URL(document.location.href);

    if (!url.pathname.endsWith('api.html')) return;

    /*
    * redirects_map is set by the redirects sphinx extension
    * and actually exists here at the time of loading the page
    */
    let postfix = redirects_map[url.hash.slice(1)];

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

const redirects_map =
"""


def main(app: Sphinx, exception: Exception) -> None:
    if exception:
        return

    # mapping of html node id (i.e., thing after "#" in URLs) to the same but
    # prefixed with the right doc name
    # e.g, api.html#disnake.Thread => api/channels.html#disnake.Thread
    actual_redirects: Dict[str, str] = {}

    domain = app.env.domains["py"]

    # see https://www.sphinx-doc.org/en/master/extdev/domainapi.html#sphinx.domains.Domain.get_objects
    for _, _, _, document, html_node_id, _ in domain.get_objects():
        actual_redirects[html_node_id] = document + ".html#" + html_node_id

    path = Path(os.path.join(app.outdir, "_static", "api_redirect.js"))

    path.touch()

    with open(path, "w") as redirects_js:
        redirect_data = json.dumps(actual_redirects)

        javascript = api_redirect_source + redirect_data + ";"

        redirects_js.write(javascript)


def setup(app: Sphinx) -> SphinxExtensionMeta:
    app.connect("build-finished", main)

    return {
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
