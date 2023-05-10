# SPDX-License-Identifier: MIT

import json
from pathlib import Path
from typing import Dict

from _types import SphinxExtensionMeta
from sphinx.application import Sphinx
from sphinx.util.fileutil import copy_asset_file

SCRIPT_PATH = "_templates/api_redirect.js_t"


def collect_redirects(app: Sphinx):
    # mapping of html node id (i.e., thing after "#" in URLs) to the correct page name
    # e.g, api.html#disnake.Thread => api/channels.html
    mapping: Dict[str, str] = {}

    # see https://www.sphinx-doc.org/en/master/extdev/domainapi.html#sphinx.domains.Domain.get_objects
    domain = app.env.domains["py"]
    for _, _, _, document, html_node_id, _ in domain.get_objects():
        mapping[html_node_id] = document + ".html"

    return mapping


def copy_redirect_script(app: Sphinx, exception: Exception) -> None:
    if app.builder.format != "html" or exception:
        return

    redirect_mapping = collect_redirects(app)
    context = {"redirect_data": json.dumps(redirect_mapping)}

    # sanity check
    assert Path(SCRIPT_PATH).exists()  # noqa: S101

    copy_asset_file(
        SCRIPT_PATH,
        str(Path(app.outdir, "_static", "api_redirect.js")),
        context=context,
    )


def setup(app: Sphinx) -> SphinxExtensionMeta:
    app.connect("build-finished", copy_redirect_script)

    return {
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
