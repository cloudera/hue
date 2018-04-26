def test_evens():
    yield check_even_cls

class Test(object):
    def test_evens(self):
        yield check_even_cls

class Check(object):
    def __call__(self):
        pass

check_even_cls = Check()
