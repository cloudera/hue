from __future__ import print_function
import argparse
import gc
import importlib
import inspect
import math
import random
import re
import sys
import timeit

import eventlet
import six


# legacy, TODO convert context/localhost_socket benchmarks to new way
def measure_best(repeat, iters,
                 common_setup='pass',
                 common_cleanup='pass',
                 *funcs):
    funcs = list(funcs)
    results = dict((f, []) for f in funcs)

    for _ in range(repeat):
        random.shuffle(funcs)
        for func in funcs:
            gc.collect()
            t = timeit.Timer(func, setup=common_setup)
            results[func].append(t.timeit(iters))
            common_cleanup()

    best_results = {}
    for func, times in six.iteritems(results):
        best_results[func] = min(times)
    return best_results


class Benchmark:
    func = None
    name = ''
    iters = 0
    ns_per_op = 0
    allocs_per_op = 0
    mb_per_s = 0

    def __init__(self, **kwargs):
        for k, v in six.iteritems(kwargs):
            if not hasattr(self, k):
                raise AttributeError(k)
            setattr(self, k, v)

    def __str__(self):
        kvs = ', '.join('{}={}'.format(k, v) for k, v in six.iteritems(self.__dict__) if not k.startswith('_'))
        return 'Benchmark<{}>'.format(kvs)

    __repr__ = __str__

    def format_result(self, name_pad_to=64):
        # format compatible with golang.org/x/tools/cmd/benchcmp
        return "Benchmark_{b.name}{pad}\t{b.iters}\t{b.ns_per_op} ns/op".format(
            b=self, pad=' ' * (name_pad_to + 1 - len(self.name)))

    def run(self, repeat=5):
        wrapper_time = _run_timeit(self.func, 0)
        times = []
        for _ in range(repeat):
            t = _run_timeit(self.func, self.iters)
            if t == 0.0:
                raise Exception('{} time=0'.format(repr(self)))
            times.append(t)
        best_time = min(times) - wrapper_time
        self.ns_per_op = int((best_time * 1e9) / self.iters)


def _run_timeit(func, number):
    # common setup
    gc.collect()
    manager = getattr(func, '_benchmark_manager', None)
    try:
        # TODO collect allocations count, memory usage
        # TODO collect custom MB/sec metric reported by benchmark
        if manager is not None:
            with manager(number) as ctx:
                return timeit.Timer(lambda: func(ctx)).timeit(number=number)
        else:
            return timeit.Timer(func).timeit(number=number)
    finally:
        # common cleanup
        eventlet.sleep(0.01)


def optimal_iters(func, target_time):
    '''Find optimal number of iterations to run func closely >= target_time.
    '''
    iters = 1
    target_time = float(target_time)
    max_iters = int(getattr(func, '_benchmark_max_iters', 0))
    # TODO automatically detect non-linear time growth
    scale_factor = getattr(func, '_benchmark_scale_factor', 0.0)
    for _ in range(10):
        if max_iters and iters > max_iters:
            return max_iters
        # print('try iters={iters}'.format(**locals()))
        t = _run_timeit(func, number=iters)
        # print('... t={t}'.format(**locals()))
        if t >= target_time:
            return iters

        if scale_factor:
            iters *= scale_factor
            continue

        # following assumes and works well for linear complexity target functions
        if t < (target_time / 2):
            # roughly target half optimal time, ensure iterations keep increasing
            iters = iters * (target_time / t / 2) + 1
            # round up to nearest power of 10
            iters = int(10 ** math.ceil(math.log10(iters)))
        elif t < target_time:
            # half/double dance is less prone to overshooting iterations
            iters *= 2
    raise Exception('could not find optimal iterations for time={} func={}'.format(target_time, repr(func)))


def collect(filter_fun):
    # running `python benchmarks/__init__.py` or `python -m benchmarks`
    # puts .../eventlet/benchmarks at top of sys.path, fix it to project root
    if sys.path[0].endswith('/benchmarks'):
        path = sys.path.pop(0)
        correct = path.rsplit('/', 1)[0]
        sys.path.insert(0, correct)

    common_prefix = 'benchmark_'
    result = []
    # TODO step 1: put all toplevel benchmarking code under `if __name__ == '__main__'`
    # TODO step 2: auto import benchmarks/*.py, remove whitelist below
    # TODO step 3: convert existing benchmarks
    for name in ('hub_timers', 'spawn'):
        mod = importlib.import_module('benchmarks.' + name)
        for name, obj in inspect.getmembers(mod):
            if name.startswith(common_prefix) and inspect.isfunction(obj):
                useful_name = name[len(common_prefix):]
                if filter_fun(useful_name):
                    result.append(Benchmark(name=useful_name, func=obj))

    return result


def noop(*a, **kw):
    pass


def configure(manager=None, scale_factor=0.0, max_iters=0):
    def wrapper(func):
        func._benchmark_manager = manager
        func._benchmark_scale_factor = scale_factor
        func._benchmark_max_iters = max_iters
        return func
    return wrapper


def main():
    cmdline = argparse.ArgumentParser(description='Run benchmarks')
    cmdline.add_argument('-autotime', default=3.0, type=float, metavar='seconds',
                         help='''autoscale iterations close to this time per benchmark,
                         in seconds (default: %(default).1f)''')
    cmdline.add_argument('-collect', default=False, action='store_true',
                         help='stop after collecting, useful for debugging this tool')
    cmdline.add_argument('-filter', default='', metavar='regex',
                         help='process benchmarks matching regex (default: all)')
    cmdline.add_argument('-iters', default=None, type=int, metavar='int',
                         help='force this number of iterations (default: auto)')
    cmdline.add_argument('-repeat', default=5, type=int, metavar='int',
                         help='repeat each benchmark, report best result (default: %(default)d)')
    args = cmdline.parse_args()
    filter_re = re.compile(args.filter)

    bs = collect(filter_re.search)
    if args.filter and not bs:
        # TODO stderr
        print('error: no benchmarks matched by filter "{}"'.format(args.filter))
        sys.exit(1)
    if args.collect:
        bs.sort(key=lambda b: b.name)
        print('\n'.join(b.name for b in bs))
        return
    if not bs:
        raise Exception('no benchmarks to run')

    # execute in random order
    random.shuffle(bs)
    for b in bs:
        b.iters = args.iters or optimal_iters(b.func, target_time=args.autotime)
        b.run()

    # print results in alphabetic order
    max_name_len = max(len(b.name) for b in bs)
    bs.sort(key=lambda b: b.name)
    for b in bs:
        print(b.format_result(name_pad_to=max_name_len))


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(1)
