"""
The MIT License (MIT)

Copyright (c) 2015-2021 Rapptz
Copyright (c) 2021-present Disnake Development

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, Any, ClassVar, Dict, List, Mapping, Optional, Protocol, Union

from . import utils
from .colour import Colour
from .file import File
from .utils import MISSING

__all__ = ("Embed",)


class EmbedProxy:
    def __init__(self, layer: Optional[Dict[str, Any]]):
        if layer is not None:
            self.__dict__.update(layer)

    def __len__(self) -> int:
        return len(self.__dict__)

    def __repr__(self) -> str:
        inner = ", ".join((f"{k}={v!r}" for k, v in self.__dict__.items() if not k.startswith("_")))
        return f"EmbedProxy({inner})"

    def __getattr__(self, attr: str) -> None:
        return None


if TYPE_CHECKING:
    from typing_extensions import Self

    from disnake.types.embed import Embed as EmbedData, EmbedType

    class _EmbedFooterProxy(Protocol):
        text: Optional[str]
        icon_url: Optional[str]
        proxy_icon_url: Optional[str]

    class _EmbedFieldProxy(Protocol):
        name: Optional[str]
        value: Optional[str]
        # TODO: make this non-optional again by setting a default in from_dict?
        inline: Optional[bool]

    class _EmbedMediaProxy(Protocol):
        url: Optional[str]
        proxy_url: Optional[str]
        height: Optional[int]
        width: Optional[int]

    class _EmbedVideoProxy(Protocol):
        url: Optional[str]
        proxy_url: Optional[str]
        height: Optional[int]
        width: Optional[int]

    class _EmbedProviderProxy(Protocol):
        name: Optional[str]
        url: Optional[str]

    class _EmbedAuthorProxy(Protocol):
        name: Optional[str]
        url: Optional[str]
        icon_url: Optional[str]
        proxy_icon_url: Optional[str]


class Embed:
    """Represents a Discord embed.

    .. container:: operations

        .. describe:: len(x)

            Returns the total size of the embed.
            Useful for checking if it's within the 6000 character limit.

        .. describe:: bool(b)

            Returns whether the embed has any data set.

            .. versionadded:: 2.0

    Certain properties return an ``EmbedProxy``, a type
    that acts similar to a regular :class:`dict` except using dotted access,
    e.g. ``embed.author.icon_url``.

    For ease of use, all parameters that expect a :class:`str` are implicitly
    cast to :class:`str` for you.

    Attributes
    ----------
    title: Optional[:class:`str`]
        The title of the embed.
    type: :class:`str`
        The type of embed. Usually "rich".
        Possible strings for embed types can be found on discord's
        `api docs <https://discord.com/developers/docs/resources/channel#embed-object-embed-types>`_
    description: Optional[:class:`str`]
        The description of the embed.
    url: Optional[:class:`str`]
        The URL of the embed.
    timestamp: Optional[:class:`datetime.datetime`]
        The timestamp of the embed content. This is an aware datetime.
        If a naive datetime is passed, it is converted to an aware
        datetime with the local timezone.
    colour: Optional[:class:`Colour`]
        The colour code of the embed. Aliased to ``color`` as well.
        In addition to :class:`Colour`, :class:`int` can also be assigned to it,
        in which case the value will be converted to a :class:`Colour` object.
    """

    __slots__ = (
        "title",
        "url",
        "type",
        "_timestamp",
        "_colour",
        "_footer",
        "_image",
        "_thumbnail",
        "_video",
        "_provider",
        "_author",
        "_fields",
        "description",
        "_files",
    )

    _default_colour: ClassVar[Optional[Colour]] = None

    def __init__(
        self,
        *,
        title: Optional[Any] = None,
        type: EmbedType = "rich",
        description: Optional[Any] = None,
        url: Optional[Any] = None,
        timestamp: Optional[datetime.datetime] = None,
        colour: Optional[Union[int, Colour]] = MISSING,
        color: Optional[Union[int, Colour]] = MISSING,
    ):
        self.title: Optional[str] = str(title) if title is not None else title
        self.type: EmbedType = type
        self.description: Optional[str] = (
            str(description) if description is not None else description
        )
        self.url: Optional[str] = str(url) if url is not None else url

        self.timestamp = timestamp

        # possible values:
        # - MISSING: embed color will be _default_color
        # - None: embed color will not be set
        # - Color: embed color will be set to specified color
        if colour is not MISSING:
            color = colour
        if color is not MISSING:
            self.colour = color

        self._thumbnail: Optional[Dict[str, Any]] = None
        self._video: Optional[Dict[str, Any]] = None
        self._provider: Optional[Dict[str, Any]] = None
        self._author: Optional[Dict[str, Any]] = None
        self._image: Optional[Dict[str, Any]] = None
        self._footer: Optional[Dict[str, Any]] = None
        self._fields: Optional[List[Dict[str, Any]]] = None

        self._files: List[File] = []

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> Self:
        """Converts a :class:`dict` to a :class:`Embed` provided it is in the
        format that Discord expects it to be in.

        You can find out about this format in the `official Discord documentation`__.

        .. _DiscordDocs: https://discord.com/developers/docs/resources/channel#embed-object

        __ DiscordDocs_

        Parameters
        ----------
        data: :class:`dict`
            The dictionary to convert into an embed.
        """
        # we are bypassing __init__ here since it doesn't apply here
        self = cls.__new__(cls)

        # fill in the basic fields

        self.title = data.get("title", None)
        self.type = data.get("type", None)
        self.description = data.get("description", None)
        self.url = data.get("url", None)

        if self.title is not None:
            self.title = str(self.title)

        if self.description is not None:
            self.description = str(self.description)

        if self.url is not None:
            self.url = str(self.url)

        self._files = []

        # try to fill in the more rich fields

        color_value: Optional[int] = data.get("color", None)
        self.colour = color_value

        self.timestamp = utils.parse_time(data.get("timestamp", None))

        self._thumbnail = data.get("thumbnail", None)
        self._video = data.get("video", None)
        self._provider = data.get("provider", None)
        self._author = data.get("author", None)
        self._image = data.get("image", None)
        self._footer = data.get("footer", None)
        self._fields = data.get("fields", None)

        return self

    def copy(self) -> Self:
        """Returns a shallow copy of the embed."""
        embed = type(self).from_dict(self.to_dict())
        if hasattr(self, "_colour"):
            embed._colour = self._colour
        else:
            del embed._colour
        embed._files = self._files  # TODO: Maybe copy these too?
        return embed

    def __len__(self) -> int:
        total = len(self.title or "") + len(self.description or "")
        if self._fields:
            for field in self._fields:
                total += len(field["name"]) + len(field["value"])

        if self._footer:
            total += len(self._footer["text"])

        if self._author:
            total += len(self._author["name"])

        return total

    def __bool__(self) -> bool:
        return any(
            (
                self.title,
                self.url,
                self.description,
                # checking `is not None` as `0` is a valid color value
                getattr(self, "_colour", None) is not None,
                self._fields,
                self._timestamp,
                self._author,
                self._thumbnail,
                self._footer,
                self._image,
                self._provider,
                self._video,
            )
        )

    @property
    def colour(self) -> Optional[Colour]:
        return getattr(self, "_colour", type(self)._default_colour)

    @colour.setter
    def colour(self, value: Optional[Union[int, Colour]]):
        if value is None or isinstance(value, Colour):
            self._colour = value
        elif isinstance(value, int):
            self._colour = Colour(value=value)
        else:
            raise TypeError(
                f"Expected disnake.Colour, int, or None but received {type(value).__name__} instead."
            )

    @colour.deleter
    def colour(self):
        del self._colour

    color = colour

    @property
    def timestamp(self) -> Optional[datetime.datetime]:
        return self._timestamp

    @timestamp.setter
    def timestamp(self, value: Optional[datetime.datetime]):
        if isinstance(value, datetime.datetime):
            if value.tzinfo is None:
                value = value.astimezone()
            self._timestamp = value
        elif value is None:
            self._timestamp = value
        else:
            raise TypeError(
                f"Expected datetime.datetime or None received {type(value).__name__} instead"
            )

    @property
    def footer(self) -> _EmbedFooterProxy:
        """Returns an ``EmbedProxy`` denoting the footer contents.

        Possible attributes you can access are:

        - ``text``
        - ``icon_url``
        - ``proxy_icon_url``

        If the attribute has no value then :attr:`Empty` is returned.
        """
        return EmbedProxy(self._footer)  # type: ignore

    def set_footer(self, *, text: Optional[Any] = None, icon_url: Optional[Any] = None) -> Self:
        """Sets the footer for the embed content.

        This function returns the class instance to allow for fluent-style
        chaining.

        Parameters
        ----------
        text: Optional[:class:`str`]
            The footer text.
        icon_url: Optional[:class:`str`]
            The URL of the footer icon. Only HTTP(S) is supported.
        """
        self._footer = {}
        if text is not None:
            self._footer["text"] = str(text)

        if icon_url is not None:
            self._footer["icon_url"] = str(icon_url)

        return self

    def remove_footer(self) -> Self:
        """Clears embed's footer information.

        This function returns the class instance to allow for fluent-style
        chaining.

        .. versionadded:: 2.0
        """
        self._footer = None
        return self

    @property
    def image(self) -> _EmbedMediaProxy:
        """Returns an ``EmbedProxy`` denoting the image contents.

        Possible attributes you can access are:

        - ``url``
        - ``proxy_url``
        - ``width``
        - ``height``

        If the attribute has no value then :attr:`Empty` is returned.
        """
        return EmbedProxy(self._image)  # type: ignore

    def set_image(self, url: Optional[Any] = MISSING, *, file: File = MISSING) -> Self:
        """Sets the image for the embed content.

        This function returns the class instance to allow for fluent-style
        chaining.

        .. versionchanged:: 1.4
            Passing ``None`` removes the image.

        Parameters
        ----------
        url: Optional[:class:`str`]
            The source URL for the image. Only HTTP(S) is supported.
        file: :class:`File`
            The file to use as the image.

            .. versionadded:: 2.2
        """
        if file:
            if url:
                raise TypeError("Cannot use both a url and a file at the same time")
            if file.filename is None:
                raise TypeError("File doesn't have a filename")
            self._image = {"url": f"attachment://{file.filename}"}
            self._files.append(file)
        elif url is None:
            self._image = None
        elif url is MISSING:
            raise TypeError("Neither a url nor a file have been provided")
        else:
            self._image = {"url": str(url)}

        return self

    @property
    def thumbnail(self) -> _EmbedMediaProxy:
        """Returns an ``EmbedProxy`` denoting the thumbnail contents.

        Possible attributes you can access are:

        - ``url``
        - ``proxy_url``
        - ``width``
        - ``height``

        If the attribute has no value then :attr:`Empty` is returned.
        """
        return EmbedProxy(self._thumbnail)  # type: ignore

    def set_thumbnail(self, url: Optional[Any] = MISSING, *, file: File = MISSING) -> Self:
        """Sets the thumbnail for the embed content.

        This function returns the class instance to allow for fluent-style
        chaining.

        .. versionchanged:: 1.4
            Passing ``None`` removes the thumbnail.

        Parameters
        ----------
        url: Optional[:class:`str`]
            The source URL for the thumbnail. Only HTTP(S) is supported.
        file: :class:`File`
            The file to use as the image.

            .. versionadded:: 2.2
        """
        if file:
            if url:
                raise TypeError("Cannot use both a url and a file at the same time")
            if file.filename is None:
                raise TypeError("File doesn't have a filename")
            self._thumbnail = {"url": f"attachment://{file.filename}"}
            self._files.append(file)
        elif url is None:
            self._thumbnail = None
        elif url is MISSING:
            raise TypeError("Neither a url nor a file have been provided")
        else:
            self._thumbnail = {"url": str(url)}

        return self

    @property
    def video(self) -> _EmbedVideoProxy:
        """Returns an ``EmbedProxy`` denoting the video contents.

        Possible attributes include:

        - ``url`` for the video URL.
        - ``proxy_url`` for the proxied video URL.
        - ``height`` for the video height.
        - ``width`` for the video width.

        If the attribute has no value then :attr:`Empty` is returned.
        """
        return EmbedProxy(self._video)  # type: ignore

    @property
    def provider(self) -> _EmbedProviderProxy:
        """Returns an ``EmbedProxy`` denoting the provider contents.

        The only attributes that might be accessed are ``name`` and ``url``.

        If the attribute has no value then :attr:`Empty` is returned.
        """
        return EmbedProxy(self._provider)  # type: ignore

    @property
    def author(self) -> _EmbedAuthorProxy:
        """Returns an ``EmbedProxy`` denoting the author contents.

        See :meth:`set_author` for possible values you can access.

        If the attribute has no value then :attr:`Empty` is returned.
        """
        return EmbedProxy(self._author)  # type: ignore

    def set_author(
        self,
        *,
        name: Any,
        url: Optional[Any] = None,
        icon_url: Optional[Any] = None,
    ) -> Self:
        """Sets the author for the embed content.

        This function returns the class instance to allow for fluent-style
        chaining.

        Parameters
        ----------
        name: :class:`str`
            The name of the author.
        url: Optional[:class:`str`]
            The URL for the author.
        icon_url: Optional[:class:`str`]
            The URL of the author icon. Only HTTP(S) is supported.
        """
        self._author = {
            "name": str(name),
        }

        if url is not None:
            self._author["url"] = str(url)

        if icon_url is not None:
            self._author["icon_url"] = str(icon_url)

        return self

    def remove_author(self) -> Self:
        """Clears embed's author information.

        This function returns the class instance to allow for fluent-style
        chaining.

        .. versionadded:: 1.4
        """
        self._author = None
        return self

    @property
    def fields(self) -> List[_EmbedFieldProxy]:
        """List[``EmbedProxy``]: Returns a :class:`list` of ``EmbedProxy`` denoting the field contents.

        See :meth:`add_field` for possible values you can access.

        If the attribute has no value then :attr:`Empty` is returned.
        """
        return [EmbedProxy(d) for d in (self._fields or [])]  # type: ignore

    def add_field(self, name: Any, value: Any, *, inline: bool = True) -> Self:
        """Adds a field to the embed object.

        This function returns the class instance to allow for fluent-style
        chaining.

        Parameters
        ----------
        name: :class:`str`
            The name of the field.
        value: :class:`str`
            The value of the field.
        inline: :class:`bool`
            Whether the field should be displayed inline.
            Defaults to ``True``.
        """
        field = {
            "inline": inline,
            "name": str(name),
            "value": str(value),
        }

        if self._fields is not None:
            self._fields.append(field)
        else:
            self._fields = [field]

        return self

    def insert_field_at(self, index: int, name: Any, value: Any, *, inline: bool = True) -> Self:
        """Inserts a field before a specified index to the embed.

        This function returns the class instance to allow for fluent-style
        chaining.

        .. versionadded:: 1.2

        Parameters
        ----------
        index: :class:`int`
            The index of where to insert the field.
        name: :class:`str`
            The name of the field.
        value: :class:`str`
            The value of the field.
        inline: :class:`bool`
            Whether the field should be displayed inline.
            Defaults to ``True``.
        """
        field = {
            "inline": inline,
            "name": str(name),
            "value": str(value),
        }

        if self._fields is not None:
            self._fields.insert(index, field)
        else:
            self._fields = [field]

        return self

    def clear_fields(self) -> None:
        """Removes all fields from this embed."""
        self._fields = None

    def remove_field(self, index: int) -> None:
        """Removes a field at a specified index.

        If the index is invalid or out of bounds then the error is
        silently swallowed.

        .. note::

            When deleting a field by index, the index of the other fields
            shift to fill the gap just like a regular list.

        Parameters
        ----------
        index: :class:`int`
            The index of the field to remove.
        """
        if self._fields is not None:
            try:
                del self._fields[index]
            except IndexError:
                pass

    def set_field_at(self, index: int, name: Any, value: Any, *, inline: bool = True) -> Self:
        """Modifies a field to the embed object.

        The index must point to a valid pre-existing field.

        This function returns the class instance to allow for fluent-style
        chaining.

        Parameters
        ----------
        index: :class:`int`
            The index of the field to modify.
        name: :class:`str`
            The name of the field.
        value: :class:`str`
            The value of the field.
        inline: :class:`bool`
            Whether the field should be displayed inline.
            Defaults to ``True``.

        Raises
        ------
        IndexError
            An invalid index was provided.
        """
        if not self._fields or not (0 <= index < len(self._fields)):
            raise IndexError("field index out of range")

        self._fields[index] = {
            "inline": inline,
            "name": str(name),
            "value": str(value),
        }
        return self

    def to_dict(self) -> EmbedData:
        """Converts this embed object into a dict."""

        # add in the raw data into the dict
        result: EmbedData = {
            key[1:]: getattr(self, key)
            for key in self.__slots__
            if (
                key[0] == "_"
                and key not in ("_colour", "_timestamp", "_files")
                and getattr(self, key) is not None
            )
        }  # type: ignore

        # deal with basic convenience wrappers
        if isinstance(self.colour, Colour):
            result["color"] = self.colour.value

        if self._timestamp:
            result["timestamp"] = self._timestamp.astimezone(tz=datetime.timezone.utc).isoformat()

        # add in the non raw attribute ones
        if self.type:
            result["type"] = self.type

        if self.description:
            result["description"] = self.description

        if self.url:
            result["url"] = self.url

        if self.title:
            result["title"] = self.title

        return result

    @classmethod
    def set_default_colour(cls, value: Optional[Union[int, Colour]]):
        """
        Set the default colour of all new embeds.

        .. versionadded:: 2.4

        Returns
        -------
        Optional[:class:`Colour`]
            The colour that was set.
        """
        if value is None or isinstance(value, Colour):
            cls._default_colour = value
        elif isinstance(value, int):
            cls._default_colour = Colour(value=value)
        else:
            raise TypeError(
                f"Expected disnake.Colour, int, or None but received {type(value).__name__} instead."
            )
        return cls._default_colour

    set_default_color = set_default_colour

    @classmethod
    def get_default_colour(cls) -> Optional[Colour]:
        """
        Get the default colour of all new embeds.

        .. versionadded:: 2.4

        Returns
        -------
        Optional[:class:`Colour`]
            The default colour.

        """
        return cls._default_colour

    get_default_color = get_default_colour
