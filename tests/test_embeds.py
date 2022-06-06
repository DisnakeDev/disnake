import io
from datetime import datetime, timedelta

import pytest

from disnake import Color, Embed, File
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
    embed.timestamp = datetime.now()
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


def test_color_zero() -> None:
    e = Embed()
    assert not e

    # color=0 should be applied to bool and dict
    e.color = 0
    assert e
    assert e.to_dict() == {"color": 0, **_BASE}


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

    # shallow copy, but `_files` should be copied
    assert embed._files == copy._files
    assert embed._files is not copy._files


def test_copy_empty() -> None:
    e = Embed.from_dict({})
    copy = e.copy()
    assert e.to_dict() == copy.to_dict() == {}
