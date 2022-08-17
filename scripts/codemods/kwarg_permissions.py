from typing import Optional

import libcst as cst
import libcst.codemod.visitors as codevisitors
import libcst.matchers as m
from libcst import codemod

from disnake import Permissions


class PermissionTypings(codemod.VisitorBasedCodemodCommand):
    DESCRIPTION: str = "Adds overloads for all permissions."

    def __init__(self, context: codemod.CodemodContext):
        super().__init__(context)
        # add all of the permissions
        self.permissions = sorted(Permissions.VALID_FLAGS.keys())

    def transform_module(self, tree: cst.Module) -> cst.Module:
        if "@_overload_with_permissions" not in tree.code:
            raise codemod.SkipFile(
                "this module does not contain the required decorator: `@_overload_with_permissions`."
            )
        return super().transform_module(tree)

    def visit_FunctionDef(self, node: cst.FunctionDef) -> Optional[bool]:
        # don't recurse into the body of a function
        return False

    def leave_FunctionDef(self, _: cst.FunctionDef, node: cst.FunctionDef):
        # we don't care about with the unedited note
        has_overload_deco = False
        is_overload = False
        previously_generated = False
        for deco in node.decorators:
            if isinstance(deco.decorator, cst.Call):
                continue
            name = deco.decorator.value
            if name == "_overload_with_permissions":
                has_overload_deco = True
            elif name == "overload":
                is_overload = True
            elif name == "_generated":
                previously_generated = True

        if previously_generated:
            return cst.RemovalSentinel.REMOVE

        if not has_overload_deco:
            return node

        # create permission matchers
        perm_matchers = m.Name(self.permissions[0])
        for perm in self.permissions[1:]:
            perm_matchers |= m.Name(perm)

        if not node.params.star_kwarg and not is_overload:
            raise RuntimeError(
                'a function cannot be decorated with "_overload_with_permissions" and not take any kwargs unless it is an overload.'
            )
        # always true if this isn't an overload
        elif node.params.star_kwarg:
            # use the existing annotation if one exists
            annotation = node.params.star_kwarg.annotation
            if annotation is None:
                raise RuntimeError(
                    f"parameter {node.params.star_kwarg.name.value} must be annotated."
                )
        # only possible in the case of an overload
        else:
            # use the first permission annotation if it exists, otherwise default to `bool`
            # make a matcher instance of all valid permission names
            for kw_param in node.params.kwonly_params:
                if (
                    kw_param.annotation
                    and m.matches(kw_param.name, perm_matchers)
                    and m.matches(kw_param.annotation, m.Annotation())
                ):
                    annotation = kw_param.annotation
                    break
            else:
                annotation = cst.Annotation(cst.Name("bool"))

        # remove all of the existing permissions from the params
        def remove_existing_permissions(params: cst.Parameters) -> cst.Parameters:

            existing_params = list(params.params)
            for param in existing_params.copy():
                if param.name.value in self.permissions:
                    existing_params.remove(param)

            # unlike params, these may contain generated objects
            # we only have to do this for overloads, as we only change overloads directly
            existing_kwonly_params = list(params.kwonly_params)
            if is_overload:
                # make matches
                found_start = False
                for param in existing_kwonly_params.copy():
                    if m.matches(param.name, perm_matchers):
                        found_start = True
                    if found_start:
                        existing_kwonly_params.remove(param)
            else:
                for param in existing_kwonly_params.copy():
                    if m.matches(param.name, perm_matchers):
                        existing_kwonly_params.remove(param)

            star_arg = params.star_arg if existing_kwonly_params else cst.MaybeSentinel.DEFAULT
            return params.with_changes(
                params=existing_params,
                kwonly_params=existing_kwonly_params,
                star_arg=star_arg,
            )

        def get_perm_kwargs():
            return [
                cst.Param(
                    cst.Name(perm),
                    annotation,
                    default=cst.Ellipsis(),
                )
                for perm in self.permissions
            ]

        # get a Params with all of the new params that we should have
        params = remove_existing_permissions(node.params)
        params = params.with_changes(star_kwarg=None)
        empty_overload_params = params.deep_clone()

        # add the permissions to the kw_only params
        kwonly_params = list(params.kwonly_params)
        kwonly_params.extend(get_perm_kwargs())
        params = params.with_changes(kwonly_params=kwonly_params)

        if is_overload:
            node = node.with_changes(params=params)
            return node

        # make an overload before permissions
        empty_overload = node.deep_clone().with_changes(params=empty_overload_params)
        empty_overload = empty_overload.with_changes(
            body=cst.IndentedBlock([cst.SimpleStatementLine([cst.Expr(cst.Ellipsis())])]),
            decorators=[
                cst.Decorator(cst.Name("overload")),
                cst.Decorator(cst.Name("_generated")),
            ],
        )
        # if the decorated method is an overload we make an in-place change and don't add overloads

        overload = empty_overload.deep_clone()
        overload = overload.with_changes(params=params)

        codevisitors.AddImportsVisitor.add_needed_import(self.context, "typing", "overload")
        codevisitors.AddImportsVisitor.add_needed_import(
            self.context, "disnake.utils", "_generated"
        )

        return cst.FlattenSentinel([overload, empty_overload, node])
