# SPDX-License-Identifier: MIT
from __future__ import annotations

import asyncio
import importlib
import inspect
import re
from collections import defaultdict
from typing import TYPE_CHECKING, ClassVar, DefaultDict, Dict, List, NamedTuple, Optional, Tuple

from docutils import nodes
from sphinx import addnodes
from sphinx.locale import _
from sphinx.util.docutils import SphinxDirective

if TYPE_CHECKING:
    from sphinx.application import Sphinx
    from sphinx.environment import BuildEnvironment
    from sphinx.util.typing import OptionSpec
    from sphinx.writers.html import HTMLTranslator

    from ._types import SphinxExtensionMeta


class attributetable(nodes.General, nodes.Element):
    pass


class attributetablecolumn(nodes.General, nodes.Element):
    pass


class attributetabletitle(nodes.TextElement):
    pass


class attributetableplaceholder(nodes.General, nodes.Element):
    pass


class attributetablebadge(nodes.TextElement):
    pass


class attributetable_item(nodes.Part, nodes.Element):
    pass


def visit_attributetable_node(self: HTMLTranslator, node: nodes.Element) -> None:
    class_ = node["python-class"]
    self.body.append(f'<div class="py-attribute-table" data-move-to-id="{class_}">')


def visit_attributetablecolumn_node(self: HTMLTranslator, node: nodes.Element) -> None:
    self.body.append(self.starttag(node, "div", CLASS="py-attribute-table-column"))


def visit_attributetabletitle_node(self: HTMLTranslator, node: nodes.Element) -> None:
    self.body.append(self.starttag(node, "span"))


def visit_attributetablebadge_node(self: HTMLTranslator, node: nodes.Element) -> None:
    """Add a class to each badge of the type that it is."""
    badge_type: str = node["badge-type"]
    if badge_type not in ("coroutine", "decorator", "method", "classmethod"):
        raise RuntimeError(f"badge_type {badge_type} is currently unsupported")
    attributes = {
        "class": f"badge-{badge_type}",
    }
    self.body.append(self.starttag(node, "span", **attributes))


def visit_attributetable_item_node(self: HTMLTranslator, node: nodes.Element) -> None:
    self.body.append(self.starttag(node, "li"))


def depart_attributetable_node(self: HTMLTranslator, node: nodes.Element) -> None:
    self.body.append("</div>")


def depart_attributetablecolumn_node(self: HTMLTranslator, node: nodes.Element) -> None:
    self.body.append("</div>")


def depart_attributetabletitle_node(self: HTMLTranslator, node: nodes.Element) -> None:
    self.body.append("</span>")


def depart_attributetablebadge_node(self: HTMLTranslator, node: nodes.Element) -> None:
    self.body.append("</span>")


def depart_attributetable_item_node(self: HTMLTranslator, node: nodes.Element) -> None:
    self.body.append("</li>")


_name_parser_regex = re.compile(r"(?P<module>[\w.]+\.)?(?P<name>\w+)")


class PyAttributeTable(SphinxDirective):
    has_content = False
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec: ClassVar[OptionSpec] = {}

    def parse_name(self, content: str) -> Tuple[str, Optional[str]]:
        match = _name_parser_regex.match(content)
        path, name = match.groups() if match else (None, None)
        if path:
            modulename = path.rstrip(".")
        else:
            modulename = self.env.temp_data.get("autodoc:module")
            if not modulename:
                modulename = self.env.ref_context.get("py:module")
        if modulename is None:
            raise RuntimeError(f"modulename somehow None for {content} in {self.env.docname}.")

        return modulename, name

    def run(self) -> List[nodes.Node]:
        """If you're curious on the HTML this is meant to generate:

        <div class="py-attribute-table">
            <div class="py-attribute-table-column">
                <span>_('Attributes')</span>
                <ul>
                    <li>
                        <a href="...">
                    </li>
                </ul>
            </div>
            <div class="py-attribute-table-column">
                <span>_('Methods')</span>
                <ul>
                    <li>
                        <a href="..."></a>
                        <span class="py-attribute-badge" title="decorator">D</span>
                    </li>
                </ul>
            </div>
        </div>

        However, since this requires the tree to be complete
        and parsed, it'll need to be done at a different stage and then
        replaced.
        """
        content = self.arguments[0].strip()
        node = attributetableplaceholder("")
        modulename, name = self.parse_name(content)
        node["python-doc"] = self.env.docname
        node["python-module"] = modulename
        node["python-class"] = name
        node["python-full-name"] = f"{modulename}.{name}"
        return [node]


def build_lookup_table(env: BuildEnvironment) -> Dict[str, List[str]]:
    # Given an environment, load up a lookup table of
    # full-class-name: objects
    result: DefaultDict[str, List[str]] = defaultdict(list)
    domain = env.domains["py"]

    ignored = {
        "data",
        "exception",
        "module",
        "class",
    }

    for fullname, _unused, objtype, _unused, _unused, _unused in domain.get_objects():
        if objtype in ignored:
            continue

        classname, _unused, child = fullname.rpartition(".")
        result[classname].append(child)

    return result


class TableElement(NamedTuple):
    fullname: str
    label: str
    badge: Optional[attributetablebadge]


def process_attributetable(app: Sphinx, doctree: nodes.document, docname: str) -> None:
    env = app.builder.env

    lookup = build_lookup_table(env)
    for node in doctree.traverse(attributetableplaceholder):
        modulename, classname, fullname = (
            node["python-module"],
            node["python-class"],
            node["python-full-name"],
        )
        groups = get_class_results(lookup, modulename, classname, fullname)
        table = attributetable("")
        for label, subitems in groups.items():
            if not subitems:
                continue
            table.append(class_results_to_node(label, sorted(subitems, key=lambda c: c.label)))

        table["python-class"] = fullname

        if not table:
            node.replace_self([])
        else:
            node.replace_self([table])


def get_class_results(
    lookup: Dict[str, List[str]], modulename: str, name: str, fullname: str
) -> Dict[str, List[TableElement]]:
    module = importlib.import_module(modulename)
    cls = getattr(module, name)

    groups: Dict[str, List[TableElement]] = {
        _("Attributes"): [],
        _("Methods"): [],
    }

    try:
        members = lookup[fullname]
    except KeyError:
        return groups

    for attr in members:
        attrlookup = f"{fullname}.{attr}"
        key = _("Attributes")
        badge = None
        label = attr
        value = None

        for base in cls.__mro__:
            value = base.__dict__.get(attr)
            if value is not None:
                break

        if value is not None:
            doc = value.__doc__ or ""
            if asyncio.iscoroutinefunction(value) or doc.startswith("|coro|"):
                key = _("Methods")
                badge = attributetablebadge("async", "async")
                badge["badge-type"] = _("coroutine")
            elif isinstance(value, classmethod):
                key = _("Methods")
                label = f"{name}.{attr}"
                badge = attributetablebadge("cls", "cls")
                badge["badge-type"] = _("classmethod")
            elif inspect.isfunction(value):
                if doc.lstrip().startswith(("A decorator", "A shortcut decorator")):
                    # finicky but surprisingly consistent
                    badge = attributetablebadge("@", "@")
                    badge["badge-type"] = _("decorator")
                    key = _("Methods")
                else:
                    key = _("Methods")
                    badge = attributetablebadge("def", "def")
                    badge["badge-type"] = _("method")

        groups[key].append(TableElement(fullname=attrlookup, label=label, badge=badge))

    return groups


def class_results_to_node(key: str, elements: List[TableElement]) -> attributetablecolumn:
    title = attributetabletitle(key, key)
    ul = nodes.bullet_list("")
    ul["classes"].append("py-attribute-table-list")
    for element in elements:
        ref = nodes.reference(
            "",
            "",
            internal=True,
            refuri="#" + element.fullname,
            anchorname="",
            *[nodes.Text(element.label)],
        )
        para = addnodes.compact_paragraph("", "", ref)
        if element.badge is not None:
            ul.append(attributetable_item("", element.badge, para))
        else:
            ul.append(attributetable_item("", para))

    return attributetablecolumn("", title, ul)


def setup(app: Sphinx) -> SphinxExtensionMeta:
    app.add_directive("attributetable", PyAttributeTable)
    app.add_node(attributetable, html=(visit_attributetable_node, depart_attributetable_node))
    app.add_node(
        attributetablecolumn,
        html=(visit_attributetablecolumn_node, depart_attributetablecolumn_node),
    )
    app.add_node(
        attributetabletitle, html=(visit_attributetabletitle_node, depart_attributetabletitle_node)
    )
    app.add_node(
        attributetablebadge, html=(visit_attributetablebadge_node, depart_attributetablebadge_node)
    )
    app.add_node(
        attributetable_item, html=(visit_attributetable_item_node, depart_attributetable_item_node)
    )
    app.add_node(attributetableplaceholder)
    app.connect("doctree-resolved", process_attributetable)

    return {
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
