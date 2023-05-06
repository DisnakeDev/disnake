# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from . import utils
from .asset import Asset
from .enums import TeamMembershipState, try_enum
from .user import BaseUser

if TYPE_CHECKING:
    from .state import ConnectionState
    from .types.team import Team as TeamPayload, TeamMember as TeamMemberPayload

__all__ = (
    "Team",
    "TeamMember",
)


class Team:
    """Represents an application team for a bot provided by Discord.

    Attributes
    ----------
    id: :class:`int`
        The team ID.
    name: :class:`str`
        The team name.
    owner_id: :class:`int`
        The team's owner ID.
    members: List[:class:`TeamMember`]
        A list of the members in the team.

        .. versionadded:: 1.3
    """

    __slots__ = ("_state", "id", "name", "_icon", "owner_id", "members")

    def __init__(self, state: ConnectionState, data: TeamPayload) -> None:
        self._state: ConnectionState = state

        self.id: int = int(data["id"])
        self.name: str = data["name"]
        self._icon: Optional[str] = data["icon"]
        self.owner_id: Optional[int] = utils._get_as_snowflake(data, "owner_user_id")
        self.members: List[TeamMember] = [
            TeamMember(self, self._state, member) for member in data["members"]
        ]

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id} name={self.name}>"

    @property
    def icon(self) -> Optional[Asset]:
        """Optional[:class:`.Asset`]: Retrieves the team's icon asset, if any."""
        if self._icon is None:
            return None
        return Asset._from_icon(self._state, self.id, self._icon, path="team")

    @property
    def owner(self) -> Optional[TeamMember]:
        """Optional[:class:`TeamMember`]: The team's owner."""
        return utils.get(self.members, id=self.owner_id)


class TeamMember(BaseUser):
    """Represents a team member in a team.

    .. container:: operations

        .. describe:: x == y

            Checks if two team members are equal.

        .. describe:: x != y

            Checks if two team members are not equal.

        .. describe:: hash(x)

            Return the team member's hash.

        .. describe:: str(x)

            Returns the team member's username (with discriminator, if not migrated to new system yet), or global name if set.

    .. versionadded:: 1.3

    Attributes
    ----------
    name: :class:`str`
        The team member's username.
    id: :class:`int`
        The team member's unique ID.
    discriminator: :class:`str`
        The team member's discriminator.

        .. deprecated:: 2.9
            This is being phased out by Discord; the username system is moving away from ``username#discriminator``
            to users having a globally unique ``@username``.
            The value of a single zero (``"0"``) indicates that the user has been migrated to the new system.
            See the :ddocs:`changelog <change-log#unique-usernames-on-discord>` for details.
    global_name: Optional[:class:`str`]
        The team members's global display name, if set.
        This takes precedence over :attr:`.name` when shown.

        .. versionadded:: 2.9
    avatar: Optional[:class:`str`]
        The avatar hash the team member has. Could be None.
    bot: :class:`bool`
        Specifies if the user is a bot account.
    team: :class:`Team`
        The team that the member is from.
    membership_state: :class:`TeamMembershipState`
        The membership state of the member (e.g. invited or accepted)
    """

    __slots__ = ("team", "membership_state", "permissions")

    def __init__(self, team: Team, state: ConnectionState, data: TeamMemberPayload) -> None:
        self.team: Team = team
        self.membership_state: TeamMembershipState = try_enum(
            TeamMembershipState, data["membership_state"]
        )
        self.permissions: List[str] = data["permissions"]
        super().__init__(state=state, data=data["user"])

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} id={self.id} name={self.name!r} global_name={self.global_name!r}"
            f" discriminator={self.discriminator!r} membership_state={self.membership_state!r}>"
        )
