from __future__ import annotations

import ast
from dataclasses import dataclass, fields
from functools import partial
from typing import TYPE_CHECKING, cast, Any

import libcst as cst

if TYPE_CHECKING:
    import cstq


@dataclass(frozen=True)
class CSTQExtendedNode:
    root: cstq.query.Query
    node_id: str

    __registered_class = {}

    def node(self) -> cst.CSTNode:
        return self.root.get_node_by_id(self.node_id)

    def get_original_node_attr(self, attr):
        node = getattr(self.node(), attr)
        if isinstance(node, tuple):
            return (self.root.get_extended_node(e) for e in node)
        if isinstance(node, cst.CSTNode):
            return self.root.get_extended_node(node)
        return node

    @classmethod
    def register_type(cls, registered_class):
        libcst_baseclass = registered_class.mro()[1]
        cls.__registered_class[libcst_baseclass] = registered_class
        return registered_class

    @classmethod
    def from_node(cls, node: cst.CSTNode, root: cstq.query.Query) -> CSTQExtendedNode:
        node_cls = cls.__registered_class.get(node.__class__, node.__class__)
        node_id = root.get_node_id(node)

        original_fields = tuple(field.name for field in fields(node))
        extended_node_cls = type(
            node_cls.__name__,
            (cls, node_cls),
            {
                "root": None,
                "__module__": node_cls.__module__,
                "__name__": node_cls.__name__,
                "__qualname__": node_cls.__qualname__,
                "__doc__": node_cls.__doc__,
                "__annotations__": {
                    "root": None,
                    "original_node": None,
                },
                **{field: property(fget=partial(cls.get_original_node_attr, attr=field)) for field in original_fields},
            },
        )
        # dataclass(frozen=True)(extended_node_cls)

        return cast(
            CSTQExtendedNode,
            extended_node_cls(
                # **{field.name: getattr(node, field.name) for field in fields(node)},
                root=root,
                node_id=node_id,
            ),
        )

    def parent(self) -> CSTQExtendedNode:
        return self.root.get_extended_node(self.root.get_parent_of_node(self.node()))

    def code(self, module=None) -> str:
        return (module if module else self.root.module).code_for_node(self.node())

    def literal_eval(self):
        return ast.literal_eval(self.code())

    def match(self, test):
        from cstq.matchers import match

        return match(self, test, self.root)

    def collection(self):
        return self.root.collection([self.node_id])

    def replace(self, new_node) -> None:
        self.collection().replace(new_node)

    def change(self, *args, **kwargs) -> CSTQExtendedNode:
        self.collection().change(*args, **kwargs)
        return self

    def remove(self) -> None:
        self.collection().remove()

    def with_changes(self, **changes: Any) -> cst.CSTNode:
        return self.node().with_changes(**changes)









