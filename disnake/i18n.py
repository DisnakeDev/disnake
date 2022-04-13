"""
The MIT License (MIT)

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

import logging
import os
import warnings
from abc import ABC, abstractmethod
from collections import defaultdict
from pathlib import Path
from typing import DefaultDict, Dict, Optional, Set, Union

from . import utils
from .custom_warnings import LocalizationWarning
from .enums import Locale

MISSING = utils.MISSING


Localizations = Union[str, Dict[Locale, str], Dict[str, str]]


__all__ = (
    "is_valid_locale",
    "LocalizationProtocol",
    "LocalizationStore",
)


_log = logging.getLogger(__name__)


def is_valid_locale(locale: str) -> bool:
    """
    Returns ``True`` if the locale is valid for use with the API, ``False`` otherwise.

    .. versionadded:: 2.5
    """
    return locale in Locale._enum_value_map_  # type: ignore


class LocalizationValue:
    """
    Internal container type for (pending) localization data

    .. versionadded:: 2.5
    """

    __slots__ = ("_key", "_data")

    def __init__(self, localizations: Optional[Localizations]):
        self._key: Optional[str]
        self._data: Optional[Dict[str, str]]

        if localizations is None:
            # no localization
            self._key = None
            self._data = None
        elif isinstance(localizations, str):
            # got localization key
            self._key = localizations
            self._data = MISSING  # not localized yet
        elif isinstance(localizations, dict):
            # got localization data
            self._key = None
            self._data = {str(k): v for k, v in localizations.items()}
        else:
            raise TypeError(f"Invalid localizations type: {type(localizations).__name__}")

    def _link(self, store: LocalizationProtocol) -> None:
        """Loads localizations from the specified store if this object has a key"""
        if self._key is not None:
            self._data = store.get(self._key)

    def to_dict(self) -> Optional[Dict[str, str]]:
        """Returns a dict with a locale -> localization mapping"""
        if self._data is MISSING:
            warnings.warn(
                "value was never localized, this is likely a library bug",
                LocalizationWarning,
                stacklevel=2,
            )
            return None
        return self._data

    def __eq__(self, other) -> bool:
        d1 = self.to_dict()
        d2 = other.to_dict()
        # consider values equal if they're both falsy, or actually equal
        # (it doesn't matter if localizations are `None` or `{}`)
        return (not d1 and not d2) or d1 == d2


class LocalizationProtocol(ABC):
    """
    Manages a key-value mapping of localizations.

    This is an abstract class, a concrete implementation is provided as :class:`LocalizationStore`.

    .. versionadded:: 2.5
    """

    @abstractmethod
    def get(self, key: str) -> Optional[Dict[str, str]]:
        """
        Returns localizations for the specified key.

        Parameters
        ----------
        key: :class:`str`
            The lookup key.

        Raises
        ------
        RuntimeError
            May be raised if no localizations for the provided key were found,
            depending on the implementation.

        Returns
        -------
        Optional[Dict[:class:`str`, :class:`str`]]
            The localizations for the provided key.
            May return ``None`` if no localizations could be found.
        """
        raise NotImplementedError

    # subtypes don't have to implement this
    def load(self, path: Union[str, os.PathLike]) -> None:
        """
        Adds localizations from the provided path.

        Parameters
        ----------
        path: Union[:class:`str`, :class:`os.PathLike`]
            The path to the file/directory to load.

        Raises
        ------
        RuntimeError
            The provided path is invalid or couldn't be loaded
        """

    # subtypes don't have to implement this
    def reload(self) -> None:
        """
        Clears localizations and reloads all previously loaded sources again.
        If an exception occurs, the previous data gets restored and the exception is re-raised.
        """


class LocalizationStore(LocalizationProtocol):
    """
    Manages a key-value mapping of localizations.

    .. versionadded:: 2.5

    Attributes
    ------------
    strict: :class:`bool`
        Specifies whether :meth:`.get` raises an exception if localizations for a provided key couldn't be found.
    """

    def __init__(self, *, strict: bool):
        self.strict = strict

        self._loc: DefaultDict[str, Dict[str, str]] = defaultdict(dict)
        self._paths: Set[Path] = set()

    def get(self, key: str) -> Optional[Dict[str, str]]:
        """
        Returns localizations for the specified key.

        Parameters
        ----------
        key: :class:`str`
            The lookup key.

        Raises
        ------
        RuntimeError
            No localizations for the provided key were found.
            Raised only if :attr:`strict` is enabled, returns ``None`` otherwise.

        Returns
        -------
        Optional[Dict[:class:`str`, :class:`str`]]
            The localizations for the provided key.
            Returns ``None`` if no localizations could be found and :attr:`strict` is disabled.
        """

        data = self._loc.get(key)
        if data is None and self.strict:
            raise RuntimeError(f"no localizations found for key '{key}'")
        return data

    def load(self, path: Union[str, os.PathLike]) -> None:
        """
        Adds localizations from the provided path to the store.
        If the path points to a file, the file gets loaded.
        If it's a directory, all ``.json`` files in that directory get loaded (non-recursive).

        Parameters
        ----------
        path: Union[:class:`str`, :class:`os.PathLike`]
            The path to the file/directory to load.

        Raises
        ------
        RuntimeError
            The provided path is invalid or couldn't be loaded
        """

        path = Path(path)

        if path.is_file():
            self._load_file(path)
        elif path.is_dir():
            for file in path.glob("*.json"):
                if not file.is_file():
                    continue
                self._load_file(file)
        else:
            raise RuntimeError(f"Path '{path}' does not exist or is not a directory/file")

        self._paths.add(path)

    def reload(self) -> None:
        """
        Clears localizations and reloads all previously loaded files/directories again.
        If an exception occurs, the previous data gets restored and the exception is re-raised.
        See :func:`~LocalizationStore.load` for possible raised exceptions.
        """

        old = self._loc
        try:
            self._loc = defaultdict(dict)
            for path in self._paths:
                self.load(path)
        except Exception:
            # restore in case of error
            self._loc = old
            raise

    def _load_file(self, path: Path) -> None:
        try:
            if path.suffix != ".json":
                raise ValueError(f"not a .json file")
            locale = path.stem
            if not is_valid_locale(locale):
                raise ValueError(f"invalid locale '{locale}'")

            data = utils._from_json(path.read_text("utf-8"))
            self._load_dict(data, locale)
            _log.debug(f"Loaded localizations from '{path}'")
        except Exception as e:
            raise RuntimeError(f"Unable to load '{path}': {e}") from e

    def _load_dict(self, data: Dict[str, str], locale: str) -> None:
        if not isinstance(data, dict) or not all(isinstance(o, str) for o in data.values()):
            raise TypeError("data must be a flat dict with string values")
        for key, value in data.items():
            self._loc[key][locale] = value
