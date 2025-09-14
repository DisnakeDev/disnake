# SPDX-License-Identifier: MIT


def make_role(primary=None, secondary=None, tertiary=None):
    class DummyRole:
        def __init__(self, p, s, t):
            self.primary_color = p
            self.secondary_color = s
            self.tertiary_color = t

        @property
        def is_gradient(self) -> bool:
            return self.secondary_color is not None and self.tertiary_color is None

        @property
        def is_holographic(self) -> bool:
            return self.tertiary_color is not None

    return DummyRole(primary, secondary, tertiary)


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
