# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import List, Literal, Optional, TypedDict

from .snowflake import Snowflake
from .user import PartialUser

TeamMembershipState = Literal[1, 2]


class TeamMember(TypedDict):
    user: PartialUser
    membership_state: TeamMembershipState
    permissions: List[str]
    team_id: Snowflake


class Team(TypedDict):
    id: Snowflake
    name: str
    owner_user_id: Snowflake
    members: List[TeamMember]
    icon: Optional[str]
