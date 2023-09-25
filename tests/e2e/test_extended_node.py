import libcst.matchers as m


def test_get_parent(CSTQuery):
    q = CSTQuery("""import os""")
    enode = q.search(m.Import()).extended_node()
    assert enode.parent().parent().node().deep_equals(q.module)


def test_expand_tuple(CSTQuery):
    # this should not cause an issue, if they do its because we are not extanding the
    # tuple
    CSTQuery("#hello\n\n\ndef foo():\n ...").body[0].extended_node().leading_lines[::-1]
    CSTQuery("#hello\n\n\ndef foo():\n ...").extended_node().header
