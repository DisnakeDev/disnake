# -*- encoding: utf-8 -*-

# Original copyright notice as follows

# Copyright © 2012 New Dream Network, LLC (DreamHost)
#
# Author: Doug Hellmann <doug.hellmann@dreamhost.com>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

# changes made:
# - added typehinting
# - formatted with black
# - removed `display_toc` being forced to True

# This is done by arl and shift, not by me


from __future__ import annotations

from typing import TYPE_CHECKING, List, cast

from _types import SphinxExtensionMeta
from docutils import nodes
from sphinx import addnodes

if TYPE_CHECKING:
    from sphinx.application import Sphinx
    from sphinx.builders.html import StandaloneHTMLBuilder
    from sphinx.environment import BuildEnvironment

GROUPED_SECTIONS = {"api/": "api/index", "ext/commands/api/": "ext/commands/api/index"}


def html_page_context(app: Sphinx, pagename: str, templatename, context, doctree):
    """Event handler for the html-page-context signal.
    Modifies the context directly.
     - Replaces the `toc` value created by the HTML builder with one
       that shows all document titles and the local table of contents.
     - Sets `display_toc` to True so the table of contents is always displayed.
    """
    # only work on grouped folders
    index = next(
        (index for name, index in GROUPED_SECTIONS.items() if pagename.startswith(name)), None
    )
    if index is None:
        return

    rendered_toc = get_rendered_toctree(
        app.builder,  # type: ignore
        pagename,
        index,
        prune=False,
        collapse=False,
    )

    context["toc"] = rendered_toc
    context["display_toc"] = True
    context["parent_index"] = index


def get_rendered_toctree(builder: StandaloneHTMLBuilder, docname: str, index: str, **kwargs):
    """Build the toctree relative to the named document,
    with the given parameters, and then return the rendered
    HTML fragment.
    """
    fulltoc = build_full_toctree(
        builder,
        docname,
        index,
        **kwargs,
    )
    rendered_toc = builder.render_partial(fulltoc)["fragment"]
    return rendered_toc


def build_full_toctree(builder: StandaloneHTMLBuilder, docname: str, index: str, **kwargs):
    """Return a single toctree starting from docname containing all
    sub-document doctrees.
    """
    env: BuildEnvironment = builder.env
    doctree = env.get_doctree(index)
    toctrees: List[nodes.Element] = []
    for toctreenode in doctree.traverse(addnodes.toctree):
        toctree = env.resolve_toctree(
            docname,
            builder,
            toctreenode,
            includehidden=True,
            **kwargs,
        )
        if toctree is not None:
            toctrees.append(cast(nodes.Element, toctree))

    if not toctrees:
        raise RuntimeError("Expected at least one toctree")

    result = toctrees[0]
    for toctree in toctrees[1:]:
        result.extend(toctree.children)
    result = nodes.bullet_list("", *result.children)
    env.resolve_references(result, docname, builder)
    return result


def setup(app: Sphinx) -> SphinxExtensionMeta:
    app.connect("html-page-context", html_page_context)

    print(app.registry.transforms)

    return {
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
