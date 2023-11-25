def foo(arg1,arg2):         
    #do something with args 
    a = arg1 + arg2         
    return a  

import inspect
lines = inspect.getsource(foo)
print(lines)