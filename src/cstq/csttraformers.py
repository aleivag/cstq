from dataclasses import dataclass
from enum import Enum, auto

import libcst as cst

from cstq.node2id import NodeIDProvider


class ReplaceNodeTransformer(cst.CSTTransformer):
    METADATA_DEPENDENCIES = (NodeIDProvider,)

    def __init__(self, replace_map: dict[str, cst.CSTNode | cst.RemovalSentinel]) -> None:
        self.replace_map = replace_map
        super().__init__()

    def on_leave(  # type: ignore
        self, old_node: cst.CSTNodeT, new_node: cst.CSTNode | cst.RemovalSentinel
    ) -> cst.CSTNode | cst.RemovalSentinel:
        node_id = self.get_metadata(NodeIDProvider, old_node)
        node = self.replace_map.get(node_id)

        if node:
            return node

        return new_node


class InsertMode(Enum):
    insert = auto()
    append = auto()
    extend = auto()


@dataclass(frozen=True)
class InsertAction:
    node_id: str
    attribute: str
    index: int
    node: cst.CSTNode | list[cst.CSTNode]
    mode: InsertMode


class InserterNodeTransformer(cst.CSTTransformer):
    METADATA_DEPENDENCIES = (NodeIDProvider,)

    def __init__(self) -> None:
        self.inserter_map: dict[str, list[InsertAction]] = {}
        super().__init__()

    def add_inserter(self, node_id, attribute, index, node, mode):
        if node_id not in self.inserter_map:
            self.inserter_map[node_id] = []

        self.inserter_map[node_id].append(
            InsertAction(node_id=node_id, attribute=attribute, index=index, node=node, mode=mode)
        )

    def on_leave(  # type: ignore
        self, old_node: cst.CSTNodeT, new_node: cst.CSTNode | cst.RemovalSentinel
    ) -> cst.CSTNode | cst.RemovalSentinel:
        node_id = self.get_metadata(NodeIDProvider, old_node)
        actions = self.inserter_map.get(node_id, [])

        for action in actions:
            attr = getattr(new_node, action.attribute)
            assert isinstance(attr, (list, tuple)), f"{action.attribute} for {action.node_id} should be a sequence"
            attr = list(attr)

            if action.mode == InsertMode.insert:
                attr.insert(action.index, action.node)
            elif action.mode == InsertMode.append:
                attr.append(action.node)
            elif action.mode == InsertMode.extend:
                attr.extend(action.node)

            new_node = new_node.with_changes(**{action.attribute: attr})

        return new_node
