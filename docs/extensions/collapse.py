# SPDX-License-Identifier: MIT
from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from docutils import nodes
from docutils.parsers.rst import Directive, directives

if TYPE_CHECKING:
    from sphinx.application import Sphinx
    from sphinx.util.typing import OptionSpec
    from sphinx.writers.html import HTMLTranslator

    from ._types import SphinxExtensionMeta


class collapse(nodes.General, nodes.Element):
    pass


def visit_collapse_node(self: HTMLTranslator, node: nodes.Element) -> None:
    attrs = {"open": ""} if node["open"] else {}
    self.body.append(self.starttag(node, "details", **attrs))
    self.body.append("<summary></summary>")


def depart_collapse_node(self: HTMLTranslator, node: nodes.Element) -> None:
    self.body.append("</details>\n")


class CollapseDirective(Directive):
    has_content = True

    optional_arguments = 1
    final_argument_whitespace = True

    option_spec: ClassVar[OptionSpec] = {"open": directives.flag}

    def run(self):
        self.assert_has_content()
        node = collapse(
            "\n".join(self.content),
            open="open" in self.options,
        )

        classes = directives.class_option(self.arguments[0] if self.arguments else "")
        node["classes"].extend(classes)

        self.state.nested_parse(self.content, self.content_offset, node)
        return [node]


def setup(app: Sphinx) -> SphinxExtensionMeta:
    app.add_node(collapse, html=(visit_collapse_node, depart_collapse_node))
    app.add_directive("collapse", CollapseDirective)

    return {
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
