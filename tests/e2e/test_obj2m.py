import libcst.matchers as m

from cstq import Query, obj2cst, obj2m 
from cstq.matchers import match


def test_int():
    # brite force testing ob obj2m
    q = Query("{}")
    obj = {
            "int": 42,
            "float": 4.2,
            "list": [4, 2],
            "set": {4, 2},
            "tuple": (4, 2),
            "complex": 42j,
            "None": None,
            "True": True,
            "False": False,
    }
    q.search(m.Dict()).replace(obj2cst(obj))
    assert match(q.search(m.Dict()).node(), obj2m(obj), q.root)
