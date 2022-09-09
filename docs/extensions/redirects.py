import json
import os
from typing import Dict

from _types import SphinxExtensionMeta
from sphinx.application import Sphinx


def main(app: Sphinx, exception: Exception) -> None:
    # mapping of html node id (i.e., thing after "#" in URLs) to the same but
    # prefixed with the right doc name
    # e.g, api.html#disnake.Thread => api/channels.html#disnake.Thread
    actual_redirects: Dict[str, str] = {}

    for domainname, domain in app.env.domains.items():
        if domainname != "py":
            continue  # skip non-python objects

        # first is the real object name - we dont need it
        # second is object's "display name" (idk what is that mmlol), we dont need it
        # third is object type (class, method etc), we too dont need it
        # sixth is whether the object is aliased (not sure what does it actually mean,
        # i guess whether you did :ref:`abcedfg <hijklm>` instead of just :ref:`hijklm`
        # idk), again, we dont need it
        for _, _, _, document, html_node_id, _ in domain.get_objects():
            actual_redirects[html_node_id] = document + ".html#" + html_node_id

    with open(os.path.join(app.outdir, "_static", "api_redirect.js"), "a") as redirects_js:
        redirect_data = json.dumps(actual_redirects)
        prefix = "const redirects_map = "

        javascript = prefix + redirect_data  # yeah, raw json doesnt look cool in js, but who cares

        redirects_js.write(javascript)


def setup(app: Sphinx) -> SphinxExtensionMeta:
    app.connect("build-finished", main)
    # app.add_config_value("redirects", {}, "env")
    return {
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
