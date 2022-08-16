import inspect

from sphinx.application import Sphinx
from sphinx.builders.html import StandaloneHTMLBuilder
from sphinx.config import Config
from sphinx.environment.adapters.indexentries import IndexEntries
from sphinx.writers.html5 import HTML5Translator


class DPYHTML5Translator(HTML5Translator):
    def visit_section(self, node):
        self.section_level += 1
        self.body.append(self.starttag(node, "section"))

    def depart_section(self, node):
        self.section_level -= 1
        self.body.append("</section>\n")

    def visit_table(self, node):
        self.body.append('<div class="table-wrapper">')
        super().visit_table(node)

    def depart_table(self, node):
        super().depart_table(node)
        self.body.append("</div>")


class DPYStandaloneHTMLBuilder(StandaloneHTMLBuilder):
    # This is mostly copy pasted from Sphinx.
    def write_genindex(self) -> None:
        # the total count of lines for each index letter, used to distribute
        # the entries into two columns
        genindex = IndexEntries(self.env).create_index(self, group_entries=False)
        indexcounts = []
        for _k, entries in genindex:
            indexcounts.append(sum(1 + len(subitems) for _, (_, subitems, _) in entries))

        genindexcontext = {
            "genindexentries": genindex,
            "genindexcounts": indexcounts,
            "split_index": self.config.html_split_index,
        }

        if self.config.html_split_index:
            self.handle_page("genindex", genindexcontext, "genindex-split.html")
            self.handle_page("genindex-all", genindexcontext, "genindex.html")
            for (key, entries), count in zip(genindex, indexcounts):
                ctx = {"key": key, "entries": entries, "count": count, "genindexentries": genindex}
                self.handle_page("genindex-" + key, ctx, "genindex-single.html")
        else:
            self.handle_page("genindex", genindexcontext, "genindex.html")

    def post_process_images(self, doctree) -> None:
        super().post_process_images(doctree)

        for path in self.app.config.copy_static_images:
            self.images[path] = path.split("/")[-1]


def add_custom_jinja2(app):
    env = app.builder.templates.environment
    env.tests["prefixedwith"] = str.startswith
    env.tests["suffixedwith"] = str.endswith


def add_builders(app):
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
        new_builder = type(original.__name__, injected_mro, {"name": "readthedocs"})
        app.set_translator("readthedocs", DPYHTML5Translator, override=True)
        app.add_builder(new_builder, override=True)


def disable_mathjax(app: Sphinx, config: Config) -> None:
    # prevent installation of mathjax script, which gets installed due to
    # https://github.com/readthedocs/sphinx-hoverxref/commit/7c4655092c482bd414b1816bdb4f393da117062a
    #
    # inspired by https://github.com/readthedocs/sphinx-hoverxref/blob/003b84fee48262f1a969c8143e63c177bd98aa26/hoverxref/extension.py#L151

    for listener in app.events.listeners.get("html-page-context", []):
        module_name = inspect.getmodule(listener.handler).__name__  # type: ignore
        if module_name == "sphinx.ext.mathjax":
            app.disconnect(listener.id)


def setup(app):
    app.add_config_value("copy_static_images", [], "env")

    add_builders(app)
    app.connect("config-inited", disable_mathjax)
    app.connect("builder-inited", add_custom_jinja2)

    return {
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
