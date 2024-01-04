from cstq import Query

TEXT = """

FOO = ["one", "two"]
BAR = 42

"""


def test_find_all_assignment():
    query = Query(TEXT)
    assigns = query.find_assignment()
    assert len(assigns) == 2
    assert [["one", "two"], 42] == [n.literal_eval() for n in assigns.value.extended_nodes()]


def test_find_assignment_by_name():
    query = Query(TEXT)
    assigns = query.find_assignment(variable_name="BAR")

    assert 42 == assigns.value.extended_node().literal_eval()
