# SPDX-License-Identifier: MIT
import disnake


def make_role(primary=None, secondary=None, tertiary=None):
    role = object.__new__(disnake.Role)
    role.color = primary
    role.secondary_color = secondary
    role.tertiary_color = tertiary
    return role


def test_is_gradient_true():
    r = make_role(primary=0x111111, secondary=0x222222, tertiary=None)
    assert r.is_gradient is True
    assert r.is_holographic is False


def test_is_holographic_true():
    r = make_role(primary=0x111111, secondary=0x222222, tertiary=0x333333)
    assert r.is_holographic is True
    assert r.is_gradient is False


def test_basic_role():
    r = make_role(primary=0x111111, secondary=None, tertiary=None)
    assert r.is_gradient is False
    assert r.is_holographic is False
