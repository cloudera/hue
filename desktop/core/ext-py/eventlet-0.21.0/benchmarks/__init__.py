import gc
import timeit
import random

from eventlet.support import six


def measure_best(repeat, iters,
                 common_setup='pass',
                 common_cleanup='pass',
                 *funcs):
    funcs = list(funcs)
    results = dict([(f, []) for f in funcs])

    for i in six.moves.range(repeat):
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
