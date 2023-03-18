# SPDX-License-Identifier: MIT

import json
from pathlib import Path
from typing import Dict

from _types import SphinxExtensionMeta
from sphinx.application import Sphinx
from sphinx.util.fileutil import copy_asset_file


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
        actual_redirects[html_node_id] = document + ".html"

    path = Path(app.outdir, "_static", "api_redirect.js")

    path.touch(exist_ok=True)

    context = {}
    context["redirect_data"] = json.dumps(actual_redirects)

    copy_asset_file(
        str(Path("_templates", "api_redirect.js_t")),
        str(path),
        context=context,
    )


def setup(app: Sphinx) -> SphinxExtensionMeta:
    app.connect("build-finished", main)

    return {
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
