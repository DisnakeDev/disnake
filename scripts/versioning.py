# SPDX-License-Identifier: MIT

# This script runs as part of the wheel building process,
# all dependencies MUST be included in pyproject.toml
from __future__ import annotations

from typing import TYPE_CHECKING, Any

import packaging.version

if TYPE_CHECKING:
    import versioningit


def template_fields(
    *,
    version: str,
    description: versioningit.VCSDescription | None,
    base_version: str | None,
    next_version: str | None,
    params: dict[str, Any],
) -> dict[str, Any]:
    """Implement a custom template_fields function for Disnake."""
    # params = copy.deepcopy(params)
    parsed_version = packaging.version.parse(version)
    fields: dict[str, Any] = {}
    if description is not None:
        fields.update(description.fields)
        fields["branch"] = description.branch
    fields["version"] = version

    releaselevels = {
        "a": "alpha",
        "b": "beta",
        "rc": "candidate",
        "": "final",
    }

    if parsed_version.pre:
        pre = parsed_version.pre
        releaselevel = releaselevels.get(pre[0], "final")
        serial = pre[1]
    else:
        releaselevel = "final"
        serial = 0

    fields["version_tuple"] = (
        parsed_version.major,
        parsed_version.minor,
        parsed_version.micro,
        releaselevel,
        serial,
    )
    return fields
