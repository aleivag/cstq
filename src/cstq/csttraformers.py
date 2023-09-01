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
