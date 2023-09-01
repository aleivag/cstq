from functools import partial
from typing import Callable

import libcst as cst
import libcst.matchers as m


def match(
    node: cst.CSTNode,
    test: m.BaseMatcherNode | Callable[[cst.CSTNode], bool] | cst.CSTNode,
) -> bool:
    if isinstance(test, m.BaseMatcherNode):
        return m.matches(node, test)
    elif callable(test):
        return test(node)
    elif isinstance(test, cst.CSTNode):
        return node.deep_equals(test)
    else:
        return test == node


def matcher(test: m.BaseMatcherNode | Callable[[cst.CSTNode], bool] | cst.CSTNode) -> Callable[[cst.CSTNode], bool]:
    return partial(match, test=test)
