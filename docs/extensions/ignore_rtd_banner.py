from _types import SphinxExtensionMeta
from docutils import nodes
from sphinx.application import Sphinx
from sphinx.errors import ExtensionError


def custom(app, doctree, fromdocname):
    """
    Add warning banner for external versions in every page.

    If the version type is external this will show a warning banner
    at the top of each page of the documentation.

    Adopted from https://github.com/readthedocs/readthedocs-sphinx-ext
    """
    if not app.config.readthedocs_build_url or not app.config.readthedocs_vcs_url:
        return

    if isinstance(doctree, nodes.bullet_list):
        return

    is_gitlab = app.config.html_context.get("display_gitlab")
    name = "merge request" if is_gitlab else "pull request"

    build_url = app.config.readthedocs_build_url
    build_url_node = nodes.reference(
        "",
        "",
        nodes.Text("was created "),
        internal=False,
        refuri=build_url,
    )

    pr_number = app.config.html_context.get("current_version")
    pr_number = "#{number}".format(number=pr_number)
    vcs_url = app.config.readthedocs_vcs_url
    vcs_url_node = nodes.reference(
        "",
        "",
        nodes.Text(pr_number),
        internal=False,
        refuri=vcs_url,
    )

    children = [
        nodes.Text("This page "),
        build_url_node,  # was created
        nodes.Text("from a {name} (".format(name=name)),
        vcs_url_node,  # #123
        nodes.Text(")."),
    ]
    prose = nodes.paragraph("", "", *children)
    warning_node = nodes.warning(prose, prose)
    doctree.insert(0, warning_node)


def main(app: Sphinx) -> None:
    for index, listener in enumerate(app.events.listeners.get("doctree-resolved")):  # type: ignore
        if listener.handler.__qualname__ == "process_external_version_warning_banner":
            app.events.listeners["doctree-resolved"].pop(index)


def setup(app: Sphinx) -> SphinxExtensionMeta:
    app.connect("builder-inited", main)
    app.connect("doctree-resolved", custom)

    try:
        app.add_config_value("readthedocs_vcs_url", "", "html")
        app.add_config_value("readthedocs_build_url", "", "html")
    except ExtensionError:
        pass

    return {
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
