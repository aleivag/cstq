from __future__ import annotations

import ast
from dataclasses import dataclass, fields
from typing import TYPE_CHECKING, NoReturn, Sequence, cast

import libcst as cst
from libcst._add_slots import add_slots
from libcst._nodes.internal import CodegenState  # noqa: F401

if TYPE_CHECKING:
    import cstq


class CSTQExtendedNode:
    root: cstq.query.Query
    original_node: cst.CSTNode

    @classmethod
    def from_node(cls, node: cst.CSTNode, original_node: cst.CSTNode, root: cstq.query.Query) -> CSTQExtendedNode:
        node_cls = node.__class__
        extended_node_cls = type(
            node_cls.__name__,
            (cls, node_cls),
            {
                "root": None,
                "original_node": node,
                "__module__": node_cls.__module__,
                "__name__": node_cls.__name__,
                "__qualname__": node_cls.__qualname__,
                "__doc__": node_cls.__doc__,
                "__annotations__": {**node_cls.__annotations__, "root": None, "original_node": None},
            },
        )
        dataclass(frozen=True)(extended_node_cls)

        return cast(
            CSTQExtendedNode,
            extended_node_cls(
                **{field.name: getattr(node, field.name) for field in fields(node)},
                root=root,
                original_node=original_node,
            ),
        )

    @classmethod
    def map_module(cls, root):
        class ExtendCSTNodesProvider(cst.CSTTransformer):
            def __init__(self) -> None:
                self.mapping: dict[cst.CSTNode, CSTQExtendedNode] = {}
                super().__init__()

            def on_leave(self, original_node, updated_node):
                self.mapping[original_node] = cls.from_node(updated_node, original_node, root)
                return self.mapping[original_node]

        w = ExtendCSTNodesProvider()
        root.module.visit(w)
        return w.mapping

    def parent(self):
        return self.root.get_extended_node(self.root.get_parent_of_node(self.original_node))

    def code(self, module=None) -> str:
        return (module if module else self.root.module).code_for_node(self.original_node)

    def literal_eval(self):
        return ast.literal_eval(self.code())

    def match(self, test):
        from cstq.matchers import match

        return match(self, test, self.root)


@add_slots
@dataclass(frozen=True)
class CSTQRange(cst.CSTNode):
    elems: Sequence[cst.CSTNode]
    parent: cst.CSTNode
    attribute: str

    def _codegen_impl(
        self,
        state: cst._nodes.internal.CodegenState,
    ) -> None:
        raise NotImplementedError()

    def _visit_and_replace_children(
        self,
        visitor: cst.CSTVisitorT,  # noqa: ARG002
    ) -> NoReturn:  # cst.CSTNode:
        msg = "This is a fake range object, you can visit... expand it with q.elem[:]"
        raise NotImplementedError(msg)

    def __getitem__(self, item) -> cst.CSTNode:
        return self.elems[item]

    def __len__(self) -> int:
        return len(self.elems)

    def __iter__(self):
        return iter(self.elems)

    def insert(self, index, node):
        ...
