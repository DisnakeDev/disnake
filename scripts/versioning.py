# SPDX-License-Identifier: MIT

import copy
from typing import Any, Dict, Optional

import packaging.version
import versioningit


def template_fields(
    *,
    version: str,
    description: Optional[versioningit.VCSDescription],
    base_version: Optional[str],
    next_version: Optional[str],
    params: Dict[str, Any],
) -> Dict[str, Any]:
    """Implements the ``"basic"`` ``template-fields`` method"""
    params = copy.deepcopy(params)
    parsed_version = packaging.version.parse(version)
    fields: Dict[str, Any] = {}
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
        releaselevel = releaselevels.get(parsed_version.pre[0], "final")
    else:
        releaselevel = "final"

    fields["version_tuple"] = (
        parsed_version.major,
        parsed_version.minor,
        parsed_version.micro,
        releaselevel,
        parsed_version.dev or 0,
    )
    try:
        fields["normalized_version"] = str(packaging.version.Version(version))
    except ValueError:
        fields["normalized_version"] = version
    return fields
