CSTQExtendedNode
================

This is the node your get when you are filtering, searching, and in general exploring the cst


# Literal eval

Python standard library comes with a very simple function in the ast module called 
[literal_eval](https://docs.python.org/3/library/ast.html#ast.literal_eval), this allows to... well  
eval a literal value into a python object _without_ executing its contents. I recommend read the docs for that function 
as you need to be carefully on what to use it on. But safety aside, its usefull to convert libcst's SimpleString, Integer, List
and other into a python object.


```dumas[python]
from cstq import Query

q = Query("""
X = {
    "a string": "one element",
    "a int": 42,
    "a set": {"a", "set"},
    "a tuple": ("a", "tuple"),
    "an array": ["an", "array"], 
}

""")

q.body
```

```dumas[python]
import libcst.matchers as m
the_dict = q.search(m.Dict()).literal_eval_for_node()
```

```dumas[python]
the_dict
```

```dumas[python]
the_dict["a int"]
```