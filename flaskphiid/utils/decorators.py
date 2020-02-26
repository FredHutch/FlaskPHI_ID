import inspect

def checkargs(function):
    def _f(*arguments):
        for index, argument in enumerate(inspect.getfullargspec(function)[0]):
            if not isinstance(arguments[index], function.__annotations__[argument]):
                raise TypeError("{} is not of type {}".format(arguments[index], function.__annotations__[argument]))
        return function(*arguments)
    _f.__doc__ = function.__doc__
    return _f


def validateargs(function):
    def _f(*arguments):
        for index, argument in enumerate(inspect.getfullargspec(function)[0]):
            if argument in function.__annotations__ and not (function.__annotations__[argument](arguments[index])):
                raise TypeError("{} could not be validated by {}".format(arguments[index],
                                                                         function.__annotations__[argument].__name__))
        return function(*arguments)
    _f.__doc__ = function.__doc__
    return _f


def coerceargs(function):
    def _f(*arguments):
        new_arguments = []
        for index, argument in enumerate(inspect.getfullargspec(function)[0]):
            new_arguments.append(function.__annotations__[argument](arguments[index]))
        return function(*new_arguments)
    _f.__doc__ = function.__doc__
    return _f


def validate(func, locals):
    for var, test in func.__annotations__.items():
        value = locals[var]
        msg = 'Var: {0}\tValue: {1}\tTest: {2.__name__}'.format(var, value, test)
        assert test(value), msg


def in_dict(dictionary):
    def _in_dict(key):
        return key in dictionary
    return _in_dict


def is_int(x):
    return isinstance(x, int)


def is_string(x):
    return isinstance(x, str)


def between(lo, hi):
    def _between(x):
            return lo <= x <= hi
    return _between


def f(x: between(3, 10), y: is_int):
    validate(f, locals())
    print(x, y)


if __name__ == "__main__":
    @checkargs
    def f(x: int, y: int):
        """
        A doc string!
        """
        return x, y

    @coerceargs
    def g(a: int, b: int):
        """
        Another doc string!
        """
        return a + b

    @validateargs
    def h(a: in_dict({'a': 1}), b):
        return a

    print(f(1, 2))
    try:
        print(f(3, 4.0))
    except TypeError as e:
        print(e)

    print(g(1, 2))
    print(g(3, 4.0))
    print(h('a', 2))
    print(h('b', 2))