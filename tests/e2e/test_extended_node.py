import libcst.matchers as m


def test_get_parent(CSTQuery):
    q = CSTQuery("""import os""")
    enode = q.search(m.Import()).extended_node()
    assert enode.parent().parent().node().deep_equals(q.module)
