# SPDX-License-Identifier: MIT
from __future__ import annotations

import functools
import inspect
from typing import TYPE_CHECKING, Any, Callable, Dict, Optional

from sphinx.environment.adapters.indexentries import IndexEntries

if TYPE_CHECKING:
    from _types import SphinxExtensionMeta
    from docutils import nodes
    from sphinx.application import Sphinx
    from sphinx.config import Config
    from sphinx.writers.html5 import HTML5Translator

if TYPE_CHECKING:
    translator_base = HTML5Translator
else:
    translator_base = object


class CustomHTML5TranslatorMixin(translator_base):
    def visit_table(self, node: nodes.table) -> None:
        self.body.append('<div class="table-wrapper">')
        super().visit_table(node)

    def depart_table(self, node: nodes.table) -> None:
        super().depart_table(node)
        self.body.append("</div>")


def set_translator(app: Sphinx) -> None:
    if app.builder.format != "html":
        return

    # Insert the `CustomHTML5TranslatorMixin` mixin into all defined
    # translator types, as well as the default translator if not registered already

    translators = app.registry.translators.copy()
    translators.setdefault(app.builder.name, app.builder.default_translator_class)

    for name, cls in translators.items():
        translator = type(
            "CustomHTML5Translator",
            (CustomHTML5TranslatorMixin, cls),
            {},
        )
        app.set_translator(name, translator, override=True)


def patch_genindex(*args: Any) -> None:
    # Instead of overriding `write_genindex` in a custom builder and
    # copying the entire method body while only changing one parameter (group_entries),
    # we just patch the method we want to change instead.
    new_create_index = functools.partialmethod(IndexEntries.create_index, group_entries=False)
    IndexEntries.create_index = new_create_index  # type: ignore


def patch_ogp_callback(original: Callable[..., None]):
    # Patches the given html-page-context callback to only be called if
    # the page does not contain an `:ogp_disable:` meta field
    def patched(
        app: Sphinx,
        pagename: str,
        templatename: str,
        context: Dict[str, Any],
        doctree: Optional[nodes.document],
    ):
        fields = context.get("meta") or {}
        if "ogp_disable" not in fields:
            original(app, pagename, templatename, context, doctree)

    return patched


def hook_html_page_context(app: Sphinx, config: Config) -> None:
    for listener in list(app.events.listeners.get("html-page-context", [])):
        module_name = inspect.getmodule(listener.handler).__name__  # type: ignore

        # prevent installation of mathjax script, which gets installed due to
        # https://github.com/readthedocs/sphinx-hoverxref/commit/7c4655092c482bd414b1816bdb4f393da117062a
        if module_name == "sphinx.ext.mathjax":
            app.disconnect(listener.id)

        # patch opengraph handler to add `:ogp_disable:` behavior
        elif module_name == "sphinxext.opengraph":
            app.disconnect(listener.id)
            app.connect("html-page-context", patch_ogp_callback(listener.handler))


def setup(app: Sphinx) -> SphinxExtensionMeta:
    app.connect("config-inited", patch_genindex)
    app.connect("config-inited", hook_html_page_context)
    app.connect("builder-inited", set_translator)

    return {
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
