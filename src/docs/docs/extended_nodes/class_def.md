Class definition (ClassDef)
===========================

This node extend the ClassDef cst node, that represents a class definition. its the node you woulg get if:



```dumas[python]
from cstq import Query

q = Query("""
class Foo(BaseFoo):
   def bar(self) -> "Bar":
    return Bar(2)
""")

collection = q.find_class_def("Foo")
```

The extended node would be

```dumas[python]
node = collection.extended_node()
node
```

Special methods
===============

## Class Bases

A very common operation is to find classes by what class they inherit, and then either replace it,
add one, remove one, this can be done using libcst nodes, or just string. if you want to know the bases, the regulat cst attribute can be used

```dumas[python]
node.bases
```

but most of the time you actually care about "the name", so you can just get the `str_bases` and:

```dumas[python]
node.str_bases
```

this method is nice, because lets assume that you wannt to change the base

```dumas[python]
node.str_bases[0] = "NewBaseFoo"
node.code() 
```

then you can also add or remove as you please

```dumas[python]
node.str_bases.insert(0, "BaseFoo") # inserts BaseFoo at the begining
node.str_bases.pop() # remove the last element  
node.str_bases.append("new_bases.NewBaseFoo") # add a new element thats a dotted attribute
node.code() 
```

finally if you want to remove the bases, there is 2 things you can do, that has similar results, but are different conceptually. first you can assign an empty list to the `str_bases` attribute, this will result in a empty bases, but the parentesys will still be there

```dumas[python]
node.str_bases = []
node.code()
```

or you can delete the attributem, in that case, no more parentesis will be there 


```dumas[python]
del node.str_bases
node.code()
```

