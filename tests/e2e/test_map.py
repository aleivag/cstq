from cstq import Query
Q = """

foo(
    name = "Bar"
)

foo(
    name = "Baz"
)

"""


def test_map():
    assert Query(Q).find_function_call("foo").map(lambda node: node.keyword_args["name"].literal_eval()) == ["Bar", "Baz"]