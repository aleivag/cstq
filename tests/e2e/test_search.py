import libcst.matchers as m

from cstq import Query


def test_multiple_search():
    "makes sure you can pass multiple methods to search"
    node = Query(
        """
def foo():
    def bar():
        ...
    return bar()

def bar():
   ...
    """
    ).search(m.FunctionDef(), lambda n: n.name.value == "foo")

    assert (
        node.code_for_node()
        == """def foo():
    def bar():
        ...
    return bar()
"""
    )
