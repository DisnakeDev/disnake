# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import Any, Dict

import packaging.version


def build(setup_kwargs: Dict[str, Any]):
    # modify the version
    version = setup_kwargs["version"]
    if version:
        parsed_version = packaging.version.Version(version)
        if parsed_version.pre:
            # remove the version id as we add our own
            version = version[: -1 * len(str(parsed_version.pre[1]))]
            print(version)
            # append version identifier based on commit count
            try:
                import subprocess  # noqa: S404

                p = subprocess.Popen(  # noqa: S603,S607
                    ["git", "rev-list", "--count", "HEAD"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                out, _err = p.communicate()
                if out:
                    version += out.decode("utf-8").strip()
                p = subprocess.Popen(  # noqa: S603,S607
                    ["git", "rev-parse", "--short", "HEAD"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                out, _err = p.communicate()
                if out:
                    version += "+g" + out.decode("utf-8").strip()
            except Exception:
                pass
            else:
                print(version)
                setup_kwargs.update({"version": version})
