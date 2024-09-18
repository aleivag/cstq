from __future__ import annotations
from functools import singledispatch
from typing import Generator, Tuple

import libcst as cst

from cstq.nodes.range import CSTQRange
from dataclasses import dataclass
from itertools import zip_longest


@dataclass(frozen=True, slots=True, repr=False, eq=True)
class PathID:
    parent:None = None

    def __str__(self):
        return self.id()
    
    def __repr__(self):
        return self.id()
    
    def cmp_val(self, value):
        if self == value:
            return 0
        else:
            raise RuntimeError("cmpvar err")

    def cmp(self, value: PathID):
        for a, b in zip_longest(reversed([self, *self.parents]), reversed([value, *value.parents])):
            if a is None:
                return -1
            if b is None:
                return 1
            
            if type(a) != type(b):
                raise RuntimeError(f"{a.id()} != {b.id()}")
            
            ncmp = a.cmp_val(b)
            if ncmp != 0:
                return ncmp
        return ncmp
            

    def __lt__(self, value: object) -> bool:
        return self.cmp(value) < 0

    def __le__(self, value: object) -> bool:
        return self.cmp(value) <= 0
    
    def __gt__(self, value: object) -> bool:
        return self.cmp(value) > 0

    def __ge__(self, value: object) -> bool:
        return self.cmp(value) >= 0

    def attribute(self, attr: str) -> AttributeID:
        return AttributeID(parent=self, attr=attr)

    def item(self, key: object) -> ItemID:
        return ItemID(parent=self, key=key)
    
    def solve(self, obj):
        return obj
    
    def resolve(self, obj):
        imp = obj
        for path in reversed([*self.parents]):
            imp = path.solve(imp)
        return self.solve(imp)

    def id(self):
        return "$"
    
    @property
    def parents(self) -> Generator["PathID", None, None]:
        if self.parent:
            yield self.parent
            yield from self.parent.parents
    

@dataclass(frozen=True, slots=True, repr=False)
class AttributeID(PathID):
    parent: PathID
    attr: str

    def solve(self, obj):
        return getattr(obj, self.attr)
    
    def id(self):
        return f'{self.parent.id()}.{self.attr}'
    
    def cmp_val(self, value):
        if self.attr < value.attr:
            return -1
        elif self.attr == value.attr:
            return 0
        else:
            return 1


@dataclass(frozen=True, slots=True, repr=False)
class ItemID(PathID):
    parent: PathID
    key: object

    def solve(self, obj):
        return obj[self.key]

    def id(self):
        return f'{self.parent.id()}[{self.key}]'
    
    def cmp_val(self, value):
        if self.key < value.key:
            return -1
        elif self.key == value.key:
            return 0
        else:
            return 1


class NodeIDProvider(cst.VisitorMetadataProvider[str]):
    def visit_Module(self, module_node: cst.Module) -> None:  # noqa: N802
        for node, node_id in node2id(module_node):
            self.set_metadata(node, node_id)


@singledispatch
def __node2id(
    node, objid: PathID, parent_node=None, attribute=None
) -> Generator[Tuple[cst.CSTNode, str], None, None]:
    yield from []


@__node2id.register(list)
@__node2id.register(set)
@__node2id.register(tuple)
def _(e: list, objid: PathID, parent_node, attribute) -> Generator[Tuple[cst.CSTNode, str], None, None]:
    yield CSTQRange(elems=e, parent=parent_node, attribute=attribute), objid
    for item, elem in enumerate(e):
        yield from __node2id(elem, objid.item(item))


@__node2id.register(cst.CSTNode)
def _(node, objid: PathID, parent_node=None, attribute=None) -> Generator[Tuple[cst.CSTNode, str], None, None]:
    yield node, objid

    for attr in node.__dataclass_fields__:
        if attr in ("__slots__",):
            # this is not a real field of a cstnode, its more of a dataclass thingi, ignore it
            continue

        yield from [
            inner
            for inner in __node2id(
                getattr(node, attr),
                objid.attribute(attr),
                parent_node=node, 
                attribute=attr,
            )
            if inner
        ]


def node2id(module_node: cst.Module):
    yield from __node2id(module_node, PathID())