from cstq import Query, obj2cst
import pytest
import libcst.matchers as m


def test_get():
    l = Query("(1, 2, 3, 4)").search(m.Tuple()).extended_node()
    assert l[1].literal_eval() == 2


def test_set():
    q = Query("(1, 2, 3, 4)")
    l = q.search(m.Tuple()).extended_node()
    l[1] = obj2cst("42")
    assert l[1].literal_eval() == "42"


def test_del():
    q = Query("(1, 2, 3, 4)")
    l = q.search(m.Tuple()).extended_node()
    del l[-1]
    # assert l.pop().literal_eval() == 4
    assert l[-1].literal_eval() == 3


def test_pop():
    q = Query("(1, 2, 3, 4)")
    l = q.search(m.Tuple()).extended_node()
    with pytest.raises(RuntimeError):
        l.pop().literal_eval()



def test_remove():
    q = Query("(1, 2, 3, 4)")
    l = q.search(m.Tuple()).extended_node()
    l.remove_at(-1)
    l.remove_at(0)
    assert q.root.code() == "(2, 3, )"


def test_insert():
    q = Query("(1, 2, 3, 4)")
    l = q.search(m.Tuple()).extended_node()
    l.insert(1, obj2cst(42))
    assert q.root.code() == "(1, 42, 2, 3, 4)"


def test_iter():
    q = Query("(1, 2, 3, 4)")
    l = q.search(m.Tuple()).extended_node()
    assert [e.literal_eval() for e in l] == [1, 2, 3, 4]


