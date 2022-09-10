from sphinx.application import Sphinx


def main(app: Sphinx) -> None:
    return
    for index, listener in enumerate(app.events.listeners.get("doctree-resolved")):  # type: ignore
        if listener.handler.__qualname__ == "process_external_version_warning_banner":
            app.events.listeners["doctree-resolved"].pop(index)


def setup(app: Sphinx) -> None:
    app.connect("builder-inited", main)
