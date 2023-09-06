from functools import singledispatch
from typing import Generator, Tuple

import libcst as cst

from cstq.nodes import CSTRange


class NodeIDProvider(cst.VisitorMetadataProvider[str]):
    def visit_Module(self, module_node: cst.Module) -> None:  # noqa: N802
        for node, node_id in node2id(module_node, "$"):
            self.set_metadata(node, node_id)


@singledispatch
def node2id(
    node,  # noqa: ARG001
    id_prefix: str,  # noqa: ARG001
) -> Generator[Tuple[cst.CSTNode, str], None, None]:
    yield from []


@node2id.register(list)
@node2id.register(set)
@node2id.register(tuple)
def _(e: list, id_prefix: str) -> Generator[Tuple[cst.CSTNode, str], None, None]:
    yield CSTRange(elems=e), id_prefix
    for n, elem in enumerate(e):
        yield from node2id(elem, f"{id_prefix}[{n}]")


@node2id.register(cst.CSTNode)
def _(node, id_prefix: str) -> Generator[Tuple[cst.CSTNode, str], None, None]:
    id_prefix = f"{id_prefix}({type(node).__name__})"
    yield node, id_prefix

    for attr in node.__dataclass_fields__:
        yield from [inner for inner in node2id(getattr(node, attr), id_prefix=f"{id_prefix}.{attr}") if inner]
