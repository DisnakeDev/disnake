# SPDX-License-Identifier: MIT

from hatchling.metadata.plugin.interface import MetadataHookInterface


class CustomMetadataHook(MetadataHookInterface):
    def update(self, metadata: dict) -> None:
        metadata["optional-dependencies"]["discord"] = ["discord-disnake"]
