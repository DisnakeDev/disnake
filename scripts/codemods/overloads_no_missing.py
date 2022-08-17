from typing import List, Optional

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

        for param_type in ["params", "kwonly_params", "posonly_params"]:
            params: List[cst.Param] = getattr(node.params, param_type, [])
            if not params:
                continue

            new_params: List[cst.Param] = []
            for param in params:
                if not param.default:
                    new_params.append(param)
                    continue
                if isinstance(param.default, cst.Ellipsis):
                    new_params.append(param)
                    continue
                if not isinstance(param.default, cst.Name):
                    new_params.append(param)
                elif param.default.value == "MISSING":
                    new_param = param.with_changes(default=cst.Ellipsis())
                    new_params.append(new_param)
                else:
                    new_params.append(param)
            kw = {}
            kw[param_type] = new_params
            node = node.with_deep_changes(node.params, **kw)

        return node
