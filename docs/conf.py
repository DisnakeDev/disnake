# SPDX-License-Identifier: MIT

# disnake documentation build configuration file, created by
# sphinx-quickstart on Fri Aug 21 05:43:30 2015.
#
# This file is execfile()d with the current directory set to its
# containing dir.
#
# Note that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.

import importlib.util
import inspect
import os
import re
import subprocess  # noqa: TID251
import sys
from typing import Any, Dict, Optional

from sphinx.application import Sphinx

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
sys.path.insert(0, os.path.abspath(".."))
sys.path.append(os.path.abspath("extensions"))

# -- General configuration ------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
# needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "builder",
    "sphinx.ext.autodoc",
    "sphinx.ext.extlinks",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.linkcode",
    "sphinxcontrib_trio",
    "sphinxcontrib.towncrier.ext",
    "hoverxref.extension",
    "notfound.extension",
    "sphinxext.opengraph",
    "redirects",
    "fulltoc",
    "exception_hierarchy",
    "attributetable",
    "resourcelinks",
    "nitpick_file_ignorer",
]

autodoc_member_order = "bysource"
autodoc_typehints = "none"
# maybe consider this?
# napoleon_attr_annotations = False

github_repo = "https://github.com/DisnakeDev/disnake"
dpy_github_repo = "https://github.com/Rapptz/discord.py"

extlinks = {
    "issue": (f"{github_repo}/issues/%s", "#%s"),
    "issue-dpy": (f"{dpy_github_repo}/issues/%s", "#%s"),
    "ddocs": ("https://discord.com/developers/docs/%s", None),
}

extlinks_detect_hardcoded_links = True


rst_prolog = """
.. |coro| replace:: This function is a |coroutine_link|_.
.. |maybecoro| replace:: This function *could be a* |coroutine_link|_.
.. |coroutine_link| replace:: *coroutine*
.. |components_type| replace:: Union[:class:`disnake.ui.ActionRow`, :class:`disnake.ui.WrappedComponent`, List[Union[:class:`disnake.ui.ActionRow`, :class:`disnake.ui.WrappedComponent`, List[:class:`disnake.ui.WrappedComponent`]]]]
.. |resource_type| replace:: Union[:class:`bytes`, :class:`.Asset`, :class:`.Emoji`, :class:`.PartialEmoji`, :class:`.StickerItem`, :class:`.Sticker`]
.. _coroutine_link: https://docs.python.org/3/library/asyncio-task.html#coroutine
"""

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix of source filenames.
source_suffix = ".rst"

# The encoding of source files.
# source_encoding = 'utf-8-sig'

# The root toctree document.
root_doc = "index"

# General information about the project.
project = "disnake"
copyright = "2015-2021, Rapptz, 2021-present, Disnake Development"

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.

version = ""
with open("../disnake/__init__.py") as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)  # type: ignore

# The full version, including alpha/beta/rc tags.
release = version


_IS_READTHEDOCS = bool(os.getenv("READTHEDOCS"))


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args]).strip().decode()


# Current git reference. Uses branch/tag name if found, otherwise uses commit hash
git_ref = None
try:
    git_ref = git("name-rev", "--name-only", "--no-undefined", "HEAD")
    git_ref = re.sub(r"^(remotes/[^/]+|tags)/", "", git_ref)
except Exception:
    pass

# (if no name found or relative ref, use commit hash instead)
if not git_ref or re.search(r"[\^~]", git_ref):
    try:
        git_ref = git("rev-parse", "HEAD")
    except Exception:
        git_ref = "master"

towncrier_draft_autoversion_mode = "draft"
towncrier_draft_include_empty = False  # hides the unreleased indicator if there are no changes
towncrier_draft_working_directory = ".."


# Whether or not to include every attribute and object in the toc
toc_object_entries = False

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = "en"

locale_dirs = ["locale/"]
gettext_compact = False

# There are two options for replacing |today|: either, you set today to some
# non-false value, then it is used:
# today = ''
# Else, today_fmt is used as the format for a strftime call.
# today_fmt = '%B %d, %Y'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ["_build"]

# The reST default role (used for this markup: `text`) to use for all
# documents.
# default_role = None

# If true, '()' will be appended to :func: etc. cross-reference text.
# add_function_parentheses = True

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
# add_module_names = True

# If true, sectionauthor and moduleauthor directives will be shown in the
# output. They are ignored by default.
# show_authors = False

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "friendly"

# A list of ignored prefixes for module index sorting.
# modindex_common_prefix = []

# If true, keep warnings as "system message" paragraphs in the built documents.
# keep_warnings = False


# Nitpicky mode options
nitpick_ignore_files = [
    "migrating_to_async",
    "migrating",
    "whats_new",
    "whats_new_legacy",
]


_spec = importlib.util.find_spec("disnake")
if not (_spec and _spec.origin):
    # this should never happen
    raise RuntimeError("Unable to find module spec")
_disnake_module_path = os.path.dirname(_spec.origin)


def linkcode_resolve(domain: str, info: Dict[str, Any]) -> Optional[str]:
    if domain != "py":
        return None

    try:
        obj: Any = sys.modules[info["module"]]
        for part in info["fullname"].split("."):
            obj = getattr(obj, part)
        obj = inspect.unwrap(obj)

        if isinstance(obj, property):
            obj = inspect.unwrap(obj.fget)  # type: ignore

        path = os.path.relpath(inspect.getsourcefile(obj), start=_disnake_module_path)  # type: ignore
        src, lineno = inspect.getsourcelines(obj)
    except Exception:
        return None

    path = f"{path}#L{lineno}-L{lineno + len(src) - 1}"
    return f"{github_repo}/blob/{git_ref}/disnake/{path}"


hoverx_default_type = "tooltip"
hoverxref_domains = ["py"]
hoverxref_role_types = dict.fromkeys(
    ["ref", "class", "func", "meth", "attr", "exc", "data"],
    "tooltip",
)
hoverxref_tooltip_theme = ["tooltipster-custom"]
hoverxref_tooltip_lazy = True

# these have to match the keys on intersphinx_mapping, and those projects must be hosted on readthedocs.
hoverxref_intersphinx = [
    "py",
    "aio",
    "req",
]

# Links used for cross-referencing stuff in other documentation
# when this is updated hoverxref_intersphinx also needs to be updated IF THE docs are hosted on readthedocs.
intersphinx_mapping = {
    "py": ("https://docs.python.org/3", None),
    "aio": ("https://docs.aiohttp.org/en/stable/", None),
    "req": ("https://requests.readthedocs.io/en/latest/", None),
}


# use proxied API endpoint on readthedocs to avoid CORS issues
if _IS_READTHEDOCS:
    hoverxref_api_host = "/_"

# when not on readthedocs, assume no prefix for the 404 page.
# this means that /404.html should properly render on local builds
if not _IS_READTHEDOCS:
    notfound_urls_prefix = "/"

# ignore common link types that we don't particularly care about or are unable to check
linkcheck_ignore = [
    r"https?://github.com/.+?/.+?/(issues|pull)/\d+",
    r"https?://support.discord.com/",
]

if _IS_READTHEDOCS:
    # set html_baseurl based on readthedocs-provided env variable
    # https://github.com/readthedocs/readthedocs.org/pull/10224
    # https://docs.readthedocs.io/en/stable/reference/environment-variables.html#envvar-READTHEDOCS_CANONICAL_URL
    html_baseurl = os.environ.get("READTHEDOCS_CANONICAL_URL")
    if not html_baseurl:
        raise RuntimeError("Expected `READTHEDOCS_CANONICAL_URL` to be set on readthedocs")

    # enable opensearch (see description somewhere below)
    html_use_opensearch = html_baseurl.rstrip("/")


# ogp_site_url = ""  # automatically set on readthedocs
ogp_site_name = "disnake documentation"
ogp_image = "https://disnake.dev/assets/disnake-logo-transparent.png"
ogp_image_alt = "disnake icon"
ogp_custom_meta_tags = [
    '<meta property="og:image:width" content="64" />',
    '<meta property="og:image:height" content="64" />',
]


# -- Options for HTML output ----------------------------------------------

html_experimental_html5_writer = True

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = "basic"

html_context = {
    "discord_invite": "https://discord.gg/disnake",
    "discord_extensions": [
        ("disnake.ext.commands", "ext/commands"),
        ("disnake.ext.tasks", "ext/tasks"),
    ],
}

resource_links = {
    "disnake": "https://discord.gg/disnake",
    "issues": f"{github_repo}/issues",
    "discussions": f"{github_repo}/discussions",
    "examples": f"{github_repo}/tree/{git_ref}/examples",
}

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
html_theme_options = {
    "enable_search_shortcuts": True,
}

# Add any paths that contain custom themes here, relative to this directory.
# html_theme_path = []

# The name for this set of Sphinx documents.  If None, it defaults to
# "<project> v<release> documentation".
# html_title = None

# A shorter title for the navigation bar.  Default is the same as html_title.
# html_short_title = None

# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
# html_logo = None

# The name of an image file (within the static path) to use as favicon of the
# docs.  This file should be a Windows icon file (.ico) being 16x16 or 32x32
# pixels large.
html_favicon = "./images/disnake_logo.ico"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# Add any extra paths that contain custom files (such as robots.txt or
# .htaccess) here, relative to this directory. These files are copied
# directly to the root of the documentation.
# html_extra_path = []

# If not '', a 'Last updated on:' timestamp is inserted at every page bottom,
# using the given strftime format.
# html_last_updated_fmt = '%b %d, %Y'

# If true, SmartyPants will be used to convert quotes and dashes to
# typographically correct entities.
# html_use_smartypants = True

# Custom sidebar templates, maps document names to template names.
# html_sidebars = {}

# Additional templates that should be rendered to pages, maps page names to
# template names.
# html_additional_pages = {}

# If false, no module index is generated.
# html_domain_indices = True

# If false, no index is generated.
# html_use_index = True

# If true, the index is split into individual pages for each letter.
# html_split_index = False

# If true, links to the reST sources are added to the pages.
# html_show_sourcelink = True

# If true, "Created using Sphinx" is shown in the HTML footer. Default is True.
# html_show_sphinx = True

# If true, "(C) Copyright ..." is shown in the HTML footer. Default is True.
# html_show_copyright = True

# If true, an OpenSearch description file will be output, and all pages will
# contain a <link> tag referring to it.  The value of this option must be the
# base URL from which the finished HTML is served.
# html_use_opensearch = ''  # NOTE: this is being set above

# This is the file name suffix for HTML files (e.g. ".xhtml").
# html_file_suffix = None

# Language to be used for generating the HTML full-text search index.
# Sphinx supports the following languages:
#   'da', 'de', 'en', 'es', 'fi', 'fr', 'hu', 'it', 'ja'
#   'nl', 'no', 'pt', 'ro', 'ru', 'sv', 'tr'
# html_search_language = 'en'

# A dictionary with options for the search language support, empty by default.
# Now only 'ja' uses this config value
# html_search_options = {'type': 'default'}

# The name of a javascript file (relative to the configuration directory) that
# implements a search results scorer. If empty, the default will be used.
html_search_scorer = "_static/scorer.js"

html_js_files = [
    "custom.js",
    "copy.js",
    "sidebar.js",
    "touch.js",
]

# Output file base name for HTML help builder.
htmlhelp_basename = "disnake.pydoc"

# -- Options for LaTeX output ---------------------------------------------

latex_elements = {
    # # The paper size ('letterpaper' or 'a4paper').
    # 'papersize': 'letterpaper',
    # # The font size ('10pt', '11pt' or '12pt').
    # 'pointsize': '10pt',
    # # Additional stuff for the LaTeX preamble.
    # 'preamble': '',
    # # Latex figure (float) alignment
    # 'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    ("index", "disnake.tex", "disnake Documentation", "Rapptz", "manual"),
]

# The name of an image file (relative to this directory) to place at the top of
# the title page.
# latex_logo = None

# For "manual" documents, if this is true, then toplevel headings are parts,
# not chapters.
# latex_use_parts = False

# If true, show page references after internal links.
# latex_show_pagerefs = False

# If true, show URL addresses after external links.
# latex_show_urls = False

# Documents to append as an appendix to all manuals.
# latex_appendices = []

# If false, no module index is generated.
# latex_domain_indices = True


# -- Options for manual page output ---------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [("index", "disnake", "disnake Documentation", ["Rapptz"], 1)]

# If true, show URL addresses after external links.
# man_show_urls = False


# -- Options for Texinfo output -------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (
        "index",
        "disnake",
        "disnake Documentation",
        "Rapptz",
        "disnake",
        "One line description of project.",
        "Miscellaneous",
    ),
]

# Documents to append as an appendix to all manuals.
# texinfo_appendices = []

# If false, no module index is generated.
# texinfo_domain_indices = True

# How to display URL addresses: 'footnote', 'no', or 'inline'.
# texinfo_show_urls = 'footnote'

# If true, do not generate a @detailmenu in the "Top" node's menu.
# texinfo_no_detailmenu = False


def setup(app: Sphinx) -> None:
    if app.config.language == "ja":
        app.config.intersphinx_mapping["py"] = ("https://docs.python.org/ja/3", None)
        app.config.html_context["discord_invite"] = "https://discord.gg/disnake"
        app.config.resource_links["disnake"] = "https://discord.gg/disnake"

    # HACK: avoid deprecation warnings caused by sphinx always iterating over all class attributes
    import disnake

    del disnake.Embed.Empty  # type: ignore
