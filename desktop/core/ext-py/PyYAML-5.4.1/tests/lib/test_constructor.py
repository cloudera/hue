
import yaml
import pprint

import datetime
try:
    set
except NameError:
    from sets import Set as set
import yaml.tokens

def execute(code):
    exec code
    return value

def _make_objects():
    global MyLoader, MyDumper, MyTestClass1, MyTestClass2, MyTestClass3, YAMLObject1, YAMLObject2,  \
            AnObject, AnInstance, AState, ACustomState, InitArgs, InitArgsWithState,    \
            NewArgs, NewArgsWithState, Reduce, ReduceWithState, Slots, MyInt, MyList, MyDict,  \
            FixedOffset, today, execute, MyFullLoader

    class MyLoader(yaml.Loader):
        pass
    class MyDumper(yaml.Dumper):
        pass

    class MyTestClass1:
        def __init__(self, x, y=0, z=0):
            self.x = x
            self.y = y
            self.z = z
        def __eq__(self, other):
            if isinstance(other, MyTestClass1):
                return self.__class__, self.__dict__ == other.__class__, other.__dict__
            else:
                return False

    def construct1(constructor, node):
        mapping = constructor.construct_mapping(node)
        return MyTestClass1(**mapping)
    def represent1(representer, native):
        return representer.represent_mapping("!tag1", native.__dict__)

    def my_time_constructor(constructor, node):
        seq = constructor.construct_sequence(node)
        dt = seq[0]
        tz = None
        try:
            tz = dt.tzinfo.tzname(dt)
        except:
            pass
        return [dt, tz]

    yaml.add_constructor("!tag1", construct1, Loader=MyLoader)
    yaml.add_constructor("!MyTime", my_time_constructor, Loader=MyLoader)
    yaml.add_representer(MyTestClass1, represent1, Dumper=MyDumper)

    class MyTestClass2(MyTestClass1, yaml.YAMLObject):
        yaml_loader = MyLoader
        yaml_dumper = MyDumper
        yaml_tag = "!tag2"
        def from_yaml(cls, constructor, node):
            x = constructor.construct_yaml_int(node)
            return cls(x=x)
        from_yaml = classmethod(from_yaml)
        def to_yaml(cls, representer, native):
            return representer.represent_scalar(cls.yaml_tag, str(native.x))
        to_yaml = classmethod(to_yaml)

    class MyTestClass3(MyTestClass2):
        yaml_tag = "!tag3"
        def from_yaml(cls, constructor, node):
            mapping = constructor.construct_mapping(node)
            if '=' in mapping:
                x = mapping['=']
                del mapping['=']
                mapping['x'] = x
            return cls(**mapping)
        from_yaml = classmethod(from_yaml)
        def to_yaml(cls, representer, native):
            return representer.represent_mapping(cls.yaml_tag, native.__dict__)
        to_yaml = classmethod(to_yaml)

    class YAMLObject1(yaml.YAMLObject):
        yaml_loader = MyLoader
        yaml_dumper = MyDumper
        yaml_tag = '!foo'
        def __init__(self, my_parameter=None, my_another_parameter=None):
            self.my_parameter = my_parameter
            self.my_another_parameter = my_another_parameter
        def __eq__(self, other):
            if isinstance(other, YAMLObject1):
                return self.__class__, self.__dict__ == other.__class__, other.__dict__
            else:
                return False

    class YAMLObject2(yaml.YAMLObject):
        yaml_loader = MyLoader
        yaml_dumper = MyDumper
        yaml_tag = '!bar'
        def __init__(self, foo=1, bar=2, baz=3):
            self.foo = foo
            self.bar = bar
            self.baz = baz
        def __getstate__(self):
            return {1: self.foo, 2: self.bar, 3: self.baz}
        def __setstate__(self, state):
            self.foo = state[1]
            self.bar = state[2]
            self.baz = state[3]
        def __eq__(self, other):
            if isinstance(other, YAMLObject2):
                return self.__class__, self.__dict__ == other.__class__, other.__dict__
            else:
                return False

    class AnObject(object):
        def __new__(cls, foo=None, bar=None, baz=None):
            self = object.__new__(cls)
            self.foo = foo
            self.bar = bar
            self.baz = baz
            return self
        def __cmp__(self, other):
            return cmp((type(self), self.foo, self.bar, self.baz),
                    (type(other), other.foo, other.bar, other.baz))
        def __eq__(self, other):
            return type(self) is type(other) and    \
                    (self.foo, self.bar, self.baz) == (other.foo, other.bar, other.baz)

    class AnInstance:
        def __init__(self, foo=None, bar=None, baz=None):
            self.foo = foo
            self.bar = bar
            self.baz = baz
        def __cmp__(self, other):
            return cmp((type(self), self.foo, self.bar, self.baz),
                    (type(other), other.foo, other.bar, other.baz))
        def __eq__(self, other):
            return type(self) is type(other) and    \
                    (self.foo, self.bar, self.baz) == (other.foo, other.bar, other.baz)

    class AState(AnInstance):
        def __getstate__(self):
            return {
                '_foo': self.foo,
                '_bar': self.bar,
                '_baz': self.baz,
            }
        def __setstate__(self, state):
            self.foo = state['_foo']
            self.bar = state['_bar']
            self.baz = state['_baz']

    class ACustomState(AnInstance):
        def __getstate__(self):
            return (self.foo, self.bar, self.baz)
        def __setstate__(self, state):
            self.foo, self.bar, self.baz = state

    class InitArgs(AnInstance):
        def __getinitargs__(self):
            return (self.foo, self.bar, self.baz)
        def __getstate__(self):
            return {}

    class InitArgsWithState(AnInstance):
        def __getinitargs__(self):
            return (self.foo, self.bar)
        def __getstate__(self):
            return self.baz
        def __setstate__(self, state):
            self.baz = state

    class NewArgs(AnObject):
        def __getnewargs__(self):
            return (self.foo, self.bar, self.baz)
        def __getstate__(self):
            return {}

    class NewArgsWithState(AnObject):
        def __getnewargs__(self):
            return (self.foo, self.bar)
        def __getstate__(self):
            return self.baz
        def __setstate__(self, state):
            self.baz = state

    class Reduce(AnObject):
        def __reduce__(self):
            return self.__class__, (self.foo, self.bar, self.baz)

    class ReduceWithState(AnObject):
        def __reduce__(self):
            return self.__class__, (self.foo, self.bar), self.baz
        def __setstate__(self, state):
            self.baz = state

    class Slots(object):
        __slots__ = ("foo", "bar", "baz")
        def __init__(self, foo=None, bar=None, baz=None):
            self.foo = foo
            self.bar = bar
            self.baz = baz

        def __eq__(self, other):
            return type(self) is type(other) and \
                (self.foo, self.bar, self.baz) == (other.foo, other.bar, other.baz)

    class MyInt(int):
        def __eq__(self, other):
            return type(self) is type(other) and int(self) == int(other)

    class MyList(list):
        def __init__(self, n=1):
            self.extend([None]*n)
        def __eq__(self, other):
            return type(self) is type(other) and list(self) == list(other)

    class MyDict(dict):
        def __init__(self, n=1):
            for k in range(n):
                self[k] = None
        def __eq__(self, other):
            return type(self) is type(other) and dict(self) == dict(other)

    class FixedOffset(datetime.tzinfo):
        def __init__(self, offset, name):
            self.__offset = datetime.timedelta(minutes=offset)
            self.__name = name
        def utcoffset(self, dt):
            return self.__offset
        def tzname(self, dt):
            return self.__name
        def dst(self, dt):
            return datetime.timedelta(0)

    class MyFullLoader(yaml.FullLoader):
        def get_state_keys_blacklist(self):
            return super(MyFullLoader, self).get_state_keys_blacklist() + ['^mymethod$', '^wrong_.*$']

    today = datetime.date.today()

def _load_code(expression):
    return eval(expression)

def _serialize_value(data):
    if isinstance(data, list):
        return '[%s]' % ', '.join(map(_serialize_value, data))
    elif isinstance(data, dict):
        items = []
        for key, value in data.items():
            key = _serialize_value(key)
            value = _serialize_value(value)
            items.append("%s: %s" % (key, value))
        items.sort()
        return '{%s}' % ', '.join(items)
    elif isinstance(data, datetime.datetime):
        return repr(data.utctimetuple())
    elif isinstance(data, unicode):
        return data.encode('utf-8')
    elif isinstance(data, float) and data != data:
        return '?'
    else:
        return str(data)

def test_constructor_types(data_filename, code_filename, verbose=False):
    _make_objects()
    native1 = None
    native2 = None
    try:
        native1 = list(yaml.load_all(open(data_filename, 'rb'), Loader=MyLoader))
        if len(native1) == 1:
            native1 = native1[0]
        native2 = _load_code(open(code_filename, 'rb').read())
        try:
            if native1 == native2:
                return
        except TypeError:
            pass
        if verbose:
            print "SERIALIZED NATIVE1:"
            print _serialize_value(native1)
            print "SERIALIZED NATIVE2:"
            print _serialize_value(native2)
        assert _serialize_value(native1) == _serialize_value(native2), (native1, native2)
    finally:
        if verbose:
            print "NATIVE1:"
            pprint.pprint(native1)
            print "NATIVE2:"
            pprint.pprint(native2)

test_constructor_types.unittest = ['.data', '.code']

def test_subclass_blacklist_types(data_filename, verbose=False):
    _make_objects()
    try:
        yaml.load(open(data_filename, 'rb').read(), MyFullLoader)
    except yaml.YAMLError as exc:
        if verbose:
            print("%s:" % exc.__class__.__name__, exc)
    else:
        raise AssertionError("expected an exception")

test_subclass_blacklist_types.unittest = ['.subclass_blacklist']

def test_timezone_copy(verbose=False):
    import copy
    tzinfo = yaml.constructor.timezone(datetime.timedelta(0))

    tz_copy = copy.copy(tzinfo)
    tz_deepcopy = copy.deepcopy(tzinfo)

    if tzinfo.tzname() != tz_copy.tzname() != tz_deepcopy.tzname():
        raise AssertionError("Timezones should be equal")

test_timezone_copy.unittest = []

if __name__ == '__main__':
    import sys, test_constructor
    sys.modules['test_constructor'] = sys.modules['__main__']
    import test_appliance
    test_appliance.run(globals())

