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
        return False

    def leave_FunctionDef(self, node: cst.FunctionDef, new_node: cst.FunctionDef):
        has_overload_deco = False
        is_overload = False
        previously_generated = False
        for deco in new_node.decorators:
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
            return new_node

        node = new_node

        # if the function is not an overload and is decorated with the deco
        if not node.params.star_kwarg and not is_overload:
            raise RuntimeError(
                'a function cannot be decorated with "_overload_with_permissions" and not take any kwargs.'
            )
        elif node.params.star_kwarg:
            # use the existing annotation if one exists
            annotation = node.params.star_kwarg.annotation
            if annotation is None:
                raise RuntimeError(
                    f"parameter {node.params.star_kwarg.name.value} must be annotated."
                )
        else:
            # use the first permission annotation if it exists, otherwise default to `bool`
            # make a matcher instance of all valid permission names
            matches = m.Name(self.permissions[0])
            for perm in self.permissions[1:]:
                matches |= m.Name(perm)
            for kw_param in node.params.kwonly_params:
                if (
                    kw_param.annotation
                    and m.matches(kw_param.name, matches)
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

            existing_kwonly_params = list(params.kwonly_params)
            for param in existing_kwonly_params.copy():
                if param.name.value in self.permissions:
                    existing_kwonly_params.remove(param)

            star_arg = params.star_arg if existing_kwonly_params else cst.MaybeSentinel.DEFAULT
            return params.with_changes(
                params=existing_params,
                kwonly_params=existing_kwonly_params,
                star_arg=star_arg,
            )

        # now we have the function, we can add all of the permissions
        params = remove_existing_permissions(node.params)
        # also remove the permissions from the original node
        node = node.with_changes(params=params)
        # remove kwargs from the params
        params = params.with_changes(star_kwarg=None)
        # make an overload before permissions
        empty_overload = node.deep_clone().with_changes(params=params)
        empty_overload = empty_overload.with_changes(
            body=cst.IndentedBlock([cst.SimpleStatementLine([cst.Expr(cst.Ellipsis())])]),
            decorators=[
                cst.Decorator(cst.Name("overload")),
                cst.Decorator(cst.Name("_generated")),
            ],
        )

        perms = []
        # we use the annotation of kwargs

        for perm in self.permissions:
            perms.append(
                cst.Param(
                    cst.Name(perm),
                    annotation,
                    default=cst.Ellipsis(),
                )
            )

        codevisitors.AddImportsVisitor.add_needed_import(self.context, "typing", "overload")

        overload = empty_overload.deep_clone()
        params = remove_existing_permissions(overload.params)
        kwonly_params = list(params.kwonly_params)
        kwonly_params.extend(perms)
        params = params.with_changes(kwonly_params=kwonly_params, star_kwarg=None)
        if is_overload:
            node = node.with_changes(params=params)
            return node

        overload = overload.with_changes(params=params)

        # only add the import if we're using the empty overload
        codevisitors.AddImportsVisitor.add_needed_import(
            self.context, "disnake.utils", "_generated"
        )

        return cst.FlattenSentinel([overload, empty_overload, node])
