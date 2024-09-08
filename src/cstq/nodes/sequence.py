from collections.abc import MutableSequence

import libcst as cst


class Container(MutableSequence):
    def __getitem__(self, item):
        return self.elements[item].value

    def __setitem__(self, key, value):
        self[key].replace(value)

    def __delitem__(self, key):
        # remove the Element object
        self.elements[key].remove()

    def __len__(self):
        return len(self.elements)

    def pop(self, _=-1):
        raise RuntimeError(
            "Cannot pop element from List node. Once an element is removed from the list, it no longer belongs to the document and any operations performed on it would be lost."
        )

    def remove_at(self, idx):
        del self[idx]

    def insert(self, index: int, value: cst.CSTNode) -> None:
        seq = list(self.node().elements)
        if not isinstance(value, cst.Element):
            value = cst.Element(value=value)
        seq.insert(index, value)
        self.change(elements=seq)


class CSTQList(cst.List, Container):
    """
    Wrapper around cst.List that implements a few Sequence methods
    """


class CSTQTuple(cst.Tuple, Container):
    """
    Wrapper around cst.Tuple that implements a few Sequence methods
    """
