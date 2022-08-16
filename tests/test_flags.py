import pytest

from disnake.flags import ListBaseFlags, flag_value


class _ListFlags(ListBaseFlags):
    @flag_value
    def flag1(self):
        return 1 << 0

    @flag_value
    def flag2(self):
        return 1 << 1

    @flag_value
    def flag3(self):
        return 1 << 2


class TestListBaseFlags:
    @pytest.mark.parametrize(
        ("kwargs", "expected_value", "expected_values"),
        [
            ({}, 0, []),
            ({"flag2": True}, 2, [1]),
            ({"flag3": True, "flag2": False, "flag1": True}, 5, [0, 2]),
        ],
    )
    def test_init(self, kwargs, expected_value, expected_values) -> None:
        flags = _ListFlags(**kwargs)
        assert flags.value == expected_value
        assert flags.values == expected_values

    def test_class_vars(self) -> None:
        assert _ListFlags.DEFAULT_VALUE == 0
        assert _ListFlags.VALID_FLAGS == {"flag1": 1, "flag2": 2, "flag3": 4}

    def test_from_values(self) -> None:
        flags = _ListFlags._from_values([0, 2, 3, 4, 5, 10])
        assert flags.value == 1085
        assert flags.values == [0, 2, 3, 4, 5, 10]

    @pytest.mark.parametrize("value", [-10, -1, 100])
    def test_from_values__invalid(self, value) -> None:
        with pytest.raises(ValueError, match=r"Flag values must be within \[0, 64\)"):
            _ListFlags._from_values([0, 2, value, 3])

    def test_update(self) -> None:
        flags = _ListFlags(flag2=True)
        flags.flag2 = False
        flags.flag3 = True
        assert flags.value == 4
        assert flags.values == [2]

    def test_operators(self) -> None:
        a = _ListFlags(flag1=True, flag3=True)
        b = _ListFlags(flag1=False, flag3=True)
        assert a.values == [0, 2]
        assert b.values == [2]
        assert (~(a & b)).values == [0, 1]
