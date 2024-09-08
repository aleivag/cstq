from functools import singledispatch
from typing import Generator, Tuple

import libcst as cst

from cstq.nodes.range import CSTQRange


class NodeIDProvider(cst.VisitorMetadataProvider[str]):
    def visit_Module(self, module_node: cst.Module) -> None:  # noqa: N802
        for node, node_id in node2id(module_node, "$", parent=None, attribute=None):
            self.set_metadata(node, node_id)


@singledispatch
def node2id(
    node, id_prefix: str, parent: cst.CSTNode, attribute: str  # noqa: ARG001  # noqa: ARG001
) -> Generator[Tuple[cst.CSTNode, str], None, None]:
    yield from []


@node2id.register(list)
@node2id.register(set)
@node2id.register(tuple)
def _(e: list, id_prefix: str, parent: cst.CSTNode, attribute: str) -> Generator[Tuple[cst.CSTNode, str], None, None]:
    yield CSTQRange(elems=e, parent=parent, attribute=attribute), id_prefix
    for n, elem in enumerate(e):
        yield from node2id(elem, f"{id_prefix}[{n}]", parent=parent, attribute=attribute)


@node2id.register(cst.CSTNode)
def _(node, id_prefix: str, parent: cst.CSTNode, attribute: str) -> Generator[Tuple[cst.CSTNode, str], None, None]:
    id_prefix = f"{id_prefix}({type(node).__name__})"
    yield node, id_prefix

    for attr in node.__dataclass_fields__:
        if attr in ("__slots__",):
            # this is not a real field of a cstnode, its more of a dataclass thingi, ignore it
            continue
        yield from [
            inner
            for inner in node2id(
                getattr(node, attr),
                id_prefix=f"{id_prefix}.{attr}",
                parent=node,
                attribute=attr,
            )
            if inner
        ]
