from typing import Callable

import libcst as cst


class Extractor(cst.CSTVisitor):
    def __init__(self, match_test: Callable[[cst.CSTNode], bool]) -> None:
        self.match_test = match_test
        self.result: list[cst.CSTNode] = []
        super().__init__()

    def on_visit(self, node: cst.CSTNode) -> bool:
        if self.match_test(node):
            self.result.append(node)
        return True

    @staticmethod
    def match(node: cst.CSTNode, match_test: Callable[[cst.CSTNode], bool]) -> list[cst.CSTNode]:
        """
        returns all the children nodes (counting node itself) that pass the match test
        """
        e = Extractor(match_test)
        node.visit(e)
        return e.result
