# SPDX-License-Identifier: MIT

import io
from datetime import datetime, timedelta

import pytest

from disnake import Color, Embed, File, embeds
from disnake.utils import MISSING, utcnow

_BASE = {"type": "rich"}


@pytest.fixture
def embed() -> Embed:
    time = utcnow() + timedelta(days=42)
    return Embed(
        type="link",
        title="wow",
        description="what a cool embed",
        url="http://endless.horse",
        timestamp=time,
        color=0xF8A8B8,
    )


@pytest.fixture
def file() -> File:
    return File(io.BytesIO(b"abcd"), filename="data.txt")


def test_init_empty() -> None:
    embed = Embed()
    assert embed.title is None
    assert embed.description is None
    assert embed.url is None
    assert embed.timestamp is None

    assert embed.to_dict() == _BASE
    assert not bool(embed)

    assert embed.fields == []


def test_init_all(embed: Embed) -> None:
    assert embed.timestamp
    assert embed.to_dict() == {
        "type": "link",
        "title": "wow",
        "description": "what a cool embed",
        "url": "http://endless.horse",
        "timestamp": embed.timestamp.isoformat(),
        "color": 0xF8A8B8,
    }
    assert bool(embed)


def test_type_default() -> None:
    # type for new embeds should be set to default value
    assert Embed().type == "rich"

    # type shouldn't be set in from_dict if dict didn't contain a type
    assert Embed.from_dict({}).type is None


def test_timestamp_naive(embed: Embed) -> None:
    embed.timestamp = datetime.now()  # noqa: DTZ005  # the point of this is to test naive dts
    assert embed.timestamp.tzinfo is not None


def test_len(embed: Embed) -> None:
    assert len(embed) == 20

    embed.set_footer(text="hmm", icon_url="https://localhost")
    assert len(embed) == 23

    embed.set_author(name="someone", url="https://127.0.0.1", icon_url="https://127.0.0.2")
    assert len(embed) == 30

    embed.add_field("field name", "field value")
    embed.add_field("another field", "woooo")
    assert len(embed) == 69


def test_eq() -> None:
    # basic test
    embed_1, embed_2 = Embed(), Embed()
    assert embed_1 == embed_2

    embed_1.title, embed_2.title = None, ""
    assert embed_1 == embed_2

    # color tests
    embed_1, embed_2 = Embed(), Embed()
    embed_1.color = Color(123456)
    assert not embed_1 == embed_2

    embed_1.color = MISSING
    assert embed_1 == embed_2

    embed_1, embed_2 = Embed(color=None), Embed()
    assert embed_1 == embed_2

    try:
        Embed.set_default_color(123456)
        assert not embed_1 == embed_2
    finally:
        Embed.set_default_color(None)

    # test fields
    embed_1, embed_2 = Embed(), Embed()
    embed_1.add_field(name="This is a test field", value="69 test 69")
    embed_2.add_field(name="This is a test field", value="69 test 69", inline=False)
    assert not embed_1 == embed_2

    embed_1, embed_2 = Embed(), Embed()
    embed_1._fields = []
    embed_2._fields = None
    assert embed_1 == embed_2


def test_embed_proxy_eq() -> None:
    embed_1, embed_2 = Embed(), Embed()

    embed_1.set_image("https://disnake.dev/assets/disnake-logo.png")
    embed_2.set_image(None)
    assert not embed_1.image == embed_2.image

    embed_2.set_image("https://disnake.dev/assets/disnake-logo.png")
    assert embed_1.image == embed_2.image


def test_color_zero() -> None:
    e = Embed()
    assert not e

    # color=0 should be applied to to_dict, __bool__, and __eq__
    e.color = 0
    assert e
    assert e.to_dict() == {"color": 0, **_BASE}
    assert e != Embed(color=None)


def test_default_color() -> None:
    try:
        # color applies if set before init
        Embed.set_default_color(123456)
        embed = Embed()
        assert embed.color == Color(123456)

        # default color should not affect __bool__
        assert not bool(embed)

        # custom value overrides default
        embed.color = 987654
        assert embed.color == Color(987654)
        assert embed.to_dict() == {"color": 987654, **_BASE}
        assert bool(embed)

        # removing custom value resets to default
        del embed.color
        assert embed.color == Color(123456)

        # clearing default changes color to `None`
        Embed.set_default_color(None)
        assert embed.color is None
    finally:
        Embed.set_default_color(None)


def test_default_color_copy(embed: Embed) -> None:
    # copy should retain color
    assert embed.copy().color == Color(0xF8A8B8)

    del embed.color
    assert embed.copy().color is None

    try:
        # copying with default value should not set attribute
        Embed.set_default_color(123456)
        c = embed.copy()
        assert c._colour is MISSING

        assert c.color == Color(123456)
    finally:
        Embed.set_default_color(None)


def test_attr_proxy() -> None:
    embed = Embed()
    author = embed.author
    assert len(author) == 0

    embed.set_author(name="someone")
    author = embed.author
    assert len(author) == 1
    assert author.name == "someone"
    assert embed.to_dict() == {"author": {"name": "someone"}, **_BASE}
    assert author.icon_url is None

    embed.set_author(name="abc", icon_url="https://xyz")
    assert len(embed.author) == 2

    embed.remove_author()
    assert len(embed.author) == 0
    assert embed.to_dict() == _BASE


def test_image_init() -> None:
    # should be empty initially
    embed = Embed()
    assert embed._files == {}
    assert embed.to_dict() == _BASE


def test_image_none() -> None:
    # removing image shouldn't change dict
    embed = Embed()
    embed.set_image(None)
    assert embed._files == {}
    assert embed.to_dict() == _BASE


def test_image_url() -> None:
    embed = Embed()
    embed.set_image("https://disnake.dev")
    assert embed._files == {}
    assert embed.to_dict() == {"image": {"url": "https://disnake.dev"}, **_BASE}


def test_image_file(file: File) -> None:
    embed = Embed()
    embed.set_image(file=file)
    assert embed._files == {"image": file}
    assert embed.to_dict() == {"image": {"url": "attachment://data.txt"}, **_BASE}


def test_image_remove(file: File) -> None:
    embed = Embed()
    embed.set_image(file=file)
    embed.set_image(None)
    assert embed._files == {}
    assert embed.to_dict() == _BASE


def test_file_params(file: File) -> None:
    embed = Embed()
    with pytest.raises(TypeError):
        embed.set_image("https://disnake.dev/assets/disnake-logo.png", file=file)  # type: ignore

    assert embed._files == {}
    assert embed.to_dict() == _BASE


def test_file_filename(file: File) -> None:
    embed = Embed()
    file.filename = None
    with pytest.raises(TypeError):
        embed.set_image(file=file)


def test_file_overwrite_url(file: File) -> None:
    embed = Embed()
    # setting url should remove file
    embed.set_image(file=file)
    embed.set_image("https://abc")
    assert embed._files == {}
    assert embed.to_dict() == {"image": {"url": "https://abc"}, **_BASE}


def test_file_overwrite_file(file: File) -> None:
    embed = Embed()
    # setting file twice should keep second one
    file2 = File(io.BytesIO(), filename="empty.dat")
    embed.set_image(file=file)
    embed.set_image(file=file2)
    assert embed._files == {"image": file2}
    assert embed.to_dict() == {"image": {"url": "attachment://empty.dat"}, **_BASE}


def test_file_multiple(file: File) -> None:
    embed = Embed()
    # setting multiple files should work correctly
    embed.set_image(file=file)
    embed.set_thumbnail(file=file)
    assert embed._files == {"image": file, "thumbnail": file}
    assert embed.to_dict() == {
        "image": {"url": "attachment://data.txt"},
        "thumbnail": {"url": "attachment://data.txt"},
        **_BASE,
    }


def test_fields() -> None:
    embed = Embed()

    embed.insert_field_at(42, "a", "b")
    assert embed.to_dict() == {"fields": [{"name": "a", "value": "b", "inline": True}], **_BASE}

    embed.insert_field_at(0, "c", "d")
    assert embed.to_dict() == {
        "fields": [
            {"name": "c", "value": "d", "inline": True},
            {"name": "a", "value": "b", "inline": True},
        ],
        **_BASE,
    }

    embed.set_field_at(-1, "e", "f", inline=False)
    assert embed.to_dict() == {
        "fields": [
            {"name": "c", "value": "d", "inline": True},
            {"name": "e", "value": "f", "inline": False},
        ],
        **_BASE,
    }

    embed.remove_field(0)
    assert embed.to_dict() == {"fields": [{"name": "e", "value": "f", "inline": False}], **_BASE}

    embed.clear_fields()
    assert embed.to_dict() == _BASE


def test_fields_exceptions() -> None:
    embed = Embed()

    # shouldn't raise
    embed.remove_field(42)

    # also shouldn't raise
    embed.add_field("a", "b")
    embed.remove_field(5)

    with pytest.raises(IndexError):
        embed.set_field_at(42, "x", "y")

    embed.clear_fields()
    with pytest.raises(IndexError):
        embed.set_field_at(0, "x", "y")


def test_field_restraints() -> None:
    embed = Embed(title="T" * 256)  # Size = 256
    embed.set_footer(text="T" * 2048)  # Size = 2304
    embed.add_field(name="A" * 256, value="B" * 1024)  # Size = 3584
    embed.add_field(name="A" * 256, value="B" * 1024)  # Size = 4864
    embed.add_field(name="A" * 112, value="B" * 1024)  # Size = 6000
    assert len(embed) == 6000
    embed.check_limits()

    embed.add_field(name="A", value="B")  # Breaks limit of 6000 chars
    with pytest.raises(ValueError, match="^Embed total size"):
        embed.check_limits()
    embed.remove_field(3)

    embed.check_limits()
    embed.insert_field_at(index=3, name="A", value="B")  # Breaks limit of 6000 chars
    with pytest.raises(ValueError, match="^Embed total size"):
        embed.check_limits()
    embed.remove_field(3)

    embed.set_field_at(index=2, name="A" * 113, value="B" * 1024)  # Breaks limit of 6000 chars
    assert len(embed) == 6001
    with pytest.raises(ValueError, match="^Embed total size"):
        embed.check_limits()
    embed.set_field_at(index=2, name="A" * 112, value="B" * 1024)
    assert len(embed) == 6000

    embed.set_author(name="A")  # Breaks limit of 6000 chars
    with pytest.raises(ValueError, match="^Embed total size"):
        embed.check_limits()
    embed.remove_author()

    embed.set_footer(
        text="T" * 2048 + " " * 500
    )  # Would break the 6000 limit, but leading + trailing whitespace doesn't count
    embed.check_limits()

    embed = Embed(title="Too many fields :WAYTOODANK:")
    for _ in range(25):
        embed.add_field(name="OK", value=":D")
    embed.check_limits()

    embed.add_field(name="NOTOK", value="D:")
    with pytest.raises(ValueError, match="Embeds cannot have more than 25 fields"):
        embed.check_limits()

    embed = Embed(title="author_check")
    embed.set_author(name="A" * 256)
    embed.check_limits()
    embed.set_author(name="B" * 257)
    with pytest.raises(ValueError, match="^Embed author"):
        embed.check_limits()

    embed = Embed(title="footer_check")
    embed.set_footer(text="A" * 2048)
    embed.check_limits()
    embed.set_footer(text="B" * 2049)
    with pytest.raises(ValueError, match="^Embed footer"):
        embed.check_limits()

    embed = Embed(title="title_check" + "A" * 245)
    embed.check_limits()
    embed = Embed(title="title_check" + "A" * 246)
    with pytest.raises(ValueError, match="^Embed title"):
        embed.check_limits()

    embed = Embed(description="desc_check" + "A" * 4086)
    embed.check_limits()
    embed = Embed(description="desc_check" + "A" * 4087)
    with pytest.raises(ValueError, match="^Embed description"):
        embed.check_limits()


def test_copy(embed: Embed, file: File) -> None:
    embed.set_footer(text="hi there", icon_url="https://localhost")
    embed.set_author(name="someone", url="https://127.0.0.1", icon_url="https://127.0.0.2")
    embed.add_field("field name", "field value")
    embed.add_field("another field", "woooo")
    embed.set_thumbnail("https://thumbnail.url")
    embed.set_image(file=file)

    # copying should keep exact dict representation
    copy = embed.copy()
    assert embed.to_dict() == copy.to_dict()

    # shallow copy, but `_files` and `_fields` should be copied
    assert embed._files == copy._files
    assert embed._files is not copy._files
    assert embed._fields == copy._fields
    assert embed._fields is not copy._fields


def test_copy_empty() -> None:
    e = Embed.from_dict({})
    copy = e.copy()
    assert e.to_dict() == copy.to_dict() == {}

    # shallow copy, but `_files` and `_fields` should be copied
    assert e._files == copy._files
    assert e._files is not copy._files
    assert e._fields is None
    assert copy._fields is None


def test_copy_fields(embed: Embed) -> None:
    embed.add_field("things", "stuff")
    copy = embed.copy()
    embed.clear_fields()
    assert copy._fields

    embed.insert_field_at(0, "w", "x")
    copy = embed.copy()
    embed.remove_field(0)
    assert embed._fields == []
    assert copy._fields == [{"name": "w", "value": "x", "inline": True}]

    embed.insert_field_at(0, "w", "x")
    copy = embed.copy()
    embed.insert_field_at(1, "y", "z")
    embed.set_field_at(0, "abc", "def", inline=False)

    assert embed._fields == [
        {"name": "abc", "value": "def", "inline": False},
        {"name": "y", "value": "z", "inline": True},
    ]
    assert copy._fields == [{"name": "w", "value": "x", "inline": True}]


# backwards compatibility
def test_emptyembed() -> None:
    with pytest.warns(DeprecationWarning):
        assert embeds.EmptyEmbed is None  # type: ignore
    with pytest.warns(DeprecationWarning):
        assert Embed.Empty is None  # type: ignore
    with pytest.warns(DeprecationWarning):
        assert Embed().Empty is None  # type: ignore

    # make sure unknown module attrs continue to raise
    with pytest.raises(AttributeError):
        _ = embeds.this_does_not_exist  # type: ignore
