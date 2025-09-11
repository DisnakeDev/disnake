# SPDX-License-Identifier: MIT

import sphinx.domains.changeset
from sphinx.application import Sphinx


class VersionAddedNext(sphinx.domains.changeset.VersionChange):
    """Add support for a `|vnext|` version placeholder in versionadded directives."""

    def run(self):
        # If the argument is |vnext|, replace with config version
        if self.arguments and self.arguments[0] == "|vnext|":
            # Get the version from the Sphinx config
            version = self.env.config.version
            self.arguments[0] = version
        return super().run()


def setup(app: Sphinx) -> None:
    app.add_directive("versionadded", VersionAddedNext, override=True)
    app.add_directive("versionchanged", VersionAddedNext, override=True)
    app.add_directive("deprecated", VersionAddedNext, override=True)
    app.add_directive("versionremoved", VersionAddedNext)
