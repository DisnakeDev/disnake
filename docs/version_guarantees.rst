.. SPDX-License-Identifier: MIT

.. _version_guarantees:

Version Guarantees
==================

This library does **not** quite follow the semantic versioning principle, the notable difference being that breaking changes may not only occur on major version increases, but also on minor version bumps (think Python's own versioning scheme).
The primary reason for this is the lack of guarantees on the Discord API side when it comes to breaking changes, which along with the dynamic nature of the API results in breaking changes sometimes being required more frequently than desired.
However, any breaking changes will always be explicitly marked as such in the release notes.

In general, the versioning scheme (``major.minor.micro``) used in this library aims to follow these rules:

- ``major`` bumps indicate a significant refactoring or other large changes that would constitute such an increase (will most likely include breaking changes)
- ``minor`` bumps contain new features, fixes, and **may also have breaking changes**
- ``micro`` bumps only contain fixes, no new features and no breaking changes

One thing to keep in mind is that breaking changes only apply to **publicly documented functions and classes**.
If it's not listed in the documentation here then it is not part of the public API and is thus bound to change.
This includes attributes that start with an underscore or functions without an underscore that are not documented.

.. note::

    The examples below are non-exhaustive.

Examples of Breaking Changes
----------------------------

- Changing the default parameter value to something else.
- Renaming a function without an alias to an old function.
- Adding or removing parameters to an event.

Examples of Non-Breaking Changes
--------------------------------

- Adding or removing private underscored attributes.
- Adding an element into the ``__slots__`` of a data class.
- Changing the behaviour of a function to fix a bug.
- Changes in the documentation.
- Modifying the internal HTTP handling.
- Upgrading the dependencies to a new version, major or otherwise.
