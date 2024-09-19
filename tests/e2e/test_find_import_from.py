from cstq import Query


def test_find_a_import_from():
    mod = ["a", "b", "c"]
    q = Query("from a.b.c import d")
    import_node_code = q.find_import_from(module=mod).code_for_node()
    assert import_node_code == "from a.b.c import d"
    assert mod == ["a", "b", "c"], "mod was mutated inside the function, that's bad"


def test_cant_find_a_simple_module():
    mod = ["a", "z", "z"]
    q = Query("import a.b.c as d")
    assert len(q.find_import_from(module=mod)) == 0


def test_find_import_with_alias():
    q = Query(
        """
from a.b.c import x
from a.b.c import y
from a.b.c import z
"""
    )
    assert q.find_import_from(module="a.b.c".split("."), name="z").code_for_node() == "from a.b.c import z"


def test_find_all_import_from():
    q = Query(
        "\n".join(
            code := [
                "from a.b.c import x",
                "from a.b.c import y",
                "from a.b.c import z",
            ]
        )
    )
    assert q.find_import_from().code_for_nodes() == code
