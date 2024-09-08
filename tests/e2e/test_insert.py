import libcst.matchers as m

from cstq import Query

MODULE = """
import sys

def foo():
    ...

if __name__ == "__main__":
    DEBUG = True
    print("starting")
    foo()
    print("ending")
""".strip()


def test_insert_import_node():
    # This test inserts a "import os" at the top of the file
    q = Query(MODULE)
    import_os = Query("import os").body[0].node()
    q.body.insert(0, import_os)
    assert q.code().strip() == f"import os\n{MODULE}".strip()


def test_insert_import_collection_of_node():
    # This test inserts a "import os" at the top of the file
    q = Query(MODULE)
    import_os = Query("import os").body[0]
    q.body.insert(0, import_os)
    assert q.code().strip() == f"import os\n{MODULE}".strip()


def test_convert_id_main_into_main_call():
    q = Query(MODULE)
    if_node = q.search(m.If(), lambda n: n.test.code() == '__name__ == "__main__"').node()
    new_q = Query(
        """

def main() -> None:
    ...

if __name__ == "__main__":
    main()
    """
    )
    new_q.search(m.FunctionDef()).change(body=if_node.body)

    q.search(m.If(), lambda n: n.test.code() == '__name__ == "__main__"').remove()
    q.body.extend(new_q.body[:])

    assert (
        q.code().strip()
        == """
import sys

def foo():
    ...
def main() -> None:
    DEBUG = True
    print("starting")
    foo()
    print("ending")

if __name__ == "__main__":
    main()
""".strip()
    )


def test_empty_body():
    q = Query("")
    q.body.insert(0, Query("import foo").body[0])
    assert q.root.code() == "import foo"
