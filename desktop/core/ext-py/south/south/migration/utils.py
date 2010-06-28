import sys
from collections import deque

from django.utils.datastructures import SortedDict
from django.db import models

from south import exceptions


class SortedSet(SortedDict):
    def __init__(self, data=tuple()):
        self.extend(data)

    def __str__(self):
        return "SortedSet(%s)" % list(self)

    def add(self, value):
        self[value] = True

    def remove(self, value):
        del self[value]

    def extend(self, iterable):
        [self.add(k) for k in iterable]


def get_app_label(app):
    """
    Returns the _internal_ app label for the given app module.
    i.e. for <module django.contrib.auth.models> will return 'auth'
    """
    return app.__name__.split('.')[-2]


def app_label_to_app_module(app_label):
    """
    Given the app label, returns the module of the app itself (unlike models.get_app,
    which returns the models module)
    """
    # Get the models module
    app = models.get_app(app_label)
    module_name = ".".join(app.__name__.split(".")[:-1])
    try:
        module = sys.modules[module_name]
    except KeyError:
        __import__(module_name, {}, {}, [''])
        module = sys.modules[module_name]
    return module


def flatten(*stack):
    stack = deque(stack)
    while stack:
        try:
            x = stack[0].next()
        except AttributeError:
            stack[0] = iter(stack[0])
            x = stack[0].next()
        except StopIteration:
            stack.popleft()
            continue
        if hasattr(x, '__iter__'):
            stack.appendleft(x)
        else:
            yield x

def _dfs(start, get_children):
    # Prepend ourselves to the result
    yield start
    children = get_children(start)
    if children:
        # We need to apply all the migrations this one depends on
        yield (_dfs(n, get_children) for n in children)

def dfs(start, get_children):
    return flatten(_dfs(start, get_children))

def detect_cycles(iterable):
    result = []
    i = iter(iterable)
    try:
        # Point to the tortoise
        tortoise = 0
        result.append(i.next())
        # Point to the hare
        hare = 1
        result.append(i.next())
        # Start looking for cycles
        power = 1
        while True:
            # Use Richard P. Brent's algorithm to find an element that
            # repeats.
            while result[tortoise] != result[hare]:
                if power == (hare - tortoise):
                    tortoise = hare
                    power *= 2
                hare += 1
                result.append(i.next())
            # Brent assumes the sequence is stateless, but since we're
            # dealing with a DFS tree, we need to make sure that all
            # the items between `tortoise` and `hare` are identical.
            cycle = True
            for j in xrange(0, hare - tortoise + 1):
                tortoise += 1
                hare += 1
                result.append(i.next())
                if result[tortoise] != result[hare]:
                    # False alarm: no cycle here.
                    cycle = False
                    power = 1
                    tortoise = hare
                    hare += 1
                    result.append(i.next())
                    break
            # Both loops are done, so we must have a cycle
            if cycle:
                raise exceptions.CircularDependency(result[tortoise:hare+1])
    except StopIteration:
        # Return when `iterable` is exhausted. Obviously, there are no cycles.
        return result

def depends(start, get_children):
    result = SortedSet(reversed(detect_cycles(dfs(start, get_children))))
    return list(result)
