# SPDX-License-Identifier: MIT

"""disnake.webhook
~~~~~~~~~~~~~~

Webhook support

:copyright: (c) 2015-2021 Rapptz, 2021-present Disnake Development
:license: MIT, see LICENSE for more details.

"""

from disnake.webhook import async_, sync
from disnake.webhook.async_ import *
from disnake.webhook.sync import *

__all__ = []
__all__.extend(async_.__all__)
__all__.extend(sync.__all__)
