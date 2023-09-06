from __future__ import annotations

from dataclasses import dataclass
from typing import NoReturn, Sequence

import libcst as cst
from libcst._add_slots import add_slots
from libcst._nodes.internal import CodegenState  # noqa: F401


@add_slots
@dataclass(frozen=True)
class CSTRange(cst.CSTNode):
    elems: Sequence[cst.CSTNode]

    def _codegen_impl(
        self,
        state: cst._nodes.internal.CodegenState,
    ) -> None:
        raise NotImplementedError()

    def _visit_and_replace_children(self, visitor: cst.CSTVisitorT) -> NoReturn:  # cst.CSTNode:
        raise NotImplementedError()

    def __getitem__(self, item) -> cst.CSTNode:
        return self.elems[item]

    def __len__(self) -> int:
        return len(self.elems)

    def __iter__(self):
        return iter(self.elems)
