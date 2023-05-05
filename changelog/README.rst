This directory contains "news fragments" which are short files that contain a small **ReST**-formatted
text that will be added to the next changelog.

The changelog will be read by **users**, so this description should be aimed at users
instead of describing internal changes which are only relevant to the developers.

Make sure to use full sentences in the **present tense** and use punctuation, examples:

- Improve Guild.create_text_channel by returning the channel type.

- Command syncing now uses logging instead of print.

Each file should use the following naming: ``<ISSUE>.<TYPE>.rst``, where
``<ISSUE>`` is an issue number, and ``<TYPE>`` is one of:

* ``breaking``: a change which may break existing code, such as feature removal or behavior change.
* ``deprecate``: feature deprecation.
* ``feature``: new user facing features, support of new API features, and/or otherwise new behavior.
* ``bugfix``: fixes a bug.
* ``doc``: documentation improvement.
* ``misc``: fixing a small typo or internal change that might be noteworthy.

So for example: ``123.feature.rst``, ``456.bugfix.rst``.

If your PR fixes an issue, use that number here. If there is no issue,
then after you submit the PR and get the PR number you can add a
changelog using that instead.

If there are multiple changes of the same type for the same issue, use the following naming for the conflicting changes:
``<ISSUE>.<TYPE>.<COUNTER>.rst``

If you are not sure what issue type to use, don't hesitate to ask in your PR.

``towncrier`` preserves multiple paragraphs and formatting (code blocks, lists, and so on), but for entries
other than ``features`` it is usually better to stick to a single paragraph to keep it concise.

You can also run ``pdm run docs`` to build the documentation
with the draft changelog (http://127.0.0.1:8009/whats_new.html) if you want to get a preview of how your change will look in the final release notes.


~~~~~

This file is adapted from `pytest's changelog documentation <https://github.com/pytest-dev/pytest/blob/4414c4adaeb06f1c883df2ccc3f4d469886b788d/changelog/README.rst>`_
