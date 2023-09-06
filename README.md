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


```python
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


```python
>>> q
<CollectionOfNodes nodes=['$(Module)']>

>>> q.body
<CollectionOfNodes nodes=['$(Module).body']>

>>> q.body[:]
<CollectionOfNodes nodes=['$(Module).body[0](SimpleStatementLine)', '$(Module).body[1](FunctionDef)', '$(Module).body[2](If)']>

>>> q.body[0].body[:]
<CollectionOfNodes nodes=['$(Module).body[0](SimpleStatementLine).body[0](Import)']>

```
and then get the node (and the code) back as

```python
>>> q.body[0].body[0].node()
Import(
    names=[
        ImportAlias(
            name=Name(
                value='sys',
                lpar=[],
                rpar=[],
            ),
            asname=None,
            comma=MaybeSentinel.DEFAULT,
        ),
    ],
    semicolon=MaybeSentinel.DEFAULT,
    whitespace_after_import=SimpleWhitespace(
        value=' ',
    ),
)


>>> q.body[0].body[0].code_for_node()
'import sys'

>>> q.body[0].body[:].names[0].name.node() 
Name(
    value='sys',
    lpar=[],
    rpar=[],
)
```
### 2. Filtering

Filtering allows you to "filter" the current selection of nodes to specific ones. Each one of these accepts either a 
[`libcst.matchers`](https://libcst.readthedocs.io/en/latest/matchers_tutorial.html) or a callback. `libcst.matchers` 
presents a very powerful query language, and when that's not enough, you can always fall back to a custom callback.


```python

>>> import libcst.matchers as m

# main root nodes
>>> q.body[:]
<CollectionOfNodes nodes=['$(Module).body[0](SimpleStatementLine)', '$(Module).body[1](FunctionDef)', '$(Module).body[2](If)']>

# filter out function definitions using explicit filter
>>> q.body[:].filter(m.FunctionDef())
<CollectionOfNodes nodes=['$(Module).body[1](FunctionDef)']>

# filter out function definitions using implicit filter
>>> q.body[m.FunctionDef()]
<CollectionOfNodes nodes=['$(Module).body[1](FunctionDef)']>

```

By using the `.filter` method, you can filter any selection. For instance, `q.body[:]` represents the elements of the body of 
the module. However, you can also filter out by using the `getitem` operation, making it a bit more compact.

### 3. Searching

If you want to search, not only in the current selection but also at every level, you can use `.search`. Similar 
to `.filter`, it accepts a `libcst.matchers` or a callback.

```python
>>> q.search(m.Import())
<CollectionOfNodes nodes=['$(Module).body[0](SimpleStatementLine).body[0](Import)', '$(Module).body[1](FunctionDef).body(IndentedBlock).body[0](SimpleStatementLine).body[0](Import)']>

# get the __name__ == "__main__" using search and filter
>>> q.search(m.If()).filter(lambda n: q.module.code_for_node(n.test) == '__name__ == "__main__"')
<CollectionOfNodes nodes=['$(Module).body[2](If)']>

# combining multiple search and filters into a single statement 
>>> q.search(m.If(), lambda n: q.module.code_for_node(n.test) == '__name__ == "__main__"')
<CollectionOfNodes nodes=['$(Module).body[2](If)']>
```

### codemod (changes)

If you want to change nodes, it's not hard to do, for instance removing the first import would be as easy as finding it
(using any combination of `.search` and/or `.filter`) and then call `.remove()`

```python
>>> q.body[0].body[0].remove()
<CollectionOfNodes nodes=[]>

# print the code on top
>>> print(q.code())


def main() -> None:
    import os
    print('hello world' if os.environ.get("USER") else "who are you?")

if __name__ == "__main__":
    main()
```

As you can see, there are several empty lines at the top. This is because of 2 things, first the module object is 
defined to have 1 empty line as a header, and the funtion def has the leading_lines attribute set to also have a empty line

```python
>>> q.header[:].node()
EmptyLine(
    indent=True,
    whitespace=SimpleWhitespace(
        value='',
    ),
    comment=None,
    newline=Newline(
        value=None,
    ),
)

>>> q.body[0]
<CollectionOfNodes nodes=['$(Module).body[0](FunctionDef)']>

>>>  q.body[0].leading_lines[:].node()
EmptyLine(
    indent=True,
    whitespace=SimpleWhitespace(
        value='',
    ),
    comment=None,
    newline=Newline(
        value=None,
    ),
)
```


Let's address this by simply changing the attribute `leading_lines` in that function definition using the method `.change`

```python

>>> q.body[0].change(leading_lines=[])
<CollectionOfNodes nodes=['$(Module).body[0](FunctionDef)']>

>>> print(q.code())

def main() -> None:
    import os
    print('hello world' if os.environ.get("USER") else "who are you?")

if __name__ == "__main__":
    main()

```

you can replace a node with another one


```python
# creates a node from text
>>> import_from = Query("from python_wrapper import os").search(m.ImportFrom()).node()

>>> q.search(m.Import()).replace(import_from)

>>> print(q.code())

def main() -> None:
    from python_wrapper import os
    print('hello world' if os.environ.get("USER") else "who are you?")

if __name__ == "__main__":
    main()

```


```python

# Let's add the import at the top level
>>> q.change(lambda n:n.with_changes(body=[cst.SimpleStatementLine(body=[import_from]), *n.body]))
<CollectionOfNodes nodes=['$(Module)']>

# Let's remove the inner import
>>> q.search(m.FunctionDef()).search(m.ImportFrom()).remove()
<CollectionOfNodes nodes=[]>

# Let's print the result
>>> print(q.code())

from python_wrapper import os
def main() -> None:
    print('hello world' if os.environ.get("USER") else "who are you?")

if __name__ == "__main__":
    main()


```

## License

`cstq` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
