# SPDX-License-Identifier: MIT

from typing import Dict, Literal, Optional

import pytest

from disnake.permissions import PermissionOverwrite, Permissions


class TestPermissions:
    def test_init_permissions_keyword_arguments(self) -> None:
        perms = Permissions(manage_messages=True)

        assert perms.manage_messages is True

        # check we only have the manage message permission
        assert perms.value == Permissions.manage_messages.flag

    def test_init_permissions_keyword_arguments_with_aliases(self) -> None:
        assert Permissions(read_messages=True, view_channel=False).value == 0
        assert Permissions(view_channel=True, read_messages=False).value == 0

        assert Permissions(read_messages=False, view_channel=True).value == 1024
        assert Permissions(view_channel=False, read_messages=True).value == 1024

    def test_init_invalid_value(self) -> None:
        with pytest.raises(TypeError, match="Expected int parameter, received str instead."):
            Permissions("h")  # type: ignore

    def test_init_invalid_perms(self) -> None:
        with pytest.raises(TypeError, match="'h' is not a valid permission name."):
            Permissions(h=True)  # type: ignore

    @pytest.mark.parametrize(
        ("perms_int", "other_int", "expected"),
        [
            (0b11, 0b10, False),
            (0b10, 0b10, True),
            (0b01, 0b11, True),
        ],
    )
    def test_is_subset(self, perms_int: int, other_int: int, expected: bool) -> None:
        perms = Permissions(perms_int)
        other = Permissions(other_int)
        assert perms.is_subset(other) is expected

    def test_is_subset_only_permissions(self) -> None:
        perms = Permissions()
        with pytest.raises(TypeError, match="cannot compare Permissions with int"):
            perms.is_subset(5)  # type: ignore

    @pytest.mark.parametrize(
        ("perms_int", "other_int", "expected"),
        [
            (0b11, 0b10, True),
            (0b10, 0b10, True),
            (0b01, 0b11, False),
        ],
    )
    def test_is_superset(self, perms_int: int, other_int: int, expected: bool) -> None:
        perms = Permissions(perms_int)
        other = Permissions(other_int)
        assert perms.is_superset(other) is expected

    def test_is_superset_only_permissions(self) -> None:
        perms = Permissions()
        with pytest.raises(TypeError, match="cannot compare Permissions with int"):
            perms.is_superset(5)  # type: ignore

    @pytest.mark.parametrize(
        ("perms_int", "other_int", "expected"),
        [
            (0b11, 0b10, False),
            (0b10, 0b10, False),
            (0b01, 0b11, True),
        ],
    )
    def test_is_strict_subset(self, perms_int: int, other_int: int, expected: bool) -> None:
        perms = Permissions(perms_int)
        other = Permissions(other_int)
        assert perms.is_strict_subset(other) is expected

    @pytest.mark.parametrize(
        ("perms_int", "other_int", "expected"),
        [
            (0b11, 0b10, True),
            (0b10, 0b10, False),
            (0b01, 0b11, False),
        ],
    )
    def test_is_strict_superset(self, perms_int: int, other_int: int, expected: bool) -> None:
        perms = Permissions(perms_int)
        other = Permissions(other_int)

        assert perms.is_strict_superset(other) is expected

    @pytest.mark.parametrize(
        ("perms_dict", "update", "expected"),
        [
            (
                {"view_channel": True},
                {"move_members": True},
                {"view_channel": True, "move_members": True},
            ),
        ],
    )
    def test_update(
        self,
        perms_dict: Dict[str, bool],
        update: Dict[str, bool],
        expected: Dict[str, Literal[True]],
    ) -> None:
        perms = Permissions(**perms_dict)
        perms.update(**update)

        expected_perms = Permissions(**expected)

        assert perms.value == expected_perms.value

    @pytest.mark.parametrize(
        ("update", "expected"),
        [
            ({"read_messages": True, "view_channel": False}, 8),
            ({"view_channel": True, "read_messages": False}, 8),
            ({"read_messages": False, "view_channel": True}, 8 + 1024),
            ({"view_channel": False, "read_messages": True}, 8 + 1024),
        ],
    )
    def test_update_aliases(self, update: Dict[str, bool], expected: int) -> None:
        perms = Permissions(administrator=True)
        perms.update(**update)
        assert perms.value == expected

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
    def test_iter(self, parameters: Dict[str, bool], expected: Optional[Dict[str, bool]]) -> None:
        perms = Permissions(**parameters)
        if expected is None:
            expected = parameters
        for key, value in iter(perms):
            assert value == expected.pop(key, False)
        assert not len(expected)

    def test_update_ignores(self) -> None:
        perms = Permissions()
        perms.update(h=True)  # type: ignore

    @pytest.mark.parametrize(
        ("initial", "allow", "deny", "expected"),
        [
            (0b1010, 0b0101, 0b1111, 0b0101),
            (0b0011, 0b0100, 0b0001, 0b0110),
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
        with pytest.raises(ValueError, match="'h' is not a valid permission name."):
            PermissionOverwrite(h=True)  # type: ignore

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

        with pytest.raises(
            AttributeError, match="'PermissionOverwrite' object has no attribute 'oh'"
        ):
            po.oh = False  # type: ignore

    @pytest.mark.parametrize(
        ("allow", "deny"),
        [
            ({"view_channel": True}, {"ban_members": True}),
            ({"view_channel": True}, {"view_channel": True}),
            ({"administrator": True}, {"manage_channels": False}),
        ],
    )
    def test_from_pair(
        self,
        allow: Dict[str, bool],
        deny: Dict[str, bool],
    ) -> None:
        perm_allow = Permissions(**allow)
        perm_deny = Permissions(**deny)

        po = PermissionOverwrite.from_pair(perm_allow, perm_deny)

        # iterate over the allowed perms and assert that the overwrite is what the allowed perms are
        for perm, allowed in perm_allow:
            # get the attr from the denied perms as denied perms override the allow list in from_pair
            if allowed and not getattr(perm_deny, perm):
                assert getattr(po, perm) is True
            else:
                assert getattr(po, perm) is not True

        for perm, denied in deny.items():
            if denied:
                assert getattr(po, perm) is False
            else:
                assert getattr(po, perm) is not False

    @pytest.mark.parametrize(
        ("allow", "deny"),
        [
            # these intentionally do not interfere with each other
            (0b1, 0b10),
            (0x313, 0x424),
            (0x69420, 0x2301),
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
        po.update(h=True)  # type: ignore
        assert not hasattr(po, "h")

    @pytest.mark.parametrize(
        ("expected"),
        [
            ({"view_channel": True}),
            ({"ban_members": None}),
            ({"view_channel": True, "administrator": False, "ban_members": None}),
            ({"kick_members": False}),
        ],
    )
    def test_iter(
        self,
        expected: Dict[str, bool],
    ) -> None:
        po = PermissionOverwrite(**expected)

        for perm, value in po:
            assert expected.get(perm, None) is value
