# SPDX-License-Identifier: MIT

import importlib
import textwrap
import types
from typing import List, Optional, cast

import libcst as cst
import libcst.codemod.visitors as codevisitors
import libcst.matchers as m
from libcst import codemod

from disnake import flags

BASE_FLAG_CLASSES = (flags.BaseFlags, flags.ListBaseFlags)

MODULES = (
    "disnake.flags",
    "disnake.ext.commands.flags",
)


class FlagTypings(codemod.VisitorBasedCodemodCommand):
    DESCRIPTION: str = (
        "Types every flag classes's init method, using overloads or if typechecking blocks."
    )

    flag_classes: List[str]
    imported_module: types.ModuleType

    def transform_module(self, tree: cst.Module) -> cst.Module:
        current_module = self.context.full_module_name
        if current_module not in MODULES:
            raise codemod.SkipFile("this module contains no definitions of flag classes.")

        # import and load the module
        module = importlib.import_module(current_module)
        # we preformulate a list of all flag classes on the imported flags module
        all_flag_classes = []
        for attr_name in dir(module):
            obj = getattr(module, attr_name)
            if (
                isinstance(obj, type)
                and issubclass(obj, BASE_FLAG_CLASSES)
                and obj not in BASE_FLAG_CLASSES
            ):
                all_flag_classes.append(obj.__name__)

        self.flag_classes = all_flag_classes
        self.imported_module = module

        return super().transform_module(tree)

    def visit_ClassDef(self, node: cst.ClassDef) -> Optional[bool]:
        # no reason to continue into classes
        return False

    def leave_ClassDef(self, _: cst.ClassDef, node: cst.ClassDef):
        if not m.matches(node.name, m.OneOf(*map(m.Name, self.flag_classes))):
            return node

        # now the meat of the function
        # we have two options here, and both of them depend on if __init__ exists, and *how* __init__ exists.
        # thankfully, we aren't limited to just codemodding, we can import the module if we need it
        # if __init__ exists without a TYPE_CHECKING block, we create and add two overloads
        # if __init__ exists under a TYPE_CHECKING block, we remove and replace it
        # we also check and remove previously existing TYPE_CHECKING and overloads

        # and we have to import the module anyways, to get a list of valid flags for each subclass.
        flag: flags.BaseFlags = getattr(self.imported_module, node.name.value)
        all_flags = sorted(flag.VALID_FLAGS.keys())

        # determine which method to use for creating the init overload, and possibly the update overload too.
        # only a few of these need to be overloads, in which we can use the same technique from permission overloads.
        # for the other ones, we need to find a TYPE_CHECKING block that *may* or may not contain a function definition.
        # if none of the TYPE_CHECKING blocks contain a function definition, we make a new one and
        # insert it near the beginning of the class body.
        # we also decorate with @_generated so we can delete it later.

        if_block: Optional[cst.If] = None
        init: Optional[cst.FunctionDef] = None
        body = list(node.body.body)
        kwonly_params = [
            cst.Param(cst.Name(flag_name), cst.Annotation(cst.Name("bool")), default=cst.Ellipsis())
            for flag_name in all_flags
        ]
        for b in body.copy():
            if m.matches(b, m.FunctionDef(m.Name("__init__"))) and isinstance(b, cst.FunctionDef):
                if any(m.matches(deco.decorator, m.Name("_generated")) for deco in b.decorators):
                    body.remove(b)
                    continue
                init = b
                break

        if not init:
            for b in body:
                if m.matches(b, m.If(test=m.Name("TYPE_CHECKING"))) and m.findall(
                    b, m.FunctionDef(m.Name("__init__"))
                ):
                    if_block = cast("cst.If", b)
                    break
            else:
                # one doesn't currently exist, great.
                # so we have two options here... we could make a typechecking block from scratch or... we could cheat
                code = textwrap.dedent(
                    """
                    if TYPE_CHECKING:
                        @_generated
                        def __init__(self):
                            ...
                    """
                )
                if_block = cast(
                    "cst.If", cst.parse_statement(code, config=self.module.config_for_parsing)
                )
                codevisitors.AddImportsVisitor.add_needed_import(
                    self.context, "typing", "TYPE_CHECKING"
                )
                # now we need to add this if_block into the CST of node
                # find the first function definition and insert it before there
                for pos, b in enumerate(body):  # noqa: B007
                    if m.matches(b, m.FunctionDef()):
                        break
                else:
                    # so there wasn't any function, not sure why
                    # doesn't really matter, we just insert at the end
                    pos = len(body)
                body.insert(pos, if_block)
                node = node.with_deep_changes(node.body, body=body)

            # find the init
            init = cast(
                "cst.FunctionDef",
                m.findall(if_block, m.FunctionDef(m.Name("__init__")))[0],
            )
            # add to the init the generated decorator
            old_init = init
            init = old_init.with_changes(
                decorators=[cst.Decorator(cst.Name("_generated"))],
                params=old_init.params.with_changes(kwonly_params=kwonly_params, star_kwarg=None),
            )
            codevisitors.AddImportsVisitor.add_needed_import(
                self.context, "disnake.utils", "_generated"
            )
            node = node.deep_replace(old_init, init)  # type: ignore

        else:
            # the init exists, so we need to make overloads
            # here's how:
            # first, we use the init we've already found
            # now, we need to insert two overloaded functions before it
            # this can be done by getting an init `with_changes` and remove the body
            # then we add the _generated decorator
            # then we remove all parameters except for self, and save that as our first overload
            # next, we need to add all of the flag values and that is our second overload
            # then we put them together and insert them before the existing overload
            # todo: this is very complicated, and maybe this visitor should be split into another visitor just to do this logic
            full_init = init.with_changes(
                body=cst.IndentedBlock([cst.SimpleStatementLine([cst.Expr(cst.Ellipsis())])]),
                decorators=[
                    cst.Decorator(cst.Name("overload")),
                    cst.Decorator(cst.Name("_generated")),
                ],
                params=init.params.with_changes(kwonly_params=kwonly_params, star_kwarg=None),
            )
            codevisitors.AddImportsVisitor.add_needed_import(self.context, "typing", "overload")
            codevisitors.AddImportsVisitor.add_needed_import(
                self.context, "disnake.utils", "_generated"
            )
            empty_init = full_init.with_changes(
                params=cst.Parameters(
                    params=[cst.Param(cst.Name("self"), cst.Annotation(cst.Name("NoReturn")))]
                )
            )
            codevisitors.AddImportsVisitor.add_needed_import(self.context, "typing", "NoReturn")
            pos = body.index(init)
            body.insert(pos, empty_init)
            body.insert(pos, full_init)
            node = node.with_deep_changes(node.body, body=body)

        return node
