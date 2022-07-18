from __future__ import annotations

import pytest

from disnake import flags


@flags.fill_with_flags()
class TestFlags(flags.BaseFlags):
    """A test class for flag testing."""

    __test__ = False

    @flags.flag_value
    def one(self):
        return 1 << 0

    @flags.flag_value
    def two(self):
        return 1 << 1

    @flags.flag_value
    def four(self):
        return 1 << 2


def test_flag_value_creation() -> None:
    flag = flags.flag_value(lambda x: 1 << 2)
    assert 1 << 2 == flag.flag


def test_fill_with_flags() -> None:
    assert TestFlags.VALID_FLAGS == {"one": 1, "two": 2, "four": 4}


class TestBaseFlags:
    def test__init__default_value(self) -> None:
        ins = TestFlags()
        assert ins.DEFAULT_VALUE is ins.value

    def test__init__kwargs(self) -> None:

        ins = TestFlags(one=True, two=False)
        assert ins.one is True
        assert ins.two is False

    def test__init__invalid_kwargs(self) -> None:
        with pytest.raises(TypeError, match="'h' is not a valid flag name."):
            TestFlags(h=True)

    def test_set_require_bool(self) -> None:
        with pytest.raises(TypeError, match="Value to set for TestFlags must be a bool."):
            TestFlags(one="h")  # type: ignore

        ins = TestFlags()

        with pytest.raises(TypeError, match="Value to set for TestFlags must be a bool."):
            ins.two = "h"  # type: ignore

    def test__eq__(self) -> None:
        ins = TestFlags(one=True, two=True)
        other = TestFlags(one=True, two=True)

        assert ins is not other
        assert ins == other
        assert not ins != other

        ins.two = False
        assert ins is not other
        assert not ins == other
        assert ins != other

    def test__and__(self) -> None:
        ins = TestFlags(one=True, two=True)
        other = TestFlags(one=True, two=True)

        third = ins & other
        assert third is not ins
        assert third.value == 0b011
        assert third == ins == other

        ins.one = False
        third = ins & other
        assert third is not ins
        assert third.value == 0b010

    def test__iand__(self) -> None:
        ins = TestFlags(one=True, two=True)
        other = TestFlags(one=True, two=True)

        third = ins
        ins &= other
        assert third is ins
        assert ins.value == 0b011

        other.two = False
        other.four = True
        ins &= other
        assert third is ins
        assert ins.value == 0b001

    def test__or__(self) -> None:
        ins = TestFlags(one=True, two=False)
        other = TestFlags(one=False, two=True)

        third = ins | other
        assert third is not ins
        assert third.value == 0b011
        assert ins.value == 0b001
        assert other.value == 0b010

        ins.one = False
        third = ins | other
        assert third.value == 0b010
        assert third is not ins

    def test__ior__(self) -> None:
        ins = TestFlags(one=True, two=False)
        other = TestFlags(one=False, two=True)

        third = ins
        ins |= other
        assert ins is third
        assert ins.value == 0b011
        assert other.value == 0b010

        other.four = True
        ins |= other
        assert ins.value == 0b111

    def test__xor__(self) -> None:
        ins = TestFlags(one=True, two=False)
        other = TestFlags(one=False, two=True)

        third = ins ^ other
        assert third.value == 0b011
        assert third is not ins

        other.one = True
        third = ins ^ other
        assert third.value == 0b010

    def test__ixor__(self) -> None:
        ins = TestFlags(one=True, two=False)
        other = TestFlags(one=False, two=True)

        third = ins
        ins ^= other
        assert ins is third
        assert ins.value == 0b011

        ins.two = False
        other.one = True
        ins ^= other
        assert ins.value == 0b010

    def test__le__(self) -> None:
        ins = TestFlags(one=True, two=False)
        other = TestFlags(one=False, two=True)

        assert not ins <= other
        other.one = True
        assert ins <= other

        with pytest.raises(
            TypeError, match="'<=' not supported between instances of 'TestFlags' and 'int'"
        ):
            ins <= 4  # type: ignore  # noqa: B015

    def test__ge__(self) -> None:
        ins = TestFlags(one=True, two=False)
        other = TestFlags(one=False, two=True)

        assert not ins >= other
        ins.two = True
        assert ins >= other

        with pytest.raises(
            TypeError, match="'>=' not supported between instances of 'TestFlags' and 'int'"
        ):
            _ = ins >= 4  # type: ignore

    def test__lt__(self) -> None:
        ins = TestFlags(one=True, two=False)
        other = TestFlags(one=False, two=True)

        assert not ins < other
        other.one = True
        assert ins < other

        with pytest.raises(
            TypeError, match="'<' not supported between instances of 'TestFlags' and 'int'"
        ):
            _ = ins < 4  # type: ignore

    def test__gt__(self) -> None:
        ins = TestFlags(one=True, two=False)
        other = TestFlags(one=False, two=True)

        assert not ins > other
        ins.two = True
        assert ins > other

        with pytest.raises(
            TypeError, match="'>' not supported between instances of 'TestFlags' and 'int'"
        ):
            _ = ins > 4  # type: ignore

    def test__invert__(self) -> None:
        ins = TestFlags(one=True)
        assert ins.value == 0b0001
        other = ~ins
        assert ins.value == 0b0001
        # the other `0` here is because invert does not invert values that are not defined
        assert other.value == 0b10110

    def test__hash__(self) -> None:
        ins = TestFlags(one=True)
        assert hash(ins) == hash(ins.value)

    def test_iter(self) -> None:
        ins = TestFlags(one=True, two=False)
        ran_at_least_once = False
        for flag, value in iter(ins):
            ran_at_least_once = True
            assert flag in ins.VALID_FLAGS
            assert getattr(ins, flag) == value

        assert ran_at_least_once

    def test_from_value(self) -> None:
        ins = TestFlags._from_value(0b101)
        assert ins.value == 0b101

    def test_has_flag(self) -> None:
        ins = TestFlags()

        ins.two = True

        assert ins.two is True

    def test_set_and_get_flag(self) -> None:
        ins = TestFlags()
        assert ins.DEFAULT_VALUE == ins.value

        ins.two = True
        assert ins.two is True
        assert ins.value == TestFlags.two.flag == 1 << 1


class TestIntents:
    def test_all_only_valid(self) -> None:
        """Test that Intents.all() doesn't include flags that aren't defined."""

        intents = flags.Intents.all()

        assert not (1 << 18 | 1 << 17) & intents.value
