import inspect

def test(*, k:int=1, m=2, **kwargs):
    pass

s = inspect.signature(test)

def test2(a: str, b, *, c:int =1, d=2, **kwargs):
    pass

print(inspect.signature(test2).return_annotation)
print(inspect.get_annotations(test2))


t = [1]
k = {'c': 33, 'd': 44, 'e': 55}
# print(s.bind_partial(**k).arguments)
# print(s.bind(*t, **k).arguments)

print(str(inspect.signature(test))[1:-1].split(', '))


from requests.api import request

print(request.__module__)
top = request.__module__.find('.')
print(request.__module__[:top])
print(request.__module__[top+1:])
a = inspect.getmodule(request)
# print(a)
# print(inspect.signature(test2).bind_partial(*t, **k).arguments)
# print(inspect.signature(test2).bind(*t, **k).arguments)