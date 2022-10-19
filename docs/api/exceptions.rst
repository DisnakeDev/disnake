.. SPDX-License-Identifier: MIT

.. currentmodule:: disnake

Exceptions and Warnings
=======================

This section documents exceptions and warnings thrown by the library and their hierarchy.

Exceptions
----------

DiscordException
~~~~~~~~~~~~~~~~

.. autoexception:: DiscordException

ClientException
~~~~~~~~~~~~~~~

.. autoexception:: ClientException

LoginFailure
~~~~~~~~~~~~

.. autoexception:: LoginFailure

NoMoreItems
~~~~~~~~~~~

.. autoexception:: NoMoreItems

HTTPException
~~~~~~~~~~~~~

.. autoexception:: HTTPException
    :members:

Forbidden
~~~~~~~~~

.. autoexception:: Forbidden

NotFound
~~~~~~~~

.. autoexception:: NotFound

DiscordServerError
~~~~~~~~~~~~~~~~~~

.. autoexception:: DiscordServerError

InvalidData
~~~~~~~~~~~

.. autoexception:: InvalidData

WebhookTokenMissing
~~~~~~~~~~~~~~~~~~~

.. autoexception:: WebhookTokenMissing

GatewayNotFound
~~~~~~~~~~~~~~~

.. autoexception:: GatewayNotFound

ConnectionClosed
~~~~~~~~~~~~~~~~

.. autoexception:: ConnectionClosed

PrivilegedIntentsRequired
~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoexception:: PrivilegedIntentsRequired

SessionStartLimitReached
~~~~~~~~~~~~~~~~~~~~~~~~

.. autoexception:: SessionStartLimitReached

InteractionException
~~~~~~~~~~~~~~~~~~~~

.. autoexception:: InteractionException

InteractionResponded
~~~~~~~~~~~~~~~~~~~~

.. autoexception:: InteractionResponded

InteractionNotResponded
~~~~~~~~~~~~~~~~~~~~~~~

.. autoexception:: InteractionNotResponded

InteractionTimedOut
~~~~~~~~~~~~~~~~~~~

.. autoexception:: InteractionTimedOut

ModalChainNotSupported
~~~~~~~~~~~~~~~~~~~~~~

.. autoexception:: ModalChainNotSupported

LocalizationKeyError
~~~~~~~~~~~~~~~~~~~~

.. autoexception:: LocalizationKeyError

OpusError
~~~~~~~~~

.. autoexception:: disnake.opus.OpusError

OpusNotLoaded
~~~~~~~~~~~~~

.. autoexception:: disnake.opus.OpusNotLoaded

Exception Hierarchy
-------------------

.. exception_hierarchy::

    - :exc:`Exception`
        - :exc:`DiscordException`
            - :exc:`ClientException`
                - :exc:`InvalidData`
                - :exc:`LoginFailure`
                - :exc:`ConnectionClosed`
                - :exc:`PrivilegedIntentsRequired`
                - :exc:`SessionStartLimitReached`
                - :exc:`InteractionException`
                    - :exc:`InteractionResponded`
                    - :exc:`InteractionNotResponded`
                    - :exc:`InteractionTimedOut`
                    - :exc:`ModalChainNotSupported`
            - :exc:`NoMoreItems`
            - :exc:`GatewayNotFound`
            - :exc:`HTTPException`
                - :exc:`Forbidden`
                - :exc:`NotFound`
                - :exc:`DiscordServerError`
            - :exc:`LocalizationKeyError`
            - :exc:`WebhookTokenMissing`


Warnings
--------

DiscordWarning
~~~~~~~~~~~~~~

.. autoclass:: DiscordWarning

ConfigWarning
~~~~~~~~~~~~~

.. autoclass:: ConfigWarning

SyncWarning
~~~~~~~~~~~

.. autoclass:: SyncWarning

LocalizationWarning
~~~~~~~~~~~~~~~~~~~

.. autoclass:: LocalizationWarning

Warning Hierarchy
-----------------

.. exception_hierarchy::

    - :class:`DiscordWarning`
        - :class:`ConfigWarning`
        - :class:`SyncWarning`
        - :class:`LocalizationWarning`
