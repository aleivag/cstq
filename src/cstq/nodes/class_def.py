from __future__ import annotations

from collections.abc import MutableMapping, MutableSequence
from typing import TYPE_CHECKING

import libcst as cst

from cstq.obj2cst import str2attr

if TYPE_CHECKING:
    from cstq.nodes.extended import CSTQExtendedNode


class Bases(MutableSequence):
    def __init__(self, node: CSTQExtendedNode):
        self.node = node

    def __getitem__(self, item):
        return self.node.bases[item].value.code()

    def __setitem__(self, key, value):
        from cstq.matchers_helpers import build_attribute_matcher

        self.node.bases[key].change(value=str2attr(value))

    def __delitem__(self, key):
        self.node.bases[key].remove()

    def __len__(self):
        return len(self.node.bases)

    def insert(self, index: int, value: str) -> None:
        _bases = [node.node() for node in self.node.bases]
        _bases.insert(index, cst.Arg(value=str2attr(value)))
        self.node.change(bases=_bases)

    def replace_base(self, original: str, final: str) -> None:
        idx = self.index(original)
        self[idx] = final


class CSTQClassDef(cst.ClassDef):
    """
    Wrapper around cst.ClassDef that helps the retrieval of kwargs and pos args
    """

    @property
    def str_bases(self):
        return Bases(self)

    @str_bases.setter
    def str_bases(self, values: list[str]) -> None:
        self.change(bases=[cst.Arg(value=str2attr(value)) for value in values])

    @str_bases.deleter
    def str_bases(self) -> None:
        self.change(bases=[], lpar=cst.MaybeSentinel.DEFAULT, rpar=cst.MaybeSentinel.DEFAULT)

    def __setattr__(self, attr: str, val) -> None:
        if attr == "str_bases":
            CSTQClassDef.str_bases.fset(self, val)
        else:
            super().__setattr__(attr, val)

    def __delattr__(self, attr: str) -> None:
        if attr == "str_bases":
            CSTQClassDef.str_bases.fdel(self)
        else:
            super().__delattr__(attr)

    def replace_base(self, original: str, final: str):
        self.str_bases.replace_base(original, final)
        return self
