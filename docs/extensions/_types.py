from typing import Optional, TypedDict


class _SphinxExtensionMeta(TypedDict, total=False):
    version: str
    env_version: int
    parallel_read_safe: bool
    parallel_write_safe: bool


SphinxExtensionMeta = Optional[_SphinxExtensionMeta]
