from typing import Dict, Literal, Optional

import pytest

from disnake.permissions import PermissionOverwrite, Permissions


class TestPermissions:
    def test_init_permissions_keyword_arguments(self) -> None:
        perms = Permissions(manage_messages=True)

        assert perms.manage_messages is True

        # check we only have the manage message permission
        assert perms.value == Permissions.manage_messages.flag

    @pytest.mark.skip("this behavior is currently undefined")
    def test_init_permissions_keyword_arguments_with_aliases(self) -> None:
        assert Permissions(read_messages=True, view_channel=False).value == 0

    def test_init_invalid_value(self) -> None:
        with pytest.raises(TypeError, match="Expected int parameter, received str instead."):
            Permissions("h")  # type:ignore

    def test_init_invalid_perms(self) -> None:
        with pytest.raises(TypeError, match="'h' is not a valid permission name."):
            Permissions(h=True)

    @pytest.mark.parametrize(
        ("perms", "other", "expected"),
        [
            (Permissions(3), Permissions(2), False),
            (Permissions(2), Permissions(2), True),
            (Permissions(1), Permissions(3), True),
        ],
    )
    def test_is_subset(self, perms: Permissions, other: Permissions, expected: bool) -> None:
        assert perms.is_subset(other) is expected

    def test_is_subset_only_permissions(self) -> None:
        perms = Permissions()
        with pytest.raises(TypeError, match="cannot compare Permissions with int"):
            perms.is_subset(5)  # type: ignore

    @pytest.mark.parametrize(
        ("perms", "other", "expected"),
        [
            (Permissions(3), Permissions(2), True),
            (Permissions(2), Permissions(2), True),
            (Permissions(1), Permissions(3), False),
        ],
    )
    def test_is_superset(self, perms: Permissions, other: Permissions, expected: bool) -> None:
        assert perms.is_superset(other) is expected

    def test_is_superset_only_permissions(self) -> None:
        perms = Permissions()
        with pytest.raises(TypeError, match="cannot compare Permissions with int"):
            perms.is_superset(5)  # type: ignore

    @pytest.mark.parametrize(
        ("perms", "other", "expected"),
        [
            (Permissions(3), Permissions(2), False),
            (Permissions(2), Permissions(2), False),
            (Permissions(1), Permissions(3), True),
        ],
    )
    def test_is_strict_subset(self, perms: Permissions, other: Permissions, expected: bool) -> None:
        assert perms.is_strict_subset(other) is expected

    @pytest.mark.parametrize(
        ("perms", "other", "expected"),
        [
            (Permissions(3), Permissions(2), True),
            (Permissions(2), Permissions(2), False),
            (Permissions(1), Permissions(3), False),
        ],
    )
    def test_is_strict_superset(
        self, perms: Permissions, other: Permissions, expected: bool
    ) -> None:
        assert perms.is_strict_superset(other) is expected

    @pytest.mark.parametrize(
        ("perms", "update", "expected"),
        [
            [
                Permissions(view_channel=True),
                {"move_members": True},
                {"view_channel": True, "move_members": True},
            ],
        ],
    )
    def test_update(
        self, perms: Permissions, update: Dict[str, bool], expected: Dict[str, Literal[True]]
    ) -> None:
        perms.update(**update)

        expected_perms = Permissions(**expected)

        assert perms.value == expected_perms.value

    @pytest.mark.parametrize(
        ("parameters", "expected"),
        [
            ({"view_channel": True, "move_members": True}, None),
            (
                # test aliases
                {"read_messages": True, "create_forum_threads": True},
                {"view_channel": True, "send_messages": True},
            ),
        ],
    )
    def test_dict(self, parameters: dict, expected: Optional[dict]) -> None:
        perms = Permissions(**parameters)
        perms_dict = dict(perms)
        if expected is None:
            expected = parameters
        for key in perms_dict:
            if key in expected:
                assert perms_dict[key] == expected[key]
            else:
                assert perms_dict[key] is False

    def test_dict_ignores(self) -> None:
        perms = Permissions()
        perms.update(h=True)

    @pytest.mark.parametrize(
        ("initial", "allow", "deny", "expected"),
        [
            (0x1010, 0x0101, 0x1111, 0x0101),
            (0x1010, 0x0101, 0x1111, 0x0101),
            (0x0400, 0x0401, 0x5001, 0x0401),
        ],
    )
    def test_handle_overwrite(self, initial: int, allow: int, deny: int, expected: int) -> None:
        perms = Permissions(initial)
        assert perms.value == initial
        perms.handle_overwrite(allow, deny)
        assert perms.value == expected

    def test_none_is_none(self):
        perms = Permissions.none()
        assert perms.value == 0

    @pytest.mark.parametrize(
        "method_name",
        [
            "all",
            "none",
            "all_channel",
            "general",
            "membership",
            "text",
            "voice",
            "stage",
            "stage_moderator",
            "events",
            "advanced",
            "private_channel",
        ],
    )
    def test_classmethods(self, method_name: str):
        method = getattr(Permissions, method_name)

        perms: Permissions = method()
        assert isinstance(perms, Permissions)

        # check that caching does not return the same permissions instance
        perms_two: Permissions = method()
        assert perms is not perms_two
        assert perms.value == perms_two.value


class TestPermissionOverwrite:
    def test_init(self) -> None:
        perms = PermissionOverwrite(manage_messages=True)

        assert perms.manage_messages is True

    def test_init_invalid_perms(self) -> None:
        with pytest.raises(TypeError, match="'h' is not a valid permission name."):
            PermissionOverwrite(h=True)

    def test_equality(self) -> None:
        one = PermissionOverwrite()
        two = PermissionOverwrite()

        assert one is not two
        assert one == two

        two.ban_members = False
        assert one != two

    def test_set(self) -> None:
        po = PermissionOverwrite()
        po.attach_files = False
        assert po.attach_files is False

        po.attach_files = True
        assert po.attach_files is True

        po.attach_files = None
        assert po.attach_files is None

    def test_set_invalid_type(self) -> None:
        po = PermissionOverwrite()
        with pytest.raises(TypeError, match="Expected bool or NoneType, received str"):
            po.connect = "h"  # type: ignore

    @pytest.mark.parametrize(
        ("allow", "deny"),
        [
            [0x1, 0x2],
            [0x313, 0x313],
            [0x69420, 0x3600],
        ],
    )
    def test_from_pair(self, allow: int, deny: int) -> None:
        p_allow = Permissions(allow)
        p_deny = Permissions(deny)
        po = PermissionOverwrite.from_pair(p_allow, p_deny)
        for perm, allowed in p_allow:
            if allowed and not getattr(p_deny, perm):
                assert getattr(po, perm) is True
            else:
                assert getattr(po, perm) is not True

        for perm, denied in p_deny:
            if denied:
                assert getattr(po, perm) is False
            else:
                assert getattr(po, perm) is not False

    @pytest.mark.parametrize(
        ("allow", "deny"),
        [
            # these intentionally do not interfere with each other
            [0x1, 0x2],
            [0x313, 0x424],
            [0x69420, 0x2301],
        ],
    )
    def test_pair(self, allow: int, deny: int) -> None:
        og_perms_allow = Permissions(allow)
        og_perms_deny = Permissions(deny)

        po = PermissionOverwrite.from_pair(og_perms_allow, og_perms_deny)

        perms_allow, perms_deny = po.pair()

        assert perms_allow.value == og_perms_allow.value
        assert perms_deny.value == og_perms_deny.value

    def test_is_empty(self) -> None:
        po = PermissionOverwrite()
        assert po.is_empty()

        po.add_reactions = True
        assert not po.is_empty()

    def test_update(self) -> None:
        po = PermissionOverwrite()
        assert po.manage_emojis is None

        po.update(manage_emojis=True)
        assert po.manage_emojis is True

        assert po.manage_permissions is None
        po.update(manage_permissions=False)
        assert po.manage_permissions is False

        po.update(manage_permissions=None, manage_emojis=None)
        assert po.manage_permissions is None
        assert po.manage_emojis is None

        # invalid names are silently ignored
        po.update(h=True)
        assert not hasattr(po, "h")

    def test_iter(self) -> None:
        po = PermissionOverwrite()
        to_update = {
            "manage_channels": True,
            "add_reactions": True,
            "create_instant_invite": False,
            "attach_files": False,
            "use_slash_commands": None,
        }
        po.update(**to_update)

        for perm, value in po:
            assert to_update.get(perm, None) is value
