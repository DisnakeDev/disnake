from typing import List, Optional, Sequence

import libcst as cst
import libcst.matchers as m
from libcst import codemod

EllipsisType = type(Ellipsis)


class EllipsisOverloads(codemod.VisitorBasedCodemodCommand):
    DESCRIPTION = "Ensure that `MISSING` is not used in any overloads as a default."

    def visit_FunctionDef(self, node: cst.FunctionDef) -> Optional[bool]:
        return False

    def leave_FunctionDef(
        self, node: cst.FunctionDef, new_node: cst.FunctionDef
    ) -> cst.FunctionDef:
        for deco in node.decorators:
            if m.matches(deco.decorator, m.Name("overload")):
                break
        else:
            return node

        kw = {}
        for param_type in ["params", "kwonly_params", "posonly_params"]:
            params: Sequence[cst.Param] = getattr(node.params, param_type)
            if not params:
                continue

            new_params: List[cst.Param] = []
            for param in params:
                if param.default and m.matches(param.default, m.Name("MISSING")):
                    new_param = param.with_changes(default=cst.Ellipsis())
                    new_params.append(new_param)
                else:
                    new_params.append(param)
            kw[param_type] = new_params

        node = node.with_deep_changes(node.params, **kw)

        return node
