from typing import TypedDict


class SphinxExtensionMeta(TypedDict, total=False):
    version: str
    env_version: int
    parallel_read_safe: bool
    parallel_write_safe: bool
