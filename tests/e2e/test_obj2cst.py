import libcst.matchers as m

from cstq import Query, obj2cst


def test_int():
    q = Query("{}")
    obj = obj2cst(
        {
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
    )
    q.search(m.Dict()).replace(obj)
    assert (
        q.code()
        == "{'int': 42, 'float': 4.2, 'list': [4, 2], 'set': {2, 4}, 'tuple': (4, 2), 'complex': 42j, 'None': None, 'True': True, 'False': False}"
    )
