# SPDX-License-Identifier: MIT

import asyncio
from pathlib import Path
from typing import Iterator
from unittest import mock

import pytest

from disnake.ext.commands import errors
from disnake.ext.commands.common_bot_base import CommonBotBase

from ... import helpers


class TestExtensions:
    @pytest.fixture
    def module_root(self, tmpdir: Path) -> Iterator[str]:
        with helpers.chdir_module(tmpdir):
            yield str(tmpdir)

    @pytest.fixture
    def bot(self):
        with mock.patch.object(asyncio, "get_event_loop", mock.Mock()), mock.patch.object(
            CommonBotBase, "_fill_owners", mock.Mock()
        ):
            bot = CommonBotBase()
        return bot

    def test_find_path_invalid(self, bot: CommonBotBase) -> None:
        with pytest.raises(ValueError, match=r"Paths outside the cwd are not supported"):
            bot.find_extensions("../../etc/passwd")

    def test_find(self, bot: CommonBotBase, module_root: str) -> None:
        helpers.create_dirs(module_root, {"test_cogs": {"__init__.py": "", "admin.py": ""}})

        assert bot.find_extensions("test_cogs")

        with pytest.raises(errors.ExtensionError, match=r"Unable to find root module 'other_cogs'"):
            bot.find_extensions("other_cogs")

        with pytest.raises(
            errors.ExtensionError, match=r"Module 'test_cogs.admin' is not a package"
        ):
            bot.find_extensions(".admin", package="test_cogs")
