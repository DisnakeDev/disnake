import functools
import inspect
from typing import Any, Dict, Type

from _types import SphinxExtensionMeta
from docutils import nodes
from sphinx.application import Sphinx
from sphinx.builders.html import StandaloneHTMLBuilder
from sphinx.config import Config
from sphinx.environment.adapters.indexentries import IndexEntries
from sphinx.writers.html5 import HTML5Translator


class DPYHTML5Translator(HTML5Translator):
    def visit_table(self, node: nodes.table) -> None:
        self.body.append('<div class="table-wrapper">')
        super().visit_table(node)

    def depart_table(self, node: nodes.table) -> None:
        super().depart_table(node)
        self.body.append("</div>")


class DPYStandaloneHTMLBuilder(StandaloneHTMLBuilder):
    pass


def add_custom_jinja2(app: Sphinx) -> None:
    tests: Dict[str, Any] = app.builder.templates.environment.tests
    tests["prefixedwith"] = str.startswith
    tests["suffixedwith"] = str.endswith


def add_builders(app: Sphinx) -> None:
    """This is necessary because RTD injects their own for some reason."""
    app.set_translator("html", DPYHTML5Translator, override=True)
    app.add_builder(DPYStandaloneHTMLBuilder, override=True)

    try:
        original = app.registry.builders["readthedocs"]
    except KeyError:
        pass
    else:
        injected_mro = tuple(
            base if base is not StandaloneHTMLBuilder else DPYStandaloneHTMLBuilder
            for base in original.mro()[1:]
        )
        new_builder: Type[DPYStandaloneHTMLBuilder] = type(original.__name__, injected_mro, {"name": "readthedocs"})  # type: ignore
        app.set_translator("readthedocs", DPYHTML5Translator, override=True)
        app.add_builder(new_builder, override=True)


def patch_genindex() -> None:
    # Instead of overriding `write_genindex` in a custom builder and
    # copying the entire method body while only changing one parameter (group_entries),
    # we just patch the method we want to change instead.
    new_create_index = functools.partialmethod(IndexEntries.create_index, group_entries=False)
    IndexEntries.create_index = new_create_index  # type: ignore


def disable_mathjax(app: Sphinx, config: Config) -> None:
    # prevent installation of mathjax script, which gets installed due to
    # https://github.com/readthedocs/sphinx-hoverxref/commit/7c4655092c482bd414b1816bdb4f393da117062a
    #
    # inspired by https://github.com/readthedocs/sphinx-hoverxref/blob/003b84fee48262f1a969c8143e63c177bd98aa26/hoverxref/extension.py#L151

    for listener in app.events.listeners.get("html-page-context", []):
        module_name = inspect.getmodule(listener.handler).__name__  # type: ignore
        if module_name == "sphinx.ext.mathjax":
            app.disconnect(listener.id)


def setup(app: Sphinx) -> SphinxExtensionMeta:
    add_builders(app)
    patch_genindex()
    app.connect("config-inited", disable_mathjax)
    app.connect("builder-inited", add_custom_jinja2)
