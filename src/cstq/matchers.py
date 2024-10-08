from functools import partial
from typing import Callable

import libcst as cst
import libcst.matchers as m

from cstq.nodes.extended import CSTQExtendedNode

MATCH_INPUT = m.BaseMatcherNode | Callable[[cst.CSTNode | CSTQExtendedNode], bool] | cst.CSTNode | CSTQExtendedNode


def match(
    node: cst.CSTNode | CSTQExtendedNode,
    test: MATCH_INPUT | list[MATCH_INPUT] | tuple[MATCH_INPUT, ...],
    root: "cstq.query.Query",
) -> bool:
    if isinstance(test, m.BaseMatcherNode):
        return m.matches(node, test)

    if isinstance(test, (list, tuple)):
        return all(match(node, t, root) for t in test)

    if not isinstance(node, CSTQExtendedNode):
        node = root.get_extended_node(node)

    if callable(test):
        return test(node)
    elif isinstance(test, cst.CSTNode):
        return node.original_node.deep_equals(test)
    else:
        return test == node


def matcher(
    test: MATCH_INPUT | list[MATCH_INPUT] | tuple[MATCH_INPUT, ...], root: "cstq.query.Query"
) -> Callable[[cst.CSTNode], bool]:
    return partial(match, test=test, root=root)
