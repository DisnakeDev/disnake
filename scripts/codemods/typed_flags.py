# SPDX-License-Identifier: MIT

import textwrap
from typing import Optional

import libcst as cst
import libcst.codemod.visitors as codevisitors
import libcst.matchers as m
from libcst import codemod

from disnake import flags

# whew
# this code was a pain to write
# seriously, i regret everything
# please, save me
# these comments were written before the code was actually written
# they were written as procrastination

BASE_FLAG_CLASSES = ("BaseFlags", "ListBaseFlags")


class FlagTypings(codemod.VisitorBasedCodemodCommand):
    DESCRIPTION: str = (
        "Types every flag classes's init method, using overloads or if typechecking blocks."
    )

    def transform_module(self, tree: cst.Module) -> cst.Module:
        if self.context.full_module_name != "disnake.flags":
            raise codemod.SkipFile("this module contains no definitions of flag classes.")
        return super().transform_module(tree)

    def visit_ClassDef(self, node: cst.ClassDef) -> Optional[bool]:
        # no reason to continue into classes
        return False

    def leave_ClassDef(self, _: cst.ClassDef, node: cst.ClassDef):
        # this might not match every flag, like new classes, but it works for now
        # todo: consider preformulating a list with dir and getattr
        # todo: on the module and simply checking the class name here
        if m.matches(node.name, m.OneOf(*map(m.Name, BASE_FLAG_CLASSES))):
            return node
        for base in node.bases:
            if m.matches(base, m.OneOf(*[m.Arg(m.Name(klass)) for klass in BASE_FLAG_CLASSES])):
                # valid node
                break
        else:
            return node

        # now the meat of the function
        # we have two options here, and both of them depend on if __init__ exists, and *how* __init__ exists.
        # thankfully, we aren't limited to just codemodding, we can import the module if we need it
        # if __init__ exists without a TYPE_CHECKING block, we create and add two overloads
        # if __init__ exists under a TYPE_CHECKING block, we remove and replace it
        # we also check and remove previously existing TYPE_CHECKING and overloads

        # and we have to import the module anyways, to get a list of valid flags for each subclass.
        flag: flags.BaseFlags = getattr(flags, node.name.value)
        all_flags = sorted(flag.VALID_FLAGS.keys())

        # determine which method to use for creating the init overload, and possibly the update overload too.
        # only a few of these need to be overloads, in which we can use the same technique from permission overloads.
        # for the other ones, we need to find a TYPE_CHECKING block that *may* or may not contain a function definition.
        # if none of the TYPE_CHECKING blocks contain a function definition, we make a new one and
        # insert it near the beginning of the class body.
        # we also decorate with @_generated so we can delete it later.

        hide_behind_typechecking: bool = True
        if_block: Optional[cst.If] = None
        init: Optional[cst.FunctionDef] = None
        body = list(node.body.body)
        kwonly_params = [
            cst.Param(cst.Name(flag_name), cst.Annotation(cst.Name("bool")))
            for flag_name in all_flags
        ]
        for b in body.copy():
            if m.matches(b, m.FunctionDef(m.Name("__init__"))) and isinstance(b, cst.FunctionDef):
                deco_names = [getattr(deco.decorator, "value", "") for deco in b.decorators]
                if "_generated" in deco_names:
                    body.remove(b)
                    continue
                hide_behind_typechecking = False
                init = b  # type: ignore
                break
        node = node.with_deep_changes(node.body, body=body)

        if hide_behind_typechecking:
            # find the existing one if one exists
            for b in body:
                if m.matches(b, m.If(test=m.Name("TYPE_CHECKING"))):
                    # iterate through the options to see if one of the body is __init__
                    for line in b.body.body:
                        if m.matches(line, m.FunctionDef(m.Name("__init__"))):
                            if_block = b
                            break
                if if_block:
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
                if_block = cst.parse_statement(code)  # type: ignore
                assert if_block  # noqa: S101
                # now we need to add this if_block into the CST of node
                # find the first function definition and insert it before there
                body = list(node.body.body)
                for pos, b in enumerate(body):
                    if m.matches(b, m.FunctionDef()):
                        body.insert(pos, if_block)
                        node = node.with_deep_changes(node.body, body=body)
                        break
                else:
                    # so there wasn't any function, not sure why
                    # doesn't really matter, we just insert at the end
                    body.append(if_block)
                    node = node.with_deep_changes(node.body, body=body)

            # find the init
            for b in if_block.body.body:
                if m.matches(b, m.FunctionDef(m.Name("__init__"))) and isinstance(
                    b, cst.FunctionDef
                ):
                    init = b
                    break
            else:
                raise RuntimeError
            # add to the init the generated decorator
            old_init = init
            init = old_init.with_changes(decorators=[cst.Decorator(cst.Name("_generated"))])
            node = node.deep_replace(old_init, init)  # type: ignore
            node = node.with_deep_changes(init.params, kwonly_params=kwonly_params, star_kwarg=None)

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
            # todo: this is very complicated, and i think this visitor should be split into another visitor
            # aka never
            assert init  # noqa: S101
            no_body_init = init.with_changes(
                body=cst.IndentedBlock([cst.SimpleStatementLine([cst.Expr(cst.Ellipsis())])]),
                decorators=[
                    cst.Decorator(cst.Name("overload")),
                    cst.Decorator(cst.Name("_generated")),
                ],
            )

            # todo: remove all parameters except the first
            empty_init = no_body_init.with_changes(
                params=init.params.with_changes(params=init.params.params[:1], star_kwarg=None),
            )
            full_init = no_body_init.with_deep_changes(
                no_body_init.params, kwonly_params=kwonly_params, star_kwarg=None
            )
            body = list(node.body.body)
            for pos, b in enumerate(body):
                if m.matches(b, m.FunctionDef(m.Name("__init__"))):
                    body.insert(pos, empty_init)
                    body.insert(pos, full_init)
                    break
            node = node.with_deep_changes(node.body, body=body)

        # we need to add the import if it doesn't exist
        codevisitors.AddImportsVisitor.add_needed_import(self.context, "typing", "overload")
        codevisitors.AddImportsVisitor.add_needed_import(
            self.context, "disnake.utils", "_generated"
        )
        return node
