import libcst as cst
import libcst.matchers as m

from cstq import Query



def test_insert_after_last_import_node():
    # This test inserts a "import os" at the top of the file
    q = Query("import re\nimport sys")
    import_os = Query("import os").body[0].node()
    q.body[1].insert_after(import_os)
    assert q.code().strip() == "import re\nimport sys\nimport os".strip()

def test_insert_after_first_import_node():
    q = Query("import re\nimport sys")
    import_os = Query("import os").body[0].node()
    q.body[0].insert_after(import_os)
    assert q.code().strip() == "import re\nimport os\nimport sys".strip()



def test_insert_after_arg():
    # This test inserts a "import os" at the top of the file
    q = Query("def foo(a, b, c):...")
    
    q.search(m.Name("b")).parent().insert_after(
        cst.Param(cst.Name("z"))
    )
    assert q.code().strip() == "def foo(a, b, z, c):...".strip()



def test_multi_index():
    # This test inserts a "import os" at the top of the file
    q = Query("""
def foo(a, b, c):...
def bar(a, b, c):...
def baz(a, b, c):...
""".strip())
    
    # insert after the second param
    q.search(m.FunctionDef()).params.params[1].insert_after(
        cst.Param(cst.Name("z"))
    )
    assert q.code().strip() == """
def foo(a, b, z, c):...
def bar(a, b, z, c):...
def baz(a, b, z, c):...
""".strip()
