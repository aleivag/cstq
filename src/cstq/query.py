from __future__ import annotations

from functools import singledispatch
from pathlib import Path
from typing import Any, Iterable, NoReturn, Sequence

import libcst as cst
import libcst.matchers as m

from cstq.csttraformers import ReplaceNodeTransformer
from cstq.cstvisitors import Extractor
from cstq.matchers import matcher
from cstq.node2id import NodeIDProvider


class CollectionOfNodes:
    def __init__(self, node_ids: Iterable[str], root: Query) -> None:
        self.__node_ids = sorted(set(node_ids))
        self.root = root

    @property
    def __nodes(self) -> dict[str, cst.CSTNode]:
        return {node_id: node for node_id, node in self.root.get_nodes_by_id(self.__node_ids).items() if node}

    @property
    def _nodes_id(self) -> list[str]:
        return self.__node_ids

    def filter(self, test) -> CollectionOfNodes:  # noqa: A003
        match_test = matcher(test)
        return CollectionOfNodes(
            [node_id for node_id in self.__node_ids if match_test(self.root.get_node_by_id(node_id))],
            root=self.root,
        )

    def filter_by_type(self, type_, test=None) -> CollectionOfNodes:
        return self.filter(lambda x: isinstance(x, type_) and (test(x) if test is not None else True))

    def search(self, test) -> CollectionOfNodes:
        return CollectionOfNodes(
            (
                self.root.get_node_id(found_node)
                for node in self.__nodes.values()
                for found_node in Extractor.match(node, matcher(test))
            ),
            root=self.root,
        )

    def search_by_type(self, type_, test=None) -> CollectionOfNodes:
        return self.search(lambda x: isinstance(x, type_) and (test(x) if test is not None else True))

    # find functions
    def find_function_call(self, func_name: str | None = None) -> CollectionOfNodes:
        nodes = self.search(m.Call(func=m.Name(value=func_name) if func_name else m.DoNotCare()))
        return nodes

    def __or__(self, other):
        assert self.root == other.root, "Both collections must have the same root"
        CollectionOfNodes([*self.__node_ids, *other._nodes_id], root=self.root)

    def __getitem__(self, item) -> CollectionOfNodes:
        if callable(item):
            return self.filter(item)
        if isinstance(item, int):
            return CollectionOfNodes([self.__node_ids[item]], root=self.root)
        if isinstance(item, slice):
            # maybe treat slice a bit different
            return CollectionOfNodes(self.__node_ids[item], root=self.root)

        msg = f"{item} of {type(item)=} not implemented/allowed"
        raise NotImplementedError(msg)

    def __getattr__(self, item) -> CollectionOfNodes:
        results: list[cst.CSTNode] = []
        for _node_id, node in self.__nodes.items():
            if not hasattr(node, item):
                continue
            attr = getattr(node, item)
            if isinstance(attr, (list, tuple)):
                results.extend(attr)
            else:
                results.append(attr)

        return CollectionOfNodes(self.root.get_nodes_id(results).values(), self.root)

    def __repr__(self) -> str:
        return f"<CollectionOfNodes nodes={self.__node_ids}>"

    def __len__(self) -> int:
        return len(self.__node_ids)

    def change(self, **kwargs) -> CollectionOfNodes:
        return CollectionOfNodes(
            self.root.replace_nodes({node_id: node.with_changes(**kwargs) for node_id, node in self.__nodes.items()}),
            self.root,
        )

    def replace(self, new_node: cst.CSTNode | cst.RemovalSentinel) -> CollectionOfNodes:
        new_node_ids = self.root.replace_nodes({node_id: new_node for node_id in self.__node_ids})
        return CollectionOfNodes([new_id for new_id in new_node_ids if new_id], self.root)

    # def swap(self, new_node: cst.CSTNode )  -> CollectionOfNodes:
    #     assert len(self.__node_ids) == 1, "you can only swap one node"
    #
    #     self.root.replace_nodes({
    #         self.__node_ids[0]: new_node,
    #         self.root.get_node_id(new_node): self.node(),
    #     })

    def remove(self) -> CollectionOfNodes:
        return self.replace(cst.RemovalSentinel.REMOVE)

    def node(self) -> cst.CSTNode:
        assert len(self.__node_ids) <= 1, "you have more than one, use nodes to get them all"
        assert len(self.__node_ids) == 1, "you have 0 nodes"

        return self.__nodes[self.__node_ids[0]]

    def nodes(self) -> list[cst.CSTNode]:
        return [*self.__nodes.values()]

    def childrens(self) -> CollectionOfNodes:
        node_ids = self.root.get_nodes_id(
            [children for node in self.__nodes.values() for children in node.children]
        ).values()
        return CollectionOfNodes(list(node_ids), self.root)

    def parent(self) -> CollectionOfNodes:
        node_ids = self.root.get_nodes_id(
            [self.root.get_parent_of_node(node) for node in self.__nodes.values()]
        ).values()
        return CollectionOfNodes(list(node_ids), self.root)

    def search_for_parents(self, test) -> CollectionOfNodes:
        result = []
        parents = {self.root.get_parent_of_node(node) for node in self.__nodes.values()}
        while len(parents) != 1 and not isinstance([*parents][0], cst.Module):
            for parent in parents:
                if test(parent):
                    result.append(self.root.get_node_id(parent))
            parents = {self.root.get_parent_of_node(node) for node in parents}
        return CollectionOfNodes(list(set(result)), self.root)


class Query(CollectionOfNodes):
    def __init__(self, mod: cst.CSTNode | str | Path) -> None:
        parsed_mod: cst.Module = parse_module(mod)
        self.wrapper: cst.metadata.MetadataWrapper = cst.metadata.MetadataWrapper(parsed_mod)
        self.module: cst.Module = self.wrapper.module

        self.__node_to_id: dict[cst.CSTNode, str] = self.wrapper.resolve(NodeIDProvider)
        self.__id_to_node: dict[str, cst.CSTNode] = {v: k for k, v in self.__node_to_id.items()}

        CollectionOfNodes.__init__(self, [self.get_node_id(self.module)], self)

    def get_node_id(self, node: cst.CSTNode) -> str:
        return self.__node_to_id[node]

    def get_nodes_id(self, nodes: list[cst.CSTNode]) -> dict[cst.CSTNode, str]:
        return {node: self.get_node_id(node) for node in nodes}

    def get_node_by_id(self, node_id: str) -> cst.CSTNode:
        return self.__id_to_node[node_id]

    def get_nodes_by_id(self, ids: Sequence[str]) -> dict[str, cst.CSTNode]:
        return {id_: self.get_node_by_id(id_) for id_ in ids}

    def replace_nodes(self, replace_map: dict[str, cst.CSTNode | cst.RemovalSentinel]):
        mod = self.wrapper.visit(ReplaceNodeTransformer(replace_map))
        self.__init__(mod)  # type: ignore

        return [None if to_node == cst.RemovalSentinel.REMOVE else from_id for from_id, to_node in replace_map.items()]

    def get_parent_of_node(self, node: cst.CSTNode) -> cst.CSTNode:
        return self.wrapper.resolve(cst.metadata.ParentNodeProvider)[node]

    def code(self) -> str:
        return self.module.code

    def write(self, path: Path) -> int:
        return path.write_text(self.code())


@singledispatch
def parse_module(module: Any) -> NoReturn:
    msg = f"Cant parse {type(module)} as module"
    raise RuntimeError(msg)


@parse_module.register(cst.Module)
def _(module: cst.Module) -> cst.Module:
    return module


@parse_module.register(str)
def _(module: str) -> cst.Module:
    return parse_module(cst.parse_module(module))


@parse_module.register(Path)
def _(module: Path) -> cst.Module:
    return parse_module(module.read_text())
