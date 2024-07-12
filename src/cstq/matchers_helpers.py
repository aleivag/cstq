from functools import partial
from typing import Callable

import libcst as cst
import libcst.matchers as m

import cstq.nodes

from .obj2x import obj2x

MATCH_INPUT = (
    m.BaseMatcherNode
    | Callable[[cst.CSTNode | cstq.nodes.CSTQExtendedNode], bool]
    | cst.CSTNode
    | cstq.nodes.CSTQExtendedNode
)


def build_attribute_matcher(mod):
    nmod = [*mod.copy()]

    def _attribute_matcher(attr, mod):
        if not mod:
            return m.Name(attr)
        else:
            value = _attribute_matcher(mod.pop(), mod)

        return m.Attribute(value=value, attr=m.Name(attr))

    return _attribute_matcher(nmod.pop(), nmod)


obj2m = obj2x(m)
