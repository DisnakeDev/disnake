# SPDX-License-Identifier: MIT

"""Discord API Wrapper
~~~~~~~~~~~~~~~~~~~

A basic wrapper for the Discord API.

:copyright: (c) 2015-2021 Rapptz, 2021-present Disnake Development
:license: MIT, see LICENSE for more details.

"""

__title__ = "disnake"
__author__ = "Rapptz, EQUENOS"
__license__ = "MIT"
__copyright__ = "Copyright 2015-present Rapptz, 2021-present EQUENOS"
__version__ = "2.9.0a"

__path__ = __import__("pkgutil").extend_path(__path__, __name__)

import logging
from typing import Literal, NamedTuple

from disnake import (  # explicitly re-export modules
    abc as abc,
    opus as opus,
    ui as ui,
    utils as utils,
)
from disnake.activity import *
from disnake.app_commands import *
from disnake.appinfo import *
from disnake.application_role_connection import *
from disnake.asset import *
from disnake.audit_logs import *
from disnake.automod import *
from disnake.bans import *
from disnake.channel import *
from disnake.client import *
from disnake.colour import *
from disnake.components import *
from disnake.custom_warnings import *
from disnake.embeds import *
from disnake.emoji import *
from disnake.enums import *
from disnake.errors import *
from disnake.file import *
from disnake.flags import *
from disnake.guild import *
from disnake.guild_preview import *
from disnake.guild_scheduled_event import *
from disnake.i18n import *
from disnake.integrations import *
from disnake.interactions import *
from disnake.invite import *
from disnake.member import *
from disnake.mentions import *
from disnake.message import *
from disnake.object import *
from disnake.partial_emoji import *
from disnake.permissions import *
from disnake.player import *
from disnake.raw_models import *
from disnake.reaction import *
from disnake.role import *
from disnake.shard import *
from disnake.stage_instance import *
from disnake.sticker import *
from disnake.team import *
from disnake.template import *
from disnake.threads import *
from disnake.user import *
from disnake.voice_client import *
from disnake.voice_region import *
from disnake.webhook import *
from disnake.welcome_screen import *
from disnake.widget import *


class VersionInfo(NamedTuple):
    major: int
    minor: int
    micro: int
    releaselevel: Literal["alpha", "beta", "candidate", "final"]
    serial: int


version_info: VersionInfo = VersionInfo(major=2, minor=9, micro=0, releaselevel="alpha", serial=0)

logging.getLogger(__name__).addHandler(logging.NullHandler())
