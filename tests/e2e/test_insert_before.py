import libcst as cst
import libcst.matchers as m

from cstq import Query



def test_insert_before_last_import_node():
    # This test inserts a "import os" at the top of the file
    q = Query("import re\nimport sys")
    import_os = Query("import os").body[0].node()
    q.body[1].insert_before(import_os)
    assert q.code().strip() == "import re\nimport os\nimport sys".strip()

def test_insert_before_first_import_node():
    q = Query("import re\nimport sys")
    import_os = Query("import os").body[0].node()
    q.body[0].insert_before(import_os)
    assert q.code().strip() == "import os\nimport re\nimport sys".strip()



def test_insert_before_arg():
    # This test inserts a "import os" at the top of the file
    q = Query("def foo(a, b, c):...")
    
    q.search(m.Name("b")).parent().insert_before(
        cst.Param(cst.Name("z"))
    )
    assert q.code().strip() == "def foo(a, z, b, c):...".strip()



def test_multi_index():
    # This test inserts a "import os" at the top of the file
    q = Query("""
def foo(a, b, c):...
def bar(a, b, c):...
def baz(a, b, c):...
""".strip())
    
    q.search(m.FunctionDef()).params.params[0].insert_before(
        cst.Param(cst.Name("z"))
    )
    assert q.code().strip() == """
def foo(z, a, b, c):...
def bar(z, a, b, c):...
def baz(z, a, b, c):...
""".strip()
