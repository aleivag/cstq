from functools import partial
from typing import Callable

import libcst as cst
import libcst.matchers as m

from cstq.nodes.extended import CSTQExtendedNode

from .obj2x import obj2x, str2xattr

MATCH_INPUT = m.BaseMatcherNode | Callable[[cst.CSTNode | CSTQExtendedNode], bool] | cst.CSTNode | CSTQExtendedNode


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
str2mattr = partial(str2xattr, x=m)
# TODO: replace build_attribute_matcher with str2mattr
