from cstq import Query


def test_find_a_simple_module():
    mod = ["a", "b", "c"]
    q = Query("import a.b.c as d")
    import_node_code = q.find_import_alias(module=mod).parent().code_for_node()
    assert import_node_code == "import a.b.c as d"
    assert mod == ["a", "b", "c"], "mod was mutated inside the function, that's bad"


def test_cant_find_a_simple_module():
    mod = ["a", "z", "z"]
    q = Query("import a.b.c as d")
    assert len(q.find_import_alias(module=mod)) == 0
