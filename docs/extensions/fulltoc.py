# SPDX-License-Identifier: Apache-2.0

"""A sphinx extension to display specific pages' table of contents in the context
of a parent page.
"""

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

# Changes made:
# - added typehinting
# - formatted with black
# - refactored generated toc to suit project documentation structure

from __future__ import annotations

from typing import TYPE_CHECKING, List, cast

from _types import SphinxExtensionMeta
from docutils import nodes
from sphinx import addnodes

if TYPE_CHECKING:
    from sphinx.application import Sphinx
    from sphinx.builders.html import StandaloneHTMLBuilder
    from sphinx.environment import BuildEnvironment

# {prefix: index_doc} mapping
# Any document that matches `prefix` will use `index_doc`'s toctree instead.
GROUPED_SECTIONS = {"api/": "api/index", "ext/commands/api/": "ext/commands/api/index"}


def html_page_context(app: Sphinx, docname: str, templatename, context, doctree):
    """Event handler for the html-page-context signal.

    Modifies the context directly, if `docname` matches one of the items in `GROUPED_SECTIONS`.

    - Replaces the default `toc` created by the builder with one
      that shows all document titles and the local TOC.
    - Sets `display_toc` to True so the TOC is always displayed.
    - Sets `parent_index` (used in custom `localtoc.html`) such that the "Table of Contents"
      link on top of the TOC points to the index page, not the current page.

    Note that this doesn't replace the `toctree` callback in the context, since
    we're currently not using it in any templates.
    """
    # only work on grouped folders
    index = next(
        (index for name, index in GROUPED_SECTIONS.items() if docname.startswith(name)), None
    )
    if index is None:
        return

    rendered_toc = get_rendered_toctree(
        app.builder,  # type: ignore
        docname,
        index,
        # don't prune tree at a certain depth; always include all entries
        prune=False,
        # don't collapse sibling entries; this will be done through javascript later,
        # collapsing here would remove the elements from the output entirely
        collapse=False,
        # include :hidden: toctrees
        includehidden=True,
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

    This is similar to `sphinx.environment.adapters.TocTree.get_toctree_for`,
    but instead of generating a toctree for `docname` in the context of the root doc,
    this generates one for `docname` in the context of `index`.
    """
    env: BuildEnvironment = builder.env
    doctree = env.get_doctree(index)
    toctrees: List[nodes.Element] = []
    for toctreenode in doctree.traverse(addnodes.toctree):
        toctree = env.resolve_toctree(
            docname,
            builder,
            toctreenode,
            **kwargs,
        )
        if toctree is not None:
            toctrees.append(cast(nodes.Element, toctree))

    if not toctrees:
        raise RuntimeError("Expected at least one toctree")

    result = toctrees[0]
    for toctree in toctrees[1:]:
        result.extend(toctree.children)
    return nodes.bullet_list("", *result.children)


def setup(app: Sphinx) -> SphinxExtensionMeta:
    app.connect("html-page-context", html_page_context)

    return {
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
