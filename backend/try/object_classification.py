import inspect

def object_classification(object):
    if inspect.ismodule(object):
        print("{} is a module".format(object))
    if inspect.isclass(object):
        print("{} is a class".format(object))
    if inspect.ismethod(object):
        print("{} is a method".format(object))
    if inspect.isfunction(object):
        print("{} is a function".format(object))

    if inspect.isgeneratorfunction(object):
        print("{} is a generator function".format(object))
    if inspect.isgenerator(object):
        print("{} is a generator".format(object))
    if inspect.iscoroutinefunction(object):
        print("{} is a coroutine function".format(object))
    if inspect.iscoroutine(object):
        print("{} is a coroutine".format(object))
    if inspect.isawaitable(object):
        print("{} is awaitable".format(object))
    if inspect.isasyncgenfunction(object):
        print("{} is an async generator function".format(object))
    if inspect.isasyncgen(object):
        print("{} is an async generator".format(object))
    if inspect.istraceback(object):
        print("{} is a traceback".format(object))
    if inspect.isframe(object):
        print("{} is a frame".format(object))
    if inspect.iscode(object):
        print("{} is a code".format(object))
    if inspect.isbuiltin(object):
        print("{} is a builtin".format(object))
    if inspect.ismethodwrapper(object):
        print("{} is a method wrapper".format(object))
    if inspect.isroutine(object):
        print("{} is a routine".format(object))
    if inspect.isabstract(object):
        print("{} is abstract".format(object))
    if inspect.ismethoddescriptor(object):
        print("{} is a method descriptor".format(object))
    if inspect.isdatadescriptor(object):
        print("{} is a data descriptor".format(object))
    if inspect.isgetsetdescriptor(object):
        print("{} is a getset descriptor".format(object))
    if inspect.ismemberdescriptor(object):
        print("{} is a member descriptor".format(object))

# Example usage:
import time
import datetime
import requests

class TestClass:
    def __init__(self):
        pass
    def test_method(self):
        pass
    @classmethod
    def test_class_method(cls):
        pass

object_classification(range)

