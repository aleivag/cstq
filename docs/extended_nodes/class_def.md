# Class definition (ClassDef)

This node extend the ClassDef cst node, that represents a class definition. its the node you woulg get if:

```python

In [1]: from cstq import Query
   ...: 
   ...: q = Query(
   ...:     """
   ...: class Foo(BaseFoo):
   ...:    def bar(self) -> "Bar":
   ...:     return Bar(2)
   ...: """
   ...: )
   ...: 
   ...: collection = q.find_class_def("Foo")
```

The extended node would be

```python

In [2]: node = collection.extended_node()
   ...: node


Out[2]: CSTQClassDef(
    root=<CollectionOfNodes nodes=['$(Module)']>,
    node_id='$(Module).body[0](ClassDef)',
)
```

# Special methods

## Class Bases

A very common operation is to find classes by what class they inherit, and then either replace it,
add one, remove one, this can be done using libcst nodes, or just string. if you want to know the bases, the regulat cst attribute can be used

```python

In [3]: node.bases


Out[3]: (Arg(
    root=<CollectionOfNodes nodes=['$(Module)']>,
    node_id='$(Module).body[0](ClassDef).bases[0](Arg)',
),)
```

but most of the time you actually care about "the name", so you can just get the `str_bases` and:

```python

In [4]: node.str_bases


Out[4]: <cstq.nodes.class_def.Bases object at 0x1108067e0>
```

this method is nice, because lets assume that you wannt to change the base

```python

In [5]: node.str_bases[0] = "NewBaseFoo"
   ...: node.code()


Out[5]: class Foo(NewBaseFoo):
   def bar(self) -> "Bar":
    return Bar(2)
```

then you can also add or remove as you please

```python

In [6]: node.str_bases.insert(0, "BaseFoo")  # inserts BaseFoo at the begining
   ...: node.str_bases.pop()  # remove the last element
   ...: node.str_bases.append(
   ...:     "new_bases.NewBaseFoo"
   ...: )  # add a new element thats a dotted attribute
   ...: node.code()


Out[6]: class Foo(BaseFoo, new_bases.NewBaseFoo):
   def bar(self) -> "Bar":
    return Bar(2)
```

finally if you want to remove the bases, there is 2 things you can do, that has similar results, but are different conceptually. first you can assign an empty list to the `str_bases` attribute, this will result in a empty bases, but the parentesys will still be there

```python

In [7]: node.str_bases = []
   ...: node.code()


Out[7]: class Foo():
   def bar(self) -> "Bar":
    return Bar(2)
```

or you can delete the attributem, in that case, no more parentesis will be there 

```python

In [8]: del node.str_bases
   ...: node.code()


Out[8]: class Foo:
   def bar(self) -> "Bar":
    return Bar(2)
```

