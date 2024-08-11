from __future__ import annotations

import ast
from functools import partial, singledispatch
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, NoReturn, Sequence, cast

import libcst as cst
import libcst.matchers as m

from cstq.csttraformers import InserterNodeTransformer, InsertMode, ReplaceNodeTransformer
from cstq.cstvisitors import Extractor
from cstq.matchers import MATCH_INPUT, match, matcher
from cstq.matchers_helpers import build_attribute_matcher
from cstq.node2id import NodeIDProvider
from cstq.nodes import CSTQExtendedNode, CSTQRange


class CollectionOfNodes:
    def __init__(self, node_ids: Iterable[str], root: Query) -> None:
        self.__node_ids = sorted(set(node_ids))
        self.root = root

    @property
    def __nodes(self) -> dict[str, cst.CSTNode]:
        return {node_id: node for node_id, node in self.root.get_nodes_by_id(self.__node_ids).items() if node is not None}

    @property
    def _nodes_id(self) -> list[str]:
        return self.__node_ids

    def slice(self, start=None, end=None, step=None):  # noqa: A003
        return CollectionOfNodes(self.__node_ids[slice(start, end, step)], root=self.root)

    def filter(  # noqa: A003
        self,
        *test: m.BaseMatcherNode | Callable[[cst.CSTNode | CSTQExtendedNode], bool] | cst.CSTNode,
    ) -> CollectionOfNodes:
        match_test = matcher(test, self.root)
        return CollectionOfNodes(
            [
                self.root.get_node_id(real_node)
                for node_id in self.__node_ids
                if (node := self.root.get_node_by_id(node_id))
                for real_node in (node.elems if isinstance(node, CSTQRange) else [node])
                if match_test(real_node)
            ],
            root=self.root,
        )

    def search(
        self,
        *tests: m.BaseMatcherNode | Callable[[cst.CSTNode | CSTQExtendedNode], bool] | cst.CSTNode,
    ) -> CollectionOfNodes:
        return CollectionOfNodes(
            (
                self.root.get_node_id(found_node)
                for node in self.__nodes.values()
                for found_node in Extractor.match(node, matcher(tests, self.root))
            ),
            root=self.root,
        )

    def find_assignment(self, variable_name: str = None) -> CollectionOfNodes:
        nodes = self.search(m.Assign())
        if variable_name is not None:
            nodes = nodes.search(m.AssignTarget(target=m.Name(variable_name))).parent()
        return nodes

    def find_class_def(
        self,
        name: str | None = None,
        *,
        has_bases: list[str] | None = None,
        keyword_has_value: dict[str, MATCH_INPUT] | None = None,
    ) -> CollectionOfNodes:
        """
        Find all class definitions in the collection that match the given criteria. If name is provided and its a string
        it will filter by that class name. If has_bases is provided, then we will check for those as base classes. Same for
        `keyword_has_value` thats a dictionary, where the keys are a string representing the exact keyword, and the value is
        a match expression.

        For instance for the class deifition `class Foo(unittest.TestCase, TestMixIn, answer=42): ...` then

           self.find_class_def("Foo")
           self.find_class_def(has_bases=["unittest.TestCase"])
           self.find_class_def(has_bases=["TestMixIn"])
           self.find_class_def(has_bases=["unittest.TestCase", "TestMixIn"])
           self.find_class_def(has_bases=["TestMixIn"], keyword_has_value={"answer": obj2m(42)})

        they all return the same cclass a collection of nodes, but:

            self.find_class_def("F00")
            self.find_class_def(has_bases=["NotAClass"])
            self.find_class_def(has_bases=["unittest.TestCase", "NotAClass"])

        return an empty collection of nodes

        """

        some_classes = self.search(m.ClassDef(name=m.Name(value=name)) if name else m.ClassDef())

        for base in has_bases or []:
            if isinstance(base, str):
                some_classes = some_classes.bases.filter(
                    m.Arg(
                        value=build_attribute_matcher(base.split(".")),
                    )
                ).parent()
            else:
                raise NotImplementedError("Havent got arround to implemenat serach by anything else")

        for keyword, value in (keyword_has_value or {}).items():
            some_classes = some_classes.keywords.filter(
                m.Arg(keyword=m.Name(value=keyword)),
                lambda enode: match(enode.value, value, root=self.root),
            ).parent()
        return some_classes

    # find functions
    def find_function_call(
        self,
        func_name: str | None = None,
        *,
        has_args: None | list[Any] = None,
        has_kwargs: None | dict[str, Any] = None,
    ) -> CollectionOfNodes:
        # has_args = has_args or []
        has_kwargs = has_kwargs or {}
        nodes = self.search(m.Call(func=m.Name(value=func_name) if func_name else m.DoNotCare()))

        for arg in has_args or []:
            nodes = nodes.search(
                m.Arg(keyword=None),
                partial(lambda value, node: node.value.match(value), arg),
            ).parent()

        for kw_name, kw_value in has_kwargs.items():
            nodes = nodes.search(
                m.Arg(keyword=m.Name(kw_name)),
                partial(lambda value, node: node.value.match(value), kw_value),
            ).parent()

        return nodes

    def find_import_from(self, module: list[str] | str, name: None | str = None):
        if isinstance(module, str):
            module = module.split(".")
        
        module_match: m.BaseMatcherNode | m.DoNotCareSentinel = (
            build_attribute_matcher(module) if module else m.DoNotCare()
        )
        names = [m.ImportAlias(name=m.Name(name))] if name else m.DoNotCare()
        matcher = m.ImportFrom(module=module_match, names=names)

        return self.search(matcher)

    def find_import_alias(self, module: list[str]):
        if isinstance(module, str):
            module = module.split(".")
        module_match: m.BaseMatcherNode | m.DoNotCareSentinel = (
            build_attribute_matcher(module) if module else m.DoNotCare()
        )
        return self.search(m.ImportAlias(name=module_match))

    def __bool__(self):
        return bool(self.__len__())

    def __or__(self, other):
        assert self.root == other.root, "Both collections must have the same root"
        return CollectionOfNodes([*self.__node_ids, *other._nodes_id], root=self.root)

    def __getitem__(self, item) -> CollectionOfNodes:
        if isinstance(item, int):
            return CollectionOfNodes(
                [self.root.get_node_id(node[item]) for node in self.nodes() if isinstance(node, CSTQRange)],
                root=self.root,
            )
        if isinstance(item, slice):
            # maybe treat slice a bit different
            return CollectionOfNodes(
                [
                    self.root.get_node_id(elem)
                    for node in self.nodes()
                    if isinstance(node, CSTQRange)
                    for elem in cast(CSTQRange, node[item])
                ],
                root=self.root,
            )

        return self.filter(item)

    def __getattr__(self, item) -> CollectionOfNodes:
        results: list[str] = []
        for _node_id, node in self.__nodes.items():
            if not hasattr(node, item):
                continue

            attr = getattr(node, item)
            if isinstance(attr, cst.CSTNode):
                results.append(self.root.get_node_id(attr))
            elif isinstance(attr, (list, tuple)):
                results.append(f"{_node_id}.{item}")

        return CollectionOfNodes(
            results,
            self.root,
        )

    def __repr__(self) -> str:
        return f"<CollectionOfNodes nodes={self.__node_ids}>"

    def __len__(self) -> int:
        return len(self.__node_ids)

    def change(self, *arg, **kwargs) -> CollectionOfNodes:
        assert len(arg) < 2, "should provide only one callable"
        if arg:
            callable_ = arg[0]
        else:

            def callable_(n):
                return n

        return CollectionOfNodes(
            self.root.replace_nodes(
                {
                    node_id: callable_(self.root.get_extended_node(node)).with_changes(**kwargs)
                    for node_id, node in self.__nodes.items()
                }
            ),
            self.root,
        )

    def replace(self, new_node: cst.CSTNode | cst.RemovalSentinel | CollectionOfNodes) -> CollectionOfNodes:
        if isinstance(new_node, CollectionOfNodes):
            return self.replace(new_node.node())

        new_node_ids = self.root.replace_nodes({node_id: new_node for node_id in self.__node_ids})
        return CollectionOfNodes([new_id for new_id in new_node_ids if new_id], self.root)

    def insert(self, index: int, object: cst.CSTNode | CSTQExtendedNode | CollectionOfNodes) -> None:
        if isinstance(object, CollectionOfNodes):
            return self.insert(index=index, object=object.node())

        nodes = self.nodes()
        assert all(isinstance(node, CSTQRange) for node in nodes), "all nodes need to be a instance of a CSTQRange"

        transformer = InserterNodeTransformer()
        for node in nodes:
            transformer.add_inserter(
                node_id=self.root.get_node_id(node.parent),
                attribute=node.attribute,
                index=index,
                node=object,
                mode=InsertMode.insert,
            )
        self.root.transform(transformer)
    
    def insert_before(self, object: cst.CSTNode | CSTQExtendedNode | CollectionOfNodes) -> None:
        # get position of obj
        if isinstance(object, CollectionOfNodes):
            return self.insert_before(object=object.node())
        
        transformer = InserterNodeTransformer()
        for node_id in self.__node_ids:
            node = self.root.get_node_by_id(node_id)
            range_parent_id = self.root.get_range_parent_id_by_id(node_id)
            range_parent_node = self.root.get_node_by_id(range_parent_id)

            parent_id = self.root.get_node_id(range_parent_node.parent)
            
            index = range_parent_node.elems.index(node)
            
            transformer.add_inserter(
                node_id=parent_id,
                attribute=range_parent_node.attribute,
                index=index,
                node=object,
                mode=InsertMode.insert,
            )
        
        self.root.transform(transformer)


    
    def insert_after(self, object: cst.CSTNode | CSTQExtendedNode | CollectionOfNodes) -> None:
        # get position of obj
        if isinstance(object, CollectionOfNodes):
            return self.insert_before(object=object.node())
        
        transformer = InserterNodeTransformer()
        for node_id in self.__node_ids:
            node = self.root.get_node_by_id(node_id)
            range_parent_id = self.root.get_range_parent_id_by_id(node_id)
            range_parent_node = self.root.get_node_by_id(range_parent_id)

            parent_id = self.root.get_node_id(range_parent_node.parent)
            
            index = range_parent_node.elems.index(node)
            
            transformer.add_inserter(
                node_id=parent_id,
                attribute=range_parent_node.attribute,
                index=index + 1,
                node=object,
                mode=InsertMode.insert,
            )
        
        self.root.transform(transformer)

    def append(self, object: cst.CSTNode | CSTQExtendedNode) -> None:
        if isinstance(object, CollectionOfNodes):
            return self.append(object=object.node())

        nodes = self.nodes()
        assert all(isinstance(node, CSTQRange) for node in nodes), "all nodes need to be a instance of a CSTQRange"

        transformer = InserterNodeTransformer()
        for node in nodes:
            transformer.add_inserter(
                node_id=self.root.get_node_id(node.parent),
                attribute=node.attribute,
                index=-1,
                node=object,
                mode=InsertMode.append,
            )
        self.root.transform(transformer)

    def extend(self, iterable: list[cst.CSTNode | CSTQExtendedNode | CSTQRange] | CollectionOfNodes) -> None:
        if isinstance(iterable, CollectionOfNodes):
            return self.extend(iterable.nodes())

        nodes = self.nodes()
        assert all(isinstance(node, CSTQRange) for node in nodes), "all nodes need to be a instance of a CSTQRange"

        transformer = InserterNodeTransformer()
        for node in nodes:
            transformer.add_inserter(
                node_id=self.root.get_node_id(node.parent),
                attribute=node.attribute,
                index=-1,
                node=iterable,
                mode=InsertMode.extend,
            )
        self.root.transform(transformer)

    def remove(self) -> CollectionOfNodes:
        return self.replace(cst.RemovalSentinel.REMOVE)

    def node(self) -> cst.CSTNode:
        assert len(self.__node_ids) <= 1, "you have more than one, use nodes to get them all"
        assert len(self.__node_ids) == 1, "you have 0 nodes"

        return self.__nodes[self.__node_ids[0]]

    def nodes(self) -> list[cst.CSTNode]:
        return [*self.__nodes.values()]

    def extended_node(self) -> CSTQExtendedNode:
        return self.root.get_extended_node(self.node())

    def extended_nodes(self) -> list[CSTQExtendedNode]:
        return [self.root.get_extended_node(node) for node in self.nodes()]

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

    def code_for_nodes(self) -> list[str]:
        return [self.root.module.code_for_node(node) for node in self.nodes()]

    def code_for_node(self) -> str:
        return self.root.module.code_for_node(self.node())

    def literal_eval_for_node(self):
        return ast.literal_eval(self.code_for_node())

    def literal_eval_for_nodes(self):
        return [ast.literal_eval(self.root.module.code_for_node(node)) for node in self.nodes()]


class Query(CollectionOfNodes):
    def __init__(self, mod: cst.CSTNode | str | Path) -> None:
        parsed_mod: cst.Module = parse_module(mod)
        self.wrapper: cst.metadata.MetadataWrapper = cst.metadata.MetadataWrapper(parsed_mod)
        self.module: cst.Module = self.wrapper.module

        self.__node_to_id: Mapping[cst.CSTNode, str] =  self.wrapper.resolve(NodeIDProvider)
        self.__id_to_node: dict[str, cst.CSTNode] =  {v: k for k, v in self.__node_to_id.items()}
        self.__extended_nodes: dict[cst.CSTNode, CSTQExtendedNode] = {}

        self.__parent_range = {
            self.__node_to_id[node]: range_id
            for range_node, range_id in self.__node_to_id.items()
            if isinstance(range_node, CSTQRange)
            for node in range_node.elems
        }

        CollectionOfNodes.__init__(self, [self.get_node_id(self.module)], self)

    def get_extended_node(self, node: cst.CSTNode) -> CSTQExtendedNode:
        if node not in self.__extended_nodes:
            self.__extended_nodes[node] = CSTQExtendedNode.from_node(node, self)
        return self.__extended_nodes[node]

    def get_node_id(self, node: cst.CSTNode) -> str:
        return self.__node_to_id[node]

    def get_nodes_id(self, nodes: list[cst.CSTNode]) -> dict[cst.CSTNode, str]:
        return {node: self.get_node_id(node) for node in nodes}

    def get_node_by_id(self, node_id: str) -> cst.CSTNode:
        return self.__id_to_node[node_id]

    def get_nodes_by_id(self, ids: Sequence[str]) -> dict[str, cst.CSTNode]:
        return {id_: self.get_node_by_id(id_) for id_ in ids}

    def replace_nodes(self, replace_map: dict[str, cst.CSTNode | cst.RemovalSentinel]):
        self.transform(ReplaceNodeTransformer(replace_map))
        return [None if to_node == cst.RemovalSentinel.REMOVE else from_id for from_id, to_node in replace_map.items()]

    def transform(self, transformer):
        mod = self.wrapper.visit(transformer)
        self.__init__(mod)  # type: ignore
        return mod

    def get_parent_of_node(self, node: cst.CSTNode) -> cst.CSTNode:
        return self.wrapper.resolve(cst.metadata.ParentNodeProvider)[node]

    def get_range_parent_id_by_id(self, node_id: str) -> cst.CSTNode:
        """
        This method return the node id of the CSTRange that contains the node, for instance while for the code

            def func(arg1, arg2): ...
        
        the cst node is something like

            FunctionDef(
                name=Name(value='func'),
                params=Parameters(
                    params=(
                        Param(Name(value='arg1')),
                        Param(Name(value='arg2')),
                    )
                )    
                ...
            ),
        
        the parent of `Param(Name(value='arg1'))` is `Parameters`, the range parent id `Parameters.params`
        """

        return  self.__parent_range[node_id]
    

    def code(self) -> str:
        return self.module.code

    def write(self, path: Path) -> int:
        return path.write_text(self.code())

    def collection(self, node_ids: list[str]) -> CollectionOfNodes:
        return CollectionOfNodes(node_ids, self.root)

    def collection_for_nodes(self, nodes: list[cst.CSTNode]):
        return self.create_collection(
            [self.get_node_id(node) for node in nodes],
            self.root,
        )


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
