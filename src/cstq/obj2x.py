from functools import singledispatch


def obj2x(cst):
    @singledispatch
    def obj2cst(obj):
        """
        takes a simple obj consisting of only Python literal structures: strings, bytes, numbers, tuples, lists, dicts,
        sets, booleans, None and Ellipsis, and return a simple and naive cst tree for it, with almost no formatting done.
        """
        if obj is None:
            return cst.Name(value="None")
        msg = f"{type(obj)=} is not supported for cst conversion"
        raise NotImplementedError(msg)

    @obj2cst.register(list)
    @obj2cst.register(set)
    @obj2cst.register(tuple)
    def _(obj):
        cst_type = {list: cst.List, set: cst.Set, tuple: cst.Tuple}[type(obj)]
        return cst_type(elements=[cst.Element(value=obj2cst(element)) for element in obj])

    @obj2cst.register(dict)
    def _(obj):
        return cst.Dict(
            elements=[cst.DictElement(key=obj2cst(key), value=obj2cst(value)) for key, value in obj.items()]
        )

    @obj2cst.register(str)
    @obj2cst.register(bytes)
    def _(obj):
        # I would really love to use https://github.com/psf/black/blob/main/src/black/strings.py#L173
        # black.strings.normalize_string_quotes, but don't want to pull so many dependencies
        # so I can just have my string "double quoted".
        return cst.SimpleString(value=repr(obj))

    @obj2cst.register(int)
    def _(obj):
        return cst.Integer(value=str(obj))

    @obj2cst.register(float)
    def _(obj):
        return cst.Float(value=str(obj))

    @obj2cst.register(complex)
    def _(obj):
        return cst.Imaginary(value=str(obj))

    @obj2cst.register(type(...))
    def _(obj):
        return cst.Ellipsis()

    @obj2cst.register(bool)
    def _(obj):
        return cst.Name(value=str(obj))

    return obj2cst
