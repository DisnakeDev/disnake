# SPDX-License-Identifier: MIT

from __future__ import annotations

import logging
import os
import warnings
from abc import ABC, abstractmethod
from collections import defaultdict
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    DefaultDict,
    Dict,
    Generic,
    Literal,
    Optional,
    Set,
    TypeVar,
    Union,
    overload,
)

from . import utils
from .custom_warnings import LocalizationWarning
from .enums import Locale
from .errors import LocalizationKeyError

if TYPE_CHECKING:
    from typing_extensions import Self

    LocalizedRequired = Union[str, "Localized[str]"]
    LocalizedOptional = Union[Optional[str], "Localized[Optional[str]]"]


__all__ = (
    "Localized",
    "Localised",
    "LocalizationValue",
    "LocalizationProtocol",
    "LocalizationStore",
)

MISSING = utils.MISSING

_log = logging.getLogger(__name__)


LocalizationsDict = Union[Dict[Locale, str], Dict[str, str]]
Localizations = Union[str, LocalizationsDict]

StringT = TypeVar("StringT", str, Optional[str], covariant=True)


# This is generic over `string`, as some localized strings can be optional, e.g. option descriptions.
# The basic idea for parameters is this:
#     abc: LocalizedRequired
#     xyz: LocalizedOptional = None
#
# With that, one may use `abc="somename"` and `abc=Localized("somename", ...)`,
# but not `abc=Localized(None, ...)`. All three work fine for `xyz` though.


class Localized(Generic[StringT]):
    """A container type used for localized parameters.

    Exactly one of ``key`` or ``data`` must be provided.

    There is an alias for this called ``Localised``.

    .. versionadded:: 2.5

    Parameters
    ----------
    string: Optional[:class:`str`]
        The default (non-localized) value of the string.
        Whether this is optional or not depends on the localized parameter type.
    key: :class:`str`
        A localization key used for lookups.
        Incompatible with ``data``.
    data: Union[Dict[:class:`.Locale`, :class:`str`], Dict[:class:`str`, :class:`str`]]
        A mapping of locales to localized values.
        Incompatible with ``key``.
    """

    __slots__ = ("string", "localizations")

    @overload
    def __init__(self: Localized[StringT], string: StringT, *, key: str) -> None:
        ...

    @overload
    def __init__(self: Localized[Optional[str]], *, key: str) -> None:
        ...

    @overload
    def __init__(
        self: Localized[StringT],
        string: StringT,
        *,
        data: Union[Optional[LocalizationsDict], LocalizationValue],
    ) -> None:
        ...

    @overload
    def __init__(
        self: Localized[Optional[str]],
        *,
        data: Union[Optional[LocalizationsDict], LocalizationValue],
    ) -> None:
        ...

    # note: `data` accepting `LocalizationValue` is intentionally undocumented,
    # as it's only meant to be used internally
    def __init__(
        self,
        string: StringT = None,
        *,
        key: str = MISSING,
        data: Union[Optional[LocalizationsDict], LocalizationValue] = MISSING,
    ) -> None:
        self.string: StringT = string

        if not (key is MISSING) ^ (data is MISSING):
            raise TypeError("Exactly one of `key` or `data` must be provided")
        if isinstance(data, LocalizationValue):
            self.localizations = data
        else:
            self.localizations = LocalizationValue(key if key is not MISSING else data)

    @overload
    @classmethod
    def _cast(cls, string: LocalizedOptional, required: Literal[False]) -> Localized[Optional[str]]:
        ...

    @overload
    @classmethod
    def _cast(cls, string: LocalizedRequired, required: Literal[True]) -> Localized[str]:
        ...

    @classmethod
    def _cast(cls, string: Union[Optional[str], Localized[Any]], required: bool) -> Localized[Any]:
        if not isinstance(string, Localized):
            string = cls(string, data=None)

        # enforce the `StringT` type at runtime
        if required and string.string is None:
            raise ValueError("`string` parameter must be provided")
        return string

    @overload
    def _upgrade(self, *, key: Optional[str]) -> Self:
        ...

    @overload
    def _upgrade(self, string: str, *, key: Optional[str] = None) -> Localized[str]:
        ...

    def _upgrade(
        self: Localized[Any], string: Optional[str] = None, *, key: Optional[str] = None
    ) -> Localized[Any]:
        # update key if provided and not already set
        self.localizations._upgrade(key)

        # Only overwrite if not already set (`Localized()` parameter value takes precedence over function names etc.)
        # Note: not checking whether `string` is an empty string, to keep generic typing correct
        if not self.string and string is not None:
            self.string = string

        # this is safe, see above
        return self


Localised = Localized


class LocalizationValue:
    """Container type for (pending) localization data.

    .. versionadded:: 2.5
    """

    __slots__ = ("_key", "_data")

    def __init__(self, localizations: Optional[Localizations]) -> None:
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

    def _upgrade(self, key: Optional[str]) -> None:
        if not key:
            return

        # if empty, use new key
        if self._key is None and self._data is None:
            self._key = key
            self._data = MISSING
            return

        # if key is the same, ignore
        if self._key == key:
            return

        # at this point, the keys don't match, which either means that they're different strings,
        # or that there is no existing `_key` but `_data` is set
        raise ValueError("Can't specify multiple localization keys or dicts")

    def _link(self, store: LocalizationProtocol) -> None:
        """Loads localizations from the specified store if this object has a key."""
        if self._key is not None:
            self._data = store.get(self._key)

    def _copy(self) -> LocalizationValue:
        cls = self.__class__
        ins = cls.__new__(cls)
        ins._key = self._key
        ins._data = self._data
        return ins

    @property
    def data(self) -> Optional[Dict[str, str]]:
        """Optional[Dict[:class:`str`, :class:`str`]]: A dict with a locale -> localization mapping, if available."""
        if self._data is MISSING:
            warnings.warn(
                "value was never localized, this is likely a library bug",
                LocalizationWarning,
                stacklevel=2,
            )
            return None
        return self._data

    def __eq__(self, other) -> bool:
        d1 = self.data
        d2 = other.data
        # consider values equal if they're both falsy, or actually equal
        # (it doesn't matter if localizations are `None` or `{}`)
        return (not d1 and not d2) or d1 == d2


class LocalizationProtocol(ABC):
    """Manages a key-value mapping of localizations.

    This is an abstract class, a concrete implementation is provided as :class:`LocalizationStore`.

    .. versionadded:: 2.5
    """

    @abstractmethod
    def get(self, key: str) -> Optional[Dict[str, str]]:
        """Returns localizations for the specified key.

        Parameters
        ----------
        key: :class:`str`
            The lookup key.

        Raises
        ------
        LocalizationKeyError
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
        """Adds localizations from the provided path.

        Parameters
        ----------
        path: Union[:class:`str`, :class:`os.PathLike`]
            The path to the file/directory to load.

        Raises
        ------
        RuntimeError
            The provided path is invalid or couldn't be loaded
        """
        raise NotImplementedError

    # subtypes don't have to implement this
    def reload(self) -> None:
        """Clears localizations and reloads all previously loaded sources again.
        If an exception occurs, the previous data gets restored and the exception is re-raised.
        """
        pass


class LocalizationStore(LocalizationProtocol):
    """Manages a key-value mapping of localizations using ``.json`` files.

    .. versionadded:: 2.5

    Attributes
    ----------
    strict: :class:`bool`
        Specifies whether :meth:`.get` raises an exception if localizations for a provided key couldn't be found.
    """

    def __init__(self, *, strict: bool) -> None:
        self.strict = strict

        self._loc: DefaultDict[str, Dict[str, str]] = defaultdict(dict)
        self._paths: Set[Path] = set()

    def get(self, key: str) -> Optional[Dict[str, str]]:
        """Returns localizations for the specified key.

        Parameters
        ----------
        key: :class:`str`
            The lookup key.

        Raises
        ------
        LocalizationKeyError
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
            raise LocalizationKeyError(key)
        return data

    def load(self, path: Union[str, os.PathLike]) -> None:
        """Adds localizations from the provided path to the store.
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
        """Clears localizations and reloads all previously loaded files/directories again.
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
                raise ValueError("not a .json file")
            locale = path.stem

            if not (api_locale := utils.as_valid_locale(locale)):
                raise ValueError(f"invalid locale '{locale}'")
            locale = api_locale

            data = utils._from_json(path.read_text("utf-8"))
            self._load_dict(data, locale)
            _log.debug(f"Loaded localizations from '{path}'")
        except Exception as e:
            raise RuntimeError(f"Unable to load '{path}': {e}") from e

    def _load_dict(self, data: Dict[str, str], locale: str) -> None:
        if not isinstance(data, dict) or not all(
            o is None or isinstance(o, str) for o in data.values()
        ):
            raise TypeError("data must be a flat dict with string/null values")
        for key, value in data.items():
            d = self._loc[key]  # always create dict, regardless of value
            if value is not None:
                d[locale] = value
