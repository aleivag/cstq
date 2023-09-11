# cstq

[![PyPI - Version](https://img.shields.io/pypi/v/cstq.svg)](https://pypi.org/project/cstq)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/cstq.svg)](https://pypi.org/project/cstq)

-----

A very simple and, at least according to the author, intuitive library to navigate Python source code, and code modeling.

## Enough said, I need some action!

In code as in screenwriting, it's better to show rather than tell. So, here are a couple of examples that scratch the surface of 
this library. 

### Installation

First things first, let's install the library

```console
pip install cstq
```

### Example base code 

To start working with cstq, you can pass the path to a Python file or pass the module directly by:


```dumas[python]
from cstq import Query

q = Query("""
import sys

def main() -> None:
    import os
    print('hello world' if os.environ.get("USER") else "who are you?")

if __name__ == "__main__":
    main()
""")
```

Now lets get down to business

## Basic Navigation

There are 3 types of basic navigation:

### 1. Direct Attribute Access

You can navigate by referencing attributes directly.


```dumas[python]
q
```
```dumas[python]
q.body
```
```dumas[python]
q.body[:]
```
```dumas[python]
q.body[0].body[:]
```
and then get the node (and the code) back as

```dumas[python]
q.body[0].body[0].node()
```

```dumas[python]
q.body[0].body[0].code_for_node()
```

```dumas[python]
q.body[0].body[:].names[0].name.node()
```
### 2. Filtering

Filtering allows you to "filter" the current selection of nodes to specific ones. Each one of these accepts either a 
[`libcst.matchers`](https://libcst.readthedocs.io/en/latest/matchers_tutorial.html) or a callback (more on callbacks later). 
`libcst.matchers` presents a very powerful query language, and when that's not enough, you can always fall back to a custom callback.


```dumas[python]
import libcst.matchers as m

```

```dumas[python]
# main root nodes
q.body[:]

```

```dumas[python]
# filter out function definitions using explicit filter
q.body[:].filter(m.FunctionDef())
```

```dumas[python]
# filter out function definitions using implicit filter
q.body[m.FunctionDef()]
```

By using the `.filter` method, you can filter any selection. For instance, `q.body[:]` represents the elements of the body of 
the module. However, you can also filter out by using the `__getitem__` operation (`[.. add your filter here ...]`), 
making it a bit more compact.

### 3. Searching

If you want to search, not only in the current selection but also at every level, you can use `.search`. Similar 
to `.filter`, it accepts a `libcst.matchers` or a callback.

```dumas[python]
q.search(m.Import())
```

```dumas[python]

# get the __name__ == "__main__" using search and filter
q.search(m.If()).filter(lambda n: n.test.code() == '__name__ == "__main__"')
```

```dumas[python]
# combining multiple search and filters into a single statement 
q.search(m.If(), lambda n: n.test.code() == '__name__ == "__main__"')
```

### using callbacks

`.filter` and `.search` can take a callback method that takes an _extended version_ of a CSTNode and returns true or false.
The extended version of the CSTNode its the regular CSTNode with a couple of extra methods like `.parent()` to give your the parent,
and `.code()` to generate the code that node represents, soo far I haven't added anything else.

### codemod (changes)

If you want to change nodes, it's not hard to do, for instance removing the first import would be as easy as finding it
(using any combination of `.search` and/or `.filter`) and then call `.remove()`

```dumas[python]
q.body[0].body[0].remove()
```

```dumas[python]

# print the code on top
print(q.code())

```

As you can see, there are several empty lines at the top. This is because of 2 things, first the module object is 
defined to have 1 empty line as a header, and the funtion def has the leading_lines attribute set to also have a empty line

```dumas[python]
q.header[:].node()
```

```dumas[python]
q.body[0]
```

```dumas[python]
q.body[0].leading_lines[:].node()
```


Let's address this by simply changing the attribute `leading_lines` in that function definition using the method `.change`

```dumas[python]
q.body[0].change(leading_lines=[])


```

```dumas[python]
print(q.code())
```

you can replace a node with another one


```dumas[python]
# Lets create an "import from" node and using the serach and node function,
# and then lets use that node to replace the "import" on our module.

import_from = Query("from python_wrapper import os").search(m.ImportFrom()).node()
q.search(m.Import()).replace(import_from)

q.code()
```


```dumas[python]
# Let's add the import at the top level

import libcst as cst
q.change(lambda n: n.with_changes(body=[cst.SimpleStatementLine(body=[import_from]), *n.body]))

```
```dumas[python]
# Let's remove the inner import
q.search(m.FunctionDef()).search(m.ImportFrom()).remove()
```
```dumas[python]
# Let's print the result
q.code()
```

## License

`cstq` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.