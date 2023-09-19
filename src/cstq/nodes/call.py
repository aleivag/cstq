from collections.abc import MutableMapping, MutableSequence

import libcst as cst

from cstq.nodes.extended import CSTQExtendedNode

class Positional(MutableSequence):
    def __init__(self, node: CSTQExtendedNode):
        self.node = node

    @property
    def __sequence(self):
        return tuple(arg for arg in self.node.args if not arg.keyword)

    def __getitem__(self, item):
        return self.__sequence[item].value

    def __setitem__(self, key, value):
        self.__sequence[key].value.replace(value)
    def __delitem__(self, key):
        self.__sequence[key].remove()
    def __len__(self):
        return len(self.__sequence)

    def insert(self, index: int, value: cst.CSTNode) -> None:
        seq = list(self.__sequence)
        seq.insert(index, cst.Arg(value=value))
        new_args = [
                *seq,
                *(arg for arg in self.node.args if arg.keyword)
            ]
        # raise Exception(f"""{[
        #                          *seq,
        #                          *(arg for arg in self.node.args if arg.keyword)
        #                      ]}""")
        self.node.change(
            args=[getattr(n, "node", lambda :n)() for n in new_args]
        )

class Keywords(MutableMapping):
    def __init__(self, node: CSTQExtendedNode):
        self.node = node

    @property
    def __dict(self) -> dict[str, CSTQExtendedNode]:
        return {arg.keyword.value: arg for arg in self.node.args if arg.keyword}

    def __getitem__(self, key) -> CSTQExtendedNode:
        return self.__dict[key].value

    def __setitem__(self, key, value) -> None:
        or_val = self.__dict.get(key)
        if or_val:
            or_val.value.replace(value)
        else:
            self.node.change(
                args=[
                    *self.node.node().args,
                    cst.Arg(
                        value=value,
                        keyword=cst.Name(value=key),
                    ),
                ]
            )

    def __delitem__(self, key) -> None:
        self.__dict[key].remove()

    def __len__(self) -> int:
        return len(self.__dict)

    def __iter__(self) -> dict[str, CSTQExtendedNode]:
        return {k: v.value for k, v in self.__dict.items()}.__iter__()


@CSTQExtendedNode.register_type
class Call(cst.Call):
    """
    Wrapper around cst.Call that helps the retrieval of kwargs and pos args
    """

    @property
    def positional_args(self):
        return Positional(self)


    @property
    def keyword_args(self):
        return Keywords(self)
