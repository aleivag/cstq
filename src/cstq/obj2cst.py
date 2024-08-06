from functools import partial

import libcst

from .obj2x import obj2x, str2xattr

obj2cst = obj2x(libcst)
str2attr = partial(str2xattr, x=libcst)
