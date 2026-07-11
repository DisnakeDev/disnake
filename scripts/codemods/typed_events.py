# SPDX-License-Identifier: MIT

from __future__ import annotations

from collections import defaultdict
from typing import cast

import libcst as cst
import libcst.matchers as m

from disnake import Event
from disnake._event_data import EVENT_DATA, EventData

from .base import BaseCodemodCommand


def get_param(func: cst.FunctionDef, name: str) -> cst.Param:
    results = m.findall(func.params, m.Param(m.Name(name)))
    assert len(results) == 1
    return cast("cst.Param", results[0])


class EventTypings(BaseCodemodCommand):
    DESCRIPTION: str = "Adds overloads for library events."
    CHECK_MARKER: str = "@_overload_with_events"

    def visit_FunctionDef(self, node: cst.FunctionDef) -> bool | None:
        # don't recurse into the body of a function
        return False

    def leave_FunctionDef(
        self, _: cst.FunctionDef, node: cst.FunctionDef
    ) -> cst.FlattenSentinel[cst.FunctionDef] | cst.FunctionDef | cst.RemovalSentinel:
        decorators = [
            deco.decorator.value for deco in node.decorators if isinstance(deco.decorator, cst.Name)
        ]
        if "_generated" in decorators:
            # remove generated methods
            return cst.RemovalSentinel.REMOVE
        if "_overload_with_events" not in decorators:
            # ignore
            return node

        if node.name.value == "wait_for":
            generator = self.generate_wait_for_overload
        else:
            msg = f"unknown method '{node.name.value}' with @_overload_with_events decorator"
            raise RuntimeError(msg)

        # if we're here, we found a @_overload_with_events decorator

        groups: dict[EventData, list[Event]] = defaultdict(list)
        for event in Event:
            if not (event_data := EVENT_DATA.get(event)):
                msg = f"{event} is missing an EVENT_DATA definition"
                raise RuntimeError(msg)
            groups[event_data].append(event)

        new_overloads: list[cst.FunctionDef] = []
        for event_data, events in groups.items():
            if overload := generator(node, events, event_data):
                new_overloads.append(overload)

        return cst.FlattenSentinel([*new_overloads, node])

    def create_empty_overload(self, func: cst.FunctionDef) -> cst.FunctionDef:
        return func.with_changes(
            body=cst.SimpleStatementLine([cst.Expr(cst.Ellipsis())]),
            decorators=[
                cst.Decorator(cst.Name("overload")),
                cst.Decorator(cst.Name("_generated")),
            ],
            leading_lines=[cst.EmptyLine()],
        )

    def create_literal(self, events: list[Event]) -> cst.BaseExpression:
        event_literals = [f'Event.{event.name}, "{event.value}"' for event in events]
        return cst.parse_expression(
            f"Literal[{', '.join(event_literals)}]",
            config=self.module.config_for_parsing,
        )

    def create_args_list(self, event_data: EventData) -> cst.BaseExpression:
        return cst.parse_expression(
            f"[{','.join(event_data.arg_types)}]",
            config=self.module.config_for_parsing,
        )

    def generate_wait_for_overload(
        self, func: cst.FunctionDef, events: list[Event], event_data: EventData
    ) -> cst.FunctionDef | None:
        if event_data.event_only:
            return None
        args = event_data.arg_types

        new_overload = self.create_empty_overload(func)

        # set `event` annotation
        new_overload = new_overload.with_deep_changes(
            get_param(new_overload, "event"),
            annotation=cst.Annotation(self.create_literal(events)),
        )

        # set `check` annotation
        callable_annotation = m.findall(
            get_param(new_overload, "check"), m.Subscript(m.Name("Callable"))
        )[0]
        callable_params = m.findall(callable_annotation, m.Ellipsis())[0]
        new_overload = cast(
            "cst.FunctionDef",
            new_overload.deep_replace(callable_params, self.create_args_list(event_data)),
        )

        # set return annotation
        if len(args) == 0:
            new_annotation_str = "None"
        elif len(args) == 1:
            new_annotation_str = args[0]
        else:
            new_annotation_str = f"tuple[{','.join(args)}]"
        new_annotation = cst.parse_expression(
            f"Coroutine[Any, Any, {new_annotation_str}]",
            config=self.module.config_for_parsing,
        )
        new_overload = new_overload.with_changes(returns=cst.Annotation(new_annotation))

        # set `self` annotation as a workaround for overloads in subclasses
        if event_data.self_type:
            new_overload = new_overload.with_deep_changes(
                get_param(new_overload, "self"),
                annotation=cst.Annotation(cst.Name(event_data.self_type)),
            )

        return new_overload
