class C:
    def __init__(self):
        self.x = 1
        self.y = 2
        self.z = 3

    def method(self):
        print(self.x, self.y, self.z)

c = C()
code = c.method.__code__
exec(code, c.__dict__)