from cstq import Query

def test_find_a_import_from():
    mod = ["a", "b", "c"]
    q = Query("from a.b.c import d")
    import_node_code =  q.find_import_from(
        module=mod
    ).code_for_node()
    assert import_node_code == "from a.b.c import d"
    assert mod == ["a", "b", "c"], "mod was mutated inside the function, that's bad"

def test_cant_find_a_simple_module():
    mod = ["a", "z", "z"]
    q = Query("import a.b.c as d")
    assert len( q.find_import_from(
        module=mod
    )) == 0