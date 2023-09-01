from cstq import Query

MODULE = """
# this is a random module
one = 1
two = one + one
""".strip()


def test_get_node_by_id():
    """
    This test is here to prove that we can get the main module by id.
    and that getting a node by id, and then asking the id of the node are idemponent actions
    """
    q = Query(MODULE)
    module_id = "$(Module)"
    module = q.get_node_by_id(module_id)
    assert module == q.module
    assert q.get_node_id(q.get_node_by_id(module_id)) == module_id


def test_get_nodes_by_id():
    """
    This test is here to prove that we can get the main module by id.
    and that getting a node by id, and then asking the id of the node are idemponent actions
    """
    q = Query(MODULE)
    module = q.module

    simple_statement_line = q.get_nodes_by_id(
        ["$(Module).body[0](SimpleStatementLine)", "$(Module).body[1](SimpleStatementLine)"]
    )

    assert simple_statement_line == {
        "$(Module).body[0](SimpleStatementLine)": module.body[0],
        "$(Module).body[1](SimpleStatementLine)": module.body[1],
    }


def test_get_nodes_id():
    q = Query(MODULE)
    module = q.module

    simple_statement_line = q.get_nodes_id([module.body[0], module.body[1]])

    assert simple_statement_line == {
        module.body[0]: "$(Module).body[0](SimpleStatementLine)",
        module.body[1]: "$(Module).body[1](SimpleStatementLine)",
    }


def test_get_parent():
    "makes sure that get_parent returns the node parent"
    q = Query(MODULE)
    module = q.module
    assert q.get_parent_of_node(module.body[1]) == module
