from sphinx.application import Sphinx


def setup(app: Sphinx) -> None:
    for index, listener in enumerate(app.events.listeners.get("doctree-resolved")):  # type: ignore
        if listener.handler.__qualname__ == "process_external_version_warning_banner":
            print("OMFG IT WORKS")
            print("BEFORE: %s" % app.events.listeners.get("doctree-resolved"))
            print()
            app.events.listeners["doctree-resolved"].pop(index)
            print("AFTER: %s" % app.events.listeners.get("doctree-resolved"))
