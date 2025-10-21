# SPDX-License-Identifier: MIT

from typing import Any, Optional

import packaging.version
import versioningit


def template_fields(
    *,
    version: str,
    description: Optional[versioningit.VCSDescription],
    base_version: Optional[str],
    next_version: Optional[str],
    params: dict[str, Any],
) -> dict[str, Any]:
    """Implements the ``"basic"`` ``template-fields`` method"""
    # params = copy.deepcopy(params)
    parsed_version = packaging.version.parse(version)
    fields: dict[str, Any] = {}
    if description is not None:
        fields.update(description.fields)
        fields["branch"] = description.branch
    if base_version is not None:
        fields["base_version"] = base_version
    if next_version is not None:
        fields["next_version"] = next_version
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
    try:
        fields["normalized_version"] = str(packaging.version.Version(version))
    except ValueError:
        fields["normalized_version"] = version
    return fields
