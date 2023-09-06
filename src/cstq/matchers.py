from functools import partial
from typing import Callable

import libcst as cst
import libcst.matchers as m

MATCH_INPUT = m.BaseMatcherNode | Callable[[cst.CSTNode], bool] | cst.CSTNode


def match(
    node: cst.CSTNode,
    test: MATCH_INPUT | list[MATCH_INPUT] | tuple[MATCH_INPUT, ...],
) -> bool:
    if isinstance(test, m.BaseMatcherNode):
        return m.matches(node, test)
    elif callable(test):
        return test(node)
    elif isinstance(test, cst.CSTNode):
        return node.deep_equals(test)
    elif isinstance(test, (list, tuple)):
        return all(match(node, t) for t in test)
    else:
        return test == node


def matcher(test: MATCH_INPUT | list[MATCH_INPUT] | tuple[MATCH_INPUT, ...]) -> Callable[[cst.CSTNode], bool]:
    return partial(match, test=test)
