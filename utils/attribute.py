
class SettableProperty(property):

    __setattr__ = property.fset


class Attribute(object):
    """ A decorator that is used for lazy evaluation of an object attribute.
    property should represent immutable data, as it replaces itself.

    .. NOTE: I AM NOT THE ORIGINAL AUTHOR, THIS IS FROM JACK MANEY'S REPO

    https://github.com/jackmaney/lazy-property/blob/master/lazy_property/__init__.py
    """

    __slots__ = ['method', '__name__']

    def __init__(self, method):
        self.method = method
        self.__name__ = method.__name__

    # def __init__(self, method, fget=None, fset=None, fdel=None, doc=None):
    #     self.method = method
    #     self.cache_name = "_{}".format(self.method.__name__)
    #
    #     doc = doc or method.__doc__
    #     super(self.__class__, self).__init__(fget=fget, fset=fset, fdel=fdel, doc=doc)
    #
    #     update_wrapper(self, method)
#
    def __get__(self, instance, owner):
        if instance is None:
            return self
        value = self.method(instance)
        setattr(instance, self.__name__, value)
        return value

    # def __get__(self, instance, owner=None):
    #
    #     if instance is None:
    #         return self
    #
    #     if hasattr(instance, self.cache_name):
    #         result = getattr(instance, self.cache_name)
    #     else:
    #         if self.fget is not None:
    #             result = self.fget(instance)
    #         else:
    #             result = self.method(instance)
    #
    #         setattr(instance, self.cache_name, result)
    #
    #     return result
    #
    # def __set__(self, instance, value):
    #
    #     if instance is None:
    #         raise AttributeError
    #
    #     if self.fset is None:
    #         setattr(instance, self.cache_name, value)
    #     else:
    #         self.fset(instance, value)