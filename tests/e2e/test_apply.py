from cstq import Query, obj2cst, str2attr

Q = """

foo(
    name = "Bar"
)

"""


def test_map():
    TRUE = obj2cst(True)
    bar_name = str2attr("bar")
    
    def n(node):
        node.change(func=bar_name)
        node.keyword_args["use_foo"] = TRUE
    
    q = Query(Q)
    new_node = q.find_function_call("foo").apply(n).extended_node()
    assert new_node.func_name == bar_name.value
    assert new_node.keyword_args["use_foo"].literal_eval()
    assert new_node.keyword_args["name"].literal_eval() == "Bar"
