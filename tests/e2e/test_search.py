import libcst as cst
import libcst.matchers as m

from cstq import Query

MODULE = """
import foo
import bar
from a.module import a_function

def foo():
    def bar():
        ...
    return bar()

def bar():
    import baz
""".strip()


def test_multiple_search():
    "makes sure you can pass multiple methods to search"
    node = Query(MODULE).search(m.FunctionDef(), lambda n: n.name.value == "foo")

    assert (
        node.code_for_node().strip()
        == """
def foo():
    def bar():
        ...
    return bar()
""".strip()
    )


def test_get_all_first_level_imports():
    "makes sure you can pass multiple methods to search, and you get a extended node"

    node = Query(MODULE).search(m.Import() | m.ImportFrom(), lambda n: isinstance(n.parent().parent(), cst.Module))

    assert node.code_for_nodes() == ["import foo", "import bar", "from a.module import a_function"]


def test_get_all_imports():
    "makes sure you can pass multiple methods to search, and you get a extended node"

    node = Query(MODULE).search(m.Import() | m.ImportFrom())

    assert node.code_for_nodes() == ["import foo", "import bar", "from a.module import a_function", "import baz"]
